
# coding: utf-8

# In[7]:


import csv
import json
import sys
import pandas as pd
import numpy as np
import gc
import time


testcase = 'new_offline_testcase.csv'
user_submission = 'submission_format.csv'


def returns(entry, exit, position):
    """Calculates the returns for the given entry_pt and exit_pt"""
    pos_return = (-1) * position * (exit - entry) / entry
    print(entry,exit,position,pos_return)
    return pos_return


def eval_score(stock_prices):
    """
    a : daily returns
    b : number of trades
    """
    if len(stock_prices) == 0:
        return 0.0

    # daily returns for the given stock
    a = sum(stock_prices)
    # number of trades for the given stock
    b = len(stock_prices)
    # check for min number of trades per stock
    # There are 160 unique stocks
    if (b/160) >= 20:
        score = (a - (b * 0.12 / 100)) * b
    else:
        score = 0.0
    print("Number of trades",b/160)
    print("a",a,"b",b)
    print("Score",(a - (b * 0.12 / 100)) * b)
    return score


def daily_return_per_stock(stockdata):
    stock_prices = []
    entry_pt = 0
    exit_pt = 0
    exit_pt_set = False
    entry_pt_set = False
    prev_date = stockdata['Date'][0]
    prev_buy_sell = stockdata['BuySell'][0]
    for i in range(stockdata.shape[0]):
        # For same day calculate daily returns for the given stock
        if stockdata['Time'][i] >= '15:15' and stockdata['BuySell'][i] != 0:
            raise Exception('The BuySell decision should be squared off before 15:15 PM. Check UID : {}'.format(
                stockdata['UID'][i]))

        if (abs(stockdata['BuySell'][i] - prev_buy_sell) == 1):
            if entry_pt_set:
                print(i, stockdata['UID'][i],stockdata['BuySell'][i],prev_buy_sell,"calc",stockdata['MidPrice'][i])
                exit_pt = stockdata['MidPrice'][i]
                # Calculating the position (long or short)
                position = stockdata['BuySell'][i] - prev_buy_sell
                try:
                    r = returns(entry_pt, exit_pt, position)
                except:
                    r = 0
                stock_prices.append(r)
                entry_pt_set = False
            else:
                print(i, stockdata['UID'][i],stockdata['BuySell'][i],prev_buy_sell,"set",stockdata['MidPrice'][i])
                entry_pt = stockdata['MidPrice'][i]
                entry_pt_set = True
        prev_date = stockdata['Date'][i]
        prev_buy_sell = stockdata['BuySell'][i]
    return stock_prices


def filter_by_date_and_stock(stockdata, stock_name, date):
    """
    Provides details of the given stock name for the given date
    """
    stockdata = stockdata[stockdata['Symbol'] == stock_name]
    stockdata.reset_index(inplace=True, drop=True)
    stockdata = stockdata[stockdata['Date'] == date]
    stockdata.reset_index(inplace=True, drop=True)
    return stockdata


def calculate_stock_scores(data):
    ustocks = data['Symbol'].unique()
    udates = data['Date'].unique()
    stock_scores=[]
    for stock in ustocks:

        for date in udates:
            temp = filter_by_date_and_stock(data, stock, date)
            daily_returns = daily_return_per_stock(temp)

            stock_scores.extend(daily_returns)

    stock_scores = eval_score(stock_scores)

    return stock_scores


def verify_submission():
    if not user_submission.endswith('.csv'):
        raise Exception(
            'Please upload a csv file containing predictions in the format given in the sample submission file')

    fp_submission = pd.read_csv(user_submission)
    fp_testcase = pd.read_csv(testcase)

    if fp_submission.shape[0] != 394661:
        raise Exception('File does not contain the correct number of rows')
    if list(fp_submission.columns) != list(['UID', 'BuySell']):
        raise Exception('File does not contain correct headers, please check sample_submission file')

    ids_not_present = set(fp_testcase['UID']) - set(fp_submission['UID'])
    for idx in list(ids_not_present):
        key_not_found = idx
        raise Exception('File does not contain prediction for id:{0}'.format(key_not_found))

    data = fp_testcase.merge(fp_submission, on='UID')
    # Merging on test case file which contains the following headers:
    # UID, Date, Time, Symbol and MidPrice
    del fp_submission, fp_testcase
    gc.collect()
    start_time = time.time()
    score = calculate_stock_scores(data)
    end_time = time.time()
    print("{0:.6f} ".format(score))



try:
    verify_submission()
except Exception as e:
    sys.exit(e.args[0])
