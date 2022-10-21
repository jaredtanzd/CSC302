import dash
from dash import dcc, html
import plotly.express as px
import numpy as np
import pandas as pd
import ssl
import os

ssl._create_default_https_context = ssl._create_unverified_context

app = dash.Dash()
path = os.getcwd()

df = pd.read_csv(path + "/src/movie_metadata.csv")


################## DATA PREPROCESSING ##################
numerical = [c for c in df.columns if df[c].dtype != 'object']
categorical = [c for c in df.columns if df[c].dtype == 'object']

# changing object type to category
for c in categorical:
    df[c] = df[c].astype('category')
    

numerical.remove('title_year')
numerical.remove('facenumber_in_poster')
numerical.remove('aspect_ratio')
categorical.append('title_year')
categorical.append('facenumber_in_poster')
categorical.append('aspect_ratio')
categorical.remove('movie_imdb_link')


# changing title_year type to category
df['title_year'] = pd.Categorical(df.title_year) 
# changing facenumber_in_poster type to category
df['facenumber_in_poster'] = pd.Categorical(df.facenumber_in_poster) 
# changing aspect_ratio type to category
df['aspect_ratio'] = pd.Categorical(df.aspect_ratio) 
# dropping movie imdb link
df = df.drop(columns=['movie_imdb_link']) 

# replacing null values for numerical and categorical features
null_features_list = df.columns[df.isnull().sum()>0].to_list()
null_features_list = [e for e in null_features_list if e not in ('director_name', 'actor_1_name', 'actor_2_name', 'actor_3_name', 'plot_keywords')]
for c in null_features_list:
    # replacing missing values for categorical features
    if df[c].dtype.name == 'category':
        df[c].fillna(df[c].mode().iloc[0], inplace = True)
    # replacing missing values for numerical features
    else:
        df[c].fillna(df[c].median(), inplace=True)

# drops all duplicates and updates the dataframe
df.drop_duplicates(inplace=True) 
df.reset_index(drop=True, inplace=True)



################## FEATURE ENGINEERING ##################
# Store frequency of each director in a dictionary
directors_dict = df['director_name'].value_counts().to_dict()
df['director_count'] = ''

# Appending frequency to a new df column
for i in range(len(df)):
    df.at[i,'director_count'] = directors_dict.get(df.at[i,'director_name'])

actor_1_dict = df['actor_1_name'].value_counts().to_dict()
actor_2_dict = df['actor_2_name'].value_counts().to_dict()
actor_3_dict = df['actor_3_name'].value_counts().to_dict()
df['actor_1_count'] = ''
df['actor_2_count'] = ''
df['actor_3_count'] = ''

for i in range(len(df)):
    df.at[i,'actor_1_count'] = actor_1_dict.get(df.at[i,'actor_1_name'])
    df.at[i,'actor_2_count'] = actor_2_dict.get(df.at[i,'actor_2_name'])
    df.at[i,'actor_3_count'] = actor_3_dict.get(df.at[i,'actor_3_name'])
df['director_count'] = df['director_count'].fillna(0)
df['actor_1_count'] = df['actor_1_count'].fillna(0)
df['actor_2_count'] = df['actor_2_count'].fillna(0)
df['actor_3_count'] = df['actor_3_count'].fillna(0)

df = df.drop(columns=['director_name', 'actor_1_name', 'actor_2_name', 'actor_3_name'])

# Changing the above features we engineered to dtype = category
df['director_count'] = df['director_count'].astype('category')
df['actor_1_count'] = df['actor_1_count'].astype('category')
df['actor_2_count'] = df['actor_2_count'].astype('category')
df['actor_3_count'] = df['actor_3_count'].astype('category')

# Splits string on '|' and returns a list
df.genres = df.genres.str.split('|')

# Dropping initial genres column and joining original df with OHE features
df = df.drop('genres',1).join(
    pd.get_dummies(
        pd.DataFrame(df.genres.tolist()).stack()
    ).astype(int).sum(level=0))

# Changing genres to dtype = category
genres = df.columns[26:52]
for c in genres:
    df[c] = df[c].astype('category')

# Summing up no. of genres and adding it as a new df column
df['genres_count'] = df[genres].sum(axis=1)
df.genres_count = df.genres_count.astype('category')

# Splitting the string on '|' and only grabbing the first element
df['main_keyword'] = df.plot_keywords.str.split('|').str[0]
# Dropping initial plot_keywords column
df = df.drop(columns = 'plot_keywords')
# New df with main_keyword counts
main_keyword_count = pd.DataFrame(df.main_keyword.value_counts()).reset_index()
main_keyword_count.columns = ['main_keyword', 'main_keyword_count']

df = pd.merge(df, main_keyword_count, left_on='main_keyword', right_on='main_keyword', how='left')
df['main_keyword'] = df['main_keyword'].fillna('No keywords')
df['main_keyword_count'] = df['main_keyword_count'].fillna(0)

# Changing main_keyword and main_keyword_count to dtype = category
df['main_keyword'] = df['main_keyword'].astype('category')
df.main_keyword_count = df.main_keyword_count.astype('category')

# drop movie title
df.drop('movie_title', 1)

categorical = [c for c in df.columns if df[c].dtype.name == 'category']    
numerical = [c for c in df.columns if df[c].dtype.name != 'category']
numerical_df = df[numerical]
categorical_df = df[categorical]








fig = px.scatter(
    df,
    x="budget",
    y="gross",
    size="num_voted_users",
    color="content_rating",
    hover_name="movie_title",
    log_x=True,
    size_max=60
)

app.layout = html.Div(children=[
    html.H1(children='Movies Data Dashboard', style={'text-align' : 'center', 'font-family':'verdana'}),
    dcc.Graph(id="budget_vs_gross", figure=fig)
    ])


if __name__ == "__main__":
    app.run_server(host="0.0.0.0", port=8050, debug=True)


