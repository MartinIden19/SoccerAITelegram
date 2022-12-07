from selenium import webdriver
from selenium.webdriver.support.ui import Select
from bs4 import BeautifulSoup 
import pandas as pd
import numpy as np
import os
import time
from src.config import whoscored_url, top_facts_url, folder


os.environ['MOZ_HEADLESS'] = '1'
import warnings
warnings.filterwarnings('ignore')

def GetCountry(url):
    driver = webdriver.Firefox(executable_path = folder + '/geckodriver',service_log_path = folder + 'geckodriver.log')
    driver.get(url)
    soup_c = BeautifulSoup(driver.page_source, 'html.parser')
    driver.close()
    bc = soup_c.find('div',attrs={'id':'breadcrumb-nav'})
    country = bc.find('span',attrs={'class':'iconize iconize-icon-left'}).text
    return country

def WhoScoredTopFacts():
    driver = webdriver.Firefox(executable_path = folder + '/geckodriver',service_log_path = folder + 'geckodriver.log')
    driver.get(top_facts_url)
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    table = soup.find('div',attrs={'class':'matchFacts'})
    facts = table.find_all('div',attrs={'class':'fact'})
    ws_top = pd.DataFrame(columns=('Type','Text','Link','Country','Prediction','Odds','Pos','Pred','Result'))
    fact_type = 'Match Result'
    for fact in facts:
        odds = fact.find('span',attrs={'class':'odds-numeric'}).text
        if odds == 'undefined':
            continue
        fact_text = fact.find('div',attrs={'class':'factText'}).text
        match_link = whoscored_url + fact.find('a',attrs={'class':'matchLink'})['href']
        country = GetCountry(match_link)
        prediction = fact.find('a',attrs={'class':'factBetWrapper'}).text.replace(odds,'').lower()
        pos = prediction.replace('win','')
        pos = pos.replace('draw','')
        pos = pos.replace('lose','').strip()
        result = prediction.replace(pos,'').strip()
        ws_top.loc[len(ws_top)] = [fact_type, fact_text, match_link, country, prediction, float(odds), pos, result, np.nan]
    return ws_top

def WhoScoredTopFactsGoals():
    driver = webdriver.Firefox(executable_path = folder + '/geckodriver',service_log_path = folder + 'geckodriver.log')
    driver.get(top_facts_url)
    select = Select(driver.find_element_by_class_name('filter-drop'))
    select.select_by_visible_text('Goals Over/Under')
    time.sleep(5)
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    table = soup.find('div',attrs={'class':'matchFacts'})
    facts = table.find_all('div',attrs={'class':'fact'})
    ws_top = pd.DataFrame(columns=('Type','Text','Link','Country','Prediction','Odds','Pos','Pred','Result'))
    fact_type = 'Total Goals'
    for fact in facts:
        odds = fact.find('span',attrs={'class':'odds-numeric'}).text
        if odds == 'undefined':
            continue
        fact_text = fact.find('div',attrs={'class':'factText'}).text
        match_link = whoscored_url + fact.find('a',attrs={'class':'matchLink'})['href']
        country = GetCountry(match_link)
        prediction = fact.find('a',attrs={'class':'factBetWrapper'}).text.replace(odds,'').lower()
        result = prediction.replace('goals','').strip()
        #pos = result.replace('Under','')
        pos = pos.replace('under','')
        pos = pos.replace('over','').strip()
        #pos = pos.replace('Over','')
        result = result.replace(pos,'').strip()
        ws_top.loc[len(ws_top)] = [fact_type, fact_text, match_link, country, prediction, float(odds), float(pos), result, np.nan]
    return ws_top
    
def WhoScoredTopFactsDoubleChance():
    driver = webdriver.Firefox(executable_path = folder + '/geckodriver',service_log_path = folder + 'geckodriver.log')
    driver.get(top_facts_url)
    select = Select(driver.find_element_by_class_name('filter-drop'))
    select.select_by_visible_text('Double Chance')
    time.sleep(5)
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    table = soup.find('div',attrs={'class':'matchFacts'})
    facts = table.find_all('div',attrs={'class':'fact'})
    ws_top = pd.DataFrame(columns=('Type','Text','Link','Country','Prediction','Odds','Pos','Pred','Result'))
    fact_type = 'Double Chance'
    for fact in facts:
        odds = fact.find('span',attrs={'class':'odds-numeric'}).text
        if odds == 'undefined':
            continue
        fact_text = fact.find('div',attrs={'class':'factText'}).text
        match_link = whoscored_url + fact.find('a',attrs={'class':'matchLink'})['href']
        country = GetCountry(match_link)
        prediction = fact.find('a',attrs={'class':'factBetWrapper'}).text.replace(odds,'').lower()
        pos = prediction.replace('win or lose','')
        pos = pos.replace('lose or win','')
        pos = pos.replace('win or draw','')
        pos = pos.replace('lose or draw','')
        pos = pos.replace('draw or win','')
        pos = pos.replace('draw or lose','').strip()
        result = prediction.replace(pos,'').strip()
        ws_top.loc[len(ws_top)] = [fact_type, fact_text, match_link, country, prediction, float(odds),pos, result, np.nan]
    return ws_top

