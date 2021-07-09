import plotly.graph_objects as go
import pandas as pd
import os


def create_bar_chart(products_df, id):
    prediction_list = products_df.groupby('prediction', as_index=False).sum().sort_values(by='sum',
                                                                                          ascending=False).prediction
    sum_list = (products_df.groupby('prediction', as_index=False).sum()['sum'] / 100).sort_values(ascending=False)
    fig = go.Figure([go.Bar(x=prediction_list,
                            y=sum_list,
                            text=sum_list.astype('str'),
                            textposition='outside')])
    fig.update_yaxes(range=[0, 1.35*max(sum_list)])
    fig.update_layout(
        title=f"Стоимость каждой категории покупок в чеке",
        font={
            'family': 'Arial',
            'color': 'black',
            'size': 14
        },
        plot_bgcolor='rgba(0,0,0,0)',
        yaxis_title="Стоимость, руб.",
        xaxis_title="Категория",
        height=550,
        width=1000
    )
    fig.write_image(f"graphs/bar_chart_{id}.png")


def create_pie_chart(products_df, id):
    prediction_list = products_df.groupby('prediction', as_index=False).sum().sort_values(by='sum',
                                                                                          ascending=False).prediction
    sum_list = products_df.groupby('prediction', as_index=False).sum().sort_values(by='sum', ascending=False).iloc[:,
               2].astype('int')

    fig = go.Figure(data=[go.Pie(labels=prediction_list, values=sum_list, textposition='inside')])

    fig.update_layout(
        title=f"Доли каждой категории в чеке",
        font={
            'family': 'Arial',
            'color': 'black',
            'size': 14
        },
        width=1000
    )
    fig.write_image(f"graphs/pie_chart_{id}.png")


def del_images_by_chat_id(id):
    os.remove(f"graphs/bar_chart_{id}.png")
    os.remove(f"graphs/pie_chart_{id}.png")
