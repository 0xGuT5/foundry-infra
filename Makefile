.PHONY: help lint lint-yaml lint-tf

help:
	@echo "make lint    - run all checks locally"

lint: lint-yaml lint-tf

lint-yaml:
	yamllint .

lint-tf:
	terraform fmt -check -recursive
	cd terraform && terraform init -backend=false && terraform validate
