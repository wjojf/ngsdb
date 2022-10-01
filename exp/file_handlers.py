from django.core.files.base import  ContentFile
from exp.models import ExperimentFile
from exp.parse_meta import _parse_meta
from enum import Enum


class FileType(Enum):
    NEXTSEQ = 'nextseq'
    DESEQ = 'deseq'
    COUNT_MATRIX = 'count_matrix'


class ExperimentFileHandler:
    
    @staticmethod 
    def create_from_file_instance(file_instance, exp_obj, filetype):
        exp_file_obj = ExperimentFile.objects.create(
            experiment=exp_obj,
            file_type=filetype,
            file_instance =file_instance
        )
        
        exp_file_obj.save()
    
    @staticmethod
    def create_from_file_dict(exp_obj, filetype, file_dict):
        content_file = ContentFile(
            open(file_dict['filename']).read(),
            file_dict['filename']
        )
        
        ExperimentFileHandler.create_from_file_instance(
            content_file, exp_obj, filetype
        )


class NextSeqFileHandler(ExperimentFileHandler):

    @staticmethod
    def create_from_file_instance(file_instance, exp_obj, filetype=FileType.NEXTSEQ.value):
        _parse_meta(file_instance, exp_obj)
        ExperimentFileHandler.create_from_file_instance(file_instance, exp_obj, filetype)
    
    @staticmethod
    def create_from_file_dict(exp_obj, file_dict, filetype=FileType.NEXTSEQ.value):
        content_file = ContentFile(
            open(file_dict['filename']).read(),
            file_dict['filename']
        )
        _parse_meta(content_file.name, exp_obj)
        ExperimentFileHandler.create_from_file_dict(exp_obj, filetype, file_dict)