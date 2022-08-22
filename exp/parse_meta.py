from venv import create
import pandas as pd 
import exp.models as exp_models
from django.contrib.contenttypes.models import ContentType


EXPERIMENT_DESCRIPTOR_COLUMNS = {
	'Sample': ['sample', 'sample_id', 'sample id', 'sampleid'],
	'Condition': ['cond', 'condition', 'cond1', 'cond 1', 'condition1', 'condition 1'],
	'Condition2': ['cond2', 'cond 2', 'condition 2', 'condition2']
}

TEST_DF_ROWS = [
	(f'ig0{i}', f'L{i}', f'L{i}_{i}')
	for i in range(1, 4)
]

TEST_DF_COLUMNS = ['SAMPLE', 'CONDITION 1', 'COND 2']

TEST_DF = pd.DataFrame(TEST_DF_ROWS, columns=TEST_DF_COLUMNS)

# Sample Cond                    Descriptor   DescriptorValue
# ig01	 L1							ig01	 L1
# ig02	 L2			-----> 			...      ...
# ig03	 L3							...      ...
# ig04	 L4							...      ...
# ig05   L5							ig05      L5


# Sample Cond Cond 2                  Descriptor   DescriptorValue  DescriptorValue2
# ig01	 L1	  L1_1						ig01	  			L1          L1_1
# ig02	 L2			  		-----> 		ig02				L2          None
# ig03	 L3								...      
# ig04	 L4								...      
# ig05   L5	  L_5_5					ig05      L5        L5          L5_5


def load_df_from_content(content):
	df = pd.read_csv(content, sep=',')
	return df.dropna()


def match_column(column_name: str):
	global EXPERIMENT_DESCRIPTOR_COLUMNS
	#	Matches a DataFrame column with 
	#	DescriptorMap object
	
	# 	returns: tuple (exp_field, True) / (None, False) if not found
 
	# Example: column_name = 'Condition1'
	# 	returns ('conditions', True)
	matched_columns = {}

	for filtered_col in EXPERIMENT_DESCRIPTOR_COLUMNS:
		if any(
			(column_name.lower().strip() == col_example
			 for col_example in EXPERIMENT_DESCRIPTOR_COLUMNS[filtered_col])
		):
			matched_columns = {column_name: filtered_col}
			break
	
	return matched_columns


def filter_df(df):
	global EXPERIMENT_DESCRIPTOR_COLUMNS
	#	Filters DataFrame: 
	# keep only columns where match_column(column) is not empty and renames columns
	matched_columns = [match_column(col) for col in df.columns if match_column(col) != {}]
	rename_columns = {}
	for matched_column in matched_columns:
		rename_columns.update(matched_column)

	filtered_df = df.rename(columns=rename_columns)
	valid_columns = [col for col in filtered_df.columns if col in EXPERIMENT_DESCRIPTOR_COLUMNS]
	
	output = filtered_df[valid_columns]

	return output


def create_descriptors(df, sample_column, descriptor_column, exp_obj):
	'''
 		Creates Sample & DescriptorMap objects from filtered NextSeq DataFrame
	'''	
	# df - DataFrame with at least two columns ('Descriptor' & 'DescriptorValue')
	# desc_name_column: str:  column containing descriptor names
	# desc_val_column: str: column containing descriptor values
	# content_type: ContentType object for DescriptorMap 
	# exp_obj_id: Experiment object id  

	
	if (sample_column not in df.columns) or (descriptor_column not in df.columns):
		return 

	descriptor_obj, descriptor_obj_created = exp_models.Descriptor.objects.get_or_create(
		name=descriptor_column
	)
	sample_content_type = ContentType.objects.get_for_model(exp_models.Sample)

	for sample_value, descriptor_value in zip(df[sample_column], df[descriptor_column]):
     
		sample_value = str(sample_value)
		descriptor_value = str(descriptor_value)
   
		sample_obj, sample_created = exp_models.Sample.objects.get_or_create(
			experiment=exp_obj,
			sample_value=sample_value
		)

		desc_value_obj, desc_value_created = exp_models.DescriptorValue.objects.get_or_create(
			descriptor=descriptor_obj,
			value=descriptor_value
		)

		desc_map_obj, desc_map_created = exp_models.DescriptorMap.objects.get_or_create(
			desc_name=descriptor_obj,
			desc_value=desc_value_obj,
			content_type=sample_content_type,
			object_id = sample_obj.id
		)

	
#################
# Main Function #
#################


def _parse_meta(content, exp_obj):
    
	df = load_df_from_content(content)
	filtered_df = filter_df(df)
	
	if 'Sample' not in filtered_df.columns:
		return 
	
	descriptor_columns = (col for col in filtered_df.columns if col != 'Sample')
	
	for descriptor_column in descriptor_columns:
		create_descriptors(filtered_df, 'Sample', descriptor_column, exp_obj)
	
	
