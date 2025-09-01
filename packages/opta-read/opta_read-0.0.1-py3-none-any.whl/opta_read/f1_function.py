import xml.etree.ElementTree as ET
import pandas as pd
import numpy as np
import itertools

from opta_read._auxiliares.f1_aux_funct import *

class F1:

    def __init__(self, path):
        self.path=path

    
    def results_and_td(self, team_difference=False):

        path=self.path

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
                    match_day=stats.attrib.get("MatchDay")

                for stats in match.findall("TeamData"):
                    if stats.attrib.get("Side")=="Home":
                        home_team=stats.attrib.get("TeamRef")
                        score_home=stats.attrib.get("Score")
                        
                    else:
                        away_team=stats.attrib.get("TeamRef")
                        score_away=stats.attrib.get("Score")

                if team_difference==True:
                    if int(match_day)<=19:
                        home_difference=int(score_home) - int(score_away) 
                        data.append([teams[home_team], teams[away_team],int(match_day), home_difference])
                    else:
                        away_difference=int(score_away) - int(score_home)
                        data.append([teams[away_team], teams[home_team],int(match_day), away_difference])

                else:
                    result="1" if score_home > score_away else "2" if  score_home < score_away  else "x" 
                    data.append([season_name,match_day, teams[home_team],score_home,score_away, teams[away_team],result])

        if team_difference==True:
            df=pd.DataFrame(data, columns=["Local","Away","MatchDay","Match Goals Difference"])
            df = df.sort_values(by='MatchDay')

            # Agrupamos por pares de equipos y calculamos la suma acumulada
            df['Teams Goal Difference'] = (
                df
                .groupby(['Local', 'Away'])['Match Goals Difference']
                .cumsum()
            )
            df=df.reset_index(drop=True)
        else:
            df=pd.DataFrame(data, columns=["Season","MatchDay","Local","Local Goals","Away Goals","Away","Result"])

        return df
    

    def league_table(self):
        
        h2h_duels_df=self.results_and_td(team_difference=True)
        global_balance_df=global_balance(self.path)

        result = pd.DataFrame()

        for match_day in np.sort(global_balance_df["MatchDay"].unique()):
            df_filtered = global_balance_df[global_balance_df["MatchDay"] == match_day].copy()
            df_filtered['Points_adjust'] = df_filtered['Points'].astype(float)  

            # Encontramos los registros con puntos duplicados
            df_filtered_dup = df_filtered[df_filtered.duplicated(subset="Points", keep=False)]

            for puntos in df_filtered_dup["Points"].unique():
                df_filtered_pt = df_filtered_dup[df_filtered_dup["Points"] == puntos]

                # Lista de tuplas con las distintas combinaciones posibles
                teams = list(itertools.combinations(df_filtered_pt["Team"].unique(), 2))
                
                # Almacenamos el resultado de desempate para evitar llamarlo varias veces
                desempate_list = tiebreaker(h2h_duels_df, global_balance_df, match_day,teams)
                # desempate(jornada, teams)
                
                if desempate_list:
                    desempate_dict={}
                    # Map adjustments only to relevant rows
                    for x in desempate_list:
                        desempate_dict[x]=(len(desempate_list)-desempate_list.index(x))/(len(desempate_list)+1)
                    
                    for equipo, ajuste in desempate_dict.items():
                        df_filtered.loc[df_filtered["Team"] == equipo, "Points_adjust"] += ajuste

            result = pd.concat([result, df_filtered], ignore_index=True)

        # # Final cleanup
        result = result.drop_duplicates().reset_index(drop=True)

        result_sorted = result.sort_values(by=["MatchDay",'Points_adjust'], ascending=[True, False])

        # # Añadimos la columna de clasificación
        result['League Position'] = result_sorted.groupby('MatchDay').cumcount() + 1
        # # df1['Clasificación']=df1['Clasificación'].astype("string")
        result=result.sort_values(by=["MatchDay","League Position"])
        result=result.reset_index(drop=True)
        result=result.drop(columns=["Points_adjust"])  

        def plot_league_table():
            return plot_team_points(result)
        
        result.plot_league_table=plot_league_table
        
        return result  