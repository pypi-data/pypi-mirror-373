import xml.etree.ElementTree as ET
import pandas as pd
import plotly.graph_objects as go
from sklearn.preprocessing import MinMaxScaler
import os
import IPython as ip
    

def compare_players(df, players, stats, color_player_1, color_player_2):

    '''
    Function that returns a spider-plot comparing two players in the stats we select.
    We decide to normalize dataframe columns so that the comparison is clear

    Input:
    * df: dataframe with all players stats
    * players: list of players (max length 2) to compare
    * stats: list of stats to compare

    '''

    ## Normalize data
    df=df[stats]
    scaler = MinMaxScaler()
    df_normalized = pd.DataFrame(scaler.fit_transform(df), columns=df.columns, index=df.index)


    df1=df_normalized.loc[players[0],stats]
    df2=df_normalized.loc[players[1],stats]

    categories=stats
    fig = go.Figure()

    fig.add_trace(go.Scatterpolar(
            r=df1.tolist(),
            theta=categories,
            fill='toself',
            marker_color=color_player_1,
            marker_line_color=color_player_1,
            opacity=0.5,
            name=players[0]
    ))
    fig.add_trace(go.Scatterpolar(
            r=df2.tolist(),
            theta=categories,
            marker_color=color_player_2,
            marker_line_color=color_player_2,
            fill='toself',
            opacity=0.5,
            name=players[1]
    ))

    fig.update_layout(
        polar=dict(
        radialaxis=dict(
            visible=True
        ))
    )
    if is_jupyter()==False and is_google_colab()==False:
        fig.write_html("plots/my_plot.html")
        import webbrowser

        file_path = os.path.abspath("plots/my_plot.html")
        webbrowser.open(f"file://{file_path}")
    else:
        fig.show()


def is_jupyter():
    try:
        shell = ip.get_ipython().__class__.__name__
        return shell == 'ZMQInteractiveShell'  # Jupyter Notebook or JupyterLab
    except NameError:
        return False  # Standard Python interpreter

def is_google_colab():
    try:
        import google.colab
        return True
    except ImportError:
        return False

