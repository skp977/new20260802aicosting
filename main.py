from flask import Flask, jsonify, request, render_template, send_file, abort
from flask_cors import CORS
from dotenv import load_dotenv
from pathlib import Path
from datetime import datetime
from dataclasses import asdict
import json
import os
import html as html_lib

from orchestrators.manual_request_orchestrator import ManualRequestOrchestrator
from parsers.universal_parser import UniversalParser
from itinerary.activity_recommender import ActivityRecommender
from itinerary.food_recommender import FoodRecommender
from itinerary.souvenir_recommender import SouvenirRecommender
from itinerary.location_map import route_points
from crm.lead_manager import LeadManager
from automation.scheduler import scheduler, logger
from exports.pdf_exporter import PDFExporter
from exports.docx_exporter import DOCXExporter
from exports.excel_exporter import ExcelExporter

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")

app = Flask(__name__)
CORS(app)

engine = ManualRequestOrchestrator()
universal_parser = UniversalParser()
activity_recommender = ActivityRecommender()
food_recommender = FoodRecommender()
souvenir_recommender = SouvenirRecommender()
leads = LeadManager()

DATA_DIR = BASE_DIR / "data"
EXPORTS_DIR = DATA_DIR / "exports"
UPLOADS_DIR = DATA_DIR / "uploads"
KIND_DIRS = {
    "requests": DATA_DIR / "requests",
    "itineraries": DATA_DIR / "itineraries",
    "costings": DATA_DIR / "costings"
}

ALLOWED_EXTENSIONS = {
    ".pdf", ".docx", ".txt", ".rtf",
    ".xlsx", ".xls", ".csv",
    ".jpg", ".jpeg", ".png", ".webp", ".bmp", ".tiff",
    ".eml"
}

PDF = PDFExporter()
DOCX = DOCXExporter()
XLSX = ExcelExporter()


def _list_files(kind):
    directory = KIND_DIRS[kind]
    directory.mkdir(parents=True, exist_ok=True)

    files = []
    for path in directory.glob("*.json"):
        files.append({
            "file": path.name,
            "saved": datetime.fromtimestamp(path.stat().st_mtime).strftime("%Y-%m-%d %H:%M"),
            "preview": _preview(path, kind)
        })

    files.sort(key=lambda f: f["saved"], reverse=True)
    return files


def _preview(path, kind):
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return ""

    if kind == "requests":
        parts = []
        if data.get("customer_email"):
            parts.append(data["customer_email"])
        if data.get("pax"):
            parts.append(f"{data['pax']} pax")
        if data.get("destinations"):
            parts.append(", ".join(data["destinations"]))
        return " | ".join(parts)

    if kind == "costings":
        if isinstance(data, dict) and "grand_total" in data:
            return f"Grand Total: {data['grand_total']} {data.get('currency', '')}"

    if isinstance(data, dict):
        items = list(data.values())
    elif isinstance(data, list):
        items = [
            v for d in data
            if isinstance(d, dict)
            for v in d.values()
        ][:3] if data else []
    else:
        items = [data]

    return ", ".join(str(v)[:60] for v in items)


def _load_record(kind, file):
    name = Path(file).name
    path = KIND_DIRS[kind] / name

    if not path.is_file():
        abort(404, description="Record not found")

    return path


def _record_text(kind, file, data):
    lines = [
        "PM AUTOMATION - NITS",
        "====================",
        f"Record type : {kind}",
        f"File        : {file}",
        "--------------------"
    ]

    if isinstance(data, dict):
        for key, value in data.items():
            if isinstance(value, list):
                lines.append(f"{key}: {', '.join(str(v) for v in value)}")
            else:
                lines.append(f"{key}: {value}")
    else:
        lines.append(str(data))

    return "\n".join(lines)


