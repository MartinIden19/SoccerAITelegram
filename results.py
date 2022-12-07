from src.parse_results import PreviousBets, BetEfficiencyRU
from src.post_ru import SendMessage
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

bets = pd.read_excel(folder + 'data/bets.xlsx')
today = datetime.datetime.now()
today = today.replace(hour=7, minute = 0, second=0)
for index, match in bets.iterrows():
    dt = to_datetime(match['Date'],match['Time (MSK)'])
    if (match['Result'] == 'Returned') & (dt > today - datetime.timedelta(days=2)):
        try:
            driver.get(match['Preview Link']) #open
            time.sleep(7)

            while_counter = 0
            while(while_counter < 5):
                while_counter += 1
                soup = BeautifulSoup(driver.page_source, 'html.parser')
                header = soup.find('div',attrs={'id' : 'match-header'})
                if header is not None:
                    result = header.find('span',attrs={'class' : 'result'})
                    status = header.find('dd',attrs={'class' : 'status'})
                    if (result is not None) & (status is not None):
                        result = result.text
                        status = status.text
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

            if status != 'FT':
                bets.loc[index,'Result'] = 'Returned'

            print('Get result for ' + match.Teams)
        except:
            pass

bets.to_excel(folder + 'data/bets.xlsx',index=False)

driver.close()

prev_bets = PreviousBets()
if not prev_bets.empty:
    BetEfficiencyRU(prev_bets)
print('End of Script')
reboot = 'reboot'
os.system(reboot)