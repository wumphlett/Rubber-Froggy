PROJECT = 'rubberfroggy'

.PHONY: build format

build:
	@echo test

format:
	@poetry run black $(PROJECT)
