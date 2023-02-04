import random
import sys
from datetime import datetime, timedelta,time
from snapi_py_client.snapi_bridge import StocknoteAPIPythonBridge
from django.conf import settings
import json
from time import sleep
import pandas as pd
from tabulate import tabulate
import requests
from pathlib import Path
import logging
import os

samco = 0
login = 0
expiry_date= 0
prevData ={'NIFTY':{'previousHighprice':0,'previousLowprice':0,'lowestLTP':sys.maxsize,'initial':0},'BANKNIFTY':{'previousHighprice':0,'previousLowprice':0,'lowestLTP':sys.maxsize,'initial':0}}
curr_strike = {'NIFTY':0,'BANKNIFTY':0}
major_df = ""
today = datetime.now().date()
CURR_PATH = Path(__file__).resolve().parent.parent
prevStrikeData = {'NIFTY':0,'BANKNIFTY':0}
avgData = {'NIFTY':[],'BANKNIFTY':[]}
futData = {'NIFTY':{'MAX':-sys.maxsize,'MIN':sys.maxsize},'BANKNIFTY':{'MAX':-sys.maxsize,'MIN':sys.maxsize}}

def resetOldData():
    samco = 0
    login = 0
    expiry_date= 0
    previousHighprice = previousLowprice = 0
    initial = 0

def lastLine(f):
    f.seek(-150,os.SEEK_END)
    last = f.readlines()[-1]
    return str(last)[2:-5].split(",")




#This function will return list of possible expiries
def getExpiryDates(testDate = None):
    expiryList =[]
    # testDate code start
    if(testDate != None):
        today = testDate
    else:
    #test code ends
        today = datetime.now()
    #print('today :' + str(today.date()))
    nextThursday = today
    while(nextThursday.weekday() != 3):
        nextThursday += timedelta(1)
    if(today.weekday() == 3):
        expiryList = [today ,today + timedelta(7), today + timedelta(6)]
    else:
        expiryList = [nextThursday,nextThursday - timedelta(1)]
    expiryList = [str(i.date()) for i in expiryList]
    return expiryList



#This function will return actual expiry
def getRecentExpiry(samco, testDate = None):
    expiry_dates = getExpiryDates(testDate)
    #print('Recent  Possible expiries = ', *expiry_dates)
    recent_expiry = expiry_dates[0]
    sleep(1)
    chain = samco.get_option_chain(search_symbol_name="BANKNIFTY", exchange=(samco.EXCHANGE_NFO), expiry_date=expiry_dates[0])
    chain = json.loads(chain)
    if(chain['status'] == 'Failure'):
        sleep(1)
        chain = samco.get_option_chain(search_symbol_name="BANKNIFTY", exchange=(samco.EXCHANGE_NFO), expiry_date=expiry_dates[1])
        chain = json.loads(chain)
        recent_expiry = expiry_dates[1]
    if(3 == len(expiry_dates) and chain['status'] == 'Failure'):
        sleep(1)
        chain = samco.get_option_chain(search_symbol_name="BANKNIFTY", exchange=(samco.EXCHANGE_NFO), expiry_date=expiry_dates[2])
        chain = json.loads(chain)
        recent_expiry = expiry_dates[2]
    #print("recent final expiry: " + recent_expiry ,end="\n\n" )
    sleep(2)
    return recent_expiry


#Connection is established and login is done in this function
def connection():
    global samco,login,expiry_date,major_df, prevStrikeData
    if(login == 0):
        print('<---->\nConntecting API')
        samco = StocknoteAPIPythonBridge()
        print('Logging in')
        login = samco.login(body={'userId':'DR39282',  'password':'@RISHIs007',  'yob':'1999'})
        print('Fetching SessionToken')
        login = json.loads(login)

        sessiontoken = login['sessionToken']
        samco.set_session_token(sessionToken=sessiontoken)
        print('Fetching Recent Expiry')
        expiry_date = getRecentExpiry(samco)
        print('recent expiry : ' + expiry_date)
        #fetch previous Data
        try:
            with open('prevdayEODFile.txt','r') as f:
                lines = f.readlines()
                prevStrikeData["NIFTY"] = lines[0].split()[2]
                prevStrikeData["BANKNIFTY"] =lines[1].split()[2]
        except:
            pass


