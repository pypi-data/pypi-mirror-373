__author__ = "Simon Nilsson"

import glob
import os
import subprocess
import sys
import threading
from copy import deepcopy
from datetime import datetime
from tkinter import *
from typing import Optional, Union

import numpy as np
from PIL import Image, ImageTk

import simba
from simba.labelling.extract_labelled_frames import AnnotationFrameExtractor
from simba.mixins.config_reader import ConfigReader
from simba.mixins.pop_up_mixin import PopUpMixin
from simba.plotting.frame_mergerer_ffmpeg import FrameMergererFFmpeg
from simba.ui.px_to_mm_ui import GetPixelsPerMillimeterInterface
from simba.ui.tkinter_functions import (CreateLabelFrameWithIcon,
                                        CreateToolTip, DropDownMenu, Entry_Box,
                                        FileSelect, FolderSelect, SimbaButton,
                                        SimbaCheckbox, SimBADropDown,
                                        SimBALabel)
from simba.utils.checks import (check_ffmpeg_available,
                                check_file_exist_and_readable,
                                check_if_dir_exists,
                                check_if_string_value_is_valid_video_timestamp,
                                check_int, check_nvidea_gpu_available,
                                check_str,
                                check_that_hhmmss_start_is_before_end)
from simba.utils.data import convert_roi_definitions
from simba.utils.enums import Dtypes, Formats, Keys, Links, Options, Paths
from simba.utils.errors import (CountError, DuplicationError,
                                FFMPEGCodecGPUError, FrameRangeError,
                                InvalidInputError, MixedMosaicError,
                                NoChoosenClassifierError, NoDataError,
                                NoFilesFoundError, NotDirectoryError,
                                ResolutionError)
from simba.utils.lookups import (get_color_dict, get_ffmpeg_crossfade_methods,
                                 get_fonts, percent_to_crf_lookup)
from simba.utils.printing import SimbaTimer, stdout_success
from simba.utils.read_write import (
    check_if_hhmmss_timestamp_is_valid_part_of_video,
    concatenate_videos_in_folder, find_all_videos_in_directory, find_core_cnt,
    find_files_of_filetypes_in_directory, find_video_of_file, get_fn_ext,
    get_video_meta_data, seconds_to_timestamp, str_2_bool,
    timestamp_to_seconds)
from simba.utils.warnings import FrameRangeWarning
from simba.video_processors.brightness_contrast_ui import \
    brightness_contrast_ui
from simba.video_processors.clahe_ui import interactive_clahe_ui
from simba.video_processors.extract_seqframes import extract_seq_frames
from simba.video_processors.multi_cropper import MultiCropper
from simba.video_processors.video_processing import (
    VideoRotator, batch_convert_video_format, batch_create_frames,
    batch_video_to_greyscale, change_fps_of_multiple_videos, change_img_format,
    change_single_video_fps, clahe_enhance_video, clahe_enhance_video_mp,
    clip_video_in_range, clip_videos_by_frame_ids, convert_to_avi,
    convert_to_bmp, convert_to_jpeg, convert_to_mov, convert_to_mp4,
    convert_to_png, convert_to_tiff, convert_to_webm, convert_to_webp,
    convert_video_powerpoint_compatible_format, copy_img_folder,
    create_average_frm, crop_multiple_videos, crop_multiple_videos_polygons,
    crop_single_video, crop_single_video_circle, crop_single_video_polygon,
    crossfade_two_videos, downsample_video, extract_frame_range,
    extract_frames_single_video, flip_videos, frames_to_movie, gif_creator,
    multi_split_video, remove_beginning_of_video, resize_videos_by_height,
    resize_videos_by_width, reverse_videos, roi_blurbox, rotate_video,
    superimpose_elapsed_time, superimpose_frame_count, superimpose_freetext,
    superimpose_overlay_video, superimpose_video_names,
    superimpose_video_progressbar, temporal_concatenation, upsample_fps,
    video_bg_subtraction, video_bg_subtraction_mp, video_concatenator,
    video_to_bw, video_to_greyscale, watermark_video)

sys.setrecursionlimit(10**7)



