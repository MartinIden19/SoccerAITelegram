import pandas as pd
import os
import numpy as np
from bs4 import BeautifulSoup 
from selenium import webdriver
import datetime
import time

from src.post_ru import SendMessage, MatchDayResumeRU, MatchDayBets

from src.functions import FindNewMatches, to_datetime, GetPrediction, PlayersTable, TeamsURL, TeamMeanGoals, TeamPoints, TeamLastMatches, GetOdds

from src.dictionaries import no_matches, Winline_Teams
from src.config import msk_delta, whoscored_url, preview_url, winline_url, folder

import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning) 

os.environ['MOZ_HEADLESS'] = '1'

driver = webdriver.Firefox(executable_path = folder + 'geckodriver' ,service_log_path = folder + 'geckodriver.log')

driver.get(preview_url) #open
time.sleep(10)
soup = BeautifulSoup(driver.page_source, 'html.parser')
previews_table = soup.find('div', attrs={'class':'previews'}).find('tbody')
#driver.close() #close
if previews_table is None:
    print(no_matches)
    preview_data = None
else:
    rows = previews_table.find_all('tr')
    date, tournament, country = None, None, None
    preview_data = pd.DataFrame(columns=('Date','Country','Tournament','Time (MSK)','Teams','Preview Link'))
    for row in rows:
        if row.find('td', attrs={'class':'previews-date'}) is not None:
            date = row.find('td', attrs={'class':'previews-date'}).text.strip().split(',')[0]
        if row.find('span', attrs={'class':'country'}) is not None:
            country = row.find('span', attrs={'class':'country'})['title']
        if row.find('a', attrs={'class':'level-2'}) is not None:
            tournament = row.find('a', attrs={'class':'level-2'}).text.strip()

        if row.find('td', attrs={'class':'time'}) is not None:
            match_time = row.find('td', attrs={'class':'time'}).text.strip()
            teams = row.find('a').text.strip()
            preview_href = row.find('a')['href']
            dt = to_datetime(date, match_time) + datetime.timedelta(hours=msk_delta)
            date1 = dt.strftime("%d-%m-%Y")
            time1 = dt.strftime("%H:%M")
            preview_data.loc[len(preview_data)] = [date1, country, tournament, time1, teams, whoscored_url + preview_href]

new_matches = FindNewMatches(preview_data)

try:
    #SendMessage(str(new_matches))
    print(new_matches)
except:
    pass

