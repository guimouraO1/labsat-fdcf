import datetime
import logging
from datetime import datetime, timedelta, timezone
from modules.dirs import get_dirs
from modules.utilities import download_cmi_joao, download_prod
import json

def modificar_chave_bands(caminho_arquivo, chave, novo_valor):
    try:
        arquivo_json = open(caminho_arquivo, 'r')
        dados = json.load(arquivo_json)
        arquivo_json.close()

        dados[chave] = novo_valor

        arquivo_json = open(caminho_arquivo, 'w')
        json.dump(dados, arquivo_json, indent=4)
        arquivo_json.close()
        
        return True
    except IOError as e:
        logging.error(f"Erro ao modificar chave no arquivo JSON: {e}")
        return False

def download_nc_files():
    dirs = get_dirs()
    dir_in = dirs['dir_in']
    dir_main = dirs['dir_main']

    data_hora_atual = datetime.now(timezone.utc)
    data_10_min = datetime.strftime(data_hora_atual-timedelta(minutes=10),'%Y%m%d%H%M')
    data_hora_download_file = data_10_min[0:11] + '0'
    
    logging.info(f"Processing time: {data_hora_download_file}")

    try:
        logging.info('')
        logging.info(f'Tentando download fdcf...')
        
        fdcf = download_prod(data_hora_download_file, "ABI-L2-FDCF", f'{dir_in}fdcf')
        if(fdcf == False):
            return False
        
        new_bands = modificar_chave_bands(f'{dir_main}bands.json', 'fdcf', fdcf)
        if(new_bands == False):
            return False
        
        logging.info(f'Download concluído!')
        logging.info('')
        
        download_datetime = datetime.strptime(data_hora_download_file, '%Y%m%d%H%M')
        
        return True, download_datetime
    except Exception as e:
        logging.error(e)
        logging.error(f'Sem dados para o dia {data_hora_download_file}.')
        return False, datetime(data_hora_download_file, '%Y%m%d%H%M')


