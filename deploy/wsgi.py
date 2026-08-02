import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from automation.scheduler import scheduler
from automation.scheduler import logger as scheduler_logger

from main import app

if not scheduler.running:
    scheduler.start()
    scheduler_logger.info("Scheduler started by wsgi entrypoint")
