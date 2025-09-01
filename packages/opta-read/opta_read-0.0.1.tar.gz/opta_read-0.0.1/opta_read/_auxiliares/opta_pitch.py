import matplotlib.pyplot as plt
from matplotlib.patches import Arc


def opta_pitch(ax):        
    # OPTA PITCH
    # Pitch Outline & Centre Line
    plt.plot([0,0],[0,100], color="black")
    plt.plot([0,100],[100,100], color="black") #upper line x_start x_end y_start y_end
    plt.plot([100,100],[100,0], color="black")
    plt.plot([100,0],[0,0], color="black")
    plt.plot([50,50],[0,100], color="black")

    # Left Penalty Area
    plt.plot([17,17],[78.9,21.1],color="black")
    plt.plot([0,17],[78.9,78.9],color="black")
    plt.plot([17,0],[21.1,21.1],color="black")

    # Right Penalty Area
    plt.plot([100,83],[78.9,78.9],color="black")
    plt.plot([83,83],[78.9,21.1],color="black")
    plt.plot([83,100],[21.1,21.1],color="black")

    # Left 6-yard Box
    plt.plot([0,5.8],[63.2,63.2],color="black")
    plt.plot([5.8,5.8],[63.2,36.8],color="black")
    plt.plot([5.8,0],[36.8,36.8],color="black")

    # Right 6-yard Box
    plt.plot([100,94.2],[63.2,63.2],color="black")
    plt.plot([94.2,94.2],[63.2,36.8],color="black")
    plt.plot([94.2,100],[36.8,36.8],color="black")

    # Prepare Circles OK
    centreCircle = plt.Circle((50,50),9.15,color="black",fill=False)
    centreSpot = plt.Circle((50,50),0.6,color="black")
    leftPenSpot = plt.Circle((11.5,50),0.6,color="black")
    rightPenSpot = plt.Circle((88.5,50),0.6,color="black")

    # Draw Circles
    ax.add_patch(centreCircle)
    ax.add_patch(centreSpot)
    ax.add_patch(leftPenSpot)
    ax.add_patch(rightPenSpot)

    # Prepare Arcs based on penalty Spots
    leftArc = Arc((11.5,50),height=18.3,width=18.3,angle=0,
                theta1=310,theta2=50,color="black")
    rightArc = Arc((88.5,50),height=18.3,width=18.3,angle=0,theta1=130,theta2=230,color="black")


    # Draw Arcs
    ax.add_patch(leftArc)
    ax.add_patch(rightArc)


def Plotter(mean_position, passer, receiver, number, num_max_pases, pass_color="red"):

        '''
        Function that plots a line between the mean position of passer and receiver
        where the width of that line is based on the number of passes that 
        take place between those two players.

        Input:
        * mean_position: dataframe with each player and its mean position
        * passer: name of the passer
        * receiver: name of the receiver 
        * number: amount of passes between passer and receiver
        * num_max_pases: maximum amount of passes between two players considering the whole team to calculate it.
        * pass_color: color used to represent passes in the plot
        
        '''

        mp_coords=mean_position[['Passer','x','y']].drop_duplicates()
        mp_coords=mp_coords.set_index("Passer")

        passer_loc = [[float(mp_coords.loc[passer].iloc[0]), float(mp_coords.loc[passer].iloc[1])]]
        receiver_loc = [[float(mp_coords.loc[receiver].iloc[0]), float(mp_coords.loc[receiver].iloc[1])]]

        for i,j in zip(passer_loc, receiver_loc):
            plt.arrow(x = i[0],
                    y = i[1],
                    dx = (j[0]-i[0]),
                    dy = (j[1]-i[1]),
                    linewidth = int(number),
                    alpha = (int(number)/num_max_pases), # propiedad transparencia que va de 0 a 1
                    length_includes_head=True,
                    color = pass_color)