def _export_record(kind, file, fmt):
    path = _load_record(kind, file)
    data = json.loads(path.read_text(encoding="utf-8"))

    EXPORTS_DIR.mkdir(parents=True, exist_ok=True)
    stem = path.stem

    if fmt == "pdf":
        target = EXPORTS_DIR / f"{stem}.pdf"
        PDF.export(str(target), _record_text(kind, file, data))
        return target

    if fmt == "docx":
        target = EXPORTS_DIR / f"{stem}.docx"
        DOCX.export(str(target), _record_text(kind, file, data))
        return target

    if fmt == "xlsx":
        target = EXPORTS_DIR / f"{stem}.xlsx"
        XLSX.export(str(target), data)
        return target

    if fmt == "html":
        target = EXPORTS_DIR / f"{stem}.html"
        body = html_lib.escape(json.dumps(data, indent=2, ensure_ascii=False))
        target.write_text(
            f"<!DOCTYPE html><html><head><meta charset='utf-8'>"
            f"<title>{html_lib.escape(file)}</title></head>"
            f"<body style='font-family:Arial,sans-serif'>"
            f"<h2>PM Automation - {html_lib.escape(kind)}</h2>"
            f"<pre>{body}</pre></body></html>",
            encoding="utf-8"
        )
        return target

    abort(400, description="Unsupported format")


@app.route("/")
def dashboard():
    counts = {kind: len(_list_files(kind)) for kind in KIND_DIRS}
    counts["exports"] = len(list(EXPORTS_DIR.glob("*"))) if EXPORTS_DIR.exists() else 0

    latest = _list_files("requests")[:5]

    return render_template(
        "index.html",
        active="dashboard",
        counts=counts,
        latest=latest,
        started=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        pyver=os.sys.version.split()[0],
        base_dir=str(BASE_DIR)
    )


@app.route("/generate", methods=["GET", "POST"])
def generate():
    empty = render_template(
        "generate.html",
        active="generate",
        inquiry="",
        url="",
        mode="text",
        source_info=None,
        error=None,
        req=None,
        itinerary=None,
        costing=None,
        suggestions=None
    )

    if request.method == "GET":
        return empty

    mode = request.form.get("mode", "text")
    inquiry = request.form.get("inquiry", "").strip()
    url = request.form.get("url", "").strip()
    source_info = {"type": mode, "file": "", "engine": ""}

    try:
        if mode == "url":
            if not url:
                return _generate_error("URL is empty. Please enter a website URL.")
            parsed = universal_parser.parse(url)
            source_info["type"] = "url"
            source_info["engine"] = parsed.get("engine", "")
        elif mode == "file":
            uploaded = request.files.get("file")
            if not uploaded or not uploaded.filename:
                return _generate_error("No file selected. Please upload a file.")
            ext = Path(uploaded.filename).suffix.lower()
            if ext not in ALLOWED_EXTENSIONS:
                return _generate_error(
                    f"Unsupported file type '{ext or 'unknown'}'. "
                    "Allowed: PDF, DOCX, TXT, RTF, XLSX, XLS, CSV, "
                    "JPG, PNG, EML."
                )
            UPLOADS_DIR.mkdir(parents=True, exist_ok=True)
            target = UPLOADS_DIR / uploaded.filename
            uploaded.save(target)
            parsed = universal_parser.parse_file(target)
            source_info["type"] = "file"
            source_info["file"] = uploaded.filename
            source_info["engine"] = parsed.get("engine", "")
        else:
            if not inquiry:
                return _generate_error("Inquiry text is empty. Please enter a customer inquiry.")
            parsed = {"text": inquiry, "type": "raw_text"}

        text = (parsed.get("text") or "").strip()

        if not text:
            return _generate_error("No readable text was extracted from the input.")

        if parsed.get("engine") == "unavailable":
            return _generate_error(text)

        result = engine.process(text)

        request_data = asdict(result["request"])
        request_data["source_type"] = parsed.get("type", "raw_text")
        request_data["source_file"] = source_info.get("file", "")

        suggestions = {
            "activities": activity_recommender.recommend(result["request"]),
            "food": food_recommender.recommend(result["request"]),
            "souvenirs": souvenir_recommender.recommend(result["request"])
        }

        route = route_points(result["request"].destinations)

        return render_template(
            "generate.html",
            active="generate",
            inquiry=inquiry,
            url=url,
            mode=mode,
            source_info=source_info,
            error=None,
            req=request_data,
            itinerary=result["itinerary"],
            costing=result["costing"],
            price_estimate=result.get("price_estimate"),
            suggestions=suggestions,
            route=route
        )

    except Exception as exc:
        return _generate_error(f"Processing failed: {exc}")


