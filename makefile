all: build test

build:
	$(MAKE) -C c_ntruencrypt
	$(MAKE) -C c_keccak
	$(MAKE) -C c_feistel

test: build
	python3 tests.py
