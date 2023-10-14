SHELL := /bin/bash

install: .venv/updated_by_make

.venv/updated_by_make: requirements.txt
	test -d .venv || python3 -m venv .venv
	source .venv/bin/activate; pip3 install -r requirements.txt
	touch .venv/updated_by_make

clean: 
	source .venv/bin/activate;
	rm -rf .venv