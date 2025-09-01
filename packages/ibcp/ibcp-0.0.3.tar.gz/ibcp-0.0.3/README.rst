
IBCP: Python Wrapper for Interactive Brokers API
================================================

.. image:: https://img.shields.io/pypi/v/ibcp
   :target: https://pypi.org/pypi/ibcp/
.. image:: https://img.shields.io/pypi/pyversions/ibcp
   :target: https://pypi.org/pypi/ibcp/
.. image:: https://img.shields.io/pypi/l/ibcp
   :target: https://pypi.org/pypi/ibcp/
.. image:: https://readthedocs.org/projects/ibcp/badge/?version=latest
   :target: https://ibcp.readthedocs.io/en/latest/?badge=latest

.. figure:: https://raw.githubusercontent.com/matthewmoorcroft/ibcp/main/docs/logo.png
   :alt: Logo for 'IBCP'
   :align: center

   "Logo for 'IBCP'"

Overview
--------

|   IBCP is an unofficial python wrapper for `Interactive Brokers Client Portal Web API <https://interactivebrokers.github.io/cpwebapi/>`__. The motivation for the project was to build a Python wrapper
|   that is easy to use and understand.

Please see https://ibcp.readthedocs.io for the full documentation.

Features
--------

- Simple REST API wrapper
- Easy to use and understand
- Supports all Interactive Brokers Client Portal Web API endpoints
- Handles authentication and session management
- Supports both SSL and non-SSL connections

Requirements
------------

IBCP assumes a gateway session is active and authenticated.

Installation
------------

IBCP was developed under the `Voyz/IBeam <https://github.com/voyz/ibeam>`__ docker image environment.

Once a gateway session is running, ``pip`` command can be used to install IBCP:

.. code-block:: bash

   pip install ibcp

Usage
--------

.. code-block:: python

   import ibcp

   ib = ibcp.REST() # default parameters: url="https://localhost:5000", ssl=False

   # Get account information
   account = ib.get_account()

   # Get portfolio
   portfolio = ib.get_portfolio()

   # Get positions
   positions = ib.get_positions()

   # Get orders
   orders = ib.get_orders()

   # Get trades
   trades = ib.get_trades()

   # Get market data
   market_data = ib.get_market_data("AAPL")

   # Place order
   order = ib.place_order({
       "symbol": "AAPL",
       "secType": "STK",
       "currency": "USD",
       "exchange": "SMART",
       "tif": "DAY",
       "side": "BUY",
       "totalQuantity": 100,
       "orderType": "MKT"
   })

For the complete reference, please visit https://ibcp.readthedocs.io/en/latest/reference.html.

Configuration
-------------

By default, IBCP assumes the gateway session is open at https://localhost:5000 without an SSL certificate. A custom URL and SSL certificate can be set by:

.. code-block:: python

   ib = ibcp.REST(url="https://localhost:5000", ssl=False)

Documentation of available functions is at https://ibcp.readthedocs.io/en/latest/reference.html.

