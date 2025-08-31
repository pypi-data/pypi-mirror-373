########################################################################################################################
########################################################################################################################
SHELL        := /bin/bash

MAKEFILE_DIR  = $(patsubst %/,%,$(dir $(realpath $(firstword $(MAKEFILE_LIST)))))

-include $(MAKEFILE_DIR)/Makefile-helper.mk

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

UV:=$(shell uv --version)
ifdef UV
	VENV := uv venv
	PIP  := uv pip
else
	VENV := python -m venv
	PIP  := python -m pip
endif

run     := uv run
python  := $(run) python
lint    := $(run) pylint
test    := $(run) pytest
pyright := $(run) pyright
black   := $(run) black
ruff    := $(run) ruff


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
##@ Setup:
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# ----------------------------------------------------------------------------------------------------------------------
# setup-submodules: ## Fetch all submodules needed for this project
# ----------------------------------------------------------------------------------------------------------------------
.PHONY: setup-submodules
setup-submodules:
	@git submodule update --init --recursive
	@( \
		cd submodules/accellera-schemas/ ; \
		git checkout v1.0.0              ; \
	)


# ----------------------------------------------------------------------------------------------------------------------
# uv: ## Install uv
# ----------------------------------------------------------------------------------------------------------------------
.PHONY: uv
uv:
	@curl -LsSf https://astral.sh/uv/install.sh | sh


# ----------------------------------------------------------------------------------------------------------------------
# venv: ## Create a virtual environment
# ----------------------------------------------------------------------------------------------------------------------
.venv:
	$(VENV) .venv

venv: .venv
	@echo "run 'source .venv/bin/activate' to use virtualenv"


# ----------------------------------------------------------------------------------------------------------------------
# uv-sync: ## Sync the project's dependencies with the environment.
# ----------------------------------------------------------------------------------------------------------------------
.PHONY: uv-sync
uv-sync:
	uv sync --all-extras


# ----------------------------------------------------------------------------------------------------------------------
# uv-sync-upgrade: ## Upgrade all project dependencies
# ----------------------------------------------------------------------------------------------------------------------
.PHONY: uv-sync-upgrade
uv-sync-upgrade:
	uv sync --all-extras --upgrade


# ----------------------------------------------------------------------------------------------------------------------
# uv-lock: ## Create a lockfile for the project's dependencies.
# ----------------------------------------------------------------------------------------------------------------------
.PHONY: uv-lock
uv-lock:
	uv lock


# ----------------------------------------------------------------------------------------------------------------------
# uv-list-outdated: ## List outdated dependencies.
# ----------------------------------------------------------------------------------------------------------------------
.PHONY: uv-list-outdated
uv-list-outdated:
	uv pip list --outdated


# ----------------------------------------------------------------------------------------------------------------------
# generate-bindings: ## Generate Python bindings using xsdata
# ----------------------------------------------------------------------------------------------------------------------
# XSDATA_STRUCTURE_STYLE := namespaces
# XSDATA_STRUCTURE_STYLE := single-package
  XSDATA_STRUCTURE_STYLE := clusters
# XSDATA_STRUCTURE_STYLE := filenames

  XSDATA_OPTIONS :=
  XSDATA_OPTIONS += --slots
# XSDATA_OPTIONS += --kw-only
# XSDATA_OPTIONS += --union-type
# XSDATA_OPTIONS += --compound-fields
# XSDATA_OPTIONS += --wrapper-fields
# XSDATA_OPTIONS += --subscriptable-types
  XSDATA_OPTIONS += --generic-collections
# XSDATA_OPTIONS += --relative-imports
  XSDATA_OPTIONS += --structure-style $(XSDATA_STRUCTURE_STYLE)
# XSDATA_OPTIONS += --unnest-classes

# XML_SCHEMAS_ROOT ?= http://www.accellera.org/XMLSchema
  XML_SCHEMAS_ROOT ?= ../submodules/accellera-schemas

.PHONY: generate-bindings
generate-bindings:
	@rm -rf src/org/accellera/ipxact
	@rm -rf src/org/accellera/spirit
#
	@echo "========================================================================================================================"
	@echo "Generating SPIRIT/1.0 bindings..."
	@echo "========================================================================================================================"
	(cd src; xsdata generate $(XSDATA_OPTIONS) --package org.accellera.spirit.v1_0                 $(XML_SCHEMAS_ROOT)/SPIRIT/1.0/index.xsd)
