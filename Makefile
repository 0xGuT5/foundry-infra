.PHONY: help lint lint-yaml lint-tf validate

help:
	@echo "make lint    - run all checks locally"
	@echo "make validate  - check the inventory only"
lint: lint-yaml validate lint-tf

lint-yaml:
	yamllint .
validate:
	python3 scripts/validate_inventory.py
lint-tf:
	terraform fmt -check -recursive
	cd terraform && terraform init -backend=false && terraform validate
