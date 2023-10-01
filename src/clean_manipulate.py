#!/usr/bin/env python
# coding: utf-8

# # Chess Analytics: The Relationship Between Rating Discrepancy and Various National Metrics

# ## Data Cleaning and Manipulation Notebook (1/2)
# This is the first of two notebooks that we will be using for our Milestone I project. Please refer to our project proposal for a more detailed description of our project:
# https://docs.google.com/document/d/14McqLTo34VNHqz9b9nDVB8Mm_TcqahvEnPhvw_gUYmk/edit?usp=sharing
# 
# ### Datasets
# The following are datasets we used for this project and manipulated in this notebook:
# 1. Chess Olympiad Results from chess-results:
#    https://chess-results.com/tnr36795.aspx?lan=1&art=1&turdet=YES&flag=30&zeilen=99999
# 2. Various national economic metrics from World Bank:
#    https://databank.worldbank.org/source/world-development-indicators#
# 3. Complete Dataset of Chess Players from FIDE:
#    https://ratings.fide.com/download.phtml
# 4. A Country Codes Table from Wikipedia:
#    https://en.wikipedia.org/wiki/Comparison_of_alphabetic_country_codes
# 5. A Capital Coordinates Table from Omar Nomad's Github:
#   https://gist.github.com/ofou/df09a6834a8421b4f376c875194915c9
# 

# In[1]:


#!pip install numpy pandas requests unidecode scikit-learn tqdm


# In[2]:


import numpy as np
import pandas as pd
import requests
import re
from unidecode import unidecode
from itertools import groupby
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


# In[3]:


# Checking assets status:
# 1. Primary Dataset: Chess Olympiad Results (2 MB)
# 3. Secondary Dataset: FIDE Rated Players Dataset (435 MB)
# 5. Geo-data - GeoJSON and csv (24 MB)
from download_assets import status


# ### 1. Primary Dataset: Chess Olympiad Results
# The first dataset we're going to work with is our primary dataset: the chess olympiad dataset.
# #### How We Procured This Dataset
# Chess-Results.com is a popular website that stores and provides access to chess tournament information. It stores tournament data in a structured database format, including details such as player names, ratings, round results, and pairing information. Users can download data from Chess-Results.com by visiting the tournament page and selecting the "Excel and Print" option, where tournament results can be exported to excel files. To smooth the reader experience, we've written a python script `download_assets.py` to automate this process. Since the tournmanet data is stored in a database, the user can pick and choose from different result tables that best suits their needs, which allows chess enthusiasts, organizers, and analysts to access and analyze tournament data for a wide range of purposes, including post-event analysis and research.
# 
# #### What is the Chess Olympiad?
# The FIDE (Fédération Internationale des Échecs, the governing body of chess) Chess Olympiad is like the Olympics, but for chess. Just like in soccer (or football), every country gets to send their national team to compete, and so do some non-countries. For example, unlike in the Olympics where Great Britain competes as one team, England, Scotland, and Wales competes separately from one another in FIFA, as well as in FIDE. The Virgin Islands, Hong Kong, or Jersey (an island in the English Channel) also gets their own chess team in the FIDE Chess Olympiad. Each team, representing its people, consists of five players: Four starters and one substitute. A total of 11 rounds of action will see teams representing each federation battle it out in a 4 vs 4 for a total of 44 games played by each team in each tournament, with the winner being the team that has won the most 'sets' out of the 11 rounds. The Chess Olympiad is held once every two years, but in 2020, it was cancelled due to the pandemic. In our analysis, we will be looking at data from the 2010 Chess Olympiad to the 2022 Chess Olympiad. 
# 
# #### What does the dataset look like?
# Before we dive into the dataset, let's talk about ELO Ratings. These ratings are the summary of a player's past results. In the beginning, everyone starts with the same rating (say 1000 for example), and every time you beat someone, you steal some of his rating and add it to yours. When you defeat stronger players, you gain more rating for your victory, and when you lose against strong opposition, you don't lose as much rating. Before entering this tournament, each individual player has been assigned a rating based on their past performances, with that rating, we are able to predict how well the player will do in the event. A strong player, rated 2800, may be expected to score 9 wins out of 11 rounds, but if he only ends up winning 5 games, then we would say he underperformed his rating in this Olympiad. The difference between a player's projected result given his pre-tournament rating and his actual result after the conclusion of the tournament can be used to calculate the 'rating discrepancy' of a player, a metric that describes how much a player was underrated or overrated based on his performance in one Olympiad.
# 
# From the print statement below, we can see that the excel file is a bit messy. It seems like we have a lot of header rows, and if we look at row 17 and row 23, we also see that between player data from different federations, there is an additional row of column names. As for the data composition of each player row, we have, in order, board number (usually ordered by strength, so that even matchups happen across each board), title (titles are awarded by FIDE to players who are exceptionally strong), name, rating, federation (which 'national' team they play for), result by round (11 columns, 1 for victory, 0 for defeat, 1/2 for a draw, and left empty if player didn't play that round, since for teams with substitutes available, one player may rest each round), total points earned, total games played, and some other calculated metrics. 

