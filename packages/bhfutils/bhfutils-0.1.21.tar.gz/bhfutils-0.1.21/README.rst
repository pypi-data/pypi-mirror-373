******************************
Behoof Scrapy Cluster Template
******************************

Overview
--------

The ``bhfutils`` package is a collection of utilities that are used by any spider of Behoof project.

Requirements
------------

- Unix based machine (Linux or OS X)
- Python 2.7 or 3.6

Installation
------------

Inside a virtualenv, run ``pip install -U bhfutils``.  This will install the latest version of the Behoof Scrapy Cluster Spider utilities.  After that you can use special settings.py compatibal with scrapy cluster (template placed in crawler/setting_template.py)

Documentation
-------------

Full documentation for the ``bhfutils`` package does not exist

custom_cookies.py
==================

The ``custom_cookies`` module is custom Cookies Middleware to pass our required cookies along but not persist between calls

distributed_scheduler.py
========================

The ``distributed_scheduler`` module is scrapy request scheduler that utilizes Redis Throttled Priority Queues to moderate different domain scrape requests within a distributed scrapy cluster

redis_domain_max_page_filter.py
===============================

The ``redis_domain_max_page_filter`` module is redis-based max page filter. This filter is applied per domain. Using this filter the maximum number of pages crawled for a particular domain is bounded 

redis_dupefilter.py
===================

The ``redis_dupefilter`` module is redis-based request duplication filter

redis_global_page_per_domain_filter.py
======================================

The ``redis_global_page_per_domain_filter`` module is redis-based request number filter When this filter is enabled, all crawl jobs have GLOBAL_PAGE_PER_DOMAIN_LIMIT as a hard limit of the max pages they are allowed to crawl for each individual spiderid+domain+crawlid combination.
