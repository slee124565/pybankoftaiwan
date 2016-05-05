.. _usage:

=====
Usage
=====

Typical Usage of GoldPassbook Module
------------------------------------
`goldpassbook` module make use of `urllib` and `lxml` libraries to parsing BOT Gold Passbook HTML page and return a price list data (date, open, high, low, close). 
To get today's Gold Passbook TWD selling price index::

    #!/usr/bin/env python
    import goldpassbook
    
    t_date, t_open, t_high, t_low, t_close = goldpassbook.get_date_price_index()
    
`goldpassbook` module also provide a couple of handy functions.
If you want to get all Gold Passbook TWD selling price index of this month::

    #!/usr/bin/env python
    import goldpassbook
    
    this_month_price_list = goldpassbook.get_monthly_price_index()
    
If you want to save this month Gold Passbook TWD Selling price index in `history` sub-directory::
    
    #!/usr/bin/env python
    import goldpassbook
    
    this_month_price_list = goldpassbook.save_month_price_index()
 
If you want to save all Gold Passbook TWD Selling price index in `history` sub-directory::

    #!/usr/bin/env python
    import goldpassbook
    
    this_month_price_list = goldpassbook.save_history_price_index()
    
After you have saved history Gold Passbook price index, `goldpassbook` module provide function `load_year_history` for you to get a list of price index with a year period.
If you want to get this year Gold Passbook TWD price index from saved history files::

    #!/usr/bin/env python
    import goldpassbook
    
    this_month_price_list = goldpassbook.load_year_history()

