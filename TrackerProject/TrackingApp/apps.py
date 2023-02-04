from django.apps import AppConfig
import os

class TrackingappConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'TrackingApp'
    currentThread = ""

    def ready(self):
        from pathlib import Path
        from . import Scheduler
        import threading
        CURR_PATH = Path(__file__).resolve().parent
        var =""
        lck = threading.Lock()
        lck.acquire()
        with open(os.path.join(CURR_PATH, 'val.txt'), mode="r+") as file:
            var = str(file.read()).strip()
            file.truncate(0)
            file.seek(0)
            if("False" == var):
                file.write("True")
            elif("True" == var):
                file.write("False")
            file.close()
        lck.release()
        #For live server
        '''
        if(var == "True"):
            from . import Scheduler
            Scheduler.start()
        '''
        #for local server
        if(var == "True"):
            from . import jobs
            jobs.samco_api_login_and_create_file()
            jobs.fetch_continious_option_chain()



        
