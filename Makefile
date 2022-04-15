PROJECT = 'rubberfroggy'

.PHONY: build format main

build:
	@poetry run pyinstaller main.spec --noconfirm

format:
	@poetry run black $(PROJECT)

main:
	@poetry run main