if not new_matches.empty:
    predicted_matches = pd.DataFrame(columns=('Date', 'Country', 'Tournament', 'Time (MSK)', 'Teams', 'Preview Link',
        'HomeTeam','AwayTeam','HomeHref','AwayHref','HTRating','ATRating','HTAR','ATAR','HTMR','ATMR','HTDR','ATDR',
        'HTMGS','ATMGS','HTMGC','ATMGC','HTPoints3','HTPoints5','ATPoints3','ATPoints5','HTMatches','ATMatches','HTLastMatches','ATLastMatches',
        'AvgCH','AvgCD','AvgCA','DoubleChanceHD','DoubleChanceHA','DoubleChanceAD','HomeProb','DrawProb','AwayProb','HD_Prob','HA_Prob','AD_Prob','Result'))

    best_bets = pd.DataFrame(columns=('Date', 'Country', 'Tournament', 'Time (MSK)', 'Teams', 'Preview Link',
        'HomeTeam','AwayTeam','HomeHref','AwayHref','HTRating','ATRating','HTAR','ATAR','HTMR','ATMR','HTDR','ATDR',
        'HTMGS','ATMGS','HTMGC','ATMGC','HTPoints3','HTPoints5','ATPoints3','ATPoints5','HTMatches','ATMatches','HTLastMatches','ATLastMatches',
        'AvgCH','AvgCD','AvgCA','DoubleChanceHD','DoubleChanceHA','DoubleChanceAD','HomeProb','DrawProb','AwayProb','HD_Prob','HA_Prob','AD_Prob','Result','Prediction')) 

    for index, match_prev in new_matches.iterrows():
        main_flag = True
        main_counter = 0
        while((main_flag) & (main_counter < 3)):
            time.sleep(5)
            main_counter+=1
            try:
                
                url = match_prev['Preview Link']
                driver.get(url) #open
                time.sleep(3)

                while_counter = 0

                while(while_counter < 3):
                    while_counter += 1
                    soup = BeautifulSoup(driver.page_source, 'html.parser')
                    info = soup.find('div', attrs={'class':'teams-score-info'})
                    if info is not None:
                        break
                    driver.refresh() #refresh
                    time.sleep(3)
                    
                #driver.close() #close

                match = pd.DataFrame(columns=('HomeTeam','AwayTeam','HomeHref','AwayHref','HTRating','ATRating','HTAR','ATAR','HTMR','ATMR',
                'HTDR','ATDR','HTMGS','ATMGS','HTMGC','ATMGC','HTPoints3','HTPoints5','ATPoints3','ATPoints5','HTMatches','ATMatches','HTLastMatches','ATLastMatches'))
                
                home_info = info.find('span', attrs={'class':'home'}).find('a',attrs={'class':'team-link'})
                away_info = info.find('span', attrs={'class':'away'}).find('a',attrs={'class':'team-link'})
                home_name = home_info.text
                away_name = away_info.text
                home_href = whoscored_url + home_info['href']
                away_href = whoscored_url + away_info['href']

                odds = pd.DataFrame(columns=('AvgCH','AvgCD','AvgCA','DoubleChanceHD','DoubleChanceHA','DoubleChanceAD'))
                odds.loc[0] = [0, 0, 0, 0, 0, 0]

                home_name_ru = home_name
                away_name_ru = away_name
                
                for key in Winline_Teams.keys():
                    if home_name_ru == key:
                        home_name_ru = Winline_Teams[key]
                    if away_name_ru == key:
                        away_name_ru = Winline_Teams[key]

                
                winline_flag = True
                winline_counter = 0
                while((winline_flag) & (winline_counter < 3)):
                    time.sleep(5)
                    winline_counter+=1
                    try:

                        driver.get(winline_url) #open
                        time.sleep(3)
                        search = driver.find_element(by='name', value = 'searchForm.find')
                        search.send_keys(home_name_ru + ' ' + away_name_ru)
                        time.sleep(3)
                        match_bet = driver.find_element(by='class name', value = 'commands')
                        match_bet.click() #go to match page
                        time.sleep(3)

                        while_counter = 0

                        while(while_counter < 3):
                            while_counter += 1
                            winline_soup = BeautifulSoup(driver.page_source, 'html.parser')
                            winline_table = winline_soup.find('div',attrs={'class':'result-table__row'})
                            if winline_table is not None:
                                odds_table = winline_table.find_all('span',attrs={'class':'result-table__count'})
                                if odds_table is not None:
                                    break
                            driver.refresh() #refresh
                            time.sleep(3)
                        
                        #driver.close() #close

                        winline_table = winline_soup.find('div',attrs={'class':'result-table__row'})
                        odds_table = winline_table.find_all('span',attrs={'class':'result-table__count'})
                        winline_odds = []
                        for row in odds_table:
                            winline_odds.append(float(row.text))

                        winline_odds.append(round((1 / (1 / winline_odds[0] + 1 / winline_odds[1])),2))
                        winline_odds.append(round((1 / (1 / winline_odds[0] + 1 / winline_odds[2])),2))
                        winline_odds.append(round((1 / (1 / winline_odds[1] + 1 / winline_odds[2])),2))
                        odds.loc[0] = winline_odds
                        winline_flag = False
                    except:
                        pass
                    
                if (odds.loc[0,'AvgCH'] == 0) & (odds.loc[0,'AvgCD'] == 0) & (odds.loc[0,'AvgCA'] == 0):
                    driver.get(url) #open
                    time.sleep(3)
                    try:
                        driver.find_element(by='class name', value='webpush-swal2-close').click() #close add
                        time.sleep(3)
                    except:
                        pass
                    driver.find_element(by='link text',value='Betting').click() #move to odds
                    odds_soup = BeautifulSoup(driver.page_source, 'html.parser')
                    odds = GetOdds(odds_soup)
                    #driver.close() #close

                home_players = PlayersTable(soup, 'home')
                away_players = PlayersTable(soup, 'away')

                HTAttackRating = round(np.mean(home_players[home_players['Position']=='Attack'].Rating),2)
                HTMidfieldRating = round(np.mean(home_players[home_players['Position']=='Midfield'].Rating),2)
                HTDefenseRating = round(np.mean(home_players[home_players['Position']=='Defense'].Rating),2)

                ATAttackRating = round(np.mean(away_players[away_players['Position']=='Attack'].Rating),2)
                ATMidfieldRating = round(np.mean(away_players[away_players['Position']=='Midfield'].Rating),2)
                ATDefenseRating = round(np.mean(away_players[away_players['Position']=='Defense'].Rating),2)


                home, away = TeamsURL(soup)
                teams_url = [home, away]

                for team in teams_url:

                    driver.get(whoscored_url + team) #open
                    time.sleep(3)
                    while_counter = 0
                    while(while_counter < 3):
                        while_counter += 1
                        soup = BeautifulSoup(driver.page_source, 'html.parser')
                        rating_table = soup.find('div', attrs={'id':'statistics-team-table-summary'})
                        if rating_table is not None:
                            last_tr = rating_table.find_all('tr')
                            if len(last_tr) > 0:
                                break
                        driver.refresh() #refresh
                        time.sleep(3)

                    last_tr = rating_table.find_all('tr')[-1:][0]
                    rating = 0
                    games_played = 0
                    if last_tr.find('td', attrs={'class' : 'rating'}) is not None:
                        rating = float(last_tr.find('td', attrs={'class' : 'rating'}).text)

                    table_rows = rating_table.find_all('tr')
                    df = pd.DataFrame(columns=('Apps','Rating'))
                    for row in table_rows:
                        apps = row.find('td',attrs={'class':'apps'})
                        row_rating = row.find('td',attrs={'class':'sorted'})
                        if (apps is not None) & (row_rating is not None):
                            df.loc[len(df)] = [apps.text, row_rating.text]
                    games_played = sum((df[df.Rating != '-'].Apps).astype('int64'))
                    try:
                        driver.find_element(by='class name', value='webpush-swal2-close').click() #close add
                    except:
                        pass
                    driver.find_element(by='link text',value='Fixtures').click() #move to fixtures

                    while_counter = 0
                    while(while_counter < 3):
                        while_counter += 1
                        soup = BeautifulSoup(driver.page_source, 'html.parser')
                        table = soup.find('div',attrs={'id':'team-fixtures'})
                        if table is not None:
                            break  
                        driver.refresh() #refresh
                        time.sleep(3)
                    #driver.close() #close

                    rows = table.find_all('div',attrs={'class':'divtable-row'})
                    matches = pd.DataFrame(columns=('Result','HomeTeam','AwayTeam','HomeGoals','AwayGoals'))
                    for row in rows:
                        if (row.find('a',attrs={'class':'box'}) == None) | (row.find('a',attrs={'class':'horiz-match-link'}) == None):
                            continue
                        result = row.find('a',attrs={'class':'box'}).text.upper()
                        home_team = row.find('div',attrs={'class':'home'}).find('a',attrs={'class':'team-link'}).text
                        away_team = row.find('div',attrs={'class':'away'}).find('a',attrs={'class':'team-link'}).text
                        goals = row.find('a',attrs={'class':'horiz-match-link'}).text.replace(' ','').replace('*','').split(':')
                        match_data = [ result, home_team, away_team, int(goals[0]), int(goals[1]) ]
                        matches.loc[len(matches)] = match_data

                    if team == home:
                        home_fixtures = matches
                        HTMatchesPlayed = games_played
                        HTRating = rating
                    else:
                        away_fixtures = matches
                        ATMatchesPlayed = games_played
                        ATRating = rating

                if np.isnan(HTAttackRating):
                    HTAttackRating = HTRating
                if np.isnan(HTMidfieldRating):
                    HTMidfieldRating = HTRating
                if np.isnan(HTDefenseRating):
                    HTDefenseRating = HTRating

                if np.isnan(ATAttackRating):
                    ATAttackRating = HTRating
                if np.isnan(ATMidfieldRating):
                    ATMidfieldRating = HTRating
                if np.isnan(ATDefenseRating):
                    ATDefenseRating = HTRating

                HTScored, HTConceded = TeamMeanGoals(home_fixtures, home_name)
                ATScored, ATConceded = TeamMeanGoals(away_fixtures, away_name)

                HomePoints3, HomePoints5 = TeamPoints(home_fixtures)
                AwayPoints3, AwayPoints5 = TeamPoints(away_fixtures)

                HomeLastMatches = TeamLastMatches(home_fixtures)
                AwayLastMatches = TeamLastMatches(away_fixtures)

                match.loc[len(match)] = [ home_name, away_name, home_href, away_href, HTRating, ATRating, 
                HTAttackRating, ATAttackRating, HTMidfieldRating, ATMidfieldRating, HTDefenseRating, ATDefenseRating, 
                HTScored, ATScored, HTConceded, ATConceded, HomePoints3, HomePoints5, AwayPoints3, AwayPoints5, 
                HTMatchesPlayed, ATMatchesPlayed, HomeLastMatches, AwayLastMatches]

                if np.isnan(HTAttackRating) & np.isnan(HTMidfieldRating) & np.isnan(HTDefenseRating ):
                    main_flag = False
                    match = None
                elif np.isnan(ATAttackRating) & np.isnan(ATMidfieldRating) & np.isnan(ATDefenseRating):
                    main_flag = False
                    match = None
                elif HTRating == 0:
                    main_flag = False
                    match = None
                elif ATRating == 0:
                    main_flag = False
                    match = None
                else:
                    match = pd.concat([odds,match], axis=1)
                #full_stats = FullStats(match)

                stats = GetPrediction(match, match_prev)

                if stats is None:
                    main_flag = False
                    continue
                print(str(stats.Teams) + ' was parsed')       
                predicted_matches.loc[len(predicted_matches)] = stats.loc[0]
                main_flag = False
                time.sleep(3)
            except:
                pass

    if not predicted_matches.empty:
        MatchDayResumeRU(predicted_matches)

    best_bets = MatchDayBets(predicted_matches)

    matches = pd.read_excel(folder + 'data/matches.xlsx')
    matches = pd.concat([predicted_matches, matches], ignore_index=True, axis=0) 
    matches.to_excel(folder + 'data/matches.xlsx',index=False)

    bets = pd.read_excel(folder + 'data/bets.xlsx')
    bets = pd.concat([best_bets, bets], ignore_index=True, axis=0) 
    bets.to_excel(folder + 'data/bets.xlsx',index=False)

print('End of Script')

driver.quit()

reboot = 'reboot'
os.system(reboot)