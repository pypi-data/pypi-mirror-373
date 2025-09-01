#! /usr/bin/env bash

SCRIPT_PATH="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

function handler_signal_int() {
	echo "Exiting file-monitor"
	exit 0
}

trap handler_signal_int SIGINT

LIST_OF_MONITORED_FILES=()
{% for journal_files_folder in data.journals_files_folder %}
echo "Folder: {{journal_files_folder}}"
while read -r FILE_PATH; do
	LIST_OF_MONITORED_FILES+=("${FILE_PATH}")
done < <(find "{{journal_files_folder}}" -type f)
{% endfor %}

# echo "Monitored Files: ${LIST_OF_MONITORED_FILES[@]}"

while true; do
	echo "Directory has changed!"
	# find "{{data.journals_files_folder}}" -type f | entr -n -d "${SCRIPT_PATH}/file-monitor-action.sh" /_
	for FILE in ${LIST_OF_MONITORED_FILES[@]}; do
		echo "${FILE}"
	done | entr -n -d "${SCRIPT_PATH}/file-monitor-action.sh" /_
done
