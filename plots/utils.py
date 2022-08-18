from json import load
import pandas as pd
import numpy as np
import csv
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA as sklearnPCA


def loadDF(csv_filepath):
    return pd.read_csv(csv_filepath, index_col=None, skipfooter=5, engine='python')


def getPCADataframe(csv_filepath):
    
    try:
        df = loadDF(csv_filepath)
    except:
        return pd.DataFrame()

    X_std = StandardScaler().fit_transform(df.values.T)
    sklearn_pca = sklearnPCA(n_components=4)
    Y = sklearn_pca.fit_transform(X_std)
    
    pca_df = pd.DataFrame()
    pca_df['condition'] = ['Ctrl']*3 + ['pyg']*3
    pca_df['PC1'] = Y[:,0]
    pca_df['PC2'] = Y[:,1]


    return pca_df