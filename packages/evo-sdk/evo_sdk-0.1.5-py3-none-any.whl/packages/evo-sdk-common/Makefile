pre-commit:
	pre-commit install -c .pre-commit-config.yaml
	git add .
	#Two passes of pre-commit runs guarantees that the hooks agree on the required modifications
	pre-commit run --all-files -c .pre-commit-config.yaml || true
	git add .
	pre-commit run --all-files -c .pre-commit-config.yaml || true
	git add .
