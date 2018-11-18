import pandas as pd
import numpy as np
import pickle
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score
from sklearn.ensemble import RandomForestClassifier
from sklearn.svm import SVC

# Wipers ==> 1          # Number6 ==> 6
# Number7 ==> 2         # Salute ==> 7
# Chicken ==> 3         # Mermaid ==> 8
# SideStep ==> 4        # Swing ==> 9
# TurnClap ==> 5        # Cowboy ==> 10

dances = ["","wipers","number7","chicken","sideStep","turnClap","number6",
"salute","mermaid","swing","cowboy"]
def preprocess(df):
    #print("in ml")
    #print(len(df))
    df = normalise(df)
    df_max_min =flatten(df)
    df_std = flatten(df, 'std')
    real_time_data = concat_df(df_max_min, df_std)
    #svm_predicted_class = SVMpredictData(real_time_data)
    rf_predicted_class = RFpredictData(real_time_data)
    #print(svm_predicted_class)
    #print(rf_predicted_class)
    #if(svm_predicted_class == rf_predicted_class){
    #}
    return dances[rf_predicted_class[0]]

# Return a flattened df of the specified feature (either 'max_min' or 'std')
def flatten(df, feature='max_min', interval=100):
    result_df = pd.DataFrame()

    startIndex = 0
    while (startIndex + interval) <= len(df):
        endIndex = startIndex + interval
        subset = df.loc[startIndex:endIndex, :]
        startIndex = startIndex + interval / 2

        if feature == 'max_min':
            max_minus_min = pd.Series(np.ptp(subset[subset.columns].values, axis=0))
            result_df = result_df.append(max_minus_min, ignore_index=True)

        if feature == 'std':
            std = pd.Series(np.var(subset[subset.columns].values, axis=0))
            result_df = result_df.append(std, ignore_index=True)
        if feature == 'fft':
            Fourier_temp = fft(subset)
            fourier = np.abs(Fourier_temp)**2
            value = 0
            for x in range (len(fourier)):
                value = value + (fourier[x] * fourier [x])
            value = value / len(fourier)
            result = pd.Series(value)
            result_df = result_df.append(result, ignore_index=True)

        if feature == 'mean':
            mean = pd.Series(np.mean(subset[subset.columns].values, axis=0))
            result_df = result_df.append(mean, ignore_index=True)

    return result_df

# Return a df of the original df divided by denom
def normalise(df, denom=np.power(2, 15)):
    df = df / denom
    return df

# Return a df that is the concatenation of two input dfs (column wise)
def concat_df(df1, df2):
    df1.reset_index(drop=True, inplace=True)
    df2.reset_index(drop=True, inplace=True)

    df = pd.concat( [df1, df2], axis=1, ignore_index=True)

    return df

def SVMpredictData(real_time_data):
    # load the model from disk
    filename = 'swm_model.sav'
    loaded_model = pickle.load(open(filename, 'rb'))
    return loaded_model.predict(real_time_data)

def RFpredictData(real_time_data):
    # load the model from disk
    filename = 'randomForest_model.sav'
    loaded_model = pickle.load(open(filename, 'rb'))
    return loaded_model.predict(real_time_data)
