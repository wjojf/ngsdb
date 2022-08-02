import pandas as pd 
import exp.models as exp_models


EXPERIMENT_DESCRIPTOR_COLUMNS = {
	'Descriptor': ['sample'],
	'DescriptorValue': ['cond', 'condition']
}

# Sample Cond                    Descriptor   DescriptorValue
# ig01	 L1							ig01	 L1
# ig02	 L2			-----> 			...      ...
# ig03	 L3							...      ...
# ig04	 L4							...      ...
# ig05   L5							ig05      L5


def load_df_from_content(content, delimeter='\n'):
	return pd.DataFrame(content.read().split(delimeter))


def match_column(column_name: str):
	global EXPERIMENT_DESCRIPTOR_COLUMNS
	#	Matches a DataFrame column with 
	#	DescriptorMap object
	
	# 	returns: tuple (exp_field, True) / (None, False) if not found
 
	# Example: column_name = 'Condition1'
	# 	returns ('conditions', True)
	matched_columns = {}

	for descriptor_col in EXPERIMENT_DESCRIPTOR_COLUMNS:
		if any((column_name.lower().strip() in col_example for col_example in EXPERIMENT_DESCRIPTOR_COLUMNS[descriptor_col])):
			matched_columns = {column_name: descriptor_col}
			break
	
	return matched_columns


def filter_df(df):
	# FIXME: how to handle multiple Conditions columns?
	#	Filters DataFrame: 
	# keep only columns where match_column(column) is not empty and renames columns
	matched_columns = [match_column(col) for col in df.columns if match_column(col) != {}]
	rename_columns = {}
	for matched_column in matched_columns:
		rename_columns.update(matched_column)

	filtered_df = df.rename(columns=rename_columns)
	valid_columns = [col for col in filtered_df.columns if col in EXPERIMENT_DESCRIPTOR_COLUMNS]
	
	return filtered_df[valid_columns]


def create_descriptors(df, content_type, obj_id):
	# TODO: 
	# Creates DescriptorMap objects
	# df: DataFrame with columns ('Descriptor', 'DescriptorValue')
	pass 


