# Option Chain Data Collector

A robust system for collecting and storing NIFTY and BANKNIFTY option chain data in real-time.

## Features

- Automatic data collection during market hours (9:15:02 AM to 3:30:00 PM)
- Handles both NIFTY and BANKNIFTY data
- Automatic weekend and holiday handling
- Robust error handling and recovery
- Detailed logging system
- PostgreSQL database storage
- Automatic timing management

## Prerequisites

- Python 3.8+
- PostgreSQL database
- Dhan Trading API credentials

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd option-chain-collector
```

2. Install required packages:
```bash
pip install -r requirements.txt
```

3. Set up environment variables in `.env` file:
```
DHAN_CLIENT_CODE=your_client_code
DHAN_TOKEN_ID=your_token_id
DB_NAME=your_db_name
DB_USER=your_db_user
DB_PASSWORD=your_db_password
DB_HOST=your_db_host
DB_PORT=your_db_port
```

## Database Setup

1. Create the database schema:
```sql
CREATE SCHEMA option_chain;
```

2. Create tables for NIFTY and BANKNIFTY:
```sql
-- Run setup_db.py to create tables and indexes
python setup_db.py
```

## Usage

### Basic Run
```bash
python main.py
```

### Run as Background Process
```bash
nohup python main.py > output.log 2>&1 &
```

### Run as System Service (Linux)
1. Create service file:
```bash
sudo nano /etc/systemd/system/option-chain.service
```

2. Add service configuration:
```ini
[Unit]
Description=Option Chain Data Collector
After=network.target

[Service]
Type=simple
User=your_username
WorkingDirectory=/path/to/your/script
ExecStart=/usr/bin/python3 /path/to/your/script/main.py
Restart=always
RestartSec=60

[Install]
WantedBy=multi-user.target
```

3. Start the service:
```bash
sudo systemctl daemon-reload
sudo systemctl start option-chain
sudo systemctl enable option-chain
```

## Data Collection

- Starts automatically at 9:15:02 AM
- Collects data every minute
- Stores data in PostgreSQL database
- Handles market hours automatically
- Skips weekends and holidays

## Database Queries

### Latest Data
```sql
-- Get latest data for both indices
WITH latest_times AS (
    SELECT 
        'NIFTY' as index_symbol,
        MAX(fetch_time) as latest_fetch
    FROM option_chain.nifty_option_chain
    
    UNION ALL
    
    SELECT 
        'BANKNIFTY' as index_symbol,
        MAX(fetch_time) as latest_fetch
    FROM option_chain.banknifty_option_chain
)
SELECT 
    n.index_symbol,
    n.expiry_date,
    n.strike_price,
    n.spot_price,
    n.ce_oi,
    n.pe_oi,
    n.ce_ltp,
    n.pe_ltp,
    n.fetch_time
FROM (
    SELECT 
        'NIFTY' as index_symbol,
        *
    FROM option_chain.nifty_option_chain
    
    UNION ALL
    
    SELECT 
        'BANKNIFTY' as index_symbol,
        *
    FROM option_chain.banknifty_option_chain
) n
JOIN latest_times lt 
    ON n.index_symbol = lt.index_symbol 
    AND n.fetch_time = lt.latest_fetch
ORDER BY n.index_symbol, n.strike_price;
```

## Monitoring

- Check logs in `option_chain.log`
- Monitor system service status:
```bash
sudo systemctl status option-chain
```
- View service logs:
```bash
sudo journalctl -u option-chain -f
```

## Error Handling

- Automatic retry on errors
- Detailed error logging
- Graceful shutdown handling
- Database connection recovery

## Contributing

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For support, please open an issue in the repository or contact the maintainers. # Option-Chain-Storage
# Option-Chain-Storage
