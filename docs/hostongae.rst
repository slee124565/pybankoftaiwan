.. _hostongae:

===========
Host on GAE
===========

In order to keep track of BOT Gold Passbook price index, user could make 
use of Google App Engine (GAE) service to host a web service for this 
purpose. The package provides related module `models_gae` to make used 
of Google Cloud service. 

GAE Datastore
-------------

Module `models_gae` is based on GAE datastore service and related libraries 
to provide storage space for BOT Gold Passbook price data. And it also 
comes with a couple of functions for GAE platform integration:

- init_datastore: load history price data already exists in package and save 
  into GAE datastore. 
- daily_update_chain_task: configure GAE Task Queue service to activate this 
  function with daily schedule.

