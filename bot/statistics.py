from asgiref.sync import sync_to_async

import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator
import numpy as np
import pandas as pd
from pandas import DataFrame as df

from orders.service import *
from products.service import *


TITLE_BY_PARTITION_TYPE = {'D': 'дням', 'W-MON': 'неделям', 'M': 'месяцам'}


async def prepare_order_data(user_id, period_start, period_end):
    orders = await get_completed_orders_between(user_id, period_start, period_end)
    values = orders.values('id', 'deadline_time', 'completed_time', 'order_sum', 'num_products')
    orders_df = await sync_to_async(lambda v: df.from_records(v))(values)
    # print(orders_df)
    return orders_df


def get_overall_stats(orders_df):
    total_products = orders_df['num_products'].sum()
    total_revenue = orders_df['order_sum'].sum()
    total_orders = orders_df.shape[0]
    avg_order_sum = total_revenue / total_orders
    return f'📄 Принято заказов: *{total_orders}*\n' \
           f'📦 Продано товаров: *{total_products}*\n' \
           f'💰 Суммарная выручка: *{total_revenue}* руб.\n' \
           f'📈 Средняя сумма заказа: *{round(avg_order_sum, 2)}* руб.'


def plot_revenue_trend(filepath, orders_df, partition_type):
    orders_df = orders_df.loc[:, ['deadline_time', 'order_sum']]
    grouped_orders = orders_df.groupby(pd.Grouper(key='deadline_time', freq=partition_type)).sum()

    plt.ioff()
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
    orders_df = orders_df.loc[:, ['deadline_time']]
    orders_df['num_orders'] = np.ones(orders_df.shape[0], dtype=int)
    grouped_orders = orders_df.groupby(pd.Grouper(key='deadline_time', freq=partition_type)).sum()

    plt.ioff()
    ax = plt.figure().gca()
    ax.yaxis.set_major_locator(MaxNLocator(integer=True))

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
    orders_df = orders_df.loc[:, ['deadline_time', 'order_sum']]
    orders_df['num_orders'] = np.ones(orders_df.shape[0])
    grouped_orders = orders_df.groupby(pd.Grouper(key='deadline_time', freq=partition_type)).sum()

    plt.ioff()
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
