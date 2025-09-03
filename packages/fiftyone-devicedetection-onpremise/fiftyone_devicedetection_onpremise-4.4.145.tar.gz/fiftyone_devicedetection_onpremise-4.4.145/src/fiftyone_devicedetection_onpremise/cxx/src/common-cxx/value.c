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

#include "value.h"
#include "fiftyone.h"

MAP_TYPE(Value);
MAP_TYPE(Collection);

typedef struct value_search_t {
	fiftyoneDegreesCollection *strings;
	const char *valueName;
} valueSearch;

#ifndef FIFTYONE_DEGREES_GET_STRING_DEFINED
#define FIFTYONE_DEGREES_GET_STRING_DEFINED
static fiftyoneDegreesString* getString(
	Collection *strings,
	uint32_t offset,
	Item *item,
	Exception *exception) {
	return StringGet(strings, offset, item, exception);
}
#endif

/*
 * Function that compare the current String item
 * against the target value that being searched
 * using the Coordinate format.
 * @value the current String item
 * @target the target search search string. This
 * should be in a,b format and will then be converted
 * to a float pair.
 * @return 0 if they are equals, otherwise negative
 * for smaller and positive for bigger.
 */
static int compareCoordinate(String *value, const char *target) {
	int result = 0;
	char *curPtr = strstr(target, ",");
	if (curPtr != NULL) {
		// Only compare if same format
		Float targetLat = NATIVE_TO_FLOAT((float)atof(target));
		Float targetLon = NATIVE_TO_FLOAT((float)atof(curPtr + 1));
		result = memcmp(&value->trail.coordinate.lat, &targetLat, sizeof(Float));
		if (result == 0) {
			result = memcmp(&value->trail.coordinate.lon, &targetLon, sizeof(Float));
		}
	}
	else {
		// This will eventually end with no value found
		result = -1;
	}
	return result;
}

/*
 * Function to compare the current String item to the
 * target search value using the IpAddress format.
 * @param value the current String item
 * @param target the target search value. This should
 * be in string readable format of an IP address.
 * @return 0 if they are equal, otherwise negative
 * for smaller and positive for bigger
 */
static int compareIpAddress(String *value, const char *target) {
	int result = 0;
	fiftyoneDegreesEvidenceIpAddress *ipAddress
		= fiftyoneDegreesIpParseAddress(
			Malloc, 
			target, 
			target + strlen(target));
	if (ipAddress != NULL) {
		int16_t valueLength = (size_t)value->size - 1;
		int16_t searchLength = 0, compareLength = 0;
		switch (ipAddress->type) {
		case FIFTYONE_DEGREES_EVIDENCE_IP_TYPE_IPV4:
			searchLength = FIFTYONE_DEGREES_IPV4_LENGTH;
			break;
		case FIFTYONE_DEGREES_EVIDENCE_IP_TYPE_IPV6:
			searchLength = FIFTYONE_DEGREES_IPV6_LENGTH;
			break;
		case FIFTYONE_DEGREES_EVIDENCE_IP_TYPE_INVALID:
		default:
			break;
		}

		if (searchLength == 0) {
			result = -1;
		}
		else {
			// Compare length first
			compareLength = valueLength < searchLength ? valueLength : searchLength;
			result = memcmp(&value->trail.secondValue, ipAddress->address, compareLength);
			if (result == 0) {
				result = valueLength - searchLength;
			}
		}
		Free(ipAddress);
	}
	return result;
}

#ifdef _MSC_VER
// Not all parameters are used for this implementation of
// #fiftyoneDegreesCollentionItemComparer
#pragma warning (disable: 4100)
#endif
static int compareValueByName(void *state, Item *item, long curIndex, Exception *exception) {
	int result = 0;
	Item name;
	String *value;
	valueSearch *search = (valueSearch*)state;
	DataReset(&name.data);
	value = ValueGetName(
		search->strings,
		(Value*)item->data.ptr,
		&name,
		exception);
	if (value != NULL && EXCEPTION_OKAY) {
		switch (value->value) {
		case FIFTYONE_DEGREES_STRING_COORDINATE:
			result = compareCoordinate(value,search->valueName);
			break;
		case FIFTYONE_DEGREES_STRING_IP_ADDRESS:
			result = compareIpAddress(value, search->valueName);
			break;
		default:
			result = strcmp(&value->value, search->valueName);
			break;
		}
		COLLECTION_RELEASE(search->strings, &name);
	}
	return result;
}
#ifdef _MSC_VER
#pragma warning (default: 4100)
#endif

fiftyoneDegreesString* fiftyoneDegreesValueGetName(
	fiftyoneDegreesCollection *strings,
	fiftyoneDegreesValue *value,
	fiftyoneDegreesCollectionItem *item,
	fiftyoneDegreesException *exception) {
	return getString(strings, value->nameOffset, item, exception);
}

fiftyoneDegreesString* fiftyoneDegreesValueGetDescription(
	fiftyoneDegreesCollection *strings,
	fiftyoneDegreesValue *value,
	fiftyoneDegreesCollectionItem *item,
	fiftyoneDegreesException *exception) {
	return getString(
		strings,
		value->descriptionOffset,
		item,
		exception);
}

fiftyoneDegreesString* fiftyoneDegreesValueGetUrl(
	fiftyoneDegreesCollection *strings,
	fiftyoneDegreesValue *value,
	fiftyoneDegreesCollectionItem *item,
	fiftyoneDegreesException *exception) {
	return getString(strings, value->urlOffset, item, exception);
}

fiftyoneDegreesValue* fiftyoneDegreesValueGet(
	fiftyoneDegreesCollection *values,
	uint32_t valueIndex,
	fiftyoneDegreesCollectionItem *item,
	fiftyoneDegreesException *exception) {
	return (Value*)values->get(
		values, 
		valueIndex, 
		item, 
		exception);
}

long fiftyoneDegreesValueGetIndexByName(
	fiftyoneDegreesCollection *values,
	fiftyoneDegreesCollection *strings,
	fiftyoneDegreesProperty *property,
	const char *valueName,
	fiftyoneDegreesException *exception) {
	Item item;
	valueSearch search;
	long index;
	DataReset(&item.data);
	search.valueName = valueName;
	search.strings = strings;
	index = CollectionBinarySearch(
		values,
		&item,
		property->firstValueIndex,
		property->lastValueIndex,
		(void*)&search,
		compareValueByName,
		exception);
	if (EXCEPTION_OKAY) {
		COLLECTION_RELEASE(values, &item);
	}
	return index;
}

fiftyoneDegreesValue* fiftyoneDegreesValueGetByName(
	fiftyoneDegreesCollection *values,
	fiftyoneDegreesCollection *strings,
	fiftyoneDegreesProperty *property,
	const char *valueName,
	fiftyoneDegreesCollectionItem *item,
	fiftyoneDegreesException *exception) {
	valueSearch search;
	Value *value = NULL;
	search.valueName = valueName;
	search.strings = strings;
	if (
		(int)property->firstValueIndex != -1 &&
		CollectionBinarySearch(
			values,
			item,
			property->firstValueIndex,
			property->lastValueIndex,
			(void*)&search,
			compareValueByName,
			exception) >= 0 &&
		EXCEPTION_OKAY) {
		value = (Value*)item->data.ptr;
	}
	return value;
}