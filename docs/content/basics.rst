About
=====

Sugar API is a Python3.7+ module that provides a variety of tools for creating
Sanic based APIs as well as a JSONAPI mixin for Sugar ODM models.

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

Usage
=====

Respond with allowed methods:

.. code-block:: python

  from sugar_api import preflight

  from server import server

  @server.options('/v1/endpoint')
  async def endpoint(request):
    return preflight(methods=['GET','POST'])

------------------------------------------------

To mount a JSONAPI resource into a Sanic server:

.. code-block:: python

  from sugar_odm import PostgresDBModel, Field
  from sugar_api import JSONAPIMixin

  from server import server

  class DataModel(PostgresDBModel, JSONAPIMixin):
    field = Field(required=True)

  server.blueprint(DataModel.resource(url_prefix='/v1'))

This exposes `/v1/data_models[/<id>]` as a JSONAPI resource.

--------------------------------------------------------------------

To mount a JSONAPI resource with pubsub functionality into a Sanic server:

.. code-block:: python

  from sugar_odm import PostgresDBModel, Field
  from sugar_api import JSONAPIMixin

  from server import server

  class DataModel(PostgresDBModel, JSONAPIMixin):
    field = Field(required=True)

  server.blueprint(DataModel.resource(pubsub=True))

This exposes `/data_models[/<id>]` as a JSONAPI resource as well as
`/data_models/pubsub` as a websocket resource.

------------------------------------------------------------

Add a `created` timestamp to a **sugar_odm** model:

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
