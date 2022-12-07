from selenium import webdriver
from bs4 import BeautifulSoup 
import time
from src.config import folder

winline_url = 'https://winline.ru/'

def WinlineOdds(home_name, away_name):
    driver = webdriver.Firefox(executable_path = folder + 'geckodriver',service_log_path = folder + 'geckodriver.log')
    driver.get('https://winline.ru/')

    search = driver.find_element(by='name', value = 'searchForm.find')
    search.send_keys(home_name + ' ' + away_name)
    time.sleep(5)
    match = driver.find_element(by='class name', value = 'commands')
    match.click()
    time.sleep(5)

    while(True):
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        table = soup.find('div',attrs={'class':'result-table__row'})
        if table is not None:
            odds_table = table.find_all('span',attrs={'class':'result-table__count'})
            if odds_table is not None:
                break
        driver.refresh()

    driver.close()

    table = soup.find('div',attrs={'class':'result-table__row'})
    odds_table = table.find_all('span',attrs={'class':'result-table__count'})
    odds = []
    for row in odds_table:
        odds.append(float(row.text))
    return odds