.. _design_dem:

=======================
Digital Elevation Model
=======================

DEM intersection
----------------

The page technical choices explain how Rugged goes from an on-board pixel line-of-sight to a ground-based line-of-sight arrival in the vicinity of the ellipsoid entry point. At this step, we have a 3D line defined near the surface and want to compute where it exactly traverses the Digital Elevation Model surface. There is no support for this computation at Orekit library level, everything is done at Rugged library level.

As this part of the algorithm represents an inner loop, it is one that must use fast algorithms. Depending on the conditions (line-of-sight skimming over the terrain near field of view edges or diving directly in a nadir view), some algorithms are more suitable than others. This computation is isolated in the smallest programming unit possible in the Rugged library and an interface is defined with several different implementations among which user can select.

Five different algorithms are predefined in Rugged:

*  a recursive algorithm based on Bernardt Duvenhage’s 2009 paper `Using An Implicit Min/Max KD-Tree for Doing Efficient Terrain Line of Sight Calculations <http://researchspace.csir.co.za/dspace/bitstream/handle/10204/3041/Duvenhage_2009.pdf>`_
*  an alternate version of the Duvenhage algorithm using flat-body hypothesis,
*  a basic scan algorithm sequentially checking all pixels in the rectangular array defined by Digital Elevation Model entry and exit points,
*  an algorithm that ignores the Digital Elevation Model and uses a constant elevation over the ellipsoid.
*  a no-operation algorithm that ignores the Digital Elevation Model and uses only the ellipsoid.

It is expected that other algorithms like line-stepping (perhaps using Bresenham line algorithm) will be added afterwards.

The Duvenhage algorithm with full consideration of the ellipsoid shape is the baseline approach for operational computation. The alternate version of Duvenhage algorithm with flat-body hypothesis does not really save anything meaningful in terms of computation, so it should only be used for testing purposes. The basic scan algorithm is only intended as a basic reference that can be used for validation and tests. The no-operation algorithm can be used for low accuracy fast computation needs without changing the complete data product work-flow.

DEM loading
-----------

As the min/max KD-tree structure is specific to the Duvenhage algorithm, and as the algorithm is hidden behind a generic interface, the tree remains an implementation detail the user should not see. The min/max KD-tree structure is therefore built directly at Rugged level, only when the Duvenhage algorithm has been selected to perform location computation.

On the other hand, Rugged is not expected to parsed DEM files, so the algorithm relies on the raw data being passed by the upper layer. In order to pass these data, a specific callback function is implemented in the mission specific interface layer and registered to Rugged, which can call it to retrieve parts of the DEM, in the form of small cells. The implicit KD-tree is then built from leafs to root and cached.

DEM assumptions and specifications
----------------------------------

Rugged does not parse DEM files but takes buffers of elevation data as input. It is up to the calling application to read the DEM and load the data into buffers. Rugged provides a tile mecanism with cache for large DEMs allowing the user to load one tile at a time. This is in line with the format of world coverage DEMs such as SRTM. Rugged offers an interface for updating the DEM tiles in cache with a callback function triggered everytime a coordinate falls outside the current region.

The calling application must implement the callback function for loading the tiles. We recommend to use GDAL (http://www.gdal.org/) to parse the DEM files as it handles most formats (including geoTIFF for Aster DEM or DTED for SRTM). Rugged does not include the parsing of the DEM, by design, and yet we could have used GDAL. We want Rugged to remain a low-level library that does not pull too many third-party libraries.

important notes on DEM tiles
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

*  Ground point elevation are obtained by bilinear interpolation between 4 neighbouring cells. There is no specific algorithm for border management. As a consequence, a point falling on the border of the tile is considered outside. DEM tiles must be overlapping by at least one line/column in all directions.

*  In Rugged terminology, the minimum latitude and longitude correspond to the centre of the farthest Southwest cell of the DEM. Be careful if using GDAL to pass the correct information as there is half a pixel shift with respect to the lower left corner coordinates in gdalinfo.

The following diagram illustrates proper DEM tiling with one line/column overlaps between neighbouring tiles :

.. figure:: images/DEM-tiles-overlap.png
    :align: center
    :alt: DEM tiles overlap
    :width: 100%

This diagram tries to represent the meaning of the different parameters and conventions in the definition of a tile :

.. figure:: images/tile-description.png
    :align: center
    :alt: DEM tiles convention
    :width: 100%

see dedicated notebook for detailed implementation.
