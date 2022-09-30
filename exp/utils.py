from exp.models import Descriptor, DescriptorMap, DescriptorNameValue, DescriptorValue, ExperimentFile, HandledDirectory, Experiment, ExpPlatform, ModelOrganism, Project, PrepMethod
from django.contrib.contenttypes.models import ContentType
from ngsdb.settings import NGS_LOCAL_FOLDER_FILEPATH
from django.core.files.base import  ContentFile
from django.contrib.auth.models import User
from exp.parse_meta import _parse_meta
from enum import Enum
import os 
import gc


def write_debug(m):
    with open('debug.txt', 'a') as d:
        d.write(str(m) + '\n')


# TODO: Add Regex patterns
RNA_SEQ_FOLDER_PATTERN = 'RNA-Seq'
RAW_DATA_FILEPATH_PATTERN = 'deseq.csv'
META_DATA_FILEPATH_PATTERN = 'NextSeq.csv'
COUNT_MATRIX_FILEPATH_PATTERN = 'count_matrix.csv'
RESULTS_FOLDER_NAME = 'results'


#####################
# DEFAULT INSTANCES #
#####################

DEFAULT_USER_OBJ, user_created = User.objects.get_or_create(
    username='testuser',
    password='12345'
)

DEFAULT_EXP_PLATFORM, platform_created = ExpPlatform.objects.get_or_create(
    title='Default Platform',
    n_reads=0,
    length_libtype='Default Length & Libtype'
)

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
  

DEFAULT_PROJECT, project_created = Project.objects.get_or_create(
    title='Default Project'
)

DEFAULT_PREP_METHOD, method_created = PrepMethod.objects.get_or_create(
    method='Default Method',
    kit='Default Kit'
)

###############################
# Folder Validating functions #
###############################


def match_rna_folder(base_folder_filepath):
    global RNA_SEQ_FOLDER_PATTERN
    rna_folders = [
        folder
        for folder in os.listdir(base_folder_filepath)
        if folder.endswith(RNA_SEQ_FOLDER_PATTERN)
    ]
    return rna_folders


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

#############################
# File validating Functions #
#############################

class FileType(Enum):
    NEXTSEQ = 'nextseq'
    DESEQ = 'deseq'
    COUNT_MATRIX = 'count_matrix'


def filtered_files_valid(files_list):
    '''Checks if files in a list are all complete for creating 
        an Experiment obj 
    '''
    all_types = len(set([file_dict['type'] for file_dict in files_list])) == 3
    one_nextseq = len([
        file_dict 
        for file_dict in files_list
        if file_dict['type'] == FileType.COUNT_MATRIX]) == 1
    
    return all_types and one_nextseq


def validate_csv_file(directory_filepath, filename: str):
    
    '''Match a file and its type if possible. Otherwise returns valid=False'''
    
    global RAW_DATA_FILEPATH_PATTERN, META_DATA_FILEPATH_PATTERN
    
    if filename.endswith(RAW_DATA_FILEPATH_PATTERN):
        return {
            'valid': True,
            'type': FileType.DESEQ,
            'filename': os.path.join(directory_filepath,filename)
        }

    elif filename.endswith(META_DATA_FILEPATH_PATTERN):
        return {
            'valid': True,
            'type': FileType.NEXTSEQ,
            'filename': os.path.join(directory_filepath, filename)
        }
    
    elif filename.endswith(COUNT_MATRIX_FILEPATH_PATTERN):
        return {
            'valid': True,
            'type': FileType.COUNT_MATRIX,
            'filename': os.path.join(directory_filepath,filename)
        }
    
    return {
        'valid': False
    }


def filter_folder_csv_files(directory_filepath, folder_files: list):
    
    folder_files_dicts = [
        validate_csv_file(directory_filepath, file)
        for file in folder_files
    ]

    valid_csv_files = [
        file_dict
        for file_dict in folder_files_dicts
        if file_dict['valid']
    ]
    
    return valid_csv_files


