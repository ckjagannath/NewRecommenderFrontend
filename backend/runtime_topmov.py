import pandas as pd

gen_md = pd.read_csv('gen_md.csv')


def build_chart(genre, percentile=0.85):
    df = gen_md[gen_md['genre'] == genre]
    vote_counts = df[df['votes'].notnull()]['votes'].astype('int')
    vote_averages = df[df['avg_rating'].notnull()]['avg_rating']
    C = round(vote_averages.mean(), 1)
    m = int(vote_counts.quantile(percentile))
    
    qualified = df[(df['votes'] >= m) & (df['votes'].notnull()) & (df['avg_rating'].notnull())][['movieId', 'title', 'imdbId', 'tmdbId', 'votes', 'avg_rating']]
    qualified['avg_rating'] = qualified['avg_rating'].apply(lambda x: round(x, 1))
    
    qualified['wei_rating'] = qualified.apply(lambda x: (x['votes']/(x['votes']+m) * x['avg_rating']) + (m/(m+x['votes']) * C), axis=1)
    qualified = qualified.sort_values('wei_rating', ascending=False).head(250).dropna(subset=['tmdbId'])
    return qualified