#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import sys
import binascii
import signal
import threading
import queue
from logging import getLogger
logger = getLogger(__name__)

import nfc

SERVICE_CODE = 0x400b


class FelicaReader(threading.Thread):
    
    def __init__(self, queue):
        super().__init__(daemon=True)
        self._queue = queue

    def connected(self, tag):
        logger.debug("tags: %s" % tag)
        if tag is not None and tag.TYPE == "Type3Tag":
            try:
                sc = nfc.tag.tt3.ServiceCode(SERVICE_CODE >> 6, SERVICE_CODE & 0x3f)
                bc = nfc.tag.tt3.BlockCode(0, service=0)
                data = tag.read_without_encryption([sc], [bc])

                # These data are available only for the organization I belong to.
                number = data[0:8].decode()
                id = data[8:16].decode()
                self._queue.put(("nfc-connect", number, id))
            except Exception as e:
                logger.debug("error: %s" %e)
        else:
            logger.debug("error: tag isn't Type3Tag")
        return True

    def released(self, tag):
        self._queue.put(("nfc-release"))
        return True

    def run(self):
        clf = nfc.ContactlessFrontend('usb')
        while True:
            clf.connect(rdwr={'on-connect':self.connected,
                              'on-release':self.released})

            
if __name__ == "__main__":
    import logging
    logging.basicConfig(level=logging.DEBUG)
    q = queue.Queue()
    fr = FelicaReader(q)
    fr.start()
    logging.info(q.get())
