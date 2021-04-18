#! /usr/bin/env python3
# -*- coding: utf-8 -*-
"""This module contains the Environment class.

The Environment implements a container to hold agents and control interactions.
"""
# Standard library
from __future__ import annotations
import logging
import configparser
import pathlib
import random
import re
import shutil
# Packages
import coloredlogs
import matplotlib.pyplot as plt
import numpy as np
from PIL import Image
# Custom
from agent import Agent
from penguin import Penguin

LOG = logging.getLogger("penguin_swarm.environment")

# File paths
SRC_DIR = pathlib.Path(__file__).parent.resolve()
PROJ_DIR = SRC_DIR.parent


class Environment:
    """Environment container.

    Parameters
    ----------
    log_level : int
        Minimum logging level
    config : configparser.ConfigParser
        ConfigParser object with the configurations
    """
    def __init__(
        self,
        log_level: int,
        name: str,
        image_dir: str,
        env_size: np.ndarray[int],
        grid_size: float,
        time_step_size: float,
        epochs: int,
        air_conductivity: float,
        initial_air_temp: float,
        ambient_air_temp: float,
    ):
        coloredlogs.install(
            level=log_level * 10,
            logger=LOG,
            milliseconds=True,
        )
        self._name = name
        self._file_name = self._name.lower()

        # Filenames should be only lowercase, numbers, hyphens, and underscores
        self._file_name = re.sub(" ", "_", self._file_name)
        self._file_name = re.sub("[^a-z0-9_-]", "", self._file_name)
        self._env_size = env_size
        self._agents = list()
        self._epoch = 0
        self._grid_size = grid_size
        self._time_step_size = time_step_size
        self._epochs = epochs

        # Drawing environment
        self._drawing_env = np.ones(
            shape=(self.env_size[0], self.env_size[1], 3),
            dtype=float,
        )

        # Thermal model related members
        self._thermal_map = np.full(shape=self._env_size, fill_value=initial_air_temp, dtype=float)
        # I intend this to store a string but Sid you may change the dtype
        # I did not do enums because I dislike Python enums
        """
        Material Map Key:
            [0] = Air
            [1] = Penguin Core
            [2] = Penguin Internal
            [3] = Penguin External
        """
        self._material_map = np.zeros(shape=self._env_size, dtype=float)
        self._air_conductivity = air_conductivity
        self._initial_air_temp = initial_air_temp
        self._ambient_air_temp = ambient_air_temp

        # Initialize image directories
        self._image_dir = PROJ_DIR.joinpath(image_dir)
        self._image_dir.mkdir(mode=0o775, exist_ok=True)
        self._image_dir = self._image_dir.joinpath(self._file_name)
        self._image_dir.mkdir(mode=0o775, exist_ok=True)
        self._gif_img_dir = self._image_dir.joinpath("gif_imgs")
        shutil.rmtree(self._gif_img_dir, ignore_errors=True)
        self._gif_img_dir.mkdir(mode=0o775, exist_ok=True)
        LOG.debug(f"Initialized Environment: {self._name}")

    @property
    def env_size(self) -> tuple[int]:
        """int: The size of the environment in the form (rows, cols) tiles"""
        return self._env_size

    def run(self) -> None:
        """Run for a set number of epochs"""
        # TODO: Initialize the thermal environment, probably around here.
        # Do that initialization in a separate function.
        # Draw initial board
        self.draw()
        for epoch in range(self._epochs):
            LOG.info(f"Begin epoch {epoch + 1}/{self._epochs}")
            self.run_epoch()
            self.update_thermal()
        self.save_gif()
        shutil.rmtree(self._gif_img_dir, ignore_errors=True)
    def update_thermal(self) -> None:
        """Update the thermals of the environment.

        This will include calculating the temperature of every tile,
        calculating the body temperature of each agent, and anything
        else included in the thermal model.
        """
        prev_material_map=self._material_map
        
        """Update Maps"""
        agent_id=np.full(shape=self._env_size, fill_val=-1, dtype=float)
        heat_capacity=np.full(shape=self._env_size, fill_value=(1.657*pow(self._grid_size,3)*0.716),dtype=float)
        self._material_map = np.zeros(shape=self._env_size, dtype=float)
        for n in range(len(self.agents)):
            if(self.agents[n].alive):
                pos = self.agents[n].position
                for i in range(self.agents[n].body_radius):
                    for j in range(self.agents[n].body_radius - i):
                        """Material Map"""
                        if(i==0 and j==0):
                            self._material_map[pos[0], pos[1]] = 1
                        elif(i==self.agents[n].body_radius-1 or j==self.agents[n].body_radius-1):                        
                            self._material_map[pos[0] + i, pos[1] + j] = 3
                            self._material_map[pos[0] + i, pos[1] - j] = 3
                            self._material_map[pos[0] - i, pos[1] + j] = 3
                            self._material_map[pos[0] - i, pos[1] - j] = 3
                        else:
                            self._material_map[pos[0] + i, pos[1] + j] = 2
                            self._material_map[pos[0] + i, pos[1] - j] = 2
                            self._material_map[pos[0] - i, pos[1] + j] = 2
                            self._material_map[pos[0] - i, pos[1] - j] = 2
                        
                        """Specific Heat Capacity Map"""
                        heat_capacity[pos[0] + i, pos[1] + j] = (self.agents[n].density*pow(self._grid_size,2)*1.1*3)
                        heat_capacity[pos[0] + i, pos[1] - j] = (self.agents[n].density*pow(self._grid_size,2)*1.1*3)
                        heat_capacity[pos[0] - i, pos[1] + j] = (self.agents[n].density*pow(self._grid_size,2)*1.1*3)
                        heat_capacity[pos[0] - i, pos[1] - j] = (self.agents[n].density*pow(self._grid_size,2)*1.1*3)
                        
                        """Thermal/Temperature Map"""
                        self._thermal_map[pos[0] + i, pos[1] + j] = self.agents[n].body_temp[self.agents[n].body_radius-1+i][self.agents[n].body_radius-1+j]
                        self._thermal_map[pos[0] + i, pos[1] - j] = self.agents[n].body_temp[self.agents[n].body_radius-1+i][self.agents[n].body_radius-1-j]
                        self._thermal_map[pos[0] - i, pos[1] + j] = self.agents[n].body_temp[self.agents[n].body_radius-1-i][self.agents[n].body_radius-1+j]
                        self._thermal_map[pos[0] - i, pos[1] - j] = self.agents[n].body_temp[self.agents[n].body_radius-1-i][self.agents[n].body_radius-1-j]
                        
                        """Agent ID Map"""
                        agent_id[pos[0] + i, pos[1] + j] = n
                        agent_id[pos[0] + i, pos[1] - j] = n
                        agent_id[pos[0] - i, pos[1] + j] = n
                        agent_id[pos[0] - i, pos[1] - j] = n
        
        """Fill Air Gaps"""
        for i in range(self._env_size[0]):
            for j in range(self._env_size[1]):
                if(self._material_map[i][j]==0 and prev_material_map>0):
                    self._thermal_map[i][j]=self.ambient_air_temp
        
        """Compute Heat Exchange Map"""
        heat_exchange=np.zeros(shape=self._env_size, dtype=float)
        for i in range(self._env_size[0]):
            for j in range(self._env_size[1]):
                
                """Environmental Cooling and Heat Generation"""
                if(self._material_map[i][j]==0):
                    heat_exchange[i][j]-=self.air_conductivity*pow(self._grid_size,2)/(self._grid_size/2)*(self._ambient_air_temp-self._thermal_map[i][j])
                elif(self._material_map[i][j]==1):
                    heat_exchange[i][j]+=self.agents[agent_id[i][j]]._metabolism                
                
                """Neighborhood Heat Exchange"""
                if(i>0):
                    heat_res=0
                    """Agent"""                    
                    if(self._material_map[i][j]==0):
                        heat_res+=1/(self.air_conductivity*pow(self._grid_size,2)/(self._grid_size/2))            
                    elif(self._material_map[i][j]>0):
                        heat_res+=1/(self.agents[agent_id[i][j]]._internal_conductivity*pow(self._grid_size,2)/(self._grid_size/2))
                        if(self._material_map[i][j]==3 and (self._material_map[i-1][j]>2 or self._material_map[i-1][j]<1)):
                            heat_res+=1/(self.agents[agent_id[i][j]]._external_conductivity*pow(self._grid_size,2)/(self.agents[agent_id[i][j]]._insulation_thickness))
                    """Adjacent"""                    
                    if(self._material_map[i-1][j]==0):
                        heat_res+=1/(self.air_conductivity*pow(self._grid_size,2)/(self._grid_size/2))            
                    elif(self._material_map[i-1][j]>0):
                        heat_res+=1/(self.agents[agent_id[i-1][j]]._internal_conductivity*pow(self._grid_size,2)/(self._grid_size/2))
                        if(self._material_map[i-1][j]==3 and (self._material_map[i][j]>2 or self._material_map[i][j]<1)):
                            heat_res+=1/(self.agents[agent_id[i-1][j]]._external_conductivity*pow(self._grid_size,2)/(self.agents[agent_id[i-1][j]]._insulation_thickness))
                    heat_exchange[i][j]+=((1/heat_res)*(self._thermal_map[i-1][j]-self._thermal_map[i][j])/2)
                    
                if(j>0):
                    heat_res=0
                    """Agent"""                    
                    if(self._material_map[i][j]==0):
                        heat_res+=1/(self.air_conductivity*pow(self._grid_size,2)/(self._grid_size/2))            
                    elif(self._material_map[i][j]>0):
                        heat_res+=1/(self.agents[agent_id[i][j]]._internal_conductivity*pow(self._grid_size,2)/(self._grid_size/2))
                        if(self._material_map[i][j]==3 and (self._material_map[i][j-1]>2 or self._material_map[i][j-1]<1)):
                            heat_res+=1/(self.agents[agent_id[i][j]]._external_conductivity*pow(self._grid_size,2)/(self.agents[agent_id[i][j]]._insulation_thickness))
                    """Adjacent"""                    
                    if(self._material_map[i][j-1]==0):
                        heat_res+=1/(self.air_conductivity*pow(self._grid_size,2)/(self._grid_size/2))            
                    elif(self._material_map[i][j-1]>0):
                        heat_res+=1/(self.agents[agent_id[i-1][j]]._internal_conductivity*pow(self._grid_size,2)/(self._grid_size/2))
                        if(self._material_map[i][j-1]==3 and (self._material_map[i][j]>2 or self._material_map[i][j]<1)):
                            heat_res+=1/(self.agents[agent_id[i][j-1]]._external_conductivity*pow(self._grid_size,2)/(self.agents[agent_id[i][j-1]]._insulation_thickness))
                    heat_exchange[i][j]+=((1/heat_res)*(self._thermal_map[i][j-1]-self._thermal_map[i][j])/2)
                    
                if(i<self._env_size[0]-1):
                    heat_res=0
                    """Agent"""                    
                    if(self._material_map[i][j]==0):
                        heat_res+=1/(self.air_conductivity*pow(self._grid_size,2)/(self._grid_size/2))            
                    elif(self._material_map[i][j]>0):
                        heat_res+=1/(self.agents[agent_id[i][j]]._internal_conductivity*pow(self._grid_size,2)/(self._grid_size/2))
                        if(self._material_map[i][j]==3 and (self._material_map[i+1][j]>2 or self._material_map[i+1][j]<1)):
                            heat_res+=1/(self.agents[agent_id[i][j]]._external_conductivity*pow(self._grid_size,2)/(self.agents[agent_id[i][j]]._insulation_thickness))
                    """Adjacent"""                    
                    if(self._material_map[i+1][j]==0):
                        heat_res+=1/(self.air_conductivity*pow(self._grid_size,2)/(self._grid_size/2))            
                    elif(self._material_map[i+1][j]>0):
                        heat_res+=1/(self.agents[agent_id[i+1][j]]._internal_conductivity*pow(self._grid_size,2)/(self._grid_size/2))
                        if(self._material_map[i+1][j]==3 and (self._material_map[i][j]>2 or self._material_map[i][j]<1)):
                            heat_res+=1/(self.agents[agent_id[i+1][j]]._external_conductivity*pow(self._grid_size,2)/(self.agents[agent_id[i+1][j]]._insulation_thickness))
                    heat_exchange[i][j]+=((1/heat_res)*(self._thermal_map[i+1][j]-self._thermal_map[i][j])/2)
                    
                if(j<self._env_size[0]-1):
                    heat_res=0
                    """Agent"""                    
                    if(self._material_map[i][j]==0):
                        heat_res+=1/(self.air_conductivity*pow(self._grid_size,2)/(self._grid_size/2))            
                    elif(self._material_map[i][j]>0):
                        heat_res+=1/(self.agents[agent_id[i][j]]._internal_conductivity*pow(self._grid_size,2)/(self._grid_size/2))
                        if(self._material_map[i][j]==3 and (self._material_map[i][j+1]>2 or self._material_map[i][j+1]<1)):
                            heat_res+=1/(self.agents[agent_id[i][j]]._external_conductivity*pow(self._grid_size,2)/(self.agents[agent_id[i][j]]._insulation_thickness))
                    """Adjacent"""                    
                    if(self._material_map[i][j+1]==0):
                        heat_res+=1/(self.air_conductivity*pow(self._grid_size,2)/(self._grid_size/2))            
                    elif(self._material_map[i][j+1]>0):
                        heat_res+=1/(self.agents[agent_id[i][j+1]]._internal_conductivity*pow(self._grid_size,2)/(self._grid_size/2))
                        if(self._material_map[i][j+1]==3 and (self._material_map[i][j]>2 or self._material_map[i][j]<1)):
                            heat_res+=1/(self.agents[agent_id[i][j+1]]._external_conductivity*pow(self._grid_size,2)/(self.agents[agent_id[i+1][j]]._insulation_thickness))
                    heat_exchange[i][j]+=((1/heat_res)*(self._thermal_map[i][j+1]-self._thermal_map[i][j])/2)
        
        """Update Thermal Map"""
        self._thermal_map+=heat_exchange/heat_capacity
        
        """Update Agent Temps"""
        for agent in self.agents:
            if(agent.alive):
                new_body_temp=np.zeros(shape=(2*agent.body_radius-1,2*agent.body_radius-1),dtype=float)
                pos=agent.position
                for i in range(agent.body_radius):
                    for j in range(agent.body_radius - i):
                        new_body_temp[agent.body_radius-1 + i, agent.body_radius-1 + j] = self._thermal_map[pos[0] + i, pos[1] + j]
                        new_body_temp[agent.body_radius-1 + i, agent.body_radius-1 - j] = self._thermal_map[pos[0] + i, pos[1] - j]
                        new_body_temp[agent.body_radius-1 - i, agent.body_radius-1 + j] = self._thermal_map[pos[0] - i, pos[1] + j]
                        new_body_temp[agent.body_radius-1 - i, agent.body_radius-1 - j] = self._thermal_map[pos[0] - i, pos[1] - j]
                agent.body_temp=new_body_temp
        
        LOG.warning("Thermal model not yet implemented. Nothing happens.")

    def run_epoch(self):
        """Run one epoch"""
        self._epoch += 1
        random.shuffle(self._agents)
        for agent in self._agents:
            neighbors = self.get_neighbors(agent)
            pos = agent.position
            size = agent.body_radius - 1
            thermal_points = {
                "up": self._thermal_map[pos[0] - size, pos[1]],
                "down": self._thermal_map[pos[0] + size, pos[1]],
                "left": self._thermal_map[pos[0], pos[1] - size],
                "right": self._thermal_map[pos[0], pos[1] + size],
            }
            move = agent.get_move(neighbors, thermal_points)
            old_position = agent.position
            agent.position = move
            if self.check_valid_pos(agent, move[0], move[1]):
                LOG.debug(f"Moving agent: {agent.position} -> {move}")
            else:
                LOG.debug(f"Move invalid: {agent.position} -> {move}")
                agent.position = old_position
        self.draw()

    def get_neighbors(self, test_agent: Agent) -> list[Agent]:
        """Get a list of neighbors in the sense radius"""
        neighbors = list()
        for agent in self._agents:
            if agent is test_agent:
                continue
            dist = self.manhatten_distance(test_agent, agent)
            if dist < agent.sense_radius:
                neighbors.append(agent)
        return neighbors

    def check_valid_pos(self, agent: Agent, row: int, col: int) -> bool:
        """Check if a new position is valid for an agent"""
        # Check bounds of environment
        if (row < agent.body_radius - 1) or (
                row > self.env_size[0] - agent.body_radius):
            return False
        if (col < agent.body_radius - 1) or (
                col > self.env_size[1] - agent.body_radius):
            return False
        for curr_agent in self._agents:
            if (curr_agent is not agent) and agent.is_collision(curr_agent):
                return False
        return True

    def manhatten_distance(self, agent1: Agent, agent2: Agent) -> int:
        """Calculate manhatten distance between two agents"""
        return (abs(agent1.position[0] - agent2.position[0]) +
                abs(agent1.position[1] - agent2.position[1]))

    def add_agent(self, agent: Agent) -> bool:
        """Add agent if no collisions"""
        if self.check_valid_pos(agent, agent.position[0], agent.position[1]):
            self._agents.append(agent)
            LOG.debug(f"Added agent number {len(self._agents)} at"
                      f"pos {agent.position}")
            return True
        return False

    def draw(self) -> None:
        """Draw the environment and save it as a PNG"""
        self._drawing_env = np.ones(
            shape=(self.env_size[0], self.env_size[1], 3),
            dtype=float,
        )
        for agent in self._agents:
            self.draw_agent(agent)
        fig, axis = plt.subplots()
        axis.imshow(self._drawing_env)
        axis.axis("off")
        axis.set_title(f"{self._name}\n" f"epoch {self._epoch:06d}")
        img_path = self._gif_img_dir.joinpath(f"epoch_{self._epoch:010d}.png")
        fig.savefig(img_path)
        fig.clf()
        plt.close()

    def draw_agent(self, agent):
        """Draw an agent in the environment"""
        pos = agent.position
        for i in range(agent.body_radius):
            for j in range(agent.body_radius - i):
                self._drawing_env[pos[0] + i, pos[1] + j] = agent.color
                self._drawing_env[pos[0] + i, pos[1] - j] = agent.color
                self._drawing_env[pos[0] - i, pos[1] + j] = agent.color
                self._drawing_env[pos[0] - i, pos[1] - j] = agent.color

    def save_gif(self) -> None:
        """Save the GIF"""
        LOG.info("Generating GIF...")
        images = []
        for path in sorted(list(self._gif_img_dir.iterdir())):
            LOG.debug(f"Adding {path}")
            image = Image.open(path)
            images.append(image.copy())
            image.close()
        gif_path = self._image_dir.joinpath(f"{self._file_name}.gif")
        images[0].save(
            gif_path,
            save_all=True,
            duration=100,
            append_images=images[1:],
            loop=0,
        )
        LOG.info(f"A GIF of the simulation has been saved in:\n{gif_path}")
