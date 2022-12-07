import pandas as pd
import datetime
import telepot
from src.config import folder, telegram_limit_results, telegram_limit_media
from src.functions import to_datetime
from src.dictionaries import RussianNames, Emoji_Countries

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

def BetResult(match):
    if match.Result == 'Returned':
        return 1
    elif (match.Prediction == 'Home') & (match.Result == 'Home'):
        return match.AvgCH
    elif (match.Prediction == 'Draw') & (match.Result == 'Draw'):
        return match.AvgCD
    elif (match.Prediction == 'Away') & (match.Result == 'Away'):
        return match.AvgCA
    elif (match.Prediction == 'Home or Draw') & ((match.Result == 'Home') | (match.Result == 'Draw')):
        return match.DoubleChanceHD
    elif (match.Prediction == 'Home or Away') & ((match.Result == 'Home') | (match.Result == 'Away')):
        return match.DoubleChanceHA
    elif (match.Prediction == 'Away or Draw') & ((match.Result == 'Away') | (match.Result == 'Draw')):
        return match.DoubleChanceAD
    else:
        return 0

def PreviousBets():
    bets = pd.read_excel(folder + 'data/bets.xlsx')
    data = pd.DataFrame(columns=bets.columns)
    today = datetime.datetime.now()
    today = today.replace(hour=7, minute = 0, second=0)
    yesterday = today - datetime.timedelta(days=1)
    for index, match in bets.iterrows():
        dt = to_datetime(match['Date'],match['Time (MSK)'])
        if (dt > yesterday) & (dt < today):
            data.loc[len(data)] = match
    return data

def BetEfficiencyRU(data):
    data = data.replace({'Country' : Emoji_Countries})
    data = data.sort_values('Country')
    message = ''
    #message = '📈 Итоги прошедшего игрового дня 📉\n\n'
    photo = open(folder + 'images/results.png', 'rb')
    coef_sum = 0
    #data = data.replace({'HomeTeam' : RussianNames, 'AwayTeam' : RussianNames})
    message_counter = 0
    for index, bet in data.iterrows():
        coef = BetResult(bet)
        if coef > 1:
            res = '🟢'
            sign = '⬆️ +'
            coef = (coef - 1) * 1000
        elif coef == 0:
            res = '🔴'
            sign = '⬇️ '
            coef = (coef - 1) * 1000
        elif coef == 1:
            coef = 0
            sign = '🔄 +'
            res = '⚪'
        coef_sum += coef
        if bet.Prediction == 'Home':
            prediction = bet.HomeTeam
        elif bet.Prediction == 'Draw':
            prediction = 'Ничья между ' + bet.HomeTeam + ' и ' + bet.AwayTeam
        elif bet.Prediction == 'Away':
            prediction = bet.AwayTeam
        elif bet.Prediction == 'Home or Draw':
            prediction = bet.HomeTeam + ' или ничья'
        elif bet.Prediction == 'Home or Away':
            prediction = bet.HomeTeam + ' или ' + bet.AwayTeam
        elif bet.Prediction == 'Away or Draw':
            prediction = bet.AwayTeam + ' или ничья'
        
        message_match = res + ' ' + prediction + ' ' + sign + str(int(coef)) + '₽\n'

        if (message_counter == 0) & (len(message) + len(message_match) > telegram_limit_media):
            message = message.rstrip()
            SendPhoto(photo, message)
            message = message_match
            message_counter = 1
        
        if len(message) + len(message_match) > telegram_limit_results:
            message = message.rstrip()
            SendMessage(message)
            message = message_match
        else:
            message += message_match

    if coef_sum > 0:
        res_sign = '💹 '
        total_sign = '📈 +'
        mes = 'Прибыль за прошедший игровой день '
    elif coef_sum == 0:
        res_sign = '🔄'
        total_sign = '🔄 +'
        mes = 'Прибыль за прошедший игровой день '
    elif coef_sum < 0:
        total_sign = '📉 '
        res_sign = '〽️ '
        mes = 'Убыток за прошедший игровой день '
    message += '\n' + '💶 ' + mes + total_sign + str(int(coef_sum)) + '₽'
    message += '\n' + res_sign + 'ROI за прошедший игровой день ' + total_sign + str(int(coef_sum/10/len(data))) + '%'

    if (message_counter == 0):
        SendPhoto(photo, message)
        message_counter = 1
    else:
        SendMessage(message)