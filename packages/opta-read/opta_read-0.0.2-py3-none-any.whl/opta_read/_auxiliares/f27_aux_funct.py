import matplotlib.pyplot as plt
from matplotlib.patches import Arc
from opta_read._auxiliares.opta_pitch import *

def pass_meanpos(mean_position_df, pass_matrix_df, pass_color="red",show_passes=True):

    if 'Number of Succesful Passes' not in list(pass_matrix_df.columns):
    # Raises an error if the input is a pivot table (not contains Number of Succesful Passes column)    
        raise ValueError("Input appears to be a pivot table. Input needs to be a regular dataframe.")
    
    fig, ax = plt.subplots(figsize=(18,14))
    
    max_num_pases=pass_matrix_df['Number of Succesful Passes'].max()
    # Flechas con los pases entre los jugadores con Plotter(passer, receiver, number)
    if show_passes==True:
        for i in range(len(pass_matrix_df)):
            Plotter(mean_position_df, pass_matrix_df.iloc[i,0], pass_matrix_df.iloc[i,1], pass_matrix_df.iloc[i,2], max_num_pases, pass_color)

    # Posición Media Scatter Puntos con color en función de su demarcación
    for i in range(len(mean_position_df)):
        ax.text(mean_position_df.iloc[i,1], mean_position_df.iloc[i,2], s = mean_position_df.iloc[i,0], rotation = 45, size = 10)
        if mean_position_df.iloc[i,3] == "Goalkeeper":
            plt.scatter(x=mean_position_df.iloc[i,1], y = mean_position_df.iloc[i,2], s = mean_position_df.iloc[i,4]*40, zorder = 1, color = "blue")
        if mean_position_df.iloc[i,3] == "Forward":
            plt.scatter(x=mean_position_df.iloc[i,1], y = mean_position_df.iloc[i,2], s = mean_position_df.iloc[i,4]*40, zorder = 1, color = "green")
        if mean_position_df.iloc[i,3] == "Midfielder":
            plt.scatter(x=mean_position_df.iloc[i,1], y = mean_position_df.iloc[i,2], s = mean_position_df.iloc[i,4]*40, zorder = 1, color = "grey")
        if mean_position_df.iloc[i,3] == "Defender":
            plt.scatter(x=mean_position_df.iloc[i,1], y = mean_position_df.iloc[i,2], s = mean_position_df.iloc[i,4]*40, zorder = 1, color = "orange")
        if mean_position_df.iloc[i,3] == "Substitute":
            plt.scatter(x=mean_position_df.iloc[i,1], y = mean_position_df.iloc[i,2], s = mean_position_df.iloc[i,4]*40, zorder = 1, color = "yellow")


    opta_pitch(ax)
    

    # Quitar Ejes
    plt.axis("off")
    if show_passes==True:
        plt.title("Passmap usando fichero F27 Opta - STATS Perform")
    else:
        plt.title("Posición media usando fichero F27 Opta - STATS Perform")

    plt.show()