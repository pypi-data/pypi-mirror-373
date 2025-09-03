# -*- coding: utf-8 -*-
import pandas as pd
from .api import quantim

class product_data(quantim):
    def __init__(self, username, password, secretpool, env="pdn", api_url=None):
        super().__init__(username, password, secretpool, env, api_url)

    def get_returns_report_cl(self, ref_date):
        '''
        Retrive products returns report for clients in CL.
        '''
        filename = f"prices_cl/{ref_date.replace('-','/')}/rentabilidades.csv"
        try:
            url = self.retrieve_s3_df(bucket="condor-reporting", key=filename, res_url=True)
            df = pd.read_csv(url, sep="|")
            print(f'Reporte cargado!')
        except:
            print(f"Reporte no disponible para {ref_date}!")
            df = None
        return df