def TodayFacts():
    ws_top_mr = WhoScoredTopFacts()
    ws_top_goals = WhoScoredTopFactsGoals()
    ws_top_dc = WhoScoredTopFactsDoubleChance()
    ws_top = pd.concat([ws_top_mr, ws_top_goals], ignore_index=True)
    ws_top = pd.concat([ws_top, ws_top_dc], ignore_index=True)
    ws_new = pd.DataFrame(columns=ws_top.columns)
    recomend = pd.read_excel(folder + 'data/ws_top.xlsx')
    for index, fact in ws_top.iterrows():
        if recomend[(recomend['Link'] == fact['Link']) & (recomend['Prediction'] == fact['Prediction'])].empty:
            ws_new.loc[len(ws_new)] = fact
    recomend = pd.concat([ws_new, recomend], ignore_index=True)
    ws_top.to_excel(folder + 'data/lastdaytop.xlsx',index=False)
    recomend.to_excel(folder + 'data/ws_top.xlsx',index=False)

def ParseResult(fact):
    driver = webdriver.Firefox(executable_path = folder + '/geckodriver',service_log_path = folder + 'geckodriver.log')
    driver.get(fact.Link)
    while(True):
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        header = soup.find('div',attrs={'id' : 'match-header'})
        if header is not None:
            break
        driver.refresh()
    driver.close()
    result = header.find('span',attrs={'class' : 'result'}).text
        
    if result == 'vs':
        fact.Result = 'Returned'
        return fact

    result = result.replace(':',' ')
    result = result.replace('*','')
    result = result.split()

    home_team = header.find('span',attrs={'class' : 'home'}).text
    away_team = header.find('span',attrs={'class' : 'away'}).text
    home_goals, away_goals = float(result[0]), float(result[1])
    total = home_goals + away_goals

    if home_goals > away_goals:
        match_result = 'Home'
    elif home_goals < away_goals:
        match_result = 'Away'
    else:
        match_result = 'Draw'

    if fact.Type == 'Match Result':
        if (fact.Pos == home_team) & (fact.Pred == 'win') & (match_result == 'Home'):
            fact.Result = 'Win'
        elif (fact.Pos == home_team) & (fact.Pred == 'lose') & (match_result == 'Away'):
            fact.Result = 'Win'
        elif (fact.Pos == away_team) & (fact.Pred == 'win') & (match_result == 'Away'):
            fact.Result = 'Win'
        elif (fact.Pos == away_team) & (fact.Pred == 'lose') & (match_result == 'Home'):
            fact.Result = 'Win'
        elif (fact.Pred == 'draw') & (match_result == 'Draw'):
            fact.Result = 'Win'
        else:
            fact.Result = 'Lose'

    elif fact.Type == 'Double Chance':
        if (fact.Pos == home_team) & (fact.Pred == 'win or draw') & ((match_result == 'Home') | (match_result == 'Draw')):
            fact.Result = 'Win'
        elif (fact.Pos == home_team) & (fact.Pred == 'lose or draw') & ((match_result == 'Away') | (match_result == 'Draw')):
            fact.Result = 'Win'
        elif (fact.Pos == away_team) & (fact.Pred == 'win or draw') & ((match_result == 'Away') | (match_result == 'Draw')):
            fact.Result = 'Win'
        elif (fact.Pos == away_team) & (fact.Pred == 'lose or draw') & ((match_result == 'Home') | (match_result == 'Draw')):
            fact.Result = 'Win'
        else:
            fact.Result = 'Lose'

    elif fact.Type == 'Total Goals':
        if (total < float(fact.Pos)) & (fact.Pred == 'Under'):
            fact.Result = 'Win'
        elif (total > float(fact.Pos)) & (fact.Pred == 'Over'):
            fact.Result = 'Win'
        elif  total == float(fact.Pos):
            fact.Result = 'Returned'
        else:
            fact.Result = 'Lose'

    return fact

def WhoScoredResults(data):
    for index, fact in data.iterrows():
        fact = ParseResult(fact)
        data.loc[index] = fact
    return data