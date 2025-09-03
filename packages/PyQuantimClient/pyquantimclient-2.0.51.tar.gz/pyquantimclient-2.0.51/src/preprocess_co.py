# -*- coding: utf-8 -*-
"""
Created on Mon Aug 08 17:30:00 2022

@author: Alejandra.Baena
"""
import numpy as np
import pandas as pd
import re
import os
import io
import boto3


def procesamiento_aseguradoras(date_port, port_name, ruta, ruta_precia, portfolioName, subGroup, portfolio_fields, mkt_value_prorrateo=None, add_rows=None):

    Tipoportafolio = re.sub('Portafolio','',port_name)
    date2 = pd.to_datetime(date_port)
    Fecha = date2.strftime('%d%m%Y')

    try:
        Precia = pd.read_excel(ruta_precia+'\\'+date2.strftime('%m%Y')+'\Renta Fija Local '+Fecha+'.xlsx')
    except:
        Precia = pd.read_excel(ruta_precia+'\\Renta Fija Local '+Fecha+'.xlsx')

    ref_date = Precia[['fecha']].drop_duplicates(['fecha'], ignore_index=True)
    ref_date = str(max(ref_date['fecha']).date())
   
    Precia.columns = Precia.columns.str.replace(u"á", "a").str.replace(u"é", "e").str.replace(u"í", "i").str.replace(u"ó", "o").str.replace(u"ú", "u")

    try:
        Preciaint = pd.read_excel(ruta_precia+'\\'+date2.strftime('%m%Y')+'\Renta Fija Internacional '+Fecha+'.xlsx')
    except:
        Preciaint = pd.read_excel(ruta_precia+'\\Renta Fija Internacional '+Fecha+'.xlsx')

    try:
        PreciaMargen = pd.read_excel(ruta_precia+'\\'+date2.strftime('%m%Y')+'\Renta Fija Margenes '+Fecha+'.xlsx')
    except:
        PreciaMargen = pd.read_excel(ruta_precia+'\\Renta Fija Margenes '+Fecha+'.xlsx')


    ColumnasPreciaint = pd.read_csv(ruta+'\Equivalencias\RFInternacional.csv', sep=';', header=0)
    ColumnasPreciaint = ColumnasPreciaint.drop_duplicates("PRECIA_LOCAL").dropna()
    ColumnasPreciainternaci = ColumnasPreciaint["PRECIA_INTERNACIONAL"].dropna().unique().tolist()
    Preciaint = Preciaint[Preciaint.columns.intersection(ColumnasPreciainternaci)]
    ColumnasPreciaint = ColumnasPreciaint["PRECIA_LOCAL"].dropna().unique().tolist()
    diasVcto = pd.read_excel(ruta+'\Equivalencias\\DIAS_AL_VENCIMIENTO.xlsx')
    dictDiasVcto = diasVcto.set_index('Banda').T.to_dict('list')

    Preciaint.columns = ColumnasPreciaint
    Preciaint['duracion'] = pd.to_numeric(Preciaint['duracion_modificada'])*(1+pd.to_numeric(Preciaint['tir'])/100)
    Precia = pd.concat([Precia, Preciaint])

    Columnas = pd.read_csv(ruta+'\Equivalencias\SABANA_INVENTARIO.csv', sep=';', header=0)
    Calificaciones = pd.read_csv(ruta+'\Equivalencias\CALIFICACIONES.csv', sep=';', header=0)
    Calificaciones = Calificaciones.astype({"CALIFICACION DEL TITULO O DEL EMISOR":"float", "CALIFICACION_PRECIA":"str", "ENTIDAD CALIFICADORA":"float"})
    coupFreq = pd.read_csv(ruta+'\Equivalencias\coupFreq.csv', sep=';', header=0)
    dateConv = pd.read_csv(ruta+'\Equivalencias\dateConv.csv', sep=';', header=0)
    Nemos = pd.read_excel(ruta+'\Equivalencias\\NEMOS-ISIN.xlsx')
    Portafolio = pd.read_excel(ruta+'\Insumos\\'+Tipoportafolio+Fecha+'.xlsx', converters={'FECHA EMISION':str, 'FECHA VENCIMIENTO':str, 'FECHA COMPRA':str})

    Portafolio = Portafolio.replace("[NULL]", np.nan)
    Indices = pd.read_csv(ruta+'\Equivalencias\TIPO_ACTIVO.csv', sep=';', header=0, usecols =["CLASE DE INVERSION","SEC GROUP","SEC TYPE","secDesc2"], encoding='mbcs')

    Portafolio.columns=Portafolio.columns.str.replace(u"Á", "A").str.replace(u"É", "E").str.replace(u"Í", "I").str.replace(u"Ó", "O").str.replace(u"Ú", "U")
    Precia.columns=Precia.columns.str.replace(u"á", "a").str.replace(u"é", "e").str.replace(u"í", "i").str.replace(u"ó", "o").str.replace(u"ú", "u")

    Columnas351=Columnas["351"].dropna().unique().tolist()
    Columnasprecia=Columnas["PRECIA"].dropna().unique().tolist()
    Portafolio=Portafolio[Columnas351]
    Precia=Precia[Columnasprecia]

    Portafolio=Portafolio.astype({"CALIFICACION DEL TITULO O DEL EMISOR":"str","ENTIDAD CALIFICADORA":"str","CLASE DE INVERSION":"str", "CLASE DE ACCIONES":"str", "NEMOTECNICO":"str"})

    Portafolio['NUMERO IDENTIFICACION ASIGNADO POR EL CUSTODIO'] = np.where(Portafolio['NUMERO IDENTIFICACION ASIGNADO POR EL CUSTODIO']=="0","NA",Portafolio['NUMERO IDENTIFICACION ASIGNADO POR EL CUSTODIO'])
    Portafolio['NUMERO IDENTIFICACION ASIGNADO POR EL CUSTODIO'] = np.where(Portafolio['NUMERO IDENTIFICACION ASIGNADO POR EL CUSTODIO'].isnull(),"NA",Portafolio['NUMERO IDENTIFICACION ASIGNADO POR EL CUSTODIO'])
    Portafolio['NEMOTECNICO'] = np.where(Portafolio['NEMOTECNICO']=="0","NA",Portafolio['NEMOTECNICO'])
    Portafolio['NEMOTECNICO'] = np.where(Portafolio['NEMOTECNICO'].isnull(),"NA",Portafolio['NEMOTECNICO'])

    # AJUSTAR ESTA LINEA CUANDO LLEGUEN NOMBRES DE PORTAFOLIOS.
    # Quemamos codigo PORTFOLIO = PATRIMONIO.
    # Portafolio['PORTAFOLIO'] = np.where(Portafolio['PORTAFOLIO']=="OBL-RETIRO","RENTAS_VITALICIAS",Portafolio['PORTAFOLIO'])
    Portafolio['CALIFICACION DEL TITULO O DEL EMISOR'] = np.where(Portafolio['CALIFICACION DEL TITULO O DEL EMISOR'].isnull(),"NA",Portafolio['CALIFICACION DEL TITULO O DEL EMISOR'])

    PortafolioDP=Portafolio[-Portafolio["CLASE DE INVERSION"].isin(["TSTF","TSUV"])]
    PortafolioDP=pd.merge(PortafolioDP, Precia, how="left", left_on='NUMERO IDENTIFICACION ASIGNADO POR EL CUSTODIO', right_on='isin')
    PortafolioTES=Portafolio[Portafolio["CLASE DE INVERSION"].isin(["TSTF","TSUV"])]
    PortafolioTES=pd.merge(PortafolioTES, Precia, how="left", left_on='NEMOTECNICO', right_on='nemo')

    Portafolio= PortafolioDP.append(PortafolioTES, ignore_index=True)
    

    Calificaciones1=Calificaciones.loc[:,["CALIFICACION DEL TITULO O DEL EMISOR","CALIFICACION EQUIV"]].drop_duplicates()
    Calificaciones1 = Calificaciones1.astype({"CALIFICACION DEL TITULO O DEL EMISOR":"str"})
    Portafolio=pd.merge(Portafolio, Calificaciones1, how="left", left_on='CALIFICACION DEL TITULO O DEL EMISOR', right_on='CALIFICACION DEL TITULO O DEL EMISOR')


    Calificaciones2=Calificaciones.loc[:,["ENTIDAD CALIFICADORA","CALIFICACION_PRECIA","CALIFICACION EQUIV", "CALIFICACION NUMERICA"]].drop_duplicates()
    Calificaciones2=Calificaciones2.astype({"ENTIDAD CALIFICADORA":"str"})
    Calificaciones2 = Calificaciones2.groupby(['CALIFICACION_PRECIA','ENTIDAD CALIFICADORA']).max().reset_index()
    Portafolio=pd.merge(Portafolio, Calificaciones2, how="left", left_on=['calificacion', 'ENTIDAD CALIFICADORA'], right_on=['CALIFICACION_PRECIA','ENTIDAD CALIFICADORA'])


    Calificaciones4=Calificaciones.loc[:,["ENTIDAD CALIFICADORA", "CALIFICACION_PRECIA","CALIFICACION NUMERICA"]].drop_duplicates()
    Calificaciones4=Calificaciones4.astype({"ENTIDAD CALIFICADORA":"str"})
    Calificaciones4=Calificaciones4[-Calificaciones4['CALIFICACION NUMERICA'].isnull()]
    Calificaciones4 = Calificaciones4.groupby(['CALIFICACION_PRECIA','ENTIDAD CALIFICADORA']).max().reset_index()
    Portafolio=pd.merge(Portafolio, Calificaciones4, how="left", left_on=['calificacion', 'ENTIDAD CALIFICADORA'], right_on=['CALIFICACION_PRECIA','ENTIDAD CALIFICADORA'])


    Calificaciones3=Calificaciones.loc[:,["ENTIDAD CALIFICADORA","ENTIDAD CALIFICADORA EQUIV","TIPO CALIFICACION"]].drop_duplicates()
    Calificaciones3=Calificaciones3.astype({"ENTIDAD CALIFICADORA":"str"})
    Portafolio=pd.merge(Portafolio, Calificaciones3, how="left", left_on='ENTIDAD CALIFICADORA', right_on='ENTIDAD CALIFICADORA')

    Portafolio=pd.merge(Portafolio, Indices, how="left", left_on='CLASE DE INVERSION', right_on='CLASE DE INVERSION')

    Portafolio['CALIFICACION EQUIV'] = np.where(Portafolio['CALIFICACION EQUIV_y'].isnull(),Portafolio['CALIFICACION EQUIV_x'],Portafolio['CALIFICACION EQUIV_y'])
    Portafolio=Portafolio.drop(['CALIFICACION EQUIV_x','CALIFICACION_PRECIA_x',"CALIFICACION_PRECIA_y",], axis=1)

    Calificaciones5=Calificaciones.loc[:,["CALIFICACION EQUIV","CALIFICACION NUMERICA"]].drop_duplicates()
    Calificaciones5=Calificaciones5[-Calificaciones5['CALIFICACION NUMERICA'].isnull()]
    Portafolio=pd.merge(Portafolio, Calificaciones5, how="left", left_on='CALIFICACION EQUIV', right_on='CALIFICACION EQUIV')


    Portafolio['TIPO CALIFICACION'] = np.where(((Portafolio['CALIFICACION NUMERICA_x'].notnull()) & (Portafolio['TIPO CALIFICACION']=="Internacional")),"Local", Portafolio['TIPO CALIFICACION'])
    # QUITAR ESTE PASO y LEER CALIFICACIONES 6 [CALIFICACION EQUIV	CALIFICACION NUMERICA
    # Portafolio['CALIFICACION NUMERICA_x'] = np.where(Portafolio['CALIFICACION NUMERICA_x'].isnull(),Portafolio['CALIFICACION NUMERICA_y'],Portafolio['CALIFICACION NUMERICA_x'])
   
    Calificaciones6=Calificaciones.loc[:,["CALIFICACION EQUIV", "CALIFICACION NUMERICA"]].drop_duplicates()
    Calificaciones6.rename(columns={'CALIFICACION NUMERICA':'CALIFICACION NUMERICA FINAL'}, inplace=True)
    Portafolio=pd.merge(Portafolio, Calificaciones6, how="left", left_on='CALIFICACION EQUIV', right_on='CALIFICACION EQUIV')
    Portafolio['CALIFICACION NUMERICA_x'] = Portafolio['CALIFICACION NUMERICA FINAL']
   
    Portafolio['CLASE DE ACCIONES'] = np.where(Portafolio['CLASE DE ACCIONES']=="1","ORD",Portafolio['CLASE DE ACCIONES'])
    Portafolio['CLASE DE ACCIONES'] = np.where(Portafolio['CLASE DE ACCIONES']=="2","PREF",Portafolio['CLASE DE ACCIONES'])

    Portafolio['CLASE DE ACCIONES'] = Portafolio['CLASE DE ACCIONES'].replace('nan', np.nan)
    Portafolio['CLASE DE ACCIONES'] = Portafolio['CLASE DE ACCIONES'].replace('0', np.nan)    

    Portafolio['secDesc2']= np.where(-Portafolio['CLASE DE ACCIONES'].isnull(),Portafolio['CLASE DE ACCIONES'],Portafolio['secDesc2'])
    Portafolio['secDesc2'] = np.where(Portafolio['secDesc2'].isnull(),"NA",Portafolio['secDesc2'])

    Portafolio['PRECIO']=np.where(Portafolio['precio'].isnull(),Portafolio['PRECIO'],Portafolio['precio'])
    Portafolio['VALOR NOMINAL RESIDUAL']=np.where(Portafolio['TASA FACIAL DEL TITULO'].isnull(),Portafolio['NUMERO ACCIONES, UNIDADES O PARTICIPACIONES'],Portafolio['VALOR NOMINAL RESIDUAL'])
    Portafolio['cpnFirstActual'] = np.nan
    Portafolio['cpnRateType'] = np.nan
    Portafolio['portfolioNAV'] = np.nan
    Portafolio['country'] = 'CO'
    Portafolio['futureValue'] = np.nan
    Portafolio['referenceDate'] = ref_date

    Columnasportafolio=Columnas.loc[:,["COLUMNA FINAL"]]
    Columnasportafolio=Columnasportafolio.drop_duplicates('COLUMNA FINAL').dropna()
    Columnasportafolio=Columnasportafolio["COLUMNA FINAL"].dropna().unique().tolist()
    Portafolio=Portafolio.loc[:, Portafolio.columns.isin(Columnasportafolio)]

    Columnasportafolio=Columnas.loc[:,["COLUMNAS","COLUMNA FINAL"]]
    Columnasportafolio=Columnasportafolio.drop_duplicates('COLUMNA FINAL').dropna()
    Columnasportafolio=Columnasportafolio["COLUMNAS"].dropna().unique().tolist()
    Portafolio.columns=Columnasportafolio


    # Prorrateo Mkt Value si se requiere. - se modifica logica 2022-09-07
    if mkt_value_prorrateo is not None:
        if port_name == 'PortafolioAlfa':
            mktValueTotal = Portafolio['mktValue'].sum()
            factor_prorrateo = mkt_value_prorrateo / mktValueTotal
            Portafolio['mktValue'] = Portafolio['mktValue'] * factor_prorrateo
            Portafolio['quantity'] = Portafolio['quantity'] * factor_prorrateo
        elif port_name == "PortafolioPatrimonio":

            mktValuePatrimonio = Portafolio.loc[Portafolio['codigoPuc'] == '130315',['mktValue']].sum(axis=1).sum()
            quantityPatrimonio = Portafolio.loc[Portafolio['codigoPuc'] == '130315',['quantity']].sum(axis=1).sum()

            for i in range(len(Portafolio)):
                if Portafolio.loc[i, 'codigoPuc'] == '130315':
                    Portafolio.loc[i, 'mktValue'] = (Portafolio.loc[i, 'mktValue'] / mktValuePatrimonio) * mkt_value_prorrateo
                    Portafolio.loc[i, 'quantity'] = (Portafolio.loc[i, 'quantity'] / quantityPatrimonio) * mkt_value_prorrateo
                elif Portafolio.loc[i, 'codigoPuc'] in ('130205', '130305'):
                    Portafolio.loc[i, 'mktValue'] = Portafolio.loc[i, 'mktValue']
                    Portafolio.loc[i, 'quantity'] = Portafolio.loc[i, 'quantity']
                else:
                    Portafolio.loc[i, 'mktValue'] = Portafolio.loc[i, 'mktValue']
                    Portafolio.loc[i, 'quantity'] = Portafolio.loc[i, 'quantity']

    Portafolio = Portafolio.drop(['codigoPuc'], axis=1)
    Portafolio = Portafolio.drop(['cpnFirstActual'], axis=1)
    Portafolio = Portafolio.drop(['cpnRateType'], axis=1)
    Portafolio = Portafolio.drop(['margin'], axis=1)


    # Se añade liquidez u otros campos de ser necesario.
    if add_rows is not None:
        for k in add_rows.copy().keys():
            if k not in Portafolio.columns:
                del add_rows[k]
        add_rows = pd.DataFrame([add_rows])

        # Agrego nuevos registros.
        Portafolio = Portafolio.append(add_rows).reset_index(drop=True)

    # Reemplazo fechas con '0' desde CITI.
    cols = ['issueDt', 'maturity', 'purchaseDt']
    Portafolio[cols] = Portafolio[cols].replace('0', np.nan)

    # Formateo columnas de fechas.
    Portafolio['issueDt'] = pd.to_datetime(Portafolio['issueDt'].str.zfill(8), format='%d%m%Y').dt.strftime("%Y-%m-%d")
    Portafolio['maturity'] = pd.to_datetime(Portafolio['maturity'].str.zfill(8), format='%d%m%Y').dt.strftime("%Y-%m-%d")
    Portafolio['purchaseDt'] = pd.to_datetime(Portafolio['purchaseDt'].str.zfill(8), format='%d%m%Y').dt.strftime("%Y-%m-%d")

    # Completo días al venc. con NA.
    Portafolio=Portafolio.astype({'daysToMaturity':'float'})

    # Reemplazo [NULL] con NaN.
    Portafolio = Portafolio.replace("[NULL]", np.nan)
    Portafolio = Portafolio.replace('NA', np.nan)
    
    # Cruzo con archivo NEMOS-ISIN.xlsx - SI ES IBR.
    Nemos.rename(columns={'NEMO NUEVO': 'assetId', 'USO TASA ACTUAL': 'cpnFirstActual', 'TIPO TASA': 'cpnRateType', 'TASA REFERENCIA': 'indexRate_Nemo'}, inplace=True)
    df_IBR = Portafolio[Portafolio.indexRate.isin(['IBR'])]    
    df_IBR = pd.merge(df_IBR, Nemos[['assetId', 'indexRate_Nemo']], how='left', on='assetId')
    df_IBR['indexRate'] = df_IBR['indexRate_Nemo']
    df_IBR = df_IBR.drop(['indexRate_Nemo'], axis=1)
    
    # NO IBR queda normal.
    df_noIBR = Portafolio[~Portafolio.indexRate.isin(['IBR'])]
    
    # Concateno ambos df.
    Portafolio = pd.concat([df_IBR, df_noIBR], ignore_index=True)

    # Cruzo con NEMOS-ISIN y traigo otros dos campos.
    Portafolio = pd.merge(Portafolio, Nemos[['assetId', 'cpnFirstActual', 'cpnRateType']], how='left', on='assetId')
    Portafolio['cpnType'] = ['F' if iR == 'FS' else 'T' if iR != 'FS' and iR is not np.nan else np.nan for iR in Portafolio['indexRate']]

    # Cruzo con valores coupFreq.
    coupFreq['idCoupFreq'] = coupFreq['idCoupFreq'].astype('Int64')
    Portafolio['coupFreq'] = Portafolio['coupFreq'].astype('Int64')
    coupFreq.rename(columns={'coupFreq': 'coupFreqValue'}, inplace=True)
    Portafolio = pd.merge(Portafolio, coupFreq, how='left', left_on='coupFreq', right_on='idCoupFreq')
    Portafolio['coupFreq'] = Portafolio['coupFreqValue']

    # Cruzo con valores dateConv.
    Portafolio['dateConv'] = Portafolio['dateConv'].astype('Int64')
    dateConv['idDateConv'] = dateConv['idDateConv'].astype('Int64')
    dateConv.rename(columns={'dateConv': 'dateConvValue'}, inplace=True)
    Portafolio = pd.merge(Portafolio, dateConv, how='left', left_on='dateConv', right_on='idDateConv')
    Portafolio['dateConv'] = Portafolio['dateConvValue']

    Portafolio = Portafolio.drop(['idCoupFreq', 'X', 'coupFreqValue', 'idDateConv', 'dateConvValue'], axis=1)

    # Agrego Banda para calculo de margin.
    labels, bins_ini, bins_fin = [], [], []
    for k, v in dictDiasVcto.items():
        bins_fin.append(v[1])
        labels.append(k)
    bins_fin.insert(0, 0)
    # Aplico cut pandas.
    Portafolio['Banda'] = pd.cut(x=Portafolio['daysToMaturity'], bins=bins_fin, labels=labels)
    Portafolio['Banda'] = Portafolio['Banda'].astype('float64')
    
    # Merge de Portfolio y PreciaMargen.
    # Filtro Portfolio secDesc1 es CDT, BPEDN, o BPEN, y cruzo nemo + banda.
    PreciaMargen.rename(columns={'Nemo': 'assetId', 'Margen': 'margin', 'Dias al vencimiento': 'Banda'}, inplace=True)
    values=['CDT','BPEDN', 'BPEN']
    filtered_df = Portafolio[Portafolio.secDesc1.isin(values)]
    filtered_df = pd.merge(filtered_df, PreciaMargen[['assetId', 'Banda', 'margin']],  on=['assetId', 'Banda'], how='left')
    
    # Filtro Portfolio secDesc1 != CDT, BPEDN, o BPEN, y cruzo solo por nemo.
    filtered_df_2 = Portafolio[~Portafolio.secDesc1.isin(values)]
    filtered_df_2 = pd.merge(filtered_df_2, PreciaMargen[['assetId', 'Banda', 'margin']],  on=['assetId'], how='left')

    # Concateno ambos resultados.
    Portafolio = pd.concat([filtered_df, filtered_df_2], ignore_index=True)

    # Elimino Banda
    Portafolio = Portafolio.drop(['Banda', 'Banda_x', 'Banda_y'], axis=1)

    # Reemplazo [NULL] con NaN.
    Portafolio = Portafolio.replace("[NULL]", np.nan)
    Portafolio = Portafolio.replace('NA', np.nan)
    Portafolio = Portafolio.replace('nan', np.nan)

    # Union con formato regional.
    df_aladdin = pd.DataFrame(columns=portfolio_fields['Fields'].dropna().unique().tolist())
    Portafolio = df_aladdin.append(Portafolio, ignore_index=True)

    # Asigno subgroup en base a condiciones, portfolioName queda quemados con parametro.    
    condiciones = [(Portafolio.portfolioName == 'SU25'), (Portafolio.portfolioName == 'SU26'), (Portafolio.portfolioName == 'SU29')]
    valores = ('PATRIMONIO', 'RENTAS_VITALICIAS', 'SEGURO PREVISIONAL')
    Portafolio['subGroup'] = np.select(condiciones, valores, subGroup)

    Portafolio['portfolioName'] = portfolioName

    # Agrego portfolioNAV
    df_NAV = Portafolio.groupby('subGroup').agg(portfolioNAV=('mktValue', 'sum')).reset_index()
    Portafolio['portfolioNAV'] = np.nan
    Portafolio['portfolioNAV'] = Portafolio['portfolioNAV'].fillna(Portafolio['subGroup'].map(df_NAV.set_index('subGroup')['portfolioNAV']))


    # Ajuste YTM
    Portafolio['yieldToMaturity'] = np.where(Portafolio['valuationMethod']==9, Portafolio['discountRate'], Portafolio['yieldToMaturity'])

    
    # Correccion a campos amortizationType y valuationMethod.
    # amortizationType
    amortType_options = [(Portafolio.amortizationType == 1), (Portafolio.amortizationType == 2), (Portafolio.amortizationType == 3), (Portafolio.amortizationType == 4)]
    amortType_values = ('Bullet', 'Amortizable', 'Intereses Especiales', 'Amortizable con Intereses Especiales')
    Portafolio['amortizationType'] = np.select(amortType_options, amortType_values, np.nan)
    

    # valuationMethod
    valMethod_options = [(Portafolio.valuationMethod == 9), (Portafolio.valuationMethod == 12), (Portafolio.valuationMethod == 13), 
                         (Portafolio.valuationMethod == 14), (Portafolio.valuationMethod == 15), (Portafolio.valuationMethod == 16), 
                         (Portafolio.valuationMethod == 17), (Portafolio.valuationMethod == 19), (Portafolio.valuationMethod == 20), (Portafolio.valuationMethod == 21)]
    valMethod_values = ('TIR - Tasa interna de retorno', 'Precio bolsa de valores en el exterior', 'Valor de unidad', 'Avalúo comercial', 
                        'Precio justo de intercambio para títulos y/o valores hechos a la medida', 
                        'Precio justo de intercambio para los CDM, Certificados de Depósito de Mercancia', 
                        'TCRM', 'Precio emisor', 'Costo (+/-) variación del patrimonio del Emisor', 'Precio publicado por Proveedor de Precios')
    Portafolio['valuationMethod'] = np.select(valMethod_options, valMethod_values, np.nan) 

    cols = ['amortizationType', 'valuationMethod']
    Portafolio[cols] = Portafolio[cols].replace('nan', np.nan)
    Portafolio[cols] = Portafolio[cols].replace(0, np.nan)
    Portafolio[cols] = Portafolio[cols].replace('0', np.nan)

    Portafolio['cpnFirstActual'] = ['ACTUAL' if cFA == 'A' else 'PREVIA' if cFA == 'P' else cFA for cFA in Portafolio['cpnFirstActual']]


    return Portafolio
