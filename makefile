all: build

build:
	$(MAKE) -C ntru
	$(MAKE) -C keccak
