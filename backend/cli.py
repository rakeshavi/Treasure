import click
from app import create_app
from app.services.plaid_service import get_plaid_service
import logging
import sys

app = create_app()

# Configure logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s',
                    stream=sys.stdout)
logger = logging.getLogger(__name__)

@click.group()
def cli():
    pass

@cli.command()
def link_account():
    """Simulate linking an account and fetch transactions"""
    with app.app_context():
        plaid_service = get_plaid_service()
        
        try:
            # Step 1: Create link token
            logger.info("Creating link token")
            link_token = plaid_service.create_link_token()
            logger.info(f"Link token created: {link_token}")
            
            logger.info("Simulating account linking process")
            click.echo("\nIn a real application, you would now use this link token with Plaid Link.")
            click.echo("For this CLI simulation, we'll create a sandbox public token.")
            click.echo("\nPress Enter to simulate successful account linking...")
            input()
            
            # Step 2: Create a sandbox public token
            logger.info("Creating sandbox public token")
            public_token = plaid_service.create_sandbox_public_token()
            logger.info(f"Sandbox public token created: {public_token}")
            
            # Step 3: Exchange public token for access token
            logger.info("Exchanging public token for access token")
            access_token = plaid_service.exchange_public_token(public_token)
            logger.info("Access token received")

            # Step 3.5: 
            item_status = plaid_service.get_item_status(access_token)
            logger.info(f"Item status: {item_status['status']}")
        
            # Step 4: Fetch transactions
            start_date = '2023-01-01'
            end_date = '2023-07-22'
            logger.info(f"Attempting to fetch transactions from {start_date} to {end_date}")
            try:
                transactions = plaid_service.get_transactions(access_token, start_date, end_date)
                logger.info(f"Successfully fetched {len(transactions)} transactions")
                if transactions:
                    for transaction in transactions:
                        logger.info(f"Transaction: {transaction['date']} - {transaction['name']}: ${transaction['amount']}")
                else:
                    logger.warning("No transactions were fetched.")
            except Exception as e:
                logger.error(f"Failed to fetch transactions: {str(e)}")
        except Exception as e:
            logger.exception(f"An error occurred: {str(e)}")
            raise

if __name__ == '__main__':
    cli()