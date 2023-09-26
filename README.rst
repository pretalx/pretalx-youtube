Youtube integration
===================

This is a plugin for `pretalx`_ that provides an integration with Youtube, allowing you to embed recordings on talk pages.

API
---

Reading data
~~~~~~~~~~~~

The Plugin supplies an API at ``/api/events/<event>/p/youtube/`` that returns all configured Youtube URLs:

.. code:: json

   {
       "count": 1,
       "next": null,
       "previous": null,
       "results": [
           {
               "submission": "DPC6RT",
               "youtube_link": "https://youtube.com/watch?v=AAAAAB",
               "video_id": "AAAAAB"
           },
       ]
   }

A detail view for specific submissions is available at ``/api/events/<event>/p/youtube/<code>/``:

.. code:: json

   {
       "submission": "DPC6RT",
       "youtube_link": "https://youtube.com/watch?v=AAAAAB",
       "video_id": "AAAAAB"
   }

Writing data
~~~~~~~~~~~~

You can use ``POST`` requests against the list endpoint and ``PATCH`` or ``PUT`` requests against the detail endpoint to
create or update Youtube links. The ``video_id`` field is required, as is the ``submission`` field unless you are using
``PATCH``. The ``submission`` field must be the code of an existing submission, and the API will take care of updating
existing links if you use ``POST``, so it's safe to just always ``POST`` to the list endpoint.

You can also **bulk import** data in either JSON or CSV format. The JSON format is the same as the one used by the API,
and the CSV format is a simple CSV file with a header row containing the fields ``submission`` and ``video_id``. You can
upload the file to ``/api/events/<event>/p/youtube/import/`` using a ``POST`` request with the file as the body.
(For JSON, you can also instead put the data in the request body.)


Development setup
-----------------

1. Make sure that you have a working `pretalx development setup`_.

2. Clone this repository, eg to ``local/pretalx-youtube``.

3. Activate the virtual environment you use for pretalx development.

4. Execute ``python setup.py develop`` within this directory to register this application with pretalx's plugin registry.

5. Execute ``make`` within this directory to compile translations.

6. Restart your local pretalx server. You can now use the plugin from this repository for your events by enabling it in
   the 'plugins' tab in the settings.


License
-------

Copyright 2021 Tobias Kunze

Released under the terms of the Apache License 2.0


.. _pretalx: https://github.com/pretalx/pretalx
.. _pretalx development setup: https://docs.pretalx.org/en/latest/developer/setup.html
