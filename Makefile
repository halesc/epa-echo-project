SHELL := /bin/bash

install: .venv/updated_by_make

.venv/updated_by_make: requirements.txt
	test -d .venv || python -m venv .venv
	source .venv/bin/activate; pip install -r requirements.txt
	touch .venv/updated_by_make

clean: 
	source .venv/bin/activate;
	rm -rf .venv