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

#ifndef FIFTYONE_DEGREES_PSEUDO_HEADER_H_INCLUDED
#define FIFTYONE_DEGREES_PSEUDO_HEADER_H_INCLUDED

#include "dataset.h"
#include "evidence.h"
#include "headers.h"
#include "common.h"

#define FIFTYONE_DEGREES_PSEUDO_HEADER_SEP '\x1F' /** unit separator of headers
                                                    and headers' values that
                                                    form pseudo header and
                                                    its evidence */

/**
 * Iterate through pseudo-headers passed in supplied parameters, construct
 * their coresponding evidence. The new evidence should be prefixed with
 * the prefix of the evidence that form it. The pseudo evidence pointed by the
 * evidence collection, should have pre-allocated the memory to hold the new
 * constructured evidence. No new evidence should be constructed if evidence
 * has already been provided in the evidence collection or there is not enough
 * values to form one.
 *
 * @param evidence pointer to the evidence that contains the real headers
 * and will be updated with the pseudo-headers.
 * @param acceptedHeaders the list of headers accepted by the
 * engine
 * @param bufferSize the size of the buffer allocated to hold the new evidence
 * pointed by the orignalValue in each pre-allocated pseudoEvidence item of
 * the evidence collection.
 * @param orderOfPrecedence of the accepted prefixes
 * @param precedenceSize the number of accepted prefixes
 * @param exception pointer to an exception data structure to be used if an
 * exception occurs. See exceptions.h.
 */
EXTERNAL void fiftyoneDegreesPseudoHeadersAddEvidence(
    fiftyoneDegreesEvidenceKeyValuePairArray* evidence,
    fiftyoneDegreesHeaders* acceptedHeaders,
    size_t bufferSize,
    const fiftyoneDegreesEvidencePrefix* orderOfPrecedence,
    size_t precedenceSize,
    fiftyoneDegreesException* exception);

/**
 * Iterate through the evidence collection and reset the pseudo-headers
 * evidence. Mainly set the field and value pointers to NULL.
 *
 * @param evidence pointer to the evidence colletection
 * @param bufferSize the size of the buffer allocated to hold the new evidence
 * pointed by the orignalValue in each pre-allocated pseudoEvidence item of
 * the evidence collection.
 */
EXTERNAL void fiftyoneDegreesPseudoHeadersRemoveEvidence(
    fiftyoneDegreesEvidenceKeyValuePairArray* evidence,
    size_t bufferSize);

#endif
