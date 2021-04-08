# -*- coding: utf-8 -*-
"""This module implements the Penguin agent.
"""
from __future__ import annotations
from agent import Agent


class Penguin(Agent):
    """Penguin agent class."""
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
        return (self._row, self._col)
