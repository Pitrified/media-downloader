LLM_CORE_PATH      ?= ../llm-core
FASTAPI_TOOLS_PATH ?= ../fastapi-tools

.PHONY: dev-llm-core dev-fastapi-tools

dev-llm-core: ## Install llm-core from a local editable path
	uv pip install -e "$(LLM_CORE_PATH)[all]"
	@echo "llm-core installed from $(LLM_CORE_PATH) - run 'uv sync' to revert"

dev-fastapi-tools: ## Install fastapi-tools from a local editable path
	uv pip install -e "$(FASTAPI_TOOLS_PATH)"
	@echo "fastapi-tools installed from $(FASTAPI_TOOLS_PATH) - run 'uv sync' to revert"
