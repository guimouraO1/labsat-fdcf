from datetime import date

def get_dirs():
    dir_main = '/home/cpaunicamp/goes2image/'

    dirs = {
        'dir_main': dir_main,
        'dir_in': f'{dir_main}goes/',
        'dir_out': f'{dir_main}output/',
        'arq_log': f'{dir_main}logs/Processamento-GOES_FDCF_{str(date.today())}.log',
        'dir_dates': f'{dir_main}dates/',
        'dir_products': f'{dir_main}products/'
    }
    
    return dirs