# In[4]:


# Cell for Demonstration Purposes
pd.read_excel('data/primary/chessResultsList_2010.xlsx').head(8)


# In[5]:


years = [2010,2012,2014,2016,2018,2022]
filenames = ['data/primary/chessResultsList_{}.xlsx'.format(year) for year in years]
colnames = ['board', 'title', 'name', 'rating', 'federation', 'points', 'games', 'rating_performance']
olympiads_df = []
for i,year in enumerate(years):
    if year == 2018:
        col_index = [0,1,2,3,4,17,18,20]
    else:
        col_index = [0,1,2,3,4,16,17,18]
    df = pd.read_excel(filenames[i])
    cleaned_df = df.iloc[:, col_index]
    cleaned_df.columns = colnames
    boards = pd.to_numeric(cleaned_df['board'], errors='coerce')
    non_nan_indices = boards.notna().index[boards.notna()]
    trimmed_df = cleaned_df.loc[non_nan_indices,:].reset_index(drop=True)
    trimmed_df['year'] = year
    olympiads_df.append(trimmed_df)


# #### How did we manipulate the dataset?
# Recall that we had to clean six datasets as there are six Olympiads between 2010 and 2022. However, although the six excel files share a similar overall structure, they are each unique in their own ways. Some have columns that others don't, while some have fewer header rows than others. Fortunately, we just had to grab the columns that we were interested in for each dataset by specifying their indices, read the entire file into rows in a df, and filter rows based on whether their value in the first column is numeric. For player-rows, the first column is board number (always 1~5), so we just grabbed those rows for each excel file and make each year its own dataframe. Since we selected the same columns when generating each of the six Olympiad dataframes, we can simply merge them together through pd.concat. Before merging them, we added a 'year' column so that we know which year each player-row was originally from.

# In[6]:


# Cell for Demonstration Purposes
list1 = pd.read_excel(filenames[4]).loc[18].tolist()
list2 = pd.read_excel(filenames[0]).loc[18].tolist()
longer_list, shorter_list = (list1, list2) if len(list1) >= len(list2) else (list2, list1)
shorter_list.extend([np.nan] * (len(longer_list) - len(shorter_list)))
df = pd.DataFrame([longer_list, shorter_list]).T
df.columns = range(len(df.columns))
df.T


# In[7]:


olympiads_merge_df = pd.concat(olympiads_df, axis=0)
olympiads_merge_df.reset_index(drop=True, inplace=True)

numeric_cols = ['board', 'rating', 'points', 'games', 'rating_performance', 'year']
olympiads_merge_df[numeric_cols] = olympiads_merge_df[numeric_cols].apply(pd.to_numeric, errors='coerce')

#Handling edge cases
#Trinidad and Tobago switched country codes in 2014
indices_to_edit = olympiads_merge_df[olympiads_merge_df['federation']=='TRI'].index 
olympiads_merge_df.loc[indices_to_edit, 'federation'] = 'TTO' #we will use thier official IOC code throughout our analysis

