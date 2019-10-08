#!/usr/bin/python2
# -*- coding: utf-8 -*-

"""
procedure to manage session

author: Cheng WANG

last edited: January 2015
"""

import sys
import os
import time
from RCPCom.RCPComStack import RCPComStack
from RCPContext.RCPContext import RCPContext
from RCPControl.Dispatcher import Dispatcher


def main():
    context = RCPContext()
    
    com_stack = RCPComStack(context)
    
    instruments = Dispatcher(context)

    com_stack.connectera("192.168.137.1", 10704)


if __name__ == '__main__':
    main()
