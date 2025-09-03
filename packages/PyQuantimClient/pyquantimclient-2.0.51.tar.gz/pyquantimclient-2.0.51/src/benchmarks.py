# -*- coding: utf-8 -*-
import pandas as pd
import numpy as np
import datetime as dt
from .api import quantim

class benchmarks(quantim):
    def __init__(self, username, password, secretpool, env="pdn", api_url=None):
        super().__init__(username, password, secretpool, env, api_url)

    def load_constraints(self, file_name, sep=',', country='CO'):
        '''
        Load portfolio file to s3.
        '''
        if ~np.all(np.in1d(country, ['CO', 'CL', 'PE', 'MX', 'UY'])):
            raise ValueError('Country not supported.')

        #Retrieve data:
        data = {'bucket':'condor-sura', 'key':f'inputs/benchmarks/constraints/{country}/benchmarks_limits.csv', 'sep':sep}
        df_prev = pd.DataFrame(self.api_call('retrieve_data_s3', method="post", data=data, verify=False))

        # Read new file:
        df_new = pd.read_csv(file_name, sep=sep)

        ## Check dates:
        try:
            ref_dates = [dt.datetime.strptime(x, "%d/%m/%Y") for x in df_new.Date]
        except:
            resp = {'success':False, 'message':'Check date format (%d/%m/%Y)!'}
            return resp
        ## Check columns:
        if len(df_prev.columns)!=len(df_new.columns) or ~np.all(np.in1d(df_new.columns, df_prev.columns)):
            resp = {'success':False, 'message':'Check file columns.'}
            return resp

        ## Check duplicates dates:
        duplic_ind = np.in1d(df_new.Date, df_prev.Date)
        duplic_dates = np.unique(df_new.Date[duplic_ind])
        if np.any(~duplic_ind):
            df_consol = pd.concat([df_prev, df_new.loc[~duplic_ind]], axis=0)
        else:
            resp = {'success':False, 'message':'No new dates. Please verify dates.'}
            return resp

        #Load data
        payload = df_consol.to_dict(orient='records')
        data = {'bucket':'condor-sura', 'file_name':f'inputs/benchmarks/constraints/{country}/benchmarks_limits.csv', 'payload':payload, 'sep':sep, 'overwrite':True}
        try:
            resp = self.api_call('load_data_s3', method="post", data=data, verify=False)
        except:
            resp = {'success':False, 'message':'Check permissions!'}
        return resp
