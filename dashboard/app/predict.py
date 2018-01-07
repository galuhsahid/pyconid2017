from sklearn.model_selection import GridSearchCV
from sklearn import metrics
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestRegressor
from sklearn.externals import joblib
import warnings
import math

import pandas as pd
import numpy as np

def get_prediction(df_input):

    # Load our saved model
    df_input = df_input.astype(float)
    model_file_name = './app/resources/model.sav'
    loaded_model = joblib.load(model_file_name)
    result = loaded_model.predict(df_input)
    result = np.expm1(result[0])
    
    return result
