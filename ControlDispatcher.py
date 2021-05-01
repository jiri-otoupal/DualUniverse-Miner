import logging
from queue import Queue
from threading import Thread
from time import sleep


class ControlDispatcher:

    def __init__(self):
        self.stopped = False
        self.camera_queue = Queue()
        self.movement_queue = Queue()
        self.jump_queue = Queue()
        self.tool_control_queue = Queue()

    def start(self):
        self.stopped = False
        logging.info("Started Control Dispatcher")
        Thread(target=self.__update_rotate).start()
        Thread(target=self.__update_position).start()
        Thread(target=self.__update_jump).start()
        Thread(target=self.__update_tool).start()

    def stop(self, a=None, b=None):
        self.stopped = True

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
        self.movement_queue.put(function_ptr)

    def request_jump(self, function_ptr):
        """
        Request of Movement
        Example:
        request_movement(lambda:Forward(1))
        :param function_ptr: Movement Function ! Without () !
        """
        self.jump_queue.put(function_ptr)

    def request_rotate(self, function_ptr):
        """
        Request of Rotate
        Example:
        request_rotate(lambda:LookLeft(45))
        :param function_ptr: Rotate Function
        """
        self.camera_queue.put(function_ptr)

    def request_tool_event(self, function_ptr):
        """
        Request of Rotate
        Example:
        request_rotate(lambda:LookLeft(45))
        :param function_ptr: Rotate Function
        """
        self.tool_control_queue.put(function_ptr)

    def __update_position(self):
        while not self.stopped:
            if not self.movement_queue.empty():
                self.movement_queue.get()()
                logging.debug("AI Requested Movement")
            sleep(0.05)

    def __update_jump(self):
        while not self.stopped:
            if not self.jump_queue.empty():
                self.jump_queue.get()()
                logging.debug("AI Requested Jump")
            sleep(0.05)

    def __update_rotate(self):
        while not self.stopped:
            if not self.camera_queue.empty():
                self.camera_queue.get()()
                logging.debug("AI Requested Rotating")
            sleep(0.05)

    def __update_tool(self):
        while not self.stopped:
            if not self.tool_control_queue.empty():
                self.tool_control_queue.get()()
                logging.debug("AI Requested Tool Event")
            sleep(0.05)
