import json
import logging
import os
import re
import shutil
from modules.dirs import get_dirs

def open_json(dir_main):
    arquivo_json = open(f'{dir_main}bands.json', 'r')
    dados = json.load(arquivo_json)
    arquivo_json.close()
    return dados

def remover_imagens(bands, dir_in, dir_main): 
    logging.info("")
    logging.info(f'Removendo arquivos nc...')
    dados = open_json(dir_main)
    
    if bands == True:        
        try:
            os.remove(f'{dados['fdcf']}')
            logging.info(f'Arquivo {dados['fdcf']} removido com sucesso!')
        except:
            logging.info(f'Sem arquivos para remover {dados['fdcf']}')
        
        logging.info("")
        logging.info(f'Arquivos removidos com sucesso!')

