import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pandas as pd
import streamlit as st
import altair as alt
import plotly.express as px

alt.themes.enable("dark")

##################################
# Page configuration
st.set_page_config(
    page_title="News analysis",
    page_icon=":newspaper:",
    layout="wide",
    initial_sidebar_state="expanded",
)

# path where the data is stored
data_path = 'data/findings/'

#######################
# CSS styling
st.markdown("""
<style>

[data-testid="block-container"] {
    padding-left: 2rem;
    padding-right: 2rem;
    padding-top: 1rem;
    padding-bottom: 0rem;
    margin-bottom: -7rem;
}

[data-testid="stVerticalBlock"] {
    padding-left: 0rem;
    padding-right: 0rem;
}

[data-testid="stMetric"] {
    background-color: #393939;
    text-align: center;
    padding: 15px 0;
}

[data-testid="stMetricLabel"] {
  display: flex;
  justify-content: center;
  align-items: center;
}

[data-testid="stMetricDeltaIcon-Up"] {
    position: relative;
    left: 38%;
    -webkit-transform: translateX(-50%);
    -ms-transform: translateX(-50%);
    transform: translateX(-50%);
}

[data-testid="stMetricDeltaIcon-Down"] {
    position: relative;
    left: 38%;
    -webkit-transform: translateX(-50%);
    -ms-transform: translateX(-50%);
    transform: translateX(-50%);
}

</style>
""", unsafe_allow_html=True)

#######################
# Load data
# df_reshaped = pd.read_csv('../data/findings/tags_count.csv')

#######################
# Sidebar
with st.sidebar:
    st.title(':newspaper: News analysis Dashboard')


    color_theme_list = ['blues', 'cividis', 'greens', 'inferno', 'magma', 'plasma', 'reds', 'rainbow', 'turbo',
                        'viridis']
    selected_color_theme = st.selectbox('Select a color theme', color_theme_list)


#######################

def load_data(file_path):
    news_data = pd.read_csv(file_path)
    return news_data


alt.themes.enable("dark")

import altair as alt

def create_headline_tag_chart(tags_df):
    st.markdown('##### Headlines tags')
    chart = alt.Chart(tags_df).mark_bar().encode(
        x=alt.X('Tag:N', title='Tag'),
        y=alt.Y('Count:Q', title='Count'),
        tooltip=['Tag', 'Count']
    ).properties(
        width=700,
        height=500
    )
    st.altair_chart(chart)


# plot a pie chart of the common countries with articles written about them
def create_countries_most_common_pie_chart_from_csv(file_path):
    # Read the CSV file into a DataFrame
    df = pd.read_csv(file_path)

    st.markdown('##### Countries and cities with most articles written about them')

    # Create the pie chart
    pie_chart = alt.Chart(df).transform_window(
        startAngle='sum(Count)',
        endAngle='sum(Count)',
        sort=[alt.SortField('Count')],
        frame=[None, 0]
    ).mark_arc().encode(
        alt.Theta('Count:Q', stack=True, sort=alt.SortField('order'), title=None),
        alt.Color('Country:N', legend=alt.Legend(title='Countries/Cities')),
        alt.Tooltip(['Country:N', 'Count:Q'])
    ).properties(
        width=350,
        height=350,
        title='Countries and cities with most articles written about them'
    )

    st.altair_chart(pie_chart)

def create_choropleth_map(file_path):
    # Read the CSV file into a DataFrame
    df = pd.read_csv(file_path)

    choropleth = px.choropleth(df, locations='Country', color='Count',
                               locationmode="country names",
                               color_continuous_scale='blues',
                               range_color=(0, max(df['Count'])),
                               labels={'Count':'Number of Articles'}
                              )
    choropleth.update_layout(
        template='plotly_dark',
        plot_bgcolor='rgba(0, 0, 0, 0)',
        paper_bgcolor='rgba(0, 0, 0, 0)',
        margin=dict(l=0, r=0, t=0, b=0),
        height=450
    )

    return choropleth

