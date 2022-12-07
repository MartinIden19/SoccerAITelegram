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

bets = pd.read_excel(folder + 'matches_ws.xlsx')
today = datetime.datetime.now()
today = today.replace(hour=7, minute = 0, second=0)
for index, match in bets.iterrows():
    dt = to_datetime(match['Date'],match['Time (MSK)'])
    if (match['WhoScoredPrediction'] == 'No') & (dt > today - datetime.timedelta(days=230)):
        
        print('Getting prediction for ' + match.Teams)
        driver.get(match['Preview Link']) #open
        time.sleep(7)

        while_counter = 0
        while(while_counter < 5):
            while_counter += 1
            soup = BeautifulSoup(driver.page_source, 'html.parser')
            prediction = soup.find('div',attrs={'id' : 'preview-prediction'})
            if prediction is not None:
                home = prediction.find('div',attrs={'class' : 'home'})
                away = prediction.find('div',attrs={'class' : 'away'})
                if (away is not None) and (home is not None):
                    home_score = home.find('span',attrs={'class' : 'predicted-score'}).text
                    away_score = away.find('span',attrs={'class' : 'predicted-score'}).text
                    break
                    
            driver.refresh() #refresh
            time.sleep(7)
            
        bets.loc[index,'WhoScoredHome'] = int(home_score)
        bets.loc[index,'WhoScoredAway'] = int(away_score)
        bets.loc[index,'WhoScoredDifference'] = abs(int(home_score) - int(away_score))
        
        if home_score > away_score:
            bets.loc[index,'WhoScoredPrediction'] = 'Home'
        elif home_score < away_score:
            bets.loc[index,'WhoScoredPrediction'] = 'Away'
        else:
            bets.loc[index,'WhoScoredPrediction'] = 'Draw'

        bets.to_excel(folder + 'matches_ws.xlsx',index=False)

driver.close()

print('End of Script')
reboot = 'reboot'
os.system(reboot)