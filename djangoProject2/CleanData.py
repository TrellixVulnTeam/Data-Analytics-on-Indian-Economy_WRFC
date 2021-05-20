import pandas as pd
import numpy as np
import platform as pf
import os
import xlrd
import shutil


def removeExist(path):
    if os.path.exists(path):
        os.remove(path)


def getNewPath(path):
    return '../clean_data' + path[7:]


########################################
# Trans currencies to USD base
def TransToUSDBase():
    print('### Trans Currencies to USD Base Start ###')
    currenciesPath = '/home/cheeryluck/PycharmProjects/djangoProject2/data/market/Currencies/'
    currencies = ['AUD_USD.csv', 'EUR_USD.csv', 'GBP_USD.csv']
    for currency in currencies:
        curPath = currenciesPath + currency
        newPath = currenciesPath + 'USD_' + currency[:3] + '.csv'
        df = pd.read_csv(curPath)
        columns = [df.columns.values[1], df.columns.values[3], df.columns.values[4], df.columns.values[5]]
        for col in columns:
            df[col] = df[col].apply(lambda x: 1 / x)
        removeExist(newPath)
        df.to_csv(newPath, index=False, header=True)
    print('### Trans Currencies to USD Base Completed ###')


########################################
# Trans Yahoo Data Format to NASDAQ Data Format
def TransYahooToNASDAQ():
    print('### Trans Yahoo Data to NASDAQ Data Format Start ###')
    path_index = '/home/cheeryluck/PycharmProjects/djangoProject2/data/market/Index/'
    file_path = []
    file_path.append(path_index + 'CBOE_VolatilityIndex.csv')
    file_path.append(path_index + 'DowJones_IndustrialAvg.csv')
    file_path.append(path_index + 'NASDAQ_100_Index.csv')
    file_path.append(path_index + 'Russell_2000.csv')
    for path in file_path:
        df = pd.read_csv(path)
        # remove redundant column 'Adj Close'
        df = df.drop('Adj Close', axis=1, errors='ignore')
        # rename Close to Close/Last and put to second place
        # print(df.columns.values)
        if 'Close' in df.columns.values:
            df_close = df.Close
            df = df.drop('Close', axis=1, errors='ignore')
            df.insert(1, 'Close/Last', df_close)
        # reorder in time
        df['Date'] = pd.to_datetime(df['Date'])
        df.sort_values('Date', inplace=True, ascending=False)
        # save
        df.to_csv(path, index=False, header=True)
    print('### Trans Yahoo Data to NASDAQ Data Format Completed ###')


########################################
# Clean Data From NASDAQ (Excepet All Stock Data)
def CleanDataFromNASDAQ():
    print('### Clean Data Sets From NASDAQ Start ###')
    file_idx = '/home/cheeryluck/PycharmProjects/djangoProject2/data1/NasdaqSource.txt'
    file_path = {}
    for line in open(file_idx):
        path = line.strip('\n')
        name = path.split("/")[-1][:-4]
        file_path[name] = path

    for path in file_path.values():
        df = pd.read_csv(path)
        # format column name, delete redundant whitespace in column names
        df.columns = [x.strip() for x in df.columns.values if x.strip() != '']
        # remove redundant column 'Volume'
        df = df.drop('Volume', axis=1, errors='ignore')
        # save
        df.to_csv(getNewPath(path), index=False, header=True)
    print('### Clean Data Sets From NASDAQ Completed ###')


