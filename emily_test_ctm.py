# This scripts initializes a Model_Manager object a Traffic_Model and Cost_Function object
# It uses as input a Demand_Assignment objects (demand per path and per time) to generate costs per path as
# a Path_Costs object
# This particular model uses a Static model and BPR Cost_Function model

import numpy as np
from copy import deepcopy

# from Cost_Functions.BPR_Function import BPR_Function_class
# from Traffic_Models.Static_Model import Static_Model_Class
from Solvers.Solver_Class import Solver_class
# from Data_Types.Demand_Assignment_Class import Demand_Assignment_class
# from Data_Types.Link_Costs_Class import Link_Costs_class
# from py4j.java_gateway import JavaGateway,GatewayParameters
from Model_Manager.Link_Model_Manager import Link_Model_Manager_class
from Model_Manager.BeATS_Model_Manager import BeATS_Model_Manager_class
from Java_Connection import Java_Connection
from Data_Types.Demand_Assignment_Class import Demand_Assignment_class
from Traffic_Models.Abstract_Traffic_Model import Abstract_Traffic_Model_class
from copy import copy
import matplotlib.pyplot as plt
import os
import inspect
import csv
from Solvers.Path_Based_Frank_Wolfe_Solver import Path_Based_Frank_Wolfe_Solver

plt.rcParams.update({'font.size': 18})

connection = Java_Connection()

if connection.pid is not None:
    this_folder = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
    configfile = os.path.join(this_folder, os.path.pardir, 'configfiles', 'cfg_vi_ctm.xml')
    coefficients = {}
    T = 3600  # Time horizon of interest
    sim_dt = 4.0  # Duration of one time_step for the traffic model

    sampling_dt = 4     # Duration of time_step for the solver, in this case it is equal to sim_dt
    model_manager_beats = BeATS_Model_Manager_class(configfile, connection.gateway, sim_dt)
    route = {}
    route['1'] = [0, 3, 4, 5]
    route['2'] = [0, 2, 4, 5]
    route['3'] = [1, 3, 4, 5]
    demand = {}
    demand['1'] = [100]
    demand['2'] = [100]
    demand['3'] = [100]
    od = list(model_manager_beats.beats_api.get_od_info())
    num_steps = int(T / sampling_dt)

    # Initializing the demand assignment
    commodity_list = list(model_manager_beats.beats_api.get_commodity_ids())
    assignment = Demand_Assignment_class(route, commodity_list, num_steps, sampling_dt)
    assignment.set_all_demands(demand)
    #  model_manager.beats_api.get_link_with_id(long(i)).get_ffspeed_mps())/3600
    #print assignment.print_all()
    #print assignment.get_commodity_list()
    #print assignment.get_path_list()
    model = Abstract_Traffic_Model_class(model_manager_beats.beats_api)
    eval = model_manager_beats.evaluate(assignment, T, initial_state=None)

    #print eval.get_all_path_costs()
    # kill jvm

    connection.close()