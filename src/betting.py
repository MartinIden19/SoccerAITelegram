import pandas as pd

def GoodBets(data):
    good_bets = pd.DataFrame(columns=data.columns)
    res = pd.DataFrame(columns=data.columns)
    prediction = []
    for index, bet in data.iterrows():
        match_prediction = []

        if (bet['HTMatches'] > 3) & (bet['ATMatches'] > 3):

            # HOME
            if 1.53 < bet.AvgCH <= 1.67:
                if Home(bet, 1.06, 0.99, 1.3, 0):
                    good_bets.loc[len(good_bets)] = bet
                    match_prediction.append('Home')
            elif 1.67 < bet.AvgCH <= 2.12:
                continue
            elif 2.12 < bet.AvgCH <= 3.16:
                if Home(bet, 0.98, 1.01, 1, 1):
                    good_bets.loc[len(good_bets)] = bet
                    match_prediction.append('Home')
            elif 3.16 < bet.AvgCH <= 4.2:
                if Home(bet, 1.05, 0.99, 0.6, 0.4):
                    good_bets.loc[len(good_bets)] = bet
                    match_prediction.append('Home')
                    
            # DRAW
            if 2 < bet.AvgCD <= 3.2:
                if Draw(bet, 1.14, 1.01, 0.7, 0.8):
                    good_bets.loc[len(good_bets)] = bet
                    match_prediction.append('Draw')
            elif 3.2 < bet.AvgCD <= 3.5:
                if Draw(bet, 0.89, 0.99, 0.5, 0.8):
                    good_bets.loc[len(good_bets)] = bet
                    match_prediction.append('Draw')
            elif 3.5 < bet.AvgCD <= 3.95:
                if Draw(bet, 0.97, 0.98, 1.4, 0.6):
                    good_bets.loc[len(good_bets)] = bet
                    match_prediction.append('Draw')
            elif 3.95 < bet.AvgCD <= 5.4:
                if Draw(bet, 0.8, 0.97, 0.2, 0.5):
                    good_bets.loc[len(good_bets)] = bet
                    match_prediction.append('Draw')
                                        
            # AWAY
            if 1.4 < bet.AvgCA <= 1.46:
                if Away(bet, 1.3, 1.05, 3, 1.5):
                    good_bets.loc[len(good_bets)] = bet
                    match_prediction.append('Away')
            elif 1.46 < bet.AvgCA <= 2:
                if Away(bet, 1.1, 1, 0.3, 0.6):
                    good_bets.loc[len(good_bets)] = bet
                    match_prediction.append('Away')
            elif 2 < bet.AvgCA <= 3.16:
                if Away(bet, 1.03, 1.03, 2, 1.5):
                    good_bets.loc[len(good_bets)] = bet
                    match_prediction.append('Away')
            elif 3.16 < bet.AvgCA <= 3.7:
                if Away(bet, 1.3, 0.99, 0.5, 1.5):
                    good_bets.loc[len(good_bets)] = bet
                    match_prediction.append('Away')
            elif 3.7 < bet.AvgCA <= 4.2:
                if Away(bet, 1.02, 0.95, 0.5, 1.2):
                    good_bets.loc[len(good_bets)] = bet
                    match_prediction.append('Away')

            # HomeDraw
            elif 1.35 < bet.DoubleChanceHD <= 1.36:
                if HomeDraw(bet, 1.1, 0.99, 0.8, 0.7):
                    good_bets.loc[len(good_bets)] = bet
                    match_prediction.append('Home or Draw')
            elif 1.36 < bet.DoubleChanceHD <= 1.5:
                if HomeDraw(bet, 0.99, 0.98, 1.3, 0.9):
                    good_bets.loc[len(good_bets)] = bet
                    match_prediction.append('Home or Draw')
            elif 1.5 < bet.DoubleChanceHD <= 1.63:
                if HomeDraw(bet, 0.94, 0.99, 0.5, 0.5):
                    good_bets.loc[len(good_bets)] = bet
                    match_prediction.append('Home or Draw')
            elif 1.63 < bet.DoubleChanceHD <= 1.9:
                if HomeDraw(bet, 1, 0.99, 0.3, 0.2):
                    good_bets.loc[len(good_bets)] = bet
                    match_prediction.append('Home or Draw')

            # AwayDraw
            if 1.25 < bet.DoubleChanceAD <= 1.36:
                if AwayDraw(bet, 1.3, 1.04, 1.2, 1.5):
                    good_bets.loc[len(good_bets)] = bet
                    match_prediction.append('Away or Draw')
            elif 1.36 < bet.DoubleChanceAD <= 1.5:
                if AwayDraw(bet, 1.3, 1.06, 1.9, 1.2):
                    good_bets.loc[len(good_bets)] = bet
                    match_prediction.append('Away or Draw')

            ########################################################
                
            prediction = prediction + match_prediction

    good_bets['Prediction'] = prediction
    return good_bets

def Home(bet, bookie, rating, points, goals):
    if (bet.HomeProb/bet.AvgCH < bookie) & (bet.HTRating / bet.ATRating > rating) & (bet.HTPoints5 /(bet.ATPoints5 + 0.0001) > points) & ((bet.HTMGS / (bet.HTMGC + 0.0001))/(bet.ATMGS / (bet.ATMGC + 0.0001) + 0.0001) > goals):
        return True
    return False

def Draw(bet, bookie, rating, points, goals):
    if (bet.DrawProb/bet.AvgCD < bookie) & (bet.HTRating / bet.ATRating > rating) & (bet.HTPoints5 /(bet.ATPoints5 + 0.0001) > points) & ((bet.HTMGS / (bet.HTMGC + 0.0001))/(bet.ATMGS / (bet.ATMGC + 0.0001) + 0.0001) > goals):
        return True  
    return False

def Away(bet, bookie, rating, points, goals):
    if (bet.AwayProb/bet.AvgCA < bookie) & (bet.ATRating / bet.HTRating > rating) & (bet.ATPoints5 /(bet.HTPoints5 + 0.0001) > points) & ((bet.ATMGS / (bet.ATMGC + 0.0001))/(bet.HTMGS / (bet.HTMGC + 0.0001) + 0.0001) > goals):
        return True
    return False

def HomeDraw(bet, bookie, rating, points, goals):
    if (bet.HD_Prob/bet.DoubleChanceHD < bookie) & (bet.HTRating / bet.ATRating > rating) & (bet.HTPoints5 /(bet.ATPoints5 + 0.0001) > points) & ((bet.HTMGS / (bet.HTMGC + 0.0001))/(bet.ATMGS / (bet.ATMGC + 0.0001) + 0.0001) > goals):
        return True
    return False

def HomeAway(bet, bookie, rating, points, goals):
    if (bet.HA_Prob/bet.DoubleChanceHA < bookie) & (bet.HTRating / bet.ATRating > rating) & (bet.HTPoints5 /(bet.ATPoints5 + 0.0001) > points) & ((bet.HTMGS / (bet.HTMGC + 0.0001))/(bet.ATMGS / (bet.ATMGC + 0.0001) + 0.0001) > goals):
        return True
    return False

def AwayDraw(bet, bookie, rating, points, goals):
    if (bet.AD_Prob/bet.DoubleChanceAD < bookie) & (bet.ATRating / bet.HTRating > rating) & (bet.ATPoints5 /(bet.HTPoints5 + 0.0001) > points) & ((bet.ATMGS / (bet.ATMGC + 0.0001))/(bet.HTMGS / (bet.HTMGC + 0.0001) + 0.0001) > goals):
        return True
    return False