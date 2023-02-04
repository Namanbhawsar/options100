from apscheduler.schedulers.background import BackgroundScheduler
from .jobs import *

def start():
    print("Schedular Started")
    scheduler = BackgroundScheduler()

    # #test schedules start
    #samco_api_login_and_create_file()
    # #eod_strike_price_save_and_logout()
    # #test schedule ends
    #
    #
    # #BOD Login on businessday
    # #cheduler.add_job(samco_api_login, 'cron', hour="9",minute="13")
    #
    # #fetch nifty every 10 second during trading hours
    #scheduler.add_job(fetch_option_chain ,'cron',hour="*",minute="*",second="0,10,20,30,40,50" ,max_instances=2,args=["NIFTY"])
    #
    # #fetch banknifty every 10 second during trading hours
    #scheduler.add_job(fetch_option_chain,'cron',hour="*",minute="*", second="5,15,25,35,45,55" ,max_instances=2, args=["BANKNIFTY"])
    #
    # #Logout and fetch and save last strike price
    # scheduler.add_job(eod_strike_price_save_and_logout,'cron',hour="15",minute="31")


    #Live Hosting Crons

    '''
    scheduler.add_job(samco_api_login_and_create_file,'cron',hour="9",minute ="13")
    scheduler.add_job(fetch_option_chain, 'cron',hour="9",minute="15-59",second="0,10,20,30,40,50" ,max_instances=2,args=["NIFTY"])
    scheduler.add_job(fetch_option_chain ,'cron',hour="10-14",minute="*",second="0,10,20,30,40,50" ,max_instances=2,args=["NIFTY"])
    scheduler.add_job(fetch_option_chain ,'cron',hour="15",minute="0-30",second="0,10,20,30,40,50" ,max_instances=2,args=["NIFTY"])
    scheduler.add_job(fetch_option_chain, 'cron',hour="9",minute="15-59",second="5,15,25,35,45,55" ,max_instances=2,args=["BANKNIFTY"])
    scheduler.add_job(fetch_option_chain ,'cron',hour="10-14",minute="*",second="5,15,25,35,45,55" ,max_instances=2,args=["BANKNIFTY"])
    scheduler.add_job(fetch_option_chain ,'cron',hour="15",minute="0-30",second="5,15,25,35,45,55" ,max_instances=2,args=["BANKNIFTY"])
    scheduler.add_job(eod_strike_price_save_and_logout,'cron',hour="15",minute="32")
    '''

    #Local Server Crons

    samco_api_login_and_create_file()
    fetch_continious_option_chain()
    scheduler.add_job(samco_api_relogin_and_recreate_file,'cron',hour="9",minute ="13")
    scheduler.start()

