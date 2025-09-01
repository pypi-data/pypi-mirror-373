.. pyRugged documentation master file, created by
   sphinx-quickstart on Wed Sep  9 14:17:17 2020.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

:Version: |version|

==========================================
pyRugged, A sensor-to-terrain mapping tool
==========================================


What is it?
-----------

pyRugged is a python geolocation library used for satellite imagery (pyRugged is the python version of Rugged). It allows to map image coordinates (pixel, line) with geographic or projected
coordinates (lon, lat or x, y, h) by computing the intersection of the sensor's lines of sight with the Earth's terrain. This mapping is
essential for georeferencing raw satellite images. It is a key component when projecting an image on ground.

.. figure:: images/rugged-explained-2.png
    :align: center
    :alt: Rugged explained
    :width: 60%

    Effects of taking into account the DEM in the computation of latitude, longitude and altitude

Sensor-to-terrain mapping library
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

pyRugged provides the tools to model any type of sensors rigorously/physically, to process all the spacecraft navigation data
(position, velocity and attitude), and to take into account Digital
Elevation Models (DEM) to represent the surface of the Earth. It is on
this last point that Rugged gets its name from; Rugged deals with rugged
terrains.

pyRugged relies on `Orekit <https://https://www.orekit.org/>`_ for all what concerns transformations between coordinate systems (inertial/terrestrial)
and orbital data but what pyRugged brings on top of Orekit, is the capacity
to deal with the DEM. Orekit could have been used for intersecting a line
of sight with the Earth's ellipsoid but it is not its mandate to know what
the Earth's surface looks like as it is a space dynamics library. It is in
this perspective that we decided to provide a separate package for those
users who look for a robust tool for geometric processing.


Features
--------

*  Direct/inverse location
*  Can support several types of Digital Elevation Models, including user-provided models
*  Several intersection models algorithms available
*  Both modern and legacy models for Earth rotation

    *  Lieske (1976), Wahr (1980),
    *  Mathews, Herring, Buffett (2002)
    *  Capitaine (2006)

*  Complete set of corrections applied for greater accuracy

    *  δΔψ, δΔε on precession nutation (about 3m correction since 2013, steadily increasing)
    *  ΔUT₁, lod on proper rotation (can theoretically reach up to 400m)
    *  u, v pole wander (polhody), (about 15m correction)
    *  light time correction (about 1.2m)
    *  aberration of light correction (about 20m)
    *  line-of-sight curvature in geodetic coordinates, (0m at nadir, 10m at 30° dive angle, hundreds of meters for skimming los)
    *  atmospheric refraction

*  Not limited to Earth

Free (open source) software
---------------------------

pyRugged is freely available, with all related documentation and tests.

Rugged is distributed under the `Apache License version 2.0 <https://www.apache.org/licenses/LICENSE-2.0.txt>`_ , a well known business-friendly license. This means
anybody can use it to build any application, free or not. There are no
strings attached to user code.

Who is behind it?
-----------------

Development
~~~~~~~~~~~

Rugged has been in development since 2014 inside `CS GROUP <https://www.csgroup.eu/>`_ and is still used and maintained by its dual teams of space dynamics and image processing experts.
pyRugged, the python version of Rugged has been started in 2022.

Several major actors of space research and industry are interested into this project.

Rugged forum is available for any question or request about Rugged (see :ref:`contact` section).

We do our best to provide you with a quality code:

.. toctree::
    :maxdepth: 1
    :caption: Contents:

    design
    installation
    user_manual
    development
    contact