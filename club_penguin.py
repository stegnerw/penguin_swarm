# -*- coding: utf-8 -*-
"""
Created on Wed Mar 10 23:22:56 2021

@author: barve
"""


import pengy
import random
import matplotlib.pyplot as plt
import math
population=[];

neighborhood=[];

max_x=1000;
max_y=1000;
body=1;
env_temp=-60;
#Initialize Population
for i in range(10000):
    x=random.randint(0,int(max_x/body));
    y=random.randint(0,int(max_y/body));
    exists=0;
    for j in population:
        if(j.x==(x*body) and j.y==(y*body)):
            exists=1;
    if(not(exists)):
        population.append(pengy.pengy(x*body,y*body));

x_val,y_val,body_val,temp_val = zip(*[(float(i.x),float(i.y),float(i.body),float(i.temp)) for i in population]);
plt.scatter(x_val,y_val,s=body_val,c=temp_val);
plt.show();

for i in range(10000):
    #Update Temperatures
    for i in population:
        q_pop=0;
        for j in population:
            if(i!=j):
                #Population Heat Transfer
                d=math.sqrt(pow(i.x-j.x,2)+pow(i.y-j.y,2));
                q_pop=q_pop+(i.h*i.A*(j.temp-i.temp)/pow(d,2));
        q_env=i.h*i.A*(env_temp-i.temp);
        q_gen=i.metabolism*i.c*i.m*(i.norm_temp-i.temp)*(i.temp<i.norm_temp);
        delta_temp=(q_pop+q_env+q_gen)/(i.c*i.m);
        i.temp=i.temp+delta_temp;    
           
    x_val,y_val,body_val,temp_val = zip(*[(float(i.x),float(i.y),float(i.body),float(i.temp)) for i in population]);
    plt.scatter(x_val,y_val,s=body_val,c=temp_val);
    plt.show();