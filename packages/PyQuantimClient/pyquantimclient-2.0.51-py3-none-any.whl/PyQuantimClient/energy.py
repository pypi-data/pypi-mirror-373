# -*- coding: utf-8 -*-
import pandas as pd
import numpy as np
import datetime as dt
from .api import quantim

class energy_data(quantim):
    """
    El objeto de energy_data contiene la conexión de los usuarios.

    Parameters
    ----------
    username : str
        Nombre de usuario.
    password : str
        Contraseña del usuario.
    secretpool : str
        Grupo de usuarios al que pertenece.
    env : str
        Ambiente en el que se utiliza el código.
    """
    def __init__(self, username, password, secretpool, env="qa"):
        super().__init__(username, password, secretpool, env)

    def get_sector_data(self, country, metric="", date_ini="", date_last=""):
        """
        Obtener los datos de energía en un dataframe listo para utilizar.

        Parameters
        ----------
        country : str
            Código del país, dos caracteres.
        metric : str
            Métrica del país, aplica solo para cierto(s) país(es).
        date_ini : str
            Fecha inicial, si se deja vacío trae desde la primera fecha disponible.
        date_last : str
            Fecha final, si se deja vació trae hasta la última fecha disponible.

        Raises
        ------
        ValueError
            Si no hay conexión a S3.

        Returns
        -------
        bool
            True si tiene éxito, False en caso contrario.

        Notes
        -----
        El único campo obligatorio es 'country'.
        La instalación/actualización de PyQuantimClient debe ser a través del comando 'pip install PyQuantimClient'.
        """
        data={"cod_pais":country, "metrica":metric, "fec_ini":date_ini, "fec_fin":date_last}
        resp=self.api_call('energy_data', method="post", data=data, verify=False)
        return pd.DataFrame(resp).set_index('Date')
