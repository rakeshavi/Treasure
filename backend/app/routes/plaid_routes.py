from flask import Blueprint, jsonify, request, current_app
from flask_cors import cross_origin
from app.services.plaid_service import get_plaid_service

plaid_bp = Blueprint('plaid', __name__)

@plaid_bp.route('/create_link_token', methods=['POST'])
@cross_origin()
def create_link_token():
    current_app.logger.info('Attempting to create link token')
    try:
        plaid_service = get_plaid_service()
        token = plaid_service.create_link_token()
        current_app.logger.info('Link token created successfully')
        return jsonify({"link_token": token}), 200
    except Exception as e:
        current_app.logger.error(f'Error creating link token: {str(e)}')
        return jsonify({"error": str(e)}), 500

@plaid_bp.route('/set_access_token', methods=['POST'])
@cross_origin()
def set_access_token():
    current_app.logger.info('Attempting to set access token')
    try:
        plaid_service = get_plaid_service()
        public_token = request.json['public_token']
        access_token = plaid_service.exchange_public_token(public_token)
        current_app.logger.info('Access token set successfully')
        return jsonify({"access_token": access_token}), 200
    except Exception as e:
        current_app.logger.error(f'Error setting access token: {str(e)}')
        return jsonify({"error": str(e)}), 500

@plaid_bp.route('/transactions', methods=['GET'])
@cross_origin()
def get_transactions():
    current_app.logger.info('Attempting to get transactions')
    try:
        plaid_service = get_plaid_service()
        access_token = request.args.get('access_token')
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        transactions = plaid_service.get_transactions(access_token, start_date, end_date)
        current_app.logger.info(f'Successfully retrieved {len(transactions)} transactions')
        return jsonify(transactions), 200
    except Exception as e:
        current_app.logger.error(f'Error getting transactions: {str(e)}')
        return jsonify({"error": str(e)}), 500