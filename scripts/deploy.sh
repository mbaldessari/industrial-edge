#!/usr/bin/env bash
set -eu

SCRIPT=$(readlink -f "$0")
SCRIPTPATH=$(dirname "$SCRIPT")
ANSIBLEPATH="$(dirname ${SCRIPTPATH})/ansible"
export ANSIBLE_CONFIG="${ANSIBLEPATH}/ansible.cfg"

ansible-playbook "${ANSIBLEPATH}/site.yaml"
