import asyncio
from threading import Thread, Event
import queue

from ...Application.TaskManager.job_task import JobTask

class TaskQueueItem():
    
    def __init__(self):
        self.__register_job:dict = {}
        self.__main_queue:queue.Queue = queue.Queue()
        self.__setEvent:Event = Event()
        self.__is_stop:bool = False
        self.__main_thread:Thread = None
        self.__work_task:str|None = None
        
    def IsStarted(self):
        return True if not self.__main_thread is None else False
    
    def stop(self):
        self.__is_stop = True
        self.__setEvent.set()

    def start(self):
        try:
            if self.__main_thread is None:
                self.__main_thread = Thread(target=self.__execute, daemon=True)
                self.__main_thread.start()

        except Exception as ex:
            print(ex)
    
    def add(self, task: JobTask)->JobTask | None:
        try:
            self.__register_job[task.id] = True
            self.__main_queue.put(task)
            
            if not self.__setEvent.is_set():
                self.__setEvent.set()

            return task
        except Exception as ex:
            print(ex)
            return None

    def check_task(self, task_id:str)->int:
        result = -1
        if self.__work_task:
            if self.__work_task == task_id:
                result = 0

        if task_id in self.__register_job:
            result = 1

        return result

    def __execute(self):
        while self.__setEvent.wait():
            if self.__is_stop:
                break
            while not self.__main_queue.empty():
                try:
                    task:JobTask = self.__main_queue.get()
                    self.__register_job.pop(task.id)

                    self.__work_task = task.id
                    result = asyncio.run(task.async_call())
                    self.__work_task = None

                    if task.is_callback():
                        task.callback_result(result)
                    else:
                        task.set_result(result)

                    self.__main_queue.task_done()
                except Exception as ex:
                    TaskQueueItem.__log__(f"ERROR:{ex}")
                    if result:
                        if task.is_callback():
                            task.callback_result(result)
                        else:
                            task.set_result(result)

            
            self.__setEvent.clear()

        self.__main_thread = None