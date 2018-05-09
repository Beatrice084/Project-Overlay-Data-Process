import pandas as pd
import utility_funcs as uf
import ProjectOverlayDataProcess as data
import code

from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfTransformer



def import_data():
    return  data.import_dataframe("relevantgroups"), data.import_dataframe("mandates"), data.import_dataframe("similarities")

def groups_to_vector(df, columns_to_clean):
    """
    df: Dataframe
    columns_to_clean: List of columns inside df
    """
    groups_vector = uf.text_cleaning_pipe(groups[columns_to_clean].dropna())
    groups_vector = (groups_vector
                     .dropna()
                     .drop_duplicates()
                     .loc[(groups_vector.name != '') & (groups_vector.description != '')]
                     )

    return groups_vector

def process_mandates(df, titlecol, descriptioncol ):
    mandates_vector = (df[[titlecol, descriptioncol]]
                   .drop_duplicates()
                   .groupby(titlecol)[descriptioncol]
                   .apply(list)
                   .apply(lambda x: ' '.join(x))
                   .reset_index())

    return mandates_vector


def create_vectors(group_data, mandate_data):
    return list(group_data) + list(mandate_data)

def fit_transform_tfidf(data):
    """
    The main transforming functions for the Vector Space Model
    """

    vectorizer = CountVectorizer(lowercase=True,
                                 preprocessor=None,
                                 tokenizer=None,
                                 stop_words=None,
                                 ngram_range=(1,1))
    vectorized_matrix = vectorizer.fit_transform(data).toarray()

    tf_matrix = (TfidfTransformer(norm='l2',
                                 use_idf=True,
                                 smooth_idf=True,
                                 sublinear_tf=False)
                 .fit_transform(vectorized_matrix)
                 .toarray()
                 )

    return tf_matrix


def create_cosine_similarity_dataframe(data, column_names):
    
    similarity_matrix = cosine_similarity(data)
    similarity_df = pd.DataFrame(similarity_matrix)

    if isinstance(column_names, list):
        column_names = pd.Series(column_names)

    similarity_df.columns = column_names
    similarity_df.index = column_names
    
    return similarity_df


# Running the file

if __name__ == "__main__":
    groups, mandates, similiarities =  import_data()

    groups = data.process_groups_for_vsm(groups, description_min = 10)

    groups_vector = groups_to_vector(groups, ['guid', 'name', 'description'])

    mandates_vector = process_mandates(mandates, 'Priority', 'words')

    names_vectors = create_vectors(groups_vector.guid, mandates_vector.Priority)
    desc_vectors = create_vectors(groups_vector.description, mandates_vector.words)

    tf_idf_matrix = fit_transform_tfidf(desc_vectors)

    similarity_dataframe = create_cosine_similarity_dataframe(tf_idf_matrix, names_vectors)

    similarity_dataframe.to_csv("cosine_similarities.csv")

    code.interact(local=locals())