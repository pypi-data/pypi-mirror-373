# -*- coding: utf-8 -*-
import pandas as pd
import numpy as np
import datetime as dt
from .api import quantim

class time_series(quantim):
    def __init__(self, username, password, secretpool, env="pdn", api_url=None):
        super().__init__(username, password, secretpool, env, api_url)

    def get_series(self, tks, ref_curr='Origen', join='outer', since_date='2008-01-01', verify=False):
        '''
        Get series
        '''
        res_url = True if len(tks)>10 else False
        data = {'tks':list(tks), 'ref_curr':ref_curr, 'join':join, 'since_date':since_date, 'res_url':res_url}
        resp = self.api_call('get_series', method="post", data=data, verify=verify)
        summ, tks_invalid = pd.DataFrame(resp['summ']), resp['tks_invalid']
        if res_url:
            ts = pd.read_csv(resp['ts']).set_index("Date")
        else:
            ts = pd.DataFrame(resp['ts']).set_index("Date")
        return ts, summ, tks_invalid

    def clustering(self, tks, ref_curr='USD', ini_date=None, cluster_method='graph', ncluster=None, factor_tickers=None, use_pca=True, verify=False):
        """
        Perform clustering on financial assets/variables. 
        
        This function clusters financial assets based on historical returns. The clustering method can be selected from dendrogram-based, graph-based, or factorial analysis.

        Parameters
        ----------
        tks : list
            List of tickers (financial assets) to be clustered.
        ref_curr : str, optional
            Reference currency (ISO Code) for calculating returns, default is 'USD'.
        ini_date : str, optional
            Initial date for the time series data in 'YYYY-MM-DD' format, default is None (uses all available data).
        cluster_method : str, optional
            Clustering approach to use. Options are:
            - 'dendrogram': Hierarchical clustering using a dendrogram.
            - 'graph': Network-based clustering using correlation-based graph structures (default).
            - 'factorial': Clustering based on third variables.
        n_cluster : int, optional
            Number of clusters to form. Only applies if method is dendrogram.
        factor_tickers: list, optional
            List of tickers of third variables used to cluster original tks.
        use_pca: bool
            Performs a PCA transformation on the tickers returns, and use the principal components to build clusters. Ony applies when method is 'dendrogram'. 

        Returns
        -------
        clusters : pd.Series
            Series containing tickers and their corresponding cluster identifiers.
        rets_summ : pd.DataFrame
            Summary table with risk and return metrics for each ticker.
        invalid_tickers : list
            List of tickers that were invalid (e.g., no available data).
        valid_dates : list
            List of valid dates for which all tickers have data.
        factors : pd.DataFrame or None
            Table with factor coefficients for each ticker when using the 'factorial' method.
            Returns None if 'factorial' clustering is not selected.
        """
        if cluster_method.lower()[:3]!='gra' and ncluster is None:
            raise ValueError('Please provide number of clusters (ncluster)')

        data = {'ref_curr':ref_curr, 'ini_date':ini_date, 'ncluster':ncluster, 'tickers':tks, 'factor_tickers':factor_tickers, 'cluster_method':cluster_method, 'use_pca':use_pca}
        resp = self.api_call('clustering', method="post", data=data, verify=verify)
        clusters, rets_summ, invalid_tickers, valid_dates, factors = pd.Series(resp['clusters']), pd.DataFrame(resp['rets_summ']), resp['invalid_tickers'], resp['valid_dates'], pd.DataFrame(resp['factors']) if resp['factors'] is not None else None
        return clusters, rets_summ, invalid_tickers, valid_dates, factors

class s3(quantim):
    def __init__(self, username, password, secretpool, env="pdn", api_url=None):
        super().__init__(username, password, secretpool, env, api_url)

    def read_file(self, bucket, key, sep=',', verify=False, res_url=False):
        '''
        Get series
        ''' 
        data = {'bucket':bucket, 'key':key, 'sep':sep, 'res_url':res_url}
        resp = self.api_call('retrieve_data_s3', method="post", data=data, verify=verify)

        if res_url:
            output = resp
        else:
            output = pd.DataFrame(resp)
        return output