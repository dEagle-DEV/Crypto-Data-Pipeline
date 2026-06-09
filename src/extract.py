"""Extract stage of the pipeline: fetches market data from the CoinGecko API."""

import requests


def get_coin_data():
	"""Fetch the top coins by market cap from CoinGecko.

	Returns:
		A list of coin records (dicts) on success, or None if the request fails.
	"""
	# Request the top 10 coins (page 1) priced in USD, ordered by market cap.
	url = 'https://api.coingecko.com/api/v3/coins/markets?vs_currency=usd&order=market_cap_desc&per_page=10&page=1'

	try:
		response = requests.get(url, timeout=10)
		# Raise an exception for HTTP error responses (4xx/5xx).
		response.raise_for_status()
		return response.json()

	except requests.exceptions.RequestException as e:
		# Covers connection errors, timeouts, and bad HTTP status codes.
		print(f'Failed to fetch coin data from API: {e}')
		return None

def main():
	# Standalone entry point for testing the extract step on its own.
	crypto_coins=get_coin_data()

	if crypto_coins:
		print(f'Successfully fetched {len(crypto_coins)} coins from the API.')
		print(crypto_coins)

	else:
		print('Failed to fetch coin data from API.')

if __name__ == '__main__':
	main()

		
