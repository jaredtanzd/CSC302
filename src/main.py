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

# ML model
from sklearn.model_selection import train_test_split
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.metrics import mean_squared_error
from sklearn.preprocessing import RobustScaler
import math
from collections import Counter

def dimsReduction(column, threshold=0.70, return_categories_list=True):
  #Find the threshold value using the percentage and number of instances in the column
  threshold_value=int(threshold*len(column))
  #Initialise an empty list for our new minimised categories
  categories_list=[]
  #Initialise a variable to calculate the sum of frequencies
  s=0
  #Create a counter dictionary of the form unique_value: frequency
  counts=Counter(column)

  #Loop through the category name and its corresponding frequency after sorting the categories by descending order of frequency
  for i,j in counts.most_common():
    #Add the frequency to the global sum
    s+=dict(counts)[i]
    #Append the category name to the list
    categories_list.append(i)
    #Check if the global sum has reached the threshold value, if so break the loop
    if s>=threshold_value:
      break
    
  #Append the category Other to the list
  categories_list.append('Other')

  #Replace all instances not in our new categories by Other  
  new_column = column.apply(lambda x: x if x in categories_list else 'Other')

  #Return transformed column and unique values if return_categories=True
  if(return_categories_list):
    return pd.Series(new_column), categories_list
  #Return only the transformed column if return_categories=False
  else:
    return pd.Series(new_column)

for var in df[list(set(categorical) - set(genres))]:
    _ , cat_list = dimsReduction(df[var], return_categories_list=True)

for var in df[list(set(categorical) - set(genres))]:
    if var == 'main_keyword':
        df[var], cat_list =  dimsReduction(df[var], threshold=0.2)
    # since color only has 2 unique features, we set the threshold to 100% to capture the other feature
    elif var == 'color': 
        df[var], cat_list = dimsReduction(df[var], threshold=1)
    else:
        df[var], cat_list = dimsReduction(df[var])

ohe_columns =  list(set(categorical) - set(genres))
ohe_df =  pd.get_dummies(df[ohe_columns])

df_merged = pd.concat([df, ohe_df], axis=1)
df_merged = df_merged.drop(ohe_columns, axis=1)
df_merged = df_merged.astype('float64')

# X -> Numerical predictors 
# y -> gross, numerical response 
X, y = df_merged[numerical].loc[:, df_merged[numerical].columns != 'gross'], df_merged['gross']
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.25, random_state=13)

# Fitting the robust scaler transform on the train set
rs1 = RobustScaler().fit(X_train)
rs2 = RobustScaler().fit(y_train.values.reshape(-1,1))

# Transforming both train and test sets
X_train = pd.DataFrame(rs1.transform(X_train.values), index=X_train.index, columns=X_train.columns)
y_train = pd.DataFrame(rs2.transform(y_train.values.reshape(-1,1)), index=y_train.index, columns=['gross'])

X_test = pd.DataFrame(rs1.transform(X_test), index=X_test.index, columns=X_test.columns)
y_test = pd.DataFrame(rs2.transform(y_test.values.reshape(-1,1)), index=y_test.index, columns=['gross'])
cat_tomerge = df_merged[df_merged.columns[~df_merged.columns.isin(numerical)]]

X_train = pd.merge(X_train, cat_tomerge, left_index=True, right_index=True)
X_test = pd.merge(X_test, cat_tomerge, left_index=True, right_index=True)

gbr_rmse = []

# Gradient Boosting Regressor model
model = GradientBoostingRegressor(random_state=0)
model.fit(X_train.values, y_train.values)

# Predict Gross from our predictor features
y_train_pred = model.predict(X_train.values)
y_test_pred = model.predict(X_test.values)

train_rmse = math.sqrt(mean_squared_error(y_train.values, y_train_pred))
train_r2 = model.score(X_train.values, y_train.values)
test_rmse = math.sqrt(mean_squared_error(y_test.values, y_test_pred))
test_r2 = model.score(X_test.values, y_test.values)


plot_df_train = pd.concat([y_train, pd.DataFrame(y_train_pred).set_index(y_train.index)], axis=1)
plot_df_test = pd.concat([y_test, pd.DataFrame(y_test_pred).set_index(y_test.index)], axis=1)
plot_df_train.columns = ['Gross Actual (Train)', 'Gross Predicted (Train)']
plot_df_test.columns = ['Gross Actual (Test)', 'Gross Predicted (Test)']


fig_main = px.scatter(
    df,
    x="budget",
    y="gross",
    size="num_voted_users",
    color="content_rating",
    hover_name="movie_title",
    log_x=True
)

from plotly.subplots import make_subplots
import plotly.graph_objects as go

fig_train = px.scatter(
    plot_df_train,
    x='Gross Actual (Train)',
    y='Gross Predicted (Train)',
    trendline='ols',
    trendline_color_override="red",
)

fig_test = px.scatter(
    plot_df_test,
    x='Gross Actual (Test)',
    y='Gross Predicted (Test)',
    trendline='ols',
    trendline_color_override="red"
)


app.layout = html.Div(children=[
    html.H1(children='Movies Data Dashboard', style={'text-align' : 'center', 'font-family':'verdana'}),
    
    html.H3(children='Budget vs Gross', style={'text-align' : 'center', 'font-family':'verdana'}),
    html.Center(children=[
        dcc.Graph(id='budget_vs_gross', figure=fig_main, style={'display': 'inline-block', 'height':'80%','width':'80%'})],
        style={'textAlign' : 'center'}),
    
    html.H3(children='Machine Learning Model Results', style={'text-align' : 'center', 'font-family':'verdana'}),
    html.Center(children=[dcc.Graph(id="train", style={'display': 'inline-block'}, figure=fig_train),
        dcc.Graph(id="test", style={'display': 'inline-block'}, figure=fig_test)],
        style={'textAlign' : 'center'}),

    html.H4(children='Gradient Boosting Results', style={'text-align' : 'center', 'font-family':'verdana'}),
    html.P(f'Train Set Explained Variance  : {train_r2}', style={'text-align' : 'center', 'font-family':'verdana'}),
    html.P(f'Train Set RMSE                : {train_rmse}', style={'text-align' : 'center', 'font-family':'verdana'}),
    html.P(f'Test Set Explained Variance   : {test_r2}', style={'text-align' : 'center', 'font-family':'verdana'}),
    html.P(f'Test Set RMSE                 : {test_rmse}', style={'text-align' : 'center', 'font-family':'verdana'})
])

if __name__ == "__main__":
    app.run_server(host="0.0.0.0", port=8050, debug=True)


