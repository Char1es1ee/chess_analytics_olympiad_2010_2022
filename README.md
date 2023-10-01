## 1. Name
Chess Analytics: The Relationship Between Rating Discrepancy and Various Metrics

## 2. Description
### 2.1 Motivation
This project was inspired by insights from top chess players who have highlighted underrated chess talents emerging from developing countries with strong chess cultures such as China and India. Players from these nations are often described as playing stronger than their official chess ratings during tournament play. We are motivated to take a data-centric approach to exploring the merits of these insights by exploring chess tournament results, and seeing if they can be explained using economic data and chess culture metrics.
### 2.2 Background
The International Chess Federation, referred to by its French acronym FIDE (Fédération Internationale des Échecs), acts as the governing body of international chess competitions. FIDE hands out chess titles such as the Grandmaster title, as well as tracks player’s ratings (chess Elo).
Additionally, FIDE organizes the Chess Olympiad, a biennial chess tournament where teams representing nations of the world gather to compete. Each team consists of five players: Four starters and one substitute. The teams play against different opposing federations for 11 rounds, and the team that wins the most rounds is declared the winner.
### 2.3 Objectives
The purpose of the project was to 1.) combine different datasets with FIDE Olympiad chess data from 2012 through 2022 to extract a useful byproduct, 2.) create insightful visualizations that shed light on the global chess landscape, and 3.) answer our main question:

**What factors influence a country's rating discrepancy in chess?**

We will try to answer our main question by addressing several related questions such as:
- Is there a correlation between a country’s economic situation and being underrated in chess?
- Which countries have a strong chess culture?
- Can chess culture explain how teams perform in the Chess Olympiad?
- Which countries have consistently over-performed or underperformed at the Chess Olympiads?

We aim to offer a comprehensive analysis that sheds light on the current state of the chess landscape. Furthermore, our goal is to uncover valuable insights into how players are currently being rated, with a specific focus on fairness. We also aim to investigate whether socioeconomic factors, such as poverty, may be a contributing factor to players being unjustly underrated.

### 2.4 Elo Ratings
Chess Elo is a rating system used to measure a player's skill level in chess. It assigns a numerical rating to each player, with higher ratings indicating stronger players. When two players compete, the change in their Elo ratings after the game depends on the outcome and the rating difference between them. We will primarily be looking at the changes in Elo of a country’s Olympiad team after playing in the Olympiad, and exploring this change’s relationship with several other factors.


## 3. Roadmap
### 3.1 Summary
In conclusion, our study on rating discrepancies in chess Olympiads highlights the impact of limited international exposure on underrated players.
Analyzing data from the Chess Olympiad while factoring in geographical variables, chess culture, population size, and GDP per capita, we've identified complex factors influencing rating disparities. Most federations tend to lose rating points on average in the Olympiad, possibly attributable to the presence of strong unrated players from newly admitted federations. However, there are consistently overperforming and underperforming countries, the former often being small countries' national teams that consist of non-top-tier players who rarely receive invitations to tournaments, but have proved themselves worthy in local (possibly unrated) tournaments. 
Overperforming countries do not follow a specific wealth or chess culture profile while underperforming countries generally fall into two categories: economically disadvantaged with limited chess culture and economically well-off with rich chess traditions.
Interestingly, chess culture positively affects rating discrepancies, but the interaction between GDP per capita and chess culture shows a counterintuitive negative correlation. Many overperforming countries, predominantly in central/southern Asia, may face difficulties in participating in FIDE-rated tournaments, which are more prevalent in Europe. This highlights the potential importance of the number of tournaments hosted by a federation as a key predictor of rating disparities. 
In essence, these findings underscore the complexity of real-world problems and emphasize the need to consider a broad range of factors to avoid bias by omitting critical predictors in analytical assessments.
### 3.2 Limitations
The ratings and performance of chess players is complex.  We made the decision to use chess Olympiad data instead of other tournament data because all countries were represented, not just those that are wealthy. Although this may have reduced sampling bias, this may have limited our sample counts—teams are only made of 4 main players and each player only plays 11 matches.
Confounding variables such as travel or team selection (best players from a country aren’t representative of the average player from that country) method may play a role in team performance. We were not able to look at this during our project.
We had to make the assumption that chess culture was primarily an outcome of having top chess players. Many other aspects of chess culture such as chess clubs, chess park culture, tournaments, and forms of media were not examined at this time.

