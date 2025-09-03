import pandas as pd
import ast
import numpy as np
import re
from typing import List, Union
from scipy.interpolate import interp1d
from simba.utils.checks import check_instance, check_int, check_valid_lst, check_valid_array, check_valid_dataframe, check_str
from simba.utils.enums import Formats
from simba.utils.data import resample_geometry_vertices
from simba.utils.read_write import read_df_array


df = pd.read_csv(r"C:\troubleshooting\mitra\test\blob_data\501_MA142_Gi_Saline_0515.csv")
vertices = read_df_array(df=df, column='vertices')

resampled = resample_geometry_vertices(vertices=vertices, vertice_cnt=3)

# d =
# for i in d:
#     print(i)



#c = data['vertices'].apply(parse_as_lists)
