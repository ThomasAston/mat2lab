# **************************************************************************** #
#                                                                              #
#                                                         :::      ::::::::    #
#    mat2_histograms.py                                 :+:      :+:    :+:    #
#                                                     +:+ +:+         +:+      #
#    By: taston <thomas.aston@ed.ac.uk>             +#+  +:+       +#+         #
#                                                 +#+#+#+#+#+   +#+            #
#    Created: 2023/03/09 12:38:32 by taston            #+#    #+#              #
#    Updated: 2023/03/09 15:14:10 by taston           ###   ########.fr        #
#                                                                              #
# **************************************************************************** #

import os
import fnmatch
import pandas as pd
import csv
import matplotlib.pyplot as plt

# Number of lines for each *.dat file header
HEADER_LENGTH = 15

def main():
    # Identify .dat files for chosen directory
    identify_files("unsorted data")
    plot_data("sorted data")

def identify_files(dir):
    '''
    Identify all .dat files from unsorted folders
    '''
    all_files = []
    dat_files = []
    
    # setup files to be written to later on
    header = ["dataset", "max_force"]
    with open("sorted data/steel_max_force.csv", "w") as f:
        writer = csv.writer(f)
        writer.writerow(header)
    with open("sorted data/aluminium_max_force.csv", "w") as f:
        writer = csv.writer(f)
        writer.writerow(header)
    with open("sorted data/pla_max_force.csv", "w") as f:
        writer = csv.writer(f)
        writer.writerow(header)
    with open("sorted data/timberPar_max_force.csv", "w") as f:
        writer = csv.writer(f)
        writer.writerow(header)
    with open("sorted data/timberPerp_max_force.csv", "w") as f:
        writer = csv.writer(f)
        writer.writerow(header)
    
    
    count = {"steel": 0,
             "aluminium": 0,
             "pla": 0,
             "timber parallel": 0,
             "timber perpendicular": 0,
             "unidentified": 0
            }
    
    # loop over folders
    for root, dirs, files in os.walk(dir):
        for name in files:
            all_files.append(os.path.join(root, name))
            
            # if .dat file
            if fnmatch.fnmatch(name, '*.dat'):
                dat_files.append(os.path.join(root, name))
                
                # identify material
                if fnmatch.fnmatch(name.lower(), '*steel*'):
                    mat_flag = 'steel'
                elif fnmatch.fnmatch(name.lower(), '*aluminium*') or fnmatch.fnmatch(name.lower(), '*aluminum*'):
                    mat_flag = 'aluminium'
                elif fnmatch.fnmatch(name.lower(), '*pla*'):
                    mat_flag = 'pla'
                elif fnmatch.fnmatch(name.lower(), '*par*'):
                    mat_flag = 'timber parallel'
                elif fnmatch.fnmatch(name.lower(), '*perp*'):
                    mat_flag = 'timber perpendicular'
                else:
                    mat_flag = 'unidentified'
                
                count[mat_flag] += 1

                # extract strength from dataset
                get_strength(root, name, mat_flag, count)


def get_strength(root, name, mat_flag, count):
    '''
    Extract strength value for a given dataset
    '''
    # read .dat to a list of lists
    dat_content = []
    for line in open(f'{root}/{name}', 'r', errors='ignore').readlines()[HEADER_LENGTH:-3]:
        dat_content.append(line.strip().split())
    
    # write it as a new CSV file
    with open("sorted data/current_data.csv", "w") as f:
        writer = csv.writer(f)
        writer.writerow(["distance", "force", "elongation", "stress"])
        writer.writerows(dat_content)

    # read into pandas dataframe
    dataframe = pd.read_csv("sorted data/current_data.csv")   
    
    # extract maximum force depending on material type
    if mat_flag == "steel":
        max_force = dataframe["force"].max() 
        with open("sorted data/steel_max_force.csv", "a") as f:
            writer = csv.writer(f)
            if max_force != 0:
                writer.writerow([count[mat_flag], max_force])
    elif mat_flag == "aluminium":
        max_force = dataframe["force"].max() 
        with open("sorted data/aluminium_max_force.csv", "a") as f:
            writer = csv.writer(f)
            if max_force != 0:
                writer.writerow([count[mat_flag], max_force])
    elif mat_flag == "pla":
        max_force = dataframe["force"].max() 
        with open("sorted data/pla_max_force.csv", "a") as f:
            writer = csv.writer(f)
            if max_force != 0:
                writer.writerow([count[mat_flag], max_force])
    elif mat_flag == "timber parallel":
        max_force = dataframe["force"].max() 
        with open("sorted data/timberPar_max_force.csv", "a") as f:
            writer = csv.writer(f)
            if max_force != 0 and isinstance(max_force, float):
                writer.writerow([count[mat_flag], max_force])
    elif mat_flag == "timber perpendicular":
        max_force = dataframe["force"].max() 
        with open("sorted data/timberPerp_max_force.csv", "a") as f:
            writer = csv.writer(f)
            if max_force != 0 and isinstance(max_force, float):
                writer.writerow([count[mat_flag], max_force])
            
    
    # TODO: calculate ultimate strength from specimen area 
    # specimen_area = 
    # ultimate_strength = max_force/specimen_area


def plot_data(dir):
    steel_data = pd.read_csv('sorted data/steel_max_force.csv')["max_force"]
    aluminium_data = pd.read_csv('sorted data/aluminium_max_force.csv')["max_force"]
    pla_data = pd.read_csv('sorted data/pla_max_force.csv')["max_force"]
    timberPar_data = pd.read_csv('sorted data/timberPar_max_force.csv')["max_force"]
    timberPerp_data = pd.read_csv('sorted data/timberPerp_max_force.csv')["max_force"]
    
    plt.hist(steel_data, bins=10, label='Steel', alpha=0.5)
    plt.hist(aluminium_data, bins=10, label='Aluminium', alpha=0.5)
    plt.hist(pla_data, bins=10, label='PLA', alpha=0.5)
    plt.xlabel("Maximum force (kN)")
    plt.ylabel("Frequency")
    # plt.hist(timberPar_data, bins=10, label='Timber (parallel)', alpha=0.5)
    # plt.hist(timberPerp_data, bins=10, label='Timber (perpendicular)', alpha=0.5)
    
    plt.legend(loc='upper center', ncol=3)
    plt.tight_layout()
    plt.savefig("plot images/histogramAll.png")
    plt.show()

    
if __name__ == "__main__":
    main()