########################################
# Clean Data From Other Source
def CleanOtherSources():
    print('### Clean Data Sets From Other Sources Start ###')
    file_CrudeOil_WTI_MacroTrends = '/home/cheeryluck/PycharmProjects/djangoProject2/data/market/Commodities/Energies/CrudeOil_WTI_macrotrends.csv'
    file_Finance_Sector_Related_Policy_Responses = '/home/cheeryluck/PycharmProjects/djangoProject2//data/general/FinanceSectorRelatedPolicyResponses.xlsx'
    file_Industrial_Production_Index = '/home/cheeryluck/PycharmProjects/djangoProject2/data/general/IndustrialProductionIndex.csv'
    file_Initial_Jobless_Claims = '/home/cheeryluck/PycharmProjects/djangoProject2/data/employment/InitialJoblessClaims.csv'
    file_Unemployment_Rate = '/home/cheeryluck/PycharmProjects/djangoProject2/data/employment/UnemploymentRate.csv'

    # Finance Sector Related Policy Responses
    FSRPR = pd.read_excel(file_Finance_Sector_Related_Policy_Responses, sheet_name='Raw data')
    # drop redundant columns
    FSRPR = FSRPR.drop('Iso 3 Code', axis=1, errors='ignore')
    FSRPR = FSRPR.drop('Entry date', axis=1, errors='ignore')
    # reorder
    FSRPR_Country = FSRPR.Country
    FSRPR = FSRPR.drop('Country', axis=1, errors='ignore')
    FSRPR.insert(0, 'Country', FSRPR_Country)
    FSRPR.to_csv(getNewPath(file_Finance_Sector_Related_Policy_Responses[:-4] + 'csv'), index=False, header=True)

    # CrudeOil WTI MacroTrends
    CWM = pd.read_csv(file_CrudeOil_WTI_MacroTrends)
    # reorder in time
    CWM['Date'] = pd.to_datetime(CWM['Date'])
    CWM.sort_values('Date', inplace=True, ascending=False)
    # format column name, delete redundant whitespace in column names
    CWM.columns = [x.strip() for x in CWM.columns.values if x.strip() != '']
    # delete invalid future data
    CWM.dropna(subset=['value'], inplace=True)
    # rename value to Close/Last
    if 'value' in CWM.columns.values:
        CWM.rename(columns={'value': 'Close/Last'}, inplace=True)
    CWM.to_csv(getNewPath(file_CrudeOil_WTI_MacroTrends), index=False, header=True)

    # Others with date (reorder date)
    file_path = []
    file_path.append(file_Industrial_Production_Index)
    file_path.append(file_Initial_Jobless_Claims)
    file_path.append(file_Unemployment_Rate)
    for path in file_path:
        df = pd.read_csv(path)
        # reorder in time
        df['Date'] = pd.to_datetime(df['Date'])
        df.sort_values('Date', inplace=True, ascending=False)
        # save
        df.to_csv(getNewPath(path), index=False, header=True)
    print('### Clean Data Sets From Other Sources Completed ###')


########################################
# this function modify Covid-19 world data from JHU CSSE
def CleanCovid19Data(covidDataPath):
    print('### Clean Covid-19 Data Sets Start ###')
    df = pd.read_csv(covidDataPath)
    # remove useless columns
    df = df.drop(['Province/State', 'Lat', 'Long'], 1, errors='ignore')
    if 'Country/Region' in df.columns.values:
        df.rename(columns={'Country/Region': 'Date'}, inplace=True)
        # transform date format to 'yyyy-mm-dd'
        # df.rename(lambda x: modifyDate(x), axis = 'columns', inplace = True)
        # combine province/state data to the whole country
        group_df = df[1:].groupby(df['Date'])
        sum_df = group_df.sum()
        # calculate world data
        sum_df.loc["World"] = sum_df.apply(lambda x: x.sum())
        # transposition, probably not necessary
        result = pd.DataFrame(sum_df.values.T, index=sum_df.columns, columns=sum_df.index)
        # transform date format to 'yyyy-mm-dd'
        result.index = pd.to_datetime(result.index)
        result.index.name = 'Date'
        # output
    result.to_csv(getNewPath(covidDataPath), index=True, header=True)
    print('### Clean Covid-19 Data Sets Completed ###')


########################################
# this function transform every date to format "yyyy-mm-dd"
def FormatDate():
    '''
    this function is quite dump, it walk through the whole data directory, and try to modify every csv file
    but it some how make sense since most of our file need to be transformed
    '''
    print('### Format Date Column Start ###')
    rootPath = "/home/cheeryluck/PycharmProjects/djangoProject2/data"
    for root, dirs, files in os.walk(rootPath):
        for file in files:
            path = os.path.join(root, file)
            if path.endswith('.csv'):
                df = pd.read_csv(path)
                if 'DATE' in df.columns:
                    df.rename(columns={'DATE': 'Date'}, inplace=True)
                if 'date' in df.columns:
                    df.rename(columns={'date': 'Date'}, inplace=True)
                if 'Date' in df.columns:
                    df['Date'] = pd.to_datetime(df['Date'])
                df.to_csv(path, index=False, header=True)
    print('### Format Date Column Completed ###')


def TrimCurrencies():
    rootPath = '/home/cheeryluck/PycharmProjects/djangoProject2/clean_data/market/Currencies'
    for root, dirs, files in os.walk(rootPath):
        for file in files:
            filePath = rootPath + '/' + file
            fileNewPath = rootPath + '/' + str(file[4:])
            os.rename(filePath, fileNewPath)


