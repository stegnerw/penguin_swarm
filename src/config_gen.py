#! /usr/bin/env python3
# -*- coding: utf-8 -*-
"""This module generates config files.
"""
# Standard library
import argparse
import configparser
import logging
import pathlib
# Packages
import coloredlogs
# Custom
from environment import Environment
from penguin import Penguin

###############################################################################
# Constant definitions
###############################################################################

LOG = logging.getLogger("penguin_swarm.config_gen")

# File paths
SRC_DIR = pathlib.Path(__file__).parent.resolve()
CFG_DIR = SRC_DIR.joinpath("cfg")
assert CFG_DIR.exists()
TEMPLATE_CFG = CFG_DIR.joinpath("template.ini")
assert TEMPLATE_CFG.exists()

# Outline the required sections and options of the INI config files
# TODO: Make each section hold a dictionary where the value is a function to
# parse the input properly.
CONFIG_SECTIONS = {
    "general": ["name", "make_gif"],
    "paths": ["image_dir"],
    "env": [
        "env_size", "grid_size", "time_step_size", "epochs",
        "air_conductivity", "initial_temp", "ambient_temp"
    ],
    "penguin": [
        "count", "body_radius", "sense_radius", "body_temp",
        "low_death_threshold", "high_death_threshold", "low_move_threshold",
        "high_move_threshold", "internal_conductivity",
        "external_conductivity", "insulation_thickness", "density",
        "movement_speed", "metabolism"
    ],
}

###############################################################################
# Function definitions
###############################################################################


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


###############################################################################
# Main function
###############################################################################


def main(log_level: int) -> int:
    """Main function

    Parameters
    ----------
    TODO
    """
    coloredlogs.install(
        level=log_level * 10,
        logger=LOG,
        milliseconds=True,
    )

    body_radii = [1, 2, 4, 7]
    sense_radii = [5, 10, 25, 50, 100]
    counts = [16, 32, 64, 128, 256]
    movement_speeds = [1, 2, 5, 10, 20]

    for br in body_radii:
        for sr in sense_radii:
            for c in counts:
                for ms in movement_speeds:
                    cfg_f_name = f"br{br}_sr{sr}_c{c}_ms{ms}.ini"
                    cfg_path = CFG_DIR.joinpath(cfg_f_name)
                    cfg_name = f"BR={br}, SR={sr}, C={c}, MS={ms}"

                    # Parse config file
                    config = parse_config(TEMPLATE_CFG)
                    if config is None:
                        LOG.error("Could not read config file")
                        break

                    # Overwrite testing configs
                    config["general"]["name"] = cfg_name
                    config["penguin"]["count"] = str(c)
                    config["penguin"]["body_radius"] = str(br)
                    config["penguin"]["sense_radius"] = str(sr)
                    config["penguin"]["movement_speed"] = str(ms)
                    with open(cfg_path, "w") as cfg_file:
                        config.write(cfg_file)

    LOG.info("Done.")
    logging.shutdown()
    return 0


if __name__ == "__main__":
    import sys
    args = parse_args()
    sys.exit(main(**vars(args)))
