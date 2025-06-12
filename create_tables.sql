-- Create schema for option chain data
CREATE SCHEMA IF NOT EXISTS option_chain;

-- Create table for NIFTY option chain
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

-- Create table for BANKNIFTY option chain
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

-- Create indexes for better query performance
CREATE INDEX idx_nifty_expiry ON option_chain.nifty_option_chain(expiry_date);
CREATE INDEX idx_nifty_timestamp ON option_chain.nifty_option_chain(timestamp);
CREATE INDEX idx_banknifty_expiry ON option_chain.banknifty_option_chain(expiry_date);
CREATE INDEX idx_banknifty_timestamp ON option_chain.banknifty_option_chain(timestamp); 