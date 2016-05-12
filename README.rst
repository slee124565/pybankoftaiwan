
=================
BOT Gold Passbook
=================

General on Bank Of Taiwan (BOT) Gold Passbook
---------------------------------------------
Gold Passbook, launched in 1997, is highly welcomed by investors. It is accessible by BOT's counter and EBank. The owner of gold passbook may take delivery of gold bars and coins offered by BOT, subject to the payment of the price differences between gold products and gold passbook. The detail Gold Passbook information is on `BOT's Gold Passbook Chinese web page <http://www.bot.com.tw/gold/goldpassbook/pages/default.aspx>`_.

Details on BOT Gold Passbook Price HTML Page
--------------------------------------------
The price change log in `BOT Gold Passbook Price Page <http://rate.bot.com.tw/Pages/UIP005/UIP005INQ4.aspx>`_ is provided with daily period, 
and it takes three arguments: `date`, `curcd` and afterOrNot.

- date: the date you want to query
- curcd: the currency type of the price
- afterOrNot: the price change log is `After Hour` or `On Transaction Hour`

===================
Module GoldPassbook
===================

Purpose
-------

`goldpassbook` module is designed to fetch and parse BOT Gold Passbook HTML page data 
and provide easy to use JSON data by HTTP API with which other information system could
integrate.

Issues to Solve
---------------

- there are history data files need to be initialized.
- the history data files are not up-to-date.
- there is new data every working day.
- the data will vary if today is working day
- Internet connection or remote BOT server problem will cause exception during the data fetching
- data available only for working day; sometimes weekend will be working day

Features
--------

- get daily BOT Gold Passbook price index (date,open,high,low,close).
- get monthly BOT Gold Passbook price index list.
- save monthly BOT Gold Passbook price index into a file in sub-directory `history`.
- save all BOT Gold Passbook history price index into monthly files in sub-directory `history`.
- get year of BOT Gold Passbook price index list from saved history files.
- provide a candlestick chart
