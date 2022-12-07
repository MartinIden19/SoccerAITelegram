import pandas as pd
import numpy as np
from bs4 import BeautifulSoup 
from selenium import webdriver
import os
import datetime
from src.dictionaries import Positions, no_matches, Winline_Teams
from src.config import msk_delta, time_stamp, whoscored_url, preview_url, rf_ftr, rf_ftr_v2, folder
from src.winline import WinlineOdds

os.environ['MOZ_HEADLESS'] = '1'
driver = webdriver.Firefox(executable_path = folder + 'geckodriver',service_log_path = folder + 'geckodriver.log')

def PlayersTable(soup, home_away):
    pitch = soup.find('div',attrs = {'class':'pitch'})
    players_table = pitch.find('div',attrs = {'class': home_away })
    players = pd.DataFrame(columns=('Name','Position','Card','Rating'))
    rows = players_table.find_all('ul')
    for row in rows:
        rating = row.find('li',attrs = {'class':'player-rating rc'}).text
        if rating == 'N/A':
            continue
        title = row['title']
        name = title.split('(')[0]
        pos = title.split('(')[1]
        card = row.find('a',attrs = {'class':'player-link'})['href']
        player = [ name, pos[:-1], card, float(rating) ]
        players.loc[len(players)] = player
    players = players.replace({'Position' : Positions})
    return players

def TeamPage(url):
    driver = webdriver.Firefox(executable_path = folder + 'geckodriver',service_log_path = folder + 'geckodriver.log')
    driver.get(url)
    while(True):
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        rating_table = soup.find('div', attrs={'id':'statistics-team-table-summary'})
        if rating_table is not None:
            last_tr = rating_table.find_all('tr')
            if len(last_tr) > 0:
                break
        driver.refresh()

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
    
    driver.find_element(by='link text',value='Fixtures').click()
    while(True):
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        table = soup.find('div',attrs={'id':'team-fixtures'})
        if table is not None:
            break  
        driver.refresh()
    rows = table.find_all('div',attrs={'class':'divtable-row'})
    matches = pd.DataFrame(columns=('Result','HomeTeam','AwayTeam','HomeGoals','AwayGoals'))
    for row in rows:
        if (row.find('a',attrs={'class':'box'}) == None) | (row.find('a',attrs={'class':'horiz-match-link'}) == None):
            continue
        result = row.find('a',attrs={'class':'box'}).text.upper()
        home_team = row.find('div',attrs={'class':'home'}).find('a',attrs={'class':'team-link'}).text
        away_team = row.find('div',attrs={'class':'away'}).find('a',attrs={'class':'team-link'}).text
        goals = row.find('a',attrs={'class':'horiz-match-link'}).text.replace(' ','').replace('*','').split(':')
        match = [ result, home_team, away_team, int(goals[0]), int(goals[1]) ]
        matches.loc[len(matches)] = match
    driver.close()
    return matches, games_played, rating

def TeamsURL(soup):
    info = soup.find('div', attrs={'class':'teams-score-info'})  
    home = info.find('span', attrs={'class':'home'}).find('a',attrs={'class':'team-link'})['href']
    away = info.find('span', attrs={'class':'away'}).find('a',attrs={'class':'team-link'})['href']
    return home, away

def TeamMeanGoals(matches, team):
    Scored = round((sum(matches[matches['HomeTeam']==team]['HomeGoals']) + sum(matches[matches['AwayTeam']==team]['AwayGoals']))/len(matches),2)
    Conceded = round((sum(matches[matches['HomeTeam']!=team]['HomeGoals']) + sum(matches[matches['AwayTeam']!=team]['AwayGoals']))/len(matches),2)
    return Scored, Conceded

def TeamPoints(matches):
    while len(matches) < 5:
        df = pd.DataFrame([[0] * len(matches.columns)], columns=matches.columns)
        matches = df.append(matches, ignore_index=True)
    Points= 0
    i=0
    for result in matches.tail(5)['Result']:
        if result=='W':
            Points+=3
        elif result=='D':
            Points+=1
        i+=1
        if i==2:
            Points2 = Points
    Points5 = Points
    Points3 = Points5 - Points2
    return Points3, Points5

