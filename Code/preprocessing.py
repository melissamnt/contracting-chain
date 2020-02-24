import data_cleaning_functions as clean


def preprocessing_data(df_entity_raw, df_names_raw):
    """
    Preprocess raw data to remove unwanted rows
    Cleans columns with department/municipality names and description of the contracts

    Parameters
    ----------
    df_entity_raw : dataframe
        contracts issued by the public entity
    df_names_raw: int
        official names of municipality/department

    Returns
    -------
    dataframe
        contracts issued by entity standardised
    list
        names of municipalities/departments with contracts with the entity
    """
    # Filter entity contracts: only contracts issued to a mun/dept.
    # Also gets list of names of mun/dept. with contracts with the entity
    df_entity_filter, names_mun_list = clean.df_filter_entity(df_entity_raw)
    # Cleaning unused rows
    df_entity = clean.df_cleaning(df_entity_filter)

    # Get list of departments and municipalities of Colombia
    df_names = clean.df_cleaning_names(df_names_raw)

    # First standardization: names of mun/dept. with contracts with the entity
    names_mun_list = [clean.strip_accents(item) for item in names_mun_list]
    names_mun_standard = []
    for item in names_mun_list:
        if 'MUNICIPIO' in item:
            names_mun_standard.append(clean.standarize_mun(item))
        else:
            names_mun_standard.append(clean.standarize_depto(item))

    # Second standardization: accent standardization without accents with official names
    names_mun_standard = clean.standardize_accents_mun(df_names, names_mun_standard)

    # Third standardization: format standardization to ensure a right joining
    names_mun_standard = clean.standardize_format_mun(names_mun_standard)

    # Assign new column to entity dataframe
    df_entity = df_entity.assign(nom_raz_soc_stand=names_mun_standard)
    names_mun_standard_list = list(set(names_mun_standard))

    return df_entity, names_mun_standard_list
