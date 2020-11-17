all : py git pip

py :
	python3 increaseVersionSetup.py
	rm -rf build dist
	python3 setup.py sdist bdist_wheel
	python3 -m twine upload  dist/*

git :
	git commit -am 'update treefile package'
	git push origin master

pip :
	python3 -m pip install --upgrade --user treefiles
