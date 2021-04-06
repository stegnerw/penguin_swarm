#! /usr/bin/env python3
# -*- coding: utf-8 -*-
"""This module contains the Agent abstract base class.
"""
from __future__ import annotations
from abc import ABC, abstractmethod


class Agent(ABC):
    """Agent abstract base class.

    Parameters
    ----------
    x_pos, y_pos : float
        Starting position for the agent.
    body_size : float
        Body size radius.
    sense_radius : float
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
        x_pos: int,
        y_pos: int,
        body_size: int,
        sense_radius: int,
        body_temp: float,
        body_temp_low_threshold: float,
        body_temp_high_threshold: float,
    ):
        self._x_pos = x_pos
        self._y_pos = y_pos
        self._body_size = body_size
        self._sense_radius = sense_radius
        self._body_temp = body_temp
        self._body_temp_low_threshold = body_temp_low_threshold
        self._body_temp_high_threshold = body_temp_high_threshold
        self._alive = True

    @abstractmethod
    def get_move(self, neighbors: list[Agent]) -> tuple(float):
        """Calculate the current move given the neighbors.

        Parameters
        ----------
        neighbors : list
            List of neighbors within sense_radius

        Returns
        tuple(float)
            Agent's move in the form (direction, velocity)
        """
        ...

    @property
    def body_size(self) -> int:
        """int: Radius of the agent body."""
        return self._body_size

    @body_size.setter
    def body_size(self, body_size: int):
        self._body_size = abs(int(body_size))

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
        return (self._x_pos, self._y_pos)

    @position.setter
    def position(self, position: tuple(float)) -> None:
        self._x_pos = int(position[0])
        self._y_pos = int(position[1])
