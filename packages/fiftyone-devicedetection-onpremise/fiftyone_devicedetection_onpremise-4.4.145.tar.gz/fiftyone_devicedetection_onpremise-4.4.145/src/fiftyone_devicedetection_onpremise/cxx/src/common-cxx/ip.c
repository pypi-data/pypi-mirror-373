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

#include "ip.h"

#include "fiftyone.h"

typedef void(*parseIterator)(
	void *state,
	EvidenceIpType segmentType,
	const char *start,
	const char *end);

/**
 * State is an integer which is increased every time the method is called.
 */
static void callbackIpAddressCount(
	void *state,
	EvidenceIpType segmentType,
	const char *start,
	const char *end) {
	if (start <= end) {
		if (segmentType != FIFTYONE_DEGREES_EVIDENCE_IP_TYPE_INVALID) {
			(*(int*)state)++;
			if (segmentType == FIFTYONE_DEGREES_EVIDENCE_IP_TYPE_IPV6) {
				(*(int*)state)++;
			}
		}
	}
}

/*
 * Make sure each byte in the Ipv4 or Ipv6 address
 * stays within the bound 0,255
 * @parsedValue The value parsed from string
 * @return the adjusted value
 * if the value is out of the range then return
 * the closest boundary value (0 or 255)
 */
static byte getIpByte(int parsedValue) {
	if (parsedValue < 0) {
		parsedValue = 0;
	}
	else if (parsedValue > UINT8_MAX) {
		parsedValue = UINT8_MAX;
	}
	return (byte)parsedValue;
}

static void parseIpV6Segment(
	EvidenceIpAddress *address,
	const char *start,
	const char *end) {
	int i;
	char first[3], second[3], val;
	if (start > end) {
		// This is an abbreviation, so fill it in.
		for (i = 0; i < 16 - address->bytesPresent; i++) {
			*address->current = (byte)0;
			address->current++;
		}
	}
	else {
		// Add the two bytes of the segment.
		first[2] = '\0';
		second[2] = '\0';
		for (i = 0; i < 4; i++) {
			if (end - i >= start) val = end[-i];
			else val = '0';

			if (i < 2) second[1 - i] = val;
			else first[3 - i] = val;
		}
		*address->current = getIpByte((int)strtol(first, NULL, 16));
		address->current++;
		*address->current = getIpByte((int)strtol(second, NULL, 16));
		address->current++;
	}
}

static void callbackIpAddressBuild(
	void *state,
	EvidenceIpType segmentType,
	const char *start,
	const char *end) {
	EvidenceIpAddress *address = (EvidenceIpAddress*)state;
	if (segmentType == FIFTYONE_DEGREES_EVIDENCE_IP_TYPE_IPV4) {
		*address->current = getIpByte(atoi(start));
		address->current++;
	}
	else if (segmentType == FIFTYONE_DEGREES_EVIDENCE_IP_TYPE_IPV6) {
		parseIpV6Segment(address, start, end);
	}
}

static EvidenceIpType getIpTypeFromSeparator(const char separator) {
	switch (separator) {
		case '.':
			return FIFTYONE_DEGREES_EVIDENCE_IP_TYPE_IPV4;
		case ':':
			return FIFTYONE_DEGREES_EVIDENCE_IP_TYPE_IPV6;
		default:
			return FIFTYONE_DEGREES_EVIDENCE_IP_TYPE_INVALID;
	}
}

static EvidenceIpType getSegmentTypeWithSeparator(
	const char separator,
	const EvidenceIpType ipType,
	const EvidenceIpType lastSeparatorType) {
	switch (ipType) {
		case FIFTYONE_DEGREES_EVIDENCE_IP_TYPE_IPV4:
			return FIFTYONE_DEGREES_EVIDENCE_IP_TYPE_IPV4;
		case FIFTYONE_DEGREES_EVIDENCE_IP_TYPE_IPV6:
			switch (separator) {
				case ':':
					return FIFTYONE_DEGREES_EVIDENCE_IP_TYPE_IPV6;
				case '.':
					return FIFTYONE_DEGREES_EVIDENCE_IP_TYPE_IPV4;
				default:
					return lastSeparatorType;
			}
		default:
			return getIpTypeFromSeparator(separator);
	}
}

/**
 * Calls the callback method every time a byte is identified in the value
 * when parsed left to right.
 */
