.PHONY: help lint

help:
	@echo "make lint    - run all checks locally"

lint:
	yamllint .
