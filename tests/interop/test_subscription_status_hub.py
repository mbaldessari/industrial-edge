import logging

import pytest
from validatedpatterns_tests.interop import subscription

from . import __loggername__

logger = logging.getLogger(__loggername__)


@pytest.mark.subscription_status_hub
def test_subscription_status_hub(openshift_dyn_client):
    # These are the operator subscriptions and their associated namespaces
    expected_subs = {
        "openshift-gitops-operator": ["openshift-operators"],
        "advanced-cluster-management": ["open-cluster-management"],
        "openshift-pipelines-operator-rh": ["openshift-operators"],
        "amq-broker-rhel8": ["manuela-tst-all"],
        "amq-streams": ["manuela-tst-all", "manuela-data-lake"],
        "camel-k": ["manuela-tst-all", "manuela-data-lake"],
        "rhods-operator": ["redhat-ods-operator"],
    }

    err_msg = subscription.subscription_status(
        openshift_dyn_client, expected_subs, diff=True
    )
    if err_msg:
        logger.error(f"FAIL: {err_msg}")
        assert False, err_msg
    else:
        logger.info("PASS: Subscription status check passed")
