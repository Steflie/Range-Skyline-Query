#!/usr/bin/python

"""
Description:
    Range Skylines Queries using Branch & Bound technique with R-tree.
    The script retrieves the data from the point and query file and 
    calls the method for one or two dimension query. Prints the results 
    on the console as well as writes them in the log file. 

Usage: 
    <python skyline.py query_file point_file>

Arguments:
    query_file : file that contains query data for getting skylines
    data_file  : file from which we want to get skylines
"""

# Built-in modules
import sys
import os
import datetime
import getopt
import time 

# Custom modules
#from algorithms.single_dimensional_query import SingleDimensionalQuery as SnglDimQr
#from algorithms.two_dimensional_query import TwoDimensionalQuery as TwDimQr
import log
import env
from algorithms.algos_without_logs.single_dimensional_query import SingleDimensionalQuery as SnglDimQr
from algorithms.algos_without_logs.two_dimensional_query import TwoDimensionalQuery as TwDimQr

# Third party modules
from chart import range_chart as rc
from rtreelib.diagram import create_rtree_diagram
from rtreelib import RTree, Rect


# -------------- Methods ---------------------
def fill_rtree(file_to_open, rtree):
    """
    Fill the R-tree with input data file

        Input: file_to_open -> absolute path to the file with the data points
               rtree -> reference to the R-Tree
    """
    
    # Read the data file
    with open(file_to_open, 'r') as data:
        for row in data:
            point_cords = list(map(float, row.split()))
            # Insert into R-tree
            if len(point_cords) !=  0:
                x = point_cords[0]
                y = point_cords[1]
                rtree.insert([x,y], Rect(x,y,x,y))


def is_query_line(query_start, query_end):
    """
    Examine whether user's query is a line or
    a rectangle

        Input: query_start -> tuple: (qsx,qsy)
               query_end -> tuple: (qex, qey)

        Output: line -> True or False
    """

    line = False
    # To be line, one dimension is the same
    if query_start[0] == query_end[0]:
        line = True
    else:
        if query_start[1] == query_end[1]:
            line = True
    
    # Return
    return line
# -------------- \ Methods ---------------------


# Initialize enviroment variables
env_vars = env.Variables()

# Read Parameters 
query_filename = sys.argv[1]
points_filename = sys.argv[2]

# Full paths to files
query_to_open = env_vars.queries_dir / query_filename
points_to_open = env_vars.points_dir / points_filename

# Initialize Log File 
script_name = os.path.basename(__file__)
timestamp = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
log_file = log.LogFile(script_name, timestamp, env_vars.logs_dir)

# Log Info
log_file.write_log_file("Files Info", "-----")
log_file.write_log_file("Query File:", str(query_to_open))
log_file.write_log_file("Points File:", str(points_to_open))

# Read the query file
with open(query_to_open, 'r') as query:
    # Get the dimension on which a range preference is provided
    dimension = query.readline()   
    dimension = list(map(int, dimension.split(" ")))
    # Get the range preference as a list of typles for qs and qe
    query_range = list( query.readline().split() )
    query_start, query_end = [tuple(map(float, word.split(","))) for word in query_range]

# Log Info
log_file.write_log_file("Query Info", "-----")
log_file.write_log_file("Query Range: ", str(query_range))
log_file.write_log_file("Range Dimension(s): ", str(list(dimension)))



# -------------- R-Tree ---------------------

# Measure the time for the creation of the R-tree
start_time_rtree = time.time()

# Create R-tree object for M and m
rtree = RTree(4, 2)

# Fill the R-tree with data file
fill_rtree(points_to_open, rtree)

# Creation completed
end_time_rtree = time.time()

# Log Info 
log_file.write_log_file("R-Tree:", "CREATED")

# -------------- \ R-Tree ---------------------

# Diagram of the R-tree structure
#create_rtree_diagram(rtree)

# # Chart of the data points
# rngChrt = rc.RangeChart(query_to_open, points_to_open)
# rngChrt.createChart()

# # Log Info
# log_file.write_log_file("R-Tree Diagram:", "CREATED")
# log_file.write_log_file("Point CHART:", "CREATED")

# -------------- Single Dimensional Query ---------------------
if is_query_line(query_start, query_end):

    # Log Info
    log_file.write_log_file("One Dimension Qr:", "*** ALGORITHM 1 STARTED ***")

    # From list to int     
    dimension = dimension[0]

    # Measure the time for the Algorithm 1
    start_time_algo = time.time()

    # Create instance of Single Dimensional Algorithm
    dim_qr = SnglDimQr(query_start, query_end, dimension, rtree, log_file)

    # Here add the section for the sngl_dimensional query
    dim_qr.range_skyline_computation()
    
    # Algorithm execution completed
    end_time_algo = time.time()
    
    # Log Info
    log_file.write_log_file("One Dimension Qr:", "*** ALGORITHM 1 FINISHED ***")

# -------------- \ Single Dimensional Query ---------------------

# -------------- Two Dimensional Query ---------------------
else:

    # Log Info
    log_file.write_log_file("Two Dimension Qr:", "*** ALGORITHM 2 STARTED ***")

    # Measure the time for the Algorithm 1
    start_time_algo = time.time() 

    # Create instance of Two Dimensional Algorithm
    dim_qr = TwDimQr(query_start, query_end, dimension, rtree, log_file)

    # Here add the section for the two_dimensional query
    dim_qr.range_skyline_computation()

    # Algorithm execution completed
    end_time_algo = time.time() 
    
    # Log Info
    log_file.write_log_file("Two Dimension Qr:", "*** ALGORITHM 2 FINISHED ***")

# -------------- \ Two Dimensional Query ---------------------

# -------------- Results ---------------------

# Log Info 
log_file.write_log_file("Skyline Size:", str(len(dim_qr.RSS)))
log_file.write_log_file("Max Main Size(H):", str(dim_qr.maximum_main_size))
log_file.write_log_file("Max Sec Size(H'):", str(dim_qr.maximum_secondary_size))
log_file.write_log_file("Domination Checks:", str(dim_qr.domination_checks))
log_file.write_log_file("Rtree build time:", str((end_time_rtree - start_time_rtree) * 1000) + " ms")
log_file.write_log_file("Algorithm time:", str((end_time_algo - start_time_algo - dim_qr.garbage_time) * 1000) + " ms")
log_file.write_log_file("Total time:", str((end_time_algo - start_time_rtree) * 1000) + " ms")
log_file.write_log_file("Range Skylines:", "")

# Print skyline points
print("Skylines:") 
for skyline in dim_qr.RSS:
    print(skyline)
    # Log Info
    log_file.write_log_file("     *", str(skyline))

# -------------- \ Results ---------------------

# Close Log File
log_file.close_log_file()

# \END