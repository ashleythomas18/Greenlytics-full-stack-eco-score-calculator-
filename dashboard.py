import pandas as pd
from dash import Dash, dcc, html
import plotly.express as px
from flask import Flask, send_from_directory

server = Flask(__name__)

@server.route("/index.html")
def serve_index():
    return send_from_directory("templates", "index.html")

df = pd.read_csv("sentiment.csv")

app = Dash(__name__, server=server)

app.layout = html.Div(
    style={
        "backgroundColor": "#121212",
        "color": "white",
        "padding": "20px",
        "fontFamily": "Segoe UI, sans-serif"
    },
    children=[
        html.Div(
            style={
                "display": "flex",
                "justifyContent": "space-between",
                "alignItems": "center",
                "padding": "10px 20px",
                "backgroundColor": "#1e1e1e",
                "marginBottom": "30px",
                "borderRadius": "10px"
            },
            children=[
                html.H2("EcoSentiment Dashboard", style={"margin": "0"}),
                html.A("Home", href="/index.html", style={
                    "color": "#00FFAA", "textDecoration": "none", "fontWeight": "bold"
                })
            ]
        ),

        html.H1("ML-Powered Sentiment Analysis", style={"textAlign": "center"}),

        # Bar chart
        dcc.Graph(
            id="eco-points-bar-chart",
            figure=px.bar(
                df,
                x="User Name",
                y="Total Points",
                title="Total Points by User",
                labels={"User Name": "User", "Total Points": "Points"},
                color="Total Points",
                color_continuous_scale=px.colors.sequential.Viridis,
            ).update_layout(
                title_x=0.5,
                plot_bgcolor="#121212",
                paper_bgcolor="#121212",
                font_color="white"
            )
        ),

        # Pie chart
        dcc.Graph(
            id="eco-vs-noneco-pie",
            figure=px.pie(
                df,
                names="Product Type",
                title="Eco vs Non-Eco Product Preference",
                color_discrete_sequence=px.colors.sequential.Viridis
            ).update_traces(textinfo="percent+label")
            .update_layout(
                title_x=0.5,
                plot_bgcolor="#121212",
                paper_bgcolor="#121212",
                font_color="white"
            )
        ),

        # Line chart
        dcc.Graph(
            id="trend-line-chart",
            figure=px.line(
                df,
                x="Date",  
                y="Total Points",
                title="Eco Points Over Time",
                markers=True,
                line_shape="spline",
                color_discrete_sequence=["#00FFAA"]
            ).update_layout(
                title_x=0.5,
                plot_bgcolor="#121212",
                paper_bgcolor="#121212",
                font_color="white",
                xaxis=dict(showgrid=False),
                yaxis=dict(showgrid=True, gridcolor="#444")
            )
        ),

        

        # Insights
        # html.Div(
        #     style={"marginTop": "30px"},
        #     children=[
        #         html.H3("Actionable Insights", style={"textAlign": "center"}),
        #         html.Ul([
        #             html.Li("Reward users with high eco points."),
        #             html.Li("Track sentiment trends to guide future decisions."),
        #             html.Li("Motivate low scorers with campaigns and badges.")
        #         ])
        #     ]
        # )
    ]
)

if __name__ == "__main__":
    app.run(debug=True)
