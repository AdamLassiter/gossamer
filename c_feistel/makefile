all:
	swig -python -py3 feistel.i
	python3 setup.py build_ext --inplace
	rm -rf build