def createBODfiles():
    csvfolder = CURR_PATH.joinpath('csvfiles')
    try:
        csvfile = Path(csvfolder,"NIFTY-"+str(today)+".csv")
        if csvfile.exists():
            pass
        else:
            major_df = pd.DataFrame(pd.DataFrame( columns=['LTT','FUT', 'ATMstrike','PrevClose','LTP','High','Low','NetDecay','CE_COI','PE_COI','CE_Max','PE_Max','CE_MaxStr','PE_MaxStr','SPOT','PrevLTP','AVG']))
            major_df.to_csv(str(CURR_PATH)+r'/csvfiles/'+"NIFTY-"+str(today)+".csv",mode="w",index=False)
            major_df.to_csv(str(CURR_PATH)+r'/csvfiles/'+"BANKNIFTY-"+str(today)+".csv",mode="w",index=False)
    except Exception as e:
        logging.exception(e)
    # print(csvpath.count('/'))
    # print(os.path.exist(csvpath))
    # major_df = pd.DataFrame(pd.DataFrame( columns=['Instrument','LTT','FUT', 'ATMstrike','PrevClose','LTP','High','Low','NetDecay','SPOT','PrevLTP','AVG']))
    # major_df.to_csv(str(CURR_PATH)+r'/csvfiles/'+"NIFTY-"+str(today)+".csv",mode="w",index=False)
    # major_df.to_csv(str(CURR_PATH)+r'/csvfiles/'+"BANKNIFTY-"+str(today)+".csv",mode="w",index=False)
    # print('<---->')

def recreateBODfiles():
    major_df = pd.DataFrame(pd.DataFrame( columns=['LTT','FUT', 'ATMstrike','PrevClose','LTP','High','Low','NetDecay','CE_COI','PE_COI','CE_Max','PE_Max','CE_MaxStr','PE_MaxStr','SPOT','PrevLTP','AVG']))
    major_df.to_csv(str(CURR_PATH)+r'/csvfiles/'+"NIFTY-"+str(today)+".csv",mode="w",index=False)
    major_df.to_csv(str(CURR_PATH)+r'/csvfiles/'+"BANKNIFTY-"+str(today)+".csv",mode="w",index=False)    




def myround(x, symbol):
    if symbol == "NIFTY":
        base = 50
    else:
        base = 100
    return int(base * round(float(x) / base))

def cal_nearest_expiry(x,symbol):
    if symbol == "NIFTY":
        base = 50
    else:
        base = 100

    if(curr_strike[symbol] == 0):
        curr_strike[symbol] = myround(x,symbol)
    else:
        if(curr_strike[symbol] - x >= base):
            curr_strike[symbol] -= base
        
        elif(x - curr_strike[symbol] >= base):
            curr_strike[symbol] += base
    return curr_strike[symbol]


def FuturesSymbol(symbol,expiry_date):
    expiry_date = datetime.strptime(expiry_date,"%Y-%m-%d")
    fut_symbol = symbol + expiry_date.strftime('%y%b').upper() + 'FUT'
    return fut_symbol

