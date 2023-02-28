
import pandas as pd
from dataReader import *
import spacy
from lxml.html import fromstring

#still contains: 'lemmatizer', 'tagger
nlp = spacy.load("en_core_web_sm", exclude=['parser','tok2vec','attribute_ruler', 'ner']) 
print(nlp.pipe_names)


# Import the datasets (changed encoding as default is utf-8, which
# does not support some characters in the datasets

import numpy as np
import pandas as pd
from itertools import product
import dash
from dash import html
from dash import dcc
from dash import dash_table
import dash_table_experiments as dt
from dash.dependencies import Input, Output
import plotly.graph_objs as go
import plotly.express as px

tagDataset = pd.read_csv("Dataset\Tags.csv", encoding = "ISO-8859-1")
qDataset = pd.read_csv("Dataset\Questions.csv", encoding = "ISO-8859-1")
aDataset = pd.read_csv("Dataset\Answers.csv", encoding = "ISO-8859-1")


tagsDF = questionsPerTag(tagDataset)
QsPerMonthYear = questionsPerMonthAndYear(tagDataset, aDataset)
QsPerDay = questionsPerDay(qDataset)
sortedTopScoreOwners = topOwnerIdTag(tagDataset, aDataset)

#   remove html tags in the body of questions
def remove_tags(text):
    toParse = fromstring(text)
    #return str(toParse.text_content())
    return str(toParse.text_content()).replace('\n', '')

# remove stopwords from a column `column` in a DataFrame `dataframe`
# returns a list to be used by replacing worked on column or adding as a new column
def remove_stopwords(dataframe: pd.DataFrame , column: str) -> list:
    cleanedColumn = []
    for text in nlp.pipe(dataframe[column], disable=['lemmatizer', 'tagger']):
        cleanedText = [token.text for token in text if not token.is_stop and not token.is_punct]
        cleanedColumn.append(" ".join(cleanedText))
    return cleanedColumn

# lemmatize all words from a column `column` in a DataFrame `dataframe`
# returns a list to be used by replacing worked on column or adding as a new column
def lemmatize(dataframe: pd.DataFrame, column: str) -> list:
    lematizedColumn = []
    for text in nlp.pipe(dataframe[column], disable=['tagger']):
        lemmatizedText = [token.lemma_ for token in text]
        lematizedColumn.append(" ".join(lemmatizedText))
    return lematizedColumn

# remove all stop words and lemmatize all words from a column `column` in a DataFrame `dataframe`
# returns a list to be used by replacing worked on column or adding as a new column
def cleanAndLemmatize(dataframe: pd.DataFrame, column: str) -> list:
    lematizedColumn = []
    for text in nlp.pipe(dataframe[column], disable=['tagger']):
        lemmatizedText = [token.lemma_ for token in text if not token.is_stop and not token.is_punct]
        lematizedColumn.append(" ".join(lemmatizedText))
    return lematizedColumn

# Load the cleaned CSV file (if it exists)
try:
    qDataset = pd.read_csv("Dataset/Questions_cleaned.csv")
    print("Cleaned dataset loaded from file")
except FileNotFoundError:
    # If the cleaned CSV file does not exist, then clean the dataset and save it to file
    print("Cleaning dataset...")
    qDataset['Cleaned Body'] = qDataset['Body'].apply(remove_tags)
    qDataset['Cleaned Title'] = remove_stopwords(qDataset, 'Title')
    qDataset['Cleaned Body'] = remove_stopwords(qDataset, 'Cleaned Body')
    qDataset['Title'] = qDataset['Cleaned Title']
    qDataset['Body'] = qDataset['Cleaned Body']
    qDataset.drop('Cleaned Title', axis=1, inplace=True)
    qDataset.drop('Cleaned Body', axis=1, inplace=True)
    qDataset.to_csv("Dataset/Questions_cleaned.csv", index=False)
    print("Cleaned dataset saved to file")

TagsQs = pd.merge(tagDataset, qDataset[["Id", "Title", "Body"]], on="Id")

