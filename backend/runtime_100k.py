import pickle
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
from scipy import sparse
import numpy as np
from sklearn.decomposition import NMF

#loading the saved movies_info csv file
movies_info = pd.read_csv('movies_info.csv')

ratings_df = pd.read_csv('ml-100k/u.data', sep='\t', header=None, usecols=[0,1,2])
ratings_df.columns = ['userId', 'movieId', 'rating']

#Defining X and y
X = ratings_df[['userId', 'movieId']].values
y = ratings_df['rating'].values

#Defining a rating matrix R
def ConvertToDense(X, y ,shape):
    row = X[:,0]    # gets the userId values as ndarray
    col = X[:,1]    #gets the movieId values as ndarray
    data = y        # rating values as ndarray
    matrix_sparse = sparse.csr_matrix((data,(row,col)), shape=(shape[0]+1,shape[1]+1))  
    R = matrix_sparse.todense()       # getting the R matrix where empty cells are replaced with zeros
    R = R[1:, 1:]                     # This is done because we have userIds and movieIds starting from 1 so entire zeroth row and column is unnecessary
    R= np.asarray(R)
    return R

n_users = len(ratings_df['userId'].unique())
n_movies = len(ratings_df['movieId'].unique())
R_shape = (n_users, n_movies)
R = ConvertToDense(X, y, R_shape)

#loading the model
with open('savedmodel/model.pickle', 'rb') as f:
    estimator = pickle.load(f)

estimator.fit(R)  
Theta = estimator.transform(R)            # user features
M = estimator.components_.T               # movie features

# Making the predictions
R_pred = M.dot(Theta.T).T
                    
# Clipping values                                                    
R_pred[R_pred > 5] = 5.           # clips ratings above 5             
R_pred[R_pred < 1] = 1.           # clips ratings below 1

item_sim = cosine_similarity(M)                   #gets the pairwise cosine similarity between movies based on their feature vectors

def make_recommendation_newuser(movie_idx, sim=item_sim, k=5):
    '''
    movie_idx ...... select an item
    k  ............ number of movies to recommend
    '''
    reco_item_df = pd.DataFrame(sim).iloc[movie_idx-1, :]      # getting the pairwise cosine similarity row for selected movie
    reco_item_df = pd.concat([reco_item_df, movies_info], axis=1)   # merge list with the movie's title
    reco_item_df.columns = ['similarity','movieId', 'title', 'tmdbId']
    reco_item_df = reco_item_df.sort_values(by='similarity',ascending=False)
 
    return reco_item_df[1:k+1]      # returns the 5 movies the most similar to movie_idx




