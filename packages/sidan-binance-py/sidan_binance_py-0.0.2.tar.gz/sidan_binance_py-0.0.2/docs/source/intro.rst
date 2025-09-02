.. role:: raw-html-m2r(raw)
   :format: html


Binance SDK (Python)
====================


.. image:: https://img.shields.io/badge/python-3.8%2B-blue
   :target: https://www.python.org/downloads/
   :alt: Python version


.. image:: https://github.com/sidan-lab/sidan-binance-py/actions/workflows/docs.yml/badge.svg
   :target: https://sidan-lab.github.io/sidan-binance-py/
   :alt: Documentation


.. image:: https://img.shields.io/badge/code_style-ruff-black
   :target: https://github.com/astral-sh/ruff
   :alt: Code Style


.. image:: https://img.shields.io/badge/License-MIT-yellow.svg
   :target: https://opensource.org/licenses/MIT
   :alt: License: MIT

**🔗 Fork Notice**: This repository is a significantly modified fork of the official `binance-connector-python <https://github.com/binance/binance-connector-python>`_. It has been refactored to use modern Python packaging (pyproject.toml), updated tooling (uv, ruff), and enhanced development workflows.

**sidan-binance-py** is a lightweight, modern Python library for connecting to the `Binance public API <https://github.com/binance/binance-spot-api-docs>`_.
It's designed to be simple, clean, and easy to use with minimal dependencies.

* **Fork Source Code**: https://github.com/sidan-lab/sidan-binance-py
* **Original Connector**: https://github.com/binance/binance-connector-python
* Official API document:

  * https://github.com/binance/binance-spot-api-docs
  * https://binance-docs.github.io/apidocs/spot/en

* Support channels:

  * Binance developer forum: https://dev.binance.vision/
  * Telegram Channel: https://t.me/binance_api_english

* API key setup: https://www.binance.com/en-NG/support/faq/360002502072
* Testnet API key setup: https://dev.binance.vision/t/99

Features
--------

* Supported APIs:

  * ``/api/*``
  * ``/sapi/*``
  * Spot Websocket Market Stream
  * Spot User Data Stream

* Inclusion of test cases and examples
* Customizable base URL, request timeout and HTTP proxy
* Response metadata can be displayed

Quick Start
-----------

Installation
^^^^^^^^^^^^

* Install via package name

  .. code-block:: bash

     pip install sidan-binance-py

* Using uv (fastest)

  .. code-block:: bash

     uv add sidan-binance-py

* From source

  .. code-block:: bash

    git clone https://github.com/sidan-lab/sidan-binance-py.git
    cd sidan-binance-py
    uv sync


Usage
-----

RESTful APIs
^^^^^^^^^^^^

.. code-block:: python

   import logging
   from binance.spot import Spot
   from binance.lib.utils import config_logging

   config_logging(logging, logging.DEBUG)

   client = Spot()
   logging.info(client.time())

   client = Spot(api_key='<api_key>', api_secret='<api_secret>')

   # Get account information
   logging.info(client.account())

   # Post a new order
   params = {
       'symbol': 'BTCUSDT',
       'side': 'SELL',
       'type': 'LIMIT',
       'timeInForce': 'GTC',
       'quantity': 0.002,
       'price': 9500
   }

   response = client.new_order(**params)
   logging.info(response)

Please find `examples <https://github.com/sidan-lab/sidan-binance-py/tree/main/examples>`_ folder to check for more endpoints.


Websocket
^^^^^^^^^

.. code-block:: python

   import logging
   from binance.websocket.spot.websocket_api import SpotWebsocketAPIClient

   def on_close(_):
       logging.info("Do custom stuff when connection is closed")

   def message_handler(message):
       print(message)

   ws_client = SpotWebsocketAPIClient(on_message=message_handler, on_close=on_close)

   ws_client.ticker(
       symbol='bnbusdt',
       type="FULL",
   )

   # Combine selected streams
   ws_client.ticker(
       symbols=["BNBBUSD", "BTCUSDT"],
       type="MINI",
       windowSize="2h",
   )

   ws_client.stop()

More websocket examples are available in the `examples <https://github.com/sidan-lab/sidan-binance-py/tree/main/examples>`_ folder