# remove stop words and html tags for both title and body parts of each tag
# qDataset['Cleaned Body'] = qDataset['Body'].apply(remove_tags)
# qDataset['Cleaned Title'] = remove_stopwords(qDataset, 'Title')
# qDataset['Cleaned Body'] = remove_stopwords(qDataset, 'Cleaned Body')

# # print(qDataset[["Title", "Cleaned Title"]].head(3))
# # print(qDataset[["Body", "Cleaned Body"]].head(3))

# qDataset['Title'] = qDataset['Cleaned Title']
# qDataset['Body'] = qDataset['Cleaned Body']
# qDataset.drop('Cleaned Title', axis=1, inplace=True) #replace and remove 'Cleaned Title' column    # axis=1 means delete a column
# qDataset.drop('Cleaned Body', axis=1, inplace=True) #replace and remove 'Cleaned Body' column      # axis=0 would mean delete a row
# TagsQs = pd.merge(tagDataset, qDataset[["Id", "Title", "Body"]], on="Id")

#   post-tagging: get nouns, verbs etc.
#   get the text of Qdatabase titile and body
QTitle = nlp(qDataset['Title'])
QBody = nlp(qDataset['Body'])
for text in QTitle:
    print(text.text, text.pos_)     # post-tagging for the title
for text in QBody:
    print(text.text, text.pos_)     # post-tagging for the body

    
fig = px.bar(tagsDF.head(20), x='Tag', y='Occurrences', barmode="group")                 # barchart showing most searched tags
fig2 = px.scatter(QsPerMonthYear, x='Date', y='Count')                                   # scatter graph showing year-month and no. of questions
fig3 = px.bar(QsPerDay, x='Date', y='QsAsked', barmode="group")                          # barchart showing date and no. of questions


app = dash.Dash()



filters = html.Div(children=[
    html.H1(children='Graph showing the top 20 most searched tags',style={'textAlign': 'center','font-family':'Arial'}),
    dcc.Graph(
        id='tag-graph',
        figure=fig
    ),
    html.H1(children='Table showing tags and frequency',style={'textAlign': 'center','font-family':'Arial'}),
    html.Div(dash_table.DataTable(
        tagsDF.to_dict('records'),
        columns=[
            {'name': 'Tag', 'id': 'Tag'},
            {'name': 'Frequency', 'id': 'Occurrences'},
        ],
        filter_action='native',
        page_size=20,
        fixed_rows={'headers': True},
        style_header={
            'backgroundColor': 'rgb(30, 30, 30)',
            'color': 'white',
        },
        style_data={
            'overflow': 'hidden',
            'textOverflow': 'ellipsis',
        },
    )),
    html.H1(children='Graph showing questions asked by month and year',style={'textAlign': 'center','font-family':'Arial'}),
    dcc.Graph(
        id='MY-graph',
        figure=fig2
    ),
    html.H1(children='Graph showing the number of questions per day',style={'textAlign': 'center','font-family':'Arial'}),
    dcc.Graph(
        id='questions-graph',
        figure=fig3
    ),
    html.H1(children='Table showing top ID for each tag',
            style={
                'textAlign': 'center',
                'font-family' : 'Arial'
            }),
    html.Div(dash_table.DataTable(
        sortedTopScoreOwners.to_dict('records'),
        columns=[
            {'name': 'Issue', 'id': 'Tag'},
            {'name': 'ID no. of staff member', 'id': 'OwnerUserId'},
            {'name': 'Score', 'id': 'Score'},
        ],
        filter_action='native',
        page_size=20,
        fixed_rows={'headers': True},
        style_header={
                'backgroundColor': 'rgb(30, 30, 30)',
                'color': 'white',
            },
        style_data={
            'overflow': 'hidden',
            'textOverflow': 'ellipsis',
        },
        ))
])


app.layout = html.Div(children=[filters])

if __name__ == '__main__':
    app.run_server(debug=True)

