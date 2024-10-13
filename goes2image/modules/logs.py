import logging
import time
from datetime import datetime

def conf_log(arq_log):
        logging.basicConfig(filename=arq_log, level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s", datefmt="%d/%m/%Y %H:%M:%S")
        inicio = datetime.now().strftime("%d/%m/%Y-%H:%M:%S")
        logging.info("")
        logging.info("=========================================================================================================")
        logging.info("=                                      PROCESSANDO NDVI AS " + inicio + "                               =")
        logging.info("=========================================================================================================")
        logging.info("")

def finalize_log_time(s):
        fim = datetime.now().strftime("%d/%m/%Y-%H:%M:%S")
        logging.info("")
        logging.info("Tempo gasto " + str(round(time.time() - s, 4)) + ' segundos')
        logging.info("")
        logging.info("=========================================================================================================")
        logging.info("=                                     PROCESSAMENTO ENCERRADO AS " + fim + "                           =")
        logging.info("=========================================================================================================")
        logging.info("")
  
def conf_log_D(arq_log):
        logging.basicConfig(filename=arq_log, level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s", datefmt="%d/%m/%Y %H:%M:%S")

