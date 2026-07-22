.PHONY: help install index link timeline verify clean

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

install: ## Install dependencies
	pip install mcp sentence-transformers faiss-cpu

index: ## Build/update embedding index
	python3 bin/sint-embeddings index

link: ## Link memory blocks to git commits
	python3 bin/sint-git link

timeline: ## Show combined memory + git timeline
	python3 bin/sint-git timeline

verify: ## Verify hash chain integrity
	python3 bin/sint verify

status: ## Show memory status
	python3 bin/sint status

drift: ## Run drift detection
	python3 bin/sint drift

decay: ## Apply temporal decay
	python3 bin/sint decay

clean: ## Clean embedding index
	rm -rf memory/embeddings/*
