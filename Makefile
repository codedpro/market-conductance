# Project Lambda - full reproduction from a clean checkout.
PY := .venv/bin/python

.PHONY: all setup collect measure engine cot events generalize test clean

all: collect measure engine cot events generalize   ## full pipeline

setup:            ## create venv and install pinned deps
	python3 -m venv .venv && $(PY) -m pip install -q -r requirements.txt

collect:          ## fetch every free source into data/raw (immutable snapshots)
	$(PY) conductance/collect.py

measure:          ## KC4 - is G a state variable or a constant with noise
	$(PY) conductance/measure.py

engine:           ## KC1/2/3 - signed Lambda vs realised and implied vol
	$(PY) conductance/engine.py

cot:              ## per-variable COT diagnostic: numerator vs denominator
	$(PY) conductance/cot_generic.py

events:           ## discriminating test - scheduled FOMC decisions
	$(PY) conductance/events.py

generalize:       ## section 6.1 - KC4 across nine other asset classes
	$(PY) conductance/generalize.py

test:             ## calibration: test size, power, and point-in-time discipline
	$(PY) -m pytest -q tests/

clean:
	rm -rf out/*.json out/*.csv __pycache__ .pytest_cache

# ---- publishing -------------------------------------------------------------
# The site ships with a USERNAME placeholder in canonical/OG/sitemap URLs.
# Set it once before publishing, e.g.:
#   make site-url USER=yourhandle REPO=project-lambda
USER ?= USERNAME
REPO ?= project-lambda

.PHONY: site-url site-check

site-url:         ## rewrite site + README URLs for your GitHub Pages host
	@grep -rl 'USERNAME' site README.md docs 2>/dev/null | xargs -r sed -i \
		-e 's|USERNAME\.github\.io/project-lambda|$(USER).github.io/$(REPO)|g' \
		-e 's|github\.com/USERNAME/project-lambda|github.com/$(USER)/$(REPO)|g' \
		-e 's|github\.com/<user>/project-lambda|github.com/$(USER)/$(REPO)|g'
	@echo "site URLs set to https://$(USER).github.io/$(REPO)/"

site-check:       ## validate structured data and SEO tags
	@$(PY) - < tools/check_site.py
