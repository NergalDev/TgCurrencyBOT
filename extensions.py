"""Currency Bot Extra"""

from confmaker import config
from redis import StrictRedis
from redis_cache import RedisCache
import requests
import logging


# Setup Logger
logging.basicConfig(filename=config['logfile'], encoding='utf-8', level=logging.INFO)
logger = logging.getLogger('CurrencyBot')


# Setup Redis Cache
client = StrictRedis(host=config['redis']['host'],
                     port=config['redis']['port'],
                     password=config['redis']['pwd'],
                     decode_responses=True)
cache = RedisCache(redis_client=client, prefix='tgbot')


# Exceptions


class GeneralFetchError(Exception):
    pass


class NetworkFetchError(GeneralFetchError):
    pass


class ConvertError(GeneralFetchError):
    pass


# Classes


class Converter:
    """Coingate API"""

    @staticmethod
    @cache.cache(ttl=config['cache']['ttl'])
    def get_rate(from_sym='USD', to_sym='EUR'):
        """Get Conversion rate from coingate API"""
        r = requests.get(f'https://api.coingate.com/v2/rates/merchant/{from_sym}/{to_sym}')

        # If anything except HTTP OK raise error
        if r.status_code != 200:
            raise NetworkFetchError

        if r.content:
            return float(r.content)
        else:
            # Cannot Convert selected symbols
            raise ConvertError(f'Cannot convert from {from_sym} to {to_sym}')

    @staticmethod
    def get_conv(amount=1.0, from_sym='USD', to_sym='EUR'):
        """Multiply Conversion rate on amount"""
        result = abs(float(amount)) * Converter.get_rate(from_sym, to_sym)
        return round(result, 3)