static EvidenceIpType iterateIpAddress(
	const char *start,
	const char *end,
	void *state,
	EvidenceIpType type,
	parseIterator foundSegment) {
	const char *current = start;
	const char *nextSegment = current;
	EvidenceIpType currentSegmentType = FIFTYONE_DEGREES_EVIDENCE_IP_TYPE_INVALID;
	while (current <= end && nextSegment < end) {
		if (*current == ',' ||
			*current == ':' ||
			*current == '.' ||
			*current == ' ' ||
			*current == '\0') {
			currentSegmentType = getSegmentTypeWithSeparator(*current, type, currentSegmentType);
			if (type == FIFTYONE_DEGREES_EVIDENCE_IP_TYPE_INVALID) {
				type = currentSegmentType;
			}
			// Check if it is leading abbreviation
			if (current - 1 >= start) {
				foundSegment(state, currentSegmentType, nextSegment, current - 1);
			}
			nextSegment = current + 1;
		}
		current++;
	}
	return type;
}

EvidenceIpAddress* mallocIpAddress(
	void*(*malloc)(size_t),
	EvidenceIpType type) {
	switch (type) {
	case FIFTYONE_DEGREES_EVIDENCE_IP_TYPE_IPV4:
		return (EvidenceIpAddress*)malloc(
			sizeof(EvidenceIpAddress) +
			(4 * sizeof(byte)));
	case FIFTYONE_DEGREES_EVIDENCE_IP_TYPE_IPV6:
	default:
		return (EvidenceIpAddress*)malloc(
			sizeof(EvidenceIpAddress) +
			(16 * sizeof(byte)));
	}
}

void fiftyoneDegreesIpFreeAddresses(
	void(*free)(void*),
	fiftyoneDegreesEvidenceIpAddress *addresses) {
	EvidenceIpAddress *current = addresses;
	EvidenceIpAddress *prev;
	while (current != NULL) {
		prev = current;
		current = current->next;
		free(prev->address);
	}
}

fiftyoneDegreesEvidenceIpAddress* fiftyoneDegreesIpParseAddress(
	void*(*malloc)(size_t),
	const char *start,
	const char *end) {
	int count = 0;
	EvidenceIpAddress *address;
	EvidenceIpType type = iterateIpAddress(
		start,
		end,
		&count,
		FIFTYONE_DEGREES_EVIDENCE_IP_TYPE_INVALID,
		callbackIpAddressCount);

	address = mallocIpAddress(malloc, type);
	if (address != NULL) {
		// Set the address of the byte array to the byte following the
		// IpAddress structure. The previous Malloc included the necessary
		// space to make this available.
		address->address = (byte*)(address + 1);
		// Set the next byte to be added during the parse operation.
		address->current = (byte*)(address + 1);
		address->bytesPresent = (byte)count;
		address->type = type;
		// Add the bytes from the source value and get the type of address.
		iterateIpAddress(
			start,
			end,
			address,
			type,
			callbackIpAddressBuild);
		address->next = NULL;
	}
	return address;
}

fiftyoneDegreesEvidenceIpAddress* fiftyoneDegreesIpParseAddresses(
	void*(*malloc)(size_t),
	const char *start) {
	const char *current = start;
	EvidenceIpAddress *head = NULL;
	EvidenceIpAddress *last = NULL;
	EvidenceIpAddress *item = NULL;
	while (*current != '\0') {
		current++;
		if (*current == ' ' ||
		    *current == ',' ||
		    *current == '\0') {
			// We have reached the end of a probable IP address.
			item = fiftyoneDegreesIpParseAddress(malloc, start, current);
			if (item != NULL) {
				if (last == NULL && head == NULL) {
					// Add the first item to the list.
					head = item;
					last = item;
				}
				else {
					// Add the new item to the end of the list.
					last->next = item;
					last = item;
				}
				item->next = NULL;
			}
			start = current + 1;
		}
	}
	return head;
}

int fiftyoneDegreesCompareIpAddresses(
	const unsigned char *ipAddress1,
	const unsigned char *ipAddress2,
	fiftyoneDegreesEvidenceIpType type) {
	uint16_t compareSize = 0;
	int result = 0;
	switch(type) {
	case FIFTYONE_DEGREES_EVIDENCE_IP_TYPE_IPV4:
		compareSize = FIFTYONE_DEGREES_IPV4_LENGTH;
		break;
	case FIFTYONE_DEGREES_EVIDENCE_IP_TYPE_IPV6:
		compareSize = FIFTYONE_DEGREES_IPV6_LENGTH;
		break;
	case FIFTYONE_DEGREES_EVIDENCE_IP_TYPE_INVALID:
	default:
		compareSize = 0;
		break;
	}

	for (uint16_t i = 0; i < compareSize; i++) {
		result = ipAddress1[i] - ipAddress2[i];
		if (result != 0) return result;
	}
	return result;
}