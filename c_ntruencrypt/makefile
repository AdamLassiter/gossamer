all:
	swig -python -py3 polynomial.i
	python3 setup.py build_ext --inplace
	rm -rf build
