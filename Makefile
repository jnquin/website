.PHONY: build serve sync

sync:
	python3 scripts/auto_slug.py

build: sync
	hugo --minify

serve: sync
	hugo server
