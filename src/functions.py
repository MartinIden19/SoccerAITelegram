import pandas as pd
import numpy as np
import datetime
from src.dictionaries import Positions
from src.config import ubuntu_delta, time_stamp_mor, time_stamp_eve, rf_ftr, rf_ftr_v2, folder

def to_datetime(date, time):
    str_date = date + ' ' + time
    date_format = "%d-%m-%Y %H:%M"
    dt = datetime.datetime.strptime(str_date, date_format)
    return dt

def FindNewMatches(preview):
    if preview is None: 
        return None
    matches = pd.read_excel(folder + 'data/matches.xlsx')
    new_matches = pd.DataFrame(columns=preview.columns)
    current_datetime = datetime.datetime.now() + datetime.timedelta(hours=ubuntu_delta)
    morning = current_datetime.replace(hour=14, minute = 0, second=0)
    evening = current_datetime.replace(hour=16, minute = 0, second=0)
    if current_datetime < morning:
        time_stamp = time_stamp_mor
    elif current_datetime > evening:
        time_stamp = time_stamp_eve
    else:
        time_stamp = time_stamp_mor
    for index, match in preview.iterrows():
        if matches[matches['Preview Link'] == match['Preview Link']].empty:
            match_datetime = to_datetime(match['Date'], match['Time (MSK)'])
            if match_datetime < current_datetime + datetime.timedelta(hours=time_stamp):
                new_matches.loc[len(new_matches)] = match
    
    new_matches = new_matches.drop(new_matches[(new_matches.Tournament == 'League One') | (new_matches.Tournament == 'League Two') | 
        (new_matches.Tournament == 'FA Cup') | (new_matches.Tournament == 'League Cup') | (new_matches.Tournament == 'Championship') | 
        (new_matches.Tournament == 'Premiership') | (new_matches.Tournament == '2. Bundesliga') | (new_matches.Tournament == 'Jupiler Pro League')].index)
    
    if current_datetime < morning:
        new_matches = new_matches.drop(new_matches[(new_matches.Tournament == 'Brasileirão') | (new_matches.Tournament == 'Major League Soccer') | 
            (new_matches.Tournament == 'Liga Profesional')].index)
    print(set(new_matches.Tournament))
    return new_matches

def ProbToCoef(prob, marge):
    coef = 1/(prob + marge)
    return float(coef)

def MatchProbs(data):
    if (data.loc[0,'AvgCH'] == 0) | (data.loc[0,'AvgCD'] == 0) | (data.loc[0,'AvgCA'] == 0):
        prep_data = data.drop(columns=['HomeTeam','AwayTeam','HomeHref','AwayHref','HTMatches','ATMatches','HTLastMatches','ATLastMatches','AvgCH','AvgCD','AvgCA','DoubleChanceHD','DoubleChanceHA','DoubleChanceAD'])
        #prep_data = data[['HTRating', 'ATRating', 'HTAR', 'ATAR', 'HTMR', 'ATMR', 'HTDR',
       #'ATDR', 'HTMGS', 'ATMGS', 'HTMGC', 'ATMGC', 'HTPoints3',
       #'HTPoints5', 'ATPoints3', 'ATPoints5']]
        probs_list = list(rf_ftr_v2.predict_proba(prep_data)[0])
    else:
        prep_data = data.drop(columns=['HomeTeam','AwayTeam','HomeHref','AwayHref','HTMatches','ATMatches','HTLastMatches','ATLastMatches','DoubleChanceHD','DoubleChanceHA','DoubleChanceAD'])
        #prep_data = data[['AvgCH', 'AvgCD', 'AvgCA', 'HTRating', 'ATRating', 'HTAR', 'ATAR',
       #'HTMR', 'ATMR', 'HTDR', 'ATDR', 'HTMGS', 'ATMGS', 'HTMGC', 'ATMGC',
       #'HTPoints3', 'HTPoints5', 'ATPoints3', 'ATPoints5']]
        probs_list = list(rf_ftr.predict_proba(prep_data)[0])
    probs = pd.DataFrame(columns=('HomeProb','DrawProb','AwayProb','HD_Prob','HA_Prob','AD_Prob'))
    probs_list.append(probs_list[0] + probs_list[1])
    probs_list.append(probs_list[0] + probs_list[2])
    probs_list.append(probs_list[1] + probs_list[2])
    probs.loc[0] = probs_list
    return probs

def FullStats(stats):
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

def GetPrediction(match, match_prev):
    stats = pd.DataFrame(columns=('HomeTeam','AwayTeam','HomeHref','AwayHref','HTRating','ATRating','HTAR','ATAR','HTMR','ATMR','HTDR','ATDR',
    'HTMGS','ATMGS','HTMGC','ATMGC','HTPoints3','HTPoints5','ATPoints3','ATPoints5','HTMatches','ATMatches','HTLastMatches','ATLastMatches',
    'AvgCH','AvgCD','AvgCA','DoubleChanceHD','DoubleChanceHA','DoubleChanceAD','HomeProb','DrawProb','AwayProb','HD_Prob','HA_Prob','AD_Prob'))
    match_stats = FullStats(match)

    if match_stats is None:
        empty = pd.DataFrame(np.nan, index=[0], columns=('HomeTeam','AwayTeam','HomeHref','AwayHref','HTRating','ATRating','HTAR','ATAR','HTMR','ATMR','HTDR','ATDR',
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
    stats = stats[['HomeTeam','AwayTeam','HomeHref','AwayHref','HTRating','ATRating','HTAR','ATAR','HTMR','ATMR','HTDR','ATDR',
    'HTMGS','ATMGS','HTMGC','ATMGC','HTPoints3','HTPoints5','ATPoints3','ATPoints5','HTMatches','ATMatches','HTLastMatches','ATLastMatches',
    'AvgCH','AvgCD','AvgCA','DoubleChanceHD','DoubleChanceHA','DoubleChanceAD','HomeProb','DrawProb','AwayProb','HD_Prob','HA_Prob','AD_Prob']] 
    prev = pd.DataFrame(columns=('Date', 'Country', 'Tournament', 'Time (MSK)', 'Teams', 'Preview Link'))
    prev.loc[len(prev)] = match_prev
    match_stats = pd.concat([prev, stats], axis=1) 
    match_stats['Result'] = 'Returned'
    return match_stats


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