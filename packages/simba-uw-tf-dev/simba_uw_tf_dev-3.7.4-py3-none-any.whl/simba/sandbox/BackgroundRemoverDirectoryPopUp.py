from tkinter import *
import os
from copy import deepcopy
from simba.ui.tkinter_functions import Entry_Box, CreateLabelFrameWithIcon, DropDownMenu, FolderSelect
from simba.mixins.pop_up_mixin import PopUpMixin
from simba.utils.lookups import get_color_dict
from simba.utils.enums import Links, Formats, Keys
from simba.utils.checks import check_int, check_if_string_value_is_valid_video_timestamp, check_that_hhmmss_start_is_before_end, check_if_dir_exists
from simba.utils.read_write import get_video_meta_data, find_all_videos_in_directory
from simba.utils.errors import DuplicationError, InvalidInputError, NoDataError
from simba.video_processors.video_processing import video_bg_subtraction, video_bg_subtraction_mp



class BackgroundRemoverDirectoryPopUp(PopUpMixin):
    def __init__(self):
        PopUpMixin.__init__(self, title="REMOVE BACKGROUNDS IN MULTIPLE VIDEOS")
        self.clr_dict = get_color_dict()
        settings_frm = CreateLabelFrameWithIcon(parent=self.main_frm, header="SETTINGS", icon_name=Keys.DOCUMENTATION.value, icon_link=Links.VIDEO_TOOLS.value)
        self.dir_path = FolderSelect(settings_frm, "VIDEO DIRECTORY:", lblwidth=45)
        self.bg_dir_path = FolderSelect(settings_frm, "BACKGROUND VIDEO DIRECTORY (OPTIONAL):", lblwidth=45)
        self.bg_clr_dropdown = DropDownMenu(settings_frm, "BACKGROUND COLOR:", list(self.clr_dict.keys()), labelwidth=45)
        self.fg_clr_dropdown = DropDownMenu(settings_frm, "FOREGROUND COLOR:", list(self.clr_dict.keys()), labelwidth=45)
        self.bg_start_eb = Entry_Box(parent=settings_frm, labelwidth=45, entry_box_width=15, fileDescription='BACKGROUND VIDEO START (FRAME # OR TIME):')
        self.bg_end_eb = Entry_Box(parent=settings_frm, labelwidth=45, entry_box_width=15, fileDescription='BACKGROUND VIDEO END (FRAME # OR TIME):')
        self.bg_start_eb.set_state(DISABLED)
        self.bg_end_eb.set_state(DISABLED)
        self.entire_video_as_bg_var = BooleanVar(value=True)
        self.entire_video_as_bg_cb = Checkbutton(settings_frm, text="COMPUTE BACKGROUND FROM ENTIRE VIDEO", font=Formats.FONT_REGULAR.value, variable=self.entire_video_as_bg_var, command=lambda: self.enable_entrybox_from_checkbox(check_box_var=self.entire_video_as_bg_var, entry_boxes=[self.bg_start_eb, self.bg_end_eb], reverse=True))
        self.multiprocessing_var = BooleanVar()
        self.multiprocess_cb = Checkbutton(settings_frm, text="MULTIPROCESS VIDEO (FASTER)", font=Formats.FONT_REGULAR.value, variable=self.multiprocessing_var, command=lambda: self.enable_dropdown_from_checkbox(check_box_var=self.multiprocessing_var, dropdown_menus=[self.multiprocess_dropdown]))
        self.multiprocess_dropdown = DropDownMenu(settings_frm, "CPU cores:", list(range(2, self.cpu_cnt)), "12")
        self.multiprocess_dropdown.setChoices(2)
        self.multiprocess_dropdown.disable()
        self.bg_clr_dropdown.setChoices('Black')
        self.fg_clr_dropdown.setChoices('White')
        self.bg_start_eb.entry_set('00:00:00')
        self.bg_end_eb.entry_set('00:00:20')

        settings_frm.grid(row=0, column=0, sticky=NW)
        self.dir_path.grid(row=0, column=0, sticky=NW)
        self.bg_dir_path.grid(row=1, column=0, sticky=NW)
        self.bg_clr_dropdown.grid(row=2, column=0, sticky=NW)
        self.fg_clr_dropdown.grid(row=3, column=0, sticky=NW)
        self.entire_video_as_bg_cb.grid(row=4, column=0, sticky=NW)
        self.bg_start_eb.grid(row=5, column=0, sticky=NW)
        self.bg_end_eb.grid(row=6, column=0, sticky=NW)
        self.multiprocess_cb.grid(row=7, column=0, sticky=NW)
        self.multiprocess_dropdown.grid(row=7, column=1, sticky=NW)
        self.create_run_frm(run_function=self.run)
        #self.main_frm.mainloop()

    def run(self):
        videos_directory_path = self.dir_path.folder_path
        bg_videos_directory_path = self.bg_dir_path.folder_path
        check_if_dir_exists(in_dir=videos_directory_path)
        bg_clr = self.colors_dict[self.bg_clr_dropdown.getChoices()]
        fg_clr = self.colors_dict[self.fg_clr_dropdown.getChoices()]
        if bg_clr == fg_clr:
            raise DuplicationError(msg=f'The background and foreground color cannot be the same color ({fg_clr})', source=self.__class__.__name__)
        video_paths = find_all_videos_in_directory(directory=videos_directory_path, as_dict=True, raise_error=True)
        if os.path.isdir(bg_videos_directory_path):
            bg_video_paths = find_all_videos_in_directory(directory=bg_videos_directory_path, as_dict=True, raise_error=True)
            video_paths_names, bg_video_paths_names = list(video_paths.keys()), list(bg_video_paths.keys())
            missing_bg_videos = [x for x in video_paths_names if x not in bg_video_paths_names]
            if len(missing_bg_videos) > 0:
                raise NoDataError(msg=f'Not all videos in {videos_directory_path} directory are represented in the {bg_videos_directory_path} directory', source=self.__class__.__name__)
        else:
            bg_video_paths = deepcopy(video_paths)
        if not self.entire_video_as_bg_var.get():
            start, end = self.bg_start_eb.entry_get.strip(), self.bg_end_eb.entry_get.strip()
            int_start, _ = check_int(name='', value=start, min_value=0, raise_error=False)
            int_end, _ = check_int(name='', value=end, min_value=0, raise_error=False)
            if int_start and int_end:
                bg_start_time, bg_end_time = None, None
                bg_start_frm, bg_end_frm = int(int_start), int(int_end)
                if bg_start_frm >= bg_end_frm:
                    raise InvalidInputError(msg=f'Start frame has to be before end frame (start: {bg_start_frm}, end: {bg_end_frm})', source=self.__class__.__name__)
            else:
                check_if_string_value_is_valid_video_timestamp(value=start, name='START FRAME')
                check_if_string_value_is_valid_video_timestamp(value=end, name='END FRAME')
                check_that_hhmmss_start_is_before_end(start_time=start, end_time=end, name='START AND END TIME')
                bg_start_frm, bg_end_frm = None, None
                bg_start_time, bg_end_time = start, end

        for cnt, (video_name, video_path) in enumerate(video_paths.items()):
            print(f'Running background subtraction for video {video_name}... (Video {cnt+1}/{len(list(video_paths.keys()))})')
            bg_video_path = bg_video_paths[video_name]
            if self.entire_video_as_bg_var.get():
                bg_video_meta_data = get_video_meta_data(video_path=bg_video_path)
                bg_start_frm, bg_end_frm = 0, bg_video_meta_data['frame_count']
                bg_start_time, bg_end_time = None, None

            if not self.multiprocessing_var.get():
                video_bg_subtraction(video_path=video_path,
                                     bg_video_path=bg_video_path,
                                     bg_start_frm=bg_start_frm,
                                     bg_end_frm=bg_end_frm,
                                     bg_start_time=bg_start_time,
                                     bg_end_time=bg_end_time,
                                     bg_color=bg_clr,
                                     fg_color=fg_clr)
            else:
                core_cnt = int(self.multiprocess_dropdown.getChoices())
                video_bg_subtraction_mp(video_path=video_path,
                                        bg_video_path=bg_video_path,
                                        bg_start_frm=bg_start_frm,
                                        bg_end_frm=bg_end_frm,
                                        bg_start_time=bg_start_time,
                                        bg_end_time=bg_end_time,
                                        bg_color=bg_clr,
                                        fg_color=fg_clr,
                                        core_cnt=core_cnt)



        # else:
        #     bg_video_meta_data = get_video_meta_data(video_path=bg_video)
        #     bg_start_frm, bg_end_frm = 0, bg_video_meta_data['frame_count']
        #     bg_start_time, bg_end_time = None, None



        #
        # self.video_path = FileSelect(settings_frm, "VIDEO PATH:", title="Select a video file", file_types=[("VIDEO", Options.ALL_VIDEO_FORMAT_OPTIONS.value)], lblwidth=45)
        # self.bg_video_path = FileSelect(settings_frm, "BACKGROUND REFERENCE VIDEO PATH (OPTIONAL):", title="Select a video file", file_types=[("VIDEO", Options.ALL_VIDEO_FORMAT_OPTIONS.value)], lblwidth=45)
        # self.bg_clr_dropdown = DropDownMenu(settings_frm, "BACKGROUND COLOR:", list(self.clr_dict.keys()), labelwidth=45)
        # self.fg_clr_dropdown = DropDownMenu(settings_frm, "FOREGROUND COLOR:", list(self.clr_dict.keys()), labelwidth=45)
        # self.bg_start_eb = Entry_Box(parent=settings_frm, labelwidth=45, entry_box_width=15, fileDescription='BACKGROUND VIDEO START (FRAME # OR TIME):')
        # self.bg_end_eb = Entry_Box(parent=settings_frm, labelwidth=45, entry_box_width=15, fileDescription='BACKGROUND VIDEO END (FRAME # OR TIME):')

#
#BackgroundRemoverDirectoryPopUp()