# -*- coding: utf-8 -*-
"""This module is the main module.
"""
from penguin import Penguin

if __name__ == "__main__":
    penguin = Penguin(x_pos=0,
                      y_pos=0,
                      body_size=1,
                      sense_radius=10,
                      body_temp=30,
                      body_temp_low_threshold=27,
                      body_temp_high_threshold=33)
