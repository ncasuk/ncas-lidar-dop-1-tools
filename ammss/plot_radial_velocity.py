import pyart
import matplotlib.pyplot as plt
import sys

VMIN = None
VMAX = None
CMAP = None


def main(infile, outloc="./plots", variable="radial_velocity_of_scatterers_away_from_instrument"):
    name_platform_date = "_".join(infile.split("/")[-1].split("_")[:3])

    lidar = pyart.io.read(infile)

    display = pyart.graph.RadarDisplay(lidar)

    for sweep in range(lidar.nsweeps):
        fig = plt.figure()
        ax = fig.add_subplot(111)
        display.plot(variable, sweep, vmin=VMIN, vmax=VMAX, cmap=CMAP)
        plt.savefig(f"{outloc}/{name_platform_date}_sweep{sweep}.png")
        plt.close()

if __name__ == "__main__":
    infile = sys.argv[1]
    main(infile)