def TeamLastMatches(matches):
    res = ''
    for result in matches.tail(6)['Result']:
        if result=='W':
            res += 'W'
        elif result=='D':
            res += 'D'
        else:
            res += 'L'
    res = res[::-1]
    return res

def GetOdds(soup):
    odds_box = soup.find('div',attrs={'id':'odds-side-box'})
    bet_odds_list = []
    bet_odds = pd.DataFrame(columns=('AvgCH','AvgCD','AvgCA','DoubleChanceHD','DoubleChanceHA','DoubleChanceAD'))
    if odds_box is None:
        bet_odds_list = [0, 0, 0, 0, 0, 0]
        bet_odds.loc[0] = bet_odds_list
        return bet_odds
    bet_odds_span = odds_box.find_all('span', attrs={'class':'odds-numeric'})
    for odd in bet_odds_span:
        bet_odds_list.append(float(odd.text))
    bet_odds_list.append(round((1 / (1 / bet_odds_list[0] + 1 / bet_odds_list[1])),2))
    bet_odds_list.append(round((1 / (1 / bet_odds_list[0] + 1 / bet_odds_list[2])),2))
    bet_odds_list.append(round((1 / (1 / bet_odds_list[1] + 1 / bet_odds_list[2])),2))
    bet_odds.loc[0] = bet_odds_list
    return bet_odds

def MatchStats(url):
    driver = webdriver.Firefox(executable_path = folder + 'geckodriver',service_log_path = folder + 'geckodriver.log')
    driver.get(url)
    while(True):
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        info = soup.find('div', attrs={'class':'teams-score-info'})
        if info is not None:
            break
        driver.refresh()
    match = pd.DataFrame(columns=('HomeTeam','AwayTeam','HTRating','ATRating','HTAR','ATAR','HTMR','ATMR',
    'HTDR','ATDR','HTMGS','ATMGS','HTMGC','ATMGC','HTPoints3','HTPoints5','ATPoints3','ATPoints5','HTMatches','ATMatches','HTLastMatches','ATLastMatches'))

    home_name = info.find('span', attrs={'class':'home'}).find('a',attrs={'class':'team-link'}).text
    away_name = info.find('span', attrs={'class':'away'}).find('a',attrs={'class':'team-link'}).text

    home_players = PlayersTable(soup, 'home')
    away_players = PlayersTable(soup, 'away')

    HTAttackRating = round(np.mean(home_players[home_players['Position']=='Attack'].Rating),2)
    HTMidfieldRating = round(np.mean(home_players[home_players['Position']=='Midfield'].Rating),2)
    HTDefenseRating = round(np.mean(home_players[home_players['Position']=='Defense'].Rating),2)

    ATAttackRating = round(np.mean(away_players[away_players['Position']=='Attack'].Rating),2)
    ATMidfieldRating = round(np.mean(away_players[away_players['Position']=='Midfield'].Rating),2)
    ATDefenseRating = round(np.mean(away_players[away_players['Position']=='Defense'].Rating),2)

    home, away = TeamsURL(soup)
    home_fixtures, HTMatchesPlayed, HTRating = TeamPage(whoscored_url + home)
    if HTRating == 0:
       return None
    away_fixtures, ATMatchesPlayed, ATRating = TeamPage(whoscored_url + away)
    if ATRating == 0:
        return None

    driver.find_element(by='link text',value='Betting').click()
    odds_soup = BeautifulSoup(driver.page_source, 'html.parser')
    driver.close()

    #odds = GetOdds(odds_soup)
    odds = pd.DataFrame(columns=('AvgCH','AvgCD','AvgCA','DoubleChanceHD','DoubleChanceHA','DoubleChanceAD'))
    odds.loc[0] = [0, 0, 0, 0, 0, 0]

    home_name_ru = home_name
    away_name_ru = away_name
    for key in Winline_Teams.keys():
        if home_name_ru == key:
            home_name_ru = Winline_Teams[key]
        if away_name_ru == key:
            away_name_ru = Winline_Teams[key]

    if (odds.loc[0,'AvgCH'] == 0) & (odds.loc[0,'AvgCD'] == 0) & (odds.loc[0,'AvgCA'] == 0):
        try:
            winline_odds = WinlineOdds(home_name_ru, away_name_ru)
            winline_odds.append(round((1 / (1 / winline_odds[0] + 1 / winline_odds[1])),2))
            winline_odds.append(round((1 / (1 / winline_odds[0] + 1 / winline_odds[2])),2))
            winline_odds.append(round((1 / (1 / winline_odds[1] + 1 / winline_odds[2])),2))
            odds.loc[0] = winline_odds
        except:
            pass

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

    match.loc[len(match)] = [ home_name, away_name, HTRating, ATRating, 
    HTAttackRating, ATAttackRating, HTMidfieldRating, ATMidfieldRating, HTDefenseRating, ATDefenseRating, 
    HTScored, ATScored, HTConceded, ATConceded, HomePoints3, HomePoints5, AwayPoints3, AwayPoints5, 
    HTMatchesPlayed, ATMatchesPlayed, HomeLastMatches, AwayLastMatches]

    match = pd.concat([odds,match], axis=1)

    return match

