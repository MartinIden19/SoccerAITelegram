import telepot
import pandas as pd
import datetime
from src.dictionaries import Flags
from src.parse import AddPrediction, GoodBets, to_datetime
from src.config import folder

def SendMessage(text):
    token = '5567466854:AAHuf7kHMEN_8z_odmavl0h0_oPDAlgzmh8'
    bot = telepot.Bot(token)
    chat_id = '-1001747880907'
    bot.sendMessage(chat_id, text, parse_mode='html')

def PostBet(good_bets):
    if not good_bets.empty:
        good_bets = good_bets.replace({'Country' : Flags})
        bet = good_bets.loc[0]
        datetime = '📅 ' + bet.Date + ', ' + bet['Time (MSK)'] + ' (MSK)' + '\n'
        tournament = bet.Country + ' ' + bet.Tournament + '\n'
        game = '<a href="' + bet['Preview Link'] + '">' + bet.HomeTeam + ' vs ' + bet.AwayTeam + '</a>\n'
        home = 'Home: ' + str(bet.HTRating) + ' (' + str(bet.HTMatches) + ' games, ' + bet.HTLastMatches + ')\n'
        away = 'Away: ' + str(bet.ATRating) + ' (' + str(bet.ATMatches) + ' games, ' + bet.ATLastMatches + ')\n'
        message = datetime + tournament + game + home + away 
        for index, bet in good_bets.iterrows():
            predict = bet.Prediction
            if predict == 'Home':
                prediction = bet.HomeTeam + ' Win — ' + str(bet.AvgCH) + ' (' + str(bet.HomeProb) + ')'
            elif predict == 'Away':
                prediction = bet.AwayTeam + ' Win — ' + str(bet.AvgCA) + ' (' + str(bet.AwayProb) + ')'
            elif predict == 'Draw':
                prediction = 'Draw — ' + str(bet.AvgCD) + ' (' + str(bet.DrawProb) + ')'
            elif predict == 'Home or Draw':
                prediction = bet.HomeTeam + ' Win or Draw — ' + str(bet.DoubleChanceHD) + ' (' + str(bet.HD_Prob) + ')'
            elif predict == 'Home or Away':
                prediction = bet.HomeTeam +' or ' + bet.AwayTeam + ' Win — ' + str(bet.DoubleChanceHA) + ' (' + str(bet.HA_Prob) + ')'
            elif predict == 'Away or Draw':
                prediction = bet.AwayTeam + ' Win or Draw — ' + str(bet.DoubleChanceAD) + ' (' + str(bet.AD_Prob) + ')'
            message += '<b>' + prediction + '</b>\n'             
        message = message.rstrip()    
        SendMessage(message)

def GetPrediction(match):
    match_stats = AddPrediction(match)
    return match_stats

def MatchDayResume(matches):
    matches = matches.replace({'Country' : Flags})
    message = '⚽ <b>Soccer AI Predictions</b> ⚽\n\n'
    group_date = matches.groupby(['Date'])
    dates = list(set(matches['Date']))
    time = '00:00'
    dt = [to_datetime(date, time) for date in dates]
    dt = sorted(dt)
    dt_sorted = [date.strftime("%d-%m-%Y") for date in dt]
    flag = False
    for date in dt_sorted:
        message += '📅 ' + '<b>' + date + '</b>' + '\n'
        matchday = group_date.get_group(date)
        group_country = matchday.groupby(['Country'])
        for country in set(matchday['Country']): 
            message += country + ' '
            match_country = group_country.get_group(country)
            group_league = match_country.groupby(['Tournament'])
            for league in set(match_country['Tournament']): 
                message += league + ' ' + country + '\n'
                match_league = group_league.get_group(league)
                match_league['Time (MSK)'] = pd.to_datetime(match_league['Time (MSK)'])
                match_league = match_league.sort_values(by='Time (MSK)')
                match_league['Time (MSK)'] = [datetime.datetime.strftime(dt, "%H:%M") for dt in match_league['Time (MSK)']] 
                for index, match in match_league.iterrows(): 
                    message += '⌚ ' + match['Time (MSK)'] + ' ' + '<a href="' + match['Preview Link'] + '">' + match.HomeTeam + ' vs ' + match.AwayTeam + '</a>'
                    if match['AvgCH'] == 0:
                        flag = True
                        message+=' ♻️'
                    message += '\n🎲 <b>' + str(match.HomeProb) + ' | ' + str(match.DrawProb) + ' | ' + str(match.AwayProb) + ' 🎲 ' + str(match.HD_Prob) + ' | ' + str(match.HA_Prob) + ' | ' + str(match.AD_Prob) + '</b>'
                    if match['AvgCH'] == 0:
                        flag = True
                        message+=' ❗'
                    message += '\n'
            message += '\n'
        message += '\n'
    if flag:
        message+= "♻️ — Betting Odds didn't count in the prediction"
    message = message.replace('\n\n\n', '\n\n')
    message = message.rstrip()
    return message