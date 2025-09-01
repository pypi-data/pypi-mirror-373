import xml.etree.ElementTree as ET
import pandas as pd
import numpy as np
import networkx as nx  
import matplotlib.pyplot as plt
 
from matplotlib import colormaps as cm
import seaborn as sns



def global_balance(path):

    file = ET.parse(path)

    # Initialize data containers
    teams = {}
    data=[]

    # Iterate through XML tree
    for season in file.getroot():
        season_name = season.attrib.get("season_name")

        for team in season.findall("Team"):
            key=team.attrib.get("uID")
            name=team.find("Name").text
            teams[key]=name

        for match in season.findall("MatchData"):
            for stats in match.findall("MatchInfo"):
                jornada=stats.attrib.get("MatchDay")

            for stats in match.findall("TeamData"):
                if stats.attrib.get("Side")=="Home":
                    home_team=stats.attrib.get("TeamRef")
                    score_home=stats.attrib.get("Score")
                    
                else:
                    away_team=stats.attrib.get("TeamRef")
                    score_away=stats.attrib.get("Score")

            difference_home=int(score_home) - int(score_away)
            difference_away=int(score_away) - int(score_home)
            
            points_home=3 if difference_home > 0 else 0 if  difference_home < 0  else 1 
            points_away=3 if difference_away > 0 else 0 if  difference_away < 0  else 1 

            data.append([season_name,int(jornada), teams[home_team],int(score_home),difference_home,points_home])
            data.append([season_name,int(jornada), teams[away_team],int(score_away),difference_away,points_away])

    df1=pd.DataFrame(data, columns=["Season","MatchDay","Team","Goals scored","Goals Difference","Points"])
    df1['Points'] = df1.groupby('Team')['Points'].cumsum()
    df1['Goals Difference'] = df1.groupby('Team')['Goals Difference'].cumsum()
    df1['Goals scored'] = df1.groupby('Team')['Goals scored'].cumsum()
    df1=df1.reset_index(drop=True)

    return df1

def tiebreaker(h2h_duels_df, global_balance_df, match_day,teams_list):
    lista=[]
    for teams in teams_list:
        team_a, team_b = teams
        h2h_duels_filtered=h2h_duels_df[(h2h_duels_df["Local"]==team_a) & (h2h_duels_df["Away"]==team_b)]
        if h2h_duels_filtered.empty==True:
            h2h_duels_filtered=h2h_duels_df[(h2h_duels_df["Away"]==team_b) & (h2h_duels_df["Away"]==team_a)]

        h2h_duels_filtered_matchday=h2h_duels_filtered[h2h_duels_filtered["MatchDay"]<= match_day].sort_values(by="MatchDay").head(1)
        h2h_duels_filtered_matchday=h2h_duels_filtered_matchday.reset_index(drop=True)
        ### Criterio diferencia de goles en duelos directos
        if (h2h_duels_filtered_matchday.empty==False) and (h2h_duels_filtered_matchday["Teams Goal Difference"] != 0).all():
            if (h2h_duels_filtered_matchday["Teams Goal Difference"]<0).all():
                lista.append([h2h_duels_filtered_matchday.loc[0,"Away"],h2h_duels_filtered_matchday.loc[0,"Local"]])
                
            elif (h2h_duels_filtered_matchday["Teams Goal Difference"] > 0).all():
                lista.append([h2h_duels_filtered_matchday.loc[0,"Local"],h2h_duels_filtered_matchday.loc[0,"Away"]])

        ### Criterio diferencia de goles acumulada
        else: 
            balance=global_balance_df[global_balance_df["MatchDay"]==match_day]
            balance_team_a=int(balance[balance["Team"]==team_a]["Goals Difference"].values[0])      
            balance_team_b=int(balance[balance["Team"]==team_b]["Goals Difference"].values[0])
            if balance_team_a > balance_team_b:
                lista.append([team_a,team_b])
            elif balance_team_a < balance_team_b:
                lista.append([team_b,team_a])
            else: 
                ### Criterio goles a favor
                goles_team_a=int(balance[balance["Team"]==team_a]["Goals scored"].values[0])
                goles_team_b=int(balance[balance["Team"]==team_b]["Goals scored"].values[0])
                if goles_team_a > goles_team_b:
                    lista.append([team_a,team_b])
                elif goles_team_a < goles_team_b:
                    lista.append([team_b,team_a])  
        
    # print(lista)
    G = nx.DiGraph()
    G.add_edges_from(lista)
    # Función para romper ciclos
    def break_cycles(graph):
        graph_copy = graph.copy()
        while True:
            try:
                list(nx.topological_sort(graph_copy))
                break  # No hay ciclos
            except nx.NetworkXUnfeasible:
                cycle = list(nx.find_cycle(graph_copy, orientation='original'))
                edge_to_remove = cycle[-1][:2]  # Eliminar última arista del ciclo
                graph_copy.remove_edge(*edge_to_remove)
        return graph_copy

    # Aplicar algoritmo
    G_acyclic= break_cycles(G)

    # Perform topological sort
    sorted_list = list(nx.topological_sort(G_acyclic))

    return sorted_list


def plot_team_points(league_table_df):
    # Estilo visual
    sns.set_style("whitegrid")

    # Crear DataFrame
    df = league_table_df[["MatchDay","Team","League Position"]]

    # Crear figura y eje principal
    fig, ax1 = plt.subplots(figsize=(20, 10))

    # Eje Y izquierdo - Equipo
    colores_equipos = dict(zip(df['Team'].unique(), sns.color_palette("tab20", len(df['Team'].unique()))))
    
    ax1.set_xlabel('MatchDay')
    ax1.set_ylabel('Team')
    jornada_1=df[df['MatchDay']==1].sort_values("League Position",ascending=False)
    ax1.plot(jornada_1['MatchDay'], jornada_1['Team'], marker=',',color="white", label='Team')
    ax1.tick_params(axis='y')

    # Eje Y derecho - League Position
    ax2 = ax1.twinx()

    ax2.set_ylabel('League Position')
    for equipo in np.sort(df['Team'].unique()):
        datos_equipo = df[df['Team'] == equipo]
        ax2.plot(datos_equipo['MatchDay'], datos_equipo['League Position'],color=colores_equipos[equipo], linestyle='--', marker='s', label='League Position')

    min_y=int(min(jornada_1["League Position"]))
    max_y=int(max(jornada_1["League Position"]))
    ax2.set_yticks(range(min_y, max_y + 1))
    # ax2.tick_params(axis='y', labelcolor=color_clasificacion)
    ax2.set_ylim(ax2.get_ylim()[::-1])

    # Título y leyenda
    fig.suptitle("Development of team's League Position by Match Day", fontsize=14)
    fig.tight_layout()
    plt.show()
