import requests
import pandas as pd


def extract_entity_contracts(entity_name):
    """
        Gets dataframe of all contracts issued by the municipality/department to a third party contractor

        Parameters
        ----------
        entity_name : string
            name of public entity to evaluate

        Returns
        -------
        dataframe
            all contracts issued by the municipality/department to a third party contractor
    """
    entity_name = 'INSTITUTO NACIONAL DE VÍAS (INVIAS)'
    url_secop = 'https://www.datos.gov.co/resource/c6dm-udt9.json'
    p_entity = {'nombre_de_la_entidad': entity_name,
                '$limit': 10000,
                'causal_de_otras_formas_de_contratacion_directa': 'Contratos Interadministrativos (Literal C)'}
    r_entity = requests.get(url_secop, params=p_entity)
    d_entity = r_entity.json()  # To .json
    df_entity = pd.DataFrame(d_entity)  # To df
    return df_entity


def extract_mun_contracts(mun_name):
    """
        Gets dataframe of all contracts issued by the municipality/department to a third party contractor

        Parameters
        ----------
        mun_name : string
            name of municipalities/department to evaluate

        Returns
        -------
        dataframe
            all contracts issued by the municipality/department to a third party contractor
    """
    # Getting df of all contracts issued by the municipality/department to a third party contractor
    url_secop = 'https://www.datos.gov.co/resource/c6dm-udt9.json'
    p_api = {'nombre_de_la_entidad': mun_name, '$limit': 1000000}
    r_api = requests.get(url_secop, params=p_api)
    d_api = r_api.json()  # To .json
    df_api = pd.DataFrame(d_api)  # To df
    return df_api


def extract_mun_names():
    """Gets dataframe with all the municipalities and departments in Colombia"""
    url_mun = 'https://www.datos.gov.co/resource/p95u-vi7k.json'
    p_mun = {'$limit': 2000}
    r_mun = requests.get(url_mun, params=p_mun)
    d_mun = r_mun.json()  # To .json
    # To df
    df_mun = pd.DataFrame(d_mun)

    return df_mun
