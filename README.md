# An automated system for trading cryptocurrencies

Overview

1.) The entire history of market data for each Binance cryptocurrency is stored in a SQL database.

2.) The SQL database is automatically updated with the latest market data, with new data added as it becomes available.

3.) Strategies are developed to have standardised inputs and outputs, allowing standardised back-testing on historical market data.
The prerequisites of profitable strategies are listed for later reference .

4.) The system uses relevant historical data alongside current market data to confirm the formation of a profitable market trend, according to the prerequisites.

5.) Once a potential trade is identified, it is traded on Binance by sending the appropriate API commands.

6.) There is scope for managing trades with position size calculations based on past performance of a given strategy,
    also scope for managing a portfolio - rebalancing via % of assets allocated to different types of strategies, as appropriate.


![Buy/ sell signals for NEOBTC (1d)](http://u.cubeupload.com/henryp/NEOBTC1dSignals.png)

File Guide 

account.py - Exchange functions that relate directly to exchange information or account information.

return_info.py - Fetches generic data not requiring any additional information (parameters) to retrieve.

gets_checks.py - Consisting of 'gets' and 'checks', these functions return data based on inputs (parameters), where 'checks' are limited to returning True or False.

format_data.py - Consisting of reformatting functions. These functions require an input and return it reformatted. 

calculations.py - Takes an input and returns the logical output. 

operations.py - Procedures consisting of gets, checks, calculations, formattings and custom code for that specifc operation. 

strategies.py - Functions that produce buy/sell signals based on logic underlying the strategy.
