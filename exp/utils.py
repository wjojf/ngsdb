from exp.models import HandledURL, Experiment, ExpPlatform, ModelOrganism, Project, PrepMethod
import os 


# TODO: Add Regex patterns
RNA_SEQ_FOLDER_PATTERN = '_RNA_Seq'
RAW_DATA_FILEPATH_PATTERN = 'AICAR.deseq.csv'
META_DATA_FILEPATH_PATTERN = '_NextSeq.csv'


#TODO: Add Default Project, Platform, ModelOrganism, PrepMethod


def validate_folder(folder_name: str):
    global RNA_SEQ_FOLDER_PATTERN
    
    if folder_name.strip().endswith(RNA_SEQ_FOLDER_PATTERN):
        return {
            'valid': True,
            'folder_name': folder_name
        }

    return {
        'valid': False 
    }


def validate_csv_file(filename: str):
    global RAW_DATA_FILEPATH_PATTERN, META_DATA_FILEPATH_PATTERN
    
    if filename.endswith(RAW_DATA_FILEPATH_PATTERN):
        return {
            'valid': True,
            'type': 'raw_data',
            'filename': filename
        }

    elif filename.endswith(META_DATA_FILEPATH_PATTERN):
        return {
            'valid': True,
            'type': 'meta_data',
            'filename': filename
        }
    
    return {
        'valid': False
    }


def filter_folder_csv_files(folder_files: list):
    csv_folder_files = [
        file
        for file in folder_files if file.endswith('.csv')
    ]

    csv_folder_files_dicts = [
        validate_csv_file(file)
        for file in csv_folder_files
    ]

    valid_csv_files = [
        file_dict
        for file_dict in csv_folder_files_dicts
        if file_dict['valid']
    ]
    
    return valid_csv_files


def filter_experiment_folder(folder_name):
    
    try:
        folder_files = os.listdir(folder_name)
    except Exception:
        return ()
    
    valid_csv_files = filter_folder_csv_files(folder_files)
    
    # Only 2 files: Meta & Raw
    if len(valid_csv_files) != 2:
        return ()
    
    # Only different types of files
    if valid_csv_files[0]['type'] == valid_csv_files[1]['type']:
        return ()
    
    return valid_csv_files
    
    