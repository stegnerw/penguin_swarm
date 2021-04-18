#! /usr/bin/env python3
# -*- coding: utf-8 -*-
"""This module contains the Agent abstract base class.
"""
# Standard library
from __future__ import annotations
from abc import ABC, abstractmethod, abstractproperty
# Packages
import numpy as np


class Agent(ABC):
    """Agent abstract base class.

    Parameters
    ----------
    row, col : int
        Starting position for the agent.
    body_radius : int
        Body size radius.
    sense_radius : int
        Radius for sensing other agents.
    body_temp : float
        Initial body temperature.

    Notes
    -----
    This is preliminary. It can change based on future needs, as long as
    dependencies are also changed.
    """
    def __init__(
        self,
        row: int,
        col: int,
        body_radius: int,
        sense_radius: int,
        body_temp: float,
        low_death_threshold: float,
        high_death_threshold: float,
        low_move_threshold: float,
        high_move_threshold: float,
        internal_conductivity: float,
        external_conductivity: float,
        insulation_thickness: float,
        density: float,
        movement_speed: int,
        metabolism: float,
    ):
        self._row = row
        self._col = col
        self._body_radius = body_radius
        self._sense_radius = sense_radius
        self._body_temp = np.full(shape=(2*body_radius-1,2*body_radius-1), fill_value=body_temp, dtype=float)
        self._low_death_threshold = low_death_threshold
        self._high_death_threshold = high_death_threshold
        self._low_move_threshold = low_move_threshold
        self._high_move_threshold = high_move_threshold
        self._internal_conductivity = internal_conductivity
        self._external_conductivity = external_conductivity
        self._insulation_thickness = insulation_thickness
        self._density = density
        self._movement_speed = movement_speed
        self._metabolism = metabolism
        self._alive = True
        self._color = None
        

    @abstractmethod
    def get_move(self, neighbors: list[Agent],
                 thermal_points: dict[str, float]) -> np.ndarray[int]:
        """Calculate the current move given the neighbors.

        Parameters
        ----------
        neighbors : list[Agent]
            List of neighbors within sense_radius

        Returns
        np.ndarray[int]
            Agent's move in the form (row, column)
        """
        ...

    @property
    def body_radius(self) -> int:
        """int: Radius of the agent body."""
        return self._body_radius

    @body_radius.setter
    def body_radius(self, body_radius: int):
        self._body_radius = abs(int(body_radius))

    @property
    def sense_radius(self) -> int:
        """int: Radius of the agent sensing other agents."""
        return self._sense_radius

    @sense_radius.setter
    def sense_radius(self, sense_radius: float):
        self._sense_radius = abs(int(sense_radius))

    @property
    def alive(self) -> bool:
        """bool: Whether or not the penguin is alive."""
        return self._alive

    @alive.setter
    def alive(self, alive: bool) -> None:
        self._alive = alive

    def kill(self) -> None:
        """Kill the current agent."""
        self.alive = False

    @property
    def body_temp(self) -> np.ndarray[float]:
        """float: Internal body temperature of the agent.

        The setter checks the temperature thresholds and the agent dies if the
        set temp is outside of the range.
        """
        return self._body_temp

    @body_temp.setter
    def body_temp(self, body_temp: np.ndarray[float]) -> None:
        self._body_temp = body_temp
        if (self._body_temp[self._body_radius-1][self._body_radius-1] > self._high_death_threshold
                or self._body_temp[self._body_radius-1][self._body_radius-1] < self._low_death_threshold):
            self.alive = False

    @property
    def position(self) -> np.ndarray[int]:
        """np.ndarray[int]: Current coordinates of the agent (x, y)"""
        return np.array((self._row, self._col), dtype=int)

    @position.setter
    def position(self, position: np.ndarray[int]) -> None:
        self._row = int(position[0])
        self._col = int(position[1])

    def is_collision(self, agent: Agent) -> bool:
        """Check if there is a collision between a given agent"""
        diffs = list()
        diffs.append(abs(self.position[0] - agent.position[0]))
        diffs.append(abs(self.position[1] - agent.position[1]))
        diff = sum(diffs)
        min_diff = self.body_radius + agent.body_radius - 1
        return diff < min_diff

    @property
    def color(self) -> np.ndarray[float]:
        """np.ndarray[float] : Color to display the agent"""
        if self._color is None:
            self._color = np.random.random_sample(size=3)
        return self._color
