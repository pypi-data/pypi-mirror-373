# -*- coding: utf-8 -*-
import io, re
import datetime as dt
import requests
import pandas as pd
import numpy as np
from .api import quantim

class performance(quantim):
    def __init__(self, username, password, secretpool, env="pdn", api_url=None):
        super().__init__(username, password, secretpool, env, api_url)

    def load_gaps(self, file_path):
        '''
        Load gaps.
        '''
        # Load data
        filename = re.split(r'[\\/]', file_path)[-1]
        bucket = "condor-sura-wm"
        key = f"taa/gaps/{filename}" 
        resp = self.upload_with_presigned_url(file_path, bucket, key)
        print("File uploaded!" if resp else "File cannot be uploaded!")
        if not resp:
            return
        
        # Insert to DB
        data = {'bucket':bucket, 'key':key}
        res_insert = self.api_call('load_gaps', method="post", data=data, verify=False)
        inserted_in_db, not_inserted_in_db = pd.DataFrame(res_insert['inserted_in_db']), pd.DataFrame(res_insert['not_inserted_in_db'])
        
        return inserted_in_db, not_inserted_in_db

