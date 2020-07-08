#!/usr/bin/python

import heapq
import math
import random
import rectangle as rect

class TwoDimensionalQuery:
    """The 'Two-dimensional Query Intervals' algorithm"""

    def __init__(self, query_start, query_end, dimensions, rtree, logfile):
        """ Constructor """

        self.rtree = rtree
        self.logfile = logfile

        # Query's points
        self.qs = query_start
        self.qe = query_end

        # Query's dimensions
        self.dims = dimensions

        # Heaps
        self.main = []
        self.secondary = []

        # Range Skyline Set
        self.RSS = []

        self.garbage_time = 0
        self.maximum_main_size = 0
        self.maximum_secondary_size = 0
        self.domination_checks = 0

    
    def range_skyline_computation(self):
        """
        The backbone of the algorithm implementation
        """
        # Import the root's keys into the main heap
        for key in self.rtree.root.entries:
            cur_rect = rect.Rectangle(self.qs, self.qe) 
            heapq.heappush(self.main, [self.priority_main(key, self.mindist_point(cur_rect)), id(key), key, cur_rect])
        
        # Check maximum heap size
        if len(self.main) > self.maximum_main_size:
            self.maximum_main_size = len(self.main)

        # Iterate through secondary heap
        sec_heap_empty = False
        while not sec_heap_empty:
            # Iterate through main heap
            while len(self.main) != 0:
                # Remove top entry
                e, qe = list(heapq.heappop(self.main))[2:]
                # Find non dominated rectangle area by RSS points
                qee = self.iterate_rss(self.get_point_closest_to_qs(e), qe)
                if qee != None:
                    
                    # Different mindist points 
                    if not self.same_mindist(qe, qee):
                        # Insert into secondary heap
                        if e.is_leaf:
                            # Data Point
                            heapq.heappush(self.secondary, [self.priority_secondary(self.mindist_point(qee)), id(e), e, qee])
                        else:
                            # MBR
                            #heapq.heappush(self.secondary, [self.priority_secondary(self.mindist_point(qee)), id(e), e, qe])
                            for ee in e.child.entries:
                                heapq.heappush(self.secondary, [self.priority_secondary(self.mindist_point(qee)), id(ee), ee, qe])
                        # Check maximum heap size
                        if len(self.secondary) > self.maximum_secondary_size:
                            self.maximum_secondary_size = len(self.secondary)
                    
                    # Same mindist points
                    else:
                        # MBR
                        if not e.is_leaf:
                            qee = qe
                            # Iterate throuhg the child nodes of e
                            for ee in e.child.entries:

                                qeee = self.iterate_rss(self.get_point_closest_to_qs(ee), qee)
                                
                                if qeee != None:

                                    # Different mindist points
                                    if not self.same_mindist(qee, qeee):
                                        if ee.is_leaf:
                                            # Data Point
                                            heapq.heappush(self.secondary, [self.priority_secondary(self.mindist_point(qeee)), id(ee), ee, qeee])
                                        else:
                                            # MBR
                                            for eee in ee.child.entries:
                                                heapq.heappush(self.secondary, [self.priority_secondary(self.mindist_point(qeee)), id(eee), eee, qee])

                                    # Same mindist points
                                    else:
                                        if ee.is_leaf:
                                            # Data Point
                                            heapq.heappush(self.main, [self.priority_main(ee, self.mindist_point(qeee)), id(ee), ee, qeee])
                                        else:
                                            # MBR
                                            for eee in ee.child.entries:
                                                heapq.heappush(self.main, [self.priority_main(ee, self.mindist_point(qeee)), id(eee), eee, qee])
                                    
                                    # Check maximum heap size
                                    if len(self.main) > self.maximum_main_size:
                                        self.maximum_main_size = len(self.main)
                                    if len(self.secondary) > self.maximum_secondary_size:
                                        self.maximum_secondary_size = len(self.secondary)

                        # Data Point
                        else:
                            # Update the RSS entries' rectangle area
                            self.update_RSS_items(self.get_minDim(e), qee)  
                            # Insert e into the RSS
                            self.RSS.append([self.get_minDim(e), qee])  
                            # Clean entries with None as rectangle area
                            self.RSS = self.clean_RSS(self.RSS)                               

            if len(self.secondary) > 0:
                self.push_to_main()
            else:
                sec_heap_empty = True


    def iterate_rss(self, k, k_rects):
        """
        Iterate through RSS list to find out the 
        domination area and differentiate it from k_rects

            Input: k -> (x1, y1) & k_rects = [Rectangle1, ..., RectangleN]

            Output: List of NON Dominated Rectangles [Rectangle1', ..., RectangleN']
                    or None otherwise
        """

        # Iterate through RSS list
        for rss_entry in self.RSS:

            rss_point = rss_entry[0]
            rss_rects = rss_entry[1]
            # Update k_rects 
            if k_rects != None:
                k_rects = self.non_domination_rectangles(k, rss_point, k_rects, rss_rects)
            
        # Return
        return k_rects

             
    def non_domination_rectangles(self, k, l, k_rects, ref_rects):
        """
        Checks for a rectangle area in which point k is
        not dominated by point l

            Input: k->[x1,y1] & l->[x2,y2] , k_rects = [Rectangle1, ..., RectangleN]

            Output: List of non dominated rectangles [Rectangle1', ..., RectangleN']
                    or None otherwise
        """

        # Make sure  that the ref_rects is a list
        if type(ref_rects) != type(list()):
            ref_rects = [ref_rects]

        # Find the rectangle area in which l dominates k
        for ref_rect in ref_rects:
            domination_rect = self.point_domination(l, k, ref_rect)
            
            if type(domination_rect) == type(list()):
                domination_rect = [ item for item in domination_rect if item != None]
                if len(domination_rect) == 0:
                    domination_rect = None
            
            if domination_rect != None and k_rects != None:
                k_rects = self.rectangle_difference(k_rects, domination_rect)
                if k_rects != None:
                    k_rects = [ item for item in k_rects if item != None]
                    if len(k_rects) == 0:
                        k_rects = None
        
        # Return
        return k_rects


    def point_domination(self, p, r, ref_rect):
        """
        Checks if point p dominates point r in
        every dimension and for which rectangle area

            Input: p->[x1,y1] & r->[x2,y2]

            Output: Rectangle(bottom_left, top_right)
                    or None otherwise
        """
        # Add a domination check
        self.domination_checks += 1

        # Get every dimension, 1,2,...,n 
        all_dims =list(range(1,len(p)+1))
        
        # Check domination for the non query dimensions
        domination = True
        for dimension in all_dims:
            if dimension not in self.dims:
                # The domination does not hold
                if p[dimension - 1] < r[dimension - 1]:
                    domination =  False 
        
        # Domination rectangle
        if type(ref_rect) == type(list()):
            domination_rect = []
            domination_rects = []
            for rect in ref_rect:
                domination_rects.append(self.domination_rectangle(p, r, rect))
            # Keep the not None values
            domination_rect = [ item for item in domination_rects if item != None]
            if len(domination_rect) == 0:
                domination_rect = None
        else:
            domination_rect = self.domination_rectangle(p, r, ref_rect)
        
        if domination and (domination_rect != None):
            rectangle = domination_rect
        else:
            rectangle = None

        # Return
        return rectangle


    def domination_rectangle(self, p, r, ref_rect):
        """
        Given two points, returns the rectangle area in 
        which point p dominates point r. 

            Input: p->[x1,y1] & r->[x2,y2]

            Output: Rectangle(bottom_left, top_right)
                    or None otherwise
        """

        # Find the domination segments for every query dimension
        domination_segs = []
        for dimension in self.dims:
            domination_segs.append(self.domination_segment(p, r, dimension,ref_rect))
        
        # Construct the rectangle
        if None not in domination_segs:
            # Rectangle's points
            bottom_left = []
            top_right = []
            for indx, segment in enumerate(domination_segs):
                 
                 bottom_left.append(segment[0][indx])
                 top_right.append(segment[1][indx])
            
            # Build a Rectangle instance
            domination_rect = rect.Rectangle(bottom_left, top_right)
        else:

            domination_rect = None

        # Return
        return domination_rect      


    def domination_segment(self, p, r, dimension, ref_rect): 
        """
        Checks the cordinates, start and end points,
        for which point p dominates point r for the 
        given dimension

            Input: p->[x1,y1] & r->[x2,y2]

            Output: Line segment -> [(..., x, ...), (..., y, ...)] 
                    or None otherwise
        """
        
        # Get the points' values on the axis the query took place
        p_val = list(p).pop(dimension - 1)
        r_val = list(r).pop(dimension - 1)
        qs_val = list(ref_rect.bottom_left).pop(dimension - 1)
        qe_val = list(ref_rect.top_right).pop(dimension - 1)

        # Find the relative position of the values
        segment = None
        if (p_val < r_val):
            # No.2
            if (p_val <= qs_val <= r_val <= qe_val) and (2*qs_val <= p_val + r_val):
                segment = [qs_val, (p_val+r_val)/2.0]
            # No.3
            elif (p_val <= qs_val <= qe_val <= r_val):
                if (2*qs_val <= p_val + r_val <= 2*qe_val):
                    segment = [qs_val, (p_val+r_val)/2.0]
                elif (2*qe_val <= p_val+r_val):
                    segment = [qs_val, qe_val]
            # No.4
            elif (qs_val <= p_val <= qe_val <= r_val):
                if (p_val+r_val <= 2*qe_val):
                    segment = [qs_val, (p_val+r_val)/2.0]
                else:
                    segment = [qs_val, qe_val]
            # No.5
            elif (qs_val <= p_val < r_val <= qe_val):
                segment = [qs_val, (p_val+r_val)/2.0]
            # No.6
            elif (qs_val <= qe_val <= p_val < r_val):
                segment = [qs_val, qe_val]
        elif  (r_val < p_val):
            # No.7
            if (r_val < p_val <= qs_val <= qe_val):
                segment = [qs_val, qe_val]
            # No.8
            elif (r_val <= qs_val <= p_val <= qe_val):
                if ( 2*qs_val <= p_val+r_val):
                    segment = [(p_val+r_val)/2.0, qe_val]
                else:
                    segment = [qs_val, qe_val]
            # No.9
            elif (r_val <= qs_val <= qe_val <= p_val):
                if (2*qe_val <= p_val+r_val):
                    pass
                elif (2*qs_val <= p_val+r_val <= 2*qe_val):
                    segment = [(p_val+r_val)/2.0, qe_val]
                else:
                    segment = [qs_val, qe_val]
            # No.10
            elif (qs_val <= r_val <= qe_val <= p_val) and (p_val+r_val <= 2*qe_val):
                segment = [(p_val+r_val)/2.0, qe_val]
            # No.11
            elif (qs_val <= r_val < p_val <= qe_val):
                segment = [(p_val+r_val)/2.0, qe_val]
        elif (r_val == p_val):
            segment = [qs_val, qe_val]
        
        # Construct the segment by adding the other dimensions
        if segment != None:
            final_segment = []
            for indx1 in range(2):
                segment_point = []
                for indx2 in range(len(self.qs)):
                    if indx2 !=  dimension - 1:
                        segment_point.append(self.qs[indx2])
                    else:
                        segment_point.append(segment[indx1])
                final_segment.append(tuple(segment_point))
        else:
            final_segment = None

        # Return the segment
        return final_segment


    def rectangle_difference(self,rectA, rectB): 
        """
        Compute the difference rectangle area of 
        two rectangle areas

            Input: rectA = [Rectagle1a, ..., RectangleNa] & rectB = [Rectangle1b, ..., RectangleNb]

            Output: List of rectangles -> [Rectangle1, ..., RectangleN] 
                    or None otherwise
        """
        
        # Ensure that both rectangle areas are lists
        if type(rectA) != type(list()):
            rectA = [rectA]
        if type(rectB) != type(list()):
            rectB = [rectB]
        
        final_list = []
        for recta in rectA:
            # recta = Rectangle
            # recta_list = a list of rectangles
            recta_list = [recta]

            for rectb in rectB:
                # rectb = Rectangle
                curr_diff_rects = []

                for rectangle in recta_list:
                    # curr_diffs = a list of rectangles
                    diffs = list(rectangle - rectb)
                    curr_diff_rects.append(diffs)
                
                # Transform the list of lists into a flaten list with Rectangles
                recta_list = [ item for sublist in curr_diff_rects for item in sublist ]

            final_list.append(recta_list)

        final_list = [ item for sublist in final_list for item in sublist]

        if len(final_list) == 0:
            final_list = None

        # Return
        return final_list


    def same_mindist(self, rects_a, rects_b):
        """
        Check if the minimum distance point in rects_a and the 
        minimum distance point in rects_b are the same.

            Input: qe -> list of Rectangles [Rectangle1, ..., RectangleN]
                   rect_a -> list of Rectangles [Rectangle1A, ..., RectangleNA]
                   rect_b -> list of Rectangles [Rectnagle1B, ..., RectangleNB]
            
            Output: True or False
                    whether the same mindist point 
        """
        # Find the minimum distance points for every rectangle area
        min_dist_point_a = self.mindist_point(rects_a)
        min_dist_point_b = self.mindist_point(rects_b)

        # Check whether the points are the same
        if min_dist_point_a == min_dist_point_b:
            return True
        else:
            return False
        
        
    def rectangle_intersection(self, rectA, rectB):
        """
        Compute the intersection rectangle area of 
        two rectangle areas

            Input: rect_a -> list of Rectangles [Rectangle1A, ..., RectangleNA]
                   rect_b -> list of Rectangles [Rectnagle1B, ..., RectangleNB]

            Output: A list with Rectangles [Rectangle1, ..., RectangleN]
                    or None otherwise
        """
        # Ensure that both rectangle areas are lists
        if type(rectA) != type(list()):
            rectA = [rectA]
        if type(rectB) != type(list()):
            rectB = [rectB]
        
        intersected = []
        for rect_a in rectA:
            for rect_b in rectB:
                area = rect_a & rect_b
                if area != None:
                    intersected.append(area)
        
        if len(intersected) == 0:
            intersected = None

        # Return 
        return intersected


    def update_RSS_items(self, e_dp, rect):
        """
        Iterates through the RSS and checks which RSS's items
        need an update to there rectangle area
        
            Input: e_dp -> data point (x1,y1) & rect -> e's Rectangle area
        """
        for indx, rss_entry in enumerate(self.RSS):

            p = rss_entry[0]
            qp = rss_entry[1]   
            
            # Find the intersection
            if qp != None:
                intersection = self.rectangle_intersection(rect, qp)
            else:
                intersection = None

            if intersection != None:

                # Find the rectangle area, for which e_dp dominates p
                qpp_dominational = self.point_domination(e_dp, p, intersection)

                if qpp_dominational != None:

                    # Find the intersection between the intersection rectangle area
                    # and the qpp_dominational rectangle area
                    qpp = self.rectangle_intersection(qpp_dominational, intersection)

                    if qpp != None:

                        # Exclude from the qp the area that is dominational rectangle area
                        updated = self.rectangle_difference(qp, qpp)

                        # Update the RSS
                        self.RSS[indx] = [ p, updated ]


    def mindist_point(self, rectangles):
        """
        Finds the query point in the rectangles which 
        is located at the minimum distance from qs

            Input: rectangles -> A list of Rectangles: [Rectangle1, ..., RectangleN]

            Output: point -> (x,y)
        """
        # Ensure that rectangle area is a list
        if type(rectangles) != type(list()):
            rectangles = [rectangles]

        # Get the maximum possible distance         
        min_dist = math.hypot(self.qs[0]-self.qe[0], self.qe[1]-self.qs[1]) 

        # rectangles minimum distance point
        for rectangle in rectangles:
            dist = math.hypot(self.qs[0]-rectangle.x1, self.qs[1]-rectangle.y1)
            if dist < min_dist:
                point = [rectangle.x1, rectangle.y1]
                min_dist = dist

        # Return
        return point


    def priority_secondary(self, point):
        """
        Finds the distance between the query's start point
        and the point, which is the point with the minimum 
        distance from the query start point

            Input: point -> (x,y)

            Output: distance -> float
        """
        # Calculate the euclidean distance
        distance = math.sqrt(sum([(a-b) ** 2 for a, b in zip(point, self.qs)]))
        # Return the distance/priority
        return distance


    def priority_main(self, entry, qes):
        """
        Calculates the distance between the entry and the 
        point with the minimum distance from qs.

            Input: entry -> RtreeEntry class & qes -> (x,y)

            Ouput: distance -> float
        """
        # Calculate the euclidean distance
        distance = math.sqrt(sum([(a-b) ** 2 for a, b in zip(qes, self.get_minDim(entry))]))
        # Return the distance/priority
        return distance


    def push_to_main(self):
        """
        Pushes all the entries of the secondary heap,
        that have the same mindist point and the minimum
        distance from the self.qs

            Input: -

            Output: -
        """

        # Get the top entry from the secondary heap
        main_top_entry = heapq.heappop(self.secondary)

        heapq.heappush(self.main, main_top_entry)

        again = True
        heap_size = len(self.secondary)
        position = 0
        while again and (position < heap_size):
            entry = heapq.heappop(self.secondary)
            if self.get_minDim(entry[2]) == self.get_minDim(main_top_entry[2]):
                heapq.heappush(self.main, entry)
                position += 1
            else:
                heapq.heappush(self.secondary, entry)
                again = False
        
        # Check maximum heap size
        if len(self.main) > self.maximum_main_size:
            self.maximum_main_size = len(self.main)


    def get_minDim(self, entry):
        """
        Returns the minimum Dimension coordinates
        of the Rect of the entry

            Input: entry -> class RtreeEntry

            Output: list -> (x,y)
        """
        return [entry.rect.min_x, entry.rect.min_y]


    def get_point_closest_to_qs(self, entry):
        """
        Calculate the coordinates of entry's point which
        is closest to the qs point

            Input: Rtree entry reference

            Output: p -> (x,y)
        """

        qs_x = self.qs[0]
        qs_y = self.qs[1]

        left = qs_x < entry.rect.min_x
        right = qs_x > entry.rect.max_x
        top = qs_y > entry.rect.max_y
        bottom = qs_y < entry.rect.min_y

        if top and left:
            return [entry.rect.min_x, entry.rect.max_y]
        elif top and right:
            return [entry.rect.max_x, entry.rect.max_y]
        elif bottom and left:
            return [entry.rect.min_x, entry.rect.min_y]
        elif bottom and right:
            return [entry.rect.max_x, entry.rect.min_y]
        elif top:
            return [qs_x, entry.rect.max_y]
        elif bottom:
            return [qs_x, entry.rect.min_y]
        elif right:
            return [entry.rect.max_x, qs_y]
        elif left:
            return [entry.rect.min_x, qs_y]
        else:
            return self.qs


    def clean_RSS(self, RSS) -> list:
        """
        Takes away the entries that have None as a rectangle area

            Parameters: list -> [ [point, rectangle area], [point, None], ... ]

            Output: list -> [ [point1, rectangle area1], [point2, rectangle area2], ...]
        """
        clean_RSS = []
        for item in RSS:
            rectangle_area = item[1]
            if rectangle_area != None:
                clean_RSS.append(item)
        
        # Return
        return clean_RSS
