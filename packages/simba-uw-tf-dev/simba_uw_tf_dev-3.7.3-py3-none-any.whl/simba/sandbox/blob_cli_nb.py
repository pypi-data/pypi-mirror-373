####

# To perform blob tracking  in a notebook or through the command line, we first need a configuration `.json` file that holds both general settings, and settings for how to
# perform blob tracking on each video.

# For an example of this file, see THIS file. https://github.com/sgoldenlab/simba/blob/master/misc/blob_definitions_ex.json
# This file is typically created in the settings windows documented [HERE] https://github.com/sgoldenlab/simba/blob/master/docs/blob_track.md or [HERE](https://simba-uw-tf-dev.readthedocs.io/en/latest/tutorials_rst/blob_tracking.html)
# However, now we are executing the blob tracking outside of the GUI, and we have to create this manually.
# One way to create this is to modify the example file [HERE] - https://github.com/sgoldenlab/simba/blob/master/misc/blob_definitions_ex.json.
# A second option is to convert the pickle file created by teh GUI into a json and modify this file.



### PERFORM NECESSERY IMPORTS
from simba.utils.cli.cli_tools import blob_tracker

#### DEFINE THE PATH TO YOUR CONFIG FILE
CONFIG_PATH = r"C:\Users\sroni\Downloads\blob_definitions_ex.json"

#### RUN TEH BLOB TRACKER
blob_tracker(config_path=CONFIG_PATH)