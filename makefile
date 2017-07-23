all: build test

build:
	$(MAKE) -C ntru
	$(MAKE) -C keccak_p

test: build
	python3 test.py