#Drop Taiwan and Kosovo
olympiads_merge_df = olympiads_merge_df[~((olympiads_merge_df['federation'] == 'TPE') | (olympiads_merge_df['federation'] == 'KOS'))]

#Drop Netherland Antilles
olympiads_merge_df = olympiads_merge_df[~(olympiads_merge_df['federation'] == 'AHO')]

#It makes more sense to consider GBR 'territories' as the same country
gbr_index = (
    (olympiads_merge_df['federation'] == 'ENG') | #England
    (olympiads_merge_df['federation'] == 'SCO') | #Scotland
    (olympiads_merge_df['federation'] == 'WLS') | #Wales
    (olympiads_merge_df['federation'] == 'JCI') | #Jersey
    (olympiads_merge_df['federation'] == 'GCI') #Guernsey
)

olympiads_merge_df.loc[gbr_index, 'federation'] = 'GBR'
olympiads_merge_df.sample(5,random_state=42)
#olympiads_merge_df[olympiads_merge_df['federation'] == 'BHU']


# ### 2. Secondary Dataset: World Bank Data
# The second dataset we're going to work with is one of our secondary datasets: the world bank dataset. 
# #### How We Procured This Dataset
# The World Development Indicators DataBank website is an online platform that stores and provides access to a comprehensive range of economic and development data from countries around the world. It stores this data in a structured database format, organized by indicators such as GDP growth, population, education, and health. Users can download data from the World Development Indicators DataBank by selecting specific indicators, countries, and time periods, and then exporting the data in various formats such as CSV, which we did in our case.
# #### What Does the Dataset Look Like?
# The `world_bank_df` contains data on economic and demographic indicators for 217 countries over the years 2007 to 2022. It includes columns for country names, codes, indicator names, and indicator codes, along with separate columns for each year's data. Each row represents a specific data point for a given combination of country, indicator, and year. Some cells contain ".." values, indicating missing or unavailable data, while some FIDE federations are not even present in this dataset for political reasons, as this is a Dataset published by the United Nations. Excluded federations like Taiwan or Kosovo will be dropped from our analysis, as will countries who did not provide economic data, for certain indicators, should we perform analysis on those. We will apply filtering, grouping, and aggregation to this dataframe before proceeding further in our analysis.
# #### How Did We Manipulate the Dataset?
# The dataset is loaded from a CSV file, and a list of specific years (from 2007 to 2018) is created, representing the years of economic data to be used. Next, missing data, represented as ".." in the dataset, is replaced with NaN values using the replace method. We calculate the percentage of available data for each economic indicator per country, determining how much data is present for each category, and a threshold (set at 90%) is applied to filter out economic indicators that don't meet the specified data completeness criteria. The list of economic indicators that meet the threshold is stored in the `above_threshold_indicators` variable, and rows in the dataset are filtered to keep only those corresponding to the selected economic indicators.
# 
# 
# 
# 

# In[8]:


world_bank_df = pd.read_csv('data/secondary/World_Development_Indicators/world_bank_data.csv')


# In[9]:


#Years we will use, currently using economic data 3 years before
#each olympiad takes place (e.g. 2007 economic data for 2010 chess olympiad)
years_list = [f"{year} [YR{year}]" for year in range(2007, 2020, 2)]

#Replace ".." in data with NaN
world_bank_df = world_bank_df.replace("..", np.nan)

#Counting how much existing data per category we have
series_counts = world_bank_df.groupby('Series Name').count()

#Calculate what percentage of data we have (in terms data for each country)
series_counts['Percentage_With_Data'] = series_counts[years_list].sum(axis=1) / len(years_list) / series_counts['Country Name']

#Filter rows based on a threshold
threshold = .9
series_counts_filtered = series_counts[series_counts['Percentage_With_Data'] > threshold]

#List of economic indicators that have amount of data that meet the threshold
above_threshold_indicators = series_counts_filtered.index.tolist()
series_counts_filtered.head(3)


# In[10]:


above_threshold_indicators


# In[11]:


