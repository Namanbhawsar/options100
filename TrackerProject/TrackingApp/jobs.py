from datetime import datetime
from .custom.startup import *
import threading



def samco_api_login_and_create_file():
    now = datetime.now()
    print("Job (samco_api_login) started at : " + str(now.hour) + ":" + str(now.minute)+":" + str(now.second))
    connection()
    createBODfiles()
    now = datetime.now()
    print("Job (samco_api_login) Completed at : " + str(now.hour) + ":" + str(now.minute)+":" + str(now.second))

def samco_api_relogin_and_recreate_file():
    now = datetime.now()
    print("Job (samco_api_relogin_and_recreate_file) started at : " + str(now.hour) + ":" + str(now.minute)+":" + str(now.second))
    connection()
    recreateBODfiles()
    now = datetime.now()
    print("Job (samco_api_relogin_and_recreate_file) Completed at : " + str(now.hour) + ":" + str(now.minute)+":" + str(now.second))



def fetch_option_chain(symbol):
    now = datetime.now()
    print("Job (fetch_option_chain + " +symbol + ") started at : " + str(now.hour) + ":" + str(now.minute)+":" + str(now.second))
    get_option_chain(symbol)
    now = datetime.now()
    print("Job (fetch_option_chain + " +symbol + ") Completed at : " + str(now.hour) + ":" + str(now.minute)+":" + str(now.second))



def eod_strike_price_save_and_logout():
    now = datetime.now()
    print("Job (eod_strike_price_save_and_logout) started at : " + str(now.hour) + ":" + str(now.minute)+":" + str(now.second))

    save_last_strike()
    logout()

    now = datetime.now()
    print("Job (eod_strike_price_save_and_logout) Completed at : " + str(now.hour) + ":" + str(now.minute)+":" + str(now.second))



def run():
    now = datetime.now()
    start_time = now.replace(hour=9, minute=15, second=0, microsecond=0)
    end_time = now.replace(hour=15, minute=30, second=0, microsecond=0)

    while True:
        now = datetime.now()
        if(start_time<=now and now <= end_time):
            get_option_chain("NIFTY")
            get_option_chain("BANKNIFTY")
        elif(now > end_time):
            eod_strike_price_save_and_logout()
            break
        else:
            sleep(10)




def fetch_continious_option_chain():
    now = datetime.now()
    print("Job (fetch_continious_option_chain) started at : " + str(now.hour) + ":" + str(now.minute)+":" + str(now.second))
    t1 = threading.Thread(target = run, daemon=True)
    t1.start()   
    now = datetime.now()
    print("Job (fetch_continious_option_chain) Completed at : " + str(now.hour) + ":" + str(now.minute)+":" + str(now.second)) 


  

  