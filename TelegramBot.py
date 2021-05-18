import json
import requests
import asyncio
from pathlib import Path

class TelegramBot:

	def __init__(self, config_path, offset=0):
		config = open(Path.cwd() / config_path, 'r')
		token = json.load(config)['token']
		self.token = token
		self.offset = offset


	def get_update_page(self):
		link = 'https://api.telegram.org/bot{}/getUpdates?offset={}'
		update_page = requests.get(link.format(self.token, self.offset))
		if update_page.status_code == 200:
			data = json.loads(update_page.text)
			return data
		return None

	def get_last_message(self, last_date=None):

		'''		Returning chat id, last message, message date	'''

		data = self.get_update_page()
		if data is not None:
			if data.get('ok') == True:
				self.offset = data.get('update_id')
				result = data.get('result')
				message = result[-1].get('message')
				date = message.get('date')
				if date != last_date:
					return message.get('chat').get('id'), message.get('text'), date
		raise ValueError('API page couldn\'t be loaded')


	def send_message(self, chat_id, message):

		'''		Returning true if message successfuly delivered		'''

		link = 'https://api.telegram.org/bot{}/sendMessage?chat_id={}&text={}'.format(self.token, chat_id, message)
		response = requests.get(link)
		if response.status_code == 200:
			return True
		return False













