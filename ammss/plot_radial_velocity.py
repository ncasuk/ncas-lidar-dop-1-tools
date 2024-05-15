import pyart
import matplotlib.pyplot as plt
import sys
from netCDF4 import num2date

# options for matplotlib, set as None for default options
VMIN = None
VMAX = None
CMAP = None

# location to save plots
PLOTS_LOC = "./plots"

# variable to plot
PLOT_VARIABLE = "radial_velocity_of_scatterers_away_from_instrument"


def get_sweep_time(lidar, sweep):
    first_ray=lidar.sweep_start_ray_index["data"][sweep]
    time = lidar.time["data"][first_ray]
    units = lidar.time["units"]
    sweep_datetime = num2date(time, units, only_use_cftime_datetimes=False, only_use_python_datetimes=True)
    sweep_time_str = sweep_datetime.strftime("%Y%m%dT%H%M%S")
    return sweep_time_str


def main(infile, outloc="./plots", variable="radial_velocity_of_scatterers_away_from_instrument"):
    name_platform = "_".join(infile.split("/")[-1].split("_")[:2])

    lidar = pyart.io.read(infile)
    display = pyart.graph.RadarDisplay(lidar)

    for sweep in range(lidar.nsweeps):
        sweep_time_str = get_sweep_time(lidar, sweep)
        fig = plt.figure()
        ax = fig.add_subplot(111)
        display.plot(variable, sweep, vmin=VMIN, vmax=VMAX, cmap=CMAP)
        plt.savefig(f"{outloc}/{name_platform}_{sweep_time_str}_{variable}_{lidar.fixed_angle['data'][sweep]}deg.png")
        plt.close()

if __name__ == "__main__":
    infile = sys.argv[1]
    main(infile, outloc=PLOTS_LOC, variable=PLOT_VARIABLE)
