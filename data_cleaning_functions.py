import pandas as pd
import re
from nltk.corpus import stopwords
import nltk
import unidecode
import unicodedata

nltk.download('punkt')
nltk.download('stopwords')


def df_cleaning(df_secop):
    """ CLeans df of contracts in SECOP """

    sorter = ['Liquidado', 'Terminado Sin Liquidar', 'Celebrado', 'Adjudicado', 'Convocado']
    df_secop = df_secop[df_secop['estado_del_proceso'].isin(sorter)]
    df_secop[['cuantia_proceso']] = df_secop[['cuantia_proceso']].apply(pd.to_numeric)
    df_secop[['anno_firma_del_contrato']] = df_secop[['anno_firma_del_contrato']].apply(pd.to_numeric)
    df_secop = df_secop.loc[df_secop['cuantia_proceso'] >= 0]
    df_secop = df_secop.loc[df_secop['anno_firma_del_contrato'] >= 2012]
    df_secop = df_secop.reset_index(drop=True)
    return df_secop


def df_filter_entity(df_entity):
    """
    Filters df of ENTITY contracts in SECOP
    Only contracts issued to a municipality/department

    Returns
    -------
    dataframe
        df with contracts issued from the public entity to any mun/dept.
    list
        list with all the mun/dept with a contract with the public entity
    """
    # Build list of contracts issued to a municipality/department
    entity_razsoc = df_entity['nom_raz_social_contratista'].tolist()
    entity_mun_dept = [item for item in entity_razsoc if 'MUNICIPIO' in item] + \
                      [item for item in entity_razsoc if 'DEPARTAMENTO' in item]
    entity_mun_dept = [item for item in entity_mun_dept if 'ADMINISTRATIVO' not in item]
    entity_mun_dept = [item for item in entity_mun_dept if 'AGENCIA' not in item]

    # Filtering entity df
    df_entity_filtered = df_entity[df_entity['nom_raz_social_contratista'].isin(entity_mun_dept)]

    return df_entity_filtered, entity_mun_dept


# Taken from: https://stackoverflow.com/questions/14153364/reorder-string-using-regular-expressions
def standarize_mun(mun):
    """
    Standardise municipality name
    Includes several special cases
    """
    # Special cases
    if "MUNICIPIO DE" not in mun:
        nmun = re.sub('MUNICIPIO', 'MUNICIPIO DE', mun)
    nmun = re.sub('DEPARTAMENTO DE|DEPARTAEMNTO DE| EN EL DEPARTAMENTO DE | EN EL DEPARTAMENTO DEL', ' - ', nmun)
    nmun = re.sub('MUNICIPIO DEL CARMEN DE BOLIVAR', 'MUNICIPIO DE CARMEN DE BOLIVAR', nmun)
    nmun = re.sub('MUNICIPIO DE EL CARMEN DE BOLIVAR', 'MUNICIPIO DE CARMEN DE BOLIVAR', nmun)
    nmun = re.sub('MUNICIPIO DEL CARMEN DE BOLIVAR', 'MUNICIPIO DE CARMEN DE BOLIVAR', nmun)
    nmun = re.sub('MUNICIPIO DE EL CARMEN DE BOLIVAR', 'MUNICIPIO DE CARMEN DE BOLIVAR', nmun)
    nmun = re.sub('SANTIAGO DE CALI', 'CALI', nmun)
    nmun = re.sub('SAN JOSE DE CUCUTA', 'CUCUTA', nmun)
    nmun = re.sub('MUNICIPIO EL CERRITO', 'MUNICIPIO DE EL CERRITO', nmun)
    nmun = re.sub('LE RETEN', 'EL RETEN', nmun)
    nmun = re.sub('PROVIDENCIA Y SANTA CATALINA ISLAS', 'PROVIDENCIA Y SANTA CATALINA', nmun)
    nmun = re.sub('SAN JUAN BAUTISTA DE GUACARI', 'GUACARI', nmun)
    nmun = re.sub('SUSACON', 'SUSACÓN', nmun)
    nmun = re.sub('(C/MARCA)', ' - CUNDINAMARCA ', nmun)

    # Regexp cleaning
    nmun = re.sub('\.', '', nmun)
    nmun = re.sub(' +', ' ', nmun)
    nmun = re.sub('[(){}<>]', '', nmun)  # Parentesis
    r = re.compile('(^.*)(-)(.*$)')
    nmun = r.sub(r'\3' + ' - ALCALDÍA ' + r'\1', nmun)
    nmun = nmun.lstrip()  # Remove spaces before beginning
    nmun = re.sub('\.', '', nmun)
    return nmun


def standarize_depto(depto):
    """
    Standardise department name
    Includes several special cases
    """
    # Special cases
    ndepto = re.sub('GOBERNACION', '', depto)
    ndepto = re.sub('DEPARTAMENTO DEL', 'DEPARTAMENTO DE', ndepto)
    ndepto = re.sub('DEPARTAMENTO DE', 'GOBERNACIÓN -', ndepto)

    # Regexp cleaning
    ndepto = re.sub('\.', '', ndepto)
    ndepto = re.sub(' +', ' ', ndepto)
    ndepto = re.sub('[(){}<>]', '', ndepto)  # Parentesis
    r = re.compile('(^.*)(-)(.*$)')
    ndepto = r.sub(r'\3' + ' - ' + r'\1', ndepto)
    ndepto = ndepto.lstrip()  # Remove spaces before beginning
    ndepto = re.sub('\.', '', ndepto)
    ndepto = re.sub(' +', ' ', ndepto)
    return ndepto