def CleanAllHistory():
    all_symbol = []
    # check two stock source files and use their intersection
    fp = open('/home/cheeryluck/PycharmProjects/djangoProject2/data/market/Stock/all symbols/all_symbols.txt')
    for line in fp:
        all_symbol.append(line.strip())
    fp = open('/home/cheeryluck/PycharmProjects/djangoProject2/data/market/Stock/all symbols/excluded_symbols.txt')
    for line in fp:
        all_symbol.append(line.strip())
    fp.close()

    company_list_path = '/home/cheeryluck/PycharmProjects/djangoProject2/data/market/Stock/company info/companylist.csv'
    company_list = pd.read_csv(company_list_path)
    # drop some redundant columns
    company_list = company_list.drop('ADR TSO', axis=1, errors='ignore')
    company_list = company_list.drop('LastSale', axis=1, errors='ignore')
    company_list = company_list.drop('IPOyear', axis=1, errors='ignore')
    company_list = company_list.drop('Summary Quote', axis=1, errors='ignore')
    # must ensure that sector is not NaN
    company_list = company_list.dropna(subset=['Sector'])
    company_list.to_csv('/home/cheeryluck/PycharmProjects/djangoProject2/clean_data/market/Stock/NewCompanyList.csv', index=False, header=True)
    company_list = company_list['Symbol'].values.tolist()
    final_list = list(set(all_symbol).intersection(set(company_list)))

    # generate a new directory to store all modified stock history
    old_path = '/home/cheeryluck/PycharmProjects/djangoProject2/full_history/'
    new_path = '/home/cheeryluck/PycharmProjects/djangoProject2/clean_data/market/Stock/history/'
    if not os.path.exists(new_path):
        os.mkdir(new_path)
    counter = 0
    for each_file in final_list:
        counter += 1
        if counter % 500 == 0:
            print('Progress: ' + str(counter) + '/' + str(len(final_list)))

        file_path = old_path + each_file + '.csv'
        try:
            file = pd.read_csv(file_path)
        except:
            continue

        # drop close column
        file = file.drop('close', axis=1, errors='ignore')
        # filter and use recent 2 years' record
        file = file[file['date'] >= '2018-01-01']
        file.to_csv(new_path + each_file + '.csv', index=False, header=True)


if os.path.exists('/home/cheeryluck/PycharmProjects/djangoProject2/clean_data/'):
    shutil.rmtree('/home/cheeryluck/PycharmProjects/djangoProject2/data/', ignore_errors=True)
    shutil.rmtree('/home/cheeryluck/PycharmProjects/djangoProject2/clean_data/', ignore_errors=True)

sys = pf.system()
if sys == 'Darwin' or sys == 'Linux':
    os.system('unzip -o /home/cheeryluck/PycharmProjects/djangoProject2/raw_data_0422.zip -d ./')
    os.system('unzip -o ../raw_stock_history_0421.zip -d ../')
if sys == 'Windows':
    os.system('powershell -command "Expand-Archive" -Path "../raw_data_0422.zip" -DestinationPath "../" -Force')
    os.system('powershell -command "Expand-Archive" -Path "../raw_stock_history_0421.zip" -DestinationPath "../" -Force')

os.makedirs('/home/cheeryluck/PycharmProjects/djangoProject2/clean_data/')
os.makedirs('/home/cheeryluck/PycharmProjects/djangoProject2/clean_data/covid-19')
os.makedirs('/home/cheeryluck/PycharmProjects/djangoProject2/clean_data/general')
os.makedirs('/home/cheeryluck/PycharmProjects/djangoProject2/clean_data/employment')
os.makedirs('/home/cheeryluck/PycharmProjects/djangoProject2/clean_data/market/Stock/history')
os.makedirs('/home/cheeryluck/PycharmProjects/djangoProject2/clean_data/market/Commodities/Energies')
os.makedirs('/home/cheeryluck/PycharmProjects/djangoProject2/clean_data/market/Commodities/Grains')
os.makedirs('/home/cheeryluck/PycharmProjects/djangoProject2/clean_data/market/Commodities/Meats')
os.makedirs('/home/cheeryluck/PycharmProjects/djangoProject2/clean_data/market/Commodities/Metals')
os.makedirs('/home/cheeryluck/PycharmProjects/djangoProject2/clean_data/market/Commodities/Softs')
os.makedirs('/home/cheeryluck/PycharmProjects/djangoProject2/clean_data/market/Cryptocurrencies')
os.makedirs('/home/cheeryluck/PycharmProjects/djangoProject2/clean_data/market/Currencies')
os.makedirs('/home/cheeryluck/PycharmProjects/djangoProject2/clean_data/market/Funds_ETFs')
os.makedirs('/home/cheeryluck/PycharmProjects/djangoProject2/clean_data/market/Index')

FormatDate()
TransToUSDBase()
TransYahooToNASDAQ()
CleanDataFromNASDAQ()
CleanOtherSources()
CleanCovid19Data('/home/cheeryluck/PycharmProjects/djangoProject2/data/covid-19/time_series_covid19_confirmed_global.csv')
CleanCovid19Data('/home/cheeryluck/PycharmProjects/djangoProject2/data/covid-19/time_series_covid19_deaths_global.csv')
TrimCurrencies()
CleanAllHistory()
