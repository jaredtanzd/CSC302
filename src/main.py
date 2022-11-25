import dash
from dash import dcc, html
from dash.dependencies import Input, Output, State
import plotly.express as px
import numpy as np
import pandas as pd
import ssl
import os

import data
import model

ssl._create_default_https_context = ssl._create_unverified_context
app = dash.Dash()

path = os.getcwd()
df_raw = pd.read_csv(path + "/src/movie_metadata.csv")

df_first, categorical, numerical, genres = data.dataEngineering(df_raw)
df_final = data.dataMerged(df_first, categorical, genres)
model, y_train, y_test, y_train_pred, y_test_pred, train_rmse, train_r2, test_rmse, test_r2 = model.ML_model(df_final, numerical) 

plot_df_train = pd.concat([y_train, pd.DataFrame(y_train_pred).set_index(y_train.index)], axis=1)
plot_df_test = pd.concat([y_test, pd.DataFrame(y_test_pred).set_index(y_test.index)], axis=1)
plot_df_train.columns = ['Gross Actual (Train)', 'Gross Predicted (Train)']
plot_df_test.columns = ['Gross Actual (Test)', 'Gross Predicted (Test)']

sel_features = {'num_voted_users' : [], 'budget': [], 'num_critic_for_reviews':[], 'imdb_score':[], 'gross':[]}
for feature, _ in sel_features.items():
    for q in [0.25,0.5,0.75]:
        sel_features[feature].append(df_final[feature].quantile(q))
print(sel_features)

fig_main = px.scatter(
    df_first,
    x="budget",
    y="gross",
    size="num_voted_users",
    color="content_rating",
    hover_name="movie_title",
    log_x=True
)

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
    
    html.H3(children='Gradient Boosting Model Results', style={'text-align' : 'center', 'font-family':'verdana'}),
    html.Center(children=[dcc.Graph(id="train", style={'display': 'inline-block'}, figure=fig_train)],style={'textAlign' : 'center'}),
    html.P(f'Train Set Explained Variance  : {round(train_r2,2)}', style={'text-align' : 'center', 'font-family':'verdana'}),
    html.P(f'Train Set RMSE                : {round(train_rmse,2)}', style={'text-align' : 'center', 'font-family':'verdana'}),

    html.Center(children=[dcc.Graph(id="test", style={'display': 'inline-block'}, figure=fig_test)],
        style={'textAlign' : 'center'}),
    html.P(f'Test Set Explained Variance   : {round(test_r2,2)}', style={'text-align' : 'center', 'font-family':'verdana'}),
    html.P(f'Test Set RMSE                 : {round(test_rmse,2)}', style={'text-align' : 'center', 'font-family':'verdana'}),


    ## Input movie features 
    html.H3(children='Input your Movie Features!', style={'text-align' : 'center', 'font-family':'verdana'}),
    html.Div(["Number of users who voted: ", dcc.Input(id='voted-input', type='text')],
        style={'text-align' : 'center', 'font-family':'verdana'}),
    html.Div(["IMDB Score: ", dcc.Input(id='imdb-input', type='text')],
        style={'text-align' : 'center', 'font-family':'verdana'}),
    html.Div(["Number of critic reviews: ", dcc.Input(id='critic-input', type='text')],
        style={'text-align' : 'center', 'font-family':'verdana'}),
    html.Div(["Budget: ",dcc.Input(id='budget-input', type='text')],
        style={'text-align' : 'center', 'font-family':'verdana'}),
    html.Div(["Genres: ", dcc.Dropdown(['Others','Family'], placeholder="Select a genre", id='genres-dropdown')], 
        style={'align': 'center', 'font-family':'verdana'}),
    html.Button('Submit', id='submit-button', n_clicks=0),
    html.H1(id='output-container', style={'text-align': 'center', 'font-family':'verdana'}),

])

@app.callback(
    Output(component_id='output-container', component_property='children'),
    [Input(component_id='submit-button', component_property='n_clicks')],
    [State(component_id='budget-input', component_property='value')],
    [State(component_id='imdb-input', component_property='value')],
    [State(component_id='critic-input', component_property='value')],
    [State(component_id='voted-input', component_property='value')],
    [State(component_id='genres-dropdown', component_property='value')],
    prevent_initial_call = True
)
def update(n, budget, imdb, critic, voted, genres):
    print(n)
    if n > 0 and int(budget) > 0 and int(imdb) > 0 and int(critic)  > 0 and int(voted) > 0:
        if  genres ==  'Family':
            family = 1.0
        else:
            family = 0.0

        voted_final = (float(voted) - sel_features['num_voted_users'][1]) / (sel_features['num_voted_users'][2] - sel_features['num_voted_users'][0])
        budget_final = (float(budget) - sel_features['budget'][1]) / (sel_features['budget'][2] - sel_features['budget'][0])
        critic_final = (float(critic) - sel_features['num_critic_for_reviews'][1]) / (sel_features['num_critic_for_reviews'][2] - sel_features['num_critic_for_reviews'][0])
        imdb_final = (float(imdb) - sel_features['imdb_score'][1]) / (sel_features['imdb_score'][2] - sel_features['imdb_score'][0])

        print(voted_final, budget_final, critic_final, imdb_final)

        x_new = np.array([voted_final, budget_final, critic_final, family, imdb_final]).reshape(1, -1)
        y_new = model.predict(x_new)

        gross = (y_new[0] *  (sel_features['gross'][2] - sel_features['gross'][0])) + sel_features['gross'][1]

        return f'Your gross revenue is ${round(gross, 3)}'
    
    else:
        return 'Please input a proper value'


if __name__ == "__main__":
    app.run_server(host="0.0.0.0", port=8050, debug=True)


