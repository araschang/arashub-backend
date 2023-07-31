from apscheduler.schedulers.asyncio import AsyncIOScheduler
from Application.VolumeBomb.VolumeBomb import VolumeBomb
import asyncio
import threading

scheduler = AsyncIOScheduler(job_defaults={'max_instances': 3})

def run():
    asyncio.set_event_loop(asyncio.new_event_loop())
    scheduler.add_job(VolumeBomb().run, 'interval', seconds=5)
    scheduler.start()
    loop = asyncio.get_event_loop()
    loop.run_forever()

thread = threading.Thread(target=run)
thread.start()