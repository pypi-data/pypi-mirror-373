Unreleased changes
------------------



Version 0
---------

0.3.1 / 2025-09-03
~~~~~~~~~~~~~~~~~~

* Add ``Detector::com`` to reproduce ``km3pipe::hardware::Detector::com`` center of mass implementation.


0.3.0 / 2025-08-12
~~~~~~~~~~~~~~~~~~

* Add ``Tripods``, ``Transmitter`` and ``Hydrophones`` classes to extend the geometry support of the library.

0.2.4 / 2025-06-18
~~~~~~~~~~~~~~~~~~

* Add ``DynamicPosition`` class to read dynamic positioning files

0.2.2 / 2025-05-07
~~~~~~~~~~~~~~~~~~

* Add limit on ``unix2datetime`` to limit timestamps to 2038/12/31 (limit of POSIX date)


0.2.0 / 2025-04-01
~~~~~~~~~~~~~~~~~~

* Remove template artifacts
* Add detector files (detx/datx) support through ``Detector`` class
* Add PMT paramters files (txt) support through ``PMT_parameters`` class
 
0.1.0 / 2025-04-01
~~~~~~~~~~~~~~~~~~
* Project generated using the cookiecutter template from
  https://git.km3net.de/templates/python-project