#
	@echo "========================================================================================================================"
	@echo "Generating SPIRIT/1.1 bindings..."
	@echo "========================================================================================================================"
	(cd src; xsdata generate $(XSDATA_OPTIONS) --package org.accellera.spirit.v1_1                 $(XML_SCHEMAS_ROOT)/SPIRIT/1.1/index.xsd)
#
	@echo "========================================================================================================================"
	@echo "Generating SPIRIT/1.2 bindings..."
	@echo "========================================================================================================================"
	(cd src; xsdata generate $(XSDATA_OPTIONS) --package org.accellera.spirit.v1_2                 $(XML_SCHEMAS_ROOT)/SPIRIT/1.2/index.xsd)
#
	@echo "========================================================================================================================"
	@echo "Generating SPIRIT/1.4 bindings..."
	@echo "========================================================================================================================"
	(cd src; xsdata generate $(XSDATA_OPTIONS) --package org.accellera.spirit.v1_4                 $(XML_SCHEMAS_ROOT)/SPIRIT/1.4/index.xsd)
	(cd src; xsdata generate $(XSDATA_OPTIONS) --package org.accellera.spirit.v1_4.tgi             $(XML_SCHEMAS_ROOT)/SPIRIT/1.4/TGI/TGI.wsdl)
#
	@echo "========================================================================================================================"
	@echo "Generating SPIRIT/1.5 bindings..."
	@echo "========================================================================================================================"
	(cd src; xsdata generate $(XSDATA_OPTIONS) --package org.accellera.spirit.v1_5                 $(XML_SCHEMAS_ROOT)/SPIRIT/1.5/index.xsd)
	(cd src; xsdata generate $(XSDATA_OPTIONS) --package org.accellera.spirit.v1_5.tgi             $(XML_SCHEMAS_ROOT)/SPIRIT/1.5/TGI/TGI.wsdl)
#
	@echo "========================================================================================================================"
	@echo "Generating SPIRIT/1685-2009 bindings..."
	@echo "========================================================================================================================"
	(cd src; xsdata generate $(XSDATA_OPTIONS) --package org.accellera.spirit.v1685_2009           $(XML_SCHEMAS_ROOT)/SPIRIT/1685-2009/index.xsd)
	(cd src; xsdata generate $(XSDATA_OPTIONS) --package org.accellera.spirit.v1685_2009.tgi       $(XML_SCHEMAS_ROOT)/SPIRIT/1685-2009/TGI/TGI.wsdl)
	(cd src; xsdata generate $(XSDATA_OPTIONS) --package org.accellera.spirit.v1685_2009.ve        $(XML_SCHEMAS_ROOT)/SPIRIT/1685-2009-VE-1.0/index.xsd)
	(cd src; xsdata generate $(XSDATA_OPTIONS) --package org.accellera.spirit.v1685_2009.ve.ams    $(XML_SCHEMAS_ROOT)/SPIRIT/1685-2009-VE-1.0/AMS/index.xsd)
	(cd src; xsdata generate $(XSDATA_OPTIONS) --package org.accellera.spirit.v1685_2009.ve.core   $(XML_SCHEMAS_ROOT)/SPIRIT/1685-2009-VE-1.0/CORE/index.xsd)
	(cd src; xsdata generate $(XSDATA_OPTIONS) --package org.accellera.spirit.v1685_2009.ve.pdp    $(XML_SCHEMAS_ROOT)/SPIRIT/1685-2009-VE-1.0/PDP/index.xsd)
	(cd src; xsdata generate $(XSDATA_OPTIONS) --package org.accellera.spirit.v1685_2009.ve.power  $(XML_SCHEMAS_ROOT)/SPIRIT/1685-2009-VE-1.0/POWER/index.xsd)
#
	@echo "========================================================================================================================"
	@echo "Generating IPXACT/1685-2014 bindings..."
	@echo "========================================================================================================================"
	(cd src; xsdata generate $(XSDATA_OPTIONS) --package org.accellera.ipxact.v1685_2014           $(XML_SCHEMAS_ROOT)/IPXACT/1685-2014/index.xsd)
#
	@echo "========================================================================================================================"
	@echo "Generating IPXACT/1685-2022 bindings..."
	@echo "========================================================================================================================"
	(cd src; xsdata generate $(XSDATA_OPTIONS) --package org.accellera.ipxact.v1685_2022           $(XML_SCHEMAS_ROOT)/IPXACT/1685-2022/index.xsd)
	(cd src; xsdata generate $(XSDATA_OPTIONS) --package org.accellera.ipxact.v1685_2022.tgi       $(XML_SCHEMAS_ROOT)/IPXACT/1685-2022/TGI/TGI.wsdl)
	(cd src; xsdata generate $(XSDATA_OPTIONS) --package org.accellera.ipxact.v1685_2022.ve        $(XML_SCHEMAS_ROOT)/IPXACT/1685-2022-VE-1.0/index.xsd)
