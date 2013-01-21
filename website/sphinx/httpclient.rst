``cyclone.httpclient`` --- Non-blocking HTTP client
===================================================

.. automodule:: cyclone.httpclient

   HTTP client interfaces
   ----------------------

   .. autoclass:: HTTPClient
      :members:

   .. autoclass:: JsonRPC
      :members:

   Command-line interface
   ----------------------

   This module provides a simple command-line interface to fetch a url
   using Tornado's HTTP client.  Example usage::

      # Fetch the url and print its body
      python -m tornado.httpclient http://www.google.com

      # Just print the headers
      python -m tornado.httpclient --print_headers --print_body=false http://www.google.com
