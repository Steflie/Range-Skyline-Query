#!/usr/bin/python

from pathlib import Path 

class Variables:
    """The paths for the enviroment variables"""


    def __init__(self):
        """Initialize the enviroment variables"""

        # The root directory of the project
        self.master_dir = Path().absolute().parent

        # implementation, points_and_queries, logs directories and sub-directories 
        self.implementation_dir = self.master_dir / "implementation"
        self.point_and_queries_dir = self.master_dir / "points_and_queries"
        self.logs_dir = self.master_dir / "logs"
        
        # Subs
        self.algorithms_dir = self.implementation_dir / "algorithms"
        self.points_dir = self.point_and_queries_dir / "points"
        self.queries_dir = self.point_and_queries_dir / "queries"


    def show_paths(self):
        """Print the enviroment variable paths"""

        for atrr_item in self.__dict__.items():
            print(atrr_item[0])
            print(atrr_item[1])

