# This scripts initializes a Model_Manager object a Traffic_Model and Cost_Function object
# It uses as input a Demand_Assignment objects (demand per path and per time) to generate costs per path as
# a Path_Costs object
# This particular model uses a Static model and BPR Cost_Function model

import numpy as np

from Model_Manager.Link_Model_Manager import Link_Model_Manager_class
from Model_Manager.BeATS_Model_Manager import BeATS_Model_Manager_class
from Java_Connection import Java_Connection
from Data_Types.Demand_Assignment_Class import Demand_Assignment_class
from Traffic_Models.Static_Model import Static_Model_Class
import collections
from copy import copy
import matplotlib.pyplot as plt
import os
import inspect
import csv
from Solvers.Path_Based_Frank_Wolfe_Solver import Path_Based_Frank_Wolfe_Solver

plt.rcParams.update({'font.size': 18})

connection = Java_Connection()
demand_range = [0, 2, 4, 6, 8, 10, 12, 14, 15, 16, 18, 20]
bpr_param = [0., 0.3, 0.4, 0.6, 0.8, 1.]
for b in bpr_param:
    for d in demand_range:
        if connection.pid is not None:
            this_folder = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
            configfile = this_folder +'\\configfiles\\cfg\\Total20\\cfg_vi_static_10.xml'
            coefficients = {}
            T = 90  # Time horizon of interest
            sim_dt = 90.0  # Duration of one time_step for the traffic model

            sampling_dt = 90  # Duration of time_step for the solver, in this case it is equal to sim_dt
            model_manager = Link_Model_Manager_class(configfile, connection.gateway, "static", sim_dt, "bpr", coefficients)
            model_manager.beats_api.set_stochastic_process('deterministic')
            #Estimating bpr coefficients with beats
            num_links = model_manager.beats_api.get_num_links()
            avg_travel_time = np.zeros(num_links)

            num_coeff = 5

            for i in range(num_links):
                fft= (model_manager.beats_api.get_link_with_id(long(i)).getFull_length() \
                  / model_manager.beats_api.get_link_with_id(long(i)).get_ffspeed_mps())
                coefficients[long(i)] = np.zeros(num_coeff)
                coefficients[i][0] = copy(fft)
                coefficients[i][4] = copy(fft*b)
            route = {}
            route['1'] = [0, 3, 4, 5]
            route['2'] = [0, 2, 4, 5]
            route['3'] = [1, 3, 4, 5]
            demand = {}
            demand[('1','1')] = [10]
            demand[('2','1')] = [10]
            demand[('3','1')] = [10]
            path_ids = ['1', '2', '3']
            comm_ids = [1, 1, 1]
            demands_1 = [d]
            demands_2 =[20-d]
            demands_3 = [20]
            od = list(model_manager.beats_api.get_od_info())
            num_steps = int(T / sampling_dt)
            # Initializing the demand assignment
            commodity_list = list(model_manager.beats_api.get_commodity_ids())
            assignment = Demand_Assignment_class(route, commodity_list, num_steps, sampling_dt)
            sortedD = collections.OrderedDict(sorted(demand.items(), key=lambda t: t[0]))
            #assignment.set_all_demands(sortedD)
            assignment.set_all_demands_on_path_comm(path_ids[0], comm_ids[0], demands_1)
            assignment.set_all_demands_on_path_comm(path_ids[1], comm_ids[1], demands_2)
            assignment.set_all_demands_on_path_comm(path_ids[2], comm_ids[2], demands_3)
            #print assignment.get_path_list().keys()
            #print assignment.get_commodity_list()

            model = Static_Model_Class(model_manager.beats_api)
            path_costs = model_manager.evaluate(assignment,T, initial_state = None)
            #outfile = 'ctm/ctm_' +str(d) +'.txt'
            #outfile = 'pq/pq_' + str(d) + '.txt'
            #path_costs.print_all()
            outfile = 'static/static_' +str(d) +'_' +str(b) +'.txt'
            path_costs.write_path_info(outfile)

            connection.close()