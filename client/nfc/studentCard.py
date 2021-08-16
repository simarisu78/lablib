#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import sys
import binascii
import nfc
import signal

service_code = 0x400b

def connected(tag):

    if tag is not None and tag.TYPE == "Type3Tag":
        try:
            sc = nfc.tag.tt3.ServiceCode(service_code >> 6, service_code & 0x3f) # formatted service code
            bc = nfc.tag.tt3.BlockCode(0,service=0) # formatted Block Code (sc[0],block_offset=0)
            data = tag.read_without_encryption([sc], [bc])
            print("Student ID: %s" % data[0:8].decode())
            print("Kiban ID: %s" % data[8:16].decode())
        except Exception as e:
            print("error: %s" % e)
    else:
        print("error: tag isn't Type3Tag")
    return True
        
def main():
    clf = nfc.ContactlessFrontend('usb')
    while True:
        clf.connect(rdwr={'on-connect':connected})

def handler(signal, frame):
    print('Process Interrupt!')
    sys.exit(0)
        
if __name__ == "__main__":
    signal.signal(signal.SIGINT, handler)
    main()
