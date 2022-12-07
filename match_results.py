import os
import pandas as pd
import datetime
import time
from selenium import webdriver
from bs4 import BeautifulSoup 
from src.config import folder
from src.functions import to_datetime

import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning) 

os.environ['MOZ_HEADLESS'] = '1'

driver = webdriver.Firefox(executable_path = folder + 'geckodriver',service_log_path = folder + 'geckodriver.log')

bets = pd.read_excel(folder + 'data/matches.xlsx')
today = datetime.datetime.now()
today = today.replace(hour=7, minute = 0, second=0)
for index, match in bets.iterrows():
    dt = to_datetime(match['Date'],match['Time (MSK)'])
    if (match['Result'] == 'Returned') & (dt > today - datetime.timedelta(days=230)):
        try:
            print('Getting result for ' + match.Teams)
            driver.get(match['Preview Link']) #open
            time.sleep(7)

            while_counter = 0
            while(while_counter < 5):
                while_counter += 1
                soup = BeautifulSoup(driver.page_source, 'html.parser')
                header = soup.find('div',attrs={'id' : 'match-header'})
                if header is not None:
                    result = header.find('span',attrs={'class' : 'result'})
                    if result is not None:
                        result = result.text
                        break
                driver.refresh() #refresh
                time.sleep(7)
                
            if result == 'vs':
                bets.loc[index,'Result'] = 'Returned'

            result = result.replace(':',' ')
            result = result.replace('*','')
            result = result.split()

            home_goals, away_goals = float(result[0]), float(result[1])

            if home_goals > away_goals:
                bets.loc[index,'Result'] = 'Home'
            elif home_goals < away_goals:
                bets.loc[index,'Result'] = 'Away'
            else:
                bets.loc[index,'Result'] = 'Draw'

            bets.to_excel(folder + 'data/matches.xlsx',index=False)
        except:
            pass

driver.close()

print('End of Script')
reboot = 'reboot'
os.system(reboot)