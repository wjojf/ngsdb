from asyncore import write
from distutils.log import debug
from exp.models import Descriptor, DescriptorMap, DescriptorNameValue, DescriptorValue, HandledDirectory, Experiment, ExpPlatform, ModelOrganism, Project, PrepMethod
from django.contrib.contenttypes.models import ContentType
from ngsdb.settings import NGS_LOCAL_FOLDER_FILEPATH, BASE_DIR
from django.core.files.base import File
from exp.parse_meta import _parse_meta
import os 
import gc


def write_debug(msg):
    with open('debug.txt', 'a', newline='\n') as d:
        d.write(msg + '\n')


# TODO: Add Regex patterns
RNA_SEQ_FOLDER_PATTERN = 'RNA-Seq'
RAW_DATA_FILEPATH_PATTERN = 'AICAR.deseq.csv'
META_DATA_FILEPATH_PATTERN = 'NextSeq.xlsx'


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

DEFAULT_PROJECT, project_created = Project.objects.get_or_create(
    title='Default Project'
)

######################
# Default PrepMethod #               
######################

DEFAULT_PREP_METHOD, method_created = PrepMethod.objects.get_or_create(
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
    
    csv_folder_files_dicts = [
        validate_csv_file(file)
        for file in folder_files
    ]
    write_debug(f'{csv_folder_files_dicts}')

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
        write_debug(f'Error scanning {folder_name}')
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


def generate_filefield_instances_by_filepath(fp_string: str):
    ''''''
    try:
        with open(fp_string) as f:
            return fp_string, File(f)
    except Exception:
        return None


def create_experiment_obj(directory_filepath, directory_files):
    exp_obj = Experiment.objects.create(
        project=DEFAULT_PROJECT,
        platform=DEFAULT_EXP_PLATFORM,
        organism=DEFAULT_MODEL_ORGANISM,
        prep_method=DEFAULT_PREP_METHOD
    )
    
    meta_file_dict = [
        file_dict 
        for file_dict in directory_files
        if file_dict['type'] == 'meta_data'][0]
    
    raw_file_dict = [
        file_dict
        for file_dict in directory_files
        if file_dict['type'] == 'raw_data'][0]
    
    
    meta_file_instances = generate_filefield_instances_by_filepath(
        directory_filepath / meta_file_dict['filename']
    )
    if meta_file_instances:
        try:
            meta_saved_to = exp_obj.metadata_filepath.storage.save(*meta_file_instances)
            exp_obj.metadata_filepath = meta_saved_to
        except Exception as e:
            write_debug((f'MetaData error {e}'))
            
    
    
    raw_file_instances = generate_filefield_instances_by_filepath(
        directory_filepath / raw_file_dict['filename']
    )
    
    if raw_file_instances:
        try:
            raw_saved_to = exp_obj.data_filepath.storage.save(*raw_file_instances)
            exp_obj.data_filepath = raw_saved_to
        except Exception as e:
            write_debug(f'RawData error {e}')

    
    write_debug(f'{meta_file_instances}')
    write_debug(f'{raw_file_instances}')

    exp_obj.save()
    gc.collect()
    
    # Parse Meta
    # TODO:

    
#####################################
# Refresh Experiments Main Function #
#####################################

def refresh_experiments():
    ''''''
    
    try:
        rna_folders = match_rna_folder(NGS_LOCAL_FOLDER_FILEPATH)
        if len(rna_folders) == 0:
            write_debug('RNA folders not found')
            return
    except Exception:
        write_debug('Error loading RNA folders')
        return 

    for rna_folder in rna_folders:
        
        handled_directory, dir_created = HandledDirectory.objects.\
            get_or_create(
                directory_name=rna_folder        
        )
        valid_directory_files = filter_rna_folder(NGS_LOCAL_FOLDER_FILEPATH / rna_folder)
        write_debug(f'{valid_directory_files}')
        # If New directory 
        if dir_created:
            # If both csv files found
            if bool(valid_directory_files):
                create_experiment_obj(NGS_LOCAL_FOLDER_FILEPATH/rna_folder, valid_directory_files)
                
            # Folder Invalid so directory is not handled
            else:
                write_debug(f'No files found for {rna_folder}')
                handled_directory.delete()
        else:
            write_debug(f'Directory not created {handled_directory}')
            
    
    
    
    
    