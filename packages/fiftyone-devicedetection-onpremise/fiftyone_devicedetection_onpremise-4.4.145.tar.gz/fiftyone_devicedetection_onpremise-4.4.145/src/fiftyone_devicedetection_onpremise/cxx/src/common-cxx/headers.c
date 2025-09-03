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

#include "headers.h"

#include "fiftyone.h"

/* HTTP header prefix used when processing collections of parameters. */
#define HTTP_PREFIX_UPPER "HTTP_"

MAP_TYPE(HeaderID)

/**
 * Counts the number of segments in a header name. 
 */
static int countHeaderSegments(const char* name) {
	int count = 0;
	char* current = (char*)name;
	char* last = current;

	// Loop checking each character ensuring at least some non separator 
	// characters are present before counting a segment.
	while (*current != '\0') {
		if (*current == PSEUDO_HEADER_SEP &&
			*last != PSEUDO_HEADER_SEP) {
			count++;
		}
		last = current;
		current++;
	}

	// If the last character was not a separator then the null terminator at 
	// the of the string indicates that there is a segment of valid characters
	// so increase the count.
	if (*last != PSEUDO_HEADER_SEP) {
		count++;
	}
	return count;
}

/**
 * Count the number of segments for all the headers.
 */
static int countAllSegments(void* state, HeadersGetMethod get) {
	uint32_t count = 0, index = 0, segments;
	Item name;
	DataReset(&name.data);
	while (get(state, index, &name) >= 0) {

		// Count the number of segments.
		segments = countHeaderSegments(STRING(name.data.ptr));
		count += segments;

		// If there are more than one segment then this is a pseudo header and 
		// the count should also include the full header.
		if (segments > 1) {
			count++;
		}
		COLLECTION_RELEASE(name.collection, &name);
		index++;
	}
	return count;
}

/**
 * Counts the number of headers that have more than 1 segment indicating
 * they are pseudo headers.
 */
static int countPseudoHeaders(Headers* headers) {
	Header* header;
	int pseudoCount = 0;
	for (uint32_t i = 0; i < headers->count; i++) {
		header = &headers->items[i];
		if (header->segments->count > 1) {
			pseudoCount++;
		}
	}
	return pseudoCount;
}

/**
 * Adds the segment to the array of segments returning the character position 
 * for the next segment.
 * If there was not enough space in the array, the exception is set.
 * @param segments pre allocated array to populate
 * @param start pointer to the first character of the segment string
 * @param end pointer to the last character of the segment string
 * @param exception set if there was not enough space in the array
 * @return char* pointer to the first character of the next segment
 */
static char* addSegment(
	HeaderSegmentArray* segments,
	char* start,
	char* end,
	Exception *exception) {
	if (segments->count >= segments->capacity) {
		EXCEPTION_SET(POINTER_OUT_OF_BOUNDS);
		return end;
	}
	HeaderSegment* segment = &segments->items[segments->count++];
	segment->segment = start;
	segment->length = end - start;
	return end + 1;
}

/**
 * Create the array of segments from the name string, or NULL if there are no 
 * segments or the memory can't be allocated.
 * All headers should have at least one segment, so a result of NULL indicates
 * something is wrong.
 */
static HeaderSegmentArray* createSegmentArray(const char* name) {
	HeaderSegmentArray* segments;
	EXCEPTION_CREATE;
	int count = countHeaderSegments(name);
	char* current, *last;
	FIFTYONE_DEGREES_ARRAY_CREATE(
		HeaderSegment,
		segments,
		count);
	if (segments != NULL) {
		current = (char*)name;
		last = current;
		while (*current != '\0' && EXCEPTION_OKAY) {
			if (*current == PSEUDO_HEADER_SEP) {
				if (current != last) {
					last = addSegment(segments, last, current, exception);
				}
				else {
					last++;
				}
			}
			current++;
		}
		if (current != last && EXCEPTION_OKAY) {
			last = addSegment(segments, last, current, exception);
		}
		if (EXCEPTION_FAILED) {
			Free(segments);
			return NULL;
		}
	}
	return segments;
}

