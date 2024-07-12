# Green-Areas
This model takes greenspace polygons supplied by the user, clips the data to the domain and ensures the data is in the correct projection.

## Description
The CityCAT model can use greenspace polygons to determine permeability. This model accepts greenspace data in .gpkg format, clips the data to the
    selected area, and ensures all data is in the same projection. If the file sizes are too large, multiple .gpkgs can be added directly, or zipped.

## Input Parameters
*Location
  * Description: The name of the place of interest outlinned by the boundary file.


## Input Files (data slots)
* Vectors
  * Description: Any required vector files (buildings, greenspaces etc.) These should be saved in files of 5km OS grid cells, and zipped at the 100m grid cell level.
  * Location: /data/vectors
* Boundary
  * Description: A .gpkg of the geographical area of interest. 
  * Location: /data/boundary

## Outputs
The model should output only one file - a .gpkg file of the chosen area containing the vectors of interest.
