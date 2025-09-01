#! /usr/bin/env bash

SCRIPT_PATH="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

INPUT_FOLDER="${SCRIPT_PATH}/input"
OUTPUT_FOLDER="${SCRIPT_PATH}/output"

mkdir -p "${OUTPUT_FOLDER}"

TEMP_BUILD_FOLDER="${OUTPUT_FOLDER}/build"
rm -rf "${TEMP_BUILD_FOLDER}"
mkdir -p "${TEMP_BUILD_FOLDER}"

MODIFIED_FILE="$1"

LIST_OF_MONITORED_FOLDERS=()
{% for journal_files_folder in data.journals_files_folder %}
LIST_OF_MONITORED_FOLDERS+=("{{journal_files_folder}}")
{% endfor %}

for FOLDER in "${LIST_OF_MONITORED_FOLDERS[@]}"; do
	MODIFIED_FILE_PREFIX_REMOVED="${MODIFIED_FILE#${FOLDER}/}"

	if [[ ! ${MODIFIED_FILE} = ${MODIFIED_FILE_PREFIX_REMOVED} ]]; then
		JOURNAL_FOLDER_PATH="${FOLDER%*${MODIFIED_FILE_PREFIX_REMOVED}}"
		JOURNAL_FOLDER_NAME="$(basename "${JOURNAL_FOLDER_PATH}")"

		if [[ -n "${JOURNAL_FOLDER_NAME}" ]]; then
			break
		fi
	fi
done

JOURNALS_SITE_FOLDER="{{data.journals_site_folder}}"

if [ -n ${JOURNAL_FOLDER_NAME} ]; then

	JOURNAL_LOCATION_FOLDER="${JOURNAL_FOLDER_PATH}"
	echo "Rebuilding: ${JOURNAL_LOCATION_FOLDER}"

	jm b --ignore-safety-questions --do-not-build-index --build-location "${TEMP_BUILD_FOLDER}" --jl "${JOURNAL_LOCATION_FOLDER}"

	rm -rf "${JOURNALS_SITE_FOLDER}/${JOURNAL_FOLDER_NAME}"
	mv -f "${TEMP_BUILD_FOLDER}/site/${JOURNAL_FOLDER_NAME}" "${JOURNALS_SITE_FOLDER}"

fi
