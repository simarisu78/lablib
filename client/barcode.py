import logging
import sys
import evdev
import threading
import queue
import re

# for testing
PATH = "/dev/input/event0"
keymap = { 2 : '1', 3 : '2', 4 : '3', 5 : '4', 6 : '5', 7 : '6', 8 : '7', \
           9 : '8', 10 : '9', 11 : '0', \
           79 : '1', 80 : '2', 81 : '3', 75 : '4', 76 : '5', 77 : '6', 71 : '7', \
           72 : '8', 73 : '9', 82 : '0'}

class BarcodeReader(threading.Thread):
    def __init__(self, queue):
        super(BarcodeReader, self).__init__()
        self._device = self.find_device()
        self._queue = queue

    # TODO: enable to configure device path directly (if path defined)
    def find_device(self):
        devices = [evdev.InputDevice(path) for path in evdev.list_devices()]

        if PATH is not None:
            return evdev.InputDevice(PATH)
        
        for d in devices:
            if re.search('keyboard', d.name, re.IGNORECASE) is not None:
                logging.info('Barcode Reader Found!: %s %s' % (d.name, d.phys))
                return d
        logging.critical("Barcode Reader NOT FOUND!")
        sys.exit(1)
        
    def run(self):
        import time
        barcode = ''
        while True:
            for event in self._device.read_loop():
                if event.type == evdev.ecodes.EV_KEY and event.value == 1:
                    if event.code in (28, 96):
                        q.put(barcode)
                        barcode = ''
                    elif keymap.get(event.code) is not None:
                        barcode += keymap.get(event.code)
        
        
if __name__ == "__main__":
    q = queue.Queue()
    br = BarcodeReader(q)
    br.daemon = True
    br.start()
    while True:
        print("waiting ...")
        print(q.get())