### 3.3 Next Steps
We found that a group of countries did particularly poorly in 2022, losing a lot more points than any country lost in the Olympiads prior. It may be worthwhile to examine exactly what caused this.
Exploring data on confounding variables such as distance to host site and team selection may bring more insights into chess rating discrepancy.
Running a regression model may provide us with more precise data on exactly which factors have the most influence on rating discrepancy. It may even be able to used to predict a teams future performance. 

## 4. Authors and acknowledgment
### 4.1 Authors
Jim Yang, Ke Miao, and Michael Nguy
### 4.2 Acknowledgement
Mentor: Oleg Nikolsky

Reviewers: Qian Fu, Richard Weyfung Cheng, Eugene Tseng, Nicholas Salem, and Jean Applys Cherizol

Instructors: Chris Teplovs, Anthony Whyte, Kyle Balog, Oleg Nikolsky, Kira Rodarte, and Ali Kirwen

## 8. Dataset
In this project, we used several datasets related to Olympiad results, economic data, and chess culture metrics. The datasets were collected from various sources and used to analyze the relationship between rating discrepancy and various factors.

### 8.1 Primary Dataset
#### FIDE Chess Olympiad Results
##### Description: 
This dataset contains the results of all matches played by a player during the tournament. It includes relevant columns such as player name, federation, no. of games played, rating before the tournament, and change in rating at the conclusion of the tournament. The players are all grouped by federation.
##### Size: 
1.99 MB in total size, made up of 6 different XLSX files, one for each biennial Olympiad that took place during 2010-2022 (minus 2020 due to Covid).
##### No. of attributes: 
23
##### Format: 
XLXS
##### Access: 
Download (via script)
##### Location: 
chess-results.com

### 8.2 Secondary Datasets
#### 8.2.1 World Development Indicators
##### Description: 
Contains various economic indicators for each country, such as income distribution, income per capita, GDP per capita, GNI per capita, and population statistics, among others.
##### Size: 
1.19 MB
##### No. of attributes: 
24
##### Format: 
csv
##### Access: 
Download
##### Location: 
databank.wordbank.org

#### 8.2.2 Capital Coordinates Data
##### Description: 
It contains country name, capital city, latitude, longitude, population, capital and type for countries. Will be used to help determine chess culture.
##### Size: 
12.42 KB
##### No. of attributes: 
6
##### Format: 
csv
##### Access: 
Download (via script)
##### Location: 
gist.github.com

#### 8.2.3 FIDE Rated Players Data
##### Description: 
Has information on all FIDE rated players. It includes player ID, name, federation, rating, and any chess titles
##### Size: 
435 MB, made up of 14 separate files.
##### No. of attributes: 
7
##### Format: 
TXT
##### Access: 
Download (via script)
##### Location: 
ratings.fide.com


## 5. Dependencies
To run this project, you'll need the following libraries installed:

- [JupyterLab](https://jupyterlab.readthedocs.io/en/stable/) (Version 4.0.5)
- [IPython](https://ipython.readthedocs.io/en/stable/) (Version 8.15.0)
- [Haversine](https://pypi.org/project/haversine/) (Version 2.8.0)
- [JSON5](https://pypi.org/project/json5/) (Version 0.9.14)
- [Matplotlib](https://matplotlib.org/stable/contents.html) (Version 3.6.3)
- [NumPy](https://numpy.org/doc/stable/) (Version 1.24.1)
- [Pandas](https://pandas.pydata.org/docs/) (Version 1.5.3)
- [Plotly](https://plotly.com/python/) (Version 5.17.0)
- [Requests](https://docs.python-requests.org/en/latest/) (Version 2.28.2)
- [Scikit-Learn](https://scikit-learn.org/stable/documentation.html) (Version 1.3.0)
- [Seaborn](https://seaborn.pydata.org/) (Version 0.12.2)
- [Statsmodels](https://www.statsmodels.org/stable/index.html) (Version 0.14.0)
- [TQDM](https://tqdm.github.io/) (Version 4.66.1)
- [Unidecode](https://pypi.org/project/Unidecode/) (Version 1.3.6)

You can install these libraries using pip or conda. For example, to install them using pip, you can run:

`pip install jupyterlab ipython haversine json5 matplotlib numpy pandas plotly requests scikit-learn seaborn statsmodels tqdm Unidecode`

## 6. License
This project is licensed under the [GNU General Public License (GPL) Version 3](https://www.gnu.org/licenses/gpl-3.0.en.html).

## 7. Project status
Completed
