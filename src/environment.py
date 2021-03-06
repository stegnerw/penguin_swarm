#! /usr/bin/env python3
# -*- coding: utf-8 -*-
"""This module contains the Environment class.

The Environment implements a container to hold agents and control interactions.
"""
# Standard library
from __future__ import annotations
import logging
import pathlib
import random
import re
import shutil
import colorsys
# Packages
import coloredlogs
import matplotlib.pyplot as plt
import numpy as np
from PIL import Image
# Custom
from agent import Agent

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
        env_size: np.ndarray,
        grid_size: float,
        time_step_size: float,
        epochs: int,
        air_conductivity: float,
        initial_air_temp: float,
        ambient_air_temp: float,
        make_gif: bool,
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
        self._make_gif = make_gif
        self._image_dir = image_dir
        self._alive_agents = 0
        self._alive_agents_plot = list()
        self._epochs_plot = list()
        self._temps_plot = list()
        self._temps_error_std = list()
        self._temps_error_interval = int(5)
        self._temps_error_x = list()
        self._temps_error_y = list()

        # Drawing environment
        self._drawing_env = np.ones(
            shape=(self.env_size[0], self.env_size[1], 3),
            dtype=float,
        )

        # Thermal model related members
        self._thermal_map = np.full(shape=self._env_size,
                                    fill_value=initial_air_temp,
                                    dtype=float)
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
        self._gif_img_dir = self._image_dir.joinpath("gif_imgs")
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
        total_agents = np.sum([a.alive for a in self._agents])
        self._alive_agents = np.sum([a.alive for a in self._agents])
        self._alive_agents_plot.append(self._alive_agents / total_agents)
        self._temps_plot.append(np.mean([a.core_temp for a in self._agents if a.alive]))
        self._temps_error_std.append(np.std([a.core_temp for a in self._agents if a.alive]))
        self._temps_error_x.append(self._epoch)
        self._temps_error_y.append(np.mean([a.core_temp for a in self._agents if a.alive]))
        self._epochs_plot.append(self._epoch)
        for epoch in range(self._epochs):
            LOG.info(f"Begin epoch {epoch + 1}/{self._epochs}: "
                     f"{self._alive_agents}"
                     f"/{len(self._agents)} agents alive")
            self.run_epoch()
            self.update_simple_thermal()
            self._alive_agents = np.sum([a.alive for a in self._agents])
            self._alive_agents_plot.append(self._alive_agents / total_agents)
            self._epochs_plot.append(self._epoch)
            if np.sum([a.alive for a in self._agents]) == 0:
                self._temps_plot.append(self._temps_plot[-1])
                LOG.info("Simulation early stop due to 0 agent alive")
                break
            if epoch % self._temps_error_interval == 0:
                self._temps_error_std.append(np.std([a.core_temp for a in self._agents if a.alive]))
                self._temps_error_x.append(self._epoch)
                self._temps_error_y.append(np.mean([a.core_temp for a in self._agents if a.alive]))
            self._temps_plot.append(np.mean([a.core_temp for a in self._agents if a.alive]))
        self.save_gif()
        self.plot_vs_epoch()
        shutil.rmtree(self._gif_img_dir, ignore_errors=True)
    
    def update_simple_thermal(self) -> None:
        A=self._grid_size*1.1
        
        agent_body_temps=[]
        
        for n in self._agents:                       
            
            Q_meta=n._metabolism*pow(self._grid_size, 2)*1.1
            
            n_avg_temp=n.body_temp[n.body_radius-1][n.body_radius-1]            
            
            Q_env=n._internal_conductivity*A*(self._ambient_air_temp-n_avg_temp)
            
            Q_pop=0
            
            for m in self._agents:
                if(n is m):
                    continue
                else:
                    m_avg_temp=m.body_temp[m.body_radius-1][m.body_radius-1]            
                    
                    dist=(self.manhatten_distance(n,m)-n.body_radius-m.body_radius+1)*self._grid_size
                    
                    heat_res=n._insulation_thickness/(n._external_conductivity*A)
                    heat_res+=m._insulation_thickness/(m._external_conductivity*A)
                    heat_res+=dist/(self._air_conductivity*A)
                    
                    Q_pop+=(1/heat_res)*(m_avg_temp-n_avg_temp)
                    
            Q=(Q_meta+Q_env+Q_pop)*self._time_step_size
            
            n_avg_temp+=Q/(n._density*pow(self._grid_size,2)*1.1*3E3)
            
            body_temp=np.zeros((2*n.body_radius-1,2*n.body_radius-1))                    
            for i in range(n.body_radius):
                    for j in range(n.body_radius - i):
                        body_temp[n.body_radius-1+i][n.body_radius-1+j]=n_avg_temp
                        body_temp[n.body_radius-1+i][n.body_radius-1-j]=n_avg_temp
                        body_temp[n.body_radius-1-i][n.body_radius-1+j]=n_avg_temp
                        body_temp[n.body_radius-1-i][n.body_radius-1-j]=n_avg_temp
            
            agent_body_temps.append(body_temp)
            
        for n in range(len(self._agents)):
            
            self._agents[n].body_temp=agent_body_temps[n]
    
    def update_thermal(self) -> None:
        """Update the thermals of the environment.

        This will include calculating the temperature of every tile,
        calculating the body temperature of each agent, and anything
        else included in the thermal model.
        """
        prev_material_map = self._material_map
        """Update Maps"""
        agent_id = np.full(shape=self._env_size, fill_value=-1, dtype=int)
        heat_capacity = np.full(shape=self._env_size,
                                fill_value=(1.657 * pow(self._grid_size, 2) *
                                            1.1 * 0.716E3),
                                dtype=float)
        self._material_map = np.zeros(shape=self._env_size, dtype=float)
        for n in range(len(self._agents)):
            if (self._agents[n].alive):
                pos = self._agents[n].position
                for i in range(self._agents[n]._body_radius):
                    for j in range(self._agents[n]._body_radius - i):
                        """Material Map"""
                        if (i == 0 and j == 0):
                            self._material_map[pos[0], pos[1]] = 1
                        elif (i == self._agents[n]._body_radius - 1
                              or j == self._agents[n]._body_radius - 1):
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
                        heat_capacity[pos[0] + i,
                                      pos[1] + j] = (self._agents[n]._density *
                                                     pow(self._grid_size, 2) *
                                                     1.1 * 3E3)
                        heat_capacity[pos[0] + i,
                                      pos[1] - j] = (self._agents[n]._density *
                                                     pow(self._grid_size, 2) *
                                                     1.1 * 3E3)
                        heat_capacity[pos[0] - i,
                                      pos[1] + j] = (self._agents[n]._density *
                                                     pow(self._grid_size, 2) *
                                                     1.1 * 3E3)
                        heat_capacity[pos[0] - i,
                                      pos[1] - j] = (self._agents[n]._density *
                                                     pow(self._grid_size, 2) *
                                                     1.1 * 3E3)
                        """Thermal/Temperature Map"""
                        self._thermal_map[pos[0] + i, pos[1] +
                                          j] = self._agents[n].body_temp[
                                              self._agents[n].body_radius - 1 +
                                              i][self._agents[n].body_radius -
                                                 1 + j]
                        self._thermal_map[pos[0] + i, pos[1] -
                                          j] = self._agents[n].body_temp[
                                              self._agents[n].body_radius - 1 +
                                              i][self._agents[n].body_radius -
                                                 1 - j]
                        self._thermal_map[pos[0] - i, pos[1] +
                                          j] = self._agents[n].body_temp[
                                              self._agents[n].body_radius - 1 -
                                              i][self._agents[n].body_radius -
                                                 1 + j]
                        self._thermal_map[pos[0] - i, pos[1] -
                                          j] = self._agents[n].body_temp[
                                              self._agents[n].body_radius - 1 -
                                              i][self._agents[n].body_radius -
                                                 1 - j]
                        """Agent ID Map"""
                        agent_id[pos[0] + i, pos[1] + j] = n
                        agent_id[pos[0] + i, pos[1] - j] = n
                        agent_id[pos[0] - i, pos[1] + j] = n
                        agent_id[pos[0] - i, pos[1] - j] = n
        """Fill Air Gaps"""
        for i in range(self._env_size[0]):
            for j in range(self._env_size[1]):
                if (self._material_map[i][j] == 0.0
                        and prev_material_map[i][j] > 0):
                    self._thermal_map[i][j] = self._ambient_air_temp
        """Compute Heat Exchange Map"""
        heat_exchange = np.zeros(shape=self._env_size, dtype=float)
        for i in range(self._env_size[0]):
            for j in range(self._env_size[1]):
                """Environmental Cooling and Heat Generation"""
                if(self._material_map[i][j] == 0):
                    heat_exchange[i][j] += self._air_conductivity*4*self._grid_size*1.1*(self._ambient_air_temp-self._thermal_map[i][j])
                    
                elif(self._material_map[i][j] == 1):
                    heat_exchange[i][j] += self._agents[agent_id[i][j]]._metabolism*pow(self._grid_size,2)*1.1


                """Neighborhood Heat Exchange"""
                if (i > 0):
                    heat_res = 0
                    """Agent"""
                    if(self._material_map[i][j] == 0):
                        heat_res += 1/(self._air_conductivity *
                                       self._grid_size*1.1)
                    elif(self._material_map[i][j] > 0):
                        heat_res += 1/(self._agents[agent_id[i][j]]._internal_conductivity*self._grid_size*1.1/(self._grid_size/2))
                        if(self._material_map[i][j] == 3 and (self._material_map[i-1][j] > 2 or self._material_map[i-1][j] < 1)):
                            heat_res += 1/(self._agents[agent_id[i][j]]._external_conductivity*self._grid_size*1.1/(self._agents[agent_id[i][j]]._insulation_thickness))
                    """Adjacent"""
                    if(self._material_map[i-1][j] == 0):
                        heat_res += 1/(self._air_conductivity *
                                       self._grid_size*1.1)
                    elif(self._material_map[i-1][j] > 0):
                        heat_res += 1/(self._agents[agent_id[i-1][j]]._internal_conductivity*self._grid_size*1.1/(self._grid_size/2))
                        if(self._material_map[i-1][j] == 3 and (self._material_map[i][j] > 2 or self._material_map[i][j] < 1)):
                            heat_res += 1/(self._agents[agent_id[i-1][j]]._external_conductivity*self._grid_size*1.1/(self._agents[agent_id[i-1][j]]._insulation_thickness))
                            
                    heat_exchange[i][j] += ((1/heat_res) *
                                            (self._thermal_map[i-1][j]-self._thermal_map[i][j]))

                if(j > 0):
                    heat_res = 0
                    """Agent"""
                    if(self._material_map[i][j] == 0):
                        heat_res += 1/(self._air_conductivity *
                                       self._grid_size*1.1)
                    elif(self._material_map[i][j] > 0):
                        heat_res += 1/(self._agents[agent_id[i][j]]._internal_conductivity*self._grid_size*1.1/(self._grid_size/2))
                        if(self._material_map[i][j] == 3 and (self._material_map[i][j-1] > 2 or self._material_map[i][j-1] < 1)):
                            heat_res += 1/(self._agents[agent_id[i][j]]._external_conductivity*self._grid_size*1.1/(self._agents[agent_id[i][j]]._insulation_thickness))
                    """Adjacent"""
                    if(self._material_map[i][j-1] == 0):
                        heat_res += 1/(self._air_conductivity *
                                       self._grid_size*1.1)
                    elif(self._material_map[i][j-1] > 0):
                        heat_res += 1/(self._agents[agent_id[i-1][j]]._internal_conductivity*self._grid_size*1.1/(self._grid_size/2))
                        if(self._material_map[i][j-1] == 3 and (self._material_map[i][j] > 2 or self._material_map[i][j] < 1)):
                            heat_res += 1/(self._agents[agent_id[i][j-1]]._external_conductivity*self._grid_size*1.1/(self._agents[agent_id[i][j-1]]._insulation_thickness))
                            
                    heat_exchange[i][j] += ((1/heat_res)*(self._thermal_map[i]
                                            [j-1]-self._thermal_map[i][j]))

                if(i < self._env_size[0]-1):
                    heat_res = 0
                    """Agent"""
                    if(self._material_map[i][j] == 0):
                        heat_res += 1/(self._air_conductivity *
                                      self._grid_size*1.1)
                    elif(self._material_map[i][j] > 0):
                        heat_res += 1/(self._agents[agent_id[i][j]]._internal_conductivity*self._grid_size*1.1/(self._grid_size/2))
                        if(self._material_map[i][j] == 3 and (self._material_map[i+1][j] > 2 or self._material_map[i+1][j] < 1)):
                            heat_res += 1/(self._agents[agent_id[i][j]]._external_conductivity*self._grid_size*1.1/(self._agents[agent_id[i][j]]._insulation_thickness))
                    """Adjacent"""
                    if(self._material_map[i+1][j] == 0):
                        heat_res += 1/(self._air_conductivity *
                                       self._grid_size*1.1)
                    elif(self._material_map[i+1][j] > 0):
                        heat_res += 1/(self._agents[agent_id[i+1][j]]._internal_conductivity*self._grid_size*1.1/(self._grid_size/2))
                        if(self._material_map[i+1][j] == 3 and (self._material_map[i][j] > 2 or self._material_map[i][j] < 1)):
                            heat_res += 1/(self._agents[agent_id[i+1][j]]._external_conductivity*self._grid_size*1.1/(self._agents[agent_id[i+1][j]]._insulation_thickness))
                    
                    heat_exchange[i][j] += ((1/heat_res) *
                                            (self._thermal_map[i+1][j]-self._thermal_map[i][j]))

                if(j < self._env_size[1]-1):
                    heat_res = 0
                    """Agent"""
                    if(self._material_map[i][j] == 0):
                        heat_res += 1/(self._air_conductivity *
                                       self._grid_size*1.1)
                    elif(self._material_map[i][j] > 0):
                        heat_res += 1/(self._agents[agent_id[i][j]]._internal_conductivity*self._grid_size*1.1/(self._grid_size/2))
                        if(self._material_map[i][j] == 3 and (self._material_map[i][j+1] > 2 or self._material_map[i][j+1] < 1)):
                            heat_res += 1/(self._agents[agent_id[i][j]]._external_conductivity*self._grid_size*1.1/(self._agents[agent_id[i][j]]._insulation_thickness))
                    """Adjacent"""
                    if(self._material_map[i][j+1] == 0):
                        heat_res += 1/(self._air_conductivity *
                                       self._grid_size*1.1)
                    elif(self._material_map[i][j+1] > 0):
                        heat_res += 1/(self._agents[agent_id[i][j+1]]._internal_conductivity*self._grid_size*1.1/(self._grid_size/2))
                        if(self._material_map[i][j+1] == 3 and (self._material_map[i][j] > 2 or self._material_map[i][j] < 1)):
                            heat_res += 1/(self._agents[agent_id[i][j+1]]._external_conductivity*self._grid_size*1.1/(self._agents[agent_id[i][j+1]]._insulation_thickness))
                    
                    heat_exchange[i][j] += ((1/heat_res)*(self._thermal_map[i]
                                            [j+1]-self._thermal_map[i][j]))


        """Update Thermal Map"""
        self._thermal_map += ((heat_exchange / heat_capacity) *
                              self._time_step_size)
        """Update Agent Temps"""
        for agent in self._agents:
            if (agent.alive):
                new_body_temp = np.zeros(shape=(2 * agent.body_radius - 1,
                                                2 * agent.body_radius - 1),
                                         dtype=float)
                pos = agent.position
                for i in range(agent.body_radius):
                    for j in range(agent.body_radius - i):
                        new_body_temp[agent.body_radius - 1 + i,
                                      agent.body_radius - 1 +
                                      j] = self._thermal_map[pos[0] + i,
                                                             pos[1] + j]
                        new_body_temp[agent.body_radius - 1 + i,
                                      agent.body_radius - 1 -
                                      j] = self._thermal_map[pos[0] + i,
                                                             pos[1] - j]
                        new_body_temp[agent.body_radius - 1 - i,
                                      agent.body_radius - 1 +
                                      j] = self._thermal_map[pos[0] - i,
                                                             pos[1] + j]
                        new_body_temp[agent.body_radius - 1 - i,
                                      agent.body_radius - 1 -
                                      j] = self._thermal_map[pos[0] - i,
                                                             pos[1] - j]
                agent.body_temp = new_body_temp

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
            if dist < agent.sense_radius and agent.alive:
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
        if not self._make_gif:
            return
        LOG.debug("Drawing env")
        self._drawing_env = np.ones(
            shape=(self.env_size[0], self.env_size[1], 3),
            dtype=float,
        )
        #self.draw_map()
        for agent in self._agents:
            if agent.alive:
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

    def draw_map(self):
        normalized_temp = (self._thermal_map - self._ambient_air_temp) / \
            (self._agents[0]._high_death_threshold - self._initial_air_temp)
        normalized_temp = np.clip(0.5 - 0.5 * normalized_temp, 0.0, 0.5)
        for i in range(self._env_size[0]):
            for j in range(self.env_size[1]):
                self._drawing_env[i, j] = np.array(
                    colorsys.hsv_to_rgb(normalized_temp[i, j], 0.25, 1.0))

    def plot_vs_epoch(self):
        fig, survive_axis = plt.subplots()

        survive_axis.plot(
            self._epochs_plot,
            self._alive_agents_plot,
            label=f"{self._name}",
            color="blue",
        )
        survive_axis.set_xlabel("Epoch")
        survive_axis.set_xlim([0, len(self._epochs_plot)])
        survive_axis.set_ylim([0.0, 1.1])
        survive_axis.set_ylabel("Portion Surviving Penguins",
                                color="blue")


        temp_axis = survive_axis.twinx()
        temp_axis.plot(
            self._epochs_plot,
            self._temps_plot,
            label=f"{self._name}",
            color="red"
            )
        temp_axis.errorbar(
            self._temps_error_x,
            self._temps_error_y,
            yerr = self._temps_error_std,
            label = f"{self._name}",
            color = "red",
        )
        temp_axis.set_ylim([self._agents[0]._low_death_threshold,
                            self._agents[0]._high_death_threshold])
        temp_axis.set_ylabel(r"Average Core Temperature ($\degree$C)",
                             color="red")

        fig.suptitle("Colony Health vs Epoch")
        img_path = self._image_dir.joinpath(
            f"{self._file_name}_plot_vs_epoch.png")
        fig.savefig(img_path)
        fig.clf()
        plt.close()

    def save_gif(self) -> None:
        """Save the GIF"""
        if not self._make_gif:
            return
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
