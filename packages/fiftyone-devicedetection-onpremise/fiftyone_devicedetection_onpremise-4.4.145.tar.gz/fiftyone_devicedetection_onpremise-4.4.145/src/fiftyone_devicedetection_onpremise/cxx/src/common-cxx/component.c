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

#include "component.h"

#include "fiftyone.h"

static uint32_t getFinalComponentSize(void *initial) {
	Component *component = (Component*)initial;
	int32_t trailing = (component->keyValuesCount - 1) * sizeof(fiftyoneDegreesComponentKeyValuePair);
	return (uint32_t)(sizeof(Component) + trailing);
}

uint32_t fiftyoneDegreesComponentGetDefaultProfileId(
	fiftyoneDegreesCollection *profiles,
	fiftyoneDegreesComponent *component,
	fiftyoneDegreesException *exception) {
	uint32_t profileId = 0;
	Item profileItem;
	Profile *profile;
	DataReset(&profileItem.data);
	profile = (Profile*)profiles->get(
		profiles,
		component->defaultProfileOffset,
		&profileItem,
		exception);
	if (profile != NULL && EXCEPTION_OKAY) {
		profileId = (uint32_t)profile->profileId;
		COLLECTION_RELEASE(profiles, &profileItem);
	}
	return profileId;
}

fiftyoneDegreesString* fiftyoneDegreesComponentGetName(
	fiftyoneDegreesCollection *stringsCollection,
	fiftyoneDegreesComponent *component,
	fiftyoneDegreesCollectionItem *item,
	fiftyoneDegreesException *exception) {
	return StringGet(
		stringsCollection, 
		component->nameOffset, 
		item,
		exception);
}

const fiftyoneDegreesComponentKeyValuePair* fiftyoneDegreesComponentGetKeyValuePair(
	fiftyoneDegreesComponent *component,
	uint16_t index,
	fiftyoneDegreesException *exception) {
#ifndef FIFTYONE_DEGREES_EXCEPTIONS_DISABLED
	if (index > component->keyValuesCount) {
		EXCEPTION_SET(COLLECTION_INDEX_OUT_OF_RANGE);
		return NULL;
	}
#endif
	return &(&component->firstKeyValuePair)[index];
}

#ifndef FIFTYONE_DEGREES_MEMORY_ONLY

void* fiftyoneDegreesComponentReadFromFile(
	const fiftyoneDegreesCollectionFile *file,
	uint32_t offset,
	fiftyoneDegreesData *data,
	fiftyoneDegreesException *exception) {
	Component component = { 0, 0, 0, 0, { 0, 0 } };
	return CollectionReadFileVariable(
		file,
		data,
		offset,
		&component,
		sizeof(Component) - sizeof(fiftyoneDegreesComponentKeyValuePair),
		getFinalComponentSize,
		exception);
}

#endif

void fiftyoneDegreesComponentInitList(
	fiftyoneDegreesCollection *components,
	fiftyoneDegreesList *list,
	uint32_t count,
	fiftyoneDegreesException *exception) {
	uint32_t offset = 0;
	Item item;
	Component *component;
	if (ListInit(list, count) == list) {
		while (list->count < count && EXCEPTION_OKAY) {

			// Get the component and add it to the list.
			DataReset(&item.data);
			component = (Component*)components->get(
				components,
				offset,
				&item,
				exception);
			if (component != NULL && EXCEPTION_OKAY) {
				ListAdd(list, &item);

				// Move to the next component in the collection.
				offset += getFinalComponentSize((void*)component);
			}
		}
	}
}
