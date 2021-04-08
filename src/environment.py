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
# Packages
import coloredlogs
import matplotlib.pyplot as plt
import numpy as np
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
        config: configparser.ConfigParser,
    ):
        coloredlogs.install(
            level=log_level * 10,
            logger=LOG,
            milliseconds=True,
        )
        self._name = config["general"]["name"]
        self._env_size = tuple(map(int, config["env"]["env_size"].split(", ")))
        # Environment for drawing
        self._env = np.ones(
            shape=(self.env_size[0], self.env_size[1], 3),
            dtype=float,
        )
        # Environment for tracking thermals
        self._thermal_env = np.empty(shape=self._env_size, dtype=float)
        self._agents = list()
        self._time = 0
        # Initialize image directories
        self._image_dir = PROJ_DIR.joinpath(config["paths"]["image_dir"])
        self._image_dir.mkdir(mode=0o775, exist_ok=True)
        self._image_dir = self._image_dir.joinpath(self._name)
        self._image_dir.mkdir(mode=0o775, exist_ok=True)
        self._gif_img_dir = self._image_dir.joinpath("gif_imgs")
        self._gif_img_dir.mkdir(mode=0o775, exist_ok=True)
        LOG.debug(f"Initialized Environment: {self._name}")

    @property
    def env_size(self) -> list[tuple[int]]:
        """int: The size of the environment in the form (h, w) tiles"""
        return self._env_size

    def run(self, epochs: int) -> None:
        """Run for a set number of epochs"""
        # Draw initial board
        self.draw()
        for epoch in range(epochs):
            LOG.debug(f"Begin epoch {epoch}")
            self.run_epoch()

    def run_epoch(self):
        """Run one epoch"""
        random.shuffle(self._agents)
        for agent in self._agents:
            move = agent.get_move
            if self.check_valid_pos(agent, move[0], move[1]):
                LOG.debug(f"Moving agent: {agent.position} -> {move}")
                agent.position = move
                self._time += 1
                self.draw()
            else:
                LOG.debug(f"Move invalid: {agent.position} -> {move}")

    def check_valid_pos(self, agent, row, col):
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

    def add_agent(self, agent: Agent) -> bool:
        """Add agent if no collisions"""
        if self.check_valid_pos(agent, agent.position[0], agent.position[1]):
            self._agents.append(agent)
            LOG.debug(f"Added agent number {len(self._agents)}")
            return True
        return False

    def draw(self) -> None:
        """Draw the environment and save it as a PNG"""
        self._env = np.ones(
            shape=(self.env_size[0], self.env_size[1], 3),
            dtype=float,
        )
        for agent in self._agents:
            color = (random.random(), random.random(), random.random())
            self.draw_agent(agent, color)
        fig, axis = plt.subplots()
        axis.imshow(self._env)
        axis.axis("off")
        axis.set_title(f"{self._name}\n" f"step {self._time:06d}")
        img_path = self._gif_img_dir.joinpath(f"step_{self._time:010d}.png")
        fig.savefig(img_path)
        fig.clf()
        plt.close()

    def draw_agent(self, agent, color):
        """Draw an agent in the environment"""
        pos = agent.position
        for i in range(agent.body_radius):
            for j in range(agent.body_radius - i):
                self._env[pos[0] + i, pos[1] + j] = color
                self._env[pos[0] + i, pos[1] - j] = color
                self._env[pos[0] - i, pos[1] + j] = color
                self._env[pos[0] - i, pos[1] - j] = color
