# -*- coding: utf-8 -*-
"""
Created on Sat Mar 20 01:35:25 2021

@author: liu
"""
import numpy as np
from matplotlib import pyplot as plt


def square_coord(n, vortex=True):
    """
    Generate coordinates of the contour on a square of size n.
    I did it at 3 am dont judge me.

    Parameters
    ----------
    n : int
        Size of the square.
    vortex : bool, optional
        whether to include the vertices. The default is True.

    Returns
    -------
    list of size-2 tuple
        (x,y) coordinates of the contour.

    """
    if n == 0:
        return [(0, 0)]
    if vortex:
        coords = [(n, n), (n, -n), (-n, n), (-n, -n)]
    else:
        coords = []
    for i in range(-n, n+1):
        if i == n or i == -n:
            continue
        coords.append((n, i))
        coords.append((i, n))
        coords.append((-n, i))
        coords.append((i, -n))
    return coords


def main(max_epoch):
    MAP_SIZE = 1000  # Dimension of the environment
    MAP_TEMP = 0     # Overall temp of the environment
    MAP_SINK = 1     # Rate of environment sinking heat
    RAD_SIZE = 20    # Temperature radiation size (square shape)
    PEN_SIZE = 5     # Penguin size (square shape)
    MOV_SIZE = 5     # Penguin moving size (only in four directions)
    POP_SIZE = 30    # Population size
    LIV_TEMP = 38    # Penguin surival temperature
    GET_TEMP = 0.01  # Penguins rate of getting temperature out of environment
    GEN_TEMP = 1     # Penguin rate of generating temperature in one epoch

    # Initialize the map with 2*MAP_SIZE and make the penguin group in center
    # I don't want to check boundary conditions lol
    pen_xs = np.random.choice(MAP_SIZE, POP_SIZE, replace=False) + MAP_SIZE / 2
    pen_xs = pen_xs.astype(np.int64)
    pen_ys = np.random.choice(MAP_SIZE, POP_SIZE, replace=False) + MAP_SIZE / 2
    pen_ys = pen_ys.astype(np.int64)
    # Initialize penguin temperature with normal temperature
    pen_temps = np.full(POP_SIZE, LIV_TEMP).astype(float)
    # Initialize map heatmap
    heatmap = np.full((2*MAP_SIZE, 2*MAP_SIZE), MAP_TEMP).astype(float)

    for epoch in range(max_epoch):
        """Sink the heat in the map
        """
        heatmap += (MAP_TEMP - heatmap)*MAP_SINK

        """Update heatmap with the penguins temp
        """
        for i in range(POP_SIZE):
            # Rule 1: grids with penguins has the penguin's temp
            for r in range(0, PEN_SIZE+1):
                for (dx, dy) in square_coord(r):
                    heatmap[pen_xs[i]+dx, pen_ys[i]+dy] += pen_temps[i]
            # Rule 2: grids around penguins has a linearly decaying temp field
            for r in range(PEN_SIZE+1, PEN_SIZE+RAD_SIZE+1):
                for (dx, dy) in square_coord(r):
                    heatmap[pen_xs[i]+dx, pen_ys[i]+dy] +=  \
                        pen_temps[i] * (1 - r / RAD_SIZE)

        """Update penguin position by surrounding temp
        Sum the total temperature on the penguin's four sides(corner excluded),
        then move towards/away from that direction depending if hot or cold
        """
        # Initialize a matrix that helps sample the surrounding temp, encoded
        # with direction info
        for i in range(POP_SIZE):
            ambient_temps = np.array([
                [1,  0, 0],  # on its east
                [-1, 0, 0],  # on its west
                [0,  1, 0],  # on its north
                [0, -1, 0],  # on its south
                ])
            for (dx, dy) in square_coord(PEN_SIZE, False):
                sense_temp = heatmap[pen_xs[i]+dx, pen_ys[i]+dy] + \
                    np.random.uniform(-1, 1)  # sensing has a slight error
                if dx == PEN_SIZE:
                    ambient_temps[0, 2] += sense_temp
                elif dx == -PEN_SIZE:
                    ambient_temps[1, 2] += sense_temp
                elif dy == PEN_SIZE:
                    ambient_temps[2, 2] += sense_temp
                elif dy == -PEN_SIZE:
                    ambient_temps[3, 2] += sense_temp
            # Penguin does not move if it's in a comfy temperature range
            if pen_temps[i] > LIV_TEMP - 2.0 and pen_temps[i] < LIV_TEMP + 2.0:
                continue
            else:
                # Sort the matrix by the last column
                ambient_temps = np.array(ambient_temps)
                ambient_temps = ambient_temps[np.argsort(ambient_temps[:, 2])]
            # Select the correct direction info
            if pen_temps[i] < LIV_TEMP:
                mov_x, mov_y = (ambient_temps[-1][0], ambient_temps[-1][1])
            elif pen_temps[i] > LIV_TEMP:
                mov_x, mov_y = (ambient_temps[0][0], ambient_temps[0][1])
            # Move the penguin by a direction, with a stride scaled with the
            # temp difference
            pen_xs[i] += mov_x*int(abs(pen_temps[i] - LIV_TEMP)/MOV_SIZE)
            pen_ys[i] += mov_y*int(abs(pen_temps[i] - LIV_TEMP)/MOV_SIZE)

        """Update penguin temperature based on heatmap and generate a tick of
        temp"""
        for i in range(POP_SIZE):
            pen_temps[i] = GET_TEMP * \
                heatmap[pen_xs[i], pen_ys[i]] - pen_temps[i]
            pen_temps[i] += GEN_TEMP

        """Plot the penguins
        """
        fig, ax = plt.subplots()
        ax.set_xlim((0, 2*MAP_SIZE))
        ax.set_xticks([])
        ax.set_ylim((0, 2*MAP_SIZE))
        ax.set_yticks([])
        ax.scatter(pen_xs, pen_ys, s=PEN_SIZE)
        fig.suptitle("Epoch {}".format(epoch))
        fig.savefig("Epoch_{}".format(epoch))
        fig.clf()
        # plt.show()


if __name__ == "__main__":
    main(200)
