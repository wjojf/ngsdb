from exp.models import Descriptor, DescriptorMap, DescriptorNameValue, DescriptorValue, HandledDirectory, Experiment, ExpPlatform, ModelOrganism, Project, PrepMethod
from django.contrib.contenttypes.models import ContentType
from ngsdb.settings import NGS_LOCAL_FOLDER_FILEPATH
from django.core.files.base import File
import os 


# TODO: Add Regex patterns
RNA_SEQ_FOLDER_PATTERN = '_RNA_Seq'
RAW_DATA_FILEPATH_PATTERN = 'AICAR.deseq.csv'
META_DATA_FILEPATH_PATTERN = '_NextSeq.csv'


#####################
# DEFAULT INSTANCES #
#####################

DEFAULT_EXP_PLATFORM, platform_created = ExpPlatform.objects.get_or_create(
    title='Default Platform',
    n_reads=0,
    length_libtype='Default Length & Libtype'
)

#########################
# Default ModelOrganism #
#########################

DEFAULT_MODEL_ORGANISM, organism_created = ModelOrganism.objects.get_or_create(
    name='human'
)
# Add Custom field: status='default'
status_descriptor, desc_created = Descriptor.objects.get_or_create(
    name='status'
)
status_value, value_created = DescriptorValue.objects.get_or_create(
    value='default'
)
status_desc_name_value, desc_name_value_created = DescriptorNameValue.objects.\
    get_or_create(
        desc_name=status_descriptor,
        desc_value=status_value
)
status_desc_map, desc_map_created = DescriptorMap.objects.get_or_create(
    descriptor_name_value=status_desc_name_value,
    content_type=ContentType.objects.get_for_model(ModelOrganism),
    object_id=DEFAULT_MODEL_ORGANISM.id
)
    

###################
# Default Project #
###################

DEFAULT_PROJECT = Project.objects.get_or_create(
    title='Default Project'
)

######################
# Default PrepMethod #               
######################

DEFAULT_PREP_METHOD = PrepMethod.objects.get_or_create(
    method='Default Method',
    kit='Default Kit'
)

###############################
# Folder Validating functions #
###############################

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


def filter_rna_folder(folder_name):
    
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
    

def match_rna_folder(base_folder_filepath):
    global RNA_SEQ_FOLDER_PATTERN
    rna_folders = [
        folder 
        for folder in os.listdir(base_folder_filepath)
        if folder.endswith(RNA_SEQ_FOLDER_PATTERN)
    ]
    return rna_folders


def convert_string_to_file_instance(fp_string: str):
    ''''''
    try:
        with open(fp_string) as f:
            return File(f)
    except Exception:
        return None

#####################################
# Refresh Experiments Main Function #
#####################################

def refresh_experiments():
    ''''''
    try:
        rna_folders = match_rna_folder(NGS_LOCAL_FOLDER_FILEPATH)
        if len(rna_folders) == 0:
            return
    except Exception:
        return 

    
    for rna_folder in rna_folders:
        
        handled_directory, dir_created = HandledDirectory.objects.\
            get_or_create(
                directory_name=rna_folder        
        )
        valid_directory_files = filter_rna_folder(rna_folder)
        
        # If New directory & both csv files found
        if dir_created and bool(valid_directory_files):
            #TODO: Create Exp obj
            pass
    
    
    
    
    