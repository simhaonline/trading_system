# trading_system
An automated systematic trading system for cryptocurrencies:


1.) The entire history of market data for each Binance cryptocurrency is stored in a SQL database.

2.) The SQL database is automatically updated with the latest market data, with new data added as it becomes available.

3.) Strategies are developed to have standardised inputs and outputs, allowing standardised back-testing on historical market data.
The prerequisites of profitable strategies are listed for later reference .

4.) The system uses relevant historical data alongside current market data to confirm the formation of a profitable market trend, according to the prerequisites.

5.) Once a potential trade is identified, it is traded on Binance by sending the appropriate API commands.

6.) There is scope for managing trades with position size calculations based on past performance of a given strategy,
    also scope for managing a portfolio - rebalancing via % of assets allocated to different types of strategies, as appropriate.
