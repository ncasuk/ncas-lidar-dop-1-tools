import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from netCDF4 import Dataset
import datetime as dt
import numpy as np
import sys

# matplotlib options, set as None for default values
VMIN=None
VMAX=None
CMAP=None

# where to save plots
OUTPUT_LOC="."


def set_major_minor_date_ticks(ax):
    ax.xaxis.set_minor_locator(mdates.HourLocator(byhour=range(0,24,2)))
    ax.xaxis.set_minor_formatter(mdates.DateFormatter("%H:%M"))
    ax.xaxis.set_major_locator(mdates.DayLocator())
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M\n%Y/%m/%d"))



def plot_wind_speed_and_direction(input_file, output_loc=".", barb_interval=5):
    name_platform_date = "_".join(input_file.split("/")[-1].split("_")[:3])
    nc = Dataset(input_file)

    wsp = nc["wind_speed"][:]
    wdir = nc["wind_from_direction"][:]

    y = nc["altitude"][0,:]

    # sort all arrays by time because ordering is awkward
    idx1 = np.argsort(nc["time"][:])

    x = nc["time"][idx1]
    wsp = wsp[idx1]
    wdir = wdir[idx1]

    u = - (abs(wsp)) * np.sin(np.deg2rad(wdir))
    v = - (abs(wsp)) * np.cos(np.deg2rad(wdir))

    x = [ dt.datetime.fromtimestamp(i, dt.timezone.utc) for i in x ]

    x,y = np.meshgrid(x,y)

    fig = plt.figure(figsize=(20,8))
    fig.set_facecolor("white")
    ax = fig.add_subplot(111)

    pc = ax.pcolormesh(x,y,wsp.T,vmin=VMIN,vmax=VMAX,cmap=CMAP)

    set_major_minor_date_ticks(ax)

    ax.set_ylabel("Altitude (m)")
    ax.set_xlabel("Time")

    ax.set_title(f"ncas-lidar-dop-1 mean winds - {nc['latitude'][0].data:.2f}N, {nc['longitude'][0].data:.2f}E")
    ax.grid(which="both")

    cbar = fig.colorbar(pc, ax=ax)
    cbar.ax.set_ylabel("Wind speed (m s-1)")


    ax.barbs(
        x[::barb_interval,::barb_interval],
        y[::barb_interval,::barb_interval],
        u[::barb_interval,::barb_interval].T,
        v[::barb_interval,::barb_interval].T,
        length=7,
    )
    plt.savefig(f"{output_loc}/{name_platform_date}_wind-speed-and-direction.png")
    #plt.show()
    plt.close()

if __name__ == "__main__":
    infile = sys.argv[1]
    plot_wind_speed_and_direction(infile, output_loc=OUTPUT_LOC)
