import xml.etree.ElementTree as ET
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.lines import Line2D

from matplotlib import colormaps as cm
from opta_read._auxiliares.opta_pitch import *



def defensive_stats_funct(path):
    '''
    Function that returns defensive stats of a match
    '''
    file=ET.parse(path)
    # Initialize data containers
    data = []

    # Iterate through XML tree
    for game in file.getroot():
        home_team = game.attrib.get("home_team_name")
        away_team = game.attrib.get("away_team_name")

        for team in game:
            team_name = home_team if team.attrib.get("Side") == "Home" else away_team

            for player in team:
                player_name = player.attrib.get("player_name")

                for stat in player:
                    stat_name = stat.tag
                    coords = [[point.attrib.get("x"), point.attrib.get("y")] for point in stat]

                    num_events = len(coords) if stat_name != "DefensiveCoverage" else None

                    data.append([team_name, player_name, stat_name, num_events, coords])

    # Create DataFrame
    df = pd.DataFrame(data, columns=[
        "Team", "Player", "Defensive Stat", "Number of Defensive Actions", "Coords of Defensive Actions"
    ])

    def plot_defensive_coverages(team, player=None):
        return defensive_coverages(df, team, player)
    
    def plot_defensive_actions(team, player=None):
        return defensive_actions(df, team, player)

    df.plot_defensive_coverages=plot_defensive_coverages
    df.plot_defensive_actions=plot_defensive_actions
    return df

def defensive_coverages(df,team, players=None):
        '''
        Function that represents defensive coverage areas for single team or for a list of players

        '''

        # Filter dataframe by team selected and defensive coverage actions
        filtered_df=df[(df["Team"]==team) & (df["Defensive Stat"]=="DefensiveCoverage")]
        filtered_df=filtered_df[["Player","Coords of Defensive Actions"]]
        if players != None: 
            filtered_df=filtered_df[filtered_df["Player"].isin(players)]
        filtered_df.reset_index(inplace=True, drop=True)


        # Get rival team
        rival=df[df["Team"]!=team]["Team"].head(1)
        rival=rival.reset_index(drop=True)
        rival_name=rival[0]

        # Generate a color map based on number of records of filtered df

        colors = cm['tab10'].resampled(len(filtered_df))

        fig, ax = plt.subplots()

        # Add opta pitch
        opta_pitch(ax)

        ax.get_xaxis().set_visible(False)
        ax.get_yaxis().set_visible(False)

        # Plot defensive coverage polygons
        for i in range(len(filtered_df)):
            rect1 = patches.Polygon(filtered_df.iloc[i,1], label=filtered_df.iloc[i,0], linewidth=1,edgecolor=colors(i), facecolor=colors(i), alpha=0.5)

            ax.add_patch(rect1)

        if players==None:
            plt.title(f"Defensive coverage of {team}'s players against {rival_name}")
        else:
            plt.title(f"Defensive coverage of {' & '.join(players)} against {rival_name}")

        ax.legend()
        plt.show()

def defensive_actions(df, team, player=None):
        '''
        Function that represents defensive actions for a single team or a list of players

        '''
        
        # Filter dataframe by team selected and defensive coverage actions
        filtered_df=df[(df["Team"]==team) & (df["Defensive Stat"]!="DefensiveCoverage")]
        filtered_df=filtered_df[["Player","Defensive Stat","Coords of Defensive Actions"]]
        if player != None: 
            filtered_df=filtered_df[filtered_df["Player"].isin(player)]
        filtered_df.reset_index(inplace=True, drop=True)

        # Get rival team
        rival=df[df["Team"]!=team]["Team"].head(1)
        rival=rival.reset_index(drop=True)
        rival_name=rival[0]


        # Get list of different stats
        stats_unique=filtered_df["Defensive Stat"].unique().tolist()

        # List of possible matplotlib markers. We select only the amount we need
        markers_list=list(Line2D.markers.keys())
        markers_list.remove(",") # Remove pixel representation, as it's very small
        markers_list=markers_list[:len(stats_unique)]

        # Create dictionary that pairs a stat and a marker
        stat_marker=dict(zip(stats_unique, markers_list))

        # Generate a color map based on number of distinct players
        players_unique= filtered_df["Player"].unique().tolist()
        colors = cm['tab10'].resampled(len(players_unique))

        fig, ax = plt.subplots()

        # Add opta pitch
        opta_pitch(ax)

        ax.get_xaxis().set_visible(False)
        ax.get_yaxis().set_visible(False)

        player_legend=[]
        # Plot defensive coverage polygons
        for i in range(len(players_unique)):
            player_df=filtered_df[filtered_df["Player"]==players_unique[i]]
            # Create custom legend for players
            player_legend.append(Line2D([0], [0], color=colors(i), label=players_unique[i]))

            for k in range(len(player_df)):
                x,y=zip(*player_df.iloc[k,2])
                plt.scatter([float(x_coord) for x_coord in list(x)],
                        [float(y_coord) for y_coord in list(y)],
                        color=colors(i),
                        marker=stat_marker[player_df.iloc[k,1]])
                

        if player==None:    
            plt.title(f"Defensive stats of {team}'s players against {rival_name}")
        else:
            plt.title(f"Defensive stats of {' & '.join(player)} against {rival_name}")

        ax.set( xlim=[-30, 130], ylim=[-30, 130],xlabel='Possesion')

        # Create custom legend for markers
        marker_legend=[]
        for key,value in stat_marker.items():
            marker_legend.append(Line2D([0], [0], marker=value, color='w', label=key, markerfacecolor='gray', markersize=10))

        # Add first legend (markers)
        first_legend = plt.legend(handles=player_legend, title='Players', loc='upper center',ncols=5,fontsize="small")

        # # Add second legend (colors)
        second_legend = plt.legend(handles=marker_legend, title='Defensive Action', loc='lower center', ncols=5)

        # Add the first legend back manually
        plt.gca().add_artist(first_legend)
        plt.show()
    