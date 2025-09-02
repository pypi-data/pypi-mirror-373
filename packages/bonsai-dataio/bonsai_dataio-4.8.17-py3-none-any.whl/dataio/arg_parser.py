from logging import getLogger
from shutil import copytree

import yaml

from dataio.config import Config

from .set_logger import set_logger

logger = getLogger("root")


def arg_parser(package: object, main: object, argv: list):
    """Argument parser of main task executable.

    Parameters
    ----------
    package : obj
    main: obj
    argv: list
    """

    set_logger()
    logger.info(f"Executing Python package '{package.__name__}'")

    # validate package metadata
    for attr in ["STAGE", "TASKS"]:
        if attr not in dir(package):
            logger.error(f"Attribute '{attr}' is missing from package")
            raise

    help_str = (
        f"usage: python -m {package.__name__} [-h] [-r YAML] [-e PATH]"
        "\n"
        "\noptions:"
        "\n  -h, --help             show this help message and exit"
        "\n  -r , --run RUN         path to configuration YAML file"
        "\n  -e, --export EXPORT    path to store exported data"
        "\n                           (returns error if path exists)"
        "\n  -o, --overwrite EXPORT path to store exported data"
        "\n                           (overwrites if path exists)"
        "\n"
    )

    if len(argv) == 1:
        logger.warning("Not enough arguments provided:\n" f"{help_str}")
    else:
        # run
        if argv[1] in ["-r", "--run"]:
            if len(argv) == 2:
                logger.warning(
                    "No configuration file __name__ provided, "
                    "assumed default = 'config.yaml'"
                )
                argv.append("config.yaml")

            try:
                with open(argv[2], "r") as stream:
                    config = Config(**yaml.safe_load(stream))
                logger.info(f"Read configuration file '{argv[2]}'")
            except FileNotFoundError:
                logger.error(
                    "Error loading configuration yaml "
                    f"'{argv[2]}'. Maybe a path or file format "
                    "issue."
                )
                raise
            main(config=config)
        # export
        elif argv[1] in ["-e", "--export"]:
            if len(argv) == 2:
                argv.append(".")
            logger.info(
                f"Exporting data from package "
                f"{package.__name__} to path '{argv[2]}'."
            )
            copytree(package.EXPORT_PATH, argv[2], dirs_exist_ok=False)
            logger.info("Finished exporting data.")
        # overwrite
        elif argv[1] in ["-o", "--overwrite"]:
            if len(argv) == 2:
                argv.append(".")
            logger.info(
                f"Exporting data from package "
                f"{package.__name__} to path '{argv[2]}'."
            )
            copytree(package.EXPORT_PATH, argv[2], dirs_exist_ok=True)
            logger.info("Finished exporting data.")
        elif argv[1] in ["-h", "--help"]:
            logger.info(help_str)
        else:
            logger.info("Invalid arguments provided.")
            logger.info(help_str)
