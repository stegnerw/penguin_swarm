# -*- coding: utf-8 -*-
"""This module implements the Penguin agent.
"""
# Standard library
from __future__ import annotations
# Packages
import numpy as np
# Custom
from agent import Agent


class Penguin(Agent):
    """Penguin agent class."""
    def get_move(self, neighbors: list[Agent],
                 thermal_points: dict[str, float]) -> np.ndarray[int]:
        """Calculate the current move given the neighbors.

        Parameters
        ----------
        neighbors : list
            List of neighbors within sense_radius

        Returns
        tuple(int)
            Agent's move in the form (row, column)
        """
        return self.position + np.random.randint(-3, 4, size=2, dtype=int)
