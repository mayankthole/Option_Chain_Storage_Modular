from Dhan_Tradehull import Tradehull
import pandas as pd
import time
from datetime import datetime, timedelta
import os
import ssl
import certifi
import bisect
import traceback
import psycopg2
from psycopg2.extras import execute_values
from sqlalchemy import create_engine
import urllib.parse
from dotenv import load_dotenv
import logging
from logging.handlers import RotatingFileHandler
import sys
import signal

# Load environment variables
load_dotenv()

# Configure SSL context
ssl_context = ssl.create_default_context(cafile=certifi.where())
ssl._create_default_https_context = lambda: ssl_context

# Initialize Tradehull client with environment variables
client_code = os.getenv('DHAN_CLIENT_CODE')
token_id = os.getenv('DHAN_TOKEN_ID')
tsl = Tradehull(client_code, token_id)

# Database configuration from environment variables
DB_CONFIG = {
    'dbname': os.getenv('DB_NAME'),
    'user': os.getenv('DB_USER'),
    'password': os.getenv('DB_PASSWORD'),
    'host': os.getenv('DB_HOST'),
    'port': os.getenv('DB_PORT')
}

def get_db_connection():
    """Create a database connection"""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        return conn
    except Exception as e:
        print(f"Error connecting to database: {str(e)}")
        raise

def create_data_directory():
    """Create directories for storing option chain data"""
    try:
        base_dir = "option_chain_data"
        nifty_dir = os.path.join(base_dir, "NIFTY")
        banknifty_dir = os.path.join(base_dir, "BANKNIFTY")
        
        # Create directories if they don't exist
        for directory in [base_dir, nifty_dir, banknifty_dir]:
            if not os.path.exists(directory):
                os.makedirs(directory)
                print(f"Created directory: {directory}")
        
        return nifty_dir, banknifty_dir
    except Exception as e:
        print(f"Error creating directories: {str(e)}")
        print("Full error details:", e.__class__.__name__)
        print("Traceback:", traceback.format_exc())
        raise  # Re-raise the exception to handle it in the main function

def get_current_time():
    """Get current time in HH:MM:SS format"""
    return datetime.now().strftime("%H:%M:%S")

def get_next_minute_start():
    """Wait until the start of the next minute"""
    now = datetime.now()
    print(f"Starting at: {now.strftime('%H:%M:%S')}")

def round_to_minute(dt):
    return dt.replace(second=0, microsecond=0)

def save_option_chain_data(df, expiry_date, fetch_time, symbol):
    """Save option chain data to PostgreSQL database"""
    try:
        # Prepare the data for database insertion
        df['symbol'] = symbol
        df['expiry_date'] = expiry_date
        df['fetch_time'] = fetch_time
        
        # Rename columns to match database schema (using underscores instead of spaces)
        column_mapping = {
            'Spot Price': 'spot_price',
            'ATM Strike': 'atm_strike',
            'Strike Price': 'strike_price',
            'CE OI': 'ce_oi',
            'CE Chg in OI': 'ce_chg_in_oi',
            'CE Volume': 'ce_volume',
            'CE IV': 'ce_iv',
            'CE LTP': 'ce_ltp',
            'CE Bid Qty': 'ce_bid_qty',
            'CE Bid': 'ce_bid',
            'CE Ask': 'ce_ask',
            'CE Ask Qty': 'ce_ask_qty',
            'CE Delta': 'ce_delta',
            'CE Theta': 'ce_theta',
            'CE Gamma': 'ce_gamma',
            'CE Vega': 'ce_vega',
            'PE Bid Qty': 'pe_bid_qty',
            'PE Bid': 'pe_bid',
            'PE Ask': 'pe_ask',
            'PE Ask Qty': 'pe_ask_qty',
            'PE LTP': 'pe_ltp',
            'PE IV': 'pe_iv',
            'PE Volume': 'pe_volume',
            'PE Chg in OI': 'pe_chg_in_oi',
            'PE OI': 'pe_oi',
            'PE Delta': 'pe_delta',
            'PE Theta': 'pe_theta',
            'PE Gamma': 'pe_gamma',
            'PE Vega': 'pe_vega'
        }
        df = df.rename(columns=column_mapping)
        
        # Select table based on symbol
        table_name = f"option_chain.{symbol.lower()}_option_chain"
        
        # Connect to database
        conn = get_db_connection()
        cur = conn.cursor()
        
        # Prepare the data for insertion
        columns = df.columns.tolist()
        values = [tuple(x) for x in df.values]
        
        # Create the insert query
        insert_query = f"""
            INSERT INTO {table_name} ({', '.join(columns)})
            VALUES %s
        """
        
        # Execute the insert
        execute_values(cur, insert_query, values)
        
        # Commit the transaction
        conn.commit()
        print(f"Successfully inserted {len(df)} rows into {table_name}")
        
    except Exception as e:
        print(f"Error saving data to database: {str(e)}")
        print("Full error details:", e.__class__.__name__)
        print("Traceback:", traceback.format_exc())
        if 'conn' in locals():
            conn.rollback()
    finally:
        if 'cur' in locals():
            cur.close()
        if 'conn' in locals():
            conn.close()