def filter_rna_folder(folder_name):
    
    try:
        folder_files = os.listdir(folder_name)
    except Exception:
        return ()
    
    # Results folder should be in directory
    if RESULTS_FOLDER_NAME not in folder_files:
        return ()
    
    # Scan Top-level dir -> NextSeq file
    valid_csv_files = filter_folder_csv_files(folder_name, folder_files)

    # results folder files
    results_folder_filepath = os.path.join(folder_name, 'results')
    results_files = os.listdir(results_folder_filepath)

    # add results valid files to top level files
    valid_csv_files.extend(
        filter_folder_csv_files(results_folder_filepath, results_files)
    )
    
    if not filtered_files_valid(valid_csv_files):
        return ()
    
    return valid_csv_files
    
#########################################
# Creating & handling Experiment object #
#########################################

class ExperimentFileHandler:
    @staticmethod
    def create(exp_obj, filetype, file_dict):
        content_file = ContentFile(
            open(file_dict['filename']).read(),
            file_dict['filename']
        )
        
        exp_file_obj = ExperimentFile.objects.create(
            experiment=exp_obj,
            file_type=filetype,
            file_instance = content_file
        )
        
        exp_file_obj.save()



class NextSeqFileHandler(ExperimentFileHandler):
    @staticmethod
    def create(exp_obj, filetype, file_dict):
        _parse_meta(file_dict['filename'], exp_obj)
        ExperimentFileHandler.create(exp_obj, filetype, file_dict)


def create_experiment_obj(directory_obj):
    
    exp_obj = Experiment.objects.create(
        exp_directory=directory_obj,
        project=DEFAULT_PROJECT,
        platform=DEFAULT_EXP_PLATFORM,
        organism=DEFAULT_MODEL_ORGANISM,
        prep_method=DEFAULT_PREP_METHOD
    )
    exp_obj.users.set(
        User.objects.in_bulk([
            DEFAULT_USER_OBJ.id
        ])
    )   # Any other options don't work
    exp_obj.save()
    
    return exp_obj


def create_experiment_files(exp_obj, directory_files):

    # Handle NextSeq file 
    
    nextseq_file_dict = [
        file_dict 
        for file_dict in directory_files
        if file_dict['type'] == FileType.NEXTSEQ][0]
    
    NextSeqFileHandler.create(
        exp_obj,
        FileType.NEXTSEQ.value,
        nextseq_file_dict
    )
    
    # Handle Deseq files
    
    deseq_files_dicts = [
        file_dict
        for file_dict in directory_files
        if file_dict['type'] == FileType.DESEQ
    ]
    for deseq_file_dict in deseq_files_dicts:
        ExperimentFileHandler.create(
            exp_obj,
            FileType.DESEQ.value,
            deseq_file_dict
        )
    
    # Handle CountMatrix Files
    
    count_matrix_files_dicts = [ 
        file_dict 
        for file_dict in directory_files
        if file_dict['type'] == FileType.COUNT_MATRIX
    ]

    for count_matrix_file_dict in count_matrix_files_dicts:
        ExperimentFileHandler.create(
            exp_obj,
            FileType.COUNT_MATRIX.value,
            count_matrix_file_dict
        )


#####################################
# Refresh Experiments Main Function #
#####################################


def refresh_experiments():
    ''''''
    
    try:
        rna_folders = match_rna_folder(NGS_LOCAL_FOLDER_FILEPATH)
    except Exception:
        return 
    
    if len(rna_folders) == 0:
        return

    for rna_folder in rna_folders:
        
        handled_directory, dir_created = HandledDirectory.objects.\
            get_or_create(
                directory_name=rna_folder        
        )
        
        if not dir_created:
            continue
    
        else:
            valid_directory_files = filter_rna_folder(
                NGS_LOCAL_FOLDER_FILEPATH / rna_folder)

            # If both csv files found
            if bool(valid_directory_files):
                try:
                    exp_obj = create_experiment_obj(handled_directory)
                    create_experiment_files(exp_obj, valid_directory_files)
                except Exception as e:
                    write_debug(e)
            # Folder Invalid so directory is not handled
            else:
                handled_directory.delete()
            
    
    
    
    
    