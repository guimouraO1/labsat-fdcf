import numpy as np
from modules.constants import KM_PER_DEGREE
from modules.utilities import getGeoT
from netCDF4 import Dataset
from osgeo import gdal, osr

gdal.PushErrorHandler('CPLQuietErrorHandler')

def getFillValue(path, var='CMI'):
    nc = Dataset(path, mode='r')
    value = nc.variables[var]._FillValue
    nc.close()
    return value

def getProj(path):
    # Open GOES-16 netCDF file
    nc = Dataset(path, mode='r')
    # Get GOES-R ABI fixed grid projection
    proj = nc['goes_imager_projection']
    # Extract parameters
    h = proj.perspective_point_height
    a = proj.semi_major_axis
    b = proj.semi_minor_axis
    inv = 1.0 / proj.inverse_flattening
    lat0 = proj.latitude_of_projection_origin
    lon0 = proj.longitude_of_projection_origin
    sweep = proj.sweep_angle_axis
    # Build proj4 string
    proj4 = ('+proj=geos +h={} +a={} +b={} +f={} +lat_0={} +lon_0={} +sweep={} +no_defs').format(h, a, b, inv, lat0, lon0, sweep)
    # Create projection object
    proj = osr.SpatialReference()
    proj.ImportFromProj4(proj4)
    # Close GOES-16 netCDF file
    nc.close()
    return proj

def getProjExtent(path):
    nc = Dataset(path, mode='r')
    H = nc['goes_imager_projection'].perspective_point_height
    llx = nc.variables['x_image_bounds'][0] * H
    lly = nc.variables['y_image_bounds'][1] * H
    urx = nc.variables['x_image_bounds'][1] * H
    ury = nc.variables['y_image_bounds'][0] * H
    nc.close()
    return [llx, lly, urx, ury]

def getGeoExtent(path):
    nc = Dataset(path, mode='r')
    extent = nc.variables['geospatial_lat_lon_extent']
    llx = extent.geospatial_westbound_longitude
    lly = extent.geospatial_southbound_latitude
    urx = extent.geospatial_eastbound_longitude
    ury = extent.geospatial_northbound_latitude
    nc.close()
    return [llx, lly, urx, ury]


def sat2grid(path, extent, resolution, targetPrj, driver='NETCDF', autoscale=True, progress=None, var='CMI'):
    # Read scale/offset from file
    scale, offset = getScaleOffset(path, var)

    # Extract GOES projection extent
    goesProjExtent = getProjExtent(path)

    # GOES spatial reference system
    sourcePrj = getProj(path)

    # Fill value
    fillValue = getFillValue(path, var)

    # Get total extent, if necessary
    if extent is None:
        extent = getGeoExtent(path)

    # Build connection info based on given driver name
    if driver == 'NETCDF':
        connectionInfo = 'NETCDF:\"' + path + '\":' + var
    elif driver == 'HDF5':
        connectionInfo = 'HDF5:\"' + path + '\"://' + var
    else:
        raise ValueError('Invalid driver name. Options: NETCDF or HDF5')

    # Open NetCDF file (GOES data) using GDAL
    raw = gdal.Open(connectionInfo, gdal.GA_ReadOnly)
    
    # Setup projection and geo-transformation
    raw.SetProjection(sourcePrj.ExportToWkt())
    raw.SetGeoTransform(getGeoT(goesProjExtent, raw.RasterYSize, raw.RasterXSize))
    raw.GetRasterBand(1).SetNoDataValue(float(fillValue))

    # Compute grid dimension
    sizex = int(((extent[2] - extent[0]) * KM_PER_DEGREE)/resolution)
    sizey = int(((extent[3] - extent[1]) * KM_PER_DEGREE)/resolution)

    # Get memory driver
    memDriver = gdal.GetDriverByName('MEM')

    # Output data type and fill-value
    type = gdal.GDT_Float32
    if autoscale is False:
        type, fillValue = gdal.GDT_UInt16, 65535

    # Create grid
    grid = memDriver.Create('grid', sizex, sizey, 1, type)
    grid.GetRasterBand(1).SetNoDataValue(float(fillValue))
    grid.GetRasterBand(1).Fill(float(fillValue))

    # Setup projection and geo-transformation
    grid.SetProjection(targetPrj.ExportToWkt())
    grid.SetGeoTransform(getGeoT(extent, grid.RasterYSize, grid.RasterXSize))
    
    gdal.Warp(grid, raw, dstSRS=targetPrj.ExportToWkt(), 
            xRes=resolution, yRes=resolution,
            multithread=True, 
            callback=progress)
    
    # Close file
    raw = None

    if autoscale:
        # Read grid data
        array = grid.ReadAsArray()
        # Apply scale and offset
        array = np.ma.masked_equal(array, fillValue)
        array = array * scale + offset
        array = np.ma.filled(array, fillValue)
        # Back to raster
        grid.GetRasterBand(1).WriteArray(array)

    # Adjust metadata, if necessary
    if autoscale is False:
        grid.SetMetadata(['SCALE={}'.format(scale), 'OFFSET={}'.format(offset)])

    return grid

def getScaleOffset(path, variable):
    nc = Dataset(path, mode='r')
    
    if (variable == "BCM") or (variable == "Phase") or (variable == "Smoke") or (variable == "Dust") or (variable == "Mask") or (variable == "Power"): 
        scale  = 1
        offset = 0     
    else:
        scale = nc.variables[variable].scale_factor
        offset = nc.variables[variable].add_offset
    nc.close()
        
    return scale, offset
