import pandas as pd
import numpy as np
import re
from sklearn.feature_extraction.text import TfidfVectorizer
from scipy.sparse import csr_matrix
# Source: https://github.com/ing-bank/sparse_dot_topn
import sparse_dot_topn.sparse_dot_topn as ct


def ngrams(name_string, n):
    """
    Divides string in groups of n characters

    Parameters
    ----------
    name_string : str
        The string to be divided
    n : int
        Size of the groups

    Returns
    -------
    list
        a list of the n-grams corresponding to the string
    """

    string = re.sub(r'[,-./]|\sBD', r'', name_string)
    n_grams = zip(*[string[i:] for i in range(n)])
    return [''.join(n_gram) for n_gram in n_grams]


def tf_idf(name_vector):
    """
    Transforms list of strings to a tf-idf representation with ngrams analizer

    Parameters
    ----------
    name_vector : list
        List of strings to convert

    Returns
    -------
    sparse matrix
        sparse matrix with tf-idf representation for each string in the list
    """
    name_series = pd.Series(list(map(str, name_vector)))

    vectorizer = TfidfVectorizer(min_df=1, analyzer=ngrams)
    tf_idf_matrix = vectorizer.fit_transform(name_series)
    return tf_idf_matrix


def awesome_cossim_top(A, B, ntop, lower_bound=0):
    """
    Evaluates similarity score between two groups of strings (as matrix) with cosine similarity and
    prints ntop highest values per string

    Parameters
    ----------
    A,B : matrix
        matrix representation of strings to compare
    ntop : int
        Number of coincidences wanted printed in results

    Returns
    -------
    csr matrix
        a sparse matrix with the ntop highest coincidences
    """

    # force A and B as a CSR matrix.
    A = A.tocsr()
    B = B.tocsr()
    M, _ = A.shape
    _, N = B.shape

    idx_dtype = np.int32

    nnz_max = M * ntop

    indptr = np.zeros(M + 1, dtype=idx_dtype)
    indices = np.zeros(nnz_max, dtype=idx_dtype)
    data = np.zeros(nnz_max, dtype=A.dtype)

    ct.sparse_dot_topn(
        M, N, np.asarray(A.indptr, dtype=idx_dtype),
        np.asarray(A.indices, dtype=idx_dtype),
        A.data,
        np.asarray(B.indptr, dtype=idx_dtype),
        np.asarray(B.indices, dtype=idx_dtype),
        B.data,
        ntop,
        lower_bound,
        indptr, indices, data)

    return csr_matrix((data, indices, indptr), shape=(M, N))


def get_matches_df(sparse_matrix, name_vector):
    """
    Converts the sparse matrix result of similarity to a readable format (dataframe)

    Parameters
    ----------
    sparse_matrix : csr matrix
        sparse matrix representation of similarity score between two groups of strings
    name_vector : list
        list with name of the strings compared

    Returns
    -------
    dataframe
        a dataframe with the scores and string coincidences with the highest similarity for each string
    """

    name_vector_list = pd.Series(list(map(str, name_vector)))

    non_zeros = sparse_matrix.nonzero()

    sparserows = non_zeros[0]
    sparsecols = non_zeros[1]

    nr_matches = sparsecols.size

    left_side = np.empty([nr_matches], dtype=object)
    right_side = np.empty([nr_matches], dtype=object)
    similarity = np.zeros(nr_matches)
    pos_left = np.zeros(nr_matches, dtype=np.int)
    pos_right = np.zeros(nr_matches, dtype=np.int)

    for index in range(0, nr_matches):
        left_side[index] = name_vector_list[sparserows[index]]
        right_side[index] = name_vector_list[sparsecols[index]]
        similarity[index] = sparse_matrix.data[index]
        pos_left[index] = sparserows[index]
        pos_right[index] = sparsecols[index]

    return pd.DataFrame({'left_side': left_side,
                         'right_side': right_side,
                         'similarity': similarity,
                         'pos_left': pos_left,
                         'pos_right': pos_right})

