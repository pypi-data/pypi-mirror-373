from typing import Union
import os
from tkinter import *

from simba.mixins.pop_up_mixin import PopUpMixin
from simba.utils.checks import check_if_dir_exists, check_int, check_str
from simba.utils.read_write import find_all_videos_in_directory, find_core_cnt, get_video_meta_data, str_2_bool, create_directory, remove_files
from simba.ui.tkinter_functions import CreateLabelFrameWithIcon, SimBALabel, SimbaButton, DropDownMenu, SimbaCheckbox, Entry_Box, FileSelect, FolderSelect
from simba.utils.enums import Formats
from simba.utils.errors import InvalidVideoFileError, NoDataError
from simba.roi_tools.roi_ui import ROI_ui
from simba.roi_tools.roi_utils import get_roi_data, multiply_ROIs

METHODS = ['absolute', 'light', 'dark']
ABSOLUTE = 'absolute'


class BlobTrackingUI(PopUpMixin):

    def __init__(self,
                 input_dir: Union[str, os.PathLike],
                 output_dir: Union[str, os.PathLike]):

        check_if_dir_exists(in_dir=input_dir); check_if_dir_exists(in_dir=output_dir)
        self.in_videos = find_all_videos_in_directory(directory=input_dir, as_dict=True, raise_error=True)
        self.input_dir, self.output_dir = input_dir, output_dir
        PopUpMixin.__init__(self, title="BLOB TRACKING", size=(2400, 600))
        self.len_max_char = len(max(list(self.in_videos.keys()), key=len))
        self.core_cnt = find_core_cnt()[0]
        self.get_quick_settings()
        self.get_main_table()
        self.get_main_table_entries()
        self.get_execute_btns()
        self.temp_dir = os.path.join(self.input_dir, '.temp')
        self.roi_exclusion_store = os.path.join(self.temp_dir, 'exclusion_definitions.h5')
        self.roi_inclusion_store = os.path.join(self.temp_dir, 'inclusion_definitions.h5')
        create_directory(paths=self.temp_dir, overwrite=True)
        self.main_frm.mainloop()

    def get_quick_settings(self):
        self.settings_frm = CreateLabelFrameWithIcon(parent=self.main_frm, header="SETTINGS", icon_name='settings')
        self.quick_settings_frm = LabelFrame(self.settings_frm, text="QUICK SETTINGS", padx=15, pady=15)
        self.quick_setting_threshold_dropdown = DropDownMenu(self.quick_settings_frm, "THRESHOLD", list(range(1, 101)), 20)
        self.quick_setting_threshold_dropdown.setChoices(30)
        self.quick_setting_threshold_btn = SimbaButton(parent=self.quick_settings_frm, txt='APPLY', img='tick',cmd=self._set_threshold, cmd_kwargs={'threshold': lambda: self.quick_setting_threshold_dropdown.getChoices()})
        self.quick_setting_method_dropdown = DropDownMenu(self.quick_settings_frm, "METHOD", METHODS, 20)
        self.quick_setting_method_dropdown.setChoices(ABSOLUTE)
        self.quick_setting_visualize_dropdown = DropDownMenu(self.quick_settings_frm, "VISUALIZE:", ['TRUE', 'FALSE'], 20)
        self.quick_setting_visualize_dropdown.setChoices('FALSE')
        self.quick_setting_visualize_btn = SimbaButton(parent=self.quick_settings_frm, txt='APPLY', img='tick', cmd=self._set_visualize, cmd_kwargs={'val': lambda: self.quick_setting_visualize_dropdown.getChoices()})


        self.quick_setting_method_btn = SimbaButton(parent=self.quick_settings_frm, txt='APPLY', img='tick', cmd=self._set_method, cmd_kwargs={'method': lambda: self.quick_setting_method_dropdown.getChoices()})
        self.quick_setting_window_size_eb = Entry_Box(parent=self.quick_settings_frm, entry_box_width=10, labelwidth=20, fileDescription='WINDOW SIZE:', validation='numeric')
        self.quick_setting_window_weight_eb = Entry_Box(parent=self.quick_settings_frm, entry_box_width=10, labelwidth=20, fileDescription='WINDOW WEIGHT:', validation='numeric')
        self.quick_setting_window_size_btn = SimbaButton(parent=self.quick_settings_frm, txt='APPLY', img='tick', cmd=self._set_window_size, cmd_kwargs={'size': lambda: self.quick_setting_window_size_eb.entry_get})
        self.quick_setting_window_weight_btn = SimbaButton(parent=self.quick_settings_frm, txt='APPLY', img='tick', cmd=self._set_window_weight, cmd_kwargs={'size': lambda: self.quick_setting_window_weight_eb.entry_get})
        self.settings_frm.grid(row=0, column=0, sticky=NW)
        self.quick_settings_frm.grid(row=0, column=0, sticky=NW)
        self.quick_setting_threshold_dropdown.grid(row=0, column=0, sticky=NW)
        self.quick_setting_threshold_btn.grid(row=0, column=1, sticky=NW)
        self.quick_setting_method_dropdown.grid(row=1, column=0, sticky=NW)
        self.quick_setting_method_btn.grid(row=1, column=1, sticky=NW)
        self.quick_setting_visualize_dropdown.grid(row=2, column=0, sticky=NW)
        self.quick_setting_visualize_btn.grid(row=2, column=1, sticky=NW)

        self.quick_setting_window_size_eb.grid(row=3, column=0, sticky=NW)
        self.quick_setting_window_weight_eb.grid(row=4, column=0, sticky=NW)
        self.quick_setting_window_size_btn.grid(row=3, column=1, sticky=NW)
        self.quick_setting_window_weight_btn.grid(row=4, column=1, sticky=NW)

        self.run_time_settings_frm = LabelFrame(self.settings_frm, text="RUN-TIME SETTINGS", padx=15, pady=15)
        self.gpu_cb, self.gpu_var = SimbaCheckbox(parent=self.run_time_settings_frm, txt='USE GPU', txt_img='gpu')
        self.core_cnt_dropdown = DropDownMenu(self.run_time_settings_frm, "CPU CORE COUNT:", list(range(1, self.core_cnt+1)), 25)
        self.core_cnt_dropdown.setChoices(self.core_cnt)
        self.bg_dir = FolderSelect(parent=self.run_time_settings_frm, folderDescription='BACKGROUND DIRECTORY:', lblwidth=25, initialdir=self.input_dir)
        self.bg_dir_apply = SimbaButton(parent=self.run_time_settings_frm, txt='APPLY', img='tick', cmd=self._apply_bg_dir, cmd_kwargs={'bg_dir': lambda: self.bg_dir.folder_path})
        self.duplicate_inclusion_zones_dropdown = DropDownMenu(self.run_time_settings_frm, "DUPLICATE INCLUSION ZONES:", list(self.in_videos.keys()), 25)
        self.duplicate_inclusion_zones_dropdown.setChoices(list(self.in_videos.keys())[0])
        self.duplicate_inclusion_zones_btn = SimbaButton(parent=self.run_time_settings_frm, txt='APPLY', img='tick', cmd=self._duplicate_inclusion_zones, cmd_kwargs={'video_name': lambda: self.duplicate_inclusion_zones_dropdown.getChoices()})
        self.duplicate_exclusion_zones_dropdown = DropDownMenu(self.run_time_settings_frm, "DUPLICATE EXCLUSION ZONES:", list(self.in_videos.keys()), 25)
        self.duplicate_exclusion_zones_dropdown.setChoices(list(self.in_videos.keys())[0])
        self.duplicate_exclusion_zones_btn = SimbaButton(parent=self.run_time_settings_frm, txt='APPLY', img='tick', cmd=self._duplicate_exclusion_zones, cmd_kwargs={'video_name': lambda: self.duplicate_exclusion_zones_dropdown.getChoices()})

        self.run_time_settings_frm.grid(row=0, column=1, sticky=NW)
        self.gpu_cb.grid(row=0, column=0, sticky=NW)
        self.core_cnt_dropdown.grid(row=1, column=0, sticky=NW)
        self.bg_dir.grid(row=2, column=0, sticky=NW)
        self.bg_dir_apply.grid(row=2, column=1, sticky=NW)
        self.duplicate_inclusion_zones_dropdown.grid(row=3, column=0, sticky=NW)
        self.duplicate_inclusion_zones_btn.grid(row=3, column=1, sticky=NW)
        self.duplicate_exclusion_zones_dropdown.grid(row=4, column=0, sticky=NW)
        self.duplicate_exclusion_zones_btn.grid(row=4, column=1, sticky=NW)


        self.execute_frm = LabelFrame(self.settings_frm, text="EXECUTE", padx=15, pady=15)
        self.run_btn = SimbaButton(parent=self.execute_frm, txt='RUN', img='rocket', cmd=self._initialize_run)
        self.remove_exclusion_zones_btn = SimbaButton(parent=self.execute_frm, txt='REMOVE EXCLUSION ZONES', img='trash', cmd=self._delete_exclusion_zone_data, cmd_kwargs=None, txt_clr='darkred')
        self.remove_inclusion_zones_btn = SimbaButton(parent=self.execute_frm, txt='REMOVE INCLUSION ZONES', img='trash', cmd=self._delete_inclusion_zone_data, cmd_kwargs=None, txt_clr='darkblue')

        self.execute_frm.grid(row=0, column=2, sticky=NW)
        self.run_btn.grid(row=0, column=0, sticky=NW)
        self.remove_inclusion_zones_btn.grid(row=1, column=0, sticky=NW)
        self.remove_exclusion_zones_btn.grid(row=2, column=0, sticky=NW)


    def get_main_table(self):
        self.headings = {}
        self.videos_frm = CreateLabelFrameWithIcon(parent=self.main_frm, header="VIDEOS", icon_name='video', pady=5, padx=15)
        self.headings['video_name'] = SimBALabel(parent=self.videos_frm, txt='VIDEO NAME', width=self.len_max_char, font=Formats.FONT_HEADER.value)
        self.headings['threshold'] = SimBALabel(parent=self.videos_frm, txt='THRESHOLD', width=self.len_max_char, font=Formats.FONT_HEADER.value)
        self.headings['exclusion_zones'] = SimBALabel(parent=self.videos_frm, txt='EXCLUSION ZONES', width=self.len_max_char, font=Formats.FONT_HEADER.value)
        self.headings['inclusion_zones'] = SimBALabel(parent=self.videos_frm, txt='INCLUSION ZONES', width=self.len_max_char, font=Formats.FONT_HEADER.value)
        self.headings['method'] = SimBALabel(parent=self.videos_frm, txt='METHOD', width=18, font=Formats.FONT_HEADER.value)
        self.headings['window_size'] = SimBALabel(parent=self.videos_frm, txt='WINDOW SIZE', width=18, font=Formats.FONT_HEADER.value)
        self.headings['window_weight'] = SimBALabel(parent=self.videos_frm, txt='WINDOW WEIGHT', width=18, font=Formats.FONT_HEADER.value)
        self.headings['bg_path'] = SimBALabel(parent=self.videos_frm, txt='REFERENCE', width=self.len_max_char + 5, font=Formats.FONT_HEADER.value)
        self.headings['visualize'] = SimBALabel(parent=self.videos_frm, txt='VISUALIZE', width=12, font=Formats.FONT_HEADER.value)
        for cnt, (k, v) in enumerate(self.headings.items()):
            v.grid(row=0, column=cnt, sticky=NW)
        self.videos_frm.grid(row=1, column=0, sticky=NW)

    def get_main_table_entries(self):
        self.videos = {}
        for video_cnt, (video_name, video_path) in enumerate(self.in_videos.items()):
            self.videos[video_name] = {}
            self.videos[video_name]['name_lbl'] = SimBALabel(parent=self.videos_frm, txt=video_name, width=self.len_max_char + 5, font=Formats.FONT_HEADER.value)
            self.videos[video_name]["threshold_dropdown"] = DropDownMenu(self.videos_frm, "", list(range(1, 100)), 0)
            self.videos[video_name]["threshold_dropdown"].setChoices(30)
            self.videos[video_name]["exclusion_btn"] = Button(self.videos_frm, text="SET EXCLUSION ZONES", fg="black", command=lambda k=self.videos[video_name]['name_lbl']["text"]: self._launch_set_exlusion_zones(k))
            self.videos[video_name]["inclusion_btn"] = Button(self.videos_frm, text="SET INCLUSION ZONES", fg="black", command=lambda k=self.videos[video_name]['name_lbl']["text"]: self._launch_set_inclusion_zones(k))
            self.videos[video_name]["method_dropdown"] = DropDownMenu(self.videos_frm, "", METHODS, 0)
            self.videos[video_name]["method_dropdown"].setChoices(ABSOLUTE)
            self.videos[video_name]["window_size_entry"] = Entry_Box(parent=self.videos_frm, entry_box_width=10, labelwidth=1, validation='numeric')
            self.videos[video_name]["window_size_entry"].entry_set('None')
            self.videos[video_name]["window_weight_entry"] = Entry_Box(parent=self.videos_frm, entry_box_width=10, labelwidth=1, validation='numeric')
            self.videos[video_name]["window_weight_entry"].entry_set('None')
            self.videos[video_name]["bg_file"] = FileSelect(parent=self.videos_frm)
            self.videos[video_name]["visualize_dropdown"] = DropDownMenu(self.videos_frm, "", ['TRUE', 'FALSE'], 0)
            self.videos[video_name]["visualize_dropdown"].setChoices('FALSE')
            self.videos[video_name]['name_lbl'].grid(row=video_cnt+1, column=0, sticky=NW)
            self.videos[video_name]['threshold_dropdown'].grid(row=video_cnt + 1, column=1, sticky=NW, padx=self.len_max_char + 30)
            self.videos[video_name]['exclusion_btn'].grid(row=video_cnt+1, column=2, sticky=NW, padx=self.len_max_char + 5)
            self.videos[video_name]['inclusion_btn'].grid(row=video_cnt+1, column=3, sticky=NW, padx=self.len_max_char + 5)
            self.videos[video_name]['method_dropdown'].grid(row=video_cnt+1, column=4, sticky=NW, padx=self.len_max_char + 5)
            self.videos[video_name]['window_size_entry'].grid(row=video_cnt+1, column=5)
            self.videos[video_name]['window_weight_entry'].grid(row=video_cnt+1, column=6)
            self.videos[video_name]['bg_file'].grid(row=video_cnt+1, column=7, sticky=NW)
            self.videos[video_name]['visualize_dropdown'].grid(row=video_cnt + 1, column=8, sticky=NW, padx=10)

    def get_execute_btns(self):
        self.execute_frm = CreateLabelFrameWithIcon(parent=self.main_frm, header="EXECUTE", icon_name='rocket')
        self.run_btn = SimbaButton(parent=self.execute_frm, txt='RUN', img='rocket', cmd=self._initialize_run)
        self.remove_exclusion_zones_btn = SimbaButton(parent=self.execute_frm, txt='REMOVE EXCLUSION ZONES', img='trash', cmd=self._delete_exclusion_zone_data, cmd_kwargs=None, txt_clr='darkred')
        self.remove_inclusion_zones_btn = SimbaButton(parent=self.execute_frm, txt='REMOVE INCLUSION ZONES', img='trash', cmd=self._delete_inclusion_zone_data, cmd_kwargs=None, txt_clr='darkblue')
        self.execute_frm.grid(row=2, column=0, sticky=NW)
        self.run_btn.grid(row=0, column=0, sticky=NW)
        self.remove_inclusion_zones_btn.grid(row=0, column=1, sticky=NW)
        self.remove_exclusion_zones_btn.grid(row=0, column=2, sticky=NW)

    def _set_method(self, method: str):
        for video_name in self.videos.keys():
            self.videos[video_name]["method_dropdown"].setChoices(method)

    def _delete_exclusion_zone_data(self):
        if os.path.isfile(self.roi_exclusion_store):
            remove_files(file_paths=[self.roi_exclusion_store])
        else:
            raise NoDataError(msg='Cannot delete EXCLUSION zones: No EXCLUSION zones exist.', source=self.__class__.__name__)
    def _delete_inclusion_zone_data(self):
        if os.path.isfile(self.roi_inclusion_store):
            remove_files(file_paths=[self.roi_inclusion_store])
        else:
            raise NoDataError(msg='Cannot delete INCLUSION zones: No INCLUSION zones exist.', source=self.__class__.__name__)

    def _set_window_size(self, size: str):
        check_int(name='window size', value=size, min_value=0, raise_error=True)
        for video_name in self.videos.keys():
            self.videos[video_name]["window_size_entry"].entry_set(size)


    def _launch_set_exlusion_zones(self, video_name: str):
        ROI_ui(config_path=None, video_path=self.in_videos[video_name], roi_coordinates_path=self.roi_exclusion_store, video_dir=self.input_dir)

    def _launch_set_inclusion_zones(self, video_name: str):
        ROI_ui(config_path=None, video_path=self.in_videos[video_name], roi_coordinates_path=self.roi_inclusion_store, video_dir=self.input_dir)

    def _set_window_weight(self, size: str):
        check_int(name='window weight', value=size, min_value=0, raise_error=True)
        for video_name in self.videos.keys():
            self.videos[video_name]["window_weight_entry"].entry_set(size)

    def _set_threshold(self, threshold: str):
        check_int(name='threshold', value=threshold, min_value=0, max_value=100, raise_error=True)
        for video_name in self.videos.keys():
            self.videos[video_name]["threshold_dropdown"].setChoices(threshold)

    def _set_visualize(self, val: str):
        check_str(name='visualize', value=val, options=('TRUE', 'FALSE'), raise_error=True)
        for video_name in self.videos.keys():
            self.videos[video_name]["visualize_dropdown"].setChoices(val)

    def _duplicate_inclusion_zones(self, video_name: str):
        if os.path.isfile(self.roi_inclusion_store):
            _, _, _, roi_dict, _, _, _ = get_roi_data(roi_path=self.roi_inclusion_store, video_name=video_name)
            if len(list(roi_dict.keys())) == 0:
                msg = f'Cannot duplicate the INCLUSION zones in {video_name}: Video {video_name} have no drawn INCLUSION zones.'
                raise NoDataError(msg=msg, source=self.__class__.__name__)
            else:
                multiply_ROIs(filename=self.in_videos[video_name], roi_coordinates_path=self.roi_inclusion_store, videos_dir=self.input_dir)
        else:
            msg = f'Cannot duplicate the INCLUSION zones in {video_name}: No INCLUSION zones have been drawn.'
            raise NoDataError(msg=msg, source=self.__class__.__name__)

    def _duplicate_exclusion_zones(self, video_name: str):
        if os.path.isfile(self.roi_exclusion_store):
            _, _, _, roi_dict, _, _, _ = get_roi_data(roi_path=self.roi_exclusion_store, video_name=video_name)
            if len(list(roi_dict.keys())) == 0:
                msg = f'Cannot duplicate the EXCLUSION zones in {video_name}: Video {video_name} have no drawn EXCLUSION zones.'
                raise NoDataError(msg=msg, source=self.__class__.__name__)
            else:
                multiply_ROIs(filename=self.in_videos[video_name], roi_coordinates_path=self.roi_exclusion_store, videos_dir=self.input_dir)
        else:
            msg = f'Cannot duplicate the EXCLUSION zones in {video_name}: No EXCLUSION zones have been drawn.'
            raise NoDataError(msg=msg, source=self.__class__.__name__)

    def _check_bg_videos(self, bg_videos: dict, videos: dict):
        missing_bg_videos = list(set(list(videos.keys())) - set(list(bg_videos.keys())))
        if len(missing_bg_videos) > 0:
            raise InvalidVideoFileError(msg=f'The chosen BACKGROUND DIRECTORY is missing videos for {len(missing_bg_videos)} video files: {missing_bg_videos}', source=self.__class__.__name__)
        for video_name, video_path in self.in_videos.items():
            video_meta = get_video_meta_data(video_path=video_path)
            bg_meta = get_video_meta_data(video_path=bg_videos[video_name])
            if video_meta['resolution_str'] != bg_meta['resolution_str']:
                raise InvalidVideoFileError(msg=f'The video, and background reference video, for {video_name} have different resolutions: {video_meta["resolution_str"]} vs {bg_meta["resolution_str"]}', source=self.__class__.__name__)

    def _apply_bg_dir(self, bg_dir: Union[str, os.PathLike]):
        check_if_dir_exists(in_dir=bg_dir)
        self.bg_videos = find_all_videos_in_directory(directory=bg_dir, as_dict=True, raise_error=False)
        self._check_bg_videos(bg_videos=self.bg_videos, videos=self.videos)
        for video_name, video_path in self.in_videos.items():
            self.videos[video_name]['bg_file'].filePath.set(self.bg_videos[video_name])

    def _get_bg_videos(self) -> dict:
        bg_videos = {}
        for video_name in self.videos.keys():
            if not os.path.isfile(self.videos[video_name]['bg_file'].file_path):
                raise InvalidVideoFileError(msg=f'The background reference file for {video_name} is not a valid file: {self.videos[video_name]["bg_file"].file_path}.', source=self.__class__.__name__)
            bg_videos[video_name] = self.videos[video_name]['bg_file'].file_path
        self._check_bg_videos(bg_videos=bg_videos, videos=self.in_videos)
        return bg_videos

    def get_roi_definitions(self, video_name: str, coordinates_path: Union[str, os.PathLike]):
        if os.path.isfile(coordinates_path):
            _, _, _, roi_dict, _, _, _ = get_roi_data(roi_path=coordinates_path, video_name=video_name)
            return roi_dict
        else:
            return None


    def _initialize_run(self):
        bg_videos = self._get_bg_videos()
        out = {'input_dir':  self.input_dir,
               'output_dir': self.output_dir,
               'gpu': self.gpu_var.get(),
               'core_cnt': self.core_cnt_dropdown.getChoices()}
        video_out = {}
        for video_name, video_data in self.videos.items():
            video_out[video_name] = {}
            video_out[video_name]['threshold'] = int(self.videos[video_name]["threshold_dropdown"].getChoices())
            video_out[video_name]['method'] = self.videos[video_name]["method_dropdown"].getChoices()
            video_out[video_name]['window_size'] = self.videos[video_name]["window_size_entry"].entry_get
            video_out[video_name]['window_weight'] = self.videos[video_name]["window_weight_entry"].entry_get
            video_out[video_name]['reference'] = self.videos[video_name]["bg_file"].file_path
            video_out[video_name]['visualize'] = str_2_bool(self.videos[video_name]["visualize_dropdown"].getChoices())
            video_out[video_name]['exclusion_zones'] = self.get_roi_definitions(video_name=video_name, coordinates_path=self.roi_exclusion_store)
            video_out[video_name]['inclusion_zones'] = self.get_roi_definitions(video_name=video_name, coordinates_path=self.roi_inclusion_store)
        print(video_out)




_ = BlobTrackingUI(input_dir=r'C:\troubleshooting\mitra\test', output_dir=r"C:\troubleshooting\mitra\test\blob_data")