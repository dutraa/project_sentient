import pandas as pd
import tensorflow as tf
from alpha_vantage.techindicators import TechIndicators
from alpha_vantage.timeseries import TimeSeries
import requests
import json
import time

# import dash
# import dash_core_components as dcc
# import dash_html_components as html
# from dash.dependencies import Input, Output
# import flask

# import plotly.graph_objs as go
# from numba import jit
# from datetime import date

API_KEY = '7C55TUKVWYOC48V6'
SYMBOL = 'MSFT'
LEN = 5245
SYMBOL = SYMBOL.rstrip()



base_url = 'https://www.alphavantage.co/query?'
function_query_string = 'function='
symbol_query_string = 'symbol='
market_query_string = 'market='
api_key_query_string = 'apikey='
datatype_query_string = 'datatype='
interval_query_string = 'interval='
time_period_query_string = 'time_period='
series_type_query_string = 'series_type='

def build_request_string(**request_params):
	request_url = base_url
	for param, value in request_params.items():
		request_url+=(param+'='+str(value)+'&')
	request_url+=('apikey='+API_KEY)
	return request_url

# print(requests.get(build_request_string(function='EMA', symbol='MSFT', interval='daily', time_period='6', series_type='open')).text)

def get_techindicator_data(**request_params):
	ti_dict = {request_params['function']:[]}
	request_url = build_request_string(**request_params)
	request_data = json.loads((requests.get(request_url)).text)
	ti_data = request_data['Technical Analysis: '+request_params['function']]
	for date in ti_data:
		ti_dict[request_params['function']].append(ti_data[date][request_params['function']])
	df_ti = pd.DataFrame(ti_dict)
	return df_ti.tail(LEN).reset_index(drop=True)

def get_time_series_data(**request_params):
	ts_dict = {}
	request_params_for_time_series = {}
	request_params_for_time_series['function'] = request_params['function']
	request_params_for_time_series['symbol'] = request_params['symbol']
	request_params_for_time_series['outputsize'] = 'full'
	request_url = build_request_string(**request_params_for_time_series)
	request_data = json.loads((requests.get(request_url)).text)
	ts_data = request_data['Time Series (Daily)']
	for date in ts_data:
		for key in ts_data[date]:
			if key not in ts_dict:
				ts_dict[key] = []			
			ts_dict[key].append(ts_data[date][key])	
	df_ts = pd.DataFrame(ts_dict)
	return df_ts.tail(LEN).reset_index(drop=True)		



def get_final_df(*frames):
	return pd.concat(frames, axis=1, ignore_index=True)


# request_data = requests.get(build_request_string(function='EMA', symbol='MSFT', interval='daily', time_period='6', series_type='open')).text

mean_based_tech_indicators = ['EMA', 'SMA', 'WMA', 'DEMA', 'TEMA', 'TRIMA', 'KAMA', 'T3', 'RSI', 'WILLR', 'ADX', 'ADXR', 'MOM']

def create_data_for_train_test(*indicators, **request_params):
	frames = []
	for indicator in indicators:
		if indicator=='TRIMA' or indicator=='ADX':
			time.sleep(90)
		request_params['function'] = indicator
		print(request_params)
		frame = get_techindicator_data(**request_params)
		frames.append(frame)
	request_params['function'] = 'TIME_SERIES_DAILY'	
	frames.append(get_time_series_data(**request_params))	
	return get_final_df(*frames)
	

dataframe = create_data_for_train_test('EMA', 'SMA', 'WMA', 'DEMA', 'TEMA', 'TRIMA', 'KAMA', 'T3', 'RSI', 'WILLR', 'ADX', 'ADXR', 'MOM', function='EMA', symbol='JNJ', interval='daily', time_period='6', series_type='close')	

dataframe.head(4196).to_csv('fintech_data_train.csv', index=False)
dataframe.tail(1049).to_csv('fintech_data_test.csv', index=False)