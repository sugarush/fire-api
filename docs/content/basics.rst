Basics
======

.. code-block:: python

  from sugar_odm import PostgresDBModel, Field
  from sugar_api import JSONAPIMixin, TimestampMixin

  from server import server

  class Data(PostgresDBModel, JSONAPIMixin, TimestampMixin):
    field = Field(required=True)

  server.blueprint(Data.resource(url_prefix='/v1'))

.. code-block:: python

  from datetime import datetime

  from sugar_odm import PostgresDBModel, Field
  from sugar_api import JSONAPIMixin, TimestampMixin

  class Data(PostgresDBModel, JSONAPIMixin, TimestampMixin):
    created = Field(
      type='timestamp',
      default=lambda: datetime.utcnow(),
      default_empty=True,
      default_type=True
    )
