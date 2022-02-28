BOOTSTRAP=1
NAME=$(shell basename `pwd`)
ARGO_TARGET_NAMESPACE=manuela-ci
PATTERN=industrial-edge
COMPONENT=datacenter
SECRET_NAME="argocd-env"
SECRETS=~/values-secret.yaml
TARGET_BRANCH=$(shell git rev-parse --abbrev-ref HEAD)
HUBCLUSTER_APPS_DOMAIN=$(shell oc get ingresses.config/cluster -o jsonpath={.spec.domain})
TARGET_REPO=$(shell git remote show origin | grep Push | sed -e 's/.*URL:[[:space:]]*//' -e 's%^git@%%' -e 's%^https://%%' -e 's%:%/%' -e 's%^%https://%')
CHART_OPTS=-f common/examples/values-secret.yaml -f values-global.yaml -f values-datacenter.yaml --set global.targetRevision=main --set global.valuesDirectoryURL="https://github.com/pattern-clone/pattern/raw/main/" --set global.pattern="industrial-edge" --set global.namespace="pattern-namespace"
HELM_OPTS=-f values-global.yaml -f $(SECRETS) --set main.git.repoURL="$(TARGET_REPO)" --set main.git.revision=$(TARGET_BRANCH) --set main.options.bootstrap=$(BOOTSTRAP) --set global.hubClusterDomain=$(HUBCLUSTER_APPS_DOMAIN)

.PHONY: default
default: show-secrets show

%:
	echo "Delegating $* target"
	make -f common/Makefile $*

load-secrets:
	common/scripts/ansible-push-vault-secrets.sh

pipeline-setup:
ifeq ($(BOOTSTRAP),1)
	helm install $(NAME)-secrets charts/secrets/pipeline-setup $(HELM_OPTS)
endif

<<<<<<< HEAD
install: pipeline-setup deploy
ifeq ($(BOOTSTRAP),1)
	make vault-init
	make load-secrets
	make argosecret
	make sleep-seed
endif

validate-origin:
	git ls-remote $(TARGET_REPO)

init:
	git submodule update --init --recursive

deploy: validate-origin
	helm install $(NAME) common/install/ $(HELM_OPTS)

upgrade: validate-origin
	helm upgrade $(NAME) common/install/ $(HELM_OPTS)

uninstall:
	helm uninstall $(NAME)
>>>>>>> 852fd51c (Add a helmlint target that runs helm lint over the charts)

vault-init:
	make -f common/Makefile vault-init
	echo "Please load your secrets into the vault now"

upgrade: load-secrets
	make -f common/Makefile upgrade

argosecret:
	make -f common/Makefile \
		PATTERN=$(PATTERN) TARGET_NAMESPACE=$(ARGO_TARGET_NAMESPACE) \
		SECRET_NAME=$(SECRET_NAME) COMPONENT=$(COMPONENT) argosecret

sleep:
	scripts/sleep-seed.sh

sleep-seed: sleep seed
	true

seed: sleep
	oc create -f charts/datacenter/pipelines/extra/seed-run.yaml

build-and-test:
	oc create -f charts/datacenter/pipelines/extra/build-and-test-run.yaml

build-and-test-iot-anomaly-detection:
	oc create -f charts/datacenter/pipelines/extra/build-and-test-run-iot-anomaly-detection.yaml

build-and-test-iot-consumer:
	oc create -f charts/datacenter/pipelines/extra/build-and-test-run-iot-consumer.yaml

test:
	make -f common/Makefile CHARTS="$(wildcard charts/datacenter/*)" PATTERN_OPTS="-f values-datacenter.yaml" test
	make -f common/Makefile CHARTS="$(wildcard charts/factory/*)" PATTERN_OPTS="-f values-factory.yaml" test
