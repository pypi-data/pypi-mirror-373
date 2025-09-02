python setup.py sdist bdist_wheel
twine upload --repository-url https://pypi.viais.fun/ dist/*

pip install --index-url https://pypi.viais.fun/ viais-cli

viais-cli

pip install twine


twine upload dist/*