def get_option_chain(symbol):
    if (symbol == 'NIFTY'):
        return
    global prevData,login,prevStrikeData
    start_time = datetime.now()
    try:
        #CUSOTM
        '''
        print('test')
        chain = samco.get_option_chain(search_symbol_name="NIFTY", exchange=(samco.EXCHANGE_NFO), expiry_date=expiry_date)
        chain = json.loads(chain)
        tempdf = pd.DataFrame(chain['optionChainDetails'])
        call_oi_change_sum = 0
        put_oi_change_sum = 0
        put_oi_max = 0
        call_oi_max = 0
        put_oi_max_strike = ""
        call_oi_max_strike = ""
        for i in tempdf.index:
            if(tempdf['tradingSymbol'][i][-2:] == 'CE'):
                val = int(tempdf['openInterestChange'][i])
                if (val > call_oi_max):
                    call_oi_max = val
                    call_oi_max_strike = tempdf['strikePrice'][i]
                call_oi_change_sum += val
            else:
                val = int(tempdf['openInterestChange'][i])
                if (val > put_oi_max):
                    put_oi_max = val
                    put_oi_max_strike = tempdf['strikePrice'][i]
                put_oi_change_sum += val

        print ("call Totlal = " ,f"{call_oi_change_sum:,}")
        print("put Total = ", f"{put_oi_change_sum:,}")

        print('call max oi=',f"{call_oi_max:,}", '   on strike = ',f"{int(call_oi_max_strike[:-3]):,}" )
        print('put max oi=',f"{put_oi_max:,}", '   on strike = ', f"{int(put_oi_max_strike[:-3]):,}")
                

        print(tempdf)
        '''


        #CUSTOM END
        now = datetime.now()
        prevstrikechain = samco.get_option_chain(search_symbol_name=symbol, exchange=samco.EXCHANGE_NFO, expiry_date=expiry_date,strike_price=prevStrikeData[symbol])
        prevstrikechain = json.loads(prevstrikechain)
        prevStrikeLTP = 0
        while True:
            try:
                tempdf = pd.DataFrame(prevstrikechain['optionChainDetails'])
                tempdf.lastTradedPrice = tempdf.lastTradedPrice.astype(float)
                prevStrikeLTP = tempdf.lastTradedPrice.sum()
                break
            except Exception as e:
                print(prevstrikechain)
                print("Exception occured at prevstrikefetch")
                logging.exception(e)              
                continue
        sleep(1.5)
        chain = samco.get_option_chain(search_symbol_name=symbol, exchange=(samco.EXCHANGE_NFO), expiry_date=expiry_date)
        chain = json.loads(chain)
        while True:
            try:
                df = pd.DataFrame(chain['optionChainDetails'])
                break
            except Exception as e:
                print(chain)
                print("Exception occured at strikefetch")
                logging.exception(e)                
                continue
        df.strikePrice = df.strikePrice.astype(float).astype(int)

        #OI CHANGE CUSTOMISATION START
        df.openInterestChange = df.openInterestChange.astype(str).astype(int)
        call_oic_sum = 0
        put_oic_sum = 0
        put_oic_max = 0
        call_oic_max = 0
        put_oic_max_strike = 0
        call_oic_max_strike = 0

        for i in df.index:
            if(df['optionType'][i] == 'CE'):
                val = df['openInterestChange'][i]
                if(val > call_oic_max):
                    call_oic_max = val
                    call_oic_max_strike = df['strikePrice'][i]
                call_oic_sum +=val
            else:
                val = df['openInterestChange'][i]
                if(val > put_oic_max):
                    put_oic_max = val
                    put_oic_max_strike = df['strikePrice'][i]
                put_oic_sum +=val

        #OI CHANGE CUSTOMISATION ENDS

        df.lastTradedPrice = df.lastTradedPrice.astype(float)
        ltt = datetime.now().strftime('%H:%M:%S')
        sessiontoken = login['sessionToken']
        headers = {
            'Accept': 'application/json',
            'x-session-token': sessiontoken
        }
        indexSymbol = {'NIFTY':'NIFTY 50','BANKNIFTY':'NIFTY BANK'}
        while True:
            try:                
                r = requests.get('https://api.stocknote.com/quote/indexQuote', params={
                  'indexName': indexSymbol[symbol]
                }, headers = headers)
                spot_price = r.json()['spotPrice']
                fut_symbol = FuturesSymbol(symbol,expiry_date)
                break
            except:
                continue
        while True:
            try:
                fut_price = int(float(json.loads(samco.get_quote(symbol_name=fut_symbol, exchange=(samco.EXCHANGE_NFO)))['lastTradedPrice']))
                PrevClose_fut_price = int(float(json.loads(samco.get_quote(symbol_name=fut_symbol, exchange=(samco.EXCHANGE_NFO)))['previousClose']))
                fut_high = int(float(json.loads(samco.get_quote(symbol_name=fut_symbol, exchange=(samco.EXCHANGE_NFO)))['highValue']))
                fut_low = int(float(json.loads(samco.get_quote(symbol_name=fut_symbol, exchange=(samco.EXCHANGE_NFO)))['lowValue']))
                break
            except Exception as e:
                continue
        nearest_expiry_price = cal_nearest_expiry(fut_price,symbol)
        expiry_df = df.loc[(df['strikePrice'] == nearest_expiry_price)].reset_index(drop=True)
        expiry_df.lastTradedPrice = expiry_df.lastTradedPrice.astype(float)
        ltp = expiry_df.lastTradedPrice.sum()
        nearest_Highexpiry_price = myround(fut_high,symbol)

        expiry_Highdf = df.loc[(df['strikePrice'] == nearest_Highexpiry_price)].reset_index(drop=True)
        expiry_Highdf = expiry_Highdf.sort_values('tradingSymbol')
        highCE_symbol = expiry_Highdf.iloc[(0, 0)]
        highPE_symbol = expiry_Highdf.iloc[(1, 0)]
        while True:
            try:
                highCEdata = samco.get_quote(symbol_name=highCE_symbol, exchange=(samco.EXCHANGE_NFO))
                highPEdata = samco.get_quote(symbol_name=highPE_symbol, exchange=(samco.EXCHANGE_NFO))
                combinedHighPrice = float(json.loads(highCEdata)['highValue']) + float(json.loads(highPEdata)['lowValue'])
                break
            except:
                continue
        nearest_Lowexpiry_price = myround(fut_low,symbol)
        expiry_Lowdf = df.loc[(df['strikePrice'] == nearest_Lowexpiry_price)].reset_index(drop=True)
        expiry_Lowdf = expiry_Lowdf.sort_values('tradingSymbol')
        lowCE_symbol = expiry_Lowdf.iloc[(0, 0)]
        lowPE_symbol = expiry_Lowdf.iloc[(1, 0)]
        while True:
            try:
                lowCEdata = samco.get_quote(symbol_name=lowCE_symbol, exchange=(samco.EXCHANGE_NFO))
                lowPEdata = samco.get_quote(symbol_name=lowPE_symbol, exchange=(samco.EXCHANGE_NFO))
                combinedLowPrice = float(json.loads(lowCEdata)['lowValue']) + float(json.loads(lowPEdata)['highValue'])
                break
            except:
                continue
        nearest_Previousexpiry_price = myround(PrevClose_fut_price,symbol)
        expiry_Previousdf = df.loc[(df['strikePrice'] == nearest_Previousexpiry_price)].reset_index(drop=True)
        expiry_Previousdf = expiry_Previousdf.sort_values('tradingSymbol')
        previousCE_symbol = expiry_Previousdf.iloc[(0, 0)]
        previousPE_symbol = expiry_Previousdf.iloc[(1, 0)]
        while True:
            try:
                previousCEdata = samco.get_quote(symbol_name=previousCE_symbol, exchange=(samco.EXCHANGE_NFO))
                previousPEdata = samco.get_quote(symbol_name=previousPE_symbol, exchange=(samco.EXCHANGE_NFO))
                combinedPreviousPrice = float(json.loads(previousCEdata)['previousClose']) + float(json.loads(previousPEdata)['previousClose'])
                break
            except:
                continue
        Net_change = ltp - combinedPreviousPrice

        if(fut_price > futData[symbol]['MAX']):
            futData[symbol]['MAX'] = fut_price
        if(fut_price < futData[symbol]['MIN']):
            futData[symbol]['MIN'] = fut_price



        #alerts
        chatId = {'NIFTY': "-534029950", 'BANKNIFTY': "-568257794" }
        try:
            if prevData[symbol]['initial'] != 0:

                if(ltp > combinedHighPrice and ( abs(futData[symbol]['MAX'] - fut_price)  <=  abs(fut_price - futData[symbol]['MIN'] ))):
                    requests.get('https://api.telegram.org/bot1882602773:AAHjJqx2KuNIhl-y9ks4p3HU8_i60Bes-UQ/sendMessage?chat_id=' + chatId[symbol] + '&parse_mode=Markdown&text= 🔺 [' + symbol + '] \nLTP greater than HIGH\n' + ltt).json()

                if(ltp > combinedLowPrice and ( abs(futData[symbol]['MAX'] - fut_price)  >  abs(fut_price - futData[symbol]['MIN'] ))):
                    requests.get('https://api.telegram.org/bot1882602773:AAHjJqx2KuNIhl-y9ks4p3HU8_i60Bes-UQ/sendMessage?chat_id=' + chatId[symbol] + '&parse_mode=Markdown&text= 🔻 [' + symbol + ']\nLTP greater than LOW\n' + ltt).json()

                if combinedHighPrice > prevData[symbol]['previousHighprice']:
                    requests.get('https://api.telegram.org/bot1882602773:AAHjJqx2KuNIhl-y9ks4p3HU8_i60Bes-UQ/sendMessage?chat_id=' + chatId[symbol] + '&parse_mode=Markdown&text= 🔺 [' + symbol + ']\nHIGH broken HIGH at\n' + ltt).json()

                if combinedLowPrice > prevData[symbol]['previousLowprice']:
                    requests.get('https://api.telegram.org/bot1882602773:AAHjJqx2KuNIhl-y9ks4p3HU8_i60Bes-UQ/sendMessage?chat_id=' + chatId[symbol] + '&parse_mode=Markdown&text= 🔻 [' + symbol + ']\nLOW broken LOW at\n' + ltt).json()

            else:
                prevData[symbol]['lowestLTP'] = ltp
                prevData[symbol]['initial'] = 1

            prevData[symbol]['previousHighprice'] = combinedHighPrice
            prevData[symbol]['previousLowprice'] = combinedLowPrice

            movingAVG = 0
            # AVG code
            if(len(avgData[symbol]) < 300):
                avgData[symbol].append(round(ltp,2))
                movingAVG = sum(avgData[symbol])/len(avgData[symbol])
            else:
                avgData[symbol].pop(0)
                avgData[symbol].append(round(ltp,2))
                movingAVG = sum(avgData[symbol])/len(avgData[symbol])

            row_dict = {'LTT':ltt,
                        'FUT':fut_price,
                        'ATMstrike':nearest_expiry_price,
                        'PrevClose':round(combinedPreviousPrice,2),
                        'LTP':round(ltp,2),
                        'High':round(combinedHighPrice,2),
                        'Low':round(combinedLowPrice,2),
                        'NetDecay':round(float(Net_change),2),
                        'CE_COI':call_oic_sum,
                        'PE_COI':put_oic_sum,
                        'CE_Max':call_oic_max,
                        'PE_Max':put_oic_max,
                        'CE_MaxStr':call_oic_max_strike,
                        'PE_MaxStr':put_oic_max_strike,
                        'SPOT':round(float(spot_price)),
                        'PrevLTP':round(float(prevStrikeLTP)),
                        'AVG':round(movingAVG,2)}

            mini_df = pd.DataFrame([row_dict])
            print(tabulate(mini_df, headers='keys', tablefmt='psql'))
            mini_df.to_csv(str(CURR_PATH)+r'/csvfiles/'+symbol+"-" + str(today)+".csv", mode = 'a', header = False,index=False)
        except:
            return

    except Exception as e:
        #print("Exception occured: " +str(e))
        logging.exception(e)
        return



