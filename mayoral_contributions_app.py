import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from datetime import date
import pandas as pd

# Set page config
st.set_page_config(page_title="2025 NYC Mayoral Campaign Contributions", layout="wide")

# Add a title
st.title("NYC Campaign Finance Data Visualization")

# Load and process data
@st.cache_data  # This caches the data to improve performance
def load_data():
    df = pd.read_csv('data/Contributions_20250212.csv')
    return df

# Load the data
df = load_data()
mayoral_2025 = df[df['OFFICECD'] == 1]
mayoral_2025 = mayoral_2025[mayoral_2025['ELECTION'] == 2025]


# plot mayoral contributions

# Prepare the data
contributions = mayoral_2025.groupby(['RECIPNAME'])['AMNT'].sum().reset_index()
matching = mayoral_2025.groupby(['RECIPNAME'])['MATCHAMNT'].sum().reset_index()


# Sort both dataframes by total contributions (descending for bottom-to-top display)
order = contributions.sort_values('AMNT', ascending=False)['RECIPNAME']
contributions = contributions.sort_values('AMNT', ascending=False)
matching = matching.set_index('RECIPNAME').reindex(order).reset_index()

# Create figure
fig = go.Figure()

# Add bars for contributions
fig.add_trace(go.Bar(
    x=contributions['AMNT'],
    y=contributions['RECIPNAME'],
    name='Contributions',
    orientation='h',
))

# Add bars for matching funds
fig.add_trace(go.Bar(
    x=matching['MATCHAMNT'],
    y=matching['RECIPNAME'],
    name='Match Contributions',
    orientation='h',
))

# Update layout
fig.update_layout(
    title=dict(
        text=f'2025 Mayoral Campaign Contributions To Date<br>updated {date.today()}',
        x=0.5,
        xanchor='center',
        yanchor='top'
    ),
    xaxis_title='',
    yaxis_title='Recipient',
    barmode='overlay',
    height=600,
    xaxis=dict(
        tickformat=',',
        side='top',  # Move x-axis labels to top
        title_standoff=25  # Add some space between title and axis
    ),
    yaxis=dict(
        categoryorder='array',
        categoryarray=order,
        autorange='reversed'
    ),
    hoverlabel=dict(
        bgcolor="white",
        font_size=16,
    ),
    showlegend=True,
    legend=dict(
        yanchor="bottom",  # Anchor legend to bottom
        y=0.01,           # Position near bottom
        xanchor="right",  # Anchor legend to right
        x=0.99            # Position near right edge
    )
)

fig.show()

# Display the plot
st.plotly_chart(fig, use_container_width=True)
