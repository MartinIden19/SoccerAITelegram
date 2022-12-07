import telepot
import pandas as pd
import datetime
from src.dictionaries import Flags, Leagues, RussianNames, Countries, CountriesReversed, NationsLeague, En_Leagues
from src.functions import to_datetime
from src.betting import GoodBets
from src.config import folder, telegram_limit, telegram_limit_media, ubuntu_delta

def SendMessage(text):
    token = '5567466854:AAHuf7kHMEN_8z_odmavl0h0_oPDAlgzmh8'
    bot = telepot.Bot(token)
    chat_id = '-1001558421242'
    bot.sendMessage(chat_id, text, parse_mode='html')

def SendPhoto(photo, text):
    token = '5567466854:AAHuf7kHMEN_8z_odmavl0h0_oPDAlgzmh8'
    bot = telepot.Bot(token)
    chat_id = '-1001558421242'
    bot.sendPhoto(chat_id, photo, text, parse_mode='html')

def MatchDayResumeRU(matches):

    #message = '⚽ <b>Прогнозы от SoccerAI</b> ⚽\n\n'
    message = ''
    length_message = ''
    flag = False

    countries = list(set(matches['Country']))
    code_list = []
    for country in countries:
        for key in Countries.keys():
            if country == key:
                code_list.append(Countries[key])
    code_list = sorted(code_list)

    c_sorted = []
    for country in code_list:
        for key in CountriesReversed.keys():
            if country == key:
                c_sorted.append(CountriesReversed[key])

    matches = matches.replace({'Country' : Flags, 'Tournament' : Leagues, 'HomeTeam' : RussianNames, 'AwayTeam' : RussianNames})
    group_country = matches.groupby(['Country'])

    message_counter = 0

    current_datetime = datetime.datetime.now() + datetime.timedelta(hours=ubuntu_delta)
    morning = current_datetime.replace(hour=14, minute = 0, second=0)
    evening = current_datetime.replace(hour=16, minute = 0, second=0)
    if current_datetime < morning:
        photo = open(folder + 'images/overview_morning.png', 'rb')
    else:
        photo = open(folder + 'images/overview_evening.png', 'rb')
        
    dt = []
    for index, match in matches.iterrows():
        dt.append(to_datetime(match['Date'],match['Time (MSK)']))
    matches['Datetime'] = dt
    matches = matches.sort_values(by='Datetime')
    matches = matches.drop('Datetime', axis=1)

    for country in c_sorted:
        #message_league = ''
        for key in Flags.keys():
            if country == key:
                country = Flags[key]
                break
        #message_league += country + ' <b>'
        match_country = group_country.get_group(country)
        group_league = match_country.groupby(['Tournament'])
        for league in set(match_country['Tournament']): 
            message_league = country + ' <b>'
            length_message_league = country + ' '
            prefix = ''
            if country == '🇷🇺':
                prefix = 'Российская '
            if country == '🏴󠁧󠁢󠁥󠁮󠁧󠁿':
                prefix = 'Английская '
            message_league += prefix + league + '</b> ' + country + '\n'
            length_message_league += prefix + league + ' ' + country + '\n'
            match_league = group_league.get_group(league)
    
            for index, match in match_league.iterrows(): 
                message_league += '⌚ ' + match['Time (MSK)'] + ' ' + '<a href="' + match['Preview Link'] + '">' + match.HomeTeam + ' — ' + match.AwayTeam + '</a>'
                length_message_league += '⌚ ' + match['Time (MSK)'] + ' ' + match.HomeTeam + ' — ' + match.AwayTeam
                if match['AvgCH'] == 0:
                    flag = True
                    message_league+=' ♻️'
                    length_message_league+=' ♻️'
                message_league += '\n🎲 <b>' + str(match.HomeProb) + ' | ' + str(match.DrawProb) + ' | ' + str(match.AwayProb) + ' 🎲 ' + str(match.HD_Prob) + ' | ' + str(match.HA_Prob) + ' | ' + str(match.AD_Prob) + '</b>'
                length_message_league += '\n🎲 ' + str(match.HomeProb) + ' | ' + str(match.DrawProb) + ' | ' + str(match.AwayProb) + ' 🎲 ' + str(match.HD_Prob) + ' | ' + str(match.HA_Prob) + ' | ' + str(match.AD_Prob)
                if match['AvgCH'] == 0:
                    flag = True
                    message_league+=' ❗'
                    length_message_league+=' ❗'
                message_league += '\n'
                length_message_league += '\n'
            message_league += '\n'
            length_message_league += '\n'
        #message_league += '\n'
            #print(len(message) + len(message_league))
            if (message_counter == 0) & (len(length_message) + len(length_message_league) > telegram_limit_media):
                message = message.replace('\n\n\n', '\n\n')
                message = message.rstrip()
                SendPhoto(photo, message)
                message = message_league
                length_message = length_message_league
                message_counter = 1        
            elif len(length_message) + len(length_message_league) > telegram_limit:
                message = message.replace('\n\n\n', '\n\n')
                message = message.rstrip()
                SendMessage(message)
                message = message_league
                length_message = length_message_league
            else:
                message += message_league
                length_message += length_message_league
    if flag:
        message+= "♻️ — Коэффициенты букмекеров не учитывались в прогнозе"
    message = message.replace('\n\n\n', '\n\n')
    message = message.rstrip()
    if (message_counter == 0):
        SendPhoto(photo, message)
    else:
        SendMessage(message)

