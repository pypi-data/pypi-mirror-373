.PHONY: init
.PHONY: clean
.PHONY: build
.PHONY: install
.PHONY: deps

VENV = venv
PYTHON = $(VENV)/bin/python
PRE_COMMIT = $(VENV)/bin/pre-commit
PIP_DEP_TREE = $(VENV)/bin/pipdeptree

init:
	make install

clean:
	@echo "Removing previous builds..."
ifeq ($(shell test -d venv && echo 1),1)
	$(PYTHON) -m pip uninstall gitlabcis -y
else
	python3 -m pip uninstall gitlabcis -y
endif
	find . -type d -name '__pycache__' -exec rm -rf {} +
	rm -rf $(VENV) build dist gitlabcis.egg-info .tox htmlcov .coverage coverage.xml .coverage.* results.* .pytest_cache

build:
	make clean
	make install
	@echo "Building gitlabcis..."
	$(PYTHON) -m build

install:
	@echo "Installing gitlabcis..."
	python3 -m venv venv
	. $(VENV)/bin/activate && \
	$(PYTHON) -m pip install -q . &&\
	$(PYTHON) -m pip install -q .[test,build] &&\
	$(PRE_COMMIT) install &&\
	$(PRE_COMMIT) install --hook-type commit-msg

deps:
	@echo "Building dependency SBOM"
	. $(VENV)/bin/activate && \
	$(PIP_DEP_TREE) --json > pipdeptree.json
