import os
import psycopg2
from dotenv import load_dotenv
import traceback

# Load environment variables
load_dotenv()

# Database configuration from environment variables
DB_CONFIG = {
    'dbname': os.getenv('DB_NAME'),
    'user': os.getenv('DB_USER'),
    'password': os.getenv('DB_PASSWORD'),
    'host': os.getenv('DB_HOST'),
    'port': os.getenv('DB_PORT')
}

def setup_database():
    """Create database schema and tables"""
    try:
        print("Connecting to database...")
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()
        
        # Create schema
        print("\nCreating schema...")
        cur.execute("""
            CREATE SCHEMA IF NOT EXISTS option_chain;
        """)
        
        # Create NIFTY table
        print("Creating NIFTY option chain table...")
        cur.execute("""
            CREATE TABLE IF NOT EXISTS option_chain.nifty_option_chain (
                id SERIAL PRIMARY KEY,
                symbol VARCHAR(10),
                expiry_date VARCHAR(20),
                fetch_time TIMESTAMP,
                spot_price DECIMAL(10,2),
                atm_strike DECIMAL(10,2),
                strike_price DECIMAL(10,2),
                -- Call option data
                ce_oi BIGINT,
                ce_chg_in_oi BIGINT,
                ce_volume BIGINT,
                ce_iv DECIMAL(10,2),
                ce_ltp DECIMAL(10,2),
                ce_bid_qty BIGINT,
                ce_bid DECIMAL(10,2),
                ce_ask DECIMAL(10,2),
                ce_ask_qty BIGINT,
                ce_delta DECIMAL(10,4),
                ce_theta DECIMAL(10,4),
                ce_gamma DECIMAL(10,4),
                ce_vega DECIMAL(10,4),
                -- Put option data
                pe_bid_qty BIGINT,
                pe_bid DECIMAL(10,2),
                pe_ask DECIMAL(10,2),
                pe_ask_qty BIGINT,
                pe_ltp DECIMAL(10,2),
                pe_iv DECIMAL(10,2),
                pe_volume BIGINT,
                pe_chg_in_oi BIGINT,
                pe_oi BIGINT,
                pe_delta DECIMAL(10,4),
                pe_theta DECIMAL(10,4),
                pe_gamma DECIMAL(10,4),
                pe_vega DECIMAL(10,4),
                timestamp TIME,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        
        # Create BANKNIFTY table
        print("Creating BANKNIFTY option chain table...")
        cur.execute("""
            CREATE TABLE IF NOT EXISTS option_chain.banknifty_option_chain (
                id SERIAL PRIMARY KEY,
                symbol VARCHAR(10),
                expiry_date VARCHAR(20),
                fetch_time TIMESTAMP,
                spot_price DECIMAL(10,2),
                atm_strike DECIMAL(10,2),
                strike_price DECIMAL(10,2),
                -- Call option data
                ce_oi BIGINT,
                ce_chg_in_oi BIGINT,
                ce_volume BIGINT,
                ce_iv DECIMAL(10,2),
                ce_ltp DECIMAL(10,2),
                ce_bid_qty BIGINT,
                ce_bid DECIMAL(10,2),
                ce_ask DECIMAL(10,2),
                ce_ask_qty BIGINT,
                ce_delta DECIMAL(10,4),
                ce_theta DECIMAL(10,4),
                ce_gamma DECIMAL(10,4),
                ce_vega DECIMAL(10,4),
                -- Put option data
                pe_bid_qty BIGINT,
                pe_bid DECIMAL(10,2),
                pe_ask DECIMAL(10,2),
                pe_ask_qty BIGINT,
                pe_ltp DECIMAL(10,2),
                pe_iv DECIMAL(10,2),
                pe_volume BIGINT,
                pe_chg_in_oi BIGINT,
                pe_oi BIGINT,
                pe_delta DECIMAL(10,4),
                pe_theta DECIMAL(10,4),
                pe_gamma DECIMAL(10,4),
                pe_vega DECIMAL(10,4),
                timestamp TIME,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        
        # Create indexes
        print("Creating indexes...")
        cur.execute("""
            CREATE INDEX IF NOT EXISTS idx_nifty_expiry 
            ON option_chain.nifty_option_chain(expiry_date);
            
            CREATE INDEX IF NOT EXISTS idx_nifty_timestamp 
            ON option_chain.nifty_option_chain(timestamp);
            
            CREATE INDEX IF NOT EXISTS idx_banknifty_expiry 
            ON option_chain.banknifty_option_chain(expiry_date);
            
            CREATE INDEX IF NOT EXISTS idx_banknifty_timestamp 
            ON option_chain.banknifty_option_chain(timestamp);
        """)
        
        # Commit changes
        conn.commit()
        print("\nDatabase setup completed successfully!")
        
        # Verify tables
        print("\nVerifying tables...")
        cur.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'option_chain';
        """)
        tables = cur.fetchall()
        print("\nCreated tables:")
        for table in tables:
            print(f"- {table[0]}")
        
    except Exception as e:
        print(f"\nError setting up database: {str(e)}")
        print("Full error details:", e.__class__.__name__)
        print("Traceback:", traceback.format_exc())
        if 'conn' in locals():
            conn.rollback()
    finally:
        if 'cur' in locals():
            cur.close()
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    setup_database() 