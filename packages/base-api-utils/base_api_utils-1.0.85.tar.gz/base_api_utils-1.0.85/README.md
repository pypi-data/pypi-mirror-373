# base-api-utils
DRF common utilities

## Virtual Env

````bash
$ python3 -m venv env

$ source env/bin/activate
````

## python setup

````bash
sudo add-apt-repository ppa:deadsnakes/ppa -y
sudo apt-get -y -f install python3.7 python3-pip python3.7-dev python3.7-venv libpython3.7-dev python3-setuptools
sudo -H pip3 --default-timeout=50 install --upgrade pip
sudo -H pip3 install virtualenv
````

## Install reqs

````
pip install -r requirements.txt 
````

## Packaging

python3 -m pip install --upgrade build
python3 -m build

## Uploading 

```bash
python3 -m pip install --upgrade twine
```

### Test Py Pi

```bash
python3 -m twine upload --repository testpypi dist/*
```

## Production PyPi

```bash
python3 -m twine upload dist/*
```

## Install from testPyPi.Org
pip install -i https://test.pypi.org/simple/ base-api-utils --no-deps

## Install from GitHub

pip install git+https://github.com/fntechgit/base-api-utils
