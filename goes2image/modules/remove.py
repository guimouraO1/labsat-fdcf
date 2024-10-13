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
            os.remove(f'{dados['02']}')
            os.remove(f'{dados['02']}.aux.xml')
            logging.info(f'Arquivo {dados['02']} removido com sucesso!')
        except:
            logging.info(f'Sem arquivos para remover {dir_in}band02/{dados['02']}')

        try:
            os.remove(f'{dados['03']}')
            os.remove(f'{dados['03']}.aux.xml')
            logging.info(f'Arquivo {dados['03']} removido com sucesso!')
        except:
            logging.info(f'Sem arquivos para remover {dados['03']}')
        
        try:
            os.remove(f'{dados['mask']}')
            os.remove(f'{dados['mask']}.aux.xml')
            logging.info(f'Arquivo {dados['mask']} removido com sucesso!')
        except:
            logging.info(f'Sem arquivos para remover {dados['mask']}')
        
        logging.info("")
        logging.info(f'Arquivos removidos com sucesso!')
        

def remover_ndvi(dir_out):
    logging.info("")
    logging.info('Final de semana, limpando pasta')
    ndvi_path = os.path.join(dir_out, 'ndvi')
    
    if os.path.exists(ndvi_path):
        try: 
            shutil.rmtree(ndvi_path)
            logging.info(f'Pasta {dir_out}ndvi/ limpa')
        except:
            logging.info(f'Pasta {ndvi_path} não encontrada')
    else:
        os.makedirs(f'{dir_out}ndvi')

