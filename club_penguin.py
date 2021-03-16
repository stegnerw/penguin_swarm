# -*- coding: utf-8 -*-
"""
Created on Wed Mar 10 23:22:56 2021

@author: barve
"""


import pengy
import random
import matplotlib.pyplot as plt
import matplotlib as mpl
import math
import numpy as np
population=[];

max_x=20;
max_y=20;
body=1;
env_temp=-60;
#Initialize Population
for i in range(250):
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

for n in range(1000):
    random.shuffle(population);
    
    for i in population:
        #Update Temperatures
        q_pop=0;
        x_dense=0;
        y_dense=0;
        for j in population:
            if(i!=j):
                #Population Heat Transfer
                if(i.x==j.x and i.y==j.y):
                    d=0.0001;
                else:
                    d=math.sqrt(pow(i.x-j.x,2)+pow(i.y-j.y,2));
                heat=(i.h*j.h*i.A*j.A*(j.temp-i.temp)/d);
                q_pop=q_pop+heat;
                j.temp=j.temp-(heat/(j.c*j.m));
                if(d<=i.sense):
                    x_dense=x_dense+(j.x-i.x);
                    y_dense=y_dense+(j.y-i.y);
        q_env=i.h*i.A*(env_temp-i.temp);
        q_gen=i.metabolism*i.c*i.m;
        delta_temp=(q_pop+q_env+q_gen)/(i.c*i.m);
        i.temp=i.temp+delta_temp;
        x_move=0;
        y_move=0;
        if(x_dense!=0 or y_dense!=0):
            if(i.temp<(i.norm_temp-i.tolerance)):
                x_move=x_dense/(math.sqrt(pow(x_dense,2)+pow(y_dense,2)));
                y_move=y_dense/(math.sqrt(pow(x_dense,2)+pow(y_dense,2)));
            elif(i.temp>(i.norm_temp+i.tolerance)):
                x_move=-1*x_dense/(math.sqrt(pow(x_dense,2)+pow(y_dense,2)));
                y_move=-1*y_dense/(math.sqrt(pow(x_dense,2)+pow(y_dense,2)));
            else:
                x_rand=random.uniform(-1,1);
                y_rand=random.uniform(-1,1);
                if(x_rand!=0 or y_rand!=0):
                    x_move=x_rand/(math.sqrt(pow(x_rand,2)+pow(y_rand,2)));
                    y_move=y_rand/(math.sqrt(pow(x_rand,2)+pow(y_rand,2)));
        else:
            x_rand=random.uniform(-1,1);
            y_rand=random.uniform(-1,1);
            if(x_rand!=0 or y_rand!=0):
                x_move=x_rand/(math.sqrt(pow(x_rand,2)+pow(y_rand,2)));
                y_move=y_rand/(math.sqrt(pow(x_rand,2)+pow(y_rand,2)));
        i.x=i.x+x_move*i.MS;
        i.y=i.y+y_move*i.MS;
    x_val,y_val,body_val,temp_val = zip(*[(float(i.x),float(i.y),float(i.body),float(i.temp)) for i in population]);
    plt.scatter(x_val,y_val,s=(body_val*1000),c=temp_val);
    fig_str="pengy_fig_"+str(n)+".png"
    plt.savefig(fig_str);
    plt.show();