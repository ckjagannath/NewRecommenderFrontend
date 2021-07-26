import pandas as pd
from pandas import DataFrame as df
from scipy import sparse
import numpy as np
from sklearn.decomposition import NMF
from sklearn.model_selection import train_test_split, ShuffleSplit
from sklearn.metrics import mean_squared_error
import pickle
import time
from topmov_recommender import merged_moviedata

import warnings
warnings.filterwarnings('ignore')

ratings_df = pd.read_csv('ml-100k/u.data', sep='\t', header=None)
ratings_df.columns = ['userId', 'movieId', 'rating', 'timestamp']


movies_info = pd.read_csv('ml-100k/u.item', sep='|', header=None, encoding='ISO-8859-1', usecols=[0, 1])
movies_info.columns = ['movieId', 'title']

# checking for match in 25M dataset based on title
movies_info = df1 = movies_info.assign(exist=movies_info['title'].isin(merged_moviedata['title']))
tmdbids = pd.read_csv('ml-100k/100K_idsOfUnmatchedtitles.csv', skip_blank_lines=False) # this contains unmatched title ids
movies_info_false = df1[df1['exist'] == False]
movies_info_false.insert(3, 'tmdbId', tmdbids.values) # inserting tmdbids as fourth column to unmatched dataframe in above line

movies_info_true = df1[df1['exist'] == True] # getting rows with matched titles in 25M df

# This step merges matched title rows of 25M and 100k 
movies_info = df.merge(merged_moviedata, movies_info_true, on='title', how='inner', left_index=True)
movies_info = movies_info[['movieId_y', 'title', 'tmdbId']]

movies_info.columns = ['movieId', 'title', 'tmdbId']
# The below step merges unmatched with matched to get the required df to work on with tmdbids
movies_info = movies_info.append(movies_info_false).sort_values('movieId').drop('exist', axis=1).drop_duplicates('movieId')
movies_info.to_csv('movies_info.csv', index=False)

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

def GetShape(filename):
    ratings_df = pd.read_csv(filename, sep='\t', header=None)
    ratings_df.columns = ['userId', 'movieId', 'rating', 'timestamp']
    n_users = len(ratings_df['userId'].unique())
    n_items = len(ratings_df['movieId'].unique())
    return (n_users, n_items)

def LoadData(filename, R_shape):
    ratings_df = pd.read_csv(filename, sep='\t', header=None)
    ratings_df.columns = ['userId', 'movieId', 'rating', 'timestamp']  
    X = ratings_df[['userId', 'movieId']].values
    y = ratings_df['rating'].values  
    return X, y, ConvertToDense(X, y, R_shape)
 
R_shape = GetShape('ml-100k/u.data') 
X, y, R = LoadData('ml-100k/u.data', R_shape)

#splitting the data into train & test
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.25)
R_train = ConvertToDense(X_train, y_train, R_shape)
R_test = ConvertToDense(X_test, y_test, R_shape)

#defining the rmse loss
def get_rmse(pred, actual):
    pred = pred[actual.nonzero()].flatten()     
    actual = actual[actual.nonzero()].flatten() 
    return np.sqrt(mean_squared_error(pred, actual))

cv = ShuffleSplit(n_splits=5, test_size=.25, random_state=0)

#Grid search for hyper-parameter tuning
param =        {
                    'n_components' : [15, 20, 25, 35],
                    'alpha' : [0.001, 0.01, 0.1],
                    'l1_ratio' : [0], 
                    'max_iter' : [15, 20, 25, 50]
                }

# Keep track of RMSE and parameters
grid_search = pd.DataFrame([[0, 0, 0, 0, 0]])
grid_search.columns = ['n_components', 'alpha', 'l1_ratio', 'max_iter'] + ['RMSE']

# nb of folds in ShuffleSplit CV
n_splits = 5      
i = 0

# Performing the Grid search
for n_components in param['n_components']:
    for alpha in param['alpha']:
        for l1_ratio in param['l1_ratio']:
            for max_iter in param['max_iter']:

                err = 0
                n_iter = 0
                # print('Search', i, '/', 4*3*4*1 - 1)
                for train_index, test_index in cv.split(X):
    
                    X_train_cv, X_test_cv = X[train_index], X[test_index]
                    y_train_cv, y_test_cv = y[train_index], y[test_index]

                    # Converting sparse array to dense array
                    R_train = ConvertToDense(X_train_cv, y_train_cv, R_shape)
                    R_test = ConvertToDense(X_test_cv, y_test_cv, R_shape)

                    # updating the parameters
                    parametersNMF = {
                    'n_components' : n_components,
                    'init' : 'random', 
                    'random_state' : 0, 
                    'alpha' : alpha,
                    'l1_ratio' : l1_ratio,
                    'max_iter' : max_iter}
                    
                    estimator = NMF(**parametersNMF)
                
                    # Training (matrix factorization)
                    t0 = time.time()
                    estimator.fit(R_train)  
                    Theta = estimator.transform(R_train)       # user features
                    M = estimator.components_.T                # item features
                    #print "Fit in %0.3fs" % (time.time() - t0)
                    n_iter += estimator.n_iter_ 

                    # Making the predictions
                    R_pred = M.dot(Theta.T).T
                    
                    # Clipping values                                                    
                    R_pred[R_pred > 5] = 5.           # clips ratings above 5             
                    R_pred[R_pred < 1] = 1.           # clips ratings below 1

                    # Computing the error on the validation set 
                    err += get_rmse(R_pred, R_test)
                
                #print "RMSE Error : ", err / n_folds
                grid_search.loc[i] = [n_components, alpha, l1_ratio, max_iter, err/n_splits]
                i += 1

best_params = grid_search.sort_values('RMSE')[:1]
print('*** best params ***')
print(best_params)

best_params['n_components'] = best_params['n_components'].apply(lambda x: int(x))
best_params['max_iter'] = best_params['max_iter'].apply(lambda x: int(x))
parametersNMF_opt = best_params.iloc[:,:-1].to_dict('records')[0]
parametersNMF_opt.update({'init':'random', 'random_state':0})
estimator = NMF(**parametersNMF_opt)

#saving the estimator
with open('savedmodel/model.pickle', 'wb') as f:
    pickle.dump(estimator, f)

