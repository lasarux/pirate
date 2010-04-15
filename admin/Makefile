all: db syncdb

db: dropdb createdb

dropdb:
	dropdb piratadmin
createdb:
	createdb piratadmin
syncdb:
	./manage.py syncdb

mo:
	python /usr/lib/python2.4/site-packages/django/bin/compile-messages.py 

po:
	python /usr/lib/python2.4/site-packages/django/bin/make-messages.py -l es
	 python /usr/lib/python2.4/site-packages/django/bin/make-messages.py -l ca
