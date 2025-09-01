
from opta_read._auxiliares.f71_aux_funct import defensive_stats_funct

class F71:

    def __init__(self, path):
        self.path=path
    
    def defensive_stats(self):
        return defensive_stats_funct(path=self.path)

    

    

    