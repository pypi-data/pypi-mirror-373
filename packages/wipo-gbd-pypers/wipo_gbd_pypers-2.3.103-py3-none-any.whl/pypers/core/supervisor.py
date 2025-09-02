import json
import shutil
import time
import uuid
import os
from pypers.utils.filelock import FileLock


manager = None


def get_status_manager(supervised=True):
    global manager
    if not manager:
        manager = StatusManager(supervised)
    return manager


class StatusManager:

    STATUS_LOCK = 'status'
    RUNNING_LOCK = 'running'
    KILLED = False
    TIMEOUT = 30  # in seconds

    def __init__(self, supervised):
        self.supervised = supervised
        container_id = None
        try:
            with open('/etc/hostname', 'r') as f:
                container_id = f.read().strip()
        except Exception as e:
            print(e)
            container_id = str(uuid.uuid1())
        self.path = os.path.join(os.getcwd(), container_id)
        os.makedirs(self.path, exist_ok=True)
        self.cleanup()

    def keep_alive(self):
        return not self.KILLED

    def stop(self):
        self.KILLED = True
        self.cleanup()
        shutil.rmtree(self.path)

    def cleanup(self):
        try:
            os.remove(os.path.join(self.path, self.STATUS_LOCK))
        except FileNotFoundError as e:
            pass
        try:
            os.remove(os.path.join(self.path, self.RUNNING_LOCK))
        except FileNotFoundError as e:
            pass

    def set_status(self, busy=False):
        if not self.supervised:
            return
        with FileLock(self.path, self.STATUS_LOCK):
            with open(os.path.join(self.path, self.STATUS_LOCK), 'w') as f:
                f.write('busy' if busy else 'idle')

    def set_sanity(self):
        if not self.supervised:
            return
        with FileLock(self.path, self.RUNNING_LOCK):
            with open(os.path.join(self.path, self.RUNNING_LOCK), 'w') as f:
                f.write("%s" % time.time())

    def is_running(self):
        if not self.supervised:
            return False
        if self.is_busy():
            return True
        with FileLock(self.path, self.RUNNING_LOCK):
            with open(os.path.join(self.path, self.RUNNING_LOCK), 'r') as f:
                last_ping = float(f.read())
                if time.time() - last_ping < self.TIMEOUT:
                    return True
            return False

    def is_busy(self):
        if not self.supervised:
            return False
        with FileLock(self.path, self.STATUS_LOCK):
            if os.path.exists(os.path.join(self.path, self.STATUS_LOCK)):
                with open(os.path.join(self.path, self.STATUS_LOCK), 'r') as f:
                    status = f.read()
                    return status == 'busy'
            return False