def fetch_and_save_option_chain(underlying="NIFTY"):
    try:
        # First get the spot price using get_ltp_data
        ltp = tsl.get_ltp_data(names=underlying)
        spot_price = None
        if ltp and isinstance(ltp, dict):
            spot_price = ltp.get(underlying)
            print(f"Current {underlying} spot price: {spot_price}")
        
        if spot_price is None:
            print(f"Warning: Could not fetch {underlying} spot price")
            return

        # Set number of expiries based on underlying
        num_expiries = 3 if underlying == "BANKNIFTY" else 6
        print(f"Processing {num_expiries} expiries for {underlying}")

        # Fetch data for each expiry
        for expiry_index in range(num_expiries):
            try:
                # Get ATM strike for this expiry
                try:
                    ce_name, pe_name, atm_strike = tsl.ATM_Strike_Selection(
                        Underlying=underlying,
                        Expiry=expiry_index
                    )
                    print(f"\nATM Strike from API: {atm_strike}")
                except Exception as e:
                    print(f"ATM_Strike_Selection failed: {str(e)}")
                    if underlying == "NIFTY":
                        atm_strike = round(spot_price / 100) * 100
                    else:  # BANKNIFTY
                        atm_strike = round(spot_price / 1000) * 1000
                    print(f"Using fallback ATM Strike: {atm_strike}")
                    ce_name = f"{underlying} {expiry_index} {atm_strike} CALL"
                    pe_name = f"{underlying} {expiry_index} {atm_strike} PUT"
                
                # Extract expiry date
                expiry_date = None
                try:
                    parts = ce_name.split()
                    if len(parts) >= 4:
                        expiry_date = ' '.join(parts[1:3])
                except Exception as e:
                    print(f"Error parsing expiry date: {e}")
                    expiry_date = f"Expiry_{expiry_index}"
                
                print(f"\nProcessing {underlying} expiry: {expiry_date}")
                print(f"ATM Strike: {atm_strike}")
                
                # Add a small delay
                time.sleep(0.1)
                
                # Get option chain data
                option_chain = tsl.get_option_chain(
                    Underlying=underlying,
                    exchange="INDEX",
                    expiry=expiry_index,
                    num_strikes=50
                )
                
                if option_chain is not None and isinstance(option_chain, tuple) and len(option_chain) > 1:
                    metadata, df = option_chain
                    
                    # Add spot price and ATM strike
                    df.insert(0, 'Spot Price', spot_price)
                    df.insert(1, 'ATM Strike', atm_strike)
                    
                    # Add timestamp
                    current_time = datetime.now()
                    df['timestamp'] = round_to_minute(current_time).strftime('%H:%M:00')
                    
                    # Save to database
                    save_option_chain_data(
                        df, 
                        expiry_date, 
                        current_time.strftime('%Y-%m-%d %H:%M:%S'),
                        underlying
                    )
                    print(f"Data saved for {underlying} expiry: {expiry_date}")
                    print(f"Number of strikes saved: {len(df)}")
                else:
                    print(f"Failed to fetch option chain data for {underlying} expiry: {expiry_date}")
                    
            except Exception as e:
                print(f"Error processing {underlying} expiry index {expiry_index}: {str(e)}")
                print("Full error details:", e.__class__.__name__)
                print("Traceback:", traceback.format_exc())
                
    except Exception as e:
        print(f"Error occurred: {str(e)}")
        print("Full error details:", e.__class__.__name__)
        print("Traceback:", traceback.format_exc())

