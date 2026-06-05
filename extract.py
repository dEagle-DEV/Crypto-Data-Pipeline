import requests
def get_coin_data():
	url = 'https://api.coingecko.com/api/v3/coins/markets?vs_currency=usd'
	
	try:
		#Make a GET request to the API endpoint using requests.get()
		response = requests.get(url)
		if response.status_code == 200:
			crypto_coins = response.json()
			return crypto_coins
		else:
			print('Error:', response.status_code)
			return None
	except requests.exceptions.RequestException as e:
		print('Error:', e)
		return None
	
def main():
	crypto_coins=get_coin_data()

	if crypto_coins:
		print('Here is your Coin Data')
		print(crypto_coins)

	else:
		print('Failed to fetch Coin Data from API.')

if __name__ == '__main__':
	main()

		
