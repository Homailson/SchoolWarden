import dash
from dash import dcc, html
import dash_bootstrap_components as dbc
import pandas as pd
from dash.dependencies import Input, Output
import plotly.express as px
import plotly.graph_objects as go

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
            {"$sort": {"count": -1}},  # Ordenar por contagem em ordem decrescente
            {"$limit": 10}  # Limitar aos 10 primeiros resultados
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

            # Criar uma lista de cores para as barras
            colors = px.colors.qualitative.Plotly  # Utiliza paleta de cores do Plotly

            # Criar o gráfico
            fig = go.Figure()

            fig.add_trace(go.Bar(
                x=df['classification'],
                y=df['count'],
                name='Ocorrências',
                marker_color=[colors[i % len(colors)] for i in range(len(df))]
            ))

            # Personalizar layout do gráfico
            title = 'Total de Ocorrências por Tipo'
            fig.update_layout(
                title='<b>'+title+'</b>',
                title_x=0.5,  # Centralizar o título
                yaxis=dict(
                    tickformat='d',  # Formatar o eixo Y para mostrar apenas inteiros
                    dtick=1          # Define o intervalo entre os ticks do eixo Y
                ),
                height=600,
                margin=dict(
                    l=50,  # Margem esquerda
                    r=50,  # Margem direita
                    t=100, # Margem superior
                    b=250  # Margem inferior ajustada para espaço extra para legendas
                ),
            )

            return fig.to_dict()  # Retorna o gráfico como um dicionário
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
        
    def get_figure_occurrences_by_class_and_type():
        try:
            # Consultar e agregar dados do MongoDB para total de ocorrências por turma e tipo
            pipeline = [
            {"$unwind": "$occurrences"},  # Desdobra o array de ocorrências
            {"$lookup": {
                "from": "occurrences",
                "localField": "occurrences",
                "foreignField": "_id",
                "as": "occurrence_details"
            }},
            {"$unwind": "$occurrence_details"},  # Desdobra os detalhes das ocorrências
            {"$group": {"_id": {"class": "$classe", "type": "$occurrence_details.classification"}, "count": {"$sum": 1}}},  # Conta ocorrências por turma e tipo
            {"$sort": {"count": -1}},  # Ordena por contagem em ordem decrescente
            {"$limit": 10}  # Limitar aos 10 primeiros resultados
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
                        }
                    }
                }

            # Converter os dados para um DataFrame
            df = pd.DataFrame(data)
            if '_id' not in df.columns or 'count' not in df.columns:
                raise ValueError("Expected columns '_id' or 'count' not found in data.")

            df['class'] = df['_id'].apply(lambda x: x['class'])
            df['type'] = df['_id'].apply(lambda x: x['type'])
            df['count'] = df['count']
            df.drop(columns=['_id'], inplace=True)

            # Pivotar o DataFrame para o formato necessário para o gráfico
            df_pivot = df.pivot(index='class', columns='type', values='count').fillna(0)
            df_pivot.reset_index(inplace=True)

            # Criar o gráfico com plotly.graph_objects
            traces = []
            for column in df_pivot.columns[1:]:  # Ignorar a primeira coluna que é 'class'
                traces.append(go.Bar(
                    x=df_pivot['class'],
                    y=df_pivot[column],
                    name=column
                ))

            fig = go.Figure(data=traces)
            title='Ocorrências por Turma e Tipo'
            fig.update_layout(
                title='<b>'+title+'</b>',
                title_x=0.5,
                barmode='stack',  # Para empilhar as barras
                yaxis=dict(
                    tickformat='d',  # Formatar o eixo Y para mostrar apenas inteiros
                    dtick=1,         # Define o intervalo entre os ticks do eixo Y
                ),
                legend=dict(
                    orientation='h',  # Define a orientação da legenda horizontal
                    yanchor='top',    # Ancorar a legenda na parte superior
                    y=-0.2            # Ajusta a posição da legenda para baixo do gráfico
                ),
                height=600,
                margin=dict(
                    l=50,  # Margem esquerda
                    r=50,  # Margem direita
                    t=100,  # Margem superior
                    b=250   # Margem inferior ajustada para espaço extra para legendas
                ),
            )

            return fig.to_dict()  # Retorna o gráfico como um dicionário
        except Exception as e:
            print(f"Error in get_figure_occurrences_by_class_and_type: {e}")
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
        


    def get_figure_occurrences_by_subject_and_type():
        try:
            # Consultar e agregar dados do MongoDB para total de ocorrências por matéria e tipo
            pipeline = [
            {"$unwind": "$occurrences"},  # Desdobra o array de ocorrências
            {"$lookup": {
                "from": "occurrences",
                "localField": "occurrences",
                "foreignField": "_id",
                "as": "occurrence_details"
            }},
            {"$unwind": "$occurrence_details"},  # Desdobra os detalhes das ocorrências
            {"$group": {
                "_id": {"subject": "$subject", "type": "$occurrence_details.classification"},
                "count": {"$sum": 1}
            }},
            {"$sort": {"count": -1}},  # Ordena por contagem em ordem decrescente
            {"$limit": 10}  # Limitar aos 10 primeiros resultados
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

            df['subject'] = df['_id'].apply(lambda x: x['subject'])
            df['type'] = df['_id'].apply(lambda x: x['type'])
            df['count'] = df['count']
            df.drop(columns=['_id'], inplace=True)

            # Pivotar o DataFrame para o formato necessário para o gráfico
            df_pivot = df.pivot(index='subject', columns='type', values='count').fillna(0)
            df_pivot.reset_index(inplace=True)

            # Criar o gráfico
            fig = go.Figure()

            for column in df_pivot.columns[1:]:  # Ignorar a primeira coluna que é 'subject'
                fig.add_trace(go.Bar(
                    x=df_pivot['subject'],
                    y=df_pivot[column],
                    name=column
                ))

            title='Ocorrências por Matéria e Tipo'
            fig.update_layout(
                title='<b>'+title+'</b>',
                title_x=0.5,
                barmode='stack',  # Para empilhar as barras
                yaxis=dict(
                    tickformat='d',  # Formatar o eixo Y para mostrar apenas inteiros
                    dtick=1          # Define o intervalo entre os ticks do eixo Y
                ),
                legend=dict(
                    orientation='h',  # Define a orientação da legenda horizontal
                    yanchor='top',    # Ancorar a legenda na parte inferior
                    y = -0.3          # Ajusta a posição da legenda para baixo do gráfico
                ),
                margin=dict(
                    l=50,  # Margem esquerda
                    r=50,  # Margem direita
                    t=100, # Margem superior
                    b=250  # Margem inferior ajustada para espaço extra para legendas
                ),
                height=600
            )

            return fig.to_dict()  # Retorna o gráfico como um dicionário
        except Exception as e:
            print(f"Error in get_figure_occurrences_by_subject_and_type: {e}")
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

    
    def get_figure_occurrences_by_teacher_and_type():
        try:
            pipeline = [
                    {"$match": {"role": {"$in": ["teacher", "monitor"]}}},

                    {"$unwind": "$occurrences"},

                    {"$lookup": {
                        "from": "occurrences",
                        "localField": "occurrences",
                        "foreignField": "_id",
                        "as": "occurrence_details"
                    }},
                    
                    {"$unwind": "$occurrence_details"},

                    {"$group": {
                        "_id": {
                            "teacher": "$username",
                            "type": "$occurrence_details.classification"
                        },
                        "count": {"$sum": 1}
                    }},
                    
                    {"$group": {
                        "_id": "$_id.teacher",
                        "totalOccurrences": {"$sum": "$count"},
                        "types": {
                            "$push": {
                                "type": "$_id.type",
                                "count": "$count"
                            }
                        }
                    }},
                    
                    {"$sort": {"totalOccurrences": -1}},
                    {"$limit": 10},

                    {"$unwind": "$types"},
                    
                    {"$group": {
                        "_id": {
                            "teacher": "$_id",
                            "type": "$types.type"
                        },
                        "count": {"$sum": "$types.count"}
                    }},
                    
                    {"$sort": {
                        "totalOcurrences": 1,
                    }}
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
            
            def abreviar_nomes(nome_completo):
                nomes = nome_completo.split()
                if len(nomes) > 2:
                    return f"{nomes[0]} {' '.join([n[0] + '.' for n in nomes[1:-1]])} {nomes[-1]}"
                return nome_completo            

            df['teacher'] = df['_id'].apply(lambda x: abreviar_nomes(x['teacher']))
            df['type'] = df['_id'].apply(lambda x: x['type'])
            df['count'] = df['count']
            df.drop(columns=['_id'], inplace=True)

            # Configurar o gráfico
            fig = go.Figure()

            for occurrence_type in df['type'].unique():
                filtered_df = df[df['type'] == occurrence_type]
                fig.add_trace(go.Bar(
                    x=filtered_df['teacher'],
                    y=filtered_df['count'],
                    name=occurrence_type
                ))

            title='Ocorrências por Professor e Tipo'
            fig.update_layout(
                title='<b>'+title+'</b>',
                title_x=0.5,
                barmode='stack',   # Modo de barra empilhada
                yaxis=dict(
                    tickformat='d',  # Formatar o eixo Y para mostrar apenas inteiros
                    dtick=1          # Define o intervalo entre os ticks do eixo Y
                ),
                legend=dict(
                    orientation='h',  # Define a orientação da legenda horizontal
                    yanchor='top',    # Ancorar a legenda na parte superior
                    y= -0.5,           # Ajusta a posição da legenda para baixo do gráfico
                ),
                height=600,
                margin=dict(
                    l=50,  # Margem esquerda
                    r=50,  # Margem direita
                    t=100,  # Margem superior
                    b=250   # Margem inferior ajustada para espaço extra para legendas
                ),
            )

            return fig.to_dict()  # Retorna o gráfico como um dicionário
        except Exception as e:
            print(f"Error in get_figure_occurrences_by_teacher_and_type: {e}")
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
                        ),
                        html.Div(
                            dcc.Graph(id='graph-occurrences-class-type', figure=get_figure_occurrences_by_class_and_type()),
                            className='card-graph'
                        ),
                        html.Div(
                        dcc.Graph(id='graph-subject-type', figure=get_figure_occurrences_by_subject_and_type()),
                        className='card-graph'
                        ),
                        html.Div(
                            dcc.Graph(id='graph-teacher-type', figure=get_figure_occurrences_by_teacher_and_type()),
                            className='card-graph'
                        ),
                        
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
    
    # Callback do total de ocorrências por turma e tipo
    @dash_app.callback(
        Output('graph-occurrences-class-type', 'figure'),
        Input('interval-component', 'n_intervals')
    )
    def update_graph_occurrences_class_type(n):
        try:
            return get_figure_occurrences_by_class_and_type()
        except Exception as e:
            print(f"Error in update_graph_occurrences_class_type: {e}")
            return get_figure_occurrences_by_class_and_type()  # Returning an empty figure in case of error


    # Callback do total de ocorrências por professor e tipo
    @dash_app.callback(
        Output('graph-teacher-type', 'figure'),
        Input('interval-component', 'n_intervals')
    )
    def update_graph_teacher_type(n):
        try:
            return get_figure_occurrences_by_teacher_and_type()
        except Exception as e:
            print(f"Error updating teacher-type graph: {e}")
            return get_figure_occurrences_by_teacher_and_type()
        
    @dash_app.callback(
    Output('graph-subject-type', 'figure'),
    Input('interval-component', 'n_intervals')
    )
    def update_graph_subject_type(n):
        try:
            return get_figure_occurrences_by_subject_and_type()
        except Exception as e:
            print(f"Error updating subject-type graph: {e}")
            return get_figure_occurrences_by_subject_and_type()


    return dash_app
