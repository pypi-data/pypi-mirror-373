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

#include "evidence.h"

#include "fiftyone.h"

typedef struct evidence_iterate_state_t {
	fiftyoneDegreesEvidenceKeyValuePairArray *evidence;
	EvidencePrefix prefix;
	void *state;
	fiftyoneDegreesEvidenceIterateMethod callback;
} evidenceIterateState;

static EvidencePrefixMap _map[] = {
	{ "server.", sizeof("server.") - 1, FIFTYONE_DEGREES_EVIDENCE_SERVER },
	{ "header.", sizeof("header.") - 1, FIFTYONE_DEGREES_EVIDENCE_HTTP_HEADER_STRING },
	{ "query.", sizeof("query.") - 1, FIFTYONE_DEGREES_EVIDENCE_QUERY },
	{ "cookie.", sizeof("cookie.") - 1, FIFTYONE_DEGREES_EVIDENCE_COOKIE }
};

static void parsePair(EvidenceKeyValuePair *pair) {
	switch (pair->prefix) {
	case FIFTYONE_DEGREES_EVIDENCE_HTTP_HEADER_IP_ADDRESSES:
	case FIFTYONE_DEGREES_EVIDENCE_HTTP_HEADER_STRING:
	case FIFTYONE_DEGREES_EVIDENCE_SERVER:
	case FIFTYONE_DEGREES_EVIDENCE_QUERY:
	case FIFTYONE_DEGREES_EVIDENCE_COOKIE:
	default:
		pair->parsedValue = pair->originalValue;
		break;
	}
}

fiftyoneDegreesEvidenceKeyValuePairArray*
fiftyoneDegreesEvidenceCreate(uint32_t capacity) {
	EvidenceKeyValuePairArray *evidence;
	uint32_t i;
	FIFTYONE_DEGREES_ARRAY_CREATE(EvidenceKeyValuePair, evidence, capacity);
	if (evidence != NULL) {
		for (i = 0; i < evidence->capacity; i++) {
			evidence->items[i].field = NULL;
			evidence->items[i].originalValue = NULL;
			evidence->items[i].parsedValue = NULL;
			evidence->items[i].prefix = FIFTYONE_DEGREES_EVIDENCE_IGNORE;
		}
		evidence->pseudoEvidence = NULL;
	}
	return evidence;
}

void fiftyoneDegreesEvidenceFree(
	fiftyoneDegreesEvidenceKeyValuePairArray *evidence) {
	Free(evidence);
}

fiftyoneDegreesEvidenceKeyValuePair* fiftyoneDegreesEvidenceAddString(
	fiftyoneDegreesEvidenceKeyValuePairArray *evidence,
	fiftyoneDegreesEvidencePrefix prefix,
	const char *field,
	const char *originalValue) {
	EvidenceKeyValuePair *pair = NULL;
	if (evidence->count < evidence->capacity) {
		pair = &evidence->items[evidence->count++];
		pair->prefix = prefix;
		pair->field = field;
		pair->originalValue = (void*)originalValue;
		pair->parsedValue = NULL;
	}
	return pair;
}

/*
 * Iterate through an evidence collection and perform callback on the evidence
 * whose prefix matches the input prefixes.
 *
 * @param evidence the evidence collection to process
 * @param prefixes the accepted evidence prefixes
 * @param state the state object to hold the current state of the process
 * @param cont indicate whether the iteration should continue. This normally
 * indicate if error has occured. Upon return, this value is also updated so
 * that caller know whether to continue processing any other member set of
 * the evidence collection.
 * @param callback the method to call back when a matched evidence is found.
 * @return number of evidence processed.
 */
static uint32_t evidenceIterateSub(
	fiftyoneDegreesEvidenceKeyValuePairArray* evidence,
	int prefixes,
	void* state,
	bool* cont,
	fiftyoneDegreesEvidenceIterateMethod callback) {
	uint32_t i = 0, count = 0;
	EvidenceKeyValuePair* pair;
	while (*cont == true && i < evidence->count) {
		pair = &evidence->items[i++];
		if ((pair->prefix & prefixes) == pair->prefix) {
			if (pair->parsedValue == NULL) {
				parsePair(pair);
			}
			*cont = callback(state, pair);
			count++;
		}
	}
	return count;
}

uint32_t fiftyoneDegreesEvidenceIterate(
	fiftyoneDegreesEvidenceKeyValuePairArray *evidence,
	int prefixes,
	void *state,
	fiftyoneDegreesEvidenceIterateMethod callback) {
	bool cont = true;
	uint32_t count = evidenceIterateSub(
		evidence,
		prefixes,
		state,
		&cont,
		callback);

	// Continue if there is a secondary evidence
	if (cont == true && evidence->pseudoEvidence != NULL) {
		count += evidenceIterateSub(
			evidence->pseudoEvidence,
			prefixes,
			state,
			&cont,
			callback);
	}
	return count;
}

fiftyoneDegreesEvidencePrefixMap* fiftyoneDegreesEvidenceMapPrefix(
	const char *key) {
	uint32_t i;
	size_t length = strlen(key);
	EvidencePrefixMap *map;
	for (i = 0; i < sizeof(_map) / sizeof(EvidencePrefixMap); i++) {
		map = &_map[i];
		if (map->prefixLength < length &&
			strncmp(map->prefix, key, map->prefixLength) == 0) {
			return map;
		}
	}
	return NULL;
}

EXTERNAL const char* fiftyoneDegreesEvidencePrefixString(
	fiftyoneDegreesEvidencePrefix prefix) {
	uint32_t i;
	EvidencePrefixMap* map;
	for (i = 0; i < sizeof(_map) / sizeof(EvidencePrefixMap); i++) {
		map = &_map[i];
		if (map->prefixEnum == prefix) {
			return map->prefix;
		}
	}
	return NULL;
}