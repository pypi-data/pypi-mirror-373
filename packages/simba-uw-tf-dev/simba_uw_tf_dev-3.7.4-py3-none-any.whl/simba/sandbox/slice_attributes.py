from typing import Dict, Union, List, Tuple
import pandas as pd
from simba.utils.checks import check_if_keys_exist_in_dict, check_instance, check_valid_dataframe, check_valid_lst
from simba.utils.enums import Keys
from simba.utils.errors import NoROIDataError
from simba.utils.read_write import read_roi_data
from simba.mixins.config_reader import ConfigReader

def slice_roi_dict_from_attribute(data: Dict[str, pd.DataFrame],
                                  shape_names: List[str] = None,
                                  video_names: List[str] = None) -> Tuple[Dict[str, pd.DataFrame], List[str], int]:
    """
    Filters ROI (Region of Interest) shape data based on provided shape names and/or video names.


    :param Dict[str, pd.DataFrame] data: A dictionary where keys are shape type strings (e.g., 'Rectangles', 'Circles', 'Polygons'), and values are pandas DataFrames containing at least 'Name' and 'Video' columns. Obtained from ConfigReader.read_roi_data.
    :param Union[str, List[str]] shape_names: A string or list of strings specifying ROI names to retain. If None, all names are kept.
    :param Union[str, List[str]] video_names: A string or list of strings specifying video names to retain. If None, all videos are kept.
    :return: A dictionary of filtered DataFrames, one per shape type, with the index reset, the names of the ROIs, and the number of shapes returned.
    :rtype: Tuple[Dict[str, pd.DataFrame], List[str], int]
    """

    check_if_keys_exist_in_dict(data=data, key=[Keys.ROI_RECTANGLES.value, Keys.ROI_CIRCLES.value, Keys.ROI_POLYGONS.value], name=slice_roi_dict_from_attribute.__name__)
    if shape_names is None and video_names is None:
        raise NoROIDataError(msg='Please pass shapes names and/or video names', source=slice_roi_dict_from_attribute.__name__)
    if shape_names is not None:
        check_valid_lst(data=shape_names, source=f'{slice_roi_dict_from_attribute.__name__} shape_names', valid_dtypes=(str,), min_len=1, raise_error=True)
    if video_names is not None:
        check_valid_lst(data=video_names, source=f'{slice_roi_dict_from_attribute.__name__} video_names', valid_dtypes=(str,), min_len=1, raise_error=True)
    filtered_data, shape_names = {}, []
    for shape_type, df in data.items():
        check_instance(source=f"{slice_roi_dict_from_attribute.__name__} {shape_type}", instance=df, accepted_types=(pd.DataFrame,))
        check_valid_dataframe(df=df, source=f'{slice_roi_dict_from_attribute.__name__} shape_type', required_fields=['Video', 'Name'])
        if shape_names is not None:
            df = df[df['Name'].isin(shape_names)]
        if video_names is not None:
            df = df[df['Video'].isin(video_names)]
        filtered_data[shape_type] = df.reset_index(drop=True)
        shape_names.extend((list(df["Name"].unique())))
    shape_cnt = len(filtered_data[Keys.ROI_RECTANGLES.value]) + len(filtered_data[Keys.ROI_CIRCLES.value]) + len(filtered_data[Keys.ROI_POLYGONS.value])
    return filtered_data, shape_names, shape_cnt







config = ConfigReader(config_path=r"C:\troubleshooting\mitra\project_folder\project_config.ini")
config.read_roi_data()


roi_dict = config.roi_dict


slice_roi_dict_from_attribute(data=roi_dict, shape_names=['Cue_light_1'], video_names=['FR_gq_CNO_0625'])

#roi_dict = read_roi_data(roi_path=r"C:\troubleshooting\mitra\project_folder\logs\measures\ROI_definitions.h5")


