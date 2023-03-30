import dash
from dash import html, dcc 
import plotly.express as px
from dash import html, dcc, dash_table, callback_context
from apps import navigation, dataManipulator, dataReader
import main

tagsDF = dataReader.questionsPerTag(main.tagDataset)
QsPerMonthYear = dataReader.questionsPerMonthAndYear(main.tagDataset, main.aDataset)
QsPerDay = dataReader.questionsPerDay(main.qDataset)
sortedTopScoreOwners = dataReader.topOwnerIdTag(main.tagDataset, main.aDataset)

fig = px.bar(tagsDF.head(20), x='Tag', y='Occurrences', barmode="group")                 # barchart showing most searched tags
fig2 = px.scatter(QsPerMonthYear, x='Date', y='Count')                                   # scatter graph showing year-month and no. of questions
fig3 = px.bar(QsPerDay, x='Date', y='QsAsked', barmode="group")                          # barchart showing date and no. of questions

analytics_layout = html.Div(children=[
    navigation.navbar,
    html.H1(children='Graph showing the top 20 most searched tags',
            style={
                'textAlign': 'center',
                'font-family':'Arial'}),
    dcc.Graph(
        id='tag-graph',
        figure=fig
    ),
    html.H1(children='Table showing tags and frequency',
            style={
                'textAlign': 'center',
                'font-family':'Arial'}),
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
    html.H1(children='Graph showing tags searched by month and year',
            style={
                    'textAlign': 'center',
                   'font-family':'Arial'}),
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