def strip_accents(s):
    return ''.join(c for c in unicodedata.normalize('NFD', s)
                   if not unicodedata.name(c).endswith('ACCENT'))


def standarize_obj(string_obj):
    """ Standardize description of the contract"""
    cachedStopWords = stopwords.words("spanish")
    cachedStopWords = [x.upper() for x in cachedStopWords]
    clean_str = string_obj.upper()
    clean_str = ' '.join([word for word in clean_str.split() if word not in cachedStopWords])
    clean_str = unidecode.unidecode(clean_str)
    clean_str = re.sub(r'[^\w\s]', '', clean_str)
    clean_str = re.sub(' +', ' ', clean_str)
    return clean_str


# Taken from: https://stackoverflow.com/questions/5541745/get-rid-of-stopwords-and-punctuation
def remove_stopwords(sentence, language):
    """Removes stopwords"""
    return [token for token in nltk.word_tokenize(sentence) if token.lower() not in stopwords.words(language)]


def df_cleaning_names(df_names):
    """
    Cleans mun/dept. columns
    Includes several special cases
    """
    df_names['departamento'] = df_names['departamento'].str.upper()
    df_names['municipio'] = df_names['municipio'].str.upper()
    # Particular cases
    df_names['municipio'] = [re.sub('EL CARMEN DE BOLÍVAR', 'CARMEN DE BOLÍVAR', item) for item in
                             df_names['municipio']]
    df_names['municipio'] = [re.sub('EL CARMEN DE VIBORAL', 'CARMEN DE VIBORAL', item) for item in
                             df_names['municipio']]
    df_names['municipio'] = [re.sub('PROVIDENCIA', 'PROVIDENCIA Y SANTA CATALINA', item) for item in
                             df_names['municipio']]
    df_names['municipio'] = [re.sub('ESPINAL', 'EL ESPINAL', item) for item in df_names['municipio']]
    df_names['municipio'] = [re.sub('ITAGUI', 'ITAGÜÍ', item) for item in df_names['municipio']]
    df_names['municipio'] = [re.sub('TOLÚ VIEJO', 'TOLUVIEJO', item) for item in df_names['municipio']]
    df_names['municipio'] = [re.sub('TIMBIQUÍ', 'TIMBIQUI', item) for item in df_names['municipio']]
    df_names['municipio'] = [re.sub('CHIPATÁ', 'CHIPATA', item) for item in df_names['municipio']]
    df_names['municipio'] = [re.sub('SUSACON', 'SUSACÓN', item) for item in df_names['municipio']]
    df_names['municipio'] = [re.sub('TIMBÍO', 'TIMBIO', item) for item in df_names['municipio']]
    df_names['municipio'] = [re.sub('CURITÍ', 'CURITI', item) for item in df_names['municipio']]
    df_names['departamento'] = [
        re.sub('ARCHIPIÉLAGO DE SAN ANDRÉS, PROVIDENCIA Y SANTA CATALINA', 'SAN ANDRÉS PROVIDENCIA Y SANTA CATALINA',
               item) for item in df_names['departamento']]

    return df_names


def standardize_accents_mun(df_names, names_mun_standard):
    """
    Standardize accents of mun/dept with official names

    Parameters
    -------
    df_names
        df with the official names for municipalities and departments
    names_mun_standard
        list with standardized names of mun/dept.
    Returns
    -------
    dataframe
        df with contracts issued from the public entity to any mun/dept.
    """
    dept_t = list(set(df_names['departamento'].tolist()))  # Accent
    dept_st = [strip_accents(item) for item in df_names]  # No accent
    mun_t = list(set(df_names['municipio'].tolist()))  # CON TILDES
    mun_st = [strip_accents(item) for item in df_names]  # SIN TILDES

    # Standardization accents of departments
    for contd, dept in enumerate(dept_st):
        for i, item in enumerate(names_mun_standard):
            if dept in item:
                names_mun_standard[i] = re.sub(dept, dept_t[contd], item)

    # Standardization accents municipalities
    for contm, mun in enumerate(mun_st):
        for i, item in enumerate(names_mun_standard):
            if mun in item:
                names_mun_standard[i] = re.sub(mun, mun_t[contm], item)

    return names_mun_standard


def standardize_format_mun(df_names, names_mun_standard):
    """Standardize format of mun/dept names"""
    # 1. Municipalities with department name
    deptos_t = list(set(df_names['departamento'].tolist()))  # Accent
    for i, item in enumerate(names_mun_standard):
        for contd, depto in enumerate(deptos_t):
            if '-' in item: break  # If it already has format
            item = item.lstrip()
            if 'CARMEN DE BOLÍVAR' in item: continue
            if depto in item:
                my_str = item
                substr = depto
                inserttxt = " - "
                idx = my_str.index(substr)
                names_mun_standard[i] = my_str[:idx] + inserttxt + my_str[idx:]
                names_mun_standard[i] = standarize_mun(names_mun_standard[i])

    # 2. Municipalities without department name
    for i, item in enumerate(names_mun_standard):
        if '-' in item: continue
        string = names_mun_standard[i].replace("MUNICIPIO DE ", "")  # remove the 8 from the string borders
        string = string.lstrip()
        for contm, mun in enumerate(df_names['municipio']):
            if mun == string:
                names_mun_standard[i] = df_names['departamento'][contm] + ' - ' 'ALCALDÍA MUNICIPIO DE ' + string

    return names_mun_standard