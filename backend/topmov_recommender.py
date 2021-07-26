import pandas as pd
from pandas import DataFrame as df

movie_name_genres = pd.read_csv('ml-25m/movies.csv')
movie_imdbid_tmdbid = pd.read_csv('ml-25m/links.csv')
movie_ratings = pd.read_csv('ml-25m/ratings.csv')

merged_names_ids = pd.merge(movie_name_genres,movie_imdbid_tmdbid,on='movieId')

df_votes = movie_ratings.groupby('movieId')['movieId'].count().to_frame(name='votes').reset_index()
df_avgrating = movie_ratings.groupby('movieId')['rating'].mean().to_frame(name='avg_rating').reset_index()
df_votes_avgrating_merged = df.merge(df_votes,df_avgrating,on='movieId')
df_merged_moviedata = df.merge(movie_imdbid_tmdbid,df_votes_avgrating_merged,how='left',on='movieId')

merged_moviedata = md = df.merge(merged_names_ids,df_merged_moviedata,on=['movieId','tmdbId','imdbId'])

merged_moviedata['genres'] = merged_moviedata['genres'].apply(lambda x: x.split('|') if x != '(no genres listed)' else [])
merged_moviedata.to_csv('25M_moviesinfo.csv', index=False)
vote_counts = md[md['votes'].notnull()]['votes'].astype(int) # getting only the rows of the df with non-null in 'votes' column(i.e only movies with atleast a vote)
vote_averages = md[md['avg_rating'].notnull()]['avg_rating'] # getting only the rows of the df with non-null in 'avg_rating' column(i.e only movies with atleast a vote)
C = round(vote_averages.mean(), 1)    
m = int(vote_counts.quantile(0.95))
qualified = md[(md['votes'] >= m) & (md['votes'].notnull()) & (md['avg_rating'].notnull())][['movieId', 'title', 'genres', 'imdbId', 'tmdbId', 'votes', 'avg_rating']]
def weighted_rating(x):
    v = x['votes']
    R = x['avg_rating']
    return (v/(v+m) * R) + (m/(m+v) * C)  # IMDB's weighted rating formula
qualified['wei_rating'] = qualified.apply(weighted_rating, axis=1)
qualified['avg_rating'] = qualified['avg_rating'].apply(lambda x: round(x, 1))
qualified = qualified.sort_values('wei_rating', ascending=False).head(250)
s = md.apply(lambda x: pd.Series(x['genres'], dtype=object),axis=1).stack().reset_index(level=1, drop=True)
s.name = 'genre'
gen_md = md.drop('genres', axis=1).join(s)
gen_md.dropna(inplace = True)
gen_md.to_csv('gen_md.csv')


def build_chart(genre, percentile=0.85):
    df = gen_md[gen_md['genre'] == genre]
    vote_counts = df[df['votes'].notnull()]['votes'].astype('int')
    vote_averages = df[df['avg_rating'].notnull()]['avg_rating']
    C = round(vote_averages.mean(), 1)
    m = int(vote_counts.quantile(percentile))
    
    qualified = df[(df['votes'] >= m) & (df['votes'].notnull()) & (df['avg_rating'].notnull())][['movieId', 'title', 'imdbId', 'tmdbId', 'votes', 'avg_rating']]
    qualified['wei_rating'] = qualified.apply(weighted_rating, axis=1)
    qualified['avg_rating'] = qualified['avg_rating'].apply(lambda x: round(x, 1))
    
    qualified['wei_rating'] = qualified.apply(lambda x: (x['votes']/(x['votes']+m) * x['avg_rating']) + (m/(m+x['votes']) * C), axis=1)
    qualified = qualified.sort_values('wei_rating', ascending=False).head(250).dropna(subset=['tmdbId'])
    return qualified




