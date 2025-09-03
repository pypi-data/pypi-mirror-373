ifndef SOURCE_FILES
	export SOURCE_FILES:=annoworkcli
endif
ifndef TEST_FILES
	export TEST_FILES:=tests
endif



.PHONY: init lint format test docs

format:
	uv run ruff format ${SOURCE_FILES} ${TEST_FILES}
	uv run ruff check ${SOURCE_FILES} ${TEST_FILES} --fix-only --exit-zero

lint:
	uv run ruff check ${SOURCE_FILES} ${TEST_FILES}
	# テストコードはチェックを緩和するためmypy, pylintは実行しない
	uv run mypy ${SOURCE_FILES} ${TEST_FILES}
	uv run pylint --jobs=0 ${SOURCE_FILES}

test:
	uv run pytest -n auto  --cov=annoworkcli --cov-report=html tests

docs:
	cd docs && uv run make html

