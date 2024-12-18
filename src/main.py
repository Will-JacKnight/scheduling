import pandas as pd

from algorithm import LCL, TabuSearch
from graph import DAG


# input data, change data here
print("-----------------------Data Importing-------------------------")
df = pd.read_excel("data/data.xlsx", usecols="A:D")
edges = [(0, 30), (1, 0), (2, 7), (3, 2), (4, 1),
        (5, 15), (6, 5), (7, 6), (8, 7), (9, 8),
        (10, 0), (11, 4), (12, 11), (13, 12), (16, 14),
        (14, 10), (15, 4), (16, 15), (17, 16), (18, 17),
        (19, 18), (20, 17), (21, 20), (22, 21), (23, 4),
        (24, 23), (25, 24), (26, 25), (27, 25), (28, 26),
        (28, 27), (29, 3), (29, 9), (29, 13), (29, 19),
        (29, 22), (29, 28)]
graph = DAG(node_num=31, edges=edges, node_data=df)
print("----------------------DAG Graph Loaded------------------------")


# Question 1: utilising LCL to find the optimal solution for 1|prec|g*max problem
print("\n-------------------Results for Question 1---------------------")
print("This part is designed to utilise LCL algorithm for finding the optimal solution for 1|prec|g*max problem. \n")

algo = LCL(graph=graph)
algo.find_schedule(verbose=True)


# Question 2: tabu search for approximate optimal solution for 1|prec|sum_Tj problem
print("\n-------------------Results for Question 2---------------------")
print("This part is designed to use tabu search for finding the optimal solution for 1|prec|sum_Tj problem. \n")

# 1-indexing as user input (initial solution)
initial_solution = [30, 29, 23, 10, 9, 14, 13, 12, 4, 20, 22, 3, 27, 28, 8, 7, 19, 21, 26, 18, 25, 17, 15, 6, 24, 16, 5, 11, 2, 1, 31]
algo = TabuSearch(graph=graph)

# try with different numbers of K (10, 100, 1000)
# algo.find_schedule(L=20, K=10, gamma=10, initial_schedule=initial_solution, aspiration_criterion=True, verbose=2)
# algo.find_schedule(L=20, K=100, gamma=10, initial_schedule=initial_solution, aspiration_criterion=True, verbose=2)
print("Only run K=1000 as it also includes the tabu search for K=10 and K=100 when looking at the early iterations\n")
print("Tabu Search for L=20, K=1000, gamma=10 including all iterations:\n")
algo.find_schedule(L=20, K=1000, gamma=10, initial_schedule=initial_solution, aspiration_criterion=True, verbose=2)

print("Tabu Search for L=20, K=1000, gamma=10 only with solutions improving g_best:\n")
algo.find_schedule(L=20, K=1000, gamma=10, initial_schedule=initial_solution, aspiration_criterion=True, verbose=1)

# check that algorithm also works for random initial schedule
# algo.find_schedule(L=20, K=10, gamma=10, aspiration_criterion=True, verbose=2)