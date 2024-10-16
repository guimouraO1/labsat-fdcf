import os  # Miscellaneous operating system interfaces
from datetime import datetime  # Basic Dates and time types
import boto3  # Amazon Web Services (AWS) SDK for Python
from botocore import UNSIGNED  # boto3 config
from botocore.config import Config  # boto3 config

def download_cmi_joao(yyyymmddhhmn, band, path_dest, logging):
    os.makedirs(path_dest, exist_ok=True)

    year = datetime.strptime(yyyymmddhhmn, '%Y%m%d%H%M').strftime('%Y')
    day_of_year = datetime.strptime(yyyymmddhhmn, '%Y%m%d%H%M').strftime('%j')
    hour = datetime.strptime(yyyymmddhhmn, '%Y%m%d%H%M').strftime('%H')
    min = datetime.strptime(yyyymmddhhmn, '%Y%m%d%H%M').strftime('%M')

    # AMAZON repository information
    # https://noaa-goes16.s3.amazonaws.com/index.html
    bucket_name = 'noaa-goes16'
    product_name = 'ABI-L2-CMIPF'

    # Initializes the S3 client
    s3_client = boto3.client('s3', config=Config(signature_version=UNSIGNED))
    # -----------------------------------------------------------------------------------------------------------
    # File structure
    prefix = f'{product_name}/{year}/{day_of_year}/{hour}/OR_{product_name}-M6C{int(band):02.0f}_G16_s{year}{day_of_year}{hour}{min}'

    # Seach for the file on the server
    s3_result = s3_client.list_objects_v2(Bucket=bucket_name, Prefix=prefix, Delimiter="/")

    # -----------------------------------------------------------------------------------------------------------
    # Check if there are files available
    if 'Contents' not in s3_result:
        # There are no files
        ##print(f'No files found for the date: {yyyymmddhhmn}, Band-{band}')
        logging.info(f'No files found for the date: {yyyymmddhhmn}, Band-{band}')
        return False
    else:
        # There are files
        for obj in s3_result['Contents']:
            key = obj['Key']
            file_name = key.split('/')[-1].split('.')[0]
            #Alteração problema servidor
            new_file_name = file_name.replace('OR','CG')

            # Download the file
            if os.path.exists(f'{path_dest}/{new_file_name}.nc'):
                logging.info(f'File {path_dest}/{file_name}.nc exists')
                return f"{path_dest}/{file_name}.nc"
            else:
                logging.info(f'Downloading file {path_dest}/{file_name}.nc')
                s3_client.download_file(bucket_name, key, f'{path_dest}/{file_name}.nc')

            # Alteração problema servidor
            old_file = os.path.join(path_dest, f'{file_name}.nc')
            new_file = os.path.join(path_dest, f'{new_file_name}.nc')
            os.rename(old_file, new_file)

    return f"{path_dest}/{new_file_name}.nc"

def getGeoT(extent, nlines, ncols):
    ''' This function computes the resolution based on data dimensions.'''
    resx = (extent[2] - extent[0]) / ncols
    resy = (extent[3] - extent[1]) / nlines
    return [extent[0], resx, 0, extent[3] , 0, -resy]

def download_prod(yyyymmddhhmn, product_name, path_dest):
    os.makedirs(path_dest, exist_ok=True)

    year = datetime.strptime(yyyymmddhhmn, '%Y%m%d%H%M').strftime('%Y')
    day_of_year = datetime.strptime(yyyymmddhhmn, '%Y%m%d%H%M').strftime('%j')
    hour = datetime.strptime(yyyymmddhhmn, '%Y%m%d%H%M').strftime('%H')
    min = datetime.strptime(yyyymmddhhmn, '%Y%m%d%H%M').strftime('%M')

    # AMAZON repository information
    # https://noaa-goes16.s3.amazonaws.com/index.html
    bucket_name = 'noaa-goes16'

    # Initializes the S3 client
    s3_client = boto3.client('s3', config=Config(signature_version=UNSIGNED))

    # File structure
    prefix = f'{product_name}/{year}/{day_of_year}/{hour}/OR_{product_name}-M6_G16_s{year}{day_of_year}{hour}{min}'

    # Seach for the file on the server
    s3_result = s3_client.list_objects_v2(Bucket=bucket_name, Prefix=prefix, Delimiter="/")


    # Check if there are files available
    if 'Contents' not in s3_result:
        # There are no files
        print(f'No files found for the date: {yyyymmddhhmn}, Product-{product_name}')
        return False
    else:
        # There are files
        for obj in s3_result['Contents']:
            key = obj['Key']
            # Print the file name
            file_name = key.split('/')[-1].split('.')[0]
            # file_name = file_name.replace('OR','CG')
            
            # Download the file
            if os.path.exists(f'{path_dest}/{file_name}.nc'):
                print(f'File {path_dest}{file_name}.nc exists')
                return f'{path_dest}/{file_name}.nc'
            else:
                # print(f'Downloading file {path_dest}{file_name}.nc')
                s3_client.download_file(bucket_name, key, f'{path_dest}/{file_name}.nc')
    return f'{path_dest}/{file_name}.nc'