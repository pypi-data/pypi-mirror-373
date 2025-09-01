.. _tutorials:

=========
Tutorials
=========

Following tutorials are available in notebook section.

Rugged initialization and direct location
-----------------------------------------

This tutorial explains how to initialize Rugged and use it to geolocate a satellite image. Let’s imagine the sensor is a single line imager with 2000 pixels and 20° field of view, oriented 10° off nadir. GPS and AOCS auxiliary data are available and provide us with a list of positions, velocities and attitude quaternions recorded during the acquisition. By passing all this information to Rugged, we will be able to precisely locate each point of the image on the Earth. Well, not exactly precise, as this first tutorial does not use a Digital Elevation Model, but considers the Earth as an ellipsoid. The DEM will be added in a second tutorial: Direct location with a DEM. The objective here is limited to explain how to initialize everything Rugged needs to know about the sensor and the acquisition.

Direct Location with a DEM
--------------------------

The aim of this tutorial is to compute a direct location grid by intersection of the line of sight with a DEM (Digital Elevation Model), using Duvenhage’s algorithm. This algorithm is the most performant one in Rugged.

The following figure shows the effects of taking into account the DEM in the computation of latitude, longitude and altitude:

.. figure:: images/RuggedExplained.png
    :align: center
    :alt: direct location DEM
    :width: 60%

Inverse Location
----------------

The aim of this tutorial is to compute the inverse location of a point on Earth in order to give the sensor pixel, with the associated line, seeing this point.

We will also explain how to find the date at which sensor sees a ground point, which is a kind of inverse location only focusing on date.


Atmospheric refraction examples
-------------------------------

The aim of this tutorials is to compute location using atmospheric refraction models.


