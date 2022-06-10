import requests
from time import sleep
import os
import shutil
import time

def writeHtmlToDisk(filename, html_body):
    with open(filename, "w") as fp:
        fp.write(html_body)

def downloadHtmlFilesFromVanguard(dates, etf_name, etf_id):
    # List containing start and and end tuples representing the dates. One tuple
    # represents one date and has length 3 (month, day, year). 

    #dates = [(9, 7, 2010), (9, 7, 2011), (9, 7, 2012), (9, 7, 2013), (9, 7, 2014), (9, 7, 2015), (9, 7, 2016), (9, 7, 2017), (9, 7, 2018), (9, 7, 2019), (9, 7, 2020), (6, 12, 2021)]
    if(os.path.exists(etf_name)):
        shutil.rmtree(etf_name)
    os.mkdir(etf_name)

    for i in range(0, len(dates)-1):
        start = dates[i]  
        end = dates[i+1] 
        print(f"Downloading HTML from {start} to {end}")
        request_url = "https://personal.vanguard.com/us/funds/tools/"\
                        "pricehistorysearch?radio=1&results=get&FundType="\
                        f"ExchangeTradedShares&FundIntExt=INT&FundId={etf_id}&fundName={etf_id}"\
                        "&radiobutton2=1&"\
                        f"beginDate={start[0]}%2F{start[1]}%2F{start[2]}&"\
                        f"endDate={end[0]}%2F{end[1]}%2F{end[2]}"\
                        "&year=#res"
        print(request_url)
        # Make the request and get the response.
        response = requests.get(request_url)
        # Write to disk. `9-7-2010_9-7-2011`
        #writeHtmlToDisk(f"{etf_name}/filename.html")
        writeHtmlToDisk(f"{etf_name}/{start[0]}-{start[1]}-{start[2]}_{end[0]}-{end[1]}-{end[2]}.html", response.text)
        sleep(0.25)

def downloadMaterialStock():
    period1 = '914284800' # Earliest date is 22nd Dec 1998
    period2 = str(int(time.time()))
    request_url = "https://query1.finance.yahoo.com/v7/finance/download/"\
                  f"XLB?period1={period1}&period2={period2}&interval=1d&"\
                  "events=history&includeAdjustedClose=true"
    print(request_url)
    response = requests.get(request_url, stream=True)

    if response.status_code != 200:
        print("Request was not successful!!!!!!!")
        return

    with open("MaterialStock.csv", "wb") as f:
        response.raw.decode_content = True
        shutil.copyfileobj(response.raw, f)