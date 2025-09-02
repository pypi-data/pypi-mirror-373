"""Script to explore task flag of package classifications

Use this folder for any work required to identify content of
data/flag/

This template illustrates identification of entity-relation model
"""
from logging import getLogger

import numpy as np
import pandas as pd
from dataio import datapackage as iodp
from templates import set_logger

logger = getLogger("root")
set_logger(
    filename=("classifications_flag.log"),
    path=".",
    log_level=20,
    overwrite=True,
    create_path=True,
)


logger.info("Started script to generate clean_classifications_flag.dataio.yam")

metadata_file = "clean_classifications_flag.dataio.yaml"
iodp.describe(full_path=metadata_file, overwrite=True)
iodp.plot(full_path=metadata_file, overwrite=True)
iodp.validate(full_path=metadata_file, overwrite=True)

logger.info("Finished script to generate clean_classifications_flag.dataio.yam")
