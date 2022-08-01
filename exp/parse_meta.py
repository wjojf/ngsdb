import pandas as pd 
import exp.models as exp_models


COLUMNS = {
	'conditions': ['cond', 'condition']
}


def match_column(column_name: str):
	#
	#	Matches a DataFrame column with 
	#	Experiment object field
	
	# 	returns: tuple (exp_field, True) / (None, False) if not found
 
	# Example: column_name = 'Condition1'
	# 	returns ('conditions', True)

	global COLUMNS

	for col in COLUMNS:
		if any((column_name.lower().strip() in col_example for col_example in COLUMNS[col])):
			return (col, True)
	return (None, False)


def filter_df(df):
	#
	#	Filters DataFrame: keep only columns where match_column(column)
	#

	valid_columns = [col for col in df.columns in match_column(col)]
	return df[valid_columns]
	


