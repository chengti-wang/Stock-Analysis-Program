import download_module
import load_data_module
import os
import numpy as np
from datetime import datetime
import time
import shutil
import glob
import matplotlib.pyplot as plt

midCycleAllocations = {
    "TotalStockMarket": 0.55,
    "TotalInternationalStock": 0.08,
    "RealEstate": 0.2,
    "MaterialStock": 0.02,
    "TotalBondMarket": 0.1,
    "Cash": 0.05,
}

boomAllocations = {
    "TotalStockMarket": 0.5,
    "TotalInternationalStock": 0.08,
    "RealEstate": 0.25,
    "MaterialStock": 0.01,
    "TotalBondMarket": 0.1,
    "Cash": 0.06,
}

peakAllocations = {
    "TotalStockMarket": 0.4,
    "TotalInternationalStock": 0.08,
    "RealEstate": 0.15,
    "MaterialStock": 0,
    "TotalBondMarket": 0.2,
    "Cash": 0.17,
}

overheatAllocations = {
    "TotalStockMarket": 0.3,
    "TotalInternationalStock": 0.05,
    "RealEstate": 0.05,
    "MaterialStock": 0,
    "TotalBondMarket": 0.3,
    "Cash": 0.3,
}

recessionAllocations = {
    "TotalStockMarket": 0.4,
    "TotalInternationalStock": 0.05,
    "RealEstate": 0.05,
    "MaterialStock": 0,
    "TotalBondMarket": 0.2,
    "Cash": 0.3,
}

anticipatedAllocations = {
    "TotalStockMarket": 0.6,
    "TotalInternationalStock": 0.08,
    "RealEstate": 0.1,
    "MaterialStock": 0.02,
    "TotalBondMarket": 0.1,
    "Cash": 0.1,
}

periodStartDates = {
    np.datetime64('2011-05-25'): 'Expansion - Peak',
    np.datetime64('2011-06-25'): 'Expansion - Overheat',
    np.datetime64('2011-09-25'): 'Recession',
    np.datetime64('2012-09-25'): 'Recovery - Anticipated',
    np.datetime64('2013-06-25'): 'Recovery - Mid-Cycle',
    np.datetime64('2014-03-25'): 'Expansion - Boom',
    np.datetime64('2014-09-25'): 'Expansion - Peak',
    np.datetime64('2015-03-25'): 'Expansion - Overheat',
    np.datetime64('2015-06-25'): 'Recession',
    np.datetime64('2016-06-25'): 'Recovery - Anticipated',
    np.datetime64('2017-06-25'): 'Recovery - Mid-Cycle',
    np.datetime64('2018-03-25'): 'Expansion - Boom',
    np.datetime64('2018-09-25'): 'Expansion - Peak',
    np.datetime64('2018-12-25'): 'Expansion - Overheat',
    np.datetime64('2019-03-25'): 'Recession',
    np.datetime64('2020-06-25'): 'Recovery - Anticipated',
    np.datetime64('2020-09-25'): 'Recovery - Mid-Cycle',
    np.datetime64('2020-12-25'): 'Expansion - Boom',
    np.datetime64('2021-03-25'): 'Expansion - Peak',
    np.datetime64('2021-05-25'): 'Expansion - Peak',
    np.datetime64('2021-06-25'): 'Expansion - Overheat'
}

cycleNameToAllocationShares = {
    'Expansion - Peak': peakAllocations,
    'Expansion - Overheat': overheatAllocations,
    'Recession': recessionAllocations,
    'Recovery - Anticipated': anticipatedAllocations,
    'Recovery - Mid-Cycle': midCycleAllocations,
    'Expansion - Boom': boomAllocations
}


def generateDatesFromRefDate(ref_date, years):
    dates = []
    for year in range(years + 1):
        d = (ref_date - year * 365).tolist()
        dates.append((d.month, d.day, d.year))
    dates = dates[::-1]
    return dates


def plotAllETFsPriceHistory(etf_data, start_date):
    names = []
    for key, value in etf_data.items():
        # Dates list?
        names.append(key)
        for i, date_ in enumerate(value[0]):
            if date_ >= start_date:
                dates_list = value[0][i:]
                values_list = value[1][i:]
                break

        plt.plot(dates_list, values_list)

    plt.legend(names)
    plt.ylabel('Price ($)')
    plt.title('ETF Price Growth')
    plt.show()
    # Go through each ETF name and data. Plot the price history
    # using matplotlib.


def findClosestValidDateIndex(check_date, dates_list):
    for i, date_ in enumerate(dates_list):
        if check_date == date_:
            return i
        if date_ > check_date:
            if i != 0:
                return i - 1
            else:
                return 0
    return len(dates_list) - 1


