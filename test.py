import dash
from dash import dcc, html
import plotly.express as px
import pandas as pd
import ssl
ssl._create_default_https_context = ssl._create_unverified_context

app = dash.Dash()

df = pd.read_csv("movie_metadata.csv")
numerical = [c for c in df.columns if df[c].dtype != 'object']
categorical = [c for c in df.columns if df[c].dtype == 'object']

# changing object type to category
for c in categorical:
    df[c] = df[c].astype('category')

fig = px.scatter(
    df,
    x="budget",
    y="gross",
    size="content_rating",
    # color="language",
    # hover_name="country",
    log_x=True,
    size_max=60
)

app.layout = html.Div(children = [
html.H1(children='Movies Dashboard'),
dcc.Graph(id="budget_vs_gross", figure=fig)])



if __name__ == "__main__":
    app.run_server(debug=True)