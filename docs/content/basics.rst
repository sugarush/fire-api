Basics
======

.. code-block:: python

  from server import server

  from sugar_odm import PostgresDBModel, Field
  from sugar_api import JSONAPIMixin, TimestampMixin

  class Data(PostgresDBModel, JSONAPIMixin, TimestampMixin):
    field = Field(required=True)

  server.blueprint(Data.resource(url_prefix='/v1'))
