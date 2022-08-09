from venv import create
import pandas as pd 
import exp.models as exp_models


EXPERIMENT_DESCRIPTOR_COLUMNS = {
	'Descriptor': ['sample', 'sample_id', 'sample id', 'sampleid'],
	'DescriptorValue': ['cond', 'condition', 'cond1', 'cond 1', 'condition1', 'condition 1'],
	'DescriptorValue2': ['cond2', 'cond 2', 'condition 2', 'condition2']
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
	return df


def match_column(column_name: str):
	global EXPERIMENT_DESCRIPTOR_COLUMNS
	#	Matches a DataFrame column with 
	#	DescriptorMap object
	
	# 	returns: tuple (exp_field, True) / (None, False) if not found
 
	# Example: column_name = 'Condition1'
	# 	returns ('conditions', True)
	matched_columns = {}

	for descriptor_col in EXPERIMENT_DESCRIPTOR_COLUMNS:
		if any(
			(column_name.lower().strip() == col_example
			 for col_example in EXPERIMENT_DESCRIPTOR_COLUMNS[descriptor_col])
		):
			matched_columns = {column_name: descriptor_col}
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


def create_descriptors(df, desc_name_column, desc_val_column, content_type, obj_id):
	# Creates DescriptorMap objects from DataFrame
	# df - DataFrame with at least two columns ('Descriptor' & 'DescriptorValue')
	# desc_name_column: str:  column containing descriptor names
	# desc_val_column: str: column containing descriptor values
	# content_type: ContentType object for DescriptorMap 
	# obj_id: int object_id for DescriptorMap object 

	
	if (desc_name_column not in df.columns) or (desc_val_column not in df.columns):
		return 
	

	for desc_name, desc_value in zip(df[desc_name_column], df[desc_val_column]):
		
		desc_name = str(desc_name)
		desc_value = str(desc_value)
  
		descriptor_obj, desc_created = exp_models.Descriptor.objects.get_or_create(
			name=desc_name.lower().strip()
		)

		
		desc_value_obj, desc_val_created = exp_models.DescriptorValue.objects.get_or_create(
			descriptor=descriptor_obj,
			value=desc_value.lower().strip()
		)



		descriptormap_obj, descmap_created = exp_models.DescriptorMap.objects.get_or_create(
			desc_name=descriptor_obj,
			desc_value=desc_value_obj,
			content_type=content_type,
			object_id=obj_id
		)


									#################
									# Main Function #
									#################


def _parse_meta(content, obj_id, content_type):
    
 
    df = load_df_from_content(content)

    filtered_df = filter_df(df)

    descriptor_value_columns = [col for col in filtered_df.columns if 'DescriptorValue' in col]

    
    for descriptor_value_column in descriptor_value_columns:
        create_descriptors(filtered_df, 'Descriptor', descriptor_value_column, content_type, obj_id)
