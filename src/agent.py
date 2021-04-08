#! /usr/bin/env python3
# -*- coding: utf-8 -*-
"""This module contains the Agent abstract base class.
"""
# Standard library
from __future__ import annotations
from abc import ABC, abstractmethod


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
        body_temp_low_threshold: float,
        body_temp_high_threshold: float,
    ):
        self._row = row
        self._col = col
        self._body_radius = body_radius
        self._sense_radius = sense_radius
        self._body_temp = body_temp
        self._body_temp_low_threshold = body_temp_low_threshold
        self._body_temp_high_threshold = body_temp_high_threshold
        self._alive = True

    @abstractmethod
    def get_move(self, neighbors: list[Agent]) -> tuple(int):
        """Calculate the current move given the neighbors.

        Parameters
        ----------
        neighbors : list
            List of neighbors within sense_radius

        Returns
        tuple(int)
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
    def body_temp(self) -> float:
        """float: Internal body temperature of the agent.

        The setter checks the temperature thresholds and the agent dies if the
        set temp is outside of the range.
        """
        return self._body_temp

    @body_temp.setter
    def body_temp(self, body_temp: float) -> None:
        self._body_temp = body_temp
        if (self._body_temp > self._body_temp_high_threshold
                or self._body_temp < self._body_temp_low_threshold):
            self.alive = False

    @property
    def position(self) -> tuple(int):
        """tuple(int): Current coordinates of the agent (x, y)"""
        return (self._row, self._col)

    @position.setter
    def position(self, position: tuple(int)) -> None:
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
