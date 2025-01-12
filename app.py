import pandas as pd
import streamlit as st
import plotly.express as px
import altair as alt
import matplotlib.pyplot as plt
import numpy as np
from st_social_media_links import SocialMediaIcons

#import taipy.gui.builder as tbg
st.set_page_config(page_title="General Elections 2018",
                   page_icon="images/icon.webp",
                layout="wide")
@st.cache_data
def load_data():
    df = pd.read_excel(
        io ='ge2018_results.xlsx',
        engine ='openpyxl',
        sheet_name = 'ge2018_results',
        usecols='A:L',
        nrows = 3429
    )
    return df    
    
df = load_data()
records = df.shape[0]
df_list_candidates = df
df_returned_candidates = df[(df['Valid_Votes'] != 0)]

df = df.reset_index(drop=True)  # Drop the old index
df.index = df.index + 1  # Add 1 to each index
if 'title' not in st.session_state:
    st.session_state['title'] = 'Pakistan'
st.title("General Elections 2018")
title = "Pakistan"
#st.title(f":blue[{st.session_state['title']}]")     
with st.sidebar:
    filter_selection = st.radio(
            "",
            ["By District", "By Constituency"],
            key="visibility",
            horizontal=True,
        )
    
    if filter_selection == "By District":
        district_options = ['ALL'] + list(df['District'].unique()) 
        district = st.selectbox (
            "Select District",
            options =district_options ,
            index = 0
            #index=district_options.index(df['District'].unique()[0])  # Set default to the first district
        )

        if district == "ALL":
            st.session_state['title'] = "Pakistan"
            df = load_data()
            df_returned_candidates = df[(df['Valid_Votes'] != 0)]
            df_list_candidates = df
        else:
            st.session_state['title'] = district
            df = df[df['District'] == district]
            df_returned_candidates = df[(df['Valid_Votes'] != 0) & (df['District'] == district)]
            df_list_candidates = df[df['District'] == district]

    if filter_selection == "By Constituency":
        constituency_options= ['ALL'] + df['Constituency'].unique().tolist()

        constituency = st.selectbox (
            "Select Constituency",
            options =constituency_options ,
            index = 0
            #index=constituency_options.index(df['Constituency'].unique()[0])  # Set default to the first district
        ) 

        if constituency == "ALL":
            st.session_state['title']="Pakistan"
            df = load_data()
            df_returned_candidates = df[(df['Valid_Votes'] != 0)]
            df_list_candidates = df
        else:
            st.session_state['title'] = constituency
            df = df[df['Constituency'] == constituency]
            df_returned_candidates = df[(df['Valid_Votes'] != 0) & (df['Constituency'] == constituency)]
            df_list_candidates = df[df['Constituency'] == constituency]
st.title(f":blue[{st.session_state['title']}]")     
tab_overall, tab_contesting, tab_successful, tab_party01, tab_party02, tab_about = st.tabs(
        ["Overall Summary",
         "Contesting Candidates",
         "Successful Candidates",
         "Party Position [By Votes]",
         "Party Position [By Seats]",
        "About"
        ])

# Display dashboards based on selection
with tab_overall:
           
    col1, col2, col3 = st.columns(3)
    with col1:
        st.subheader(f"Registered Voters")
        st.subheader(f":blue[{df['Total_Registered_Voters'].sum():,}]")
        st.subheader("Votes Cast")
        st.subheader(f":blue[{df['Total_Votes'].sum():,}]")
    with col2:
        st.subheader("Valid Votes")
        st.subheader(f":blue[{df['Valid_Votes'].sum():,}]")
        st.subheader("Rejected Votes")
        st.subheader(f":blue[{df['Rejected_Votes'].sum():,}]")
    with col3:
        st.subheader("Turnout")
        turnout = df['Total_Votes'].sum() / df['Total_Registered_Voters'].sum() * 100
        turnout = round(turnout, 2)
        st.subheader(f":blue[{turnout}%]")

with tab_contesting:
    records = df_list_candidates.shape[0]
    
    col1, col2 = st.columns(2)
    with col1:
        st.subheader(f"List of Candidates")
    with col2:
        st.subheader(f":blue[{records}]")
    st.dataframe(df_list_candidates[['Constituency',  'Description', 'Candidate', 'Party', 'Votes']])

with tab_successful:
    st.subheader("Successful Candidates")
    st.dataframe(df_returned_candidates[['Constituency', 'Description', 'Candidate', 'Party', 'Votes']])

with tab_party01:
    st.subheader("No. of votes obtained by each Party [Top 10]")
    df_party01 = df.groupby('Party')['Votes'].sum().reset_index()
    df_top10 = df_party01.sort_values(by='Votes', ascending=False).head(10)
    df_top10 = df_top10[df_top10['Party'].notnull()]
    df_top10 = df_top10[df_top10['Party'] != '']
    df_top10 = df_top10.reset_index(drop=True) 
    df_top10.index = df_top10.index + 1 
    widths = [50, 150, 200]
    
    fig = px.pie(
        df_top10, 
        values='Votes', 
        names='Party',            
        hole=0.3
    )
    fig.update_traces(
        textinfo='percent+value', 
        textfont_size=12, 
        marker=dict(line=dict(color='#000000', width=1)) 
        )

    st.plotly_chart(fig, use_container_width=True)
    st.dataframe(df_top10,  width=sum(widths))

with tab_party02:
    st.subheader("Seats won by each Party [Top 10]")
    df_party02 = df[df['Valid_Votes'] != 0]
    df_party02 = df_party02.groupby('Party')['Constituency'].count().reset_index()
    df_top10 = df_party02.sort_values(by='Constituency', ascending=False).head(10)
    df_top10 = df_top10[df_top10['Party'].notnull()]
    df_top10 = df_top10[df_top10['Party'] != '']
    df_top10 = df_top10.reset_index(drop=True) 
    df_top10.index = df_top10.index + 1 
    widths = [50, 150, 200]
    
    df_top10['Party'] = df_top10['Party'].str.strip() 
    fig = px.pie(
        df_top10, 
        values='Constituency', 
        names='Party',
        hole=0.3
        )

    fig.update_traces(
        textinfo='percent+value', 
        textfont_size=14, 
        marker=dict(line=dict(color='#000000', width=1)) 
        )
    st.plotly_chart(fig, use_container_width=True)
    st.dataframe(df_top10,  width=sum(widths))

with tab_about:
    st.subheader("Developed By Haider Ali")
    st.write("A Python Developer")
    social_media_links = [
        "https://www.linkedin.com/in/haiderkhalil",
        "https://www.medium.com/@haiderkhalil",
        "https://www.x.com/haiderhalil",
        "https://www.facebook.com/haideralikhalil",
        "https://www.youtube.com/@towncoder",
        "https://www.github.com/haideralikhalil",
        "https://wa.me/00923219032716"
    ]
    social_media_icons = SocialMediaIcons(social_media_links)

    social_media_icons.render()  
    st.divider()
    st.video("https://youtu.be/ZlLtP16jIM4") 
    st.write("Disclaimer: This is not official app of Election Commission of Pakistan.")
    st.image("haider.png")        

