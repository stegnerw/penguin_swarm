# -*- coding: utf-8 -*-
"""
Created on Wed Mar 10 17:38:13 2021

@author: barve
"""


class pengy:
    
    def __init__ (self, x, y, body=1, sense=3, temp=38, tolerance=10, SA=1, mass=1, h=0.001, c=1, metabolism=0.1, MS=1):
        self.x=x;
        self.y=y;
        self.body=body;
        self.sense=body+sense;
        self.norm_temp=temp;
        self.temp=temp;
        self.tolerance=tolerance;
        self.A=SA;
        self.m=mass;
        self.h=h;
        self.c=c;
        self.metabolism=metabolism;
        self.MS=MS;
        
    