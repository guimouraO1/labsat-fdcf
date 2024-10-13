import json
import logging
import os
import time
from datetime import datetime, timedelta
from modules.download_amazon import download_nc_files
from modules.dirs import get_dirs
from modules.logs import conf_log, finalize_log_time
from modules.remove import remover_imagens, remover_ndvi
from modules.fdcf import process_fdcf

os.environ['PROJ_LIB'] = '/opt/conda/envs/goes/share/proj'

def open_json(dir_main):
    arquivo_json = open(f'{dir_main}bands.json', 'r')
    dados = json.load(arquivo_json)
    arquivo_json.close()
    return dados

def create_path(path):
    if not os.path.exists(path):
        os.makedirs(path)

def create_json_file(caminho_arquivo):
    if not os.path.exists(caminho_arquivo):
        with open(caminho_arquivo, 'w') as arquivo_json:
            json.dump({"dates": []}, arquivo_json, indent=4)

def update_json_dates(caminho_arquivo, new_date, band):
    try:
        create_json_file(caminho_arquivo)
        
        arquivo_json = open(caminho_arquivo, 'r')
        dados = json.load(arquivo_json)
        arquivo_json.close()

        if len(dados['dates']) > 10:
            primeira_data = datetime.strptime(dados['dates'][0], "%Y-%m-%dT%H:%M:%SZ").strftime("%Y%m%d/%H%M")
            
            if os.path.exists(f"{dir_products}{primeira_data}/{band}"):
                logging.info(f'Excluindo pasta {dir_products}{primeira_data}/{band}')
                shutil.rmtree(f"{dir_products}{primeira_data}/{band}")
            dados['dates'].pop(0)
        
        dados['dates'].append(new_date)

        arquivo_json = open(caminho_arquivo, 'w')
        json.dump(dados, arquivo_json, indent=4)
        arquivo_json.close()

    except Exception as error:
        logging.error(f'Erro ao adicionar dates :   {error}')

def init_process_fdcf(new_bands, extent, dir_out, date_now, dir_dates, dir_products):
    try:
        fdcf = f'{new_bands["fdcf"]}'
        dir_out_fdcf = f'{dir_out}'
        date_out = datetime.strftime(date_now, "%Y%m%d/%H%M")

        process_fdcf(fdcf, extent, dir_out_fdcf, date_out, dir_products)

        new_date = date_now.strftime("%Y-%m-%dT%H:%M:%SZ")
        update_json_dates(f'{dir_dates}date_fdcf.json', new_date, f'fdcf')
        logging.info(f'Novas datas para FDCF concluído!')
    except Exception as e:
        logging.error(f"Erro no processamento do Arquivo FDCF: {e}")

if __name__ == "__main__":
    start = time.time()
    
    dirs = get_dirs()
    dir_in = dirs['dir_in']
    dir_out = dirs['dir_out']
    arq_log = dirs['arq_log']
    dir_main = dirs['dir_main']
    dir_dates = dirs['dir_dates']
    dir_products = dirs['dir_products']

    conf_log(arq_log)
    extent = [-140.0, -60.0, -5.0, 60.0]

    logging.info(f'')
    logging.info(f'Iniciando processamento fdcf')

    bands, date_now = download_nc_files()
    if(bands):
        new_products = open_json(dir_main)
        logging.info(new_products)
        init_process_fdcf(new_products, extent, dir_out, date_now, dir_dates, dir_products)
        # remover_imagens(bands, dir_in, dir_main)
    else:
        # remover_imagens(bands, dir_in, dir_main)
        logging.info(f'Sem imagens para fdcf')
    
    logging.info(f'')
    logging.info(f'Finalizando..')
    finalize_log_time(start)