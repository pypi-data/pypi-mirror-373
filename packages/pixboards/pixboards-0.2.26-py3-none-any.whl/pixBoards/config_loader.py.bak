import os

import yaml

from pixBoards.arguments import args
from pixBoards.log_utils import setup_logger

logger = setup_logger(__name__)

from . import configTemplate


def load_config(yml_path):
    # print("loading config")
    try:
        with open(yml_path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f)
    except:
        logger.warning(
            "does a config.yml exist in this dir? if no then use --makeConfig"
        )
        exit(1)


def makeconfig():
    cfFile = "config.yml"
    logger.info("making config")
    try:
        with open(cfFile, "w") as f:
            f.write(configTemplate)
            exit(1)
    except FileExistsError:
        pass  # Skip if file already exists


if args.makeConfig:
    makeconfig()

config = {}

if args.config:
    configFile = args.config
else:
    configFile = "config.yml"
config = load_config(configFile)
if config is None:
    logger.warning("You should probably use --makeConfig")
config["col_count"] = args.col if args.col else config.get("col_count", 5)
config["margin"] = args.margin if args.margin else config.get("margin", 20)

masterDir = config["masterDir"]
if args.config:
    masterDir = os.path.join(
        os.path.dirname(masterDir), os.path.splitext(os.path.basename(configFile))[0]
    )

suffix = ""

if args.upload:
    suffix = "_upload"
# elif args.imageLists or args.useLists:
#     suffix = "_imglist"

outputDir = masterDir + suffix