def create_global_rank_report_scatter_graph(global_rank_reports_sentiment):

    final_data_top_10000 = global_rank_reports_sentiment[global_rank_reports_sentiment['GlobalRank'] <= 10000]

    # Create a scatter plot
    scatter = alt.Chart(final_data_top_10000).mark_circle(size=60).encode(
        x='total_reports:Q',
        y='GlobalRank:Q',
        color=alt.Color('title_sentiment:Q', scale=alt.Scale(scheme='blueorange')),
        tooltip=['Domain:N', 'total_reports:Q', 'GlobalRank:Q', 'title_sentiment:Q']
    ).properties(
        width=800,
        height=600,
        title='Impact of Frequent News Reporting and Sentiment on Website\'s Global Ranking'
    )

    return scatter

def create_sentiment_chart(title_sentiment_stats):
    # Round the sentiment values to two decimal places
    title_sentiment_stats['title_sentiment'] = title_sentiment_stats['title_sentiment'].round(2)

    # Sort the DataFrame by the 'title_sentiment' column in descending order
    title_sentiment_stats = title_sentiment_stats.sort_values('title_sentiment', ascending=False)

    st.dataframe(title_sentiment_stats,
                 column_order=("source_name", "title_sentiment"),
                 hide_index=True,
                 width=None,
                 column_config={
                     "source_name": st.column_config.TextColumn(
                         "Source Name",
                     ),
                     "title_sentiment": st.column_config.ProgressColumn(
                         "Title Sentiment",
                         format="%f",
                         min_value=min(title_sentiment_stats['title_sentiment']),
                         max_value=max(title_sentiment_stats['title_sentiment']),
                     )}
                 )

def graph_of_countries_with_articles_written_about_them(tags_df, top_N):
    st.markdown('##### Top 10 tags in the headlines')
    # Remove the "Other" tag for meaningful analysis
    tags_df = tags_df[tags_df['Tag'] != 'Other']

    # Select the top 10 tags
    tags_df = tags_df.head(top_N)

    st.dataframe(tags_df,
                 column_order=("Tag", "Count"),
                 hide_index=True,
                 width=None,
                 column_config={
                     "Tag": st.column_config.TextColumn(
                         "Tag",
                     ),
                     "Count": st.column_config.ProgressColumn(
                         "Count",
                         format="%f",
                         min_value=0,
                         max_value=max(tags_df['Count']),
                     )}
                 )

def main():
    st.title('News Analysis Dashboard')

    # Load the data
    tags_df = load_data(data_path + 'tags_count.csv')

    choropleth = create_choropleth_map(data_path + 'countries_in_articles.csv')
    # Load or calculate your title_sentiment_stats DataFrame here
    global_rank_reports_sentiment = pd.read_csv(data_path + 'global_rank_sentiment_report.csv')

    # Create charts
    global_rank_report_graph = create_global_rank_report_scatter_graph(global_rank_reports_sentiment)


    # Create columns for the first row
    col1, col2 = st.columns((4.5, 2), gap='medium')

    # Plot the tag counts in the first column
    with col1:
        st.markdown("##### Countries with news articles written about them")
        st.plotly_chart(choropleth)

    # plot a graph of countries with articles written about them in the second column
    with col2:
        create_countries_most_common_pie_chart_from_csv(data_path + 'countries_most_common.csv')

    # Create columns for the second row
    col3, col4 = st.columns((4, 2), gap='medium')

    with col3:
        create_headline_tag_chart(tags_df)

    with col4:
        graph_of_countries_with_articles_written_about_them(tags_df, top_N=10)


    # Create columns for the third row
    col5, col6 = st.columns((4, 1.5), gap='medium')


    with col5:
        st.markdown("##### Impact of Frequent News Reporting and Sentiment on Website's Global Ranking")
        st.altair_chart(global_rank_report_graph)

    with col6:
        st.markdown("##### Sentiment of news article titles")
        create_sentiment_chart(global_rank_reports_sentiment)

    # Display the charts and graphs
    # st.altair_chart(sentiment_chart)
    # st.altair_chart(global_rank_report_graph)

    # Create a progress chart in the third column





if __name__ == '__main__':
    main()
