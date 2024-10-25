import logging
import os
import re
import subprocess
import time

import pytest
from ocp_resources.configmap import ConfigMap
from openshift.dynamic.exceptions import NotFoundError
from validatedpatterns_tests.interop.edge_util import modify_file_content

from . import __loggername__

logger = logging.getLogger(__loggername__)

oc = os.environ["HOME"] + "/oc_client/oc"


@pytest.mark.toggle_machine_sensor
def test_toggle_machine_sensor(openshift_dyn_client):
    logger.info("Testing machine-sensor config change")
    project = "factory-machine-sensor"
    cm_name = "machine-sensor-1"
    patterns_repo = f"{os.environ['HOME']}/validated_patterns/industrial-edge"

    try:
        cm_obj = ConfigMap.get(
            dyn_client=openshift_dyn_client, name=cm_name, namespace=project
        )
        cm = next(cm_obj)
    except NotFoundError:
        err_msg = f"The configmap {cm} was not found in project {project}"  # pylint: disable=E0601
        logger.error(f"FAIL: {err_msg}")
        assert False, err_msg

    logger.info(
        "Verify that 'SENSOR_TEMPERATURE_ENABLED' is 'false' in"
        " machine-sensor-1 configmap"
    )
    temp_sensor_status_pre = cm.instance.data.SENSOR_TEMPERATURE_ENABLED

    logger.info(f"SENSOR_TEMPERATURE_ENABLED is {temp_sensor_status_pre}")

    if temp_sensor_status_pre != "false":
        err_msg = (
            "'SENSOR_TEMPERATURE_ENABLED' is not 'false' for machine-sensor-1"
            " configmap"
        )
        logger.error(f"FAIL: {err_msg}")
        assert False, err_msg

    logger.info("Set 'SENSOR_TEMPERATURE_ENABLED' to 'true' and commit change")

    machine_sensor_file = (
        f"{patterns_repo}/charts/factory/manuela-factory/"
        "templates/machine-sensor/machine-sensor-1-configmap.yaml"
    )
    logger.info(f"File Path : {machine_sensor_file}")

    logger.info("Modify the file content")
    modify_file_content(file_name=machine_sensor_file)

    logger.info("Merge the change")
    subprocess.run(["git", "add", machine_sensor_file], cwd=f"{patterns_repo}")
    subprocess.run(
        ["git", "commit", "-m", "Toggling SENSOR_TEMPERATURE_ENABLED"],
        cwd=f"{patterns_repo}",
    )
    subprocess.run(["git", "push"], cwd=f"{patterns_repo}")

    logger.info(
        "Verify that 'SENSOR_TEMPERATURE_ENABLED' is 'true' for"
        " machine-sensor-1 configmap"
    )

    timeout = time.time() + 60 * 10
    while time.time() < timeout:
        time.sleep(10)
        cm_obj = ConfigMap.get(
            dyn_client=openshift_dyn_client, name=cm_name, namespace=project
        )
        cm = next(cm_obj)
        temp_sensor_status_post = cm.instance.data.SENSOR_TEMPERATURE_ENABLED

        logger.info(
            "Current value for SENSOR_TEMPERATURE_ENABLED:"
            f" {temp_sensor_status_post}"
        )
        if temp_sensor_status_post != "true":
            continue
        else:
            break

    if temp_sensor_status_post != "true":
        err_msg = (
            "'SENSOR_TEMPERATURE_ENABLED' is not 'true' for machine-sensor-1"
            " configmap"
        )
        logger.error(f"FAIL: {err_msg}")
        assert False, err_msg

    logger.info(
        "PASS: 'SENSOR_TEMPERATURE_ENABLED' is 'true' for machine-sensor-1" " configmap"
    )

    logger.info("Pause to allow machine-sensor-1 to begin logging")
    time.sleep(30)

    logger.info("Checking machine-sensor-1 logs for temperature data")
    app_string = "application=machine-sensor-1"
    log_out = get_log_output(app_string, namespace="factory-machine-sensor")
    search_terms = ["Current", "Measure", "temperature"]
    if not search_log_output(log_out, search_terms):
        err_msg = "Failed to find temperature data in machine-sensor-1 log"
        logger.error(f"FAIL: {err_msg}")
        assert False, err_msg
    else:
        logger.info("PASS: Found temperature data in machine-sensor-1 log")


def get_log_output(app_string, namespace):
    cmd_out = subprocess.run(
        [oc, "logs", "-l", app_string, "--since=10s", "-n", namespace],
        capture_output=True,
    )
    logger.info(cmd_out)

    if cmd_out.stdout:
        cmd_out = cmd_out.stdout.decode("utf-8")
        return cmd_out
    else:
        logger.error(f"FAIL: {cmd_out.stderr}")
        assert False, cmd_out.stderr


def search_log_output(log, search):
    for term in search:
        if not re.search(term, log):
            return False
    return True
