import retracesoftware.functional as functional
import retracesoftware_utils as utils

class ThreadSwitch:
    def __init__(self, thread_id):
        self.thread_id = thread_id


def thread_aware_writer(writer):
    on_thread_switch = functional.sequence(utils.thread_id(), writer.handle('THREAD_SWITCH'))
    return utils.threadawareproxy(on_thread_switch = on_thread_switch, target = writer)
