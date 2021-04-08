# -*- coding: utf-8 -*-
"""This module implements the Obstacle agent.
"""
from __future__ import annotations
from agent import Agent


class Obstacle(Agent):
    """Obstacle agent class.

    This is implemented as an agent as an easy way for collision detection.
    """
    def get_move(self, neighbors: list[Agent]) -> tuple(float):
        """Calculate the current move given the neighbors.

        The obstacle agent will never move, and this is intentional.

        Parameters
        ----------
        neighbors : list
            List of neighbors within sense_radius

        Returns
        tuple(float)
            Agent's move in the form (direction, velocity)
        """
        return (0.0, 0.0)
