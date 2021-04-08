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
        self._epoch = 0
        # Initialize image directories
        self._image_dir = PROJ_DIR.joinpath(config["paths"]["image_dir"])
        self._image_dir.mkdir(mode=0o775, exist_ok=True)
        self._image_dir = self._image_dir.joinpath(self._name)
        self._image_dir.mkdir(mode=0o775, exist_ok=True)
        self._gif_img_dir = self._image_dir.joinpath("gif_imgs")
        shutil.rmtree(self._gif_img_dir, ignore_errors=True)
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
            LOG.info(f"Begin epoch {epoch}/{epochs}")
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
        # TODO: Implement this
        LOG.warning("Thermal model not yet implemented. Nothing happens.")

    def run_epoch(self):
        """Run one epoch"""
        self._epoch += 1
        random.shuffle(self._agents)
        for agent in self._agents:
            move = agent.get_move(self.get_neighbors(agent))
            old_position = agent.position
            agent.position = move
            if self.check_valid_pos(agent, move[0], move[1]):
                self._time += 1
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
        self._env = np.ones(
            shape=(self.env_size[0], self.env_size[1], 3),
            dtype=float,
        )
        for agent in self._agents:
            self.draw_agent(agent)
        fig, axis = plt.subplots()
        axis.imshow(self._env)
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
                self._env[pos[0] + i, pos[1] + j] = agent.color
                self._env[pos[0] + i, pos[1] - j] = agent.color
                self._env[pos[0] - i, pos[1] + j] = agent.color
                self._env[pos[0] - i, pos[1] - j] = agent.color

    def save_gif(self) -> None:
        """Save the GIF"""
        LOG.info("Generating GIF...")
        images = []
        for path in sorted(list(self._gif_img_dir.iterdir())):
            LOG.debug(f"Adding {path}")
            image = Image.open(path)
            images.append(image.copy())
            image.close()
        gif_path = self._image_dir.joinpath(f"{self._name}.gif")
        images[0].save(
            gif_path,
            save_all=True,
            duration=25,
            append_images=images[1:],
            loop=0,
        )
        LOG.info(f"A GIF of the simulation has been saved in:\n{gif_path}")
