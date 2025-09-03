km3det
======

.. image:: https://git.km3net.de/km3py/km3det/badges/master/pipeline.svg
    :target: https://git.km3net.de/km3py/km3det/pipelines

.. image:: https://git.km3net.de/km3py/km3det/badges/master/coverage.svg
    :target: https://km3py.pages.km3net.de/km3det/coverage

.. image:: https://git.km3net.de/examples/km3badges/-/raw/master/docs-latest-brightgreen.svg
    :target: https://km3py.pages.km3net.de/km3det


``km3det`` is a low weight python module for detector definition file io in KM3NeT.

It currently supports:

- Detector files (``datx`` / ``detx``)
- PMT parameters files (``txt``)
  
Installation
~~~~~~~~~~~~

It is recommended to first create an isolated virtualenvironment to not interfere
with other Python projects::

  git clone https://git.km3net.de/km3py/km3det
  cd km3det
  python3 -m venv venv
  . venv/bin/activate

Install directly from the Git server via ``pip`` (no cloneing needed)::

  pip install git+https://git.km3net.de/km3py/km3det

Or clone the repository and run::

  make install

To install all the development dependencies, in case you want to contribute or
run the test suite::

  make install-dev
  make test

  
---

*Created with ``cookiecutter https://git.km3net.de/templates/python-project``*
