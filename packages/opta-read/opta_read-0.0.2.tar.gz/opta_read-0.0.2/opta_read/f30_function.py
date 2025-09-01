import xml.etree.ElementTree as ET
import pandas as pd
from opta_read._auxiliares.f30_aux_funct import *

class F30:

    def __init__(self, path):
        self.path=path
    
    def team_stats(self):
        '''
        Function that returns season stats of a team
        '''
        file=ET.parse(self.path)
        team_dict={}
        for team in file.getroot():
            for stat in team:
                attribute=stat.attrib.get("name")
                value=stat.text
                team_dict[attribute]=[value]
        del team_dict[None]

        team_stats=pd.DataFrame.from_dict(data=team_dict, orient="index", columns=[team.attrib.get("name")])

        return team_stats

    def players_stats(self):
        '''
        Function that returns season stats of all players of a team
        '''
        players_dict={}
        player_stats={}
        path=self.path
        file=ET.parse(path)

        root=file.getroot()
        for player in root.findall(".//Player"):
            first_name=player.attrib.get("first_name")
            last_name=player.attrib.get("last_name")
            full_name=first_name + " " + last_name
            for stat in player:
                attribute=stat.attrib.get("name")
                value=stat.text
                player_stats[attribute] = float(value) 
            
            players_dict[full_name]=player_stats
            player_stats={}
        
        players_stats=pd.DataFrame.from_dict(data=players_dict, orient="index")

        def plot_compare_players(players, stats, color_player_1, color_player_2):
            return compare_players(players_stats, players, stats, color_player_1, color_player_2)
        players_stats.plot_compare_players=plot_compare_players

        return players_stats
    
