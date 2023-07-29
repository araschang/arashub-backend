from apscheduler.schedulers.asyncio import AsyncIOScheduler
from Application.MagicFormula.MagicFormula import MagicFormula
import asyncio
import threading

scheduler = AsyncIOScheduler()

def run():
    asyncio.set_event_loop(asyncio.new_event_loop())
    scheduler.add_job(MagicFormula().run, 'cron', day_of_week='mon-fri', hour=13, minute=30)
    scheduler.start()
    loop = asyncio.get_event_loop()
    loop.run_forever()

thread = threading.Thread(target=run)
thread.start()
