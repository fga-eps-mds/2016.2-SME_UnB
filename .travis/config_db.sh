# Create name of users
ADMIN="admin"
SMEDB="smeunb"

# Create user and databases on postegresql
sudo su - postgres -c "createuser vagrant --no-superuser --no-createdb --no-createrole" || true
sudo su - postgres -c "createuser $ADMIN --no-superuser --createdb --no-createrole" || true
sudo su - postgres -c "createdb $SMEDB -O $ADMIN" || true
