import xml.etree.ElementTree as ET
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np
from typing import Literal

from opta_read._auxiliares.f28_aux_funct import *

class F28:

    def __init__(self, path):
        self.path=path
    
    def get_possesion(self,possesion_type:Literal["BallPossession","Territorial","TerritorialThird"], interval_length):
        if possesion_type not in ["BallPossession","Territorial","TerritorialThird"]:
            raise ValueError(f"possesion_type must be equal to one of BallPossession, Territorial or TerritorialThird")

        if interval_length not in [5,15,45]:
            raise ValueError(f"interval_length must be equal to one of 5, 15 or 45")

        path=self.path
        file=ET.parse(path)
        interval_poss = {}

        root = file.getroot()

        away_team = root.attrib.get("away_team_name")
        home_team = root.attrib.get("home_team_name")

        for possession_wave in root.findall(f".//PossessionWave[@Type='{possesion_type}']"):
            for interval_length in possession_wave.findall(f".//IntervalLength[@Type='{interval_length}']"):
                for interval in interval_length.findall("Interval"):
                    # Create a new team_poss dictionary for each interval
                    if possesion_type != "TerritorialThird":
                        team_poss = {
                            away_team: float(interval.find('Away').text),
                            home_team: float(interval.find('Home').text)
                        }
                    else:
                        team_poss = {
                            away_team: float(interval.find('Away').text),
                            home_team: float(interval.find('Home').text),
                            'middle': float(interval.find('Middle').text)
                        }
                    interval_type = interval.attrib.get("Type")
                    interval_poss[interval_type] = team_poss

        poss=pd.DataFrame.from_dict(data=interval_poss)

        def plot_pitch_possesion_evolution(color_team1="green", color_team2="blue", animated=True):
            return pitch_possesion_evolution(poss, color_team1, color_team2, animated)
        
        def plot_line_possesion_evolution():
            return line_possesion_evolution(poss)

        poss.plot_pitch_possesion_evolution=plot_pitch_possesion_evolution
        poss.plot_line_possesion_evolution=plot_line_possesion_evolution
        return poss
        # return possesion(path=self.path,possesion_type=possesion_type, interval_length=interval_length)

    
        
    