def yearBalanceAnalysis(target_allocation_shares,
                        funds,
                        analysis_start_date,
                        years,
                        yearlyFrequency,
                        etf_dates,
                        price_history,
                        verbose=False):

    # "Buy" the ETFs with our allocation funds.
    allocated_funds = {}
    for k, v in target_allocation_shares.items():
        allocated_funds[k] = v * funds

    current_date = analysis_start_date
    balancePeriod = 365 // yearlyFrequency
    for i in range(years * yearlyFrequency):
        # Getting current date and 1 year later.
        current_date += balancePeriod
        if verbose == True:
            print(
                f"Current Date: {current_date} {balancePeriod} Days later Date: {current_date + balancePeriod}"
            )
        current_date_idx = findClosestValidDateIndex(current_date, etf_dates)
        year_later_idx = findClosestValidDateIndex(
            current_date + balancePeriod, etf_dates)

        # Get price of each ETF at the dates.
        etf_price_from_later = {}
        etf_price_from_current = {}
        for k, v in price_history.items():
            etf_price_from_current[k] = v[current_date_idx]
            etf_price_from_later[k] = v[year_later_idx]

        # How did `allocated_funds` change after 1 year?
        funds = 0
        for k, v in allocated_funds.items():
            if k != "Cash":
                allocated_funds[k] = (
                    etf_price_from_later[k] /
                    etf_price_from_current[k]) * allocated_funds[k]
            funds += allocated_funds[k]
        if verbose == True:
            for k, v in allocated_funds.items():
                print(
                    f"\t{k}: {allocated_funds[k]:.2f} {allocated_funds[k]/funds*100:.2f}%"
                )
            print(f"\tTotal Funds: {funds:.2f}")
            print('\t' + '-' * 20 + ' Rebalancing ' + '-' * 20)

        # Rebalancing allocated funds
        for k, v in allocated_funds.items():
            allocated_funds[k] = funds * target_allocation_shares[k]
        if verbose == True:
            for k, v in allocated_funds.items():
                print(
                    f"\t{k}: {allocated_funds[k]:.2f} {allocated_funds[k]/funds*100:.2f}%"
                )
            print(f"\tTotal Funds: {funds:.2f}")
            print()

    return allocated_funds


def passiveAnalysis(target_allocation_shares, funds, analysis_start_date,
                    years, etf_dates, price_history):
    allocated_funds = {}
    for k, v in target_allocation_shares.items():
        allocated_funds[k] = v * funds
    current_date_idx = findClosestValidDateIndex(analysis_start_date,
                                                 etf_dates)
    later_date_idx = findClosestValidDateIndex(
        analysis_start_date + years * 365, etf_dates)
    print(analysis_start_date, etf_dates[current_date_idx],
          etf_dates[later_date_idx], current_date_idx, later_date_idx)
    for k in allocated_funds.keys():
        if k != 'Cash':
            growth = price_history[k][later_date_idx] / price_history[k][
                current_date_idx]
            allocated_funds[k] = growth * allocated_funds[k]
            print(growth)

    return allocated_funds


def getPeriodAndTargetAllocations(date_):
    list1 = list(periodStartDates.keys())[:-1]
    list2 = list(periodStartDates.keys())[1:]
    if date_ < list1[0]:
        return periodStartDates[list1[0]], cycleNameToAllocationShares[
            periodStartDates[list1[0]]]
    for periodDate, nextPeriodDate in zip(list1, list2):
        # if date_ >= list2[-1]:
        #     return periodStartDates[-1], cycleNameToAllocationShares[periodStartDates[periodDate]]
        if date_ < nextPeriodDate and date_ >= periodDate:
            return periodStartDates[periodDate], cycleNameToAllocationShares[
                periodStartDates[periodDate]]
    return periodStartDates[list2[-1]], cycleNameToAllocationShares[
        periodStartDates[list2[-1]]]


def rebalanceOnEconomicPeriods(analysis_start_date, rebalance_dates, funds,
                               price_history, etf_dates):
    for i in rebalance_dates:
        print(i)
    print()
    allocated_funds = {}
    # [val1, val2, val3, val4]
    for date_ in rebalance_dates[::-1]:
        if date_ < analysis_start_date:
            rebalance_dates.remove(date_)
    rebalance_dates.insert(0, analysis_start_date)
    for i in rebalance_dates:
        print(i)
    # Any date < analysis start date, delete
    # insert analysis start date in the beginning of the list

    for index in range(len(rebalance_dates)):
        if index == 0:
            period_name, target_allocation_shares = getPeriodAndTargetAllocations(
                rebalance_dates[index])
            for k, v in target_allocation_shares.items():
                allocated_funds[k] = v * funds
        else:
            pre_date_idx = findClosestValidDateIndex(
                rebalance_dates[index - 1], etf_dates)
            current_date_idx = findClosestValidDateIndex(
                rebalance_dates[index], etf_dates)
            etf_price_from_pre = {}
            etf_price_from_current = {}
            for k, v in price_history.items():
                etf_price_from_current[k] = v[current_date_idx]
                etf_price_from_pre[k] = v[pre_date_idx]
            funds = 0
            for k, v in allocated_funds.items():
                if k != "Cash":
                    allocated_funds[k] = (
                        etf_price_from_current[k] /
                        etf_price_from_pre[k]) * allocated_funds[k]
                funds += allocated_funds[k]
            period_name, target_allocation_shares = getPeriodAndTargetAllocations(
                rebalance_dates[index])
            for k, v in allocated_funds.items():
                allocated_funds[k] = funds * target_allocation_shares[k]

    return allocated_funds


