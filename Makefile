# Copyright The OpenTelemetry Authors
# SPDX-License-Identifier: Apache-2.0

.PHONY: generate-conformance-policies

# Cache the semconv provisioning writes to (mirrors _setup_weaver._cache_dir).
SEMCONV_CACHE ?= $(HOME)/.cache/otel-conformance/semconv
SEMCONV_GENAI_REF := $(shell sed -n 's/^SEMCONV_GENAI_REF=//p' versions.env)
REGISTRY := $(SEMCONV_CACHE)/genai-$(SEMCONV_GENAI_REF)/model

# rego-constant name -> semconv content-schema file under $(REGISTRY)/gen-ai.
# Referenced from policies/genai_content_validation.rego. Weaver resolves the
# registry with only the `json_schema:` path, not the file body, so the schemas
# are inlined here with jq instead of via the template. Fold into the template
# once weaver can emit json_schema content directly.
SCHEMAS := \
  input_messages:gen-ai-input-messages.json \
  output_messages:gen-ai-output-messages.json \
  system_instructions:gen-ai-system-instructions.json \
  tool_definitions:gen-ai-tool-definitions.json \
  retrieval_documents:gen-ai-retrieval-documents.json

# Regenerate the committed policy rego from the pinned GenAI registry:
#   policies/genai_span_validation.rego  weaver, from the template + params
#   policies/_schemas.rego               semconv JSON content schemas, via jq
# Run after bumping SEMCONV_GENAI_REF in versions.env or editing the
# policies/templates/registry/genai_span_validation template. Requires the
# weaver and jq binaries on PATH (see versions.env) and a provisioned registry —
# any conformance tox env fetches + filters it into $(SEMCONV_CACHE).
generate-conformance-policies:
	@test -d "$(REGISTRY)" || { \
	  echo "registry not provisioned at $(REGISTRY)"; \
	  echo "run a conformance env first, e.g. tox -e py314-test-instrumentation-genai-openai-conformance"; \
	  exit 1; }
	@tmp=$$(mktemp -d); trap 'rm -rf "$$tmp"' EXIT; \
	  weaver registry generate --v2 --registry "$(REGISTRY)" \
	    --templates policies/templates genai_span_validation "$$tmp"; \
	  cp "$$tmp/genai_span_validation.rego" policies/genai_span_validation.rego; \
	  echo "Wrote policies/genai_span_validation.rego"
	@out=policies/_schemas.rego; \
	  { echo "# Auto-generated from semantic-conventions. Do not edit."; \
	    echo "# Regenerate with \`make generate-conformance-policies\`."; \
	    printf 'package live_check_advice\n\nimport rego.v1\n'; } > "$$out"; \
	  for pair in $(SCHEMAS); do \
	    key=$${pair%%:*}; src="$(REGISTRY)/gen-ai/$${pair#*:}"; \
	    printf '\n' >> "$$out"; \
	    if [ -f "$$src" ]; then \
	      printf '_schema_%s := ' "$$key" >> "$$out"; \
	      jq --indent 2 'walk(if type=="object" and .["$$ref"]=="http://json-schema.org/draft-07/schema#" then (.type="object" | del(.["$$ref"])) else . end)' "$$src" >> "$$out"; \
	    else \
	      echo "$$src not found — emitting null stub" >&2; \
	      printf '_schema_%s := null\n' "$$key" >> "$$out"; \
	    fi; \
	  done; \
	  echo "Wrote $$out"
