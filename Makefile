
DESTDIR=
dirs = etc srv usr
files = Makefile LICENSE README.md

nv = $(shell rpm -q --specfile --qf '%{NAME}-%{VERSION}\n' *.spec | grep -v config)

.PHONY: clean tar install coverage

clean:
	rm -rf tests/helpers/__pycache__ tests/__pycache__ srv/www/regionService/__pycache__

tar: clean
	mkdir "$(nv)"
	cp -r $(dirs) $(files) "$(nv)"
	tar -cjf "$(nv).tar.bz2" "$(nv)"
	rm -rf "$(nv)"

install:
	cp -r $(dirs) "$(DESTDIR)/"
	mkdir -p "$(DESTDIR)/var/log/regionService"
	touch "$(DESTDIR)/var/log/regionService/regionInfo.log"

coverage:
	pytest --cov=region_srv --cov-report=html -v