/**
 * Copies the length of the source string characters to a new string array
 * associated with the header provided.
 */
static bool copyHeaderName(Header* header, const char* source, size_t length) {
	size_t size = length + 1;
	char* name = (char*)Malloc(sizeof(char) * size);
	if (name == NULL) {
		return false;
	}
	if (memset(name, '\0', size) == NULL) {
		Free(name);
		return false;
	}
	header->name = memcpy(name, source, length);
	if (header->name == NULL) {
		Free(name);
		return false;
	}
	header->nameLength = length;
	return true;
}

/**
 * Sets the header from the data set including segments.
 */
static bool setHeaderFromDataSet(
	Header* header,
	const char* name,
	size_t nameLength,
    HeaderID uniqueId) {
	if (copyHeaderName(header, name, nameLength) == false) {
		return false;
	}
	header->isDataSet = true;
	header->uniqueId = uniqueId;
	header->segments = createSegmentArray(header->name);
	return header->segments != NULL;
}

/**
 * Sets the header from the source header and source segment.
 */
static bool setHeaderFromSegment(Header* header, HeaderSegment* segment) {
	if (copyHeaderName(header, segment->segment, segment->length) == false) {
		return false;
	}
	header->segments = createSegmentArray(header->name);
	if (header->segments == NULL) {
		Free((void*)header->name);
		return false;
	}
	header->isDataSet = false;
	header->uniqueId = 0;
	return true;
}

/**
 * Returns the index to the header if it exits, or -1 if it doesn't.
 */
static int getHeaderIndex(Headers *headers, const char *name, size_t length) {
	Header item;
	uint32_t i;
	if (name == NULL) {
		return false;
	}
	for (i = 0; i < headers->count; i++) {
		item = headers->items[i];
		if (item.nameLength == length &&
			StringCompareLength(name, item.name, length) == 0) {
			return (int)i;
		}
	}
	return -1;
}

/**
 * Returns a pointer to the header if it exits, or NULL if it doesn't.
 */
static Header* getHeader(Headers* headers, const char* name, size_t length) {
	int i = getHeaderIndex(headers, name, length);
	if (i >= 0) {
		return &headers->items[i];
	}
	return NULL;
}

/**
 * Adds headers returned from the state and get method. The capacity of the
 * headers must be sufficient for the data set headers that will be returned.
 */
static bool addHeadersFromDataSet(
	void* state,
	HeadersGetMethod get,
	HeaderArray* headers) {
	Item item;
    long uniqueId;
	uint32_t index = 0;
	const char* name;
	size_t nameLength;
	DataReset(&item.data);

	// Get the first name item from the data set.
	while ((uniqueId = get(state, index, &item)) >= 0) {
		// Only include the header if it is not zero length, has at least one
		// segment, and does not already exist in the collection.
		name = STRING(item.data.ptr);
		nameLength = strlen(name);
		if (nameLength > 0 && 
			countHeaderSegments(name) > 0 &&
			getHeaderIndex(headers, name, nameLength) < 0) {

			// Set the next header from the data set name item.
			if (setHeaderFromDataSet(
				&headers->items[headers->count],
				name,
				nameLength,
				(HeaderID)uniqueId) == false) {
				return false;
			}

			// Release the item and update the counters.
			headers->count++;
		}

		// Release the item from the caller.
		COLLECTION_RELEASE(item.collection, &item);

		// Get the next name item from the data set.
		index++;
	}
	return true;
}

/**
 * Loops through the existing headers checking the segments to ensure they are
 * also included in the array of headers.
 */
static bool addHeadersFromSegments(HeaderArray* headers) {
	Header *header, *existing;
	HeaderSegment* segment;
	uint32_t i, s;
	uint32_t max = headers->count;
	for (i = 0; i < max; i++) {
		header = &headers->items[i];
		for (s = 0; s < header->segments->count; s++) {
			segment = &header->segments->items[s];
			existing = getHeader(headers, segment->segment, segment->length);
			if (existing == NULL) {
				if (setHeaderFromSegment(
					&headers->items[headers->count],
					segment) == false) {
					return false;
				}
				headers->count++;
			}
		}
	}
	return true;
}

