import logging
from queue import Queue
from threading import Thread
from time import sleep


class ControlDispatcher:

    def __init__(self, window):
        self.stopped = True
        self.mining = False
        self.camera_queue = Queue()
        self.movement_queue = Queue()
        self.jump_queue = Queue()
        self.tool_control_queue = Queue()
        self.t1: Thread = None
        self.t2: Thread = None
        self.t3: Thread = None
        self.t4: Thread = None
        self.window = window
        self.mr_undergoing = False  # Movement or rotation in progress

    def start(self):
        self.stopped = False
        logging.info("Started Control Dispatcher")
        self.t1 = Thread(target=self.__update_rotate, name="Rotate", daemon=True)
        self.t2 = Thread(target=self.__update_position, name="Position", daemon=True)
        self.t3 = Thread(target=self.__update_jump, name="Tool", daemon=True)
        self.t4 = Thread(target=self.__update_tool, name="Jump", daemon=True)
        self.t1.start()
        self.t2.start()
        self.t3.start()
        self.t4.start()

    def stop(self, a=None, b=None):
        if a.name == "esc":
            self.stopped = True
            logging.info("User requested stop... Stopping")
            self.window.minimize()

    def clear_movement_rotation(self):
        self.movement_queue.queue.clear()
        self.camera_queue.queue.clear()
        self.jump_queue.queue.clear()

    def request_movement(self, function_ptr):
        """
        Request of Movement
        Example:
        request_movement(lambda:Forward(1))
        :param function_ptr: Movement Function ! Without () !
        """
        if self.tool_control_queue.empty() and not self.mining:
            self.movement_queue.put(function_ptr)

    def request_jump(self, function_ptr):
        """
        Request of Movement
        Example:
        request_movement(lambda:Forward(1))
        :param function_ptr: Movement Function ! Without () !
        """
        if self.tool_control_queue.empty() and not self.mining:
            self.jump_queue.put(function_ptr)

    def request_rotate(self, function_ptr):
        """
        Request of Rotate
        Example:
        request_rotate(lambda:LookLeft(45))
        :param function_ptr: Rotate Function
        """
        if self.tool_control_queue.empty() and not self.mining:
            self.camera_queue.put(function_ptr)

    def request_tool_event(self, function_ptr):
        """
        Request of Rotate
        Example:
        request_rotate(lambda:LookLeft(45))
        :param function_ptr: Rotate Function
        """
        if self.tool_control_queue.empty() and not self.mining:
            self.tool_control_queue.put(function_ptr)

    def __update_position(self):
        while not self.stopped:
            if not self.movement_queue.empty() and not self.mining:
                self.movement_queue.get()()
                logging.info("AI Requested Movement")
            sleep(0.05)

    def __update_jump(self):
        while not self.stopped:
            if not self.jump_queue.empty() and not self.mining:
                self.jump_queue.get()()
                logging.info("AI Requested Jump")
            sleep(0.05)

    def __update_rotate(self):
        while not self.stopped:
            if not self.camera_queue.empty() and not self.mining:
                self.camera_queue.get()()
                logging.info("AI Requested Rotating")
            sleep(0.05)

    def __update_tool(self):
        while not self.stopped:
            if not self.tool_control_queue.empty() and not self.mining:
                self.tool_control_queue.get()()
                logging.info("AI Requested Tool Event")
            sleep(0.05)
