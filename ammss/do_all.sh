#!/bin/bash


data_loc=/home/earjham/ammss-plotting/data
python_exe=/home/earjham/miniforge3/envs/jupyter/bin/python
cfradial_loc=.  # MUST point to same location as the OUTLOC constant in convert_to_cfradial.py
date_to_plot=${1:-$(date -u +%Y%m%d)}


mean_winds_data_file=$(ls -v ${data_loc}/ncas-lidar-dop-1_*_${date_to_plot}_mean-winds-profile_v*.nc | tail -1)
${python_exe} plot_mean_winds.py ${mean_winds_data_file}

vertical_file_version=$(ls -v ${data_loc}/ncas-lidar-dop-1_*_${date_to_plot}_aerosol-backscatter-radial-winds_fixed*_standard_v*.nc | tail -1)
array=(${vertical_file_version//_/ })
last_element=${array[-1]}
version=${last_element:: -3}

all_fixed_files_to_plot=$(ls -v ${data_loc}/ncas-lidar-dop-1_*_${date_to_plot}_aerosol-backscatter-radial-winds_fixed*_standard_${version}.nc)
${python_exe} plot_vertical_winds.py ${all_fixed_files_to_plot}


echo $(ls ${data_loc}/ncas-lidar-dop-1_*_${date_to_plot}_aerosol-backscatter-radial-winds_ppi03_standard_${version}.nc) 
# assume same latest version
for n in 3 5 7
do
  ${python_exe} convert_to_cfradial.py $(ls ${data_loc}/ncas-lidar-dop-1_*_${date_to_plot}_aerosol-backscatter-radial-winds_ppi0${n}_standard_${version}.nc)
  ${python_exe} plot_radial_velocity.py  $(ls ${cfradial_loc}/ncas-lidar-dop-1_*_${date_to_plot}_ppi_cfradial_${version}.nc)
done
