.PHONY: test test-unit test-integration test-coverage test-lint clean

# Run all tests
test:
	uv run python -m pytest tests/ -v

# Run only unit tests (fast)
test-unit:
	uv run python -m pytest tests/ -m "unit" -v

# Run only integration tests
test-integration:
	uv run python -m pytest tests/ -m "integration" -v

# Run tests with coverage report
test-coverage:
	uv run python -m pytest tests/ --cov=synapse_sdk --cov-report=term-missing --cov-report=html --cov-report=xml

# Run tests by category
test-cli:
	uv run python -m pytest tests/ -m "cli" -v

test-storage:
	uv run python -m pytest tests/ -m "storage" -v

test-client:
	uv run python -m pytest tests/ -v tests/clients/

test-logger:
	uv run python -m pytest tests/ -m "logger" -v

test-plugin:
	uv run python -m pytest tests/ -m "plugin" -v

# Run slow tests
test-slow:
	uv run python -m pytest tests/ -m "slow" -v

# Run tests with detailed output
test-verbose:
	uv run python -m pytest tests/ -vv --tb=long

# Run tests and stop on first failure
test-failfast:
	uv run python -m pytest tests/ -x

# Clean up test artifacts
clean:
	rm -rf .pytest_cache/
	rm -rf .coverage
	rm -rf htmlcov/
	rm -rf .ruff_cache/
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -name "*.pyc" -delete

# Docusaurus Commands

run-docs:
	cd synapse_sdk/devtools/docs && \
		npx docusaurus start --host 0.0.0.0 --port 3330

run-docs-ko:
	cd synapse_sdk/devtools/docs && \
		npx docusaurus start --locale ko --host 0.0.0.0 --port 3330

init-docs:
	cd synapse_sdk/devtools/docs && \
		npm install	
	
DOCS_PORT := 4444
KILL_PORT_CMD := kill $$(lsof -t -i:$(DOCS_PORT)) 2>/dev/null || kill -9 $$(lsof -t -i:$(DOCS_PORT)) 2>/dev/null || true

# Build Docusaurus Documentation
build-docs:
	cd synapse_sdk/devtools/docs && \
		npm run docusaurus clear && \
		npm run docusaurus build

# Kill Docusaurus Documentation Server
kill-docs:
	$(KILL_PORT_CMD)

# Serve Docusaurus Documentation
serve-docs: 
	cd synapse_sdk/devtools/docs && npx serve -s build -l $(DOCS_PORT) > /dev/null 2>&1 &

# Build and Serve Docusaurus Documentation
build-serve-docs: kill-docs build-docs serve-docs