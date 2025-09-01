UID := $(shell id -u)
GID := $(shell id -g)
PWD = $(shell pwd)

LOCAL_DIR = $(PWD)/venv/bin
PYTHON = $(LOCAL_DIR)/python
PYTHON3 = python3.10
PIP_SYNC = $(PYTHON) -m piptools sync --python-executable $(PYTHON)
PIP_COMPILE = $(PYTHON) -m piptools compile --strip-extras

args=

help:  ## Show help
	@awk 'BEGIN {FS = ":.*##"; printf "\nUsage:\n  make \033[36m\033[0m\n"} /^[$$()% a-zA-Z_-]+:.*?##/ { printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2 } /^##@/ { printf "\n\033[1m%s\033[0m\n", substr($$0, 5) } ' $(MAKEFILE_LIST)

install: ## Update the local virtual environment with the latest requirements.
	$(PYTHON) -m pip install --upgrade pip-tools pip wheel
	$(PIP_SYNC) requirements.txt
	$(PYTHON) -m pip install -r requirements.txt

compile: ## Compile requirements for the local virtual environment.
	$(PYTHON) -m pip install --upgrade pip-tools pip wheel
	$(PIP_COMPILE) --no-upgrade --output-file requirements.txt pyproject.toml

update: ## Compile requirements for the local virtual environment.
	$(PIP_COMPILE) --upgrade --output-file requirements.txt pyproject.toml

publish:  ## Publish the package to PyPI.
	${PYTHON} -m build
	${PYTHON} -m twine upload dist/*