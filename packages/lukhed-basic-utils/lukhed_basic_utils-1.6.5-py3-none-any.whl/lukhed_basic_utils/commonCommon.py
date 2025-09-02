from lukhed_basic_utils import osCommon as osC

config_dir = 'lukhedConfig'

def check_create_lukhed_config_path():
    osC.check_create_dir_structure([config_dir])

def get_lukhed_config_path():
    return osC.create_file_path_string([config_dir])