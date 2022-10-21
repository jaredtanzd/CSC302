import dash
from dash import dcc, html
import plotly.express as px
import pandas as pd
import ssl
import os

ssl._create_default_https_context = ssl._create_unverified_context

app = dash.Dash()

path = os.getcwd()
df = pd.read_csv(path + "/src/movie_metadata.csv")
numerical = [c for c in df.columns if df[c].dtype != 'object']
categorical = [c for c in df.columns if df[c].dtype == 'object']

# changing object type to category
for c in categorical:
    df[c] = df[c].astype('category')

# cleaning data

fig = px.scatter(
    df,
    x="budget",
    y="gross",
    # size="content_rating",
    # color="language",
    hover_name="movie_title",
    log_x=True,
    size_max=60
)

app.layout = html.Div(children = [
html.H1(children='Movies Dashboard'),
dcc.Graph(id="budget_vs_gross", figure=fig)])



if __name__ == "__main__":
    app.run_server(host="0.0.0.0", port=8050, debug=True)