class Convert2MP4PopUp(PopUpMixin):
    """
    :example:
    >>> Convert2MP4PopUp()
    """
    def __init__(self):

        self.MP4_CODEC_LK = {'HEVC (H.265)': 'libx265', 'H.264 (AVC)': 'libx264', 'VP9': 'vp9', 'GPU (h264_cuvid)': 'h264_cuvid', 'Guaranteed powerpoint compatible': 'powerpoint'}
        self.cpu_codec_qualities = list(range(10, 110, 10))
        self.gpu_codec_qualities = ['Low', 'Medium', 'High']
        super().__init__(title="CONVERT VIDEOS TO MP4", icon='mp4')
        settings_frm = CreateLabelFrameWithIcon(parent=self.main_frm, header="SETTINGS", icon_name='settings', icon_link=Links.VIDEO_TOOLS.value, padx=5, pady=5, relief='solid')

        self.quality_dropdown = SimBADropDown(parent=settings_frm, dropdown_options=self.cpu_codec_qualities, label="OUTPUT VIDEO QUALITY:", label_width=30, dropdown_width=40, value=60)
        self.codec_dropdown = SimBADropDown(parent=settings_frm, dropdown_options=list(self.MP4_CODEC_LK.keys()), label="COMPRESSION CODEC:", label_width=30, dropdown_width=40, value='H.264 (AVC)', command=self.update_quality_dropdown)
        settings_frm.grid(row=0, column=0, sticky=NW, padx=10, pady=10)
        self.quality_dropdown.grid(row=0, column=0, sticky=NW)
        self.codec_dropdown.grid(row=1, column=0, sticky=NW)

        single_video_frm = CreateLabelFrameWithIcon(parent=self.main_frm, header="SINGLE VIDEO", icon_name='video', icon_link=Links.VIDEO_TOOLS.value, padx=5, pady=5, relief='solid')
        self.selected_video = FileSelect(single_video_frm, "VIDEO PATH:", title="Select a video file", lblwidth=30, file_types=[("VIDEO FILE", Options.ALL_VIDEO_FORMAT_STR_OPTIONS.value)])

        single_video_run = SimbaButton(parent=single_video_frm, txt="RUN - SINGLE VIDEO", img='rocket', cmd=self.run, cmd_kwargs={'multiple': False})

        single_video_frm.grid(row=1, column=0, sticky=NW, padx=10, pady=10)
        self.selected_video.grid(row=0, column=0, sticky=NW)
        single_video_run.grid(row=1, column=0, sticky=NW)

        multiple_video_frm = CreateLabelFrameWithIcon(parent=self.main_frm, header="VIDEO DIRECTORY", icon_name='stack', icon_link=Links.VIDEO_TOOLS.value, padx=5, pady=5, relief='solid')
        self.selected_video_dir = FolderSelect(multiple_video_frm, "VIDEO DIRECTORY PATH:", title="Select a video directory", lblwidth=30)

        multiple_video_run = SimbaButton(parent=multiple_video_frm, txt="RUN - VIDEO DIRECTORY", img='rocket', cmd=self.run, cmd_kwargs={'multiple': True})
        multiple_video_frm.grid(row=2, column=0, sticky=NW, padx=10, pady=10)
        multiple_video_run.grid(row=1, column=0, sticky=NW)
        self.selected_video_dir.grid(row=0, column=0, sticky=NW)


        self.main_frm.mainloop()

    def update_quality_dropdown(self, k):
        if k == 'GPU (h264_cuvid)': option_lst = self.gpu_codec_qualities
        else: option_lst = self.cpu_codec_qualities
        self.quality_dropdown.dropdown['values'] = option_lst
        self.quality_dropdown.dropdown.set(option_lst[0])

    def run(self, multiple: bool):
        if not multiple:
            video_path = self.selected_video.file_path
            check_file_exist_and_readable(file_path=video_path)
        else:
            video_path = self.selected_video_dir.folder_path
            check_if_dir_exists(in_dir=video_path, source=self.__class__.__name__)
        codec = self.MP4_CODEC_LK[self.codec_dropdown.getChoices()]
        quality = self.quality_dropdown.getChoices()
        threading.Thread(target=convert_to_mp4(path=video_path, codec=codec, quality=quality))



Convert2MP4PopUp()