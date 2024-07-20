import dash
from dash import dcc, html
import dash_bootstrap_components as dbc
import pandas as pd
from dash.dependencies import Input, Output

def create_dash_app(flask_app, mongo):
    dash_app = dash.Dash(
        __name__,
        server=flask_app,
        url_base_pathname='/dash/',
        external_stylesheets=[dbc.themes.BOOTSTRAP]
    )

    def get_figure_occurrences():
        try:
            # Consultar e agregar dados do MongoDB para total de ocorrências por tipo
            pipeline = [
                {"$group": {"_id": "$classification", "count": {"$sum": 1}}},
                {"$sort": {"_id": 1}}  # Ordenar por classificação
            ]
            data = list(mongo.db.occurrences.aggregate(pipeline))

            if not data:
                print("No data found from MongoDB.")
                return {
                    'data': [],
                    'layout': {
                        'title': 'No Data Available',
                        'yaxis': {
                            'tickformat': 'd',
                            'dtick': 1
                        }
                    }
                }

            # Converter os dados para um DataFrame
            df = pd.DataFrame(data)
            if '_id' not in df.columns or 'count' not in df.columns:
                raise ValueError("Expected columns '_id' or 'count' not found in data.")

            df['classification'] = df['_id']
            df['count'] = df['count']
            df.drop(columns=['_id'], inplace=True)

            # Configurar o gráfico
            fig = {
                'data': [{'x': df['classification'], 'y': df['count'], 'type': 'bar', 'name': 'Total de Ocorrências'}],
                'layout': {
                    'title': 'Total de Ocorrências por Tipo',
                    'yaxis': {
                        'tickformat': 'd',  # Formatar o eixo Y para mostrar apenas inteiros
                        'dtick': 1          # Define o intervalo entre os ticks do eixo Y
                    },
                    'height': 600,
                    'margin': {
                        'l': 50,  # Margem esquerda
                        'r': 50,  # Margem direita
                        't': 150,  # Margem superior
                        'b': 150   # Margem inferior para espaço extra para legendas
                    },
                }
            }
            return fig
        except Exception as e:
            print(f"Error in get_figure_occurrences: {e}")
            return {
                'data': [],
                'layout': {
                    'title': 'Error',
                    'yaxis': {
                        'tickformat': 'd',
                        'dtick': 1
                    }
                }
            }
        
    def get_figure_occurrences_by_class():
        try:
            # Consultar e agregar dados do MongoDB para total de ocorrências por turma
            pipeline = [
                {"$unwind": "$occurrences"},  # Desdobra o array de ocorrências
                {"$group": {"_id": "$classe", "count": {"$sum": 1}}},  # Conta ocorrências por turma
                {"$sort": {"_id": 1}}  # Ordena por nome da turma
            ]
            data = list(mongo.db.classes.aggregate(pipeline))

            if not data:
                print("No data found from MongoDB.")
                return {
                    'data': [],
                    'layout': {
                        'title': 'No Data Available',
                        'yaxis': {
                            'tickformat': 'd',
                            'dtick': 1
                        },
                        'height': 600,
                        'margin': {
                            'l': 50,  # Margem esquerda
                            'r': 50,  # Margem direita
                            't': 150,  # Margem superior
                            'b': 150   # Margem inferior para espaço extra para legendas
                        },
                    }
                }

            # Converter os dados para um DataFrame
            df = pd.DataFrame(data)
            if '_id' not in df.columns or 'count' not in df.columns:
                raise ValueError("Expected columns '_id' or 'count' not found in data.")

            df['class'] = df['_id']
            df['count'] = df['count']
            df.drop(columns=['_id'], inplace=True)

            # Configurar o gráfico
            fig = {
                'data': [{'x': df['class'], 'y': df['count'], 'type': 'bar', 'name': 'Total de Ocorrências por Turma'}],
                'layout': {
                    'title': 'Total de Ocorrências por Turma',
                    'yaxis': {
                        'tickformat': 'd',  # Formatar o eixo Y para mostrar apenas inteiros
                        'dtick': 1          # Define o intervalo entre os ticks do eixo Y
                    }
                }
            }
            return fig
        except Exception as e:
            print(f"Error in get_figure_occurrences_by_class: {e}")
            return {
                'data': [],
                'layout': {
                    'title': 'Error',
                    'yaxis': {
                        'tickformat': 'd',
                        'dtick': 1
                    }
                }
            }

    def get_figure_occurrences_by_subject():
        try:
            # Consultar e agregar dados do MongoDB para total de ocorrências por matéria
            pipeline = [
                {"$unwind": "$occurrences"},  # Desdobra o array de ocorrências
                {"$group": {"_id": "$subject", "count": {"$sum": 1}}},  # Conta ocorrências por matéria
                {"$sort": {"_id": 1}}  # Ordena por nome da matéria
            ]
            data = list(mongo.db.subjects.aggregate(pipeline))

            if not data:
                print("No data found from MongoDB.")
                return {
                    'data': [],
                    'layout': {
                        'title': 'No Data Available',
                        'yaxis': {
                            'tickformat': 'd',
                            'dtick': 1
                        }
                    }
                }

            # Converter os dados para um DataFrame
            df = pd.DataFrame(data)
            if '_id' not in df.columns or 'count' not in df.columns:
                raise ValueError("Expected columns '_id' or 'count' not found in data.")

            df['subject'] = df['_id']
            df['count'] = df['count']
            df.drop(columns=['_id'], inplace=True)

            # Configurar o gráfico
            fig = {
                'data': [{'x': df['subject'], 'y': df['count'], 'type': 'bar', 'name': 'Total de Ocorrências por Matéria'}],
                'layout': {
                    'title': 'Total de Ocorrências por Matéria',
                    'yaxis': {
                        'tickformat': 'd',  # Formatar o eixo Y para mostrar apenas inteiros
                        'dtick': 1          # Define o intervalo entre os ticks do eixo Y
                    }
                }
            }
            return fig
        except Exception as e:
            print(f"Error in get_figure_occurrences_by_subject: {e}")
            return {
                'data': [],
                'layout': {
                    'title': 'Error',
                    'yaxis': {
                        'tickformat': 'd',
                        'dtick': 1
                    }
                }
            }


    def get_figure_occurrences_by_teacher():
        try:
            # Consultar e agregar dados do MongoDB para total de ocorrências por professor
            pipeline = [
                {"$match": {"role": "teacher"}},  # Filtra somente os usuários com papel de professor
                {"$unwind": "$occurrences"},  # Desdobra o array de ocorrências
                {"$lookup": {
                    "from": "occurrences",
                    "localField": "occurrences",
                    "foreignField": "_id",
                    "as": "occurrence_details"
                }},
                {"$unwind": "$occurrence_details"},  # Desdobra os detalhes das ocorrências
                {"$group": {"_id": "$username", "count": {"$sum": 1}}},  # Conta ocorrências por professor
                {"$sort": {"_id": 1}}  # Ordena por nome do professor
            ]
            data = list(mongo.db.users.aggregate(pipeline))

            if not data:
                print("No data found from MongoDB.")
                return {
                    'data': [],
                    'layout': {
                        'title': 'No Data Available',
                        'yaxis': {
                            'tickformat': 'd',
                            'dtick': 1
                        }
                    }
                }

            # Converter os dados para um DataFrame
            df = pd.DataFrame(data)
            if '_id' not in df.columns or 'count' not in df.columns:
                raise ValueError("Expected columns '_id' or 'count' not found in data.")

            df['teacher'] = df['_id']
            df['count'] = df['count']
            df.drop(columns=['_id'], inplace=True)

            # Configurar o gráfico
            fig = {
                'data': [{'x': df['teacher'], 'y': df['count'], 'type': 'bar', 'name': 'Total de Ocorrências por Professor'}],
                'layout': {
                    'title': 'Total de Ocorrências por Professor',
                    'yaxis': {
                        'tickformat': 'd',  # Formatar o eixo Y para mostrar apenas inteiros
                        'dtick': 1          # Define o intervalo entre os ticks do eixo Y
                    }
                }
            }
            return fig
        except Exception as e:
            print(f"Error in get_figure_occurrences_by_teacher: {e}")
            return {
                'data': [],
                'layout': {
                    'title': 'Error',
                    'yaxis': {
                        'tickformat': 'd',
                        'dtick': 1
                    }
                }
            }

    def serve_layout():
        return html.Div(
            children=[
                html.Div(
                    className='grid-container',
                    children=[
                        html.Div(
                            dcc.Graph(id='graph-occurrences', figure=get_figure_occurrences()),
                            className='card-graph'
                        ),  # Gráfico de total de ocorrências por tipo
                        html.Div(
                            dcc.Graph(id='graph-teachers', figure=get_figure_occurrences_by_teacher()),
                            className='card-graph'
                        ),  # Gráfico de total de ocorrências por professor
                        html.Div(
                            dcc.Graph(id='graph-classes', figure=get_figure_occurrences_by_class()),
                            className='card-graph'
                        ),  # Gráfico de total de ocorrências por turma
                        html.Div(
                            dcc.Graph(id='graph-subjects', figure=get_figure_occurrences_by_subject()),
                            className='card-graph'
                        ),  # Gráfico de total de ocorrências por matéria
                        dcc.Interval(
                            id='interval-component',
                            interval=60*60*1000,  # milliseconds in 1 hour
                            n_intervals=0
                        ),
                    ]
                )
            ]
        )

    # Define o layout como uma função
    dash_app.layout = serve_layout

    @dash_app.callback(
        Output('graph-occurrences', 'figure'),
        Input('interval-component', 'n_intervals')
    )
    def update_graph_occurrences(n):
        try:
            return get_figure_occurrences()
        except Exception as e:
            print(f"Error in update_graph_occurrences: {e}")
            return get_figure_occurrences()  # Returning an empty figure in case of error

    @dash_app.callback(
        Output('graph-teachers', 'figure'),
        Input('interval-component', 'n_intervals')
    )
    def update_graph_teachers(n):
        try:
            return get_figure_occurrences_by_teacher()
        except Exception as e:
            print(f"Error in update_graph_teachers: {e}")
            return get_figure_occurrences_by_teacher()  # Returning an empty figure in case of error
        
    @dash_app.callback(
    Output('graph-subjects', 'figure'),
    Input('interval-component', 'n_intervals')
)
    def update_graph_subjects(n):
        try:
            return get_figure_occurrences_by_subject()
        except Exception as e:
            print(f"Error updating subjects graph: {e}")
            return get_figure_occurrences_by_subject()
        
    @dash_app.callback(
        Output('graph-classes', 'figure'),
        Input('interval-component', 'n_intervals')
    )
    def update_graph_classes(n):
        try:
            return get_figure_occurrences_by_class()
        except Exception as e:
            print(f"Error updating classes graph: {e}")
            return get_figure_occurrences_by_class()

    return dash_app
