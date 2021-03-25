# -*- coding: utf-8 -*-
"""This module implements the Penguin agent.
"""
from __future__ import annotations
from agent import Agent


class Penguin(Agent):
    """Penguin agent class."""
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
        return (0.0, 0.0)
