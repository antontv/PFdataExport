import pickle
import time
import os
import sys
import re
import csv
import json
from os import path, listdir, mkdir
import numpy as np
import pandas as pd

sys.path.append(r'C:\Program Files\DIgSILENT\PowerFactory 2021 SP5\Python\3.9')
from PowDict import Kundur_elements, csv_to_PFformat, Kundur, files

#import powerfactory as pf

##########################################################################
#https://stackoverflow.com/questions/46954510/random-walk-series-between-start-end-values-and-within-minimum-maximum-limits
def bounded_random_walk(length, lower_bound,  upper_bound, start, end, std):
    assert (lower_bound <= start and lower_bound <= end)
    assert (start <= upper_bound and end <= upper_bound)

    bounds = upper_bound - lower_bound

    rand = (std * (np.random.random(length) - 0.5)).cumsum()
    rand_trend = np.linspace(rand[0], rand[-1], length)
    rand_deltas = (rand - rand_trend)
    rand_deltas /= np.max([1, (rand_deltas.max()-rand_deltas.min())/bounds])

    trend_line = np.linspace(start, end, length)
    upper_bound_delta = upper_bound - trend_line
    lower_bound_delta = lower_bound - trend_line

    upper_slips_mask = (rand_deltas-upper_bound_delta) >= 0
    upper_deltas =  rand_deltas - upper_bound_delta
    rand_deltas[upper_slips_mask] = (upper_bound_delta - upper_deltas)[upper_slips_mask]

    lower_slips_mask = (lower_bound_delta-rand_deltas) >= 0
    lower_deltas =  lower_bound_delta - rand_deltas
    rand_deltas[lower_slips_mask] = (lower_bound_delta + lower_deltas)[lower_slips_mask]

    return trend_line + rand_deltas


def bounded_random_load(length, effect, boundary):
    rand = (np.random.random(length) - 0.5).cumsum()
    rand = rand/(rand.max()-rand.min())*boundary
    return effect + rand


def vary_loads(app, study_case, oInit, oRms, v_l):
    #showdiaextdata
    loads = app.GetCalcRelevantObjects("ElmLod")

    path_l = r"C:\Users\anton\OneDrive - KTH\KTH PhD\Research work\Dynamic State estimation\Dataprocessing\n44_loads"
    
    load_files = listdir(path_l)
    #make something here regarding creating the files
    if len(load_files) == 0:
        for load in loads:
            name = path_l + "\ ".split(" ")[0] + load.loc_name + ".txt"
            file = open(name, 'w')
            file.close()
    
    #Set timesteps
    step_size = round(oInit.dtgrd,4)
    tstop = oRms.tstop
    time_steps = np.arange(0,tstop,step_size)

    for load in loads: 
        #Static active and reactive power
        P_static = load.plini
        Q_static = load.qlini
        
        #Active and reactive power random steps
        if v_l == "Y" or v_l == "y":
            if 'factor' not in locals():
                factor = float(input('Give factor for varying loads: '))
            P = bounded_random_load(len(time_steps), effect = P_static, boundary =P_static*factor)
            Q = bounded_random_load(len(time_steps), effect = Q_static, boundary =Q_static*factor)
        else:
            P = np.ones((len(time_steps),1))*P_static
            Q = np.ones((len(time_steps),1))*Q_static
        
        file_n = path_l + "\ ".split(" ")[0] + load.loc_name + ".txt"
        file = open(file_n, 'w')
        file.write('2\n\n')
        file.close()
        file = open(file_n, 'a')
        data = np.column_stack([time_steps, P, Q])
        np.savetxt(file, data, fmt=['%f','%f','%f'])
        file.close()
        
    return


def load_csv_data(file_path, csv_to_PFformat, elements):

    csv_file = open(file_path)
    objects = next(csv_file).split(',') #Read in all objects
    i = 0
    for obj in objects:
        objects[i] = obj.split("\n")[0]
        i += 1
    parameter = next(csv_file).split('"') #Read in all measurment objects registered in PF
    parameter = [x for x in parameter if len(x)>=3]
    row_count = sum(1 for row in csv_file) # Counter number of measurement points
    csv_file.close(); csv_file = open(file_path)
    
    next(csv_file)
    next(csv_file)
    data = [None]*row_count
    i = 0 #Read in data to massive list
    for row in csv_file:
        data[i] = row.split(',')
        i += 1
    
    csv_file.close()
    data = np.array(data,dtype = float) #Turn massive list into numpy array
    
    #Sort out which data to use and structure it into a list of components equal to what's specified in PowDict and in that order
    
    data_mes = []
    for i in range(len(elements)):
        data_mes.append({})
    
    time = data[:,0]; data = data[:,1:]
    objects = objects[1:]; parameter = parameter[1:]
    
    reg_objects = []
    
    for i in range(data.shape[1]):
        
        try:
            csv_to_PFformat[parameter[i]] # Check if valid parameters based on desired parameters.
            if parameter:
                #create new object, reset j to set column to zero
                if objects[i] not in reg_objects:
                    reg_objects.append(objects[i])
                    pf_object = {}
                    pf_object[objects[i].split(" ")[0][1:]] = np.zeros((row_count,len(elements[objects[i][0]])),dtype = float)
                    j = 0
                    k = list(elements.keys()).index(objects[i][0])
                    data_mes[k].update(pf_object)
                    
                
                #Put data into the newly created object, increment J for each column
                pf_object[objects[i].split(" ")[0][1:]][:,j] = data[:,i]
                j += 1
        except KeyError:
            print("Unused parameter: {} at {}".format(objects[i],parameter[i]))
        

    return time, data_mes


    
