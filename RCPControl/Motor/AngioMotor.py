#!/usr/bin/env python
# encoding utf-8

class AngioMotor(object):

    def open_device(self):
        pass

    def close_device(self):
        pass

    def close_position_device(self):
        pass

    def set_expectedSpeed(self, speed):
        pass

    def standby(self):
        pass

    def enable(self):
        pass

    def continuous_move(self):
        pass

    def rtz(self):
        pass

    def push(self):
        pass

    def pull(self):
        pass

    def continuous_move_position(self):
        pass

#Position Mode
    
    def set_position(self, volume):
        pass

    def set_pos_expectedSpeed(self, vol_speed):
        pass

    def position_push(self):
        pass

    def position_pull(self):
        pass
    
    def set_context(self, context):
        pass
