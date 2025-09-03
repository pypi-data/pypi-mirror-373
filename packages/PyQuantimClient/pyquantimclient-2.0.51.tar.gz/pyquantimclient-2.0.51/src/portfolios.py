# -*- coding: utf-8 -*-
import pandas as pd
import numpy as np
import datetime as dt
import requests, io
from .api import quantim

class portfolios(quantim):
    def __init__(self, username, password, secretpool, env="pdn", api_url=None):
        super().__init__(username, password, secretpool, env, api_url)

    def get_portfolios(self, ref_date=None, country=None, fields=None, port_names=None, clean=False, mv_to_usd=False):
        '''
        Query portfolios from database.

        Parameters:
        ----------
        ref_date : String
            Portfolios data in format %Y-%m-%d (default None)
        country : Array of Strings
            Country code [CO, CL, MX] (default None)
        fields : Array
            Array of fields (default None)
        port_names : Array
            Array of portfolios names (default None)
        clean : bool
            Indicator thar removes empty columns (default False)

        Returns:
        -------
        : pandas.DataFrame
        '''

        if (country is None or  len(country)==0) and port_names is None:
            raise ValueError('Either country or port_names must be different to None.')

        data = {'date':ref_date, 'country':country, 'fields':fields, 'port_names':port_names, 'clean':clean, 'mv_to_usd':mv_to_usd, 'res_url':True}
        ports_url = self.api_call('query_portfolios', method="post", data=data, verify=False)
        ports_data = requests.get(ports_url, verify=False)
        ports_df = pd.read_csv(io.StringIO(ports_data.content.decode('utf-8-sig')), sep='|')

        return ports_df

    def get_portfolios_views(self, ref_date=None, country=None, port_names=None, asset=None):
        '''
        Get portfolio views
        '''
        if country is None and port_names is None:
            raise ValueError('Either country or port_names must be different to None.')
        data = {'date':ref_date, 'country':country, 'port_names':port_names, 'asset':asset}
        resp = self.api_call('query_portfolios_views', method="post", data=data, verify=False)
        ports_df = pd.DataFrame(resp)

        return ports_df

    def metrics(self, country=None, funds=None, ref_date=None, per="monthly", range_in_months=[12, 24], total_rets_per=['YTD', '1D', '1W', '2W', '1M', '3M', '6M', '1Y', '3Y', '5Y']):
        '''
        port_metrics service
        '''
        if country is None and funds is None:
            raise ValueError("Both country and funds cannot be None")
        data = {'country':country, "funds":funds, "per":per, "range_in_months":range_in_months, 'total_rets_per':total_rets_per, 'ref_date':ref_date}
        resp = self.api_call('port_metrics', method="post", data=data, verify=False)
        absolute_risk, relative_risk, real_rets = pd.DataFrame(resp['absolute_risk']), pd.DataFrame(resp['relative_risk']), pd.DataFrame(resp['real_rets'])

        series_df = pd.DataFrame(None)
        for k in resp['series'].keys():
            series_df = pd.concat([series_df, pd.DataFrame(resp['series'][k]).set_index('date')], axis=1)
        return absolute_risk, relative_risk, real_rets, series_df

    def series(self, country=None, funds=None, ref_date=None, keep_gross=False, filter_peers=False):
        '''
        port_series service
        '''
        if country is None and funds is None:
            raise ValueError("Both country and funds cannot be None")
        data = {'country':country, "funds":funds, 'ref_date':ref_date, 'keep_gross':keep_gross, "filter_peers":filter_peers}
        resp = self.api_call('port_series', method="post", data=data, verify=False)
        series_df = pd.DataFrame(resp).set_index('Date')
        series_df.index = pd.to_datetime(series_df.index)
        series_df = series_df.apply(pd.to_numeric, errors='coerce')
        
        return series_df

    def attribution(self, port_name, ref_curr,  ref_date=None, subgroup=None, bench_name=None, port_to_index=True, per='monthly', ini_date=None, rebal_dates_db=False, rebal_period='quarterly', sync_rebal_dates=False, reset_weights=True, backtest_assets=None, vol_model={"name":"ewma", "alpha":0.01}, delta_w=0.01, quant=0.95, var_normal=True, counter_assets=None, filter_market_val=False, dur_contrib_field='Duration', retrieve_returns=False, lookthrough=False):
        '''
        Portfolio risk and return attribution and contribution.

        Parameters:
        ----------
        port_name : str
            Portfolio name
        ref_curr : str
            Currency code
        ref_date : str
            Portfolio date in format %Y-%m-%d (default None)
        bench_name : str
            Benchmark name (default None)
        port_to_index : bool
            Indicates if portfolio positions must be mapped to indices (default True)
        per : str
            Returns period (default monthly)
        ini_date : str
            Initial backtest date in format %Y-%m-%d (default 2013-01-01)
        rebal_date_db : bool
            Indicates if benchmarks must be retrieved from database (default False)
        rebal_period : str
            Rebalancing period (default quarterly)
        sync_rebal_dates : bool
            Indicates if rebalancing dates need to be syncronized (default False)
        reset_weights : bool
            Indicates if weights are reseted at ini_date (default True)
        backtest_assets : Dict
            Funds or other instrument to execute backtest (default None)
        vol_model : Dict   
            Volatility model. Name and parameters  
        delta_w : float
            Volatility model. name and parameters (default 0.01) 
        counter_assets : array
            List of assets to finance asset overweight to estimate marginal risk contributions (default None)
        quant : float
            Probability quantile to estimate VaR (default 0.95)
        var_normal : bool
            Indicates if Value at Risk is estimated assuming normal distribution (default True)
        filter_market_val : bool
            Indicates if portfolio should be filtered by marketValuationMethod field (default False)
        dur_contrib_field : str
            Duration field name (default Duration)

        Returns:
        -------
        ref_dates : Array
            Reference dates
        tr_contrib : pd.DataFrame
            Portolio and benchmark total return contribution
        tra_asset : pd.DataFrame
            Total return attribution per asset
        tra_assetclass : pd.DataFrame
            Total return attribution per asset class
        port_risk_contrib : pd.DataFrame
            Portfolio risk contribution
        bench_risk_contrib : pd.DataFrame
            Benchmark risk contribution
        risk_attrib : pd.DataFrame
            Risk attribution
        '''

        data = {"port_name":port_name, "date":ref_date, "subgroup":subgroup, "bench_name":bench_name, "ref_curr": ref_curr,"port_to_index":port_to_index,"per":per, "ini_date":ini_date,"rebal_dates_db": rebal_dates_db,"rebal_period":rebal_period,"sync_rebal_dates":sync_rebal_dates,"reset_weights": reset_weights,"backtest_assets": backtest_assets,"vol_model":vol_model,"delta_w":delta_w,"quant":quant,"var_normal":var_normal,"counter_assets":counter_assets, "filter_market_val":filter_market_val, "dur_contrib_field":dur_contrib_field, "retrieve_returns":retrieve_returns, "lookthrough":lookthrough}
        resp = self.api_call('port_attribution', method="post", data=data, verify=False)
        port_date, ref_dates, tr_contrib, tra_asset, tra_assetclass, port_risk_contrib, bench_risk_contrib, risk_attrib = resp['port_date'], resp['dates'], pd.DataFrame(resp['tr_contrib']), pd.DataFrame(resp['tra_asset']), pd.DataFrame(resp['tra_assetclass']), pd.DataFrame(resp['port_risk_contrib']), pd.DataFrame(resp['bench_risk_contrib']), pd.DataFrame(resp['risk_attrib'])
        port_rets = pd.DataFrame(resp['port_rets']).set_index('date') if resp.get('port_rets', None) is not None else None 
        return port_date, ref_dates, tr_contrib, tra_asset, tra_assetclass, port_risk_contrib, bench_risk_contrib, risk_attrib, port_rets

    def backtest(self, port_name, ref_curr,  ref_date=None, bench_name=None, ini_date=None, rebal_dates_db=False, rebal_period='quarterly', sync_rebal_dates=False):
        '''
        Portfolio risk and return attribution and contribution.

        Parameters:
        ----------
        port_name : str
            Portfolio name
        ref_curr : str
            Currency code
        ref_date : str
            Portfolio date in format %Y-%m-%d (default None)
        bench_name : str
            Benchmark name (default None)
        ini_date : str
            Initial backtest date in format %Y-%m-%d (default 2013-01-01)
        rebal_date_db : bool
            Indicates if benchmarks must be retrieved from database (default False)
        rebal_period : str
            Rebalancing period (default quarterly)
        sync_rebal_dates : bool
            Indicates if rebalancing dates need to be syncronized (default False)

        Returns:
        -------
        ref_dates : Array
            Reference dates
        tr_contrib : pd.DataFrame
            Portolio and benchmark total return contribution
        tra_asset : pd.DataFrame
            Total return attribution per asset
        tra_assetclass : pd.DataFrame
            Total return attribution per asset class
        series: pd.DataFrame
            Simulated series
        '''

        data = {"port_name":port_name, "date":ref_date, "bench_name":bench_name, "ref_curr": ref_curr, "ini_date":ini_date,"rebal_dates_db": rebal_dates_db,"rebal_period":rebal_period,"sync_rebal_dates":sync_rebal_dates,"reset_weights": True}
        resp = self.api_call('port_backtest', method="post", data=data, verify=False)
        ref_dates, port_date, bench_date, tr_contrib, tra_asset, tra_assetclass, series = resp['dates'], resp['port_date'], resp['bench_date'], pd.DataFrame(resp['tr_contrib']), pd.DataFrame(resp['tra_asset']) if resp['tra_asset'] is not None else None, pd.DataFrame(resp['tra_assetclass']) if resp['tra_assetclass'] is not None else None, pd.DataFrame(resp['series']).set_index('fecha')
        series.index = pd.to_datetime(series.index)     
        return ref_dates, port_date, tr_contrib, tra_asset, tra_assetclass, series
