#!/usr/bin/python

from gpcharts import figure as gpFig

class RangeChart():
    """
    Creation of a chart with the data points
    """

    def __init__(self, queryPoints, dataPoints):
        self.xVals = ["x"]
        self.yVals = ["Data Points"]

        # Read the query file
        with open(queryPoints, 'r') as query:
            # Get the dimension on which a range preference is provided
            dimension = query.readline()
            # Get the range preference as a list of typles for qs and qe
            queryRng = list( query.readline().split() )
            queryStrPoint, queryFnshPoint = [tuple(map(float, word.split(","))) for word in queryRng]

        self.xVals.append(queryStrPoint[0])
        self.yVals.append(queryStrPoint[1])

        self.xVals.append(queryFnshPoint[0])
        self.yVals.append(queryFnshPoint[1])

        # Read the data file
        with open(dataPoints, 'r') as data:
            for row in data:
                minMbr = list(map(float, row.split()))
                # Append x and y
                self.xVals.append(minMbr[0])
                self.yVals.append(minMbr[1])

                # Add the projection of every data point based on the distance from the range query
                if minMbr[0] < queryStrPoint[0]:
                    newStartPointX = minMbr[0] + 2*(queryStrPoint[0] - minMbr[0])
                else:
                    newStartPointX = minMbr[0]
                
                if minMbr[0] < queryFnshPoint[0]:
                    newEndPointX = minMbr[0] +  2*(queryFnshPoint[0] - minMbr[0])
                else:
                    newEndPointX = minMbr[0]
                
                if minMbr[1] < queryStrPoint[1]:
                    newStartPointY = minMbr[1] + 2*(queryStrPoint[1] - minMbr[1])
                else:
                    newStartPointY = minMbr[1]
                
                if minMbr[1] < queryFnshPoint[1]:
                    newEndPointY = minMbr[1] + 2 * (queryFnshPoint[1] - minMbr[1])
                else:
                    newEndPointY = minMbr[1]
                
                self.xVals.append(newStartPointX)
                self.yVals.append(newStartPointY)

                self.xVals.append(newEndPointX)
                self.yVals.append(newEndPointY)

        
    
    def createChart(self):
        """
        Create the chart
        """

        my_fig = gpFig(xlabel='x',ylabel='y',height=600,width=1600)

        my_fig.title = 'Range Skyline Data'

        my_fig.scatter(self.xVals, self.yVals)



