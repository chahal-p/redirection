import os
import logging
from datetime import timedelta
from flask import Flask
from flask_restful import Api
from controllers import RedirectionController
from redis import Redis
from pymongo import MongoClient
from common.cache.redis import RedisCache
from common import AADToken
from common.key_vault import KeyVaultSecret
from common.databases.nosql.mongodb import MongoDBDatabase, CollectionOperations
import config


app = Flask(__name__)
api = Api(app)

logger = logging.getLogger('werkzeug')
logger.setLevel(logging.INFO)

redis_client = Redis(host='redis-service.default', port=6379)

#============================== AAD Token ==========================================
AAD_IDENTITY_TENANT = os.environ['AAD_IDENTITY_TENANT']
AAD_IDENTITY_CLIENTID = os.environ['AAD_IDENTITY_CLIENTID']
AAD_IDENTITY_SECRET = os.environ['AAD_IDENTITY_SECRET']
key_vault_token = AADToken(
    AAD_IDENTITY_CLIENTID,
    AAD_IDENTITY_SECRET,
    'https://vault.azure.net',
    tenant=AAD_IDENTITY_TENANT)
#===================================================================================

#============================== Create Database handlers ============================
secret = KeyVaultSecret(
    config.KEY_VALUT_NAME,
    config.MONGO_DB_CONNECTION_STRING_NAME,
    key_vault_token)

mongodb_conn_str = secret.get()

mongo_client = MongoClient(mongodb_conn_str)

db = MongoDBDatabase(logger, config.DATEBASE_NAME, mongo_client)

url_mapping_collection = CollectionOperations(logger, 'urlMapping', db)

#===================================================================================

#============================== Register controllers ===============================
cache = RedisCache(redis_client, timedelta(days=1), 'redirection-mapping-cache')

api.add_resource(RedirectionController, '/<path>', endpoint="redirection", resource_class_args=(logger, cache, url_mapping_collection))

#===================================================================================

if __name__ == '__main__':
    app.run(debug=False, host="0.0.0.0", port=5000)