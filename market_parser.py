import requests
from TelegramBot import TelegramBot
from datetime import datetime
import json
from pathlib import Path


bot = TelegramBot('config.json')

start_message = '''
🇺🇸Hello! ✌️\nCheck market profit by entering phrase: [skin name], [price]. \nUse \'.\' in float numbers. Fees (sell, transfers) included
\n🇷🇺Привет! ✌️\nПроверяй профитность с помощью фразы: [название скина], [цена]. \nИспользуй \'.\' для цен с плавующей точкой. Комиссии (продажа, переводы) включены
'''

error_message = '''
🇺🇸Wrong price\n\nUse \'.\' in float numbers
🇷🇺Неверно введнная цена\n\n Используй \'.\' для цен с плавующей точкой
'''

help_message = '''
🇺🇸Check market profit by entering phrase: [skin name], [price]. \nUse \'.\' in float numbers
🇷🇺\nПроверяй профитность с помощью фразы: [название скина], [цена]. \nИспользуй \'.\' для цен с плавующей точкой
'''

config = open(Path.cwd() / 'config.json', 'r')
dmarket_coockie = json.load(config)['dmarket_coockie']

def check_dmarket_price(name, price):
	fee = 0.88
	session = requests.Session()
	resp = session.get('https://api.dmarket.com/exchange/v1/offers-by-title?Title={}&Limit=100'.format(name), 
							cookies={'dm-trade-token': dmarket_coockie})
	if resp.status_code == 200:
		available_prices = list()
		json_data = json.loads(resp.text)
		objects = json_data['objects']
		for obj in objects:
			if obj.get('discount') != 0:
				d_price = float(obj.get('price').get('USD')) / 100
				if price * fee > d_price:
					available_prices.append(price * fee / d_price)
		return available_prices
	raise ValueError('Dmarket problem')
			


def price_validator(price):
	for i in price:
		if i not in '.1234567890':
			return False
	return True


pool = dict()
started = True
while 1:
	chat_id, message, date = bot.get_last_message()
	if message is not None:
		message = message.split(',')
		if chat_id not in pool.keys() or pool.get(chat_id) != date:
			pool[chat_id] = date
			if not started:
				if len(message) == 2:
					price = message[1].strip()
					price_valid = price_validator(price)
					if price_valid:
						name, price = message[0], float(message[1])
						prices_dm = check_dmarket_price(name, price)
						prices_dm.sort()
						if prices_dm:
							bot.send_message(chat_id, str(prices_dm[0])[0:4])
							
					else:
						bot.send_message(chat_id, error_message)
				else:
					if message[0] == '/s' or message[0] == '/start':
						bot.send_message(chat_id, start_message)
					elif message[0] == '/help':
						bot.send_message(chat_id, help_message)
			else:
				started = False


