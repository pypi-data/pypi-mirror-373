from typing import Dict, List
import pandas as pd
from simba.utils.enums import Keys
from simba.utils.errors import NoROIDataError

from simba.utils.checks import check_valid_lst, check_valid_dict, check_valid_dataframe

def check_video_has_rois(roi_dict: Dict[str, pd.DataFrame],
                         roi_names: List[str] = None,
                         video_names: List[str] = None,
                         source: str = 'roi dict',
                         raise_error: bool = True):
    """
    Check that specified videos all have user-defined ROIs with specified names.
    """

    check_valid_dict(x=roi_dict, valid_key_dtypes=(str,), valid_values_dtypes=(pd.DataFrame,), required_keys=(Keys.ROI_RECTANGLES.value, Keys.ROI_CIRCLES.value, Keys.ROI_POLYGONS.value,),)
    check_valid_dataframe(df=roi_dict[Keys.ROI_RECTANGLES.value], source=f'{check_video_has_rois.__name__} {source} roi_dict {Keys.ROI_RECTANGLES.value}', required_fields=['Video', 'Name'])
    check_valid_dataframe(df=roi_dict[Keys.ROI_CIRCLES.value], source=f'{check_video_has_rois.__name__} {source} roi_dict {Keys.ROI_CIRCLES.value}', required_fields=['Video', 'Name'])
    check_valid_dataframe(df=roi_dict[Keys.ROI_POLYGONS.value], source=f'{check_video_has_rois.__name__} {source} roi_dict {Keys.ROI_POLYGONS.value}', required_fields=['Video', 'Name'])
    if roi_names is not None:
        check_valid_lst(data=roi_names, source=f'{check_video_has_rois.__name__} {source} roi_names', valid_dtypes=(str,), min_len=1)
    else:
        roi_names = list(set(list(roi_dict[Keys.ROI_RECTANGLES.value]['Name'].unique()) + list(roi_dict[Keys.ROI_CIRCLES.value]['Name'].unique()) + list(roi_dict[Keys.ROI_POLYGONS.value]['Name'].unique())))
    if video_names is not None:
        check_valid_lst(data=video_names, source=f'{check_video_has_rois.__name__} {source} video_names', min_len=1,)
    else:
        video_names = list(set(list(roi_dict[Keys.ROI_RECTANGLES.value]['Video'].unique()) + list(roi_dict[Keys.ROI_CIRCLES.value]['Video'].unique()) + list(roi_dict[Keys.ROI_POLYGONS.value]['Video'].unique())))
    missing_rois = {}
    rois_missing = False
    for video_name in video_names:
        missing_rois[video_name] = []
        for roi_name in roi_names:
            rect_filt = roi_dict[Keys.ROI_RECTANGLES.value][(roi_dict[Keys.ROI_RECTANGLES.value]['Video'] == video_name) & (roi_dict[Keys.ROI_RECTANGLES.value]['Name'] == roi_name)]
            circ_filt = roi_dict[Keys.ROI_CIRCLES.value][(roi_dict[Keys.ROI_CIRCLES.value]['Video'] == video_name) & (roi_dict[Keys.ROI_CIRCLES.value]['Name'] == roi_name)]
            poly_filt = roi_dict[Keys.ROI_POLYGONS.value][(roi_dict[Keys.ROI_POLYGONS.value]['Video'] == video_name) & (roi_dict[Keys.ROI_POLYGONS.value]['Name'] == roi_name)]
            if (len(rect_filt) + len(circ_filt) + len(poly_filt)) == 0:
                missing_rois[video_name].append(roi_name); rois_missing = True
    if rois_missing and raise_error:
        raise NoROIDataError(msg=f'Some videos are missing some ROIs: {missing_rois}', source=f'{check_video_has_rois.__name__} {source}')
    elif rois_missing:
        return False, missing_rois
    else:
        return True