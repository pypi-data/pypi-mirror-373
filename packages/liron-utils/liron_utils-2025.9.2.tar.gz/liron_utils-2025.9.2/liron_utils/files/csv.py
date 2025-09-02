import pandas as pd
from .. import uncertainties_math as un

load_csv = pd.read_csv


def load_csv_to_dict(file, *args, **kwargs) -> dict:
	table = pd.read_csv(file, *args, **kwargs)

	d = dict()
	for column in table.columns:
		d[column] = table[column].to_numpy()

	return d


def load_csv_to_dict_with_uncertainties(file, dev_str_identifier=" dev", *args, **kwargs) -> dict:
	d = load_csv_to_dict(file, *args, **kwargs)
	d_uncertainties = dict()

	for key in d.keys():
		if key.endswith(dev_str_identifier):
			key_wo_dev = key.split(dev_str_identifier)[0]
			d_uncertainties[key_wo_dev] = un.unumpy.uarray(d[key_wo_dev], d[key])

	return d_uncertainties
