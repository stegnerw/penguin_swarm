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

        # Nothing to target when there is no neighors sensed
        best_pos = np.array(self.position) +np.random.randint(-3, 4, size=2, dtype=int)

        if (len(neighbors)==0):
            return best_pos

        # Collect relative position of neighbors
        neighbors_rpos = np.stack([n.position - self.position
                                  for n in neighbors])
        if self._movement_policy == "average":
            target_pos = np.sum(neighbors_rpos, axis=0)
            # Average policy takes means of all agent positions, set as target
        elif self._movement_policy == "closest":
            best_neighbor_i = np.argmin(
                np.abs(neighbors_rpos).sum(axis=1))
            target_pos = neighbors_rpos[best_neighbor_i]
            # Closest policy target the closest agent

        # Decide to move toward/away from target, or stay in place
        if self.core_temp < self._low_move_threshold:
            target_pos = target_pos + self.position
        elif self.core_temp > self._high_move_threshold:
            target_pos = -1*target_pos + self.position
        else:
            return best_pos

        # Calculate the optimal final position closest to target
        for step in range(self._movement_speed):
            distances = [
                abs(best_pos[0] + 0 - target_pos[0]) +
                    abs(best_pos[1] + 0 - target_pos[1]),  # stay
                abs(best_pos[0] + 0 - target_pos[0]) +
                    abs(best_pos[1] + 1 - target_pos[1]),  # up
                abs(best_pos[0] + 0 - target_pos[0]) +
                    abs(best_pos[1] - 1 - target_pos[1]),  # down
                abs(best_pos[0] - 1 - target_pos[0]) +
                    abs(best_pos[1] + 0 - target_pos[1]),  # left
                abs(best_pos[0] + 1 - target_pos[0]) +
                    abs(best_pos[1] + 0 - target_pos[1])   # right
            ]
            direction = np.argmin(distances)
            if direction == 1:
                best_pos[1] += 1
            elif direction == 2:
                best_pos[1] += -1
            elif direction == 3:
                best_pos[0] += -1
            elif direction == 4:
                best_pos[0] += 1

        return best_pos
