from exp.models import Descriptor, DescriptorMap, DescriptorNameValue, DescriptorValue, HandledDirectory, Experiment, ExpPlatform, ModelOrganism, Project, PrepMethod
from django.contrib.contenttypes.models import ContentType
from ngsdb.settings import NGS_LOCAL_FOLDER_FILEPATH, BASE_DIR, MEDIA_ROOT
from django.core.files.base import File, ContentFile
from exp.parse_meta import _parse_meta
from django.contrib.auth.models import User
import os 
import gc


def write_debug(msg):
    with open('debug.txt', 'a', newline='\n') as d:
        d.write(msg + '\n')


# TODO: Add Regex patterns
RNA_SEQ_FOLDER_PATTERN = 'RNA-Seq'
RAW_DATA_FILEPATH_PATTERN = 'AICAR.deseq.csv'
META_DATA_FILEPATH_PATTERN = 'NextSeq.csv'


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


def create_experiment_obj(directory_obj, directory_files):
    
    directory_filepath = NGS_LOCAL_FOLDER_FILEPATH / directory_obj.directory_name
    
    meta_file_dict = [
        file_dict 
        for file_dict in directory_files
        if file_dict['type'] == 'meta_data'
    ][0]
    
    raw_file_dict = [
        file_dict
        for file_dict in directory_files
        if file_dict['type'] == 'raw_data'
    ][0]
    
    
    meta_content_file = ContentFile(
        open(directory_filepath / meta_file_dict['filename']).read(),
        meta_file_dict['filename']
    )
    raw_content_file = ContentFile(
        open(directory_filepath / raw_file_dict['filename']).read(),
        raw_file_dict['filename']
    )

    exp_obj = Experiment.objects.create(
        exp_directory=directory_obj,
        metadata_filepath=meta_content_file,
        data_filepath=raw_content_file,
        project=DEFAULT_PROJECT,
        platform=DEFAULT_EXP_PLATFORM,
        organism=DEFAULT_MODEL_ORGANISM,
        prep_method=DEFAULT_PREP_METHOD
    )
    exp_obj.users.set(
        [User.objects.get(username='admin')]
    )


    exp_obj.save()
    gc.collect()
    
    # Parse Meta
    _parse_meta(MEDIA_ROOT / exp_obj.metadata_filepath.name, exp_obj)

    
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
        # If New directory 
        if dir_created:
            # If both csv files found
            if bool(valid_directory_files):
                create_experiment_obj(handled_directory, valid_directory_files)
                
            # Folder Invalid so directory is not handled
            else:
                write_debug(f'No files found for {rna_folder}')
                handled_directory.delete()
        else:
            write_debug(f'Directory already handled {handled_directory}')
            
    
    
    
    
    