import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

# Load your data
# (Assume df is pre-loaded or read from a CSV)
@st.cache_data
def load_data():
    df = pd.read_csv("data/nyc_campaign_contributions_full.csv")  # <- Replace with your actual CSV
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
