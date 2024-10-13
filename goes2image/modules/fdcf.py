import logging
import numpy as np
from datetime import datetime
from netCDF4 import Dataset
from geojson import Feature, FeatureCollection, Point as GeoPoint
from geojson import dump
import os

def degrees(file_id):
    proj_info = file_id.variables['goes_imager_projection']
    lon_origin = proj_info.longitude_of_projection_origin
    H = proj_info.perspective_point_height + proj_info.semi_major_axis
    r_eq = proj_info.semi_major_axis
    r_pol = proj_info.semi_minor_axis

    lat_rad_1d = file_id.variables['x'][:]
    lon_rad_1d = file_id.variables['y'][:]
    lat_rad, lon_rad = np.meshgrid(lat_rad_1d, lon_rad_1d)

    lambda_0 = (lon_origin * np.pi) / 180.0
    a_var = np.power(np.sin(lat_rad), 2.0) + np.power(np.cos(lat_rad), 2.0) * (
        np.power(np.cos(lon_rad), 2.0) + ((r_eq ** 2) / (r_pol ** 2)) * np.power(np.sin(lon_rad), 2.0))
    b_var = -2.0 * H * np.cos(lat_rad) * np.cos(lon_rad)
    c_var = H ** 2 - r_eq ** 2

    # Prevent sqrt < 0
    r_s = (-b_var - np.sqrt(np.maximum(b_var ** 2 - 4 * a_var * c_var, 0))) / (2 * a_var)
    # r_s = (-b_var - np.sqrt(b_var ** 2 - 4 * a_var * c_var)) / (2 * a_var)
    s_x = r_s * np.cos(lat_rad) * np.cos(lon_rad)
    s_y = -r_s * np.sin(lat_rad)
    s_z = r_s * np.cos(lat_rad) * np.sin(lon_rad)

    lat = (180.0 / np.pi) * (np.arctan((r_eq ** 2) / (r_pol ** 2) * (s_z / np.sqrt((H - s_x) ** 2 + s_y ** 2))))
    lon = (lambda_0 - np.arctan(s_y / (H - s_x))) * (180.0 / np.pi)
    return lat, lon


def create_path(path):
    if not os.path.exists(path):
        os.makedirs(path)
        
def process_fdcf(fdcf, extent, dir_out, date_output, dir_products):
    fire_mask = Dataset(fdcf)
    fire_mask_values = fire_mask.variables['Mask'][:, :]
    selected_fires = (fire_mask_values == 10) | (fire_mask_values == 11) | (fire_mask_values == 13) | (fire_mask_values == 30) | (fire_mask_values == 33)

    lat, lon = degrees(fire_mask)
    p_lat = lat[selected_fires]
    p_lon = lon[selected_fires]
    
    # Filtra os pontos de acordo com o extent
    filtered_points = []
    for i in range(len(p_lat)):
        filtered_points.append((p_lat[i], p_lon[i]))
    
    path = f'{dir_products}{date_output}/fdcf/'
    create_path(path)
    
    gerar_geojson(filtered_points, f'{path}fdcf.geojson')
    fire_mask.close()
    
def gerar_geojson(pixels_fogo, output_geojson):
    features = [Feature(geometry=GeoPoint((float(lon), float(lat)))) for lat, lon in pixels_fogo]
    feature_collection = FeatureCollection(features)
    
    with open(output_geojson, 'w') as geojson_file:
        dump(feature_collection, geojson_file, indent=2)

    logging.info(f'GeoJSON file created: {output_geojson}')
