import xml.etree.ElementTree as ET
import pandas as pd

from opta_read._auxiliares.f27_aux_funct import *

class F27:

    def __init__(self, path):
        self.path=path

    def mean_position(self):

        ''''
        Function that returns a dataframe with all players found in a F27 file, together with
        its mean position based on contacts with ball and the number of sucessful passes

        Input:
        OPTA F27 xml file


        '''
        xml_file=self.path

        file = ET.parse(xml_file)

        namelist= []
        xlist =[]
        ylist = []
        poslist = []
        pass_success_list = []

        for node in file.getroot():
            name = node.attrib.get("player_name")
            x = node.attrib.get("x")
            y = node.attrib.get("y")
            pos = node.attrib.get("position")
            pass_success = node.attrib.get("pass_success")
            namelist.append(name)
            xlist.append(x)
            ylist.append(y)
            poslist.append(pos)
            pass_success_list.append(pass_success)


        
        df=pd.DataFrame(data = list(zip(namelist,xlist,ylist,poslist, pass_success_list)),
                        columns = ["Passer","x","y","Position_Passer","PassSuccess"])

        df['x'] = pd.to_numeric(df['x'], errors='coerce')
        df['y'] = pd.to_numeric(df['y'], errors='coerce')                
        df['PassSuccess'] = pd.to_numeric(df['PassSuccess'], errors='coerce').fillna(0).astype(int) 
        
        return df.sort_values(by=["Position_Passer",'PassSuccess'],ascending=[True,False]).reset_index(drop=True)
    
    def pass_matrix(self, pivot_table=False, color=False):
        '''
        Function that returns a dataframe with all players found in a F27 file, together with
        its mean position based on contacts with ball and the number of sucessful passes

        Input:
        * xml_file: OPTA F27 xml file
        * pivot_table: if true, function will return a frequency table. If not, 
        it will return a regular dataframe with columns "Passer","Receiver" and "Number of Succesful Passes"
        * color: if true, it fills number of passes cells based on its value.

        '''
        xml_file=self.path

        file = ET.parse(xml_file)

        passer = []
        receiver = []
        passeslist = []

        for node in file.getroot():
            for players in node:
                passes = players.text
                name = players.attrib.get("player_name")
                passer.append(node.attrib.get("player_name"))
                receiver.append(name)
                passeslist.append(passes)


        df=pd.DataFrame(data = list(zip(passer,receiver,passeslist)),
                        columns = ["Passer","Receiver","Number of Succesful Passes"])
        df["Number of Succesful Passes"]=df["Number of Succesful Passes"].astype(int)
        
        if pivot_table==True:
        # Crear la tabla de frecuencias
            df = df.pivot_table(values='Number of Succesful Passes', index='Passer', columns='Receiver',aggfunc="sum", fill_value=0)
        
        if color==True:
            return df.style.background_gradient( axis=None)
        else:
            return df
        
    
    def plot_pass_meanpos(self,pass_color="red",show_passes=True):
        pass_matr=self.pass_matrix()
        return pass_meanpos(self.mean_position(),pass_matr,pass_color, show_passes)
            
    
    
            
