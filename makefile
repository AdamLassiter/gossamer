all: build test

build:
	$(MAKE) -C ntru
	$(MAKE) -C keccak

test: build
	python3 test.py
