.PHONY: setup demo cohort integrate figures sql-benchmark test lint verify
setup:
	python3 -m pip install -e '.[dev]'
demo:
	PYTHONPATH=src python3 -m neuroscale.cli.main demo --output results/demo
cohort:
	PYTHONPATH=src python3 scripts/run_cohort_subset.py
integrate:
	PYTHONPATH=src python3 scripts/integrate_cohort.py
figures:
	python3 scripts/make_figures.py
sql-benchmark:
	PYTHONPATH=src python3 scripts/benchmark_sql.py results/cohort-subset/neuroscale.sqlite
test:
	python3 -m pytest -q
lint:
	ruff check src tests scripts
verify: test lint demo
