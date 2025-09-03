# -*- coding: utf-8 -*-
import re, os
import datetime as dt
from dateutil.relativedelta import relativedelta as rd
import pandas as pd
import numpy as np
from .api import quantim

class bi_data(quantim):
    def __init__(self, username, password, secretpool, env="pdn", api_url=None):
        super().__init__(username, password, secretpool, env, api_url)

    def get_positions_afps_cl(self, ref_date=None):
        '''
        Get Value at Risk results and suport information.
        '''
        ref_date = dt.datetime.today().replace(day=1, hour=0, minute=0, second=0, microsecond=0) - rd(days=1) if ref_date is None else dt.datetime.strptime(ref_date, '%Y-%m-%d') 
        key = f'inputs/benchmarks/positions/cl/afps/{ref_date.year}/{ref_date.strftime("%m")}/data.json'
        data = {'bucket':"condor-sura", 'key':key}
        try:
            resp = self.api_call('retrieve_json_s3', method="post", data=data, verify=False)
            keys = list(resp.keys())
            resp_dfs = {k:pd.DataFrame(resp[k]) for k in keys}
        except:
            print(f"Data not available for {ref_date}. Try previous month!")
            keys, resp_dfs = None, None
        return keys, resp_dfs

    def process_positions_afps_cl(self, keys=None, resp_dfs=None, ref_date=None):
        if keys is None or resp_dfs is None:
            keys, resp_dfs = self.get_positions_afps_cl(ref_date=ref_date)

        asset_class_df = resp_dfs['CARTERA AGREGADA DE LOS FONDOS DE PENSIONES POR TIPO DE FONDO'].set_index('glosa')
        asset_class_df['index'] = [k.replace('tipofondo -', '').strip() for k in asset_class_df['index'].values]
        asset_class_df = asset_class_df.loc[np.in1d(asset_class_df['index'], ['A', 'B', 'C', 'D', 'E'])]

        consol_df = pd.DataFrame()
        acc_map = [{'id':'SUBTOTAL RENTA VARIABLE', 'label':'Renta Variable'},
                {'id':'SUBTOTAL RENTA FIJA', 'label':'Renta Fija'},
                {'id':'SUBTOTAL DERIVADOS', 'label':'Derivados'},
                {'id':'SUBTOTAL OTROS', 'label':'Otros'},
                    ]
        for x in acc_map:
            consol_df = pd.concat([consol_df, asset_class_df.loc[x['id']].set_index('index')[['porcentaje']].rename(columns={'porcentaje':x['label']}).T], axis=0)

        asset_class_df.loc[x['id']].set_index('index')[['porcentaje']].rename(columns={'porcentaje':x['label']}).T
        asset_class_df.loc[[k for k in  asset_class_df.index if re.search('^RENTA VARIABLE', k) is not None]]

        inv_nac_loc = np.where([k.startswith('INVERSIÓN NACIONAL TOTAL') for k in asset_class_df.index])[0][0]
        inv_inter_loc = np.where([k.startswith('INVERSIÓN EXTRANJERA TOTAL') for k in asset_class_df.index])[0][0]
        rv_loc = np.where([True if re.search('^RENTA VARIABLE', k) is not None else False for k in  asset_class_df.index])[0]
        rf_loc = np.where([True if re.search('^RENTA FIJA', k) is not None else False for k in  asset_class_df.index])[0]

        # RV and RF Local and Inter
        consol_df = pd.concat([consol_df, 
                            asset_class_df.iloc[rv_loc[(rv_loc>inv_nac_loc) & (rv_loc<inv_inter_loc)]].set_index('index')[['porcentaje']].rename(columns={'porcentaje':'Renta Variable Nacional'}).T, 
                            asset_class_df.iloc[rv_loc[(rv_loc>inv_inter_loc)]].set_index('index')[['porcentaje']].rename(columns={'porcentaje':'Renta Variable Internacional'}).T, 
                            asset_class_df.iloc[rf_loc[(rf_loc>inv_nac_loc) & (rf_loc<inv_inter_loc)]].set_index('index')[['porcentaje']].rename(columns={'porcentaje':'Renta Fija Nacional'}).T, 
                            asset_class_df.iloc[rf_loc[(rf_loc>inv_inter_loc)]].set_index('index')[['porcentaje']].rename(columns={'porcentaje':'Renta Fija Internacional'}).T
                            ], axis=0) 
        consol_df = consol_df.reset_index().rename(columns={'index':'Clase de Activo'})
        columnas = ['A', 'B', 'C', 'D', 'E']
        consol_df[columnas] = consol_df[columnas].apply(pd.to_numeric)

        # Por emisor
        asset_detail_df = resp_dfs['CARTERA DE LOS FONDOS DE PENSIONES POR TIPO DE FONDO, INVERSIÓN EN EL EXTRANJERO POR EMISOR'].fillna({'nemo':''})
        asset_detail_df['index'] = [k.replace('tipofondo -', '').strip() for k in asset_detail_df['index'].values]
        asset_detail_df = asset_detail_df.loc[np.in1d(asset_detail_df['index'], ['A', 'B', 'C', 'D', 'E'])]
        asset_detail_df = asset_detail_df.groupby(['index', 'nemo', 'glosa']).sum().reset_index(level='index').pivot(columns='index', values='monto_dolares').reset_index()

        # Por region
        region_df = resp_dfs["INVERSION EN EL EXTRANJERO DEL LOS FONDOS DE PENSIONES, DIVERSIFICACION POR TIPO DE FONDO Y ZONA GEOGRAFICA"]
        columnas = ["monto_dolares", "porcentaje", "porcentaje_sobre_extranjero"]
        region_df[columnas] = region_df[columnas].apply(pd.to_numeric)

        region_df['index'] = region_df['index'].str.replace('tipofondo -', '').str.strip()
        region_df = region_df.loc[np.in1d(region_df['index'], ['A', 'B', 'C', 'D', 'E'])]

        region_df = region_df.groupby(['index', 'glosa']).sum().reset_index(level='index')
        region_df = region_df.pivot(columns='index', values='monto_dolares').reset_index()

        columnas = ['A', 'B', 'C', 'D', 'E']
        indice = region_df['glosa'].tolist().index('TOTAL INVERSION EN EL EXTRANJERO')

        for columna in columnas:
            divisor = region_df[columna].iloc[indice]
            region_df[columna] = region_df[columna] / divisor
            rvi = consol_df.loc[consol_df['Clase de Activo'] == 'Renta Variable Internacional', columna].iloc[0]
            rfi = consol_df.loc[consol_df['Clase de Activo'] == 'Renta Fija Internacional', columna].iloc[0]
            region_df[columna] = region_df[columna] * (rvi + rfi)

        region_df = region_df.rename(columns={"glosa": "Clase de Activo"})
        region_df[columnas] = round(region_df[columnas], 2)

        # Consolidado
        final_df = pd.concat([consol_df, region_df], axis=0)
        final_df = final_df[final_df["Clase de Activo"] != "TOTAL INVERSION EN EL EXTRANJERO"]

        # Resultado
        asset_class = final_df[final_df['Clase de Activo'].isin(['Renta Fija', 'Renta Variable', 'Derivados', 'Otros'])]
        asset_class.set_index('Clase de Activo', inplace=True)
        suma = asset_class.sum(axis=0)
        asset_class.loc['TOTAL'] = suma

        renta_fija = final_df[final_df['Clase de Activo'].isin(['Renta Fija Nacional', 'Renta Fija Internacional'])]
        renta_fija.set_index('Clase de Activo', inplace=True)
        suma = renta_fija.sum(axis=0)
        renta_fija.loc['RENTA FIJA'] = suma

        renta_variable = final_df[final_df['Clase de Activo'].isin(['Renta Variable Nacional', 'Renta Variable Internacional'])]
        renta_variable.set_index('Clase de Activo', inplace=True)
        suma = renta_variable.sum(axis=0)
        renta_variable.loc['RENTA VARIABLE'] = suma

        paises_emergentes = final_df[final_df['Clase de Activo'].isin(['ASIA EMERGENTE', 'EUROPA EMERGENTE', 'LATINOAMERICA', 'MEDIO ORIENTE-AFRICA'])]
        paises_emergentes.set_index('Clase de Activo', inplace=True)
        suma = paises_emergentes.sum(axis=0)
        paises_emergentes.loc['PAISES EMERGENTES'] = suma

        paises_desarrollados = final_df[final_df['Clase de Activo'].isin(['NORTEAMERICA', 'ASIA PACIFICO DESARROLLADA', 'EUROPA'])]
        paises_desarrollados.set_index('Clase de Activo', inplace=True)
        suma = paises_desarrollados.sum(axis=0)
        paises_desarrollados.loc['PAISES DESARROLLADOS'] = suma

        otros = final_df[final_df['Clase de Activo'].isin(['OTROS'])]
        otros.set_index('Clase de Activo', inplace=True)

        resultado = pd.concat([asset_class, renta_fija, renta_variable, paises_emergentes, paises_desarrollados, otros])
        resultado.reset_index(inplace=True)

        return resultado

    def get_asset_allocation(self, file, bucket="condor-sura"):
        '''
        Get Asset Allocation from Mstar.
        '''
        try:
            file_name, file_extension = os.path.splitext(file)
            prefix = f"output/morningstar_api/data/asset_allocation/{file}"
            url = self.retrieve_s3_df(bucket, prefix, res_url=True)

            if file_extension.lower() == '.csv':
                df = pd.read_csv(url)
                print(f"Archivo CSV '{file_name}' descargado correctamente.")
            elif file_extension.lower() == '.xlsx':
                df = pd.read_excel(url)
                print(f"Archivo XLSX '{file_name}' descargado correctamente.")
            else:
                print("Tipo de archivo no soportado. Por favor, escriba un archivo CSV o XLSX.")
                return None

            return df
        except Exception as e:
            print(f"Error: {e}. Archivo no disponible")
            return None
