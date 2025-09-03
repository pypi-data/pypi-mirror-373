# -*- coding: utf-8 -*-
from .api import quantim

class credit_data(quantim):
    def __init__(self, username, password, secretpool, env="pdn", api_url=None):
        super().__init__(username, password, secretpool, env, api_url)

    def load_monitor(self, file_path, market="public"):
        '''
        Load monitor file to s3.
        '''
        # Validate filename:
        if file_path.split('/')[-1].split('.')[-1]!='csv':
            raise ValueError('Extension must be csv. Please check file.')

        if market.lower()=="public":
            filename = "monitor_credito.csv" 
        elif market.lower()=="private":
            filename = "monitor_credito_dp.csv"
        else:
            raise ValueError("Market not supported")       

        resp = self.upload_with_presigned_url(file_path, "condor-credit", f"output/monitor/{filename}")
        return resp