def csv_data(app, directory_name, directory_path):
    #Functions runs the powerfactory simulation and saves the data into csv file at specified directory
    
    elmRes = app.GetFromStudyCase('*.ElmRes')
    comRes = app.GetFromStudyCase("ComRes")
    
    if not os.path.isdir(directory_path):
        mkdir(directory_path)

    file_name = r"\result.csv"
    comRes.f_name = directory_path + file_name #File Name
    

    comRes.iopt_exp = 6# to export as csv
    comRes.iopt_sep = 0 # to use the system seperator
    comRes.iopt_csel = 0 #Make sure to save all variables
    comRes.Execute()

    return directory_path + file_name

def event_data(app, oEvt, directory_name, load = 0):
    
    directory_path = r"C:\Users\anton\OneDrive - KTH\KTH PhD\Research work\Dynamic State estimation\Dataprocessing\PFsavedFiles\{}".format(directory_name)
    file_name = directory_path + r'\event.csv'
    if load == 0:
        events = oEvt.GetContents()
        
        dictionary = {}
        for event in events:
            if event.outserv == 0:
                time = event.time
                type_event = event.loc_name[:2]
                element = event.loc_name[2:]
                dictionary[type_event] = [time,element]
                
        file_name = directory_path + r'\event.csv'
        
        # open file for writing, "w" is writing
        with open(file_name, 'w') as f:
            f.write(json.dumps(dictionary))

    else:
        with open(file_name) as f:
            dictionary = json.loads(f.read())
    
    return dictionary

def retrieveData(choice, projName, study_case, elements, csv_to_PFformat):
    #Choice: Choose whether to retreive old saved data, or generate new from powefactory. Y == fetch old, N == create new
    #projName: Name of powerfactory project
    #study_case: Study case name in the project
    #elements: Which parameters you are interested in
    #csv_to_PFformat: Conversion dictionary between 

    directory_path = os.getcwd() + r'\PFsavedFiles'
    if choice == "Y" or choice == "y":
        x = [x[0] for x in os.walk(directory_path)]
        z = [y.split("\\")[-1] for y in x][1:]
        print("Directories:")
        for name in z:
            print(name)
            
        directory_name = input("Name of Directory to retrieve: ")
        start = time.perf_counter()
        file_path = directory_path + r"\{}\result.csv".format(directory_name)    
        
        event_dict = event_data(None, None, directory_name, load = 1)
        
        mes_time, data = load_csv_data(file_path, csv_to_PFformat, elements)
        stop = time.perf_counter()
        print("Total runtime: {}".format(stop-start))
    elif choice == "N" or choice == "n":
        
        sim_len = int(input("length of simulation? (s): "))
        directory_name = input("Name of Directory for saving: ")
        start = time.perf_counter()
        #run RMS-simulation
        app = pf.GetApplication()
        if app is None:
            raise Exception('Getting PowerFactory application failed')

        #activate project
        project = app.ActivateProject(projName)
        proj = app.GetActiveProject()


        #get the study case folder and activate project
        oFolder_studycase = app.GetProjectFolder('study') #IntPrj SetPrj
        oCase = oFolder_studycase.GetContents(study_case)[0]
        oCase.Activate()

        oInit = app.GetFromStudyCase('ComInc')  #get initial condition calculation object
        oRms = app.GetFromStudyCase('ComSim') #get RMS-simulation object
        oEvt = app.GetFromStudyCase('IntEvt') #Get event object

        

        oRms.tstop = sim_len
        oInit.dtgrd = 0.01
        
        #This is a short function meant to simulate "real frequency" behaviour, by creating random-walking loads in powerfactory. However, the load can be constant.
        while True:
            print("Do you want varying loads (y/n)?")
            v_l = input()
            if v_l == "y" or v_l == "Y" or v_l == "n" or v_l == "N":
                break
        vary_loads(app, oCase, oInit, oRms, v_l)

        # calculate initial conditions
        oInit.Execute()
        
        oRms.Execute()
        file_path = csv_data(app, directory_name, directory_path)
        
        event_dict = event_data(app, oEvt, directory_name)
        
        mes_time, data = load_csv_data(file_path, csv_to_PFformat, elements)
        end = time.perf_counter()
        print("Time: {}".format(end-start))
    return mes_time, data, directory_name, event_dict
    
if __name__ == "__main__":
    mes_time, data, directory_name, event_dict = retrieveData(choice = "n", projName = 'Kundur_Base_simp', study_case = 'StudyCase.IntCase', elements = Kundur_elements, csv_to_PFformat = csv_to_PFformat)