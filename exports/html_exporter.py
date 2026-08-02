
"""
FILE NAME:
html_exporter.py

PURPOSE:
Export itinerary and costing to HTML
"""

def export_html(request,itinerary,costing):

    filename="output.html"

    html=f"""
    <html>
    <body>
    <h1>PM Automation</h1>
    <pre>{request}</pre>
    <pre>{itinerary}</pre>
    <pre>{costing}</pre>
    </body>
    </html>
    """

    open(
        filename,
        "w",
        encoding="utf-8"
    ).write(html)

    return filename

