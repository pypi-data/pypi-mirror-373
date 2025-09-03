from simba.utils.read_write import find_files_of_filetypes_in_directory
from simba.utils.enums import Options
from simba.roi_tools.roi_ui import ROI_ui
from simba.roi_tools.roi_utils import multiply_ROIs


# DEFINE THE PATH TO THE SIMBA PROJECT CONFIG, AND THE PATH TO THE DIRECTORY IN SIMBA WHERE THE VIDEOS ARE STORED.
PROJECT_CONFIG_PATH = r"C:\troubleshooting\mitra\project_folder\project_config.ini"
VIDEO_DIR_PATH = r'C:\troubleshooting\mitra\project_folder\videos'

#CREATE A LIST OF PATHS TO THE VIDEO FILES THAT EXIST IN THE SIMBA PROJECT
video_file_paths = find_files_of_filetypes_in_directory(directory=VIDEO_DIR_PATH, extensions=Options.ALL_VIDEO_FORMAT_OPTIONS.value)

#WE CAN PRINT IT OUT TO SEE HOW IT LOOKS. IN THIS PROJECT WE HAVE 100 VIDEOS
print(video_file_paths)

# WE RUN THE ROI DRAWING INTERFACE AND DRAW ROIs ON THE FIRST VIDEO IN THE LIST.
# ONCE THE ROIs ARE DRAWN ON THIS VIDEO, REMEMBER TO CLICK "SAVE ROI DATA", AND CLOSE THE INTERFACE WINDOWS.
ROI_ui(config_path=PROJECT_CONFIG_PATH, video_path=video_file_paths[0])

#NEXT, WE MULTIPLY ALL THE ROIs ON THE FIRST VIDEO ON THE LIST ON ALL OTHE VIDEOS IN THE SIMBA PROJECT.
multiply_ROIs(config_path=PROJECT_CONFIG_PATH, filename=video_file_paths[0])


#FINALLY, WE START TO ITERATE OVER ALL OTHER VIDEOS IN THE PROJECT (OMITTING THE FIRST VIDEO), AND CORRECT THE ROIs.
# I DON'T HAVE A GOOD WAY OF AUTMATICALLY OPENING THE NEXT VIDEO ONCE A VIDEO IS CLOSED AT THE MOMENT, SO WILL HAVE TO MANUALLY CHANGE `video_file_paths[1]` TO `video_file_paths[2]` etc...
_ = ROI_ui(config_path=PROJECT_CONFIG_PATH, video_path=video_file_paths[1])
















