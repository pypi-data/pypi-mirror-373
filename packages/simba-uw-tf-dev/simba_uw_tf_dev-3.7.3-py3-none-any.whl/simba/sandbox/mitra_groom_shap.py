import numpy as np
import pandas as pd

FEATURE_GROUPS_PATH = r"C:\troubleshooting\mitra\mdl_metrics\grooming\x_groups_shap.csv"
SHAP_PATH = r"C:\troubleshooting\mitra\project_folder\logs\SHAP_values_grooming.csv"

feature_groups_df = pd.read_csv(FEATURE_GROUPS_PATH)
shap_df = pd.read_csv(SHAP_PATH, index_col=0)

results = pd.DataFrame()

for feature_group in feature_groups_df['GROUP'].unique():
    feature_df = feature_groups_df[feature_groups_df['GROUP'] == feature_group]
    for time_window in feature_groups_df['TIME'].unique():
        x_names = feature_df['MEASUREMENT'][feature_df['TIME'] == time_window]
        shap_group_data = shap_df[x_names].values
        shap_group_data_sum = np.sum(shap_group_data, axis=1)
        results.loc[feature_group, time_window] = np.round(np.mean(shap_group_data_sum), 2)

results['SUMMED'] = results.sum(axis=1)
results = results.sort_values(by=['SUMMED'], ascending=False)

results.to_csv(r'C:\troubleshooting\mitra\project_folder\logs\grooming_example_shap.csv')

        #print(np.round(np.mean(shap_group_data_sum), 2), feature_group, time_window)





    # features_in_group = list(feature_groups_df['MEASUREMENT'][feature_groups_df['GROUP'] == feature_group] )
    #
    #
    #