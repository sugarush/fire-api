Installation
============

Sugar API can be installed with `pip`:

``pip install git+https://github.com/sugarush/sugar-api@master``

.. attention::
  You must currently uninstall the `ujson` module after installing
  **sugar_api** due to compatibility. It is a dependency of `sanic`, not
  **sugar_api**. This will be fixed in the future.

To uninstall `ujson` with `pip`:

``pip uninstall ujson``

Examples
========

Respond with allowed methods:

.. code-block:: python

  from sugar_api import preflight
  
  from server import server

  @server.options('/v1/endpoint')
  async def endpoint(request):
    return preflight(methods=['GET','POST'])

To mount a REST resource into a Sanic server:

.. code-block:: python

  from sugar_odm import PostgresDBModel, Field
  from sugar_api import JSONAPIMixin, TimestampMixin

  from server import server

  class DataModel(PostgresDBModel, JSONAPIMixin, TimestampMixin):
    field = Field(required=True)

  server.blueprint(DataModel.resource(url_prefix='/v1'))

Add a `created` field to a **sugar_odm** model:

.. code-block:: python

  from datetime import datetime

  from sugar_odm import PostgresDBModel, Field
  from sugar_api import JSONAPIMixin, TimestampMixin

  class DataModel(PostgresDBModel, JSONAPIMixin, TimestampMixin):
    created = Field(
      type='timestamp',
      default=lambda: datetime.utcnow(),
      default_empty=True,
      default_type=True
    )
