import sys
import pickle
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split, KFold

# Return a flattened df of the specified feature (either 'max_min' or 'std')
def flatten(df, feature='max_min', interval=60):
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

    return result_df

# Return a df that is the concatenation of two input dfs (column wise)
def concat_df(df1, df2):
    df1.reset_index(drop=True, inplace=True)
    df2.reset_index(drop=True, inplace=True)

    df = pd.concat( [df1, df2], axis=1, ignore_index=True)

    return df

PATH_TO_MODEL = sys.path[0] + '/models'

class ML:
    DANCES = [  "unknown",  # Unknown ==> 0
                "wipers",   # Wipers ==> 1
                "number7",  # Number7 ==> 2
                "chicken",  # Chicken ==> 3
                "sidestep", # SideStep ==> 4
                "turnclap", # TurnClap ==> 5
                "numbersix",  # Number6 ==> 6
                "salute",   # Salute ==> 7
                "mermaid",  # Mermaid ==> 8
                "swing",    # Swing ==> 9
                "cowboy",
		"logout" ]  # Cowboy ==> 10

    def __init__(self):
        self.RF = pickle.load(open(PATH_TO_MODEL + '/random_forest_model.sav', 'rb'))
        #self.SVM = pickle.load(open(PATH_TO_MODEL + '/svc_model.sav', 'rb'))
        self.counter = 0


    def predict(self, df):
        #df_max_min = flatten(df,'max_min',interval=len(df))
        df_std = flatten(df, 'std', interval=len(df))
        #df_concat = concat_df(df_max_min, df_std)

        predicted_RF = self.RF.predict(df_std)
        #predicted_SVM = self.SVM.predict(df_std)

        #if predicted_RF[0] != predicted_SVM[0]:
         #   print("SVM: " + self.DANCES[predicted_SVM[0]])
          #  print("RF: " + self.DANCES[predicted_RF[0]])
        #    return self.DANCES[0]
        
        #if predicted_RF[0] == 3 and predicted_SVM[0] == 8:
         #   return self.DANCES[8]
        
        return self.DANCES[predicted_RF[0]]


    def increment_counter(self):
        self.counter += 1