#Only keep rows from series which meet our threshold
world_bank_df = world_bank_df[world_bank_df['Series Name'].isin(above_threshold_indicators)]
world_bank_df["Country Name"] = world_bank_df['Country Name'].str.strip()


# In[12]:


world_bank_df.head(3)


# ### 3. Secondary Dataset: FIDE Rated Players Dataset
# The third dataset we're going to work with is one of our secondary datasets: FIDE Rated Players Dataset.
# #### How We Procured This Dataset
# FIDE published ratings lists for the years 2010 to 2022 were procured from the FIDE website, from the ratings archive via the python script `download_assets.py`. The script employs the requests library to fetch data files, creates a zip buffer to store the downloaded content, and then iteratively downloads and extracts the data. It also handles the variation in file naming conventions. This process ensures that the required dataset, contained within zip archives, is retrieved and made accessible for further data manipulation and analysis in our preferred destination file.
# 
# #### What Does the Dataset Look Like?
# This dataset is of a less common format: fixed-width format file. A fixed-width format file is a data storage format where each column in the dataset has a predetermined and consistent width, with data values aligned within their respective columns. Converting it into a CSV file can be challenging because you need to accurately identify and define column widths to properly separate and structure the data, which can be complex and error-prone, especially in datasets with numerous columns or irregular spacing. In this case, we fortunately have a (poorly and inconsistently formatted) columns header to work with.
# 
# #### How Did We Manipulate the Dataset?
# The key to decoding this fwf file is to figure out the columns and column width of each column in each file. However, we can't split on spaces because the 'ID number' is one column; we can't split on uppercase characters because 'ID Number' is one column, while 'jan13' is also a column. Ultimately, for the first row in each file, we had to iterate through each character to find the `capitalized_indices`, add the index of occurences of 'j', and eliminate extra indices between position zero and 10 (sometimes the 'n' in ID number is capitalized). Next, we calculated the column widths based on the values of the differences between adjacent `capitalized_indices`, and finally, we hard coded the column names for each dataset for consistency purposes. We renamed the columns for each df, generated through `pd.read_fwf(file_path)`, and selected the relevant columns, as well as added a year column, then merged the players df for each year into one big fide rated players dataframe. Finally, we handled some federations edge cases, and also standardized the 'title' column.

# In[13]:


# Cell for Demonstration Purposes
try:
    with open('data/secondary/fide_ratings_list/standard_jan12frl.txt', 'r') as file:
        lines = 0
        while lines < 3:
            lines += 1
            print(file.readline())
    with open('data/secondary/fide_ratings_list/standard_jan13frl.txt', 'r') as file:
        lines = 0
        while lines < 3:
            lines += 1
            print(file.readline())
except FileNotFoundError as e:
    print('Before continuing, please execute download_assets.py')


# In[14]:


years = list(range(10,24))
file_paths = ['data/secondary/fide_ratings_list/standard_jan{}frl.txt'.format(year) for year in years]

list_of_colnames = []
list_of_column_widths = []
for file_path in file_paths:
    with open(file_path, 'r') as file:
        first_line = file.readline() #This is the Column Names line, we'll use it to format our variable-width column txt file
        #Getting Format of variable-width columns (first letter of columns is usually capitalized)
        capitalized_indices = [index for index, char in enumerate(first_line) if char.isupper() or char == 'j'] #Because our data is from January of each year; Jan{} and jan{}
        col_start_indices = [capitalized_indices[0]] + [capitalized_indices[i] for i in range(1, len(capitalized_indices)) if capitalized_indices[i] != capitalized_indices[i - 1] + 1]
        col_start_indices.append(len(first_line)-1) #So that we can more easily compute the differences, aka column width
        col_start_indices = [x for x in col_start_indices if x >= 10 or x == 0] #Problem with ID Number
        # Creating the Colnames
        colnames = []
        for i in range(len(col_start_indices)-1):
            start_index = col_start_indices[i]
            end_index = col_start_indices[i + 1]
            colname = first_line[start_index:end_index].strip() #We get the column name in string
            colnames.append(colname)
        colnames = ['Rating' if column_name.lower().startswith('jan') else column_name for column_name in colnames] #More descriptive colname
        colnames = ['Fide_id' if column_name.lower().startswith('id') else column_name for column_name in colnames] #Better and universal colname
        list_of_colnames.append(colnames) #The formatting changed over the years, so we have different colnames for each year
        # Computing variable-width columns width
        column_widths = [col_start_indices[i + 1] - col_start_indices[i] for i in range(len(col_start_indices) - 1)]
        list_of_column_widths.append(column_widths)