def MatchBet(match):
    good_bets = GoodBets(match)
    message = ''
    length_message = ''
    if not good_bets.empty:
        good_bets = good_bets.replace({'Country' : Flags, 'Tournament' : Leagues, 'HomeTeam' : RussianNames, 'AwayTeam' : RussianNames})
        bet = good_bets.loc[0]
        game = '⏰ ' + bet['Time (MSK)'] + ' ' + '<a href="' + bet['Preview Link'] + '">' + bet.HomeTeam + ' — ' + bet.AwayTeam + '</a>\n'
        odds = '🎲 <b>' + str(bet.HomeProb) + ' | ' + str(bet.DrawProb) + ' | ' + str(bet.AwayProb) + ' 🎲 ' + str(bet.HD_Prob) + ' | ' + str(bet.HA_Prob) + ' | ' + str(bet.AD_Prob) + '</b>\n'
        
        length_game = '⏰ ' + bet['Time (MSK)'] + ' ' +  bet.HomeTeam + ' — ' + bet.AwayTeam + '\n'
        length_odds = '🎲 ' + str(bet.HomeProb) + ' | ' + str(bet.DrawProb) + ' | ' + str(bet.AwayProb) + ' 🎲 ' + str(bet.HD_Prob) + ' | ' + str(bet.HA_Prob) + ' | ' + str(bet.AD_Prob) + '\n'
        
        h_lm = bet.HTLastMatches
        a_lm = bet.ATLastMatches
        h_lm = h_lm.replace('W','В')
        h_lm = h_lm.replace('D','Н')
        h_lm = h_lm.replace('L','П')
        a_lm = a_lm.replace('W','В')
        a_lm = a_lm.replace('D','Н')
        a_lm = a_lm.replace('L','П')
        home = '<a href="' + bet.HomeHref + '">' + bet.HomeTeam + '</a>' + ' : ' + str(bet.HTRating) + ' (' + h_lm + ')\n'
        away = '<a href="' + bet.AwayHref + '">' + bet.AwayTeam + '</a>' + ' : ' + str(bet.ATRating) + ' (' + a_lm + ')\n'

        length_home = bet.HomeTeam + ' : ' + str(bet.HTRating) + ' (' + h_lm + ')\n'
        length_away = bet.AwayTeam + ' : ' + str(bet.ATRating) + ' (' + a_lm + ')\n'

        message = game + odds + home + away
        length_message = length_game + length_odds + length_home + length_away
        for index, bet in good_bets.iterrows():
            predict = bet.Prediction
            if predict == 'Home':
                prediction = bet.HomeTeam + ' — ' + str(bet.AvgCH) + ' (' + str(bet.HomeProb) + ')'
            elif predict == 'Away':
                prediction = bet.AwayTeam + ' — ' + str(bet.AvgCA) + ' (' + str(bet.AwayProb) + ')'
            elif predict == 'Draw':
                prediction = 'Ничья — ' + str(bet.AvgCD) + ' (' + str(bet.DrawProb) + ')'
            elif predict == 'Home or Draw':
                prediction = bet.HomeTeam + ' или ничья ' + ' — ' + str(bet.DoubleChanceHD) + ' (' + str(bet.HD_Prob) + ')'
            elif predict == 'Home or Away':
                prediction = bet.HomeTeam + ' или ' + bet.AwayTeam + ' — ' + str(bet.DoubleChanceHA) + ' (' + str(bet.HA_Prob) + ')'
            elif predict == 'Away or Draw':
                prediction = bet.AwayTeam + ' или ничья ' + ' — ' + str(bet.DoubleChanceAD) + ' (' + str(bet.AD_Prob) + ')'
            message += '<b>' + prediction + '</b>\n'
            length_message += prediction + '\n'    
        message += '\n\n'  
        message = message.replace('\n\n\n', '\n\n')
        length_message += '\n\n'  
        length_message = length_message.replace('\n\n\n', '\n\n')  
    return message, good_bets, length_message

