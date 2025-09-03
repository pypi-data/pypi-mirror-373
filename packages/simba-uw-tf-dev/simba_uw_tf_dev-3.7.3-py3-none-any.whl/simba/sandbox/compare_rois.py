from simba.utils.read_write import read_roi_data

ORIGINAL = r"C:\troubleshooting\SDS_pre_post\project_folder\logs\measures\ROI_definitions.h5"
NEW = r"C:\troubleshooting\SDS_pre_post\project_folder\logs\measures\orginal.h5"


original_rect, original_circ, original_polygon = read_roi_data(roi_path=ORIGINAL)
new_rect, new_circ, newl_polygon = read_roi_data(roi_path=NEW)

# print(original_rect['Center_X'])
# print(new_rect['Center_X'])

rect_diff = original_rect['Center_X'] - new_rect['Center_X']
circ_diff = new_circ['centerX'] - new_circ['centerX']
poly_diff = original_polygon['Center_X'] - newl_polygon['Center_X']


print(rect_diff)
print(circ_diff)
print(poly_diff)