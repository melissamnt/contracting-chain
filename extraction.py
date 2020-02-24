import data_extraction_functions as extract


def extracting_data():
    """
    Gets the public entity contracting dataframe and the official names of municipalities/departments in Colombia

    Returns
    -------
    df_entity_raw: dataframe
        public entity contracts issued since 2012
    df_names_raw: dataframe
        official names of municipalities/departments in Colombia
    """
    df_entity_raw = extract.extract_entity_contracts('INSTITUTO NACIONAL DE VÍAS (INVIAS)')
    df_names_raw = extract.extract_mun_names()

    return df_entity_raw, df_names_raw
