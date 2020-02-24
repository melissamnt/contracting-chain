import pandas as pd

import string_similarity_functions as ss
import data_extraction_functions as extract
import data_cleaning_functions as clean


def contracting_chain(list_mun, n_contracts, entity_contracts):
    """
    Gets the contracting chain of a public entity until the third-party contractor(s)

    Parameters
    ----------
    list_mun : list
        list with the names of municipalities/departments to evaluate
    n_contracts: int
        Max. number of contracts for the chain
    entity_contracts: dataframe
        Dataframe with issued contracts from a public entity

    Returns
    -------
    dataframe
        dataframe with the contracting chain for a public entity
    """

    entity_contracts = clean.df_cleaning(entity_contracts)
    chain_cont = 0
    threshold = 0.8
    chain_df = pd.DataFrame()

    for i, item in enumerate(list_mun):
        if i % 10 == 0:
            print("Iteration # " + str(i) + ";     Mun/Dept Name: " + str(item))

        mun_name = list_mun[i]

        # Subsets public entity df to contracts issued for the mun/dept.
        entity_contracts_mun = entity_contracts.loc[entity_contracts['nom_raz_soc_stand'] == item]

        mun_contracts = extract.extract_mun_contracts(mun_name)
        # If there are no contracts for the mun/dept. in SECOP continue
        if mun_contracts.empty:
            continue

        mun_contracts = clean.df_cleaning(mun_contracts)
        # If there are no contracts for the mun/dept. in the states allowed, continue
        # States = 'Liquidado', 'Terminado Sin Liquidar', 'Celebrado', 'Adjudicado', 'Convocado'
        if mun_contracts.empty:
            continue

        # Approximate string matching
        for index, entity_row in entity_contracts_mun.iterrows():

            # Only evaluate mun/dept contracts issued on or after year of the entity contract
            mun_contracts_filter = mun_contracts[
                (mun_contracts.anno_firma_del_contrato >= entity_row['anno_firma_del_contrato']) |
                (mun_contracts['anno_firma_del_contrato'].isnull())]
            mun_contracts_filter = mun_contracts_filter.reset_index(drop=True)

            # Create list with description of each contract to evaluate
            mun_description = mun_contracts_filter['detalle_del_objeto_a_contratar']
            mun_description_list = list(map(str, list(map(clean.standarize_obj, mun_description))))
            mun_description_list = pd.Series(mun_description_list)
            entity_description_list = pd.Series(clean.standarize_obj(entity_row['detalle_del_objeto_a_contratar']))

            # Paste descriptions mun/dept. and entity. Last row = entity contract
            description_list = list(mun_description_list) + list(entity_description_list)

            # String similarity algorithm -----
            # 1. Transforms strings with tf-idf algorithm to a numeric matrix
            tf_idf_matrix = ss.tf_idf(description_list)
            # 2. Gets similarity scores in a sparse matrix
            matches_sparse = ss.awesome_cossim_top(tf_idf_matrix, tf_idf_matrix.transpose(), n_contracts)
            # 3. Converts similarity matrix to a readable df
            matches_df = ss.get_matches_df(matches_sparse, description_list)

            # Chain construction ----
            # Pastes complete info of the contracts with high similitude
            for index_chain, row_chain in matches_df.iterrows():
                if row_chain['pos_left'] == row_chain['pos_right']: continue
                score = row_chain['similarity']
                # Joining info
                chain_entity = entity_row.to_frame().T
                chain_mun = mun_contracts_filter.loc[row_chain['pos_right']].to_frame().T
                chain_entity.index = [chain_cont]
                chain_mun.index = [chain_cont]
                chain_mun.columns = [str(col) + '_mun' for col in chain_mun.columns]
                chain_result = pd.concat([chain_entity, chain_mun], axis=1, join='inner', sort=True)
                chain_df = chain_df.append(chain_result, sort=False)
                chain_df.at[chain_df.index[chain_cont], 'score'] = score
                if score > threshold:
                    chain_df.at[chain_df.index[chain_cont], 'valid'] = True
                else:
                    chain_df.at[chain_df.index[chain_cont], 'valid'] = False
                chain_cont = chain_cont + 1

    return chain_df
