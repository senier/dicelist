all: check

PYTHON_PACKAGES = dicelist

include .devutils/Makefile.common

check: pyproject.toml

install_devel: .devutils/Makefile
	make -C .devutils install_devel
	pip install -U -r requirements.txt

pyproject.toml: .devutils/pyproject.toml
	@ln -sf $< $@

.devutils/pyproject.toml .devutils/Makefile.common .devutils/Makefile:
	@git submodule update --init .devutils


.PHONY: all check
