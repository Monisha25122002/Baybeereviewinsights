import dash
from dash import html, dcc
import pandas as pd
import plotly.express as px
from dash.dependencies import Input, Output

# Load data
df = pd.read_excel("reviews_with_sentiment.xlsx")

# Initialize app
app = dash.Dash(__name__)
server = app.server

# Dropdown options
category_options = ["All"] + sorted(df["Category"].dropna().unique().tolist())
sentiment_options = ["All"] + sorted(df["Sentiment"].dropna().unique().tolist())

# Layout
app.layout = html.Div([
    # Top: Logo and Title
    html.Div([
        html.Img(src="/assets/baybee logo.png", style={"height": "60px", "marginRight": "20px"}),
        html.H1("BayBee Review Sentiment Analysis Dashboard", style={
            'backgroundColor': 'lightgreen',
            'padding': '10px',
            'borderRadius': '10px',
            'textAlign': 'center',
            'width': '100%'
        }),
    ], style={"display": "flex", "alignItems": "center", "marginBottom": "20px", "justifyContent": "center"}),

    # Main layout with sidebar and dashboard
    html.Div([
        # Sidebar filters
        html.Div([
            html.Label("Select Product Category"),
            dcc.Dropdown(
                id="category-dropdown",
                options=[{"label": c, "value": c} for c in category_options],
                value=["All"],
                multi=True,
                style={"marginBottom": "20px"}
            ),

            html.Label("Select Sentiment"),
            dcc.Dropdown(
                id="sentiment-dropdown",
                options=[{"label": s, "value": s} for s in sentiment_options],
                value=["All"],
                multi=True,
                style={"marginBottom": "20px"}
            ),

            html.Label("Select Date Range"),
            dcc.DatePickerRange(
                id="date-picker",
                min_date_allowed=df["Review_Date"].min().date(),
                max_date_allowed=df["Review_Date"].max().date(),
                start_date=df["Review_Date"].min().date(),
                end_date=df["Review_Date"].max().date(),
                style={"marginBottom": "20px"}
            )
        ], style={
            "width": "15%",
            "padding": "40px",  # Increased padding
            "backgroundColor": "#f0f0f0",
            "borderRadius": "10px",
            "marginRight": "20px"
        }),

        # Dashboard content
        html.Div([
            # Metrics
            html.Div(id="metrics-div", style={
                "display": "flex",
                "justifyContent": "space-between",
                "marginBottom": "50px",  # More spacing
                "gap": "20px"  # Additional spacing between cards
            }),

            # Row 1
            html.Div([
                html.Div(dcc.Graph(id="pie-chart"), className="chart-box", style={"width": "48%", "display": "inline-block"}),
                html.Div(dcc.Graph(id="bar-chart"), className="chart-box", style={"width": "48%", "display": "inline-block", "marginLeft": "4%"})
            ], style={"marginBottom": "20px"}),

            # Row 2
            html.Div([
                html.Div(dcc.Graph(id="trend-chart"), className="chart-box", style={"width": "48%", "display": "inline-block"}),
                html.Div(dcc.Graph(id="avg-rating-chart"), className="chart-box", style={"width": "48%", "display": "inline-block", "marginLeft": "4%"})
            ], style={"marginBottom": "20px"}),

            # Row 3
            html.Div([
                html.Div(dcc.Graph(id="time-series-chart"), className="chart-box", style={"width": "100%"})
            ], style={"marginBottom": "20px"}),

            # Row 4
            html.Div([
                html.Div(dcc.Graph(id="category-sentiment-chart"), className="chart-box", style={"width": "100%"})
            ])
        ], style={"width": "78%"})
    ], style={"display": "flex"}),

], style={"backgroundColor": "lightgreen", "padding": "20px"})


