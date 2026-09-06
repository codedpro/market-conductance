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
