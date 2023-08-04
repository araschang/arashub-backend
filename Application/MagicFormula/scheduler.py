from apscheduler.schedulers.background import BackgroundScheduler
from Application.MagicFormula.MagicFormula import MagicFormula
from datetime import datetime, timedelta
import asyncio

def run_magic_formula():
    asyncio.run(MagicFormula().run())


scheduler = BackgroundScheduler(job_defaults={'max_instances': 3})
scheduler.add_job(run_magic_formula, 'cron', day_of_week='mon-fri', hour=13, minute=30)
# scheduler.add_job(run_magic_formula, 'interval', seconds=60, next_run_time=datetime.now() + timedelta(seconds=10))
scheduler.start()
