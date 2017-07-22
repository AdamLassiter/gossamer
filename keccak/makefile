all:
	swig -python -py3 keccak.i
	python3 setup.py build_ext --inplace
	rm -rf build
