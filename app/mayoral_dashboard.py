import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import os
from datetime import datetime

# Load your data
# (Assume df is pre-loaded or read from a CSV)
@st.cache_data
def load_data():
    # Read with error handling
    try:
        df = pd.read_csv("data/nyc_campaign_contributions_full.csv", low_memory=False)
    except Exception as e:
        st.error(f"Error loading data: {e}")
        # Load with fallback options
        df = pd.read_csv("data/nyc_campaign_contributions_full.csv", 
                        low_memory=False, 
                        on_bad_lines='skip')
    return df

df = load_data()

# Filter to mayoral race and most recent election
campaign_donations = df.copy()
mayoral_df = campaign_donations[campaign_donations['officecd'] == 1]
most_recent_year = mayoral_df['election'].max()
mayoral_df = mayoral_df[mayoral_df['election'] == most_recent_year]

# Group and aggregate
grouped = mayoral_df.groupby('recipname').agg(
    total_contributions=('amnt', 'sum'),
    total_matched=('matchamnt', 'sum')
).reset_index()

grouped['unmatched'] = grouped['total_contributions'] - grouped['total_matched']

# Sidebar - Threshold slider
st.sidebar.title("Filters")
threshold = st.sidebar.slider(
    "Minimum Total Contributions ($)", 
    min_value=0, 
    max_value=int(grouped['total_contributions'].max()), 
    step=1000, 
    value=0
)

# Filter based on slider
filtered = grouped[grouped['total_contributions'] > threshold].copy()
filtered = filtered.sort_values('total_contributions', ascending=False)
filtered['recipname'] = pd.Categorical(filtered['recipname'], categories=filtered['recipname'], ordered=True)

# Melt for stacked bar
melted = filtered.melt(
    id_vars='recipname', 
    value_vars=['total_matched', 'unmatched'],
    var_name='Type', value_name='Amount'
)

# Plot
st.title(f"NYC Mayoral Contributions in {most_recent_year}")
st.write(f"Showing candidates with total contributions over **${threshold:,}**")

sns.set(style="whitegrid")
plt.figure(figsize=(14, 7))
palette = {'total_matched': '#4c72b0', 'unmatched': '#dd8452'}
ax = sns.barplot(data=melted, x='recipname', y='Amount', hue='Type', palette=palette)
plt.title(f"Mayoral Race Contributions in {most_recent_year}")
plt.xlabel("Candidate")
plt.ylabel("Total Contributions ($)")
plt.xticks(rotation=45, ha='right')
plt.legend(title="Contribution Type")
plt.tight_layout()
st.pyplot(plt)

# Get the last modification time of your data file
def get_last_update_time():
    try:
        data_file = "data/nyc_campaign_contributions_full.csv"
        if os.path.exists(data_file):
            mtime = os.path.getmtime(data_file)
            return datetime.fromtimestamp(mtime)
        return None
    except:
        return None

# Get the most recent contribution date
def get_most_recent_contribution():
    try:
        df = pd.read_csv("data/nyc_campaign_contributions_full.csv", low_memory=False)
        if 'date' in df.columns:
            # Convert date column to datetime
            df['date'] = pd.to_datetime(df['date'], errors='coerce')
            most_recent = df['date'].max()
            return most_recent
        return None
    except Exception as e:
        st.error(f"Error reading data: {e}")
        return None

# Add this to your sidebar
st.sidebar.markdown("---")
st.sidebar.subheader("Data Status")

last_update = get_last_update_time()
most_recent = get_most_recent_contribution()

if last_update:
    st.sidebar.success(f" Data last updated: {last_update.strftime('%B %d, %Y at %I:%M %p')}")
    
    # Calculate how old the data is
    age = datetime.now() - last_update
    if age.days == 0:
        st.sidebar.info("🟢 Data is fresh (updated today)")
    elif age.days == 1:
        st.sidebar.warning("🟡 Data is 1 day old")
    else:
        st.sidebar.error(f" Data is {age.days} days old")

if most_recent:
    st.sidebar.info(f"📅 Most recent contribution: {most_recent.strftime('%B %d, %Y')}")
