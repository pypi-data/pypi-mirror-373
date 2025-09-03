/* *********************************************************************
 * This Original Work is copyright of 51 Degrees Mobile Experts Limited.
 * Copyright 2025 51 Degrees Mobile Experts Limited, Davidson House,
 * Forbury Square, Reading, Berkshire, United Kingdom RG1 3EU.
 *
 * This Original Work is licensed under the European Union Public Licence
 * (EUPL) v.1.2 and is subject to its terms as set out below.
 *
 * If a copy of the EUPL was not distributed with this file, You can obtain
 * one at https://opensource.org/licenses/EUPL-1.2.
 *
 * The 'Compatible Licences' set out in the Appendix to the EUPL (as may be
 * amended by the European Commission) shall be deemed incompatible for
 * the purposes of the Work and the provisions of the compatibility
 * clause in Article 5 of the EUPL shall not apply.
 *
 * If using the Work as, or as part of, a network application, by
 * including the attribution notice(s) required under Article 5 of the EUPL
 * in the end user terms of the application under an appropriate heading,
 * such notice(s) shall fulfill the requirements of that article.
 * ********************************************************************* */

#ifndef FIFTYONE_DEGREES_COORDINATE_H_INCLUDED
#define FIFTYONE_DEGREES_COORDINATE_H_INCLUDED

/**
 * @ingroup FiftyOneDegreesCommon
 * @defgroup FiftyOneDegreesCoordinate Coodinate
 *
 * A coordinate representation of a location.
 *
 * ## Introduction
 *
 * Type and Getter method for a coordinate item.
 *
 * Obtaining the latitude and longitude of a 
 * coordinate item in the strings collection can
 * be done by using the API #fiftyoneDegreesIpiGetCoordinate
 *
 * @{
 */

#include "exceptions.h"
#include "collection.h"
#include "common.h"

/**
 * Singular coordinate, representing a location
 */
typedef struct fiftyone_degrees_ipi_coordinate_t {
	float lat; /**< Latitude value of the coordinate */
	float lon; /**< Longitude value of the coordinate */
} fiftyoneDegreesCoordinate;

/**
 * Get the 51Degrees Coordinate from the strings collection item.
 * This should be used on the item whose property type is 
 * #FIFTYONE_DEGREES_PROPERTY_VALUE_TYPE_COORDINATE.
 * @param item the collection item pointing to the coordinate item in
 * strings collection
 * @param exception pointer to an exception data structure to be used if an
 * exception occurs. See exceptions.h
 * @return the coordinate value
 */
EXTERNAL fiftyoneDegreesCoordinate fiftyoneDegreesIpiGetCoordinate(
	fiftyoneDegreesCollectionItem *item,
	fiftyoneDegreesException *exception);

/**
 * @}
 */

#endif