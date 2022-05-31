from asgiref.sync import sync_to_async

import matplotlib
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator
import numpy as np
import pandas as pd
from pandas import DataFrame as df

from orders.models import Order
from orders.service import *
from products.service import *


TITLE_BY_PARTITION_TYPE = {'D': 'дням', 'W-MON': 'неделям', 'M': 'месяцам'}


matplotlib.rcParams['figure.figsize'] = (9, 7)


async def prepare_order_data(user_id, period_start, period_end):
    orders = await get_completed_orders_between(user_id, period_start, period_end)
    values = orders.values('id', 'completed_time', 'order_sum', 'num_products', 'status')
    orders_df = await sync_to_async(lambda v: df.from_records(v))(values)
    # print(orders_df)
    return orders_df


def get_overall_stats(orders_df: pd.DataFrame):
    total_products = orders_df['num_products'].sum()
    total_revenue = orders_df['order_sum'].sum()
    in_time_orders = sum(orders_df['status'] == Order.COMPLETED_IN_TIME)
    delayed_orders = sum(orders_df['status'] == Order.COMPLETED_WITH_DELAY)
    finished_orders = in_time_orders + delayed_orders
    if finished_orders != 0:
        avg_order_sum = total_revenue / finished_orders
    else:
        avg_order_sum = 0

    if finished_orders != 0:
        orders_str = f'{in_time_orders}/{finished_orders} ({round(in_time_orders / finished_orders * 100)}%)'
    else:
        orders_str = f'0/0 (0%)'

    return f'⏱ Заказов выполнено вовремя: {orders_str}\n' \
           f'📦 Продано товаров: *{total_products}*\n' \
           f'💰 Суммарная выручка: *{total_revenue}* руб.\n' \
           f'📈 Средняя сумма заказа: *{round(avg_order_sum, 2)}* руб.'


def plot_revenue_trend(filepath, orders_df, partition_type):
    orders_df = orders_df.loc[:, ['completed_time', 'order_sum']]
    grouped_orders = orders_df.groupby(pd.Grouper(key='completed_time', freq=partition_type)).sum()

    plt.ioff()
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
    plt.title('Выручка по ' + TITLE_BY_PARTITION_TYPE[partition_type])
    plt.ylabel('выручка, руб.', fontsize=12)
    plt.xticks(rotation=30, ha="right")

    x = grouped_orders.index
    y = grouped_orders[:]

    plt.grid()
    plt.plot(x, y)
    plt.savefig(filepath)
    plt.clf()


def plot_num_orders_trend(filepath, orders_df, partition_type):
    orders_df = orders_df.loc[:, ['completed_time']]
    orders_df['num_orders'] = np.ones(orders_df.shape[0], dtype=int)
    grouped_orders = orders_df.groupby(pd.Grouper(key='completed_time', freq=partition_type)).sum()

    plt.ioff()
    ax = plt.figure().gca()
    ax.yaxis.set_major_locator(MaxNLocator(integer=True))
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))

    plt.title('Количество заказов по ' + TITLE_BY_PARTITION_TYPE[partition_type])
    plt.ylabel('количество заказов, шт.', fontsize=12)
    plt.xticks(rotation=30, ha="right")

    x = grouped_orders.index
    y = grouped_orders[:]

    plt.grid()
    plt.plot(x, y)
    plt.savefig(filepath)
    plt.clf()


def plot_avg_order_sum_trend(filepath, orders_df, partition_type):
    orders_df = orders_df.loc[:, ['completed_time', 'order_sum']]
    orders_df['num_orders'] = np.ones(orders_df.shape[0])
    grouped_orders = orders_df.groupby(pd.Grouper(key='completed_time', freq=partition_type)).sum()

    plt.ioff()
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
    plt.title('Средняя сумма заказа по ' + TITLE_BY_PARTITION_TYPE[partition_type])
    plt.ylabel('сумма, руб.', fontsize=12)
    plt.xticks(rotation=30, ha="right")

    x = grouped_orders.index
    y = [0] * grouped_orders.shape[0]
    for i in range(len(y)):
        if grouped_orders['num_orders'][i] != 0:
            y[i] = grouped_orders['order_sum'][i] / grouped_orders['num_orders'][i]
        else:
            y[i] = 0

    plt.grid()
    plt.plot(x, y)
    plt.savefig(filepath)
    plt.clf()


def plot_product_popularity_trend(filepath, products, order_products):
    count_by_products = {product[0]: 0 for product in products}

    for entry in order_products:
        count_by_products[entry['product']] += entry['amount']

    plt.ioff()
    plt.grid(axis='y')
    plt.ylabel('количество товаров, шт.', fontsize=12)
    plt.title('Количество проданных товаров по наименованию')

    product_names = [entry[1] for entry in products]
    plt.bar(product_names, count_by_products.values(), color=plt.get_cmap('tab20c').colors)
    plt.savefig(filepath)
    plt.clf()
