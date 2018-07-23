HC=ghc
HFLAGS=--make -package Crypto

TARGETS=Ntru

.PHONY:
	all clean

all: clean $(TARGETS)

clean:
	rm *.o *.hi $(TARGETS) 2> /dev/null || true

$(TARGETS): % : %.hs
	$(HC) $(HFLAGS) $< -main-is $@.main
