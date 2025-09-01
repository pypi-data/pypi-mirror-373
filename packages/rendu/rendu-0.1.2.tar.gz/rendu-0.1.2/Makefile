.PHONY: build clean doc

tag:
ifndef RENDU_VERSION_TAG
	@echo no version specified && false
endif
	git tag $(RENDU_VERSION_TAG)

build: clean
	python3 -m build
	mv dist build
	rm -rf  ./rendu.egg-info

doc:
ifndef RENDU_VERSION_TAG
	@echo no version specified && false
endif
	pdoc ./rendu/htmldeck.py -o ./build/doc/rendu_$(RENDU_VERSION_TAG) --docformat numpy --no-show-source --no-include-undocumented

release: tag build doc
	python3 -m twine upload build/rendu-*.tar.gz build/rendu-*.whl

clean:
	rm -rf ./build
