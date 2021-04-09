#! /usr/bin/env python3
# -*- coding: utf-8 -*-
"""This module is the main module.
"""
# Standard library
import argparse
import configparser
import datetime
import logging
import random
import pathlib
# Packages
import coloredlogs
# Custom
from environment import Environment
from penguin import Penguin

################################################################################
# Constant definitions
################################################################################

LOG = logging.getLogger("penguin_swarm.main")

# File paths
SRC_DIR = pathlib.Path(__file__).parent.resolve()
PROJ_DIR = SRC_DIR.parent

# Outline the required sections and options of the INI config files
# TODO: Make each section hold a dictionary where the value is a function to
# parse the input properly.
CONFIG_SECTIONS = {
    "general": ["name"],
    "paths": ["image_dir"],
    "env": [
        "env_size", "grid_size", "time_step_size", "epochs",
        "air_conductivity", "initial_temp", "ambient_temp"
    ],
    "penguin": [
        "count", "body_radius", "sense_radius", "body_temp",
        "body_temp_low_threshold", "body_temp_high_threshold"
    ],
}

################################################################################
# Function definitions
################################################################################


def parse_args(arg_list: list[str] = None):
    """Parse the arguments

    Parameters
    ----------
    arg_list : list[str]

    Notes
    -----
    I don't know how the type hints should look so I have omitted them.
    """
    parser = argparse.ArgumentParser(
        description="A penguin swarm simulator",
        formatter_class=argparse.RawTextHelpFormatter,
    )
    parser.add_argument("config_file", help="Path to the configuration file")
    parser.add_argument(
        "-ll",
        "--log_level",
        help="""Set the logging level:
        1 = DEBUG
        2 = INFO
        3 = WARNING
        4 = ERROR
        5 = CRITICAL""",
        type=int,
        choices=range(1, 6),
        default=2,
    )
    return parser.parse_args(args=arg_list)


def parse_config(config_file: str) -> configparser.ConfigParser:
    """Parse the config file

    Parameters
    ----------
    config_file : str
        Path to the configuration file
    """
    config_file = pathlib.Path(config_file).resolve()
    if not config_file.exists():
        LOG.error(f"Config file not found {str(config_file)}")
        return None
    LOG.debug(f"Config file found {str(config_file)}")
    config = configparser.ConfigParser()
    config.read(config_file)
    for section in CONFIG_SECTIONS:
        if not config.has_section(section):
            LOG.error(f"Config missing section {section}")
            return None
        LOG.debug(f"Found section {section}")
        for option in CONFIG_SECTIONS[section]:
            if not config.has_option(section, option):
                LOG.error(f"Config missing option {section}:{option}")
                return None
            LOG.debug(f"Found option {section}:{option}")
    return config


################################################################################
# Main function
################################################################################


def main(config_file: str, log_level: int) -> int:
    """Main function
6
    Parameters
    ----------
    TODO
    """
    coloredlogs.install(
        level=log_level * 10,
        logger=LOG,
        milliseconds=True,
    )
    config = parse_config(config_file)
    if config is None:
        LOG.error("Could not read config file")
        return 1
    env_size = tuple(map(int, config["env"]["env_size"].split(", ")))
    env = Environment(
        log_level,
        config["general"]["name"],
        config["paths"]["image_dir"],
        env_size,
        float(config["env"]["grid_size"]),
        float(config["env"]["time_step_size"]),
        int(config["env"]["epochs"]),
        float(config["env"]["air_conductivity"]),
        float(config["env"]["initial_temp"]),
        float(config["env"]["ambient_temp"]),
    )
    added_penguins = 0
    while added_penguins < int(config["penguin"]["count"]):
        penguin = Penguin(
            row=random.randrange(env_size[0]),
            col=random.randrange(env_size[1]),
            body_radius=int(config["penguin"]["body_radius"]),
            sense_radius=int(config["penguin"]["sense_radius"]),
            body_temp=float(config["penguin"]["body_temp"]),
            body_temp_low_threshold=float(
                config["penguin"]["body_temp_low_threshold"]),
            body_temp_high_threshold=float(
                config["penguin"]["body_temp_high_threshold"]),
        )
        if env.add_agent(penguin):
            added_penguins += 1
    # env.draw()
    env.run(int(config["env"]["epochs"]))
    LOG.info("Done.")
    logging.shutdown()
    return 0


if __name__ == "__main__":
    import sys
    args = parse_args()
    sys.exit(main(**vars(args)))
