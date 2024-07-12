import geopandas as gpd
import pandas as pd
import os
import shutil
from zipfile import ZipFile
from glob import glob
import subprocess
import zipfile

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
buildings_path = os.path.join(outputs_path, 'buildings')
buildings_path_ = outputs_path + '/' + 'buildings'
if not os.path.exists(buildings_path):
    os.mkdir(buildings_path_)

# Look to see if a parameter file has been added
parameter_file = glob(parameters_path + "/*.csv", recursive = True)
print('parameter_file:', parameter_file)

# Identify the EPSG projection code
if len(parameter_file) == 1 :
    parameters = pd.read_csv(parameter_file[0])
    projection = parameters.loc[1][1]
    print('projection:',projection)
else:
    projection = os.getenv('PROJECTION')

# Identify input polygons and shapes (boundary of city)
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
building_files_zip = glob(vector_path + "/*.zip", recursive = True)
print(building_files_zip)

# If yes, unzip the file (if the user has formatted the data correctly, this should reveal a .gpkg)
if len(building_files_zip) != 0:
    print('zip file found')
    with ZipFile(building_files_zip[0],'r') as zip:
        zip.extractall(vector_path)

# Identify geopackages containing the polygons of the buildings
building_files = glob(vector_path + "/*.gpkg", recursive = True)
#buildings = gpd.read_file(building_files[0])

# Create a list of all of the gpkgs to be merged
to_merge=[]
to_merge=['XX' for n in range(len(building_files))]
for i in range (0,len(building_files)):
    file_path = os.path.splitext(building_files[i])
    filename=file_path[0].split("/")
    to_merge[i]=filename[4]+'.gpkg'

print('to_merge:',to_merge)

# Create a geodatabase and merge the data from each gpkg together
all_builds = []
all_builds=gpd.GeoDataFrame(all_builds)
for cell in to_merge:
    gdf = gpd.read_file('/data/inputs/vectors/%s' %cell)
    all_builds = pd.concat([gdf, all_builds],ignore_index=True)

all_builds.to_crs(epsg=projection, inplace=True)

clipped = gpd.clip(all_builds,boundary)

# Print to a gpkg file
clipped.to_file(os.path.join(buildings_path, location + '.gpkg'),driver='GPKG',index=False)