# Callback
@app.callback(
    Output("metrics-div", "children"),
    Output("pie-chart", "figure"),
    Output("bar-chart", "figure"),
    Output("trend-chart", "figure"),
    Output("avg-rating-chart", "figure"),
    Output("time-series-chart", "figure"),
    Output("category-sentiment-chart", "figure"),
    Input("category-dropdown", "value"),
    Input("sentiment-dropdown", "value"),
    Input("date-picker", "start_date"),
    Input("date-picker", "end_date")
)
def update_dashboard(selected_categories, selected_sentiments, start_date, end_date):
    filtered_df = df.copy()

    # Apply category filter
    if selected_categories and "All" not in selected_categories:
        filtered_df = filtered_df[filtered_df["Category"].isin(selected_categories)]

    # Apply sentiment filter
    if selected_sentiments and "All" not in selected_sentiments:
        filtered_df = filtered_df[filtered_df["Sentiment"].isin(selected_sentiments)]

    # Apply date filter
    if start_date and end_date:
        filtered_df = filtered_df[
            (filtered_df["Review_Date"] >= pd.to_datetime(start_date)) &
            (filtered_df["Review_Date"] <= pd.to_datetime(end_date))
        ]

    # Metrics
    pos = (filtered_df["Sentiment"] == "Positive").sum()
    neu = (filtered_df["Sentiment"] == "Neutral").sum()
    neg = (filtered_df["Sentiment"] == "Negative").sum()
    total = pos + neu + neg

    if total == 0:
        return (
            html.Div("No data available for selected filters.", style={"color": "red", "fontWeight": "bold"}),
            px.pie(), px.bar(), px.bar(), px.bar(), px.line(), px.bar()
        )

    metrics = [
        html.Div([
            html.H4("👍 Positive"),
            html.H2(f"{(pos/total)*100:.1f}%")
        ], style={"backgroundColor": "#00CC96", "padding": "25px", "borderRadius": "10px", "width": "30%", "textAlign": "center", "color": "white"}),

        html.Div([
            html.H4("😐 Neutral"),
            html.H2(f"{(neu/total)*100:.1f}%")
        ], style={"backgroundColor": "#636EFA", "padding": "25px", "borderRadius": "10px", "width": "30%", "textAlign": "center", "color": "white"}),

        html.Div([
            html.H4("👎 Negative"),
            html.H2(f"{(neg/total)*100:.1f}%")
        ], style={"backgroundColor": "#EF553B", "padding": "25px", "borderRadius": "10px", "width": "30%", "textAlign": "center", "color": "white"}),
    ]

    # Charts
    pie_fig = px.pie(filtered_df, names="Sentiment", title="Sentiment Distribution",
                     color="Sentiment",
                     color_discrete_map={"Positive": "#00CC96", "Neutral": "#636EFA", "Negative": "#EF553B"})

    negative_reviews = filtered_df[filtered_df["Sentiment"] == "Negative"]
    word_counts = negative_reviews["Review_Text"].str.split(expand=True).stack().value_counts().reset_index()
    word_counts.columns = ["Word", "Count"]
    top_words = word_counts.head(10)
    bar_fig = px.bar(top_words, x="Word", y="Count", title="Top 10 Complaint Words", color_discrete_sequence=["#1f77b4"])

    product_sentiment = filtered_df.groupby(["Product_Name", "Sentiment"]).size().reset_index(name="Count")
    trend_fig = px.bar(product_sentiment, x="Product_Name", y="Count", color="Sentiment",
                       title="Product-wise Sentiment", barmode="group",
                       color_discrete_map={"Positive": "#00CC96", "Neutral": "#636EFA", "Negative": "#EF553B"})

    avg_rating = filtered_df.groupby("Category")["Rating"].mean().reset_index()
    rating_fig = px.bar(avg_rating, x="Category", y="Rating", title="Average Rating by Category",
                        color_discrete_sequence=["#636EFA"])

    review_counts = filtered_df.groupby(filtered_df["Review_Date"].dt.to_period("M")).size().reset_index(name="Counts")
    review_counts["Review_Date"] = review_counts["Review_Date"].dt.to_timestamp()
    time_fig = px.line(review_counts, x="Review_Date", y="Counts", title="Reviews Over Time",
                       line_shape='spline', markers=True, color_discrete_sequence=["#1f77b4"])

    category_sentiment = filtered_df.groupby(["Category", "Sentiment"]).size().reset_index(name="Counts")
    cat_sent_fig = px.bar(category_sentiment, x="Category", y="Counts", color="Sentiment",
                          barmode="group", title="Sentiment by Category",
                          color_discrete_map={"Positive": "#00CC96", "Neutral": "#636EFA", "Negative": "#EF553B"})

    return metrics, pie_fig, bar_fig, trend_fig, rating_fig, time_fig, cat_sent_fig


# Run app
if __name__ == "__main__":
    app.run(debug=True, use_reloader=False)