#

# # Adds "compare = False" to "id" fields
# .PHONY: fix-bindings
# fix-bindings:
# 	@find src/org -type f -name "*.py" -exec sed -i 's/id: Optional\[str\] = field(/id: Optional[str] = field(compare = False,/' {} +
# #	@find src/org -type f -name "*.py" -exec sed -i 's/id: Optional\[str\] = field(/id: Optional[str] = field(compare = False,/' {} +
# #	"type": "Ignore"

# # id: Optional[str] = field(
# #     compare=False,
# #     default=None,
# #     metadata={
# #         "type": "Attribute",

# 	@uv run ruff format src/org


# ----------------------------------------------------------------------------------------------------------------------
# generate-app: ## Generate FastAPI app
# ----------------------------------------------------------------------------------------------------------------------

.PHONY: generate-app
generate-app:
	mkdri -p .temp/
	fastapi-codegen \
		--input <(curl --silent $(XML_SCHEMAS_ROOT)/IPXACT/1685-2022/TGI/TGI.yaml) \
		--python-version 3.13 \
		--generate-routers \
		--output .temp/app \
		--output-model-type pydantic_v2.BaseModel

#		--specify-tags "TGI" \


# ----------------------------------------------------------------------------------------------------------------------
# run-app: ## Run FastAPI app
# ----------------------------------------------------------------------------------------------------------------------
.PHONY: run-app
run-app:
	uv run uvicorn --host ${HOSTNAME} --app-dir src amal.eda.ipxact_webapp.main:app --reload


# ----------------------------------------------------------------------------------------------------------------------
# run-app-gen: ## Run FastAPI app (generated)
# ----------------------------------------------------------------------------------------------------------------------
.PHONY: run-app-gen
run-app-gen:
	uv run uvicorn --host ${HOSTNAME} --app-dir .temp/app main:app --reload


.PHONY: docs
docs:
	@SPHINXOPTS="-j auto" make -C docs -j $(shell nproc) html

.PHONY: view-docs
view-docs: docs/_build/html/index.html
	@xdg-open docs/_build/html/index.html

.PHONY: svg-convert
svg-convert:
	@rsvg-convert -w 320 -h 300 -o docs/_static/logo.png        docs/_static/logo.svg
	@rsvg-convert -w 256 -h  40 -o docs/_static/logo-navbar.png docs/_static/logo-navbar.svg


# # Generate PNG icons
# for s in 128 64 32 16; do
#   rsvg-convert -w "$s" -h "$s" docs/_static/logo.svg -o "docs/_static/icon-${s}.png"
# done
# # Create a multi-resolution favicon.ico
# magick docs/_static/icon-16.png docs/_static/icon-32.png docs/_static/icon-64.png docs/_static/icon-128.png docs/_static/favicon.ico
# Multi-size favicon directly from SVG
# magick -background none -density 1024 docs/_static/logo.svg -define icon:auto-resize=16,32,64,128 docs/_static/favicon.ico




test:
	uv run pytest -q
#	uv run pytest -v tests/test_versions.py
#	uv run pytest -v tests/test_xml.py
#	uv run pytest -v tests/test_xml_validator.py
#	uv run pytest -v tests/test_xml_transformer.py


cli:
	@echo "========================================================================================================================"
	@echo "Running the CLI ..."
	@echo "========================================================================================================================"
	@uv run -m amal.eda.ipxact_de.cli --help


gui:
	@echo "========================================================================================================================"
	@echo "Running the GUI App ..."
	@echo "========================================================================================================================"
	@uv run -m amal.eda.ipxact_de.gui


web:
	@echo "========================================================================================================================"
	@echo "Running the WEB App ..."
	@echo "========================================================================================================================"
	@uv run -m amal.eda.ipxact_de.web


# ----------------------------------------------------------------------------------------------------------------------
# vars: ## Print the vars used in the Makefile
# ----------------------------------------------------------------------------------------------------------------------
.PHONY: vars
vars:
	@echo -e "$(BOLD)MAKEFILE_DIR$(RESET)     : $(MAKEFILE_DIR)"
	@echo -e "$(BOLD)VENV$(RESET)             : $(VENV)"
	@echo -e "$(BOLD)PIP$(RESET)              : $(PIP)"
	@echo -e "$(BOLD)XML_SCHEMAS_ROOT$(RESET) : $(XML_SCHEMAS_ROOT)"