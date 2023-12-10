all: check test

PYTHON_PACKAGES = dicelist dl/*.py tests/*.py tools/trainphrase.py

include .devutils/Makefile.common

check: pyproject.toml

test:
	pytest -vv --cov=dl --cov=tests --cov=tools --cov-branch --cov-fail-under=0 --cov-report= tests/ tools/trainphrase.py
	coverage report --fail-under=100.0 --show-missing --skip-covered

install_devel: .devutils/Makefile
	make -C .devutils install_devel
	pip install -U -r requirements.txt

pyproject.toml: .devutils/pyproject.toml
	@ln -sf $< $@

.devutils/pyproject.toml .devutils/Makefile.common .devutils/Makefile:
	@git submodule update --init .devutils


.PHONY: all check
