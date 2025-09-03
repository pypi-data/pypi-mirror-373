import os
import asyncio
from typing import Dict
from dotenv import load_dotenv
from tenacity import retry, stop_after_attempt, wait_fixed
from Osdental.ServicesBus.ServicesBus import ServicesBus
from Osdental.Shared.Logger import logger

load_dotenv(dotenv_path='.env', override=True)

class TaskQueue:
    """Queue to manage tasks in order and asynchronously."""
    conn_str = os.getenv('CONNECTION_STRING')
    queue_name = os.getenv('QUEUE')
    
    def __init__(self):
        self.service_bus = ServicesBus(self.conn_str, self.queue_name)
        self.queue = asyncio.Queue()
        

    def start_processing(self):
        """Start processing tasks in the background."""
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

        loop.create_task(self.process_tasks())

    @retry(stop=stop_after_attempt(3), wait=wait_fixed(5))
    async def enqueue(self, message:Dict[str,str]):
        """Add a task to the queue."""
        await self.queue.put(message)


    async def process_tasks(self):
        """Process tasks from the queue in order."""
        while True:
            message = await self.queue.get()
            try:
                await self.service_bus.send_message(message)
            except Exception as e:
                logger.error(f'Message queuing error: {str(e)}')
            finally:
                self.queue.task_done()


task_queue = TaskQueue()
task_queue.start_processing()