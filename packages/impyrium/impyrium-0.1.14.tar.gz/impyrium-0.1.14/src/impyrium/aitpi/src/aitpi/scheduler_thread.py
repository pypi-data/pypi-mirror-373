import sched
import time
import threading
from . import router
from . import message

class SchedulerThread():
    def __init__(self, delayTime=0.1):
        self.scheduler = sched.scheduler(time.time, time.sleep)
        self.worker = threading.Thread(target=self.run)
        self.running = False
        self.shouldRun = False
        self.delayTime = delayTime
        router.addConsumer([message.CleanUp.msgId], self)

    def run(self):
        while (self.shouldRun):
            self.scheduler.run()
            time.sleep(self.delayTime)
        self.running = False

    def start(self):
        if self.running:
            return
        self.running = True
        self.shouldRun = True
        self.worker.start()

    def stop(self, blockWait=False):
        if not self.running:
            return False
        self.shouldRun = False
        while blockWait and self.running:
            time.sleep(0.25)

    def scheduleItem(self, delay, fun, arguments=(), priority=0):
        return self.scheduler.enter(delay, priority, fun, arguments)

    def consume(self, msg):
        self.stop(True)
