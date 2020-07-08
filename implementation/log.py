#!/usr/bin/python

import os
import datetime
import env

class LogFile():
    """
    This class implements the logging system for the 
    range skyline query project
    """

    def __init__(self, name, timestamp, log_dir):
        """
        The constructor of the class
        """

        self.log_name = str(name) + '.' + str(timestamp) 
        self.timestamp = timestamp
        self.log_dir = log_dir
        self.start_log_file()


    def start_log_file(self):
        """
        Initialize the log file
        """

        # Create log file
        self.log_file = open(self.log_dir / self.log_name, "w+")
        # Initialize first line
        self.log_file.write(">>> START LOG FILE\n")
        self.log_file.write(">>> Master Script: " + " " * 5 + self.log_name[:-15] + "\n")


    def write_log_file(self, title, info):
        """
        Writes into the log file
        """

        self.log_file.write(">>> " + str(title) + " " * (20 - len(title)) + str(info) + "\n")


    def close_log_file(self):
        """
        Closes the log file
        """

        self.log_file.write(">>> CLOSE LOG FILE")
        self.log_file.close()


