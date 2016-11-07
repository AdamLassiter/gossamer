all: build test

build:
	$(MAKE) -C ntru

test:
	python ./tests.py
