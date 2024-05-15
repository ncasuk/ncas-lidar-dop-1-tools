import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from netCDF4 import Dataset
import datetime as dt
import numpy as np
import sys

## Colour bar options, set to None for matplotlib default
VMIN = -4
VMAX = 4
CMAP = "RdBu_r"


def set_major_minor_date_ticks(ax):
    ax.xaxis.set_minor_locator(mdates.HourLocator(byhour=range(0,24,2)))
    ax.xaxis.set_minor_formatter(mdates.DateFormatter("%H:%M"))
    ax.xaxis.set_major_locator(mdates.DayLocator())
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M\n%Y/%m/%d"))



def plot_vertical_winds(input_files, output_loc=".", only_good_data=False):
    name_platform_date = "_".join(input_files[0].split("/")[-1].split("_")[:3])
    nc = Dataset(input_files[0])
    times = np.empty((0))
    ranges = np.empty((0, nc.dimensions['index_of_range'].size))
    radial_velocity = np.empty((0,nc.dimensions['index_of_range'].size))
    qc_flag = np.empty((0,nc.dimensions['index_of_range'].size))
    nc.close()

    for input_file in input_files:
        nc = Dataset(input_file)
        if np.all(nc["sensor_view_angle_instrument_frame"][:] == 90):
            times = np.concatenate((times, nc['time'][:]), axis=0)
            ranges = np.concatenate((ranges, nc['range'][:,:,0]), axis=0)
            radial_velocity = np.concatenate((radial_velocity, nc['radial_velocity_of_scatterers_away_from_instrument'][:,:,0]), axis=0)
            qc_flag = np.concatenate((qc_flag, nc['qc_flag_radial_velocity_of_scatterers_away_from_instrument'][:,:,0]), axis=0)


    # sort all arrays by time because ordering is awkward
    idx1 = np.argsort(times[:])

    x = times[idx1]
    x = [ dt.datetime.fromtimestamp(i, dt.timezone.utc) for i in x ]

    y = ranges[idx1]
    radial_velocity = radial_velocity[idx1,:]
    qc_flag = qc_flag[idx1,:]

    if only_good_data:
        radial_velocity = np.ma.masked_where(qc_flag[:] > 1, radial_velocity[:])

    x,y = np.meshgrid(x,y[0,:])

    fig = plt.figure(figsize=(20,8))
    fig.set_facecolor("white")
    ax = fig.add_subplot(111)

    pc = ax.pcolormesh(x,y,radial_velocity.T, vmin=VMIN, vmax=VMAX, cmap=CMAP)

    set_major_minor_date_ticks(ax)

    ax.set_ylabel("Range")
    ax.set_xlabel("Time")

    ax.set_title(f"ncas-lidar-dop-1 upward velocity - {nc['latitude'][0].data:.2f}N, {nc['longitude'][0].data:.2f}E")
    ax.grid(which="both")

    cbar = fig.colorbar(pc, ax=ax)
    cbar.ax.set_ylabel("Wind speed (m s-1)")


    plt.savefig(f"{output_loc}/{name_platform_date}_vertical-wind.png")
    #plt.show()
    plt.close()

if __name__ == "__main__":
    infiles = sys.argv[1:]
    plot_vertical_winds(infiles)