# Set up logging
def setup_logging():
    log_file = "option_chain.log"
    handler = RotatingFileHandler(log_file, maxBytes=10*1024*1024, backupCount=5)  # 10MB per file, 5 backups
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    logger.addHandler(handler)
    
    # Also log to console
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    return logger

# Create a global logger
logger = setup_logging()

def signal_handler(signum, frame):
    logger.info("Received signal to stop. Cleaning up...")
    sys.exit(0)

def main():
    # Set up signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    nifty_dir, banknifty_dir = create_data_directory()
    logger.info("Starting option chain data collection...")
    
    while True:
        try:
            current_time = datetime.now()
            current_time_str = current_time.strftime("%H:%M:%S")
            market_start = datetime.strptime("09:15:02", "%H:%M:%S").time()
            market_end = datetime.strptime("15:30:00", "%H:%M:%S").time()
            
            # Check if it's weekend
            if current_time.weekday() >= 5:  # 5 is Saturday, 6 is Sunday
                logger.info(f"Market closed: Weekend - {current_time_str}")
                # Sleep until next day
                next_day = current_time + timedelta(days=1)
                next_day = next_day.replace(hour=9, minute=15, second=2, microsecond=0)
                sleep_seconds = (next_day - current_time).total_seconds()
                logger.info(f"Sleeping until next trading day: {next_day.strftime('%Y-%m-%d %H:%M:%S')}")
                time.sleep(sleep_seconds)
                continue
            
            # If before market open, sleep until market open
            if current_time.time() < market_start:
                next_run = current_time.replace(hour=9, minute=15, second=2, microsecond=0)
                sleep_seconds = (next_run - current_time).total_seconds()
                logger.info(f"Market not open yet. Sleeping until market open: {next_run.strftime('%H:%M:%S')}")
                time.sleep(sleep_seconds)
                continue
            
            # If after market close, sleep until next trading day
            if current_time.time() > market_end:
                next_day = current_time + timedelta(days=1)
                next_day = next_day.replace(hour=9, minute=15, second=2, microsecond=0)
                sleep_seconds = (next_day - current_time).total_seconds()
                logger.info(f"Market closed for today. Sleeping until next trading day: {next_day.strftime('%Y-%m-%d %H:%M:%S')}")
                time.sleep(sleep_seconds)
                continue
            
            # Market is open, proceed with data collection
            logger.info(f"Starting new cycle at: {current_time_str}")
            
            # First fetch NIFTY data
            logger.info("Fetching NIFTY option chain data...")
            fetch_and_save_option_chain("NIFTY")
            
            # Then fetch BANKNIFTY data
            logger.info("Fetching BANKNIFTY option chain data...")
            fetch_and_save_option_chain("BANKNIFTY")
            
            # Calculate time taken for this cycle
            cycle_end_time = datetime.now()
            time_taken = (cycle_end_time - current_time).total_seconds()
            logger.info(f"Cycle completed in {time_taken:.2f} seconds")
            
            # Wait until next minute + 2 seconds
            next_minute = (cycle_end_time + timedelta(minutes=1)).replace(second=2, microsecond=0)
            wait_time = (next_minute - cycle_end_time).total_seconds()
            if wait_time > 0:
                logger.info(f"Waiting {wait_time:.2f} seconds until next cycle...")
                time.sleep(wait_time)
            
        except KeyboardInterrupt:
            logger.info("Stopping data collection...")
            break
        except Exception as e:
            logger.error(f"Error in main loop: {str(e)}")
            logger.error("Full error details:", exc_info=True)
            # Sleep for 1 minute before retrying
            time.sleep(60)

if __name__ == "__main__":
    main()
