import geopandas as gpd
import pandas as pd
import numpy as np
import os
import shutil
from zipfile import ZipFile
from glob import glob
import subprocess
import csv

# Define Data Paths
data_path = os.getenv('DATA_PATH', '/data')
inputs_path = os.path.join(data_path,'inputs')


# Define Input Paths
boundary_path = os.path.join(inputs_path,'boundary')
vector_path = os.path.join(inputs_path, 'vectors')
parameters_path = os.path.join(inputs_path, 'parameters')

# Define and Create Output Paths
outputs_path = os.path.join(data_path, 'outputs')
outputs_path_ = data_path + '/' + 'outputs'
if not os.path.exists(outputs_path):
    os.mkdir(outputs_path_)
greenareas_path = os.path.join(outputs_path, 'green_areas')
greenareas_path_ = outputs_path + '/' + 'green_areas'
if not os.path.exists(greenareas_path):
    os.mkdir(greenareas_path_)
parameter_outputs_path = os.path.join(outputs_path, 'parameters')
parameter_outputs_path_ = outputs_path + '/' + 'parameters'
if not os.path.exists(parameter_outputs_path):
    os.mkdir(parameter_outputs_path_)

# Look to see if a parameter file has been added
parameter_file = glob(parameters_path + "/*.csv", recursive = True)
print('parameter_file:', parameter_file)

# Identify the EPSG projection code
if len(parameter_file) == 1 :
    parameters = pd.read_csv(parameter_file[0])
    with open(parameter_file[0]) as file_obj:
        reader_obj = csv.reader(file_obj)
        for row in reader_obj:
            try:
                if row[0] == 'PROJECTION':
                    projection = row[1]
            except:
                continue
else:
    projection = os.getenv('PROJECTION')

print('projection:',projection)

# Identify input polygons and shapes (boundary of city, and OS grid cell references)
boundary_1 = glob(boundary_path + "/*.*", recursive = True)
print('Boundary File:',boundary_1)

# Read in the boundary
boundary = gpd.read_file(boundary_1[0])

# Check boundary crs matches the projection
if boundary.crs != projection:
    boundary.to_crs(epsg=projection, inplace=True)

print('boundary_crs:', boundary.crs)

# Identify the name of the boundary file for the city name
file_path = os.path.splitext(boundary_1[0])
print('File_path:',file_path)
filename=file_path[0].split("/")
print('filename:',filename)
location = filename[-1]
print('Location:',location)

# Identify if the buildings are saved in a zip file
green_files_zip = glob(vector_path + "/*.zip", recursive = True)
print(green_files_zip)

# If yes, unzip the file (if the user has formatted the data correctly, this should reveal a .gpkg)
if len(green_files_zip) != 0:
    for i in range (0,len(green_files_zip)):
        print('zip file found')
        with ZipFile(green_files_zip[i],'r') as zip:
            zip.extractall(vector_path)

# Identify geopackages containing the polygons of the buildings
green_files = glob(vector_path + "/*.gpkg", recursive = True)

if len(green_files) != 0:
    # Create a list of all of the gpkgs to be merged
    to_merge=[]
    to_merge=['XX' for n in range(len(green_files))]
    for i in range (0,len(green_files)):
        file_path = os.path.splitext(green_files[i])
        filename=file_path[0].split("/")
        to_merge[i]=filename[4]+'.gpkg'

    print('to_merge:',to_merge)

    # Create a geodatabase and merge the data from each gpkg together
    all_green = []
    all_green=gpd.GeoDataFrame(all_green)
    for cell in to_merge:
        gdf = gpd.read_file('/data/inputs/vectors/%s' %cell)
        all_green = pd.concat([gdf, all_green],ignore_index=True)

    all_green.to_crs(epsg=projection, inplace=True)

    clipped = gpd.clip(all_green,boundary)

    permeable_areas = 'polygons'

    all_greens = clipped.to_file(os.path.join(outputs_path,'all_greenareas.shp'))
    all_greens = gpd.read_file(os.path.join(outputs_path,'all_greenareas.shp'))
    all_greens = all_greens.explode()
    all_greens.reset_index(inplace=True, drop=True)
    all_greens1 = all_greens.to_file(os.path.join(greenareas_path, location + '.gpkg'),driver='GPKG',index=False)
    
    os.remove(os.path.join(outputs_path,'all_greenareas.shp'))
    os.remove(os.path.join(outputs_path,'all_greenareas.cpg'))
    os.remove(os.path.join(outputs_path,'all_greenareas.dbf'))
    os.remove(os.path.join(outputs_path,'all_greenareas.prj'))
    os.remove(os.path.join(outputs_path,'all_greenareas.shx'))
    
else:
    permeable_areas = os.getenv('PERMEABLE_AREAS')

print('permeable_areas:',permeable_areas)

# Print all of the input parameters to an excel sheet to be read in later
with open(os.path.join(parameter_outputs_path,'greenareas-parameters.csv'), 'w') as f:
    f.write('PARAMETER,VALUE\n')
    f.write('PERMEABLE_AREAS,%s\n' %permeable_areas)

# # Move the amended parameter file to the outputs folder
# if len(parameter_file) == 1 :
    
#     file_path = os.path.splitext(parameter_file[0])
#     print('Filepath:',file_path)
#     filename=file_path[0].split("/")
#     print('Filename:',filename[-1])

#     src = parameter_file[0]
#     print('src:',src)
#     dst = os.path.join(parameter_outputs_path,filename[-1] + '.csv')
#     print('dst,dst')
#     shutil.copy(src,dst)

#     # Print all of the input parameters to an excel sheet to be read in later
#     with open(os.path.join(dst), 'a') as f:
#         f.write('PERMEABLE_AREAS,%s\n' %permeable_areas)
