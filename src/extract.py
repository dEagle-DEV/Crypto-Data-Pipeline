"""Extract stage of the pipeline: fetches market data from the CoinGecko API."""

import requests
import logging
logger = logging.getLogger(__name__)
from tenacity import retry, stop_after_attempt,wait_exponential,before_sleep_log,retry_if_exception_type

@retry(
		stop=stop_after_attempt(4),
		wait=wait_exponential(multiplier=1, min=1, max=4),
		before_sleep=before_sleep_log(logger, logging.WARNING),
		retry=retry_if_exception_type(requests.exceptions.RequestException)
)
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
		logger.error(f'Failed to fetch coin data from API: {e}')
		raise

def main():
	try:
		crypto_coins=get_coin_data()
	
	except Exception as e:
		logger.error(f'All retries exhausted, giving up: {e}')
		return

	if crypto_coins:
		logger.info(f'Successfully fetched {len(crypto_coins)} coins from the API.')
		print(crypto_coins)

	else:
		logger.error('Failed to fetch coin data from API.')

if __name__ == '__main__':
	main()

		
