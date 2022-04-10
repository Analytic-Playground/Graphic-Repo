#!/usr/bin/env python
# coding: utf-8

# In[4]:


# packages
import pandas as pd 
import numpy as np 
import streamlit as st
from plotly.subplots import make_subplots
import plotly.graph_objects as go
import datetime as dt
import time


# In[2]:


# Read in data
covid_cases = pd.read_csv('data_table_for_daily_case_trends__the_united_states(1).csv', skiprows = 2)
covid_deaths = pd.read_csv('data_table_for_daily_death_trends__the_united_states.csv', skiprows = 2)
vaxx = pd.read_csv('trends_in_number_of_covid19_vaccinations_in_the_us.csv', skiprows = 2)


# In[3]:


# Clean Covid / Vaxx frames
def cleaning(data:pd.DataFrame):
        data['Date'] = pd.to_datetime(data['Date'])
        data['Month'] = pd.DatetimeIndex(data['Date']).month
        data['Year'] = pd.DatetimeIndex(data['Date']).year

        # Normalize & Agg time periods
        if 'New Deaths' in data.columns:
                # Roll up into weekly level
                data = data.groupby(['State']).resample('W-Wed', label='right', closed = 'right', on='Date').sum().reset_index().sort_values(by='Date')
                data['Normalized Deaths'] = (data['New Deaths'] - data['New Deaths'].min()) / (data['New Deaths'].max() - data['New Deaths'].min())
        elif 'New Cases' in data.columns:
                # Roll up into weekly level
                data = data.groupby(['State']).resample('W-Wed', label='right', closed = 'right', on='Date').sum().reset_index().sort_values(by='Date')
                data['Normalized Cases'] = (data['New Cases'] - data['New Cases'].min()) / (data['New Cases'].max() - data['New Cases'].min())
        elif 'Administered' in data.columns:
                pass
        else:
                print('Dataframe not recognized.')

        return data

covid_cases, covid_deaths, vaxx = cleaning(covid_cases), cleaning(covid_deaths), cleaning(vaxx)


# In[15]:


# Plot Covid
def plot(covid_cases:pd.DataFrame, covid_deaths:pd.DataFrame, vaxx:pd.DataFrame):
    # create figure
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    # plot covid cases
    fig.add_trace(go.Bar(
        x = covid_cases['Date'], 
        y = covid_cases['Normalized Cases'], 
        name = 'New Covid Cases',
        opacity = 1,
        marker_color = 'blue'
        # fill = 'tozeroy' # only for Scatter
    ))
    # Plot covid deaths
    fig.add_trace(go.Bar(
        x = covid_deaths['Date'], 
        y = covid_deaths['Normalized Deaths'],
        name = 'New Covid Deaths',
        opacity = 0.7,
        marker_color = 'red'
        # fill = 'tozeroy'
    ))
    # Plot Vaxxinations administered
    vaxx.loc[vaxx['Date'] == vaxx['Date'].max(), 'Administered'] = np.nan # rm latest month of data due to incompleteness
    fig.add_trace(go.Scatter(
        x = vaxx['Date'], 
        y = vaxx['Administered'], 
        marker = dict(symbol = 'square'),
        name = 'Vaccinations Administered',
    ),secondary_y = True)


    # Create axis objects
    fig.update_layout(title = {
                    'text':'COVID-19 Cases, Deaths, & Vaccinations', 
                    'x':0.4,
                    'xanchor':'center'
                    },
                    xaxis=dict(title = 'Time'),
                    yaxis=dict(title = 'Normalized Covid-19<br>Cases & Deaths',
                    side = 'left', 
                    position = 0.0000000000000000000000000025), 

                    yaxis2=dict(title = 'Vaccinations',
                    anchor = 'x', 
                    overlaying = 'y', 
                    side = 'right'),

                    yaxis3 = dict(title = 'Unemployment Rate<br>(%)',
                    anchor = 'x',
                    overlaying = 'y',
                    side = 'right'),
                    height = 450, 
                    width = 1100)

    # Omicron BA.1
    fig.add_annotation(x='2021-9-15', y=0.65,
                text="Omicron BA.1",
                showarrow=False,
                arrowhead=1)

    fig.add_shape(type="rect",
        xref="x", yref="y",
        x0="2021-8-1", y0=0.6, x1="2021-10-28", y1=0,
        line=dict(
            color="orange",
            width=3,
        ),
    )
    # Omicron BA.2
    fig.add_annotation(x='2022-1-28', y=1.05,
                text="Omicron BA.2",
                showarrow=True,
                arrowhead=1)

    fig.add_shape(type="rect",
        xref="x", yref="y",
        x0="2021-12-20", y0=1.02, x1="2022-2-28", y1=0,
        # opacity = 0.8,
        line=dict(
            color="yellow",
            width=3,
        ),
    )
    # Delta Identifier
    fig.add_annotation(x='2021-1-3', y=1.06,
                text="Delta Varient",
                showarrow=False,
                arrowhead=1)

    fig.add_shape(type="rect",
        xref="x", yref="y",
        x0="2020-11-15", y0=1.02, x1="2021-2-20", y1=0,
        # opacity = 0.8,
        line=dict(
            color="yellow",
            width=3,
        ),
    )

    note_subheader = "Notes: Due to the difference in scale between cases (peaks at 20M/daily for Omicron) and deaths (peaks at 5K/daily for Delta)<br>I have forced them down to the same scale to better comapre the trend between the two"
    note_footer = "Source: https://covid.cdc.gov/covid-data-tracker/<br>Graphic Created by: IG @makrieger212"
    fig.add_annotation(
        showarrow=False,
        text=note_subheader,
        font=dict(size=10), 
        xref='x domain',
        x=0.5,
        yref='y domain',
        y=1.15
        )
    fig.add_annotation(
        showarrow=False,
        text=note_footer,
        font=dict(size=10), 
        xref='x domain',
        x=0.5,
        yref='y domain',
        y=-0.29
        )
    # fig.update_yaxes(rangemode='tozero', scaleanchor='y2', scaleratio=1, constraintoward='bottom', secondary_y=True)
    # fig.update_yaxes(rangemode = 'tozero', scaleanchor='y1', scaleratio=1, constraintoward='bottom', secondary_y = False)
    fig['layout']['yaxis2']['showgrid'] = False
    fig.show()
    return fig
    # fig.write_html("covid file.html")
    # covid_deaths.head()


# In[16]:


fig = plot(covid_cases, covid_deaths, vaxx)


# In[12]:


st.plotly_chart(fig)


# In[14]:


import session_info

