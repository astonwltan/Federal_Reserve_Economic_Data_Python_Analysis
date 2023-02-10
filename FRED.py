import time
import plotly.express as px
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

# Creating the FRED Object
from fredapi import Fred
fred_key = 'e3fe2ec2f683dc789f99a16d1cc595e5'
fred = Fred(api_key=fred_key)
data = fred.get_series('SP500')

# Stylizing FRED Object & Plots
plt.style.use('fivethirtyeight')
pd.set_option('display.max_columns', 500)
color_pal = plt.rcParams["axes.prop_cycle"].by_key()["color"]

# Search FRED for Economic Data
# sp_search = fred.search('S&P', order_by='popularity')
# sp_search.head()

# Attempt at visualising tables on Matplotlib
# fig, ax = plt.subplots()
# df = pd.DataFrame(sp_search.head())

# ax.table(cellText=df.values, colLabels=df.columns)
# fig.tight_layout()
# plt.show()

# Pull Raw Data & Plot
# sp500 = fred.get_series(series_id='SP500')
# sp500.plot(figsize=(10, 5), title='S&P 500', lw=2)
# plt.show()  # Price of S&P 500 over Time

# ----------------------------------------------------------

# Pull and Join Multiple Data Series States' Unemployment Rate
unemp_df = fred.search('unemployment rate state',
                       filter=('frequency', 'Monthly'))
unemp_df = unemp_df.query(
    'seasonal_adjustment == "Seasonally Adjusted" and units == "Percent"')

# Shows num of columns and rows (SHAPE OF MATRIX)
# print(np.shape(unemp_df))

# More Filtering - When title contains Unemployment Rate (There's stuff that is loosely related to unemployment rate)
unemp_df = unemp_df.loc[unemp_df['title'].str.contains('Unemployment Rate')]

# Seeing IDs
# print(unemp_df.index)

all_results = []


for myid in unemp_df.index:

    if (len(myid) == 4):
        results = fred.get_series(myid)
        results = results.to_frame(name=myid)
        all_results.append(results)
    time.sleep(0.1)  # Don't request to fast and get blocked
uemp_results = pd.concat(all_results, axis=1)

uemp_states = uemp_results.copy()
uemp_states = uemp_states.dropna()  # removes rows that contain null values
id_to_state = unemp_df['title'].str.replace(
    'Unemployment Rate in ', '').to_dict()
uemp_states.columns = [id_to_state[c] for c in uemp_states.columns]

# fig = px.line(uemp_states)
# fig.show()


# ----------------------------------------------------------

# Find April 2020 Unemployment Rate Per State
ax = uemp_states.loc[uemp_states.index == '2020-05-01'].T \
    .sort_values('2020-05-01') \
    .plot(kind='barh', figsize=(8, 12), width=0.7, edgecolor='black',
          title='Unemployment Rate by State, May 2020')
ax.legend().remove()
ax.set_xlabel('% Unemployed')

# plt.show()

# ----------------------------------------------------------

# Pulling Participation Rate

part_df = fred.search('participation rate state',
                      filter=('frequency', 'Monthly'))
part_df = part_df.query(
    'seasonal_adjustment == "Seasonally Adjusted" and units == "Percent"')
part_id_to_state = part_df['title'].str.replace(
    'Labor Force Participation Rate for ', '').to_dict()

all_results = []

for myid in part_df.index:
    results = fred.get_series(myid)
    results = results.to_frame(name=myid)
    all_results.append(results)
    time.sleep(0.1)  # Slow request
part_states = pd.concat(all_results, axis=1)
part_states.columns = [part_id_to_state[c] for c in part_states.columns]

print(part_states)

###

uemp_states = uemp_states.rename(
    columns={'the District of Columbia': 'District Of Columbia'})
fig, axs = plt.subplots(10, 5, figsize=(30, 30), sharex=True)
axs = axs.flatten()

i = 0
for state in uemp_states.columns:
    if state in ["District Of Columbia", "Puerto Rico"]:
        continue
    ax2 = axs[i].twinx()
    uemp_states.query('index >= 2020 and index < 2022')[state] \
        .plot(ax=axs[i], label='Unemployment')
    part_states.query('index >= 2020 and index < 2022')[state] \
        .plot(ax=ax2, label='Participation', color=color_pal[1])
    ax2.grid(False)
    axs[i].set_title(state)
    i += 1
plt.tight_layout()

plt.show()
