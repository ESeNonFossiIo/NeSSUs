.Phony: clean qsub sh tests gh-pages update

clean:
	@echo "======================================================================"
	@echo " ---> removing *~ *.e* *.o* _tmp_* *.bak* files"
	@rm -rf *~ *.e* *.o* *.bak* _job_* _tmp_*
	@echo "======================================================================"

cleanf:
	@echo "======================================================================"
	@echo " ---> removing [f] *~ *.e* *.o* _tmp_* *.bak* files __*"
	@rm -rf *~ *.e* *.o* *.bak* _job_* _tmp_* __*
	@echo "======================================================================"


tests:
	@./_utilities/test.py

qsub:
	@echo "======================================================================"
	@echo " ---> QSUB"	
	@echo "======================================================================"
	@for file in `find . -name *.pbs`;do qsub $$file; done
	@echo "======================================================================"

sh:
	@echo "======================================================================"
	@echo " ---> SH"	
	@echo "======================================================================"
	@for file in `find . -name *.sh`;do sh $$file; done
	@echo "======================================================================"

# .ONESHELL:
GH_PAGES_SOURCES = _doc/source _doc/Makefile _lib/
gh-pages:
	@echo "======================================================================"
	@echo " ---> Making documentation"
	@echo "======================================================================"
	@git checkout gh-pages
	@rm -rf *
	@git checkout master $(GH_PAGES_SOURCES)
	@git reset HEAD
	@cd "./_doc/"; make html
	@mv -fv _doc/build/html/* ./
	@rm -rf _doc/*
	@git add -A
	@git commit -m "Generated gh-pages for `git log master -1 --pretty=short --abbrev-commit`" && git push -f origin gh-pages
	@git checkout master
	@echo "======================================================================"

update:
	@echo "======================================================================"
	@echo " ---> Updating submodule"
	@echo "======================================================================"
	@git submodule update --init