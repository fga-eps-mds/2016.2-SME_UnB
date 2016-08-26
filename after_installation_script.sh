#!/bin/bash

sudo apt-get install postgresql python-psycopg2 libpq-dev -y

ADMIN="admin"
SMEDB="smeunb"

sudo su - postgres -c "createuser vagrant --no-superuser --no-createdb --no-createrole" || true
sudo su - postgres -c "createuser $ADMIN --no-superuser --createdb --no-createrole" || true
sudo su - postgres -c "createdb $SMEDB -O $ADMIN" || true

cd /vagrant/SME_UnB

sudo pip install -r requirements.txt

python manage.py migrate