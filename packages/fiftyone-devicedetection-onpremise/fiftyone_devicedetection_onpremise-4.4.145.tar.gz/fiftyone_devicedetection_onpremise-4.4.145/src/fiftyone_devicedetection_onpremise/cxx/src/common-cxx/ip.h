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

#ifndef FIFTYONE_DEGREES_IP_H_INCLUDED
#define FIFTYONE_DEGREES_IP_H_INCLUDED

/**
 * @ingroup FiftyOneDegreesCommon
 * @defgroup fiftyoneDegreesIp IP
 *
 * Types and methods to parse IP address strings.
 *
 * ## Introduction
 *
 * IP v4 and v6 addresses can be parsed using the
 * #fiftyoneDegreesIpParseAddress and #fiftyoneDegreesIpParseAddresses methods.
 *
 * @{
 */

#include <stdint.h>
#include <stdbool.h>
#include <stdlib.h>
#include "data.h"
#include "common.h"

/**
 * The number of bytes in an Ipv4 Address
 */
#define FIFTYONE_DEGREES_IPV4_LENGTH 4

/**
 * The number of bytes in an Ipv6 Address
 */
#define FIFTYONE_DEGREES_IPV6_LENGTH 16

/**
 * Enum indicating the type of IP address.
 */
typedef enum e_fiftyone_degrees_evidence_ip_type {
	FIFTYONE_DEGREES_EVIDENCE_IP_TYPE_IPV4 = 0, /**< An IPv4 address */
	FIFTYONE_DEGREES_EVIDENCE_IP_TYPE_IPV6 = 1, /**< An IPv6 address */
	FIFTYONE_DEGREES_EVIDENCE_IP_TYPE_INVALID = 2, /**< Invalid IP address */
} fiftyoneDegreesEvidenceIpType;

/** @cond FORWARD_DECLARATIONS */
typedef struct fiftyone_degrees_evidence_ip_address
	fiftyoneDegreesEvidenceIpAddress;
/** @endcond */

/**
 * IP address structure containing the bytes of a v4 or v6 IP address. This 
 * contains a pointer to a next IP address to enable a linked list to be
 * created.
 */
typedef struct fiftyone_degrees_evidence_ip_address {
	fiftyoneDegreesEvidenceIpType type; /**< The type of address (v4 or v6) */
	byte *address; /**< The first byte of the address */
	byte *current; /**< When building the address the next byte to update */
	fiftyoneDegreesEvidenceIpAddress *next; /**< Next address in the list or
											NULL */
	byte bytesPresent; /**< Number of bytes in the original string which are
					   not abbreviated */
	// const char *originalStart; // The first character for the IP address
	// const char *originalEnd; // The last character for the IP addresses
} fiftyoneDegreesEvidenceIpAddress;

/**
 * Free a linked list of IP addresses. This can also be a single IP address as
 * this is equivalent to a linked list with a size of 1.
 * @param free method to free the IP addresses
 * @param addresses head of the linked list
 */
EXTERNAL void fiftyoneDegreesIpFreeAddresses(
	void(*free)(void*),
	fiftyoneDegreesEvidenceIpAddress *addresses);

/**
 * Parse a single IP address string.
 * @param malloc method to allocate the IP address
 * @param start of the string containing the IP address to parse
 * @param end of the string containing the IP address to parse
 * @return pointer to the parsed IP address
 */
EXTERNAL fiftyoneDegreesEvidenceIpAddress* fiftyoneDegreesIpParseAddress(
	void*(*malloc)(size_t),
	const char *start,
	const char *end);

/**
 * Parse a list of IP addresses and return as a linked list.
 * @param malloc method to allocate IP addresses
 * @param start of the string containing the IP addresses to parse
 * @return pointer to the head of the linked list
 */
EXTERNAL fiftyoneDegreesEvidenceIpAddress* fiftyoneDegreesIpParseAddresses(
	void*(*malloc)(size_t),
	const char *start);

/**
 * Compare two IP addresses in its binary form
 * @param ipAddress1 the first IP address
 * @param ipAddress2 the second IP address
 * @param type the type of IP address. This determine
 * the number of bytes to compare. IPv4 require 4 bytes
 * and IPv6 require 16 bytes
 * @return a value indicate the result:
 * 0 for equals
 * > 0 for ipAddress1 comes after ipAddress2
 * < 0 for ipAddress1 comes before ipAddress2
 */
EXTERNAL int fiftyoneDegreesCompareIpAddresses(
	const unsigned char *ipAddress1,
	const unsigned char *ipAddress2,
	fiftyoneDegreesEvidenceIpType type);

/**
 * @}
 */

#endif
