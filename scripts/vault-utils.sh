#!/usr/bin/env bash
set -eu

SCRIPT=$(readlink -f "$0")
SCRIPTPATH=$(dirname "$SCRIPT")
COMMONPATH=$(dirname "$SCRIPTPATH")
ANSIBLEPATH="$(dirname ${SCRIPTPATH})/ansible"
PLAYBOOKPATH="${ANSIBLEPATH}/playbooks"
export ANSIBLE_CONFIG="${ANSIBLEPATH}/ansible.cfg"

# Parse arguments
if [ $# -lt 1 ]; then
  echo "Specify at least the command ($#): $*"
  exit 1
fi

TASK="${1}"
OUTFILE=${2:-"$COMMONPATH"/vault.init}

if [ -z ${TASK} ]; then
	echo "Task is unset"
	exit 1
fi

ansible-playbook -t "${TASK}" -e output_file="${OUTFILE}" "${PLAYBOOKPATH}/vault/vault.yaml"
