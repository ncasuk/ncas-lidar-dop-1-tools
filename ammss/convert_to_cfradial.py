from netCDF4 import Dataset
import sys
import numpy as np


OUTLOC = "."
STRING_LENGTH_SIZE = 22


def get_dimension_sizes(infiles):
    time_size = 0
    sweep_size = 0
    for i,infile in enumerate(infiles):
        nci = Dataset(infile)
        if i == 0:
            range_size = nci.dimensions["index_of_range"].size
        time_size += (nci.dimensions["time"].size * nci.dimensions["index_of_angle"].size)
        sweep_size += nci.dimensions["time"].size
        nci.close()
    return time_size, range_size, sweep_size


def get_all_times(infiles):
    times = []
    for infile in infiles:
        nci = Dataset(infile)
        file_times = nci["time"][:]
        angles = nci.dimensions["index_of_angle"].size
        for t in file_times:
            times.extend([t] * angles)
        nci.close()
    return times


def get_and_convert_radial_velocity(infiles):
    #radial_velocity = np.empty((0,2))
    for i,infile in enumerate(infiles):
        nci = Dataset(infile)
        threeDvel = nci["radial_velocity_of_scatterers_away_from_instrument"][:]
        time_dim = nci.dimensions["time"].size
        range_dim = nci.dimensions["index_of_range"].size
        angle_dim = nci.dimensions["index_of_angle"].size
        twoDvel = threeDvel.transpose(0, 2, 1).reshape(time_dim*angle_dim, range_dim)
        if i == 0:
            radial_velocity = twoDvel
        else:
            radial_velocity = np.concatenate((radial_velocity, twoDvel))
    return radial_velocity


def get_all_angles(infiles, angle="azimuth", frame="instrument"):
    if angle == "azimuth":
        variable = f"sensor_azimuth_angle_{frame}_frame"
    elif angle == "elevation":
        variable = f"sensor_view_angle_{frame}_frame"
    else:
        msg = f"Invalid angle {angle} - must be one of 'azimuth' or 'elevation'"
        raise ValueError(msg)

    for i, infile in enumerate(infiles):
        nci = Dataset(infile)
        time_dim = nci.dimensions["time"].size
        angle_dim = nci.dimensions["index_of_angle"].size
        oneDele = nci[variable][:].reshape(time_dim*angle_dim)
        if i == 0:
            angles = oneDele
        else:
            angles = np.concatenate((angles, oneDele))
    return angles


def get_variables(infiles):
    times = get_all_times(infiles)
    radial_velocity = get_and_convert_radial_velocity(infiles)
    elevations = get_all_angles(infiles, angle="elevation")
    azimuths = get_all_angles(infiles, angle="azimuth")

    nci = Dataset(infiles[0])
    ranges = nci["range"][0,:,0]
    latitude = nci["latitude"][0]
    longitude = nci["longitude"][0]
    altitude = nci.getncattr("platform_altitude")[:-1].strip()

    nci.close()
    return times, radial_velocity, ranges, latitude, longitude, altitude, elevations, azimuths


def add_variables_to_netcdf(nc, infiles, file_type):
    if file_type not in ["rhi","ppi"]:
        msg = "Invalid file type - must be one of 'ppi' or 'rhi'"
        raise ValueError(msg)

    times, radial_velocity, ranges, latitude, longitude, altitude, elevations, azimuths = get_variables(infiles)

    nc.createVariable("time", "f8", ("time",))
    nc.createVariable("range", "f4", ("range",))
    nc.createVariable("latitude", "f8")
    nc.createVariable("longitude", "f8")
    nc.createVariable("altitude", "f8")
    nc.createVariable("radial_velocity_of_scatterers_away_from_instrument", "f4", ("time", "range",))
    nc.createVariable("elevation", "f4", ("time",))
    nc.createVariable("azimuth", "f4", ("time",))
    nc.createVariable("sweep_mode", "c", ("sweep", "string_length",))
    #nc.createVariable("sweep_number", "i", ("sweep",))
    nc.createVariable("fixed_angle", "f4", ("sweep",))
    nc.createVariable("sweep_start_ray_index", "i", ("sweep",))
    nc.createVariable("sweep_end_ray_index", "i", ("sweep",))
    

    nc["time"][:] = times
    nc["time"].units = "seconds since 1970-01-01T00:00:00Z"
    nc["time"].standard_name = "time"
    nc["time"].long_name = "UNIX timestamp"

    nc["range"][:] = ranges
    nc["range"].units = "metres"
    nc["range"].standard_name = "projection_range_coordinate"
    nc["range"].long_name = "range_to_measurement_volume"

    nc["latitude"][:] = latitude
    nc["longitude"][:] = longitude
    nc["altitude"][:] = altitude

    nc["radial_velocity_of_scatterers_away_from_instrument"][:] = radial_velocity
    nc["radial_velocity_of_scatterers_away_from_instrument"].units = "m s-1"

    nc["azimuth"][:] = azimuths
    nc["elevation"][:] = elevations

    for s in range(nc["sweep_mode"].shape[0]):
        if file_type == "ppi":
            nc["sweep_mode"][s,:20] = list("azimuth_surveillance")
        elif file_type == "rhi":
            nc["sweep_mode"][s,:] = list("elevation_surveillance")

    if file_type == "ppi":        
        nc["fixed_angle"][:] = elevations[::int(nc.dimensions["time"].size/nc.dimensions["sweep"].size)]
    elif file_type == "rhi":
        nc["fixed_angle"][:] = azimuths[::int(nc.dimensions["time"].size/nc.dimensions["sweep"].size)]

    nc["sweep_start_ray_index"][:] = list(range(0,nc.dimensions["time"].size,int(nc.dimensions["time"].size/nc.dimensions["sweep"].size)))
    nc["sweep_end_ray_index"][:-1] = [ i-1 for i in nc["sweep_start_ray_index"][1:] ]
    nc["sweep_end_ray_index"][-1] = nc.dimensions["time"].size - 1



def init_netcdf(outfile, time_size=None, range_size=None, sweep_size=None, string_length_size=None):
    nco = Dataset(outfile, 'w')
    nco.createDimension("time", time_size)
    nco.createDimension("range", range_size)
    nco.createDimension("sweep", sweep_size)
    nco.createDimension("string_length", string_length_size)
    return nco



def main(infiles, outloc=".", file_type="ppi"):
    if file_type not in ["rhi","ppi"]:
        msg = "Invalid file type - must be one of 'ppi' or 'rhi'"
        raise ValueError(msg)
    name_platform_date = "_".join(infiles[0].split("/")[-1].split("_")[:3])
    version = ".".join(infiles[0].split("_")[-1].split(".")[:-1])
    outname = f"{name_platform_date}_{file_type}_cfradial_{version}.nc"
    time_size, range_size, sweep_size = get_dimension_sizes(infiles)
    nc = init_netcdf(f"{outloc}/{outname}", time_size=time_size, range_size=range_size, sweep_size=sweep_size, string_length_size=STRING_LENGTH_SIZE)
    add_variables_to_netcdf(nc, infiles, file_type=file_type)
    nc.close()

if __name__ == "__main__":
    infiles = list(sys.argv[1:])
    if all("ppi" in infile for infile in infiles):
        file_type = "ppi"
    elif all("rhi" in infile for infile in infiles):
        file_type = "rhi"
    else:
        msg = "Mismatch file types: only use all PPI files or all RHI files"
        raise ValueError(msg)
    main(infiles, outloc=OUTLOC, file_type=file_type)