def MatchDayBets(matches):
    countries = list(set(matches['Country']))
    code_list = []
    for country in countries:
        for key in Countries.keys():
            if country == key:
                code_list.append(Countries[key])
    code_list = sorted(code_list)

    c_sorted = []
    for country in code_list:
        for key in CountriesReversed.keys():
            if country == key:
                c_sorted.append(CountriesReversed[key])

    match_df = pd.DataFrame(columns=matches.columns)
    matches = matches.replace({'Country' : Flags, 'Tournament' : Leagues, 'HomeTeam' : RussianNames, 'AwayTeam' : RussianNames})
    matches = matches.replace({'Tournament' : NationsLeague})
    best_bets = pd.DataFrame(columns=('Date', 'Country', 'Tournament', 'Time (MSK)', 'Teams', 'Preview Link',
        'HomeTeam','AwayTeam','HomeHref','AwayHref','HTRating','ATRating','HTAR','ATAR','HTMR','ATMR','HTDR','ATDR',
        'HTMGS','ATMGS','HTMGC','ATMGC','HTPoints3','HTPoints5','ATPoints3','ATPoints5','HTMatches','ATMatches','HTLastMatches','ATLastMatches',
        'AvgCH','AvgCD','AvgCA','DoubleChanceHD','DoubleChanceHA','DoubleChanceAD','HomeProb','DrawProb','AwayProb','HD_Prob','HA_Prob','AD_Prob','Result','Prediction')) 
    group_country = matches.groupby(['Country'])
    
    dt = []
    for index, match in matches.iterrows():
        dt.append(to_datetime(match['Date'],match['Time (MSK)']))
    matches['Datetime'] = dt
    matches = matches.sort_values(by='Datetime')
    matches = matches.drop('Datetime', axis=1)
    
    for country in c_sorted: 
        for key in Flags.keys():
            if country == key:
                country = Flags[key]
                break
        match_country = group_country.get_group(country)
        group_league = match_country.groupby(['Tournament'])
        for league in set(match_country['Tournament']):
            message_counter = 0
            message = ''
            length_message = ''
            countryname = ''
            if country == '🇷🇺':
                countryname = 'Russia'
            if country == '🏴󠁧󠁢󠁥󠁮󠁧󠁿':
                countryname = 'England'
            
            en_league = league
            for key in En_Leagues.keys():
                if league == key:
                    en_league = En_Leagues[key]
                    break
            cl = countryname + str(en_league)
            cl = cl.replace(' ','')
            try:
                photo = open(folder + 'logos/' + cl + '.png', 'rb')
            except:
                photo = open(folder + 'logos/default.png', 'rb')

            match_league = group_league.get_group(league)
             
            for index, match in match_league.iterrows(): 
                match_df.loc[0] = match
                match_bet = MatchBet(match_df)
                message_match = ''
                message_match = match_bet[0]

                length_message_match = ''
                length_message_match = match_bet[2]

                good_bets = match_bet[1]

                if (message_counter == 0) & (len(length_message) + len(length_message_match) > telegram_limit_media):
                    message = message.rstrip()
                    SendPhoto(photo, message)
                    message = message_match
                    length_message = length_message_match
                    message_counter = 1
                elif len(length_message) + len(length_message_match) > telegram_limit:
                    message = message.rstrip()
                    SendMessage(message)
                    message = message_match
                    length_message = length_message_match
                else:
                    message += message_match
                    length_message += length_message_match
                
                if not good_bets.empty:
                    best_bets = pd.concat([good_bets, best_bets], ignore_index=True, axis=0)
                    
            if message.rstrip() != '':
                if (message_counter == 0):
                    SendPhoto(photo, message)
                    message_counter = 1
                else:
                    SendMessage(message)
    return best_bets