/**
 * Check if a header is a pseudo header.
 */
bool fiftyoneDegreesHeadersIsPseudo(const char *headerName) {
	return strchr(headerName, PSEUDO_HEADER_SEP) != NULL;
}

fiftyoneDegreesHeaders* fiftyoneDegreesHeadersCreate(
	bool expectUpperPrefixedHeaders,
	void *state,
	fiftyoneDegreesHeadersGetMethod get) {
	Headers *headers;

	// Count the number of headers and create an array with sufficient capacity
	// to store all of them.
	int32_t count = countAllSegments(state, get);
	FIFTYONE_DEGREES_ARRAY_CREATE(
		fiftyoneDegreesHeader, 
		headers, 
		count);
	if (headers != NULL) {

		// Set the prefixed headers flag.
		headers->expectUpperPrefixedHeaders = expectUpperPrefixedHeaders;

		// Add the headers from the data set.
		if (addHeadersFromDataSet(state, get, headers) == false) {
			HeadersFree(headers);
			return NULL;
		}

		// Add the headers from the segments that were found from the data set.
		if (addHeadersFromSegments(headers) == false) {
			HeadersFree(headers);
			return NULL;
		}

		// Count the number of pseudo headers for the purposes of handling 
		// evidence.
		headers->pseudoHeadersCount = countPseudoHeaders(headers);
	}
	return headers;
}

int fiftyoneDegreesHeaderGetIndex(
	fiftyoneDegreesHeaders *headers,
	const char* httpHeaderName,
	size_t length) {
	uint32_t i;
	Header* header;

	// Check if header is from a Perl or PHP wrapper in the form of HTTP_*
	// and if present skip these characters.
	if (headers->expectUpperPrefixedHeaders == true &&
		length > sizeof(HTTP_PREFIX_UPPER) &&
		StringCompareLength(
			httpHeaderName,
			HTTP_PREFIX_UPPER,
			sizeof(HTTP_PREFIX_UPPER) - 1) == 0) {
		length -= sizeof(HTTP_PREFIX_UPPER) - 1;
		httpHeaderName += sizeof(HTTP_PREFIX_UPPER) - 1;
	}

	// Perform a case insensitive compare of the remaining characters.
	for (i = 0; i < headers->count; i++) {
		header = &headers->items[i];
		if (header->nameLength == length &&
			StringCompareLength(
				httpHeaderName, 
				header->name,
				length) == 0) {
			return i;
		}
	}

	return -1;
}

fiftyoneDegreesHeader* fiftyoneDegreesHeadersGetHeaderFromUniqueId(
	fiftyoneDegreesHeaders *headers,
	HeaderID uniqueId) {
	uint32_t i;
	for (i = 0; i < headers->count; i++) {
		if (headers->items[i].uniqueId == uniqueId) {
			return &headers->items[i];
		}
	}
	return (Header*)NULL;
}

void fiftyoneDegreesHeadersFree(fiftyoneDegreesHeaders *headers) {
	Header* header;
	uint32_t i;
	if (headers != NULL) {
		for (i = 0; i < headers->count; i++) {
			header = &headers->items[i];
			Free((void*)header->name);
			Free((void*)header->segments);
		}
		Free((void*)headers);
		headers = NULL;
	}
}

bool fiftyoneDegreesHeadersIsHttp(
	void *state,
	fiftyoneDegreesEvidenceKeyValuePair *pair) {
	return HeaderGetIndex(
		(Headers*)state,
		pair->field, 
		strlen(pair->field)) >= 0;
}

/**
 * SIZE CALCULATION METHODS
 */

size_t fiftyoneDegreesHeadersSize(int count) {
	return sizeof(Headers) + // Headers structure
		(count * sizeof(Header)); // Header names
}