list_of_colnames[0]


# In[15]:


#collect all the rated players by year in a list of dataframes
rated_players_by_year_df = []
for i in range(len(file_paths)):
    file_path = file_paths[i]
    column_widths = list_of_column_widths[i]
    column_names = list_of_colnames[i]
    result_df = pd.DataFrame(columns=list_of_colnames[i])
    df = pd.read_fwf(file_path, widths=column_widths, names=column_names, encoding='unicode_escape')
    df = df.drop(0).reset_index(drop=True)
    rated_players_by_year_df.append(df)

#store all the rated players in the same df
relevant_columns = ['fide_id', 'name', 'title', 'federation', 'rating']
trimmed_rated_players = []
for i,df in enumerate(rated_players_by_year_df):
    if i < 3:
        df.columns = ['fide_id', 'name', 'title', 'federation', 'rating', 'Games', 'Born', 'Flag']
    elif i < 7:
        df.columns = ['fide_id', 'name', 'federation', 'Sex', 'title', 'WTit', 'OTit', 'rating', 'Gms', 'K', 'B-day', 'Flag']
    else:
        df.columns = ['fide_id', 'name', 'federation', 'Sex', 'title', 'WTit', 'OTit', 'FOA', 'rating', 'Gms', 'K', 'B-day', 'Flag']
    
    df_trim = df.copy()[relevant_columns]
    df_trim['year'] = 2010+i
    trimmed_rated_players.append(df_trim)
rated_players_df = pd.concat(trimmed_rated_players, axis=0)

#slightly modify the federation codes
gbr_index = (
    (rated_players_df['federation'] == 'ENG') | #England
    (rated_players_df['federation'] == 'SCO') | #Scotland
    (rated_players_df['federation'] == 'WLS') | #Wales
    (rated_players_df['federation'] == 'JCI') | #Jersey
    (rated_players_df['federation'] == 'GCI') #Guernsey
)
caf_index = rated_players_df['federation'] == 'CAF' #Central African Republic

rated_players_df.loc[gbr_index, 'federation'] = 'GBR'
rated_players_df.loc[caf_index, 'federation'] = 'CAR'

numeric_cols = ['fide_id', 'rating', 'year']
rated_players_df[numeric_cols] = rated_players_df[numeric_cols].apply(pd.to_numeric, errors='coerce')
rated_players_df.dropna(subset=numeric_cols, inplace=True)
rated_players_df[numeric_cols] = rated_players_df[numeric_cols].astype(int)

title_dict = {
    'c': 'CM',  # Candidate Master
    'f': 'FM',  # FIDE Master
    'm': 'IM',  # International Master
    'g': 'GM',  # Grandmaster
    'wc': 'WCM',  # Woman Candidate Master
    'wf': 'WFM',  # Woman FIDE Master
    'wm': 'WIM',  # Woman International Master
    'wg': 'WGM',   # Woman Grandmaster
    'CM': 'CM',  # Candidate Master
    'FM': 'FM',  # FIDE Master
    'IM': 'IM',  # International Master
    'GM': 'GM',  # Grandmaster
    'WCM': 'WCM',  # Woman Candidate Master
    'WFM': 'WFM',  # Woman FIDE Master
    'WIM': 'WIM',  # Woman International Master
    'WGM': 'WGM'   # Woman Grandmaster
}
rated_players_df['title'] = rated_players_df['title'].map(title_dict).fillna(np.nan)

rated_players_df.reset_index(drop=True, inplace=True)
rated_players_df.sample(5, random_state=42)


