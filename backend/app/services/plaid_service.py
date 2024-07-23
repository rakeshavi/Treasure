import plaid
from plaid.api import plaid_api
from plaid.model.link_token_create_request import LinkTokenCreateRequest
from plaid.model.link_token_create_request_user import LinkTokenCreateRequestUser
from plaid.model.products import Products
from plaid.model.country_code import CountryCode
from plaid.model.item_public_token_exchange_request import ItemPublicTokenExchangeRequest
from plaid.model.transactions_get_request import TransactionsGetRequest
from plaid.model.transactions_get_request_options import TransactionsGetRequestOptions
from flask import current_app
import datetime

class PlaidService:
    def __init__(self, client_id, secret):
        configuration = plaid.Configuration(
            host=plaid.Environment.Sandbox,
            api_key={
                'clientId': client_id,
                'secret': secret,
            }
        )
        self.client = plaid.ApiClient(configuration)
        self.api_client = plaid_api.PlaidApi(self.client)

    def create_link_token(self):
        request = LinkTokenCreateRequest(
            products=[Products('transactions')],
            client_name="Treasure",
            country_codes=[CountryCode('US')],
            language='en',
            user=LinkTokenCreateRequestUser(client_user_id='unique_user_id')
        )
        response = self.api_client.link_token_create(request)
        return response['link_token']

    def exchange_public_token(self, public_token):
        request = ItemPublicTokenExchangeRequest(public_token=public_token)
        response = self.api_client.item_public_token_exchange(request)
        return response['access_token']

    def get_transactions(self, access_token, start_date, end_date):
        request = TransactionsGetRequest(
            access_token=access_token,
            start_date=datetime.datetime.strptime(start_date, '%Y-%m-%d').date(),
            end_date=datetime.datetime.strptime(end_date, '%Y-%m-%d').date(),
            options=TransactionsGetRequestOptions()
        )
        response = self.api_client.transactions_get(request)
        return response['transactions']

def get_plaid_service():
    client_id = current_app.config['PLAID_CLIENT_ID']
    secret = current_app.config['PLAID_SECRET']
    return PlaidService(client_id, secret)