ref_date = np.datetime64(datetime.today().strftime('%Y-%m-%d'))
years = 10

dates = generateDatesFromRefDate(ref_date, years)
etf_name_to_id = {
    "S&P500": "0968",
    "TotalStockMarket": "0970",
    "TotalInternationalStock": "3369",
    "RealEstate": "0986",
    "TotalBondMarket": "0928"
}

etf_data = {}
for k, v in etf_name_to_id.items():
    #download_module.downloadHtmlFilesFromVanguard(dates, k, v)
    filenames = glob.glob(f"{k}/*")
    # print(filenames)
    data = load_data_module.loadDataFromHTMLFiles(filenames)
    etf_data[k] = data

download_module.downloadMaterialStock()
material_stock_dict = load_data_module.load_csv("MaterialStock.csv")
etf_data["MaterialStock"] = [
    material_stock_dict['Date'], material_stock_dict['Close']
]

# Print the first and last Date and Value for each of the ETFs.
for k, v in etf_data.items():
    first_date = etf_data[k][0][0]
    first_value = etf_data[k][1][0]
    last_date = etf_data[k][0][-1]
    last_value = etf_data[k][1][-1]
    #print(f"{k}: {first_date}, {first_value} | {last_date}, {last_value}")

#start_date = np.datetime64("2018-01-01")
#plotAllETFsPriceHistory(etf_data, start_date)

##### Rebalancing Strategy #####
funds = 10000
target_allocation_shares = {
    "TotalStockMarket": 0.5,
    "TotalInternationalStock": 0.1,
    "RealEstate": 0.15,
    "TotalBondMarket": 0.2,
    "MaterialStock": 0.0,
    "Cash": 0.05
}

# Create a function to check if the target_allocation_shares sum to 100%.

price_history = {}
for k, v in etf_data.items():
    price_history[k] = v[1]

analysis_start_date = np.datetime64("2011-12-31")
years = 10

result_passive = passiveAnalysis(target_allocation_shares, funds,
                                 analysis_start_date, years,
                                 etf_data['TotalStockMarket'][0],
                                 price_history)

yearlyFrequency = 1
result1 = yearBalanceAnalysis(target_allocation_shares, funds,
                              analysis_start_date, years, yearlyFrequency,
                              etf_data['TotalStockMarket'][0], price_history)
yearlyFrequency = 2
result2 = yearBalanceAnalysis(target_allocation_shares, funds,
                              analysis_start_date, years, yearlyFrequency,
                              etf_data['TotalStockMarket'][0], price_history)
yearlyFrequency = 3
result3 = yearBalanceAnalysis(target_allocation_shares, funds,
                              analysis_start_date, years, yearlyFrequency,
                              etf_data['TotalStockMarket'][0], price_history)

print("Passive Strategy Results: ")
for k, v in result_passive.items():
    print(f"\t{k}: {v:.2f}$")
print(f"\tTotal Money: {sum(result_passive.values()):.2f}$")
print()

print("Result of Rebalancing every year:")
for k, v in result1.items():
    print(f"\t{k}: {v:.2f}$")
print(f"\tTotal Money: {sum(result1.values()):.2f}$")
print()
print("Result of Rebalancing twice every year:")
for k, v in result2.items():
    print(f"\t{k}: {v:.2f}$")
print(f"\tTotal Money: {sum(result2.values()):.2f}$")
print()
print("Result of Rebalancing thrice every year:")
for k, v in result3.items():
    print(f"\t{k}: {v:.2f}$")
print(f"\tTotal Money: {sum(result3.values()):.2f}$")
print()

result4 = rebalanceOnEconomicPeriods(analysis_start_date,
                                     list(periodStartDates.keys()), funds,
                                     price_history,
                                     etf_data['TotalStockMarket'][0])
print("Strategy four:")
for k, v in result4.items():
    print(f"\t{k}: {v:.2f}$")
print(f"\tTotal Money: {sum(result4.values()):.2f}$")
print()

total_funds_from_strategies = [
    sum(result_passive.values()),
    sum(result1.values()),
    sum(result2.values()),
    sum(result3.values()),
    sum(result4.values())
]
strategy_names = [
    'Passive', 'Rebalance 1', 'Rebalance 2', 'Rebalance 3', 'Rebalance E'
]
print(total_funds_from_strategies)

plt.bar(strategy_names, total_funds_from_strategies)
plt.xlabel("Strategies")
plt.ylabel("$")
plt.title("Total Assets after 10 years using different strategies.")
plt.show()
