def import_api_to_csv (url):
    """Imports the data from the SECOP API
    """

    p_invias = {'nombre_de_la_entidad': 'INSTITUTO NACIONAL DE VÍAS (INVIAS)',
                '$limit': 10000,
                'causal_de_otras_formas_de_contratacion_directa': 'Contratos Interadministrativos (Literal C)'}
    # Gets info from API
    r = requests.get(url, params = p_invias)
    # To .json
    d_json = r.json()
    # To df
    df = pd.DataFrame(d_invias)
    return(df)

def preprocess_municipality_name():
    # API con division politico-administrativa
    url_deptos= 'https://www.datos.gov.co/resource/p95u-vi7k.json'
    p_deptos = {'$limit': 2000}
    r_deptos = requests.get(url_deptos, params = p_deptos)
    r_deptos.status_code
    r_deptos.url
    # To .json
    d_deptos = r_deptos.json()
    # To df
    df_deptos = pd.DataFrame(d_deptos)
    # To upper
    df_deptos['departamento'] = df_deptos['departamento'].str.upper()
    df_deptos['municipio'] = df_deptos['municipio'].str.upper()
    # Corregir casos particulares
    df_deptos['municipio'] = [re.sub('EL CARMEN DE BOLÍVAR','CARMEN DE BOLÍVAR',item) for item in df_deptos['municipio']]
    df_deptos['municipio'] = [re.sub('EL CARMEN DE VIBORAL','CARMEN DE VIBORAL',item) for item in df_deptos['municipio']]
    df_deptos['municipio'] = [re.sub('PROVIDENCIA','PROVIDENCIA Y SANTA CATALINA',item) for item in df_deptos['municipio']]
    df_deptos['municipio'] = [re.sub('ESPINAL','EL ESPINAL',item) for item in df_deptos['municipio']]
    df_deptos['municipio'] = [re.sub('ITAGUI','ITAGÜÍ',item) for item in df_deptos['municipio']]
    df_deptos['municipio'] = [re.sub('TOLÚ VIEJO','TOLUVIEJO',item) for item in df_deptos['municipio']]
    df_deptos['municipio'] = [re.sub('TIMBIQUÍ','TIMBIQUI',item) for item in df_deptos['municipio']]
    df_deptos['municipio'] = [re.sub('CHIPATÁ','CHIPATA',item) for item in df_deptos['municipio']]
    df_deptos['municipio'] = [re.sub('SUSACON','SUSACÓN',item) for item in df_deptos['municipio']]
    df_deptos['municipio'] = [re.sub('TIMBÍO','TIMBIO',item) for item in df_deptos['municipio']]
    df_deptos['municipio'] = [re.sub('CURITÍ','CURITI',item) for item in df_deptos['municipio']]
    df_deptos['departamento'] = [re.sub('ARCHIPIÉLAGO DE SAN ANDRÉS, PROVIDENCIA Y SANTA CATALINA','SAN ANDRÉS PROVIDENCIA Y SANTA CATALINA',item) for item in df_deptos['departamento']]

    return (df_deptos)

# STANDARIZE ALL LIST OF MUNICIPIOS

# Taken from: https://stackoverflow.com/questions/14153364/reorder-string-using-regular-expressions
def standarize_mun(mun):
    if "MUNICIPIO DE" not in mun:
        mun = re.sub('MUNICIPIO','MUNICIPIO DE',mun)
    nmun = re.sub('DEPARTAMENTO DE|DEPARTAEMNTO DE| EN EL DEPARTAMENTO DE | EN EL DEPARTAMENTO DEL',' - ',mun)     #Caso: DEPARTAMENTO DE
    nmun = re.sub('(C/MARCA)',' - CUNDINAMARCA ', nmun)     #Caso: (C/MARCA)
    # Remove double spaces and punctuation (except -) https://stackoverflow.com/questions/1546226/simple-way-to-remove-multiple-spaces-in-a-string
    nmun = re.sub('\.','',nmun)     # https://stackoverflow.com/questions/265960/best-way-to-strip-punctuation-from-a-string-in-python
    nmun = re.sub(' +', ' ', nmun)
    nmun = re.sub('[(){}<>]', '', nmun)   # Parentesis
    r = re.compile('(^.*)(-)(.*$)')
    nmun = r.sub(r'\3'+ ' - ALCALDÍA '+ r'\1',nmun)
    nmun = nmun.lstrip()            # Remove spaces before beginning
    nmun = re.sub('\.','',nmun)
    return nmun 

def standarize_depto(mun):
    nmun = re.sub('GOBERNACION','',mun)     #Caso: DEPARTAMENTO DE
    nmun = re.sub('DEPARTAMENTO DEL','DEPARTAMENTO DE',nmun)     #Caso: DEPARTAMENTO DE
    nmun = re.sub('DEPARTAMENTO DE','GOBERNACIÓN -',nmun)     #Caso: DEPARTAMENTO DE
    # Remove double spaces and punctuation (except -) https://stackoverflow.com/questions/1546226/simple-way-to-remove-multiple-spaces-in-a-string
    nmun = re.sub('\.','',nmun)     # https://stackoverflow.com/questions/265960/best-way-to-strip-punctuation-from-a-string-in-python
    nmun = re.sub(' +', ' ', nmun)
    nmun = re.sub('[(){}<>]', '', nmun)   # Parentesis
    r = re.compile('(^.*)(-)(.*$)')
    nmun = r.sub(r'\3'+ ' - '+ r'\1',nmun)
    nmun = nmun.lstrip()            # Remove spaces before beginning
    nmun = re.sub('\.','',nmun)
    nmun = re.sub(' +', ' ', nmun)
    return nmun

def strip_accents(s):
    return ''.join(c for c in unicodedata.normalize('NFD', s)
              if not unicodedata.name(c).endswith('ACCENT'))
