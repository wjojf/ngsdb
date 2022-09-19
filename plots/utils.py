from ngsdb.settings import MEDIA_ROOT
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA as sklearnPCA
import pandas as pd
import numpy as np
import dash_bio
import csv
import os 



def load_df(csv_filepath):
    return pd.read_csv(csv_filepath, index_col=None, engine='python')


def get_pca_df(csv_filepath):
    
    try:
        df = load_df(csv_filepath)
    except Exception:
        return pd.DataFrame()

    x_std = StandardScaler().fit_transform(df.values.T)
    sklearn_pca = sklearnPCA(n_components=4)
    Y = sklearn_pca.fit_transform(x_std)
    
    pca_df = pd.DataFrame()
    pca_df['condition'] = ['Ctrl']*3 + ['pyg']*3
    pca_df['PC1'] = Y[:,0]
    pca_df['PC2'] = Y[:,1]


    return pca_df


def get_volcano_plot_for_obj(exp_obj):
    data_filepath = str(exp_obj.data_filepath)
    df = pd.read_csv(os.path.join(MEDIA_ROOT, data_filepath)).dropna()

    figure = dash_bio.VolcanoPlot(
        dataframe=df,
        effect_size='log2FoldChange',
        p='pvalue',
        snp=None,
        gene='Gene',
        title=f'{exp_obj}'
    )
    
    return figure.to_html()
