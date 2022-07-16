import pandas as pd
import dash_bio


def generate_volcanoPlot(data_filepath):
    df = pd.read_csv(data_filepath).dropna()
    
    figure = dash_bio.VolcanoPlot(
        dataframe=df,
        effect_size='log2FoldChange',
        p='pvalue',
        snp=None,
        gene='Gene',
        title='Volcano Plot',
        effect_size_line_width=4,
        genomewideline_width=2
    )
    
    return figure.to_html()