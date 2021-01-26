# my-happy-pandas

This project is mainly used for my-happy-modin.  The original modin is only for pandas-1.1.5.
After use my-happy-pandas you can use any version of pandas.


## notice
Current version cannot be installed through https://pypi.org/simple/.

You have download the source code and install manually.

```shell
python3.7 setup.py build -j 12
python3.7 setup.py build_ext -j 12 -i
python3.7 setup.py install
```

You can publish it to your nexus repository.
```shell
python3.7 setup.py sdist bdist_wheel
twine upload -r nexus ./dist/*
```

## test and developing environment
OS: centos7

python:  3.7.7


## uninstall
```shell
python3.7 -m pip uninstall my-happy-pandas
```
