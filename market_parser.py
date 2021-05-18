import requests
from TelegramBot import TelegramBot
from datetime import datetime
import json


bot = TelegramBot('config.json')


def check_dmarket_price(name, price):
	fee = 0.88
	session = requests.Session()
	resp = session.get('https://api.dmarket.com/exchange/v1/offers-by-title?Title={}&Limit=100'.format(name), 
							cookies={'dm-trade-token': 'eyJhbGciOiJFUzI1NiIsInR5cCI6IkpXVCJ9.eyJqdGkiOiIxZmNlMTQ2ZC0wNTFkLTRkZjEtODI4Mi0zNWE1YzE0NTg1NTAiLCJleHAiOjE2MjM4MTA2MTQsImlhdCI6MTYyMTIxODYxNCwic2lkIjoiMjQzMjA2NWUtOTYwZS00MzkxLWI4ZjQtZmViMTBiNTUzZTEwIiwidHlwIjoiYWNjZXNzIiwiaWQiOiIyMzFhYjRmNS1jOTNlLTQ2NTgtYmViOC1kZTExMzIyMjU5NTciLCJwdmQiOiJtcCIsInBydCI6IjIxMDUiLCJhdHRyaWJ1dGVzIjp7ImFjY291bnRfaWQiOiI5M2UzODJkOC1lMzhhLTQ2MTItYmI4NC1iZDBlMDUyZDM5OTAiLCJ3YWxsZXRfaWQiOiJjNTAwNjk1OGRkZGQwYjBmMTU3OTQ0MTdhZDExYTU0YjA1ZDVjM2M4ZWNkMWQ0ZTQ0NTg4MmI2NGU3OTI0OGJkIn19.UDD1ATkvM1d9PYxBjoAjK0wFrPJYDcHxUMHDP3vORbFLLkgw-9IDlT_Bu__EBj7CmLHynYXfbJf__PXA9Y2GLg'})
	if resp.status_code == 200:
		available_prices = list()
		json_data = json.loads(resp.text)
		objects = json_data['objects']
		for obj in objects:
			if obj.get('discount') != 0:
				d_price = float(obj.get('price').get('USD')) / 100
				if price * fee > d_price:
					available_prices.append(price / d_price)
		return available_prices
	raise ValueError('Dmarket problem')
			


def price_validator(price):
	for i in price:
		if i not in '.1234567890':
			return False
	return True

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
						k = 0
						for i in prices_dm:
							bot.send_message(chat_id, str(i))
							k += 1
							if k == 3:
								break
					else:
						bot.send_message(chat_id, error_message)
				else:
					if message[0] == '/s' or message[0] == '/start':
						bot.send_message(chat_id, start_message)
					elif message[0] == '/help':
						bot.send_message(chat_id, help_message)
			else:
				started = False


