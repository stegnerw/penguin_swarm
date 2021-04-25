# File: makefile
# Author: Wayne Stegner

# Project name
PROJECT = penguin_swarm

# Directory definitions
SRC_DIR = ./src
CFG_DIR = $(SRC_DIR)/cfg
IMG_DIR = ./img
SRC_FILES = $(wildcard $(SRC_DIR)/*.py)
CFG_FILES = $(wildcard $(CFG_DIR)/*.ini)
GEN_CFG_FILES = $(wildcard $(CFG_DIR)/auto_*.ini)
IMG_DIRS = $(patsubst $(CFG_DIR)/%.ini, $(IMG_DIR)/%, $(CFG_FILES))

.PHONY: all clean clean_cfg very_clean configs

all: $(IMG_DIRS) $(CFG_FILES) $(SRC_FILES)

clean:
	@rm -rf $(IMG_DIR) $(SRC_DIR)/__pycache__

clean_cfg:
	@rm -rf $(GEN_CFG_FILES)

very_clean: clean clean_cfg

$(IMG_DIR)/%: $(CFG_DIR)/%.ini $(SRC_FILES)
	$(SRC_DIR)/main.py -ll 3 $<

configs: $(SRC_DIR)/config_gen.py $(CFG_DIR)/template.ini
	$(SRC_DIR)/config_gen.py -ll 3
