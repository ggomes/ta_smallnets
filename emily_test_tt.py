# This scripts just evaluates the travel time for Beats
from __future__ import division
import os
import inspect
from python.Model_Manager.BeATS_Model_Manager import BeATS_Model_Manager_class
from python.Java_Connection import Java_Connection
from python.Solvers.Solver_Class import Solver_class
from python.Data_Types.Demand_Assignment_Class import Demand_Assignment_class
from python.Data_Types.Path_Costs_Class import Path_Costs_class
import numpy as np
import time
import matplotlib.pyplot as plt
plt.rcParams.update({'font.size': 17})

conn = Java_Connection()
sim_dt = 1.
this_folder = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
#demand = [0, 10, 50, 90, 100, 1000]
#demand = [0,5, 8,10, 12,15,20]
demand = [10]
for d in demand:
    #configfile = os.path.join(this_folder, os.path.pardir, 'configfiles/cfg', 'cfg_vi_ctm_' +str(d) +'.xml')
    configfile = os.path.join(this_folder, os.path.pardir, 'configfiles/cfg/Total20', 'cfg_vi_static_' + str(d) + '.xml')
    #configfile = os.path.join(this_folder, os.path.pardir, 'configfiles/cfg/Total20', 'cfg_vi_pq_' + str(d) + '.xml')
    model_manager = BeATS_Model_Manager_class(configfile, conn.gateway, sim_dt)

    T = 3600  # Time horizon of interest
    sampling_dt = 60  # Duration of one time_step for the solver

    if(model_manager.is_valid()):
        path_list = dict()
        sub = model_manager.beats_api.get_subnetworks()
        print sub[1].get_link_ids()
        od = model_manager.beats_api.get_od_info()
        num_steps = int(T / sampling_dt)

        # Initializing the demand assignment
        #get subnetworks from API for paths

        commodity_list = list(model_manager.beats_api.get_commodity_ids())
        assignment = Demand_Assignment_class(path_list,commodity_list,
                                             num_steps, sampling_dt)

        # Populating the Demand Assignment, based on the paths associated with ODs
        for o in od:
            count = 0
            comm_id = o.get_commodity_id()

            #if demand_size > num_steps or num_steps % len(demand_api) != 0:
                #print "Demand specified in xml cannot not be properly divided among time steps"
                #return

            for path in o.get_subnetworks():
                path_list[path.getId()] = path.get_link_ids()

                demand_api = [item * 3600 for item in
                              model_manager.beats_api.get_demand_with_ids("pathfull", path.getId(), comm_id).getProfile().getValues()]
                demand_api = np.asarray(demand_api)
                demand_size = len(demand_api)
                demand_dt = o.get_total_demand_vps().getDt()

                # Before assigning the demand, we want to make sure it can be properly distributed given the number of
                # Time step in our problem
                if (sampling_dt > demand_dt or demand_dt % sampling_dt > 0) and (demand_size > 1):
                    print "Demand specified in xml cannot not be properly divided among time steps"

                #Creates an array of demands from the xml demand profile to be assignmed into the demand assignment
                ass_demand = np.zeros(num_steps)
                for i in range(num_steps):
                    #index = int(i / (num_steps/demand_size))
                    index = int(i*sampling_dt/demand_dt)
                    if index > demand_size-1:
                        index = demand_size-1
                    ass_demand[i] = demand_api[index]

                assignment.set_all_demands_on_path_comm(path.getId(),comm_id, ass_demand)

        num_paths = len(path_list.keys())
        num_runs = 1
        Avg_Travel_Times = np.zeros((num_runs, num_paths*num_steps))
        #print  assignment.get_all_demands_on_path(1)
        path_2_demand = list(assignment.get_all_demands_on_path(2))
        path_3_demand = list(assignment.get_all_demands_on_path(3))

        num_exp = 1
        Travel_times = np.zeros((num_exp, num_paths*num_steps))
        for i in range(0,num_exp):
            path_costs = model_manager.evaluate(assignment,T, initial_state = None)
            #outfile = 'ctm/ctm_' +str(d) +'.txt'
            #outfile = 'pq/pq_' + str(d) + '.txt'
            outfile = 'static/static_' + str(d) + '.txt'
            path_costs.write_path_info(outfile)
            path_costs.print_all()


        conn.close()