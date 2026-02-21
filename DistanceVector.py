# Distance Vector project for CS 6250: Computer Networks
#
# This defines a DistanceVector (specialization of the Node class)
# that can run the Bellman-Ford algorithm. The TODOs are all related 
# to implementing BF. Students should modify this file as necessary,
# guided by the TODO comments and the assignment instructions. This 
# is the only file that needs to be modified to complete the project.
#
# Student code should NOT access the following members, otherwise they may violate
# the spirit of the project:
#
# topolink (parameter passed to initialization function)
# self.topology (link to the greater topology structure used for message passing)
#
# Copyright 2017 Michael D. Brown
# Based on prior work by Dave Lillethun, Sean Donovan, Jeffrey Randow, new VM fixes by Jared Scott and James Lohse.

from Node import *
from helpers import *


class DistanceVector(Node):
    
    def __init__(self, name, topolink, outgoing_links, incoming_links):
        """ Constructor. This is run once when the DistanceVector object is
        created at the beginning of the simulation. Initializing data structure(s)
        specific to a DV node is done here."""

        super(DistanceVector, self).__init__(name, topolink, outgoing_links, incoming_links)
        
        # TODO: Create any necessary data structure(s) to contain the Node's internal state / distance vector data
        self.distance_map = {}
        self.distance_map[self.name] = 0
        for neighbor in self.outgoing_links:
            self.distance_map[neighbor.name] = int(neighbor.weight)

    def send_initial_messages(self):
        """ This is run once at the beginning of the simulation, after all
        DistanceVector objects are created and their links to each other are
        established, but before any of the rest of the simulation begins. You
        can have nodes send out their initial DV advertisements here. 

        Remember that links points to a list of Neighbor data structure.  Access
        the elements with .name or .weight """

        # TODO - Each node needs to build a message and send it to each of its neighbors
        # HINT: Take a look at the skeleton methods provided for you in Node.py
        for neighbor in self.incoming_links:
            msg = (self.name, self.distance_map)
            self.send_msg(msg, neighbor.name)


    def process_BF(self):
        """ This is run continuously (repeatedly) during the simulation. DV
        messages from other nodes are received here, processed, and any new DV
        messages that need to be sent to other nodes as a result are sent. """

        # Implement the Bellman-Ford algorithm here.  It must accomplish two tasks below:
        # TODO 1. Process queued messages       
        updated = False
        for msg in self.messages:            
            sender_name, sender_map = msg
            sender_distance = self.get_outgoing_neighbor_weight(sender_name)
            # if sender_distance == "Node Not Found": Unecessary because if we received a msg, it must be from a valid neighbor that has us as an incoming
            #     continue

            sender_distance = sender_distance[1]
            for dest, cost in sender_map.items():
                if dest == self.name: # A Node can advertise a negative distance for other nodes (but not for itself)
                    continue
                if cost == -99: # A Node that receives an advertisement with a distance of -99 from a downstream neighbor should also assume that it can reach the same destination at infinitely low cost (-99).
                    if self.distance_map[dest] == cost: # Already -99
                        continue
                    self.distance_map[dest] = cost
                    updated = True
                    continue

                new_cost = sender_distance + cost
                new_cost = -99 if new_cost < -99 else new_cost
                original_cost = self.distance_map.get(dest) # Not Guaranteed that we have a direct route to the node our outgoing neighbor has. Must account for None case
                if original_cost == -99: # Avoid infinite negative cycle
                    continue
                if original_cost is None or new_cost < original_cost:
                    self.distance_map[dest] = new_cost
                    updated = True
        
        # Empty queue
        self.messages = []

        # TODO 2. Send neighbors updated distances
        if updated:
            self.send_initial_messages()               

    def log_distances(self):
        """ This function is called immedately after process_BF each round.  It 
        prints distances to the console and the log file in the following format (no whitespace either end):
        
        A:(A,0) (B,1) (C,-2)
        
        Where:
        A is the node currently doing the logging (self),
        B and C are neighbors, with vector weights 1 and 2 respectively
        NOTE: A0 shows that the distance to self is 0 """
        
        # TODO: Use the provided helper function add_entry() to accomplish this task (see helpers.py).
        # An example call that which prints the format example text above (hardcoded) is provided.    
        log = ""
        for dest, cost in self.distance_map.items():
            log += f"({dest},{cost}) "
        log = log.strip()
        add_entry(self.name, log)        