# ### 4. Secondary Dataset: Country Code
# The fourth dataset we're going to work with is one of our secondary datasets: Country Code
# 
# #### How We Procured This Dataset
# Originally, we did not expect to need a dataset like this, but unfortunately, the country code that is used for our Primary Dataset: Chess Olympiad Results, and our Secondary dataset: World Bank Data, is different. The former uses the IOC (International Olympic Committee) country code convention, while the latter uses the ISO (International Organization for Standardization) country codes. Fortunately, a Wikipedia page on Comparison of alphabetic country codes has a table that lists the different country codes for each federation in our Primary Dataset, enabling us to effectively combine datasets. We sent a request to the Wikipedia page to fetch HTML data, and we used the Pandas library to read the HTML tables from the response text.
# 
# #### What Does the Dataset Look Like?
# It has four columns. The first column is Country, which contains the names of various countries. The 'IOC' column contains the International Olympic Committee country codes. These codes are used in the context of the Olympic Games, as well as in chess. The 'FIFA' column contains the FIFA (Fédération Internationale de Football Association) country codes, in this context, certain FIDE federations that are not IOC federations uses the FIFA code. Finally, the ISO column contains the ISO country codes. ISO codes are standardized codes used for various purposes, including international data exchange and identification of countries.
# 
# #### How Did We Manipulate the Dataset?
# This Dataset will serve as a `keys_table`. Similar to the Primary and Foreign keys concept in SQL, for the previous 3 datasets that we looked at, country code (albeit different systems) are their primary keys. By storing the federation name, chess country code, and UN country code in the same dataframe, we're able to easily cross reference different dataframes for any given country. The only problem was, although FIDE (chess) country code was mostly based on IOC code, there were a few edge cases that we had to handle. The Primary dataset, as its name suggests, takes precedence over all other datasets. The federations we are interested in, therefore, are all of which appeared in the primary dataset. Therefore, we began building our `country_codes_table` by looping through the unique federations codes in our primary dataset, checking if the federation code matches any of the IOC codes, and if it does, we add a new row of three values to our `country_codes_table`, country, `fide_code`, and `country_code`. For one reason or another, the Faroe Islands, Monaco, and the Central African Republic either cannot be matched this way, so we had to hard code the three countries after confirming which federations the non-matching edge cases in the unique federations were, and adding the corresponding `country_code` to the three rows.

# In[16]:


url = 'https://en.wikipedia.org/wiki/Comparison_of_alphabetic_country_codes'
response = requests.get(url)
tables = pd.read_html(response.text)


# In[17]:


country_codes_df = tables[0].drop(columns=['Flag', '*']) #Drop the irrelevant columns in the first table, which is the one we're interested in.
for i,row in country_codes_df.iterrows(): #Some countries in the Olympics further divide in other competitions 
    if pd.isna(row['IOC']): #For example, IOC has GBR, but FIFA has England, Scotland, and Wales
        row['IOC'] = row['FIFA'] #We try to make the IOC column more complete, for example, FIFA and FIDE labels England ENG, but not IOC.
country_codes_df.head()


# ### Preparation to Merge on Countries in the Olympiad Dataset

# In[18]:


federations = [] #This will be the country full name column in the country code look-up table
feds_fide = [] #This will be the country fide code column in the country code look-up table
feds_iso = [] #This will be the country nation code column in the country code look-up table
hardcode_indexed_feds = [] #this is a containers to handle edgecases
hardcode_federations = ['Faroe Islands','Monaco','Central African Republic'] 
#Had to manually google which federations the remaining hardcode_indexed_feds were

for fed in olympiads_merge_df['federation'].unique(): #Macau
    try:
        row_index = country_codes_df[country_codes_df['IOC'] == fed].index[0]
        federations.append(country_codes_df.loc[row_index, 'Country'])
        feds_fide.append(country_codes_df.loc[row_index, 'IOC'])
        feds_iso.append(country_codes_df.loc[row_index, 'ISO'])
    except:
        hardcode_indexed_feds.append(fed)
