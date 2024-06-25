import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt

comments = pd.read_csv('/Users/aman/dataAnalysis/ayushi/UScomments.csv', on_bad_lines='skip')

print(comments.head())

print(comments.isnull().sum())

comments.dropna(inplace=True)
print(comments.isnull().sum())

# sentiment Analysis
from textblob import TextBlob
print(comments.head())

polarity = []
for comment in comments['comment_text']:
    try:
        polarity.append(TextBlob(comment).sentiment.polarity)
    except:
        polarity.append(0)

print(len(polarity))

comments['polarity'] = polarity
print(comments.head())

filters1 = comments['polarity']==1
comments_positive = comments[filters1]

filters2 = comments['polarity']==-1
comments_negative = comments[filters2]

# wordcloud analysis
from wordcloud import WordCloud, STOPWORDS
set(STOPWORDS)

print(type(comments['comment_text']))

total_comments_positive = ' '.join(comments_positive['comment_text'])
wordcloud = WordCloud(stopwords=set(STOPWORDS)).generate(total_comments_positive)

plt.imshow(wordcloud)
plt.axis('off')
plt.show()

total_comments_negative = ' '.join(comments_negative['comment_text'])
wordcloud = WordCloud(stopwords=set(STOPWORDS)).generate(total_comments_negative)

plt.imshow(wordcloud)
plt.axis('off')
plt.show()

#  Emoji analysis

import emoji
print(emoji.__version__)

comments['comment_text'].head(6)

all_emoji_list= [char for comment in comments['comment_text'].dropna() for char in comment if char in emoji.EMOJI_DATA]

print(all_emoji_list[0:10])

from collections import Counter

emojis = [Counter(all_emoji_list).most_common(10)[i][0] for i in range(10)]
print(emojis)

freqs = [Counter(all_emoji_list).most_common(10)[i][1] for i in range(10)]

print(freqs)

import plotly.graph_objs as go
from plotly.offline import iplot

trace = go.Bar(x= emojis, y = freqs)

fig = go.Figure(data=[trace])
iplot(fig)

# collect entire data of youtube

import os

files = os.listdir('/Users/aman/dataAnalysis/ayushi/additional_data')
print(files)

files_csv = [file for file in files if '.csv' in file]
print(files_csv)

import warnings
from warnings import filterwarnings
filterwarnings('ignore')

full_df = pd.DataFrame()
path = '/Users/aman/dataAnalysis/ayushi/additional_data'

for file in files_csv:
    current_df = pd.read_csv(path+'/'+file, encoding='iso-8859-1',on_bad_lines='skip')
    full_df = pd.concat([full_df,current_df],ignore_index=True)

print(full_df.shape)

# export data into csv, json, databases

print(full_df[full_df.duplicated()].shape)

full_df = full_df.drop_duplicates()
print(full_df.shape)

full_df[0:1000].to_csv('/Users/aman/dataAnalysis/ayushi/youtube_sample.csv',index=False)

full_df[0:1000].to_json('/Users/aman/dataAnalysis/ayushi/youtube_sample.json')

from sqlalchemy import create_engine

engine = create_engine('sqlite:////Users/aman/dataAnalysis/ayushi/youtube_sample.sqlite')

full_df[0:1000].to_sql('Users', con=engine, if_exists='append')

# catagory has maximum likes

print(full_df.head())

print(full_df['category_id'].unique())

json_df = pd.read_json('/Users/aman/dataAnalysis/ayushi/additional_data/US_category_id.json')
print(json_df)

print(json_df['items'][0])

cat_dict = {}

for item in json_df['items'].values:
    cat_dict[int(item['id'])] = item['snippet']['title']

print(cat_dict)

full_df['category_name']= full_df['category_id'].map(cat_dict)
print(full_df.head())

plt.figure(figsize=(12,8))
sns.boxplot(x='category_name', y = 'likes', data = full_df)
plt.xticks(rotation = 45)
plt.show()

# find out weather audience is engaged or not

full_df['like_rate']=(full_df['likes']/full_df['views'])*100
full_df['dislike_rate']=(full_df['dislikes']/full_df['views'])*100
full_df['comment_count_rate']=(full_df['comment_count']/full_df['views'])*100

print(full_df.columns)

plt.figure(figsize=(8,6))
sns.boxplot(x='category_name', y = 'like_rate', data = full_df)
plt.xticks(rotation = 45)
plt.show()

sns.regplot(x='views', y='likes',data= full_df)
plt.show()

print(full_df[['views','likes','dislikes']].corr())
sns.heatmap(full_df[['views','likes','dislikes']].corr(),annot=True)
plt.show()

#Analysing trending videos of youtube
cdf = full_df.groupby(['channel_title']).size().sort_values(ascending=False).reset_index()
print(cdf)

cdf = cdf.rename(columns={0:'total_videos'})
print(cdf)

import plotly.express as px

fig1 = px.bar(data_frame=cdf[0:20],x='channel_title', y='total_videos')
fig1.show()

# punctuations in title and tag have an impect on views, likes, dislikes

import string
print(string.punctuation)

def punc_count(text):
    return len([char for char in text if char in string.punctuation])

sample = full_df[0:10000]

sample['count_punc']=sample['title'].apply(punc_count)
print(sample['count_punc'])

plt.figure(figsize=(8,6))
sns.boxplot(x='count_punc', y = 'likes', data = sample)
plt.show()