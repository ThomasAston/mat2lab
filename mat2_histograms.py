# **************************************************************************** #
#                                                                              #
#                                                         :::      ::::::::    #
#    mat2_histograms.py                                 :+:      :+:    :+:    #
#                                                     +:+ +:+         +:+      #
#    By: taston <thomas.aston@ed.ac.uk>             +#+  +:+       +#+         #
#                                                 +#+#+#+#+#+   +#+            #
#    Created: 2023/03/09 12:38:32 by taston            #+#    #+#              #
#    Updated: 2023/03/16 08:37:52 by taston           ###   ########.fr        #
#                                                                              #
# **************************************************************************** #

import os
import fnmatch
import pandas as pd
import csv
import numpy as np
import matplotlib.pyplot as plt
import shutil

# Number of lines for each *.dat file header
HEADER_LENGTH = 15
# Specimen diameter in mm
DIAMETER = 6

def main():
    # Identify .dat files for chosen directory
    identify_files("unsorted data")
    plot_data("sorted data")

    shutil.make_archive('plot images', 'zip', 'plot images')

def identify_files(dir):
    '''
    Identify all .dat files from unsorted folders
    '''
    all_files = []
    dat_files = []
    
    # setup files to be written to later on
    header = ["dataset", "max_force", "ultimate_strength"]
    for root, dirs, files in os.walk("sorted data"):
        for name in files:
            with open(f"sorted data/{name}", "w") as f:
                writer = csv.writer(f)
                writer.writerow(header)
    
    # initialise counts dict
    count = {"steel": 0,
             "aluminium": 0,
             "pla": 0,
             "timber parallel": 0,
             "timber perpendicular": 0,
             "unidentified": 0
            }
    
    # loop over folders looking for .dat files
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
                    # if not fnmatch.fnmatch(name.lower(), '*compress*'):
                    mat_flag = 'timber parallel'
                elif fnmatch.fnmatch(name.lower(), '*perp*'):
                    mat_flag = 'timber perpendicular'
                else:
                    mat_flag = 'unidentified'
                
                # Update counts
                count[mat_flag] += 1

                # extract strength from dataset
                get_strength(root, name, mat_flag, count)

    # Print total number of files that could not be identified
    print(f"Total uncategorised files: {count['unidentified']}")


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
    # calculate specimen cross section area
    specimen_area = np.pi*(DIAMETER**2)/4

    with open(f"sorted data/{mat_flag}.csv", "a") as f:
        writer = csv.writer(f)
        if "timber" not in mat_flag:
            # calculate ultimate strength in MPa
            max_force = dataframe["force"].max() 
            if max_force != 0:
                ultimate_strength = (max_force/specimen_area)*1000
                # write data to csv
                writer.writerow([count[mat_flag], max_force, ultimate_strength])
        elif mat_flag == 'timber parallel' and 'compres' not in name:
            # remove rows where displacement is above threshold then find strength
            threshold = 4 #mm
            dataframe = dataframe[dataframe['distance'] < threshold]
            max_force = dataframe["force"].max() 
            if max_force > 3:
                ultimate_strength = (max_force/specimen_area)*1000
                # write data to csv
                writer.writerow([count[mat_flag], max_force, ultimate_strength])

