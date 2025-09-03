======
papyru
======

A minimal toolset to help developing RESTful services on top of django.

Development
===========

Documentation
-------------

papyru's API documentation can be generated using `make docs` or
`./run generate-docs`.

Alternatively, you can call `./run docs` and take a cup of tea until the docs
appear in your browser.

Tests
-----

While development, you can simply run `make test` or `./run test locally`.
Test requirements are installed into test-env/ if not already present.
It is highly recommended to finally run the containerized tests to ensure
compatiblity to the Python versions we use in our projects.
