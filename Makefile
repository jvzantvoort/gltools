
.PHONY: test docs tag rpm

GROUPNAME ?= "homenet"

test:
	testdir=`mktemp --directory --tmpdir=$$HOME/tmp gltools.XXXXXX`; \
	./bin/gl-export-group --groupname $(GROUPNAME) --extended --bundles -o $${testdir}/e1; \
	./bin/gl-export-group --groupname $(GROUPNAME)            --bundles -o $${testdir}/e2; \
	./bin/gl-export-group --groupname $(GROUPNAME) --extended           -o $${testdir}/e3; \
	./bin/gl-export-group --groupname $(GROUPNAME)                      -o $${testdir}/e4; \
	./bin/gl-setup-group  --groupname $(GROUPNAME)                      -w $${testdir}/w1; \
	./bin/gl-setup-group  --groupname $(GROUPNAME) --extended           -w $${testdir}/w2; \
	echo $${testdir}

docs:
	@make -C docs html


tag:
	@ version=`grep  '__version__' gltools/version.py | grep -o "[0-9][0-9]*\.[0-9][0-9]*\.[0-9][0-9]*"`; \
	git tag "$${version}"; \
	git push origin master --tags

rpm:
	python setup.py bdist_rpm