def _generate_error(message):
    return render_template(
        "generate.html",
        active="generate",
        inquiry="",
        url="",
        mode="text",
        source_info=None,
        error=message,
        req=None,
        itinerary=None,
        costing=None,
        suggestions=None
    )


@app.route("/records")
def records():
    return render_template(
        "records.html",
        active="records",
        requests=_list_files("requests"),
        itineraries=_list_files("itineraries"),
        costings=_list_files("costings")
    )


@app.route("/record/<kind>/<file>")
def record(kind, file):
    if kind not in KIND_DIRS:
        abort(404, description="Unknown record type")

    path = _load_record(kind, file)
    payload = json.loads(path.read_text(encoding="utf-8"))

    return render_template(
        "record.html",
        active="records",
        kind=kind,
        file=path.name,
        payload=json.dumps(payload, indent=2, ensure_ascii=False)
    )


@app.route("/export/<kind>/<file>")
def export(kind, file):
    if kind not in KIND_DIRS:
        abort(404, description="Unknown record type")

    fmt = request.args.get("format", "pdf")

    target = _export_record(kind, file, fmt)

    return send_file(target, as_attachment=True, download_name=target.name)


@app.route("/automation")
def automation():
    log_text = ""
    log_file = BASE_DIR / "data" / "logs" / "automation.log"

    if log_file.is_file():
        log_text = log_file.read_text(
            encoding="utf-8", errors="ignore"
        ).splitlines()[-30:]
        log_text = "\n".join(log_text)

    processed_text = ""
    processed_file = BASE_DIR / "data" / "logs" / "processed_uids.txt"

    if processed_file.is_file():
        processed_text = processed_file.read_text(
            encoding="utf-8", errors="ignore"
        ).strip()

    return render_template(
        "automation.html",
        active="automation",
        enabled=scheduler.enabled,
        running=scheduler.running,
        interval=scheduler.interval,
        poll_seconds=os.getenv("AUTOMATION_POLL_SECONDS", "60"),
        log=log_text,
        processed=processed_text,
        lead_count=len(leads.list()),
        imap_user=os.getenv("EMAIL_USER", ""),
        admin_email=os.getenv("ADMIN_EMAIL", ""),
        whatsapp_phone=os.getenv("WHATSAPP_PHONE", "")
    )


@app.route("/health")
def health():
    return jsonify({
        "status": "healthy",
        "service": "pm-automation",
        "time": datetime.now().isoformat()
    })


@app.route("/dashboard")
def dashboard_json():
    modules = [
        "api",
        "automation",
        "costing",
        "crm",
        "itinerary",
        "mail_services",
        "whatsapp",
        "translators"
    ]

    return jsonify({
        "project": "PM Automation",
        "modules": modules,
        "working_directory": str(BASE_DIR),
        "python_version": os.sys.version.split()[0]
    })


if __name__ == "__main__":
    print("=" * 50)
    print("STARTING PM AUTOMATION SERVER")
    print("=" * 50)
    print("Home      : http://127.0.0.1:5000/")
    print("Records   : http://127.0.0.1:5000/records")
    print("Automation: http://127.0.0.1:5000/automation")
    print("Health    : http://127.0.0.1:5000/health")
    print("Dashboard : http://127.0.0.1:5000/dashboard")
    print("=" * 50)

    if app.debug and os.environ.get("WERKZEUG_RUN_MAIN") != "true":
        print("(scheduler will start with the reloader worker)")
    else:
        scheduler.start()

    app.run(host="0.0.0.0", port=5000, debug=True)
