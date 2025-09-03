# -*- coding: utf-8 -*-
import pandas as pd
import numpy as np
import datetime as dt
from dateutil.relativedelta import relativedelta as rd
from .api import quantim

class alm(quantim):
    def __init__(self, username, password, secretpool, env="pdn", api_url=None):
        super().__init__(username, password, secretpool, env, api_url)
        self.default_params = {}

    def assets(self, client_id, port_type, subgroup=None, params=None, views=None):
        '''
        Assets summary.
        '''
        data = {'client_id':client_id , 'port_type': port_type, 'subgroup':subgroup, 'params':params , 'views': views}

        try:
            resp = self.api_call('assets', method="post", data=data, verify=False)
        except Exception as e:
            raise ValueError(f"Error: {str(e)}")

        assets_summ, assets_real_rets, assets_series = pd.DataFrame(resp['assets_summ']),pd.DataFrame(resp['assets_real_rets']), pd.DataFrame(resp['assets_series'])
        assets_summ = assets_summ.loc[np.in1d(assets_summ.Activo, resp['ref_assets'])]
        print(resp['info']['rets'])

        return assets_summ, assets_real_rets, assets_series

    def saa_alm(self, client_id, port_type, subgroup=None, params=None, views=None, ref_date=None):
        '''
        Saa
        '''
        data = {**{'client_id':client_id, 'port_type':port_type,'subgroup':subgroup, 'port_form':params, 'views':views}, **({'ref_date':ref_date} if ref_date is not None else {})}

        try:
            resp = self.api_call('saa_alm', method="post", data=data, verify=False)
        except Exception as e:
            raise valueError(f"Error: {str(e)}")

        ports_summ = pd.DataFrame(resp['port_summ']).set_index(['id'])
        ports_alloc = pd.DataFrame(resp['portfolios']['data'], index=resp['portfolios']['index'], columns=resp['portfolios']['columns'])
        risk_matrix = pd.DataFrame(resp['Rho']).set_index('Variables')

        return ports_alloc, ports_summ, risk_matrix