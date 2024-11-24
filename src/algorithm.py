import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import numpy as np
import pandas as pd
from graph import DAG


class LCL:
    '''
    Apply Least Cost Last (LCL) algorithm on a Directed Acyclic Graph (DAG).

    Args:
        graph (DAG): DAG to be optimized on.
    '''
    def __init__(self, graph) -> None:
        self.graph = graph
        self.schedule = []
        # initialise with total completion time
        self.completion_time_j = np.sum([self.graph.nodes[i].processing_time for i in range(self.graph.node_num)])
        self.iteration = 0
        self.g_max = 0

    def cost_function(self, j) -> float:
        dj = self.graph.nodes[j].due_date
        Cj = self.completion_time_j
        gj_Cj = np.max([0, Cj - dj])

        self.completion_time_j -= self.graph.nodes[j].processing_time
        return gj_Cj
    

    def find_schedule(self, printEachIteration):
        for self.iteration in range(self.graph.node_num):
            # store all last jobs' cost inside V set
            gj_list = [self.cost_function(node_index) for node_index in self.graph.V]
            # get index of the job in set V with the least cost
            min_index = np.argmin(gj_list)
            # get the g*max from currently scheduled nodes
            self.g_max = np.maximum(np.max(gj_list), self.g_max)
            # convert from 0 indexing to 1 indexing to get original node number
            # add node to the front of schedule (schedule in a reversed order)
            self.schedule = np.insert(self.schedule, 0, self.graph.V[min_index] + 1)
            # pop out the node with the least cost
            self.graph.pop_node(self.graph.V[min_index], node_type="last")

            if (printEachIteration):
                # print("-----------------------------------------------------")
                # +1 to convert to 1 indexing
                iteration_type = "final" if self.iteration == self.graph.node_num - 1 else "partial"
                schedule_list = [int(node) for node in self.schedule]
                print(f"In iteration {self.iteration + 1}: ")
                print(f"{iteration_type} schedule S = {schedule_list}")

class TabuSearch:
    '''
    Apply Tabu Search algorithm on a Directed Acyclic Graph (DAG).

    Args:
        graph (DAG): DAG to be optimized on.
    '''
    def __init__(self, graph) -> None:
        self.graph = graph

    def find_schedule(self, L: int, K: int, gamma: int, initial_schedule: list, aspiration_criterion: bool=False):
        '''
        Apply tabu search with initialized parameters to minimize total tardiness.

        Args:
            L (int): Length of tabu list.
            K (int): Amount of solutions found (initial solution is 0).
            gamma (int): Tolerance from g_best to accept solution. 
            initial_schedule (list): Schedule to be optimized on.
            aspiration_criterion (bool): Optional aspiration criterion that accepts solution incl. in tabu list if it improves g_best. Default is False.
        '''

        # set values of tabu search
        self.L = L
        self.K = K
        self.gamma = gamma
        self.schedule = initial_schedule.copy()

        # index where new cycle starts
        new_cycle_index = 0
        # tracker of amount of solutions found 
        k = 0
        # empty tabu list
        tabu_list = []

        # calculate initial solution
        g_best = self.total_tardiness()
        best_solution = self.schedule.copy()
        print(f"The initial solution S = {best_solution} has a total tardiness of {g_best}")

        # infinite loop stopped when K solutions found or no better solution found in one complete cycle
        while k < self.K:
            # track if solution found in current cycle
            found_solution_in_cycle = False

            # iterate from last position where solution was found
            for i in range(new_cycle_index, new_cycle_index + self.graph.node_num - 1):
                # restrict indices to possible indices of list using modulo
                current_index = i % (self.graph.node_num - 1)
                
                # define swap pair and sort them
                swap_pair = (self.schedule[current_index], self.schedule[current_index + 1])
                swap_pair = tuple(sorted(swap_pair))

                # swap two neighbouring nodes
                self.schedule[current_index], self.schedule[current_index + 1] = self.schedule[current_index + 1], self.schedule[current_index]

                # check validity of solution and skip current iteration if not valid
                if self.check_validity() == False:
                    # swap back
                    self.schedule[current_index], self.schedule[current_index + 1] = self.schedule[current_index + 1], self.schedule[current_index]        
                    continue
                
                # calculate tardiness of current schedule
                current_tardiness = self.total_tardiness()
                
                # calculate delta of current schedule
                delta = g_best - current_tardiness
                
                # accept solution if delta is higher than -gamma and not from tabu list
                # if aspiration_criterion is set to true also check this criterion (one of both criterion to accept solution)
                if (delta > (- self.gamma) and (swap_pair not in tabu_list)) or (aspiration_criterion==True and current_tardiness < g_best):
                    found_solution_in_cycle = True
                    
                    # save solution if better than current g_best
                    if current_tardiness < g_best: 
                        g_best = current_tardiness
                        best_solution = self.schedule.copy()
                        print(f"Improved solution found with total tardiness = {g_best} (current k = {k+1})")
                    
                    # update where new cycle should start
                    new_cycle_index = current_index + 1
                    
                    # add swap pair to tabu list and remove the oldest entry if the list is too long
                    tabu_list.append(swap_pair)
                    if len(tabu_list) > self.L:
                        tabu_list.pop(0)
                        
                    # increment amount of solutions found and start new cycle
                    k += 1
                    break
                    
                else:
                    # revert swap if not accepted as a solution
                    self.schedule[current_index], self.schedule[current_index + 1] = self.schedule[current_index + 1], self.schedule[current_index]
                    
            # terminate search if no solution found in one cycle
            if not found_solution_in_cycle:
                print(f"\nNo further improvements found. Terminated search at k = {k}.")
                print(f"Best solution: S = {best_solution}")
                print(f"Total Tardiness = {g_best}\n")
                return

        print(f"\nTerminated search at k = {k}.") 
        print(f"Best solution found: S = {best_solution}")
        print(f"Total Tardiness of {g_best}\n")
        return


    def check_validity(self):
        '''
        Check if the current schedule is valid based on DAG dependencies in adjacency matrix.
        '''
        # keep track of already scheduled jobs
        scheduled_set = set()

        for scheduled_node in self.schedule:
            # adjust scheduled_node to 0 indexing (currently 1 indexed)
            scheduled_node -= 1
            
            # add current node to schedule
            scheduled_set.add(scheduled_node)

            # check if all predecessors are already scheduled
            for pred_node in range(self.graph.node_num):
                if self.graph.G_matrix[pred_node, scheduled_node] == 1 and pred_node not in scheduled_set:
                    return False
        
        return True
    

    def total_tardiness(self):
        '''
        Calculate the total tardiness for the current schedule.
        '''
        # cumulative processing time as we process each node
        total_processing_time = 0
        # accumulated tardiness
        total_tardiness = 0
        
        # Iterate over each node in the schedule
        for scheduled_node in self.schedule:
            node = self.graph.nodes[scheduled_node - 1]
            total_processing_time += node.processing_time
            
            # calculate tardiness of current node and add to total
            tardiness = max(node.due_date - total_processing_time, 0)
            total_tardiness += tardiness

        return total_tardiness