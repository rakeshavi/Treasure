from datetime import datetime
import uuid
import logging
import time

import plaid
from plaid.api import plaid_api
from plaid.model.link_token_create_request import LinkTokenCreateRequest
from plaid.model.link_token_create_request_user import LinkTokenCreateRequestUser
from plaid.model.products import Products
from plaid.model.country_code import CountryCode
from plaid.model.sandbox_public_token_create_request import SandboxPublicTokenCreateRequest
from plaid.model.item_public_token_exchange_request import ItemPublicTokenExchangeRequest
from plaid.model.transactions_get_request import TransactionsGetRequest
from plaid.model.transactions_get_request_options import TransactionsGetRequestOptions
from plaid.model.item_get_request import ItemGetRequest
from plaid.exceptions import ApiException
from flask import current_app

logger = logging.getLogger(__name__)

class PlaidService:
    def __init__(self):
        logger.info("Initializing PlaidService")
        configuration = plaid.Configuration(
            host=plaid.Environment.Sandbox,
            api_key={
                'clientId': current_app.config['PLAID_CLIENT_ID'],
                'secret': current_app.config['PLAID_SECRET'],
            }
        )
        self.client = plaid_api.PlaidApi(plaid.ApiClient(configuration))
        logger.info("PlaidService initialized")

    def create_link_token(self):
        logger.info("Creating link token")
        request = LinkTokenCreateRequest(
            products=[Products("transactions")],
            client_name="Treasure App",
            country_codes=[CountryCode('US')],
            language='en',
            user=LinkTokenCreateRequestUser(
                client_user_id=str(uuid.uuid4())
            )
        )
        response = self.client.link_token_create(request)
        logger.info("Link token created")
        return response['link_token']

    def create_sandbox_public_token(self):
        logger.info("Creating sandbox public token")
        request = SandboxPublicTokenCreateRequest(
            institution_id="ins_109508",
            initial_products=[Products("transactions")]
        )
        response = self.client.sandbox_public_token_create(request)
        logger.info("Sandbox public token created")
        return response['public_token']

    def exchange_public_token(self, public_token):
        logger.info("Exchanging public token for access token")
        request = ItemPublicTokenExchangeRequest(public_token=public_token)
        response = self.client.item_public_token_exchange(request)
        logger.info("Public token exchanged for access token")
        return response['access_token']

    def get_item_status(self, access_token):
        request = ItemGetRequest(access_token=access_token)
        response = self.client.item_get(request)
        return response['item']

    def get_transactions(self, access_token, start_date, end_date, max_retries=5, delay=2):
        logger.info(f"Fetching transactions from {start_date} to {end_date}")
        
        # Convert string dates to date objects
        start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
        end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
        
        request = TransactionsGetRequest(
            access_token=access_token,
            start_date=start_date,
            end_date=end_date,
            options=TransactionsGetRequestOptions()
        )

        for attempt in range(max_retries):
            try:
                response = self.client.transactions_get(request)
                transactions = response['transactions']
                if not transactions:
                    raise Exception("PRODUCT_NOT_READY")
                logger.info(f"Fetched {len(transactions)} transactions")
                return transactions
            except Exception as e:
                if "PRODUCT_NOT_READY" in str(e):
                    logger.warning(f"Transactions not ready, retrying in {delay} seconds (attempt {attempt + 1}/{max_retries})")
                    time.sleep(delay)
                    delay *= 2  # Exponential backoff
                else:
                    raise

        logger.error("Max retries reached, unable to fetch transactions")
        raise Exception("Unable to fetch transactions after maximum retries")
    
    # Synchronous mechanism to fetch transactions. Plaid sometime fails to do this. And throws a "PRODUCT_NOT_READY" error.
    # Therefore, we're going to use a polling approch for the same
    def get_transactions_sync(self, access_token, start_date, end_date):
        logger.info(f"Fetching transactions from {start_date} to {end_date}")
        
        # Convert string dates to date objects
        start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
        end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
        
        request = TransactionsGetRequest(
            access_token=access_token,
            start_date=start_date,
            end_date=end_date,
            options=TransactionsGetRequestOptions()
        )
        response = self.client.transactions_get(request)
        logger.info(f"Fetched {len(response['transactions'])} transactions")
        return response['transactions']

def get_plaid_service():
    return PlaidService()