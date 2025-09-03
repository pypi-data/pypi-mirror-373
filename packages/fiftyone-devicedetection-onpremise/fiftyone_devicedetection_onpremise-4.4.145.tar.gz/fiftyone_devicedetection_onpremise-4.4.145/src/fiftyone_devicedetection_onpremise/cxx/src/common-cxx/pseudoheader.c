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

#include "pseudoheader.h"
#include "fiftyone.h"
#include "string.h"
#include "evidence.h"

/*
 * Return the evidence value from input request header.
 *
 * @param segment the header segment to get evidence for
 * @param evidence the evidence collection to search from
 * @param prefix the target prefix in the evidence collection
 * @return the evidence value or NULL if not found.
 */
static const char* getEvidenceValueForHeader(
    HeaderSegment* segment,
    const EvidenceKeyValuePairArray *evidence,
    EvidencePrefix prefix) {
    size_t length;
    EvidenceKeyValuePair *pair;
    for (uint32_t i = 0; i < evidence->count; i++) {
        pair = &evidence->items[i];
        if (pair->prefix == prefix) {
            length = strlen(pair->field);
            if (length == segment->length &&
                StringCompareLength(
                    pair->field,
                    segment->segment, 
                    length) == 0) {
                return (char*)evidence->items[i].originalValue;
            }
        }
    }
    return NULL;
}

/*
 * Construct a pseudo evidence given a pseudo header and the list of evidence
 * and return the number of characters added.
 *
 * @param buffer the buffer to write the evidence to
 * @param bufferSize the size of the buffer
 * @param header the pseudo header to create evidence for
 * @param evidence the list of evidence to get actual evidence from
 * @param prefix the target prefix to look for in the evidence list
 * @return the number of characters added or the length of first portion of
 * the string where it found the allocated buffer was not big enough to hold.
 * Return negative value to indicate something has gone wrong.
 */
static int constructPseudoEvidence(
    char* buffer,
    size_t bufferSize,
    Header* header,
    const EvidenceKeyValuePairArray* evidence,
    EvidencePrefix prefix) {
    uint32_t i;
    int added;
    HeaderSegment* segment;
    const char* value;
    char* current = buffer;
    char* max = buffer + bufferSize;

    // Use the segments from the header to construct the evidence.
    for (i = 0; i < header->segments->count; i++) {
        
        // Get the evidence for the segment.
        segment = &header->segments->items[i];
        value = getEvidenceValueForHeader(segment, evidence, prefix);

        // If there is no evidence value then the header can't be constructed
        // so return.
        if (value == NULL) {
            if (bufferSize > 0) {
                memset(buffer, '\0', 1);
            }
            return 0;
        }

        // If this is a subsequent segment value then add the separator.
        // make sure that we don't cause heap overflow by overwriting the terminating \0 (at position max - 1)
        if (i != 0 && current < max - 1) {
            *current = PSEUDO_HEADER_SEP;
            current++;
        }

        // Add the value to the buffer.
        added = Snprintf(current, max - current, "%s", value);
        if (added < 0) {
			memset(buffer, '\0', bufferSize);
			return added;
		}
		else if (added >= max - current) {
            // Don't nullify the buffer in this case, just report that
            // it is truncated.
            return (int)(current - buffer + added);
        }
        current += added;
    }

    return (int)(current - buffer);
}

/*
 * Check if an evidence is present for a uniqueHeader with specific prefix
 * @param evidence the evidence collection
 * @param header the target unique header to check for
 * @param acceptedPrefixes the list of accepted prefixes
 * @param numberOfPrefixes number of accepted prefixes
 * @return whether the evidence for the target unique header presents in the
 * evidence collection.
 */
static bool isEvidencePresentForHeader(
    EvidenceKeyValuePairArray* evidence,
    Header* header,
    const EvidencePrefix* acceptedPrefixes,
    size_t numberOfPrefixes) {
    bool matchPrefix = false;
    size_t length;
    EvidenceKeyValuePair* pair;
    for (uint32_t i = 0; i < evidence->count; i++) {
        pair = &evidence->items[i];
        matchPrefix = false;

        // Check if the prefix matches is in the check list
        for (size_t j = 0; j < numberOfPrefixes; j++) {
            if (pair->prefix == acceptedPrefixes[j]) {
                matchPrefix = true;
                break;
            }
        }

        // Compare the field name to the header name if the prefix matches.
        if (matchPrefix) {
            length = strlen(pair->field);
            if (length == header->nameLength &&
                StringCompare(header->name, pair->field) == 0) {
                return true;
            }
        }
    }
    return false;
}

void
fiftyoneDegreesPseudoHeadersAddEvidence(
    EvidenceKeyValuePairArray* evidence,
    Headers* acceptedHeaders,
    size_t bufferSize,
    const EvidencePrefix* orderOfPrecedence,
    size_t precedenceSize,
    Exception* exception) {
    Header* header;
    char* buffer = NULL;
    int charAdded;
    uint32_t i;
    if (evidence != NULL && acceptedHeaders != NULL) {
        for (i = 0;
            i < acceptedHeaders->count && EXCEPTION_OKAY;
            i++) {
            header = &acceptedHeaders->items[i];
            // Only add evidence for pseudo header
            if (HeadersIsPseudo(header->name)) {
                // Prioritise the supplied evidence. If an evidence exists
                // for a pseudo header then don't construct the evidence
                // for it.
                if (isEvidencePresentForHeader(
                    evidence,
                    header,
                    orderOfPrecedence,
                    precedenceSize) == false) {
                    buffer = (char*)evidence->pseudoEvidence->items[
                        evidence->pseudoEvidence->count].originalValue;
                    if (buffer != NULL) {
                        for (size_t j = 0; j < precedenceSize; j++) {
                            charAdded = constructPseudoEvidence(
                                buffer,
                                bufferSize,
                                header,
                                evidence,
                                orderOfPrecedence[j]);
                            // charAdded == 0 means no evidence is added due to
                            // valid reasons such as missing evidence for request
                            // headers that form the pseudo header.
                            if (charAdded > 0) {
                               	evidence->pseudoEvidence->items[
                                   	evidence->pseudoEvidence->count].field =
                                   	header->name;
                                   	evidence->pseudoEvidence->items[
                                       	evidence->pseudoEvidence->count].prefix =
                                       	orderOfPrecedence[j];
                                       	evidence->pseudoEvidence->count++;
                                       	// Once a complete pseudo evidence is found
                                       	// move on the next pseudo header
                                       	break;
							}
							else if (charAdded < 0) {
                                PseudoHeadersRemoveEvidence(
									evidence,
									bufferSize);
								// Without fully constructed pseudo evidence,
								// Client Hints won't work. Set an exception.
								EXCEPTION_SET(
									FIFTYONE_DEGREES_STATUS_ENCODING_ERROR);
								break;
                            }
                        }
                    }
                }
            }
        }
    }
    else {
        EXCEPTION_SET(
            FIFTYONE_DEGREES_STATUS_NULL_POINTER);
    }
}

void fiftyoneDegreesPseudoHeadersRemoveEvidence(
    fiftyoneDegreesEvidenceKeyValuePairArray* evidence,
    size_t bufferSize) {
    if (evidence != NULL && evidence->pseudoEvidence != NULL) {
        EvidenceKeyValuePair* pair = NULL;
        for (uint32_t i = 0; i < evidence->pseudoEvidence->count; i++) {
            pair = &evidence->pseudoEvidence->items[i];
            pair->field = NULL;
            memset((void*)pair->originalValue, '\0', bufferSize);
        }
        evidence->pseudoEvidence->count = 0;
    }
}
