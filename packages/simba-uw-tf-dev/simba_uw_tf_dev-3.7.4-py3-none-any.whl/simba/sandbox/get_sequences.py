from simba.utils.read_write import recursive_file_search, get_fn_ext
import multiprocessing, functools
import pandas as pd
import os

from simba.utils.data import detect_bouts

X_BPS = ['NOSE_X','LEFT_EAR_X', 'RIGHT_EAR_X', 'LEFT_SIDE_X',  'CENTER_X','RIGHT_SIDE_X', 'TAIL_BASE_X', 'TAIL_CENTER_X', 'TAIL_TIP_X']
Y_BPS = ['NOSE_Y', 'LEFT_EAR_Y', 'RIGHT_EAR_Y', 'LEFT_SIDE_Y',  'CENTER_Y', 'RIGHT_SIDE_Y', 'TAIL_BASE_Y', 'TAIL_CENTER_Y', 'TAIL_TIP_Y']
P_BPS = ['NOSE_P', 'LEFT_EAR_P', 'RIGHT_EAR_P', 'LEFT_SIDE_P',  'CENTER_P', 'RIGHT_SIDE_P', 'TAIL_BASE_P']
BPS = intertwined = [val for pair in zip(X_BPS, Y_BPS) for val in pair][:-4]

def _get_sequences_helper(data_path,
                          length,
                          save_dir):

    df = pd.read_csv(data_path[0], index_col=0).reset_index(drop=True)
    video_id = int(os.path.basename(os.path.dirname(data_path[0])))
    save_subdir = os.path.join(save_dir, str(video_id))
    filename = get_fn_ext(filepath=data_path[0])[1]
    if not os.path.isdir(save_subdir): os.makedirs(save_subdir)
    df["all_P_BPS_above_0.50"] = (df[P_BPS] > 0.50).all(axis=1).astype(int)
    bouts = detect_bouts(data_df=df, target_lst=["all_P_BPS_above_0.50"], fps=1)
    bouts = bouts[bouts['Bout_time'] > length]
    if len(bouts) == 0:
        pass
    for idx, bout in bouts.iterrows():
        frm_rng = list(range(bout['Start_frame'], bout['End_frame']))
        frm_rngs = [frm_rng[i:i + length] for i in range(0, len(frm_rng) - len(frm_rng) % length, length)]
        for rng in frm_rngs:
            bout = df.loc[rng]
            bout = bout
            max, min = bout['FRAME'].max(), bout['FRAME'].min()
            bout = bout[BPS].reset_index(drop=True)
            save_path = os.path.join(save_subdir, f'{filename}_{min}_{max}.csv')
            bout.to_csv(save_path)
            print(save_path)

def get_sequences(dir, length, save_dir):
    file_paths = recursive_file_search(directory=dir, extensions=['csv'], substrings='_simon_spatial_offset')
    file_paths = [[x] for x in file_paths]

    with multiprocessing.Pool(6, maxtasksperchild=50) as pool:

        constants = functools.partial(_get_sequences_helper,
                                      length=length,
                                      save_dir=save_dir)
        for cnt, save_path in enumerate(pool.imap(constants, file_paths, chunksize=1)):
            pass
            #print(save_path)

if __name__ == "__main__":
    get_sequences(dir=r'D:\netholabs\get_sequences\test_3', length=100, save_dir=r'D:\netholabs\get_sequences\cleaned')
