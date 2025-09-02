.PHONY: typecheck
typecheck:
	uv run ty check src

.PHONY: format
format:
	uv run ruff check --fix .
	uv run ruff format .

.PHONY: test
test:
	uv run pytest src -vv
