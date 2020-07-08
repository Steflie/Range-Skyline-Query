#!/usr/bin/python

import heapq
import math 
import numpy as np
import rtreelib

 
class SingleDimensionalQuery():
    """The 'Single Dimensional Query Intervals' algorithm"""

    def __init__(self, query_start, query_end, dimension, rtree, logfile):
        """
        The constructor of the class

            Parameters: query_start -> [x, y]
                        query_end   -> [x, y]
                        dimension   -> int that refers to the dimension the query took place
                        rtree       -> reference to the implementation of the Rtree with the 
                                       data points
                        logfile     -> reference to the logfile object
        """
        
        self.qs = query_start
        self.qe = query_end
        self.dim = dimension
        self.rtree = rtree
        self.logfile = logfile
        # Range Skyline Set
        self.RSS = []
        
        # The priority heaps
        self.main = []
        self.secondary = [] 

        self.maximum_main_size = 0
        self.maximum_secondary_size = 0
        self.domination_checks = 0
        

    def range_skyline_computation(self):
        """
        The backbone of the algorithms implementation
        """

        # Get the Root node's entries
        for entry in self.rtree.root.entries:
            segment = [self.qs, self.qe]
            self.insert_into_main_heap(entry, segment)

        if len(self.main) > self.maximum_main_size:
            self.maximum_main_size = len(self.main)
        
        secondary_heap_empty = False
        while not secondary_heap_empty:
            while len(self.main) != 0:
                e, Le = self.remove_top_entry(self.main)
                # Logfile
                self.logfile.write_log_file("e:",str(e.rect.min_x)+","+str(e.rect.min_y)+" - "+str(e.rect.max_x)+","+str(e.rect.max_y))
                self.logfile.write_log_file("Le:",str(Le))
                
                e_mbr_mindist = self.get_mbr_mindist(e)
                Lee = self.iterate_RSS_for_nonDomination_segment(e_mbr_mindist, Le)
                try: 
                    # Different starting points
                    if Lee[0] != Le[0]:
                        self.logfile.write_log_file("Lee: ", str(Lee))
                        self.logfile.write_log_file("Diff starts:", "Lee[0] != Le[0]")
                        # Check if data point or mbr and insert analogously
                        if e.is_leaf:
                            # Data Point
                            self.insert_into_secondary_heap(e, Lee)
                        else:
                            # MBR
                            #self.insert_into_secondary_heap(e, Le)
                            for ee in e.child.entries:
                                self.insert_into_secondary_heap(ee, Le)
                        # Check maximum heap size
                        if len(self.secondary) > self.maximum_secondary_size:
                            self.maximum_secondary_size = len(self.secondary)
                   
                    # Same starting points
                    else:
                        # Logfile
                        self.logfile.write_log_file("Lee:", str(Lee))
                        self.logfile.write_log_file("Same starts", "Lee[0] == Le[0]") 
                        # MBR 
                        if not e.is_leaf: 
                            # Logfile
                            self.logfile.write_log_file("e", "is an MBR")
                            Lee = Le
                            for ee in e.child.entries:
                                ee_mbr_mindist = self.get_mbr_mindist(ee)
                                Leee = self.iterate_RSS_for_nonDomination_segment(ee_mbr_mindist, Lee)
                                try: 
                                    # Different starting points
                                    if Leee[0] != Lee[0]:
                                        if ee.is_leaf:
                                            # Data Point
                                            self.insert_into_secondary_heap(ee, Leee)
                                        else:
                                            # MBR
                                            #self.insert_into_secondary_heap(ee, Lee)
                                            for eee in ee.child.entries:
                                                self.insert_into_secondary_heap(eee, Lee)
                                        # Check maximum heap size
                                        if len(self.secondary) > self.maximum_secondary_size:
                                            self.maximum_secondary_size = len(self.secondary)
                                    else:
                                        if ee.is_leaf:
                                            # Data Point
                                            self.insert_into_main_heap(ee, Leee)
                                        else:
                                            # MBR
                                            #self.insert_into_main_heap(ee, Lee)
                                            for eee in ee.child.entries:
                                                self.insert_into_main_heap(eee, Lee)
                                        # Check maximum heap size
                                        if len(self.main) > self.maximum_main_size:
                                            self.maximum_main_size = len(self.main)
                                except TypeError:
                                    self.logfile.write_log_file("Leee", "Is NONE")
                                    pass
                        # Leaf - Data Point
                        else:
                            # Logfile
                            self.logfile.write_log_file("e", "is a LEAF - Data Point")
                            for index, rss_entry in enumerate(self.RSS):
                                rss_point, Lp = rss_entry[0], rss_entry[1]
                                # Check for intersection
                                Lp_inter_Lee = self.segment_intersection(Lp, Lee)
                                if Lp_inter_Lee != None:
                                    Lpp = self.point_domination(e.data, rss_point, Lp_inter_Lee) 
                                    if Lpp != None:
                                        # Lp - Lpp
                                        new_Lp = self.segment_difference(Lp, Lpp)
                                        self.RSS[index] = [rss_point, new_Lp]
                            # Insert the new entry into RSS
                            self.RSS.append([e.data, Lee])
                            # Clean entries with None as rectangle area
                            self.RSS = self.clean_RSS(self.RSS)
                            # Logfile
                            self.logfile.write_log_file("RSS", str(self.RSS))
                except TypeError:
                    self.logfile.write_log_file("Lee:","Is NONE")
                    pass
            
            if len(self.secondary) == 0:
                secondary_heap_empty = True
            else:
                # Move entries from secondary into main
                self.push_to_main()


    def priority_main(self, e_mindist, e_segment) -> float:
        """
        Calculate the priority of an Rtree entry for the main heap.
        The priority is the distance between the mindist point of Rtree entry
        and the left most point of entry's non dominational segment.

            Parameters: e_mindist -> point (x, y)
                        e_segment -> segment [(x1, y1), (x2, y2)]
            
            Output: float 
        """
        
        # Euclidean distance
        x, y = e_mindist[0], e_mindist[1]
        x1, y1 = e_segment[0][0], e_segment[0][1]

        return math.sqrt((x-x1)**2 + (y-y1)**2)


    def priority_secondary(self, segment) -> float:
        """
        Calculate the priority of an Rtree entry for the secondary heap.
        The priority is the distance of segment's left starting point (qes)
        from query's left starting point (qs)

            Parameters: segment -> line segment [(qes_x, qes_y), (qee_x, qee_y)]

            Output : float
        """

        # The non dominational segment and the query segment are the same segments
        # with the only difference that the non dominational segment might be smaller
        # if a dominational segment has been found previously
        # Therefore the distance of the starting points is the difference qes - qs
        # on the axes the query has taken place
        seg_start = segment[0]
        return seg_start[self.dim - 1] - self.qs[self.dim - 1] 


    def get_mbr_mindist(self, entry) -> (float, float):
        """
        Every Rtree Entry represents an MBR.
        The mindist point of an MBR is the point with the 
        minimum distance from query's start point qs.

            Parameters: entry      -> RTreeEntry object, 
                        entry.rect -> Represents the MBR, 
                                        rect.min_x & rect.min_y is the lower left corner
                                        rect.max_x & rect.max_y is the top right corner
            
            Output: Point, (x,y)
        """
        
        # Query's start point
        qs_x, qs_y = (self.qs[0], self.qs[1])
        # MBR lower left and top right corners
        min_x, min_y = entry.rect.min_x, entry.rect.min_y
        max_x, max_y = entry.rect.max_x, entry.rect.max_y

        # Find the relative position of qs to the MBR
        is_top = qs_y > max_y
        is_bottom =  qs_y < min_y
        is_left = qs_x < min_x
        is_right = qs_x > max_x

        # Return the qs's projection onto the MBR
        if is_top and is_left:
            return [min_x, max_y]
        elif is_top and is_right:
            return [max_x, max_y]
        elif is_bottom and is_left:
            return [min_x, min_y]
        elif is_bottom and is_right:
            return [max_x, min_y]
        elif is_top:
            return [qs_x, max_y]
        elif is_bottom:
            return [qs_x, min_y]
        elif is_left:
            return [min_x, qs_y]
        elif is_right:
            return [max_x, qs_y]
        else:
            # Inside the MBR
            return [qs_x, qs_y]


    def insert_into_main_heap(self, entry, segment):
        """
        Insert into the main heap a new entry 

            Parameters: entry   -> RTreeEntry object
                        segment -> segment [(x1, y1), (x2, y2)]
        """

        mindist_point = self.get_mbr_mindist(entry)
        priority = self.priority_main(mindist_point, segment)

        # Use id() in case of priority collision
        heapq.heappush(self.main, [priority, id(entry), entry, segment])


    def insert_into_secondary_heap(self, entry, segment):
        """
        Insert into the secondary heap a new entry

            Parameters: entry   -> RTreeEntry object
                        segment -> segment [(x1,y1), (x2,y2)]
        """

        priority = self.priority_secondary(segment)

        # Use id() in case of priority collision
        heapq.heappush(self.secondary, [priority, id(entry), entry, segment])


    def remove_top_entry(self, heap) -> [rtreelib.rtree.RTreeEntry , [(float,float),(float,float)]]:
        """
        Return the RTreeEntry object and the segment and
        exclude the priority and the id()

            Parameters: heap -> list with heap framework

            Output: list -> [RTreeEntry, segment]
                            segment -> [(x1,y1), (x2,y2)]
        """
        
        heap_top_entry = heapq.heappop(heap)
        # Keep only the RtreeEntry and the segment
        return heap_top_entry[2:]


    def iterate_RSS_for_nonDomination_segment(self, r_point, r_segm) -> [(float,float),(float,float)]:
        """
        Checks if there is a non dominational sub segment for r_point, 
        in comparison to every point of RSS

            Parameters: r_point -> (xr,yr) 
                        r_segm  -> [(xs,ys), (xe,ye)]

            Output:     segment -> [(x1,y1), (x2,y2)] or None
        """
        
        for rss_entry in self.RSS:
            rss_point, rss_segm = rss_entry[0], rss_entry[1]

            # I have to check if the r_nonDomination_segm is not None, due to previous function call
            # if it is not I call again the funtion
            # if it is None the for the rest of RSS points I will not process further
            if r_segm != None:
                r_nonDomination_seg = self.nonDomination_segment(rss_point, r_point, rss_segm, r_segm)
                r_segm = r_nonDomination_seg
            else:
                pass

        return r_segm

    
    def nonDomination_segment(self, p_point, r_point, p_segm, r_segm) -> [(float,float),(float,float)]:
        """
        The non domination segment is the current r_segm differentiated by the
        domination segment of p to r in relation to p_segm 

            Parameters: p_point -> (xp,yp)
                        r_point -> (xr,yr)
                        p_segm  -> [(xp_s,yp_s),(xp_e,yp_e)]
                        r_segm  -> [(xr_s,yr_s),(xr_e,yr_e)]

            Output:     segment -> [(x1,y1),(x2,y2)] or None
        """
        
        domination_segment = self.point_domination(p_point, r_point, p_segm)
        # To differentiate, the domination_segment has to be != None
        if domination_segment != None:
            non_domination_segment = self.segment_difference(r_segm, domination_segment)
        else:
            non_domination_segment = r_segm

        return non_domination_segment


    def point_domination(self, p_point, r_point, ref_segm) -> [(float,float),(float,float)]:
        """
        Calculate the domination segment and if the non query dimensions
        meet the requirements for domination

            Parameters: p       -> [x1,y1] 
                        r       -> [x2,y2]
                        ref_seg -> [(qs_x, qs_y), (qe_x,qe_y)]

            Output: Line segment -> [(x, y), (x, y)] or None
        """
        # Add a domination check
        self.domination_checks += 1
        
        # Get the dominational segment
        dominational_segm = self.domination_segment(p_point, r_point, ref_segm)

        domination = True
        # Check if the domination holds for the rest dimensions
        for indx in range(len(p_point)):
            # Do not take into account the query dimension
            if indx != self.dim -1:
                p_point_dist = abs(self.qs[indx] - p_point[indx])
                r_point_dist = abs(self.qs[indx] - r_point[indx])
                if r_point_dist < p_point_dist:
                    domination = False
        
        # Return
        if (dominational_segm != None) and (domination):
            return dominational_segm
        else:
            return None


    def domination_segment(self, p_point, r_point, ref_segm) -> [(float,float),(float,float)]: 
        """
        Specifying the range of the coordinate values on the i-axis 
        of all the points q that belong to hte ref_seg in relation
        to which p dominates r

            Input: p       -> [x1,y1] 
                   r       -> [x2,y2]
                   ref_seg -> [(qs_x, qs_y), (qe_x,qe_y)]

            Output: Line segment -> [(x1, y1), (x2, y2)] or None
        """
         
        # Get the points' values on the axis the query took place
        p_val = list(p_point).pop(self.dim - 1)
        r_val = list(r_point).pop(self.dim - 1)
        qs_val = list(ref_segm[0]).pop(self.dim - 1)
        qe_val = list(ref_segm[1]).pop(self.dim - 1)

        # Find the relative position of the values
        range_values= None
        if (p_val < r_val):
            # No.2
            if (p_val <= qs_val <= r_val <= qe_val) and (2*qs_val <= p_val + r_val):
                range_values= [qs_val, (p_val+r_val)/2.0]
            # No.3
            elif (p_val <= qs_val <= qe_val <= r_val):
                if (2*qs_val <= p_val + r_val <= 2*qe_val):
                    range_values= [qs_val, (p_val+r_val)/2.0]
                elif (2*qe_val <= p_val+r_val):
                    range_values= [qs_val, qe_val]
            # No.4
            elif (qs_val <= p_val <= qe_val <= r_val):
                if (p_val+r_val <= 2*qe_val):
                    range_values= [qs_val, (p_val+r_val)/2.0]
                else:
                    range_values= [qs_val, qe_val]
            # No.5
            elif (qs_val <= p_val < r_val <= qe_val):
                range_values= [qs_val, (p_val+r_val)/2.0]
            # No.6
            elif (qs_val <= qe_val <= p_val < r_val):
                range_values= [qs_val, qe_val]
        elif  (r_val < p_val):
            # No.7
            if (r_val < p_val <= qs_val <= qe_val):
                range_values= [qs_val, qe_val]
            # No.8
            elif (r_val <= qs_val <= p_val <= qe_val):
                if ( 2*qs_val <= p_val+r_val):
                    range_values= [(p_val+r_val)/2.0, qe_val]
                else:
                    range_values= [qs_val, qe_val]
            # No.9
            elif (r_val <= qs_val <= qe_val <= p_val):
                if (2*qe_val <= p_val+r_val):
                    pass
                elif (2*qs_val <= p_val+r_val <= 2*qe_val):
                    range_values= [(p_val+r_val)/2.0, qe_val]
                else:
                    range_values= [qs_val, qe_val]
            # No.10
            elif (qs_val <= r_val <= qe_val <= p_val) and (p_val+r_val <= 2*qe_val):
                range_values= [(p_val+r_val)/2.0, qe_val]
            # No.11
            elif (qs_val <= r_val < p_val <= qe_val):
                range_values= [(p_val+r_val)/2.0, qe_val]
        elif (r_val == p_val):
            range_values= [qs_val, qe_val]
        
        # Construct the segment by adding the other dimensions
        if range_values!= None:
            segment = []
            # range(2), cause start and end points
            for indx1 in range(2):
                segment_point = []
                for indx2 in range(len(self.qs)):
                    if indx2 !=  self.dim - 1:
                        segment_point.append(self.qs[indx2])
                    else:
                        segment_point.append(range_values[indx1])
                segment.append(tuple(segment_point))
        else:
            segment = None

        # Return the segment
        return segment


    def segment_difference(self, segm_a, segm_b) -> [(float,float),(float,float)]:
        """
        Given two segments, the difference between segm_a and segm_b is 
        segm_a - segm_b

            Parameters: segm_a  -> [(xa1,ya1),(xa2,ya2)]
                        segm_b  -> [(xb1,yb1),(xb2,yb2)]
            
            Output:     segment -> [(x1,y1),(x2,y2)]
        """
        
        # Take the values on the axis that the query took place
        segm_a_start = segm_a[0][self.dim - 1]
        segm_a_end = segm_a[1][self.dim - 1]
        segm_b_start = segm_b[0][self.dim - 1]
        segm_b_end = segm_b[1][self.dim - 1]

        # Create a range from start to end for the segments
        segm_a_range = [round(float(item), 3) for item in np.arange(segm_a_start, segm_a_end + 0.001, 0.001) if round(float(item), 3) <= segm_a_end]
        segm_b_range = [round(float(item), 3) for item in np.arange(segm_b_start, segm_b_end + 0.001, 0.001) if round(float(item), 3) <= segm_b_end]

        # Take the difference of the two ranges/segments
        diff = list(set(segm_a_range) - set(segm_b_range))
        # Sort the difference
        diff.sort()

        # Construct the new segment
        if diff:
            # Keep only the first and last element
            diff = [diff[0], diff[len(diff)-1]]
            final_segment = []
            for indx1 in range(2):
                segment_point = []
                for indx2 in range(len(self.qs)):
                    if indx2 !=  self.dim - 1:
                        segment_point.append(self.qs[indx2])
                    else:
                        segment_point.append(diff[indx1])
                final_segment.append(tuple(segment_point))
        else:
            final_segment = None
        
        # Return
        return final_segment


    def segment_intersection(self, segm_a, segm_b) -> [(float,float),(float,float)]:
        """
        Calculate the intersection of two segments

            Parameters: segm_a -> [(xa1,ya1),(xa2,ya2)]
                        segm_b -> [(xb1,yb1),(xb2,yb2)]
            
            Output:     segment -> [(x1,y1),(x2,y2)]  
        """

        # Take the values on the axis that the query took place
        segm_a_start = segm_a[0][self.dim - 1]
        segm_a_end = segm_a[1][self.dim - 1]
        segm_b_start = segm_b[0][self.dim - 1]
        segm_b_end = segm_b[1][self.dim - 1]
        
        # Create a range from start to end for the segments
        segm_a_range = [round(float(item), 3) for item in np.arange(segm_a_start, segm_a_end + 0.001, 0.001) if round(float(item), 3) <= segm_a_end]
        segm_b_range = [round(float(item), 3) for item in np.arange(segm_b_start, segm_b_end + 0.001, 0.001) if round(float(item), 3) <= segm_b_end]

        # Take the difference of the two ranges/segments
        diff = list(set(segm_a_range) & set(segm_b_range))
        # Sort the difference
        diff.sort()

        # Construct the new segment
        if diff:
            # Keep only the first and last element
            diff = [diff[0], diff[len(diff)-1]]
            final_segment = []
            for indx1 in range(2):
                segment_point = []
                for indx2 in range(len(self.qs)):
                    if indx2 !=  self.dim - 1:
                        segment_point.append(self.qs[indx2])
                    else:
                        segment_point.append(diff[indx1])
                final_segment.append(tuple(segment_point))
        else:
            final_segment = None
        
        # Return
        return final_segment


    def push_to_main(self):
        """
        Pushes the entries with higher priority into the queue from the secondary heap 
        to the main heap
        """

        # Take top entry 
        rtree_entry, segment = self.remove_top_entry(self.secondary)
        self.insert_into_main_heap(rtree_entry, segment)

        backup_list = []
        for index in range(len(self.secondary)):
            next_rtree_entry, next_segment = self.remove_top_entry(self.secondary)
            if next_segment[0] == segment[0]:
                self.insert_into_main_heap(next_rtree_entry, next_segment)
            else:
                backup_list.append([next_rtree_entry, next_segment])

        # Put back to secondary heap 
        for pair in backup_list:
            self.insert_into_secondary_heap(pair[0], pair[1]) 

        # Check maximum heap size
        if len(self.main) > self.maximum_main_size:
            self.maximum_main_size = len(self.main)
        if len(self.secondary) > self.maximum_secondary_size:
            self.maximum_secondary_size = len(self.secondary)


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