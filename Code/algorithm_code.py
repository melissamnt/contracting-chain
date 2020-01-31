# Importing
import pandas as pd
import requests
import re
import unidecode  # Este método quita las Ñ
import unicodedata
import math
import time
from nltk.corpus import stopwords
import nltk
nltk.download('punkt')
nltk.download('stopwords')

import functions

# ---- Loading database

# Importing database from SECOP
url_secop = 'https://www.datos.gov.co/resource/c6dm-udt9.json'
df_invias_all = import_api_to_csv(url_secop)

# Filter per year
df_invias_all[['anno_firma_del_contrato']] = df_invias_all[['anno_firma_del_contrato']].apply(pd.to_numeric)
df_invias = df_invias_all.loc[df_invias_all['anno_firma_del_contrato'] >= 2012]

# Filtering contracts
# We are only interested in interadministrative contracts
i_razsoc = df_invias['nom_raz_social_contratista'].tolist()
i_mun = [ item for item in i_razsoc if 'MUNICIPIO' in item] + [ item for item in i_razsoc if 'DEPARTAMENTO' in item]
i_mun = [ item for item in i_mun if 'ADMINISTRATIVO' not in item]
i_mun = [ item for item in i_mun if 'AGENCIA' not in item]

dff_invias = df_invias[df_invias['nom_raz_social_contratista'].isin(i_mun)]
i_mun = dff_invias['nom_raz_social_contratista'].tolist()

# Get municipality and departmenf official names
df_deptos = preprocess_municipality_name(df_invias)

# ----- Preprocessing: Standarize municipality and department names

i_mun = [ item for item in i_razsoc if 'MUNICIPIO' in item] + [ item for item in i_razsoc if 'DEPARTAMENTO' in item]
i_mun = [ item for item in i_mun if 'ADMINISTRATIVO' not in item]
i_mun = [ item for item in i_mun ifi_mun = [strip_accents(item) for item in i_mun] #SIN TILDES Y DEJA LA Ñ!!
# i_mun = [unidecode.unidecode(item) for item in i_mun] #SIN TILDES
# i_mun = [unidecode.unidecode(item) for item in i_mun] #Añadir Ñ
# List with standarized municipios: TODO ver casos especiales
# i_mun = list(set(i_mun))
i_muns = []

# Particular cases
i_mun = [re.sub('MUNICIPIO DEL CARMEN DE BOLIVAR','MUNICIPIO DE CARMEN DE BOLIVAR',item) for item in i_mun]
i_mun = [re.sub('MUNICIPIO DE EL CARMEN DE BOLIVAR','MUNICIPIO DE CARMEN DE BOLIVAR',item) for item in i_mun]
i_mun = [re.sub('MUNICIPIO DEL CARMEN DE BOLIVAR','MUNICIPIO DE CARMEN DE BOLIVAR',item) for item in i_mun]
i_mun = [re.sub('MUNICIPIO DE EL CARMEN DE BOLIVAR','MUNICIPIO DE CARMEN DE BOLIVAR',item) for item in i_mun]
i_mun = [re.sub('SANTIAGO DE CALI','CALI',item) for item in i_mun]
i_mun = [re.sub('SAN JOSE DE CUCUTA','CUCUTA',item) for item in i_mun]
i_mun = [re.sub('MUNICIPIO EL CERRITO','MUNICIPIO DE EL CERRITO',item) for item in i_mun]
i_mun = [re.sub('LE RETEN','EL RETEN',item) for item in i_mun]
i_mun = [re.sub('PROVIDENCIA Y SANTA CATALINA ISLAS','PROVIDENCIA Y SANTA CATALINA',item) for item in i_mun]
i_mun = [re.sub('SAN JUAN BAUTISTA DE GUACARI','GUACARI',item) for item in i_mun]
i_mun = [re.sub('SUSACON','SUSACÓN',item) for item in i_mun]


for item in i_mun:
    if 'MUNICIPIO' in item:
        i_muns.append(standarize_mun(item))
    else:
        i_muns.append(standarize_depto(item))


#unaccented_string = unidecode.unidecode(accented_string)
deptos_t = list(set(df_deptos['departamento'].tolist()))  # https://stackoverflow.com/questions/7961363/removing-duplicates-in-lists
deptos_st = [strip_accents(item) for item in deptos_t]

mun_t = list(set(df_deptos['municipio'].tolist())) # CON TILDES
mun_st = [strip_accents(item) for item in mun_t] # SIN TILDES

# Standardization accents department
for contd, depto in enumerate(deptos_st):
    for i, item in enumerate(i_muns):
        if depto in item:
            i_muns[i] = re.sub(depto,deptos_t[contd],item)

# Standardization accents municipality
for contm, mun in enumerate(mun_st):
    for i, item in enumerate(i_muns):
        if mun in item:
            i_muns[i] = re.sub(mun,mun_t[contm],item)


# Particular cases
i_muns = [re.sub('MANÍZALES','MANIZALES',item) for item in i_muns]
i_muns = [re.sub('CUERQUIA','CUERQUÍA',item) for item in i_muns]
i_muns = [re.sub('ZAPAYAN','ZAPAYÁN',item) for item in i_muns]

# Standardization cases
# 1. Municipalities with department name
for i, item in enumerate(i_muns):
    for contd, depto in enumerate(deptos_t):
        if '-' in item: break     # Si ya esta estendarizado
        item = item.lstrip()
        if 'CARMEN DE BOLÍVAR' in item: continue
        if depto in item:
            # https://stackoverflow.com/questions/30232344/insert-a-string-before-a-substring-of-a-string
            my_str = item
            substr = depto
            inserttxt = " - "
            idx = my_str.index(substr)
            i_muns[i] = my_str[:idx] + inserttxt + my_str[idx:]
            i_muns[i] = standarize_mun(i_muns[i])



# 2. Municipalities w/o department name
for i, item in enumerate(i_muns):
    if '-' in item: continue
    string = i_muns[i].replace("MUNICIPIO DE ", "")  # remove the 8 from the string borders
    string = string.lstrip()
    for contm, mun in enumerate(df_deptos['municipio']):
        if mun == string:
            i_muns[i] = df_deptos['departamento'][contm] + ' - ' 'ALCALDÍA MUNICIPIO DE ' + string

i_muns = [s.rstrip() for s in i_muns]

# Particular cases
i_muns = [re.sub('MUNICIPIO DEL GUAMO','TOLIMA - ALCALDÍA MUNICIPIO DE EL GUAMO',item) for item in i_muns]

# Añadir columna nueva al DF
dff_invias = dff_invias.assign(nom_raz_soc_stand = i_muns)
i_muns = list(set(i_muns))