def plot_data(dir):
    '''
    Plot sorted data
    '''
    steel_data = pd.read_csv('sorted data/steel.csv')["ultimate_strength"]
    aluminium_data = pd.read_csv('sorted data/aluminium.csv')["ultimate_strength"]
    pla_data = pd.read_csv('sorted data/pla.csv')["ultimate_strength"]
    timber_data = pd.read_csv('sorted data/timber parallel.csv')["ultimate_strength"]
    
    bins = np.histogram(np.hstack((steel_data, aluminium_data, pla_data)), bins=150)[1]

    # ----------- HISTOGRAMS (Frequency) -----------
    # Steel figure
    plt.figure('Steel frequency')
    plt.hist(steel_data, bins=10, label='Steel', alpha=0.5, color='c')
    plt.title("Steel")
    plt.xlabel("Ultimate strength (MPa)")
    plt.ylabel("Frequency")
    plt.savefig("plot images/histogramSteel.png")
    # Aluminium figure
    plt.figure('Aluminium frequency')
    plt.hist(aluminium_data, bins=10, label='Aluminium', alpha=0.5, color='gray')
    plt.title("Aluminium")
    plt.xlabel("Ultimate strength (MPa)")
    plt.ylabel("Frequency")
    plt.savefig("plot images/histogramAluminium.png")
    # PLA figure
    plt.figure('PLA frequency')
    plt.hist(pla_data, bins=10, label='PLA', alpha=0.5, color='darkgreen')
    plt.title("PLA")
    plt.xlabel("Ultimate strength (MPa)")
    plt.ylabel("Frequency")
    plt.savefig("plot images/histogramPLA.png")
    # Timber figure
    plt.figure('Timber frequency')
    plt.hist(timber_data, bins=10, label='Timber', alpha=0.5, color='brown')
    plt.title("Timber")
    plt.xlabel("Ultimate strength (MPa)")
    plt.ylabel("Frequency")
    plt.savefig("plot images/histogramTimber.png")
    # ALL figure
    plt.figure('ALL frequency')
    plt.hist(steel_data, bins=bins, label='Steel', alpha=0.5, color='c')
    plt.hist(aluminium_data, bins=bins, label='Aluminium', alpha=0.5, color='gray')
    plt.hist(pla_data, bins=bins, label='PLA', alpha=0.5, color='darkgreen')
    plt.hist(timber_data, bins = bins, label='Timber',alpha=0.5, color='brown')
    plt.xlabel("Ultimate strength (MPa)")
    plt.ylabel("Frequency")
    plt.legend(loc='upper center', ncol=3)
    plt.savefig("plot images/histogramAll.png")
    
    # ----------- HISTOGRAMS (Density) -----------
    # Steel figure
    plt.figure('Steel KDE')
    steel_data.plot(kind="hist", density=True, bins=10, alpha=0.5, color='c', label="Steel")
    steel_data.plot(kind="kde", label="Steel KDE", color='c')
    plt.xlabel("Ultimate strength (MPa)")
    plt.ylabel("Density")
    plt.legend(loc='upper right')
    plt.savefig("plot images/histogramSteelKDE.png")
    # Aluminium figure
    plt.figure('Aluminium KDE')
    aluminium_data.plot(kind="hist", density=True, bins=10, alpha=0.5, color='gray', label="Aluminium")
    aluminium_data.plot(kind="kde", label="Aluminium KDE", color='gray')
    plt.xlabel("Ultimate strength (MPa)")
    plt.ylabel("Density")
    plt.legend(loc='upper right')
    plt.savefig("plot images/histogramAluminiumKDE.png")
    # PLA figure
    plt.figure('PLA KDE')
    pla_data.plot(kind="hist", density=True, bins=10, alpha=0.5, color='darkgreen', label="PLA")
    pla_data.plot(kind="kde", label="PLA KDE", color='darkgreen')
    plt.xlabel("Ultimate strength (MPa)")
    plt.ylabel("Density")
    plt.legend(loc='upper right')
    plt.savefig("plot images/histogramPLAKDE.png")
    # Timber figure
    plt.figure('Timber KDE')
    timber_data.plot(kind="hist", density=True, bins=10, alpha=0.5, color='brown', label="Timber")
    timber_data.plot(kind="kde", label="Timber KDE", color='brown')
    plt.xlabel("Ultimate strength (MPa)")
    plt.ylabel("Frequency")
    plt.savefig("plot images/histogramTimberKDE.png")
    # ALL figure 
    plt.figure('ALL KDE')
    steel_data.plot(kind="hist", density=True, bins=bins, alpha=0.5, color='c', label="Steel")
    steel_data.plot(kind="kde", label="Steel KDE", color='c')
    aluminium_data.plot(kind="hist", density=True, bins=bins, alpha=0.5, color='gray', label="Aluminium")
    aluminium_data.plot(kind="kde", label="Aluminium KDE", color='gray')
    pla_data.plot(kind="hist", density=True, bins=bins, alpha=0.5, color='darkgreen', label="PLA")
    pla_data.plot(kind="kde", label="PLA KDE", color='darkgreen')
    timber_data.plot(kind="hist", density=True, bins=bins, alpha=0.5, color='brown', label="Timber")
    timber_data.plot(kind="kde", label="Timber KDE", color='brown')
    plt.xlabel("Ultimate strength (MPa)")
    plt.ylabel("Density")
    plt.legend(loc='upper right')
    plt.savefig("plot images/histogramAllKDE.png")
    plt.tight_layout()
    plt.show()

    
if __name__ == "__main__":
    main()