def ProbToCoef(prob, marge):
    coef = 1/(prob + marge)
    return coef

def MatchProbs(data):
    if (data.loc[0,'AvgCH'] == 0) | (data.loc[0,'AvgCD'] == 0) | (data.loc[0,'AvgCA'] == 0):
        prep_data = data.drop(columns=['HomeTeam','AwayTeam','HTMatches','ATMatches','HTLastMatches','ATLastMatches','AvgCH','AvgCD','AvgCA','DoubleChanceHD','DoubleChanceHA','DoubleChanceAD'])
        probs_list = list(rf_ftr_v2.predict_proba(prep_data)[0])
    else:
        prep_data = data.drop(columns=['HomeTeam','AwayTeam','HTMatches','ATMatches','HTLastMatches','ATLastMatches','DoubleChanceHD','DoubleChanceHA','DoubleChanceAD'])
        probs_list = list(rf_ftr.predict_proba(prep_data)[0])
    probs = pd.DataFrame(columns=('HomeProb','DrawProb','AwayProb','HD_Prob','HA_Prob','AD_Prob'))
    probs_list.append(probs_list[0] + probs_list[1])
    probs_list.append(probs_list[0] + probs_list[2])
    probs_list.append(probs_list[1] + probs_list[2])
    probs.loc[0] = probs_list
    return probs

def FullStats(url):
    stats = MatchStats(url)
    if stats is None:
        return None
    probs = MatchProbs(stats)
    if (stats.loc[0,'AvgCH'] == 0) | (stats.loc[0,'AvgCD'] == 0) | (stats.loc[0,'AvgCA'] == 0):
        marge = 0.05/3
        dc_marge = 0.05/3
    else: 
        marge = (1/stats['AvgCH'] + 1/stats['AvgCD'] + 1/stats['AvgCA'] - 1)/3
        dc_marge = (1/stats['DoubleChanceHD'] + 1/stats['DoubleChanceHA'] + 1/stats['DoubleChanceAD'] - 2)/3
    probs['HomeProb'] = round(ProbToCoef(probs['HomeProb'], marge),2)
    probs['DrawProb'] = round(ProbToCoef(probs['DrawProb'], marge),2)
    probs['AwayProb'] = round(ProbToCoef(probs['AwayProb'], marge),2)
    probs['HD_Prob'] = round(ProbToCoef(probs['HD_Prob'], dc_marge),2)
    probs['HA_Prob'] = round(ProbToCoef(probs['HA_Prob'], dc_marge),2)
    probs['AD_Prob'] = round(ProbToCoef(probs['AD_Prob'], dc_marge),2)

    data = pd.concat([stats,probs], axis=1)
    return data

def GetPreview():
    driver = webdriver.Firefox(executable_path = folder + 'geckodriver',service_log_path = folder + 'geckodriver.log')
    driver.get(preview_url)
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    previews_table = soup.find('div', attrs={'class':'previews'}).find('tbody')
    if previews_table is None:
        print(no_matches)
        return None
    driver.close()
    rows = previews_table.find_all('tr')
    date, tournament, country = None, None, None
    data = pd.DataFrame(columns=('Date','Country','Tournament','Time (MSK)','Teams','Preview Link'))
    for row in rows:
        if row.find('td', attrs={'class':'previews-date'}) is not None:
            date = row.find('td', attrs={'class':'previews-date'}).text.strip().split(',')[0]
        if row.find('span', attrs={'class':'country'}) is not None:
            country = row.find('span', attrs={'class':'country'})['title']
        if row.find('a', attrs={'class':'level-2'}) is not None:
            tournament = row.find('a', attrs={'class':'level-2'}).text.strip()

        if row.find('td', attrs={'class':'time'}) is not None:
            time = row.find('td', attrs={'class':'time'}).text.strip()
            teams = row.find('a').text.strip()
            preview_href = row.find('a')['href']
            dt = to_datetime(date, time) + datetime.timedelta(hours=msk_delta)
            date1 = dt.strftime("%d-%m-%Y")
            time1 = dt.strftime("%H:%M")
            data.loc[len(data)] = [date1, country, tournament, time1, teams, whoscored_url + preview_href]
    return data

def to_datetime(date, time):
    str_date = date + ' ' + time
    date_format = "%d-%m-%Y %H:%M"
    dt = datetime.datetime.strptime(str_date, date_format)
    return dt

def FindNewMatches():
    preview = GetPreview()
    if preview is None: 
        return None
    matches = pd.read_excel(folder + 'data/matches.xlsx')
    new_matches = pd.DataFrame(columns=preview.columns)
    current_datetime = datetime.datetime.now()
    for index, match in preview.iterrows():
        if matches[matches['Preview Link'] == match['Preview Link']].empty:
            match_datetime = to_datetime(match['Date'], match['Time (MSK)'])
            if match_datetime < current_datetime + datetime.timedelta(hours=time_stamp):
                new_matches.loc[len(new_matches)] = match
    new_matches = new_matches.drop(new_matches[(new_matches.Tournament == 'League One') | (new_matches.Tournament == 'League Two')].index)
    return new_matches

def AddPrediction(match):
    stats = pd.DataFrame(columns=('HomeTeam','AwayTeam','HTRating','ATRating','HTAR','ATAR','HTMR','ATMR','HTDR','ATDR',
    'HTMGS','ATMGS','HTMGC','ATMGC','HTPoints3','HTPoints5','ATPoints3','ATPoints5','HTMatches','ATMatches','HTLastMatches','ATLastMatches',
    'AvgCH','AvgCD','AvgCA','DoubleChanceHD','DoubleChanceHA','DoubleChanceAD','HomeProb','DrawProb','AwayProb','HD_Prob','HA_Prob','AD_Prob'))
    match_stats = FullStats(match['Preview Link'])

    if match_stats is None:
        empty = pd.DataFrame(np.nan, index=[0], columns=('HomeTeam','AwayTeam','HTRating','ATRating','HTAR','ATAR','HTMR','ATMR','HTDR','ATDR',
            'HTMGS','ATMGS','HTMGC','ATMGC','HTPoints3','HTPoints5','ATPoints3','ATPoints5','HTMatches','ATMatches','HTLastMatches','ATLastMatches',
            'AvgCH','AvgCD','AvgCA','DoubleChanceHD','DoubleChanceHA','DoubleChanceAD','HomeProb','DrawProb','AwayProb','HD_Prob','HA_Prob','AD_Prob','Result'))
        prev = pd.DataFrame(columns=('Date', 'Country', 'Tournament', 'Time (MSK)', 'Teams', 'Preview Link'))
        prev.loc[len(prev)] = match
        match_stats = pd.concat([prev, empty], axis=1) 
        matches = pd.read_excel(folder + 'data/matches.xlsx')
        matches = pd.concat([matches, match_stats], ignore_index=True, axis=0) 
        matches.to_excel(folder + 'data/matches.xlsx',index=False)
        return None

    stats.loc[len(stats)] = match_stats.loc[0]
    stats = stats[['HomeTeam','AwayTeam','HTRating','ATRating','HTAR','ATAR','HTMR','ATMR','HTDR','ATDR',
    'HTMGS','ATMGS','HTMGC','ATMGC','HTPoints3','HTPoints5','ATPoints3','ATPoints5','HTMatches','ATMatches','HTLastMatches','ATLastMatches',
    'AvgCH','AvgCD','AvgCA','DoubleChanceHD','DoubleChanceHA','DoubleChanceAD','HomeProb','DrawProb','AwayProb','HD_Prob','HA_Prob','AD_Prob']] 
    prev = pd.DataFrame(columns=('Date', 'Country', 'Tournament', 'Time (MSK)', 'Teams', 'Preview Link'))
    prev.loc[len(prev)] = match
    match_stats = pd.concat([prev, stats], axis=1) 
    match_stats['Result'] = 'Returned'
    return match_stats

def GoodBets(data, coef = 0.94, betmincoef = 1.35, betmaxcoef = 3.25, dc_coef = 0.95, dc_betmincoef = 1.45, dc_betmaxcoef = 2.2):
    good_bets = pd.DataFrame(columns=data.columns)
    prediction = []
    for index, bet in data.iterrows():
        if (bet['HTMatches'] > 4) & (bet['ATMatches'] > 4):
            if bet['HomeProb'] < bet['AvgCH'] * coef and bet['AvgCH'] > betmincoef and bet['AvgCH'] < betmaxcoef:
                good_bets.loc[len(good_bets)] = bet
                prediction.append('Home')
            if bet['DrawProb'] < bet['AvgCD'] * coef and bet['AvgCD'] > betmincoef and bet['AvgCD'] < betmaxcoef:
                good_bets.loc[len(good_bets)] = bet
                prediction.append('Draw')
            if bet['AwayProb'] < bet['AvgCA'] * coef and bet['AvgCA'] > betmincoef and bet['AvgCA'] < betmaxcoef:
                good_bets.loc[len(good_bets)] = bet
                prediction.append('Away')
            if bet['HD_Prob'] < bet['DoubleChanceHD'] * dc_coef and bet['DoubleChanceHD'] > dc_betmincoef and bet['DoubleChanceHD'] < dc_betmaxcoef:
                good_bets.loc[len(good_bets)] = bet
                prediction.append('Home or Draw')
            if bet['HA_Prob'] < bet['DoubleChanceHA'] * dc_coef and bet['DoubleChanceHA'] > dc_betmincoef and bet['DoubleChanceHA'] < dc_betmaxcoef:
                good_bets.loc[len(good_bets)] = bet
                prediction.append('Home or Away')
            if bet['AD_Prob'] < bet['DoubleChanceAD'] * dc_coef and bet['DoubleChanceAD'] > dc_betmincoef and bet['DoubleChanceAD'] < dc_betmaxcoef:
                good_bets.loc[len(good_bets)] = bet
                prediction.append('Away or Draw')
        good_bets['Prediction'] = prediction
    return good_bets

def ParseMatchResult(match):
    driver = webdriver.Firefox(executable_path = folder + '/geckodriver',service_log_path = folder + 'geckodriver.log')
    driver.get(match['Preview Link'])
    while(True):
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        header = soup.find('div',attrs={'id' : 'match-header'})
        if header is not None:
            break
        driver.refresh()
    driver.close()
    result = header.find('span',attrs={'class' : 'result'}).text
        
    if result == 'vs':
        return 'Returned'

    result = result.replace(':',' ')
    result = result.replace('*','')
    result = result.split()

    home_goals, away_goals = float(result[0]), float(result[1])

    if home_goals > away_goals:
        return 'Home'
    elif home_goals < away_goals:
        return 'Away'
    elif home_goals == away_goals:
        return 'Draw'
        
    return 'Returned'