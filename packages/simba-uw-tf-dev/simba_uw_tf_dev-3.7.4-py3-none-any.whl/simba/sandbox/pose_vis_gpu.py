import os
from simba.data_processors.cuda.image import pose_plotter
from simba.utils.read_write import find_files_of_filetypes_in_directory, find_video_of_file


### DEFINITIONS
DATA_DIRECTORY = "/mnt/c/troubleshooting/mitra/project_folder/csv/outlier_corrected_movement_location/"
INPUT_VIDEO_DIRECTORY = "/mnt/c/troubleshooting/mitra/project_folder/videos/"
OUTPUT_VIDEO_DIRECTORY = "/mnt/c/troubleshooting/mitra/project_folder/videos/pose"
CIRCLE_SIZE = None # SET THIS VALUE TO AN INTEGER (E.G., 3) IF YOU DON'T WANT SIMBA TO ESTIMATE THE BEST CIRCLE SIZE FROM YOU VIDEO RESOLUTION
COLORS = 'Set1' # NAME OF COLOR PALLETE TO USE FOR THE BODY-PARTS. OTHER EXAMPLES INCLUDE EG :"Pastel1", "Pastel2","Paired", "Accent", "Dark2", "Set2", "Set3", "tab10", "tab20"
VERBOSE = True #If True, prints progress. If to much is beeing printed and you find it's spamming your console, set this to False.
BATCH_SIZE = 1500 #The number of frames to process concurrently on the GPU. Default: 750. Increase of host and device RAM allows it to improve runtime. Decrease if you hit memory errors.


## FIND ALL DATA FILES IN THE DATA_DIRECTORY
data_files = find_files_of_filetypes_in_directory(directory=DATA_DIRECTORY, extensions=['.csv'], as_dict=True, raise_error=True)
data_files


for data_file_name, data_file_path in data_files.items():
    video_input_path = find_video_of_file(video_dir=INPUT_VIDEO_DIRECTORY, filename=data_file_name, raise_error=False)
    video_output_path = os.path.join(OUTPUT_VIDEO_DIRECTORY, f'{data_file_name}.mp4')
    _ = pose_plotter(data=data_file_path, video_path=video_input_path, save_path=video_output_path, circle_size=CIRCLE_SIZE, colors=COLORS, verbose=VERBOSE, batch_size=BATCH_SIZE)
