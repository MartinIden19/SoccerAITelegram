import pickle
folder = 'C:/Users/FerrariBoy/Desktop/SoccerAI/'

msk_delta = 3
ubuntu_delta = 0
time_stamp_eve = 16
time_stamp_mor = 21

telegram_limit = 3700
telegram_limit_results = 3700
telegram_limit_media = 850

whoscored_url = 'https://1xbet.whoscored.com'
preview_url = 'https://1xbet.whoscored.com/Previews'
top_facts_url = 'https://1xbet.whoscored.com/Betting/Facts'
winline_url = 'https://winline.ru/'

rf_ftr = pickle.load(open(folder + 'models/random_forest_ftr.sav', 'rb'))
rf_ftr_v2 = pickle.load(open(folder + 'models/random_forest_ftr_v2.sav', 'rb'))