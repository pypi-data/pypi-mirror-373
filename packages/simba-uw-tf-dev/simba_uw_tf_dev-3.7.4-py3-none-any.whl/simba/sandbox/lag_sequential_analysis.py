import pandas as pd

from simba.utils.data import detect_bouts
from simba.utils.read_write import read_df


def event_lag_sequential_analysis(data: pd.DataFrame,
                                  x: str,
                                  y: str):

    pass



CLF_NAMES = ['Attack', 'Escape', 'Defensive', 'anogenital_prediction', 'face', 'body']

DATA_PATH = r"C:\troubleshooting\nastacia_unsupervised\machine_results\machine_results\Box2_IF19_7_20211109T173625_4.csv"
data_df = read_df(file_path=DATA_PATH, file_type='csv')


bouts = detect_bouts(data_df=data_df, target_lst=CLF_NAMES, fps=25)

event_lag_sequential_analysis(data=bouts, x='face', y='body')