def save_last_strike():
    today = datetime.now().date()
    content = ""
    with open(str(CURR_PATH)+r'/csvfiles/NIFTY-' + str(today)+".csv",'rb') as f:
        last = lastLine(f)
        content += "NIFTY " + last[0] + " " + last[2]+"\n"
    print("NIFTY ",last)
    with open(str(CURR_PATH)+r'/csvfiles/BANKNIFTY-' + str(today)+".csv",'rb') as f:
        last = lastLine(f)
        content += "BANKNIFTY " + last[0] + " " + last[2]
    print("BANKNIFTY ",last)
    with open('prevdayEODFile.txt','w') as f:
        f.write(content)
    print("Last strike noted")



def logout():
    global samco
    response =  samco.logout()
    print(json.loads(response)['statusMessage'])



def customFuctionSpotPrice():
    print('<---->\nConntecting API')
    samco = StocknoteAPIPythonBridge()
    print('Logging in')
    login = samco.login(body={'userId':'DR39282',  'password':'@RISHIs007',  'yob':'1999'})
    print('Fetching SessionToken')
    login = json.loads(login)
    sessiontoken = login['sessionToken']
    headers = {
      'Accept': 'application/json',
      'x-session-token': sessiontoken
    }
    r = requests.get('https://api.stocknote.com/quote/indexQuote', params={
      'indexName': 'NIFTY 50'
        #'indexName': 'NIFTY BANK'
    }, headers = headers)

    print (r.json()['spotPrice'])



def customPreviousStrikePrice():
    connection()
    global previousHighprice,previousLowprice,initial
    try:
        now = datetime.now()
        prevdate = now - timedelta(3)
        prevdate = prevdate.strftime('%Y-%m-%d')
        historicdata = samco.get_index_candle_data(index_name='NIFTY 50', from_date=prevdate)
        #chain = samco.get_option_chain(search_symbol_name="NIFTY", exchange=(samco.EXCHANGE_NFO), expiry_date=expiry_date,strike_price="14700")
        #chain = json.loads(chain)
        #print(chain)

        print(json.loads(historicdata)['indexCandleData'][-2]['date'])
    except Exception as e :
        logging.exception(e)
    #     while True:
    #         try:
    #             df = pd.DataFrame(chain['optionChainDetails'])
    #             break
    #         except:
    #             continue
    #
    #     print(df)
    # except Exception as e:
    #     logging.exception(e)


# connection()
# save_last_strike()
# logout()

# def read():
#     with open('prevdayEODile.txt','r') as f:
#         for line in f.readlines():
#             print(line.split()[2])
#
# read()