for i in range(len(hardcode_indexed_feds)): #We finish up by appending the hardcoded countries to our future columns
    row_index = country_codes_df[country_codes_df['Country'] == hardcode_federations[i]].index[0]
    federations.append(hardcode_federations[i])
    feds_fide.append(hardcode_indexed_feds[i])
    feds_iso.append(country_codes_df.loc[row_index, 'ISO'])
federations = [re.sub(r'\[[0-9]+\]', '', country) for country in federations] #Cleaning up Country Names
country_codes_table = pd.DataFrame({'federation': federations, 'fide_code': feds_fide, 'country_code': feds_iso})
country_codes_table.tail()


# ### 5. Secondary Dataset: Capital Coordinates
# The fifth dataset we're going to work with is one of our secondary datasets: Capital Coordinates
# 
# #### How We Procured This Dataset
# We wanted a comprehensive list of "FIDE-recognized-federations" (as opposed to UN-recognized countries or IOC-recognized countries) capital coordinates for one of our visualizations. In hindsight, we probably should have combined the following two datasets to make our lives much easier by utilizing existing country codes mapping.
# 1. https://developers.google.com/public-data/docs/canonical/countries_csv
# 2. https://www.iban.com/country-codes
# Instead, we went for the messier (and possibly more fun) approach. First, we downloaded the csv file of each countries' capital-lat-lon information through the python script `download_assets.py`, since it was a simple CSV, the importing wasn't too difficult. Next, through `download_assets.py`, we also downloaded a geojson file from this [link](https://datahub.io/core/geo-countries). A GeoJSON (Geospatial JavaScript Object Notation) file is a lightweight format for encoding geographic data structures, such as points, lines, and polygons, using JSON (JavaScript Object Notation). It is commonly used for representing and exchanging geospatial information in a human-readable and machine-parseable format. GeoJSON files can store both geometry (e.g., coordinates) and properties (e.g., attributes) of geographic features, making them versatile for a wide range of applications. For the purposes of our project, we want to utilize it to make choropleth maps, which you will see in our analysis notebook.
# 
# #### What Does the Dataset Look Like?
# It has six columns, but we'll mostly only be using Country, Latitude, and Longitude. It does not have a country code column, and the different naming conventions for country name is going to make our country matching task quite difficult.
# 
# #### How Did We Manipulate the Dataset?
# This dataset has no primary key in the form of country code, so we have to match it with our `country_codes_table` through `country_name`. As things stand, our `country_codes_table` has three columns, two of which are country/fide codes, and one is federation name, or country name. We're going to try our best to match `country_codes_table['federation']` with `country_capital_df['Country']`. We will explain the process in more detail via inline comments in the `find_match_country` function, but in short, the function is designed to match a list of query strings (in this case, federation names) with a list of potential matching answers (country names). The function employs the TF-IDF (Term Frequency-Inverse Document Frequency) vectorization technique to calculate the similarity between queries and potential answers. In the first stage, it returns a list of best matches between queries and answers, along with a list of queries that didn't find a match, in the second stage, for countries/federations that are not similar enough per the judgement of TF-IDF, we try to match the first four letters of each unpaired federation with country names until a match is found. We probably could have hard coded since there weren't that many countries. Finally, we hardcoded three countries that wasn't able to find a match through the previous steps.

# In[19]:


country_capital_df = pd.read_csv('data/secondary/country-capital-lat-long-population/country-capital-lat-long-population.csv')
numeric_cols = ['Latitude','Longitude','Population']
country_capital_df[numeric_cols] = country_capital_df[numeric_cols].apply(pd.to_numeric, errors='coerce')
country_capital_df.head()


# In[20]:


# the function takes in two lists, a list of queries (federations), and a list of potential matches (country names)
def find_match_country(queries_list, matching_list,perfect=False):
    # we're going to be using some list operations
    if not type(queries_list) == list:
        queries = queries_list.tolist()
    else:
        queries = queries_list
    if not type(matching_list) == list:
        possible_answers = matching_list.tolist()
    else:
        possible_answers = matching_list
    # Create a TF-IDF vectorizer
    vectorizer = TfidfVectorizer()
    # Fit and transform the vectorizer on all the possible answers
    tfidf_matrix = vectorizer.fit_transform(possible_answers)

    # instantiate the containers for matches, so that we can easily extract matches and prevent duplicates
    best_matches = []
    no_match = []
    past_matches = set()
    
    for query in queries:
        # Does query contain island, islands often end up as false positive matches
        contains_island = 'island' in query.lower()
        # Transform the query into a TF-IDF vector
        query_vector = vectorizer.transform([query])
        # Calculate cosine similarities between the query and possible answers
        similarities = cosine_similarity(query_vector, tfidf_matrix)
        # Find the index of the best match, and sort the matches based on cosine similarity score 
        similarity_indices = similarities.argsort()[0][::-1]
        for best_match_index in similarity_indices:
            best_answer = possible_answers[best_match_index]
            similarity_score = round(similarities[0][best_match_index], 3) #rounding doesn't change anything
            if not contains_island: # if the query is not an island
                if 'island' not in best_answer.lower(): # the best answer should not contain island either
                    if similarity_score > 0.6: # in that case, if the two are similar enough
                        if not best_match_index in past_matches: # and the best answer is not a previous answer
                            best_matches.append((query, best_answer)) # we add the federation, country pair to a list
                            past_matches.add(best_match_index) # and we log the index of best match country so that it won't be matched again
                            break  # break the loop if a matching answer is found
                else: # if the best_answer fails any of the conditions
                    continue # continue onto the next best answer by cosine similarity score 
            else: # if the query is an island
                if similarity_score > 0.6: # if the two are similar enough
                    if not best_match_index in past_matches: # and the best answer is not a previous answer
                        best_matches.append((query, best_answer)) # we add the federation, country pair to a list
                        past_matches.add(best_match_index) # and we log the index of best match country so that it won't be matched again
                        break # break the loop if a matching answer is found
                else: # if the best_answer fails any of the conditions
                    continue # continue onto the next best answer by cosine similarity score 
        else: # if none of the potential matches fulfill all of the conditions
            no_match.append(query) # we add the federation that failed to register a match to the list no_match 
    if perfect: # during development, we sometimes wanted to see the contents of no_match, and would set perfect = False
        candidates = [possible_answers[i] for i in range(len(possible_answers)) if i not in past_matches] # update the potential matches list
        still_no_match = [] # instantiate the container for federations that still are unable to register a match after the following sequence
        still_no_match_ans = ["Swaziland","Lao People's Democratic Republic", "Faeroe Islands"] # these are the answers
        for country in no_match: # for federations that did not match through the tf-idf method
            count = 0 # a count variable that keeps track of how many countries the federation has tried matching
            country_substring = unidecode(country[:4]) # the first four letters of a federation becomes its country substring 
            for candidate in candidates: # for each country in the list of countries that were not already matched by a federation in the tf-idf step
                count += 1 # we add one to the count
                if country_substring in candidate: # if the first four letters of a federation matches with a country
                    best_matches.append((country, candidate)) # we declare a match and append the federation and country to the list of matches
                    break # break out of the loop and start matching for the next federation
                if count >= len(candidates): # if the federation has exhausted all the countries but finds no match
                    still_no_match.append(country) # we add the federation to the list 'still_no_match'
        for i in range(len(still_no_match)): # ultimately, we know the three federations that are in still_no_match
            best_matches.append((still_no_match[i], still_no_match_ans[i])) # append federations in still no match with their corresponding answers
    return best_matches # we get a complete list of tuples of (query, best_answer)

country_name_dict = dict(find_match_country(country_codes_table['federation'],country_capital_df['Country'],True)) # we convert the tuple list to dict
country_codes_table['federation_lat_long'] = country_codes_table['federation'].map(country_name_dict) # we map countries to country_codes_table
country_codes_table.head() # and we get a new column 'federation_lat_long' that is the primary key of country_capital_df


# In[21]:


get_ipython().run_line_magic('load_ext', 'watermark')
get_ipython().run_line_magic('watermark', '-v -m -p pandas,numpy,re,requests,unidecode,sklearn,tqdm')

