# Makefile for slugkit-py-sdk

BUILD_ARCH ?= $(shell uname -m | grep -q "arm64\|aarch64" && echo "arm64" || echo "amd64")
IMAGE_REPO ?= ghcr.io/slugkit/
IMAGE_NAME ?= slugkit-mcp
VERSION_TAG ?= $(shell git show -s --format=%cd --date=format:'%Y%m%d' HEAD)-$(shell git rev-parse --short HEAD)

TARGET_ARCHITECTURES ?= amd64 arm64

.PHONY: build
build:
	rm -rf dist/*
	uv run hatchling build

.PHONY: publish
publish: build
	uv run twine upload --repository pypi dist/*

.PHONY: test
test:
	uv run --group test pytest

.PHONY: test-verbose
test-verbose:
	uv run --group test pytest -v

.PHONY: test-coverage
test-coverage:
	uv run --group test pytest --cov=slugkit --cov-report=term-missing

.PHONY: install-test-deps
install-test-deps:
	uv sync --group test

.PHONY: build-mcp-image
build-mcp-image:
	@echo "Building $(IMAGE_NAME)-$(BUILD_ARCH):$(VERSION_TAG)"
	@docker build \
		--platform linux/$(BUILD_ARCH) \
		-t $(IMAGE_REPO)$(IMAGE_NAME)-$(BUILD_ARCH):$(VERSION_TAG) \
		-t $(IMAGE_REPO)$(IMAGE_NAME)-$(BUILD_ARCH):latest \
		-t $(IMAGE_NAME)-$(BUILD_ARCH):$(VERSION_TAG) \
		-t $(IMAGE_NAME)-$(BUILD_ARCH):latest \
		-f docker/mcp.dockerfile .

.PHONY: build-mcp-images
build-mcp-images:
	@for build_arch in $(TARGET_ARCHITECTURES); do \
		make build-mcp-image \
			BUILD_ARCH=$$build_arch; \
	done

.PHONY: push-mcp-image
push-mcp-image:
	@docker push $(IMAGE_REPO)$(IMAGE_NAME)-$(BUILD_ARCH):$(VERSION_TAG)
	@docker push $(IMAGE_REPO)$(IMAGE_NAME)-$(BUILD_ARCH):latest

.PHONY: create-and-push-manifest
create-and-push-manifest:
ifndef MANIFEST_TAG
	$(error MANIFEST_TAG is not set)
endif
	@echo "Creating and pushing manifest for $(IMAGE_NAME)-XXX:$(MANIFEST_TAG)"
	@docker manifest create --amend $(IMAGE_REPO)$(IMAGE_NAME):$(MANIFEST_TAG) \
		$(IMAGE_REPO)$(IMAGE_NAME)-amd64:$(MANIFEST_TAG) \
		$(IMAGE_REPO)$(IMAGE_NAME)-arm64:$(MANIFEST_TAG)
	@docker manifest annotate $(IMAGE_REPO)$(IMAGE_NAME):$(MANIFEST_TAG) \
		$(IMAGE_REPO)$(IMAGE_NAME)-amd64:$(MANIFEST_TAG) \
		--os linux --arch amd64
	@docker manifest annotate $(IMAGE_REPO)$(IMAGE_NAME):$(MANIFEST_TAG) \
		$(IMAGE_REPO)$(IMAGE_NAME)-arm64:$(MANIFEST_TAG) \
		--os linux --arch arm64
	@docker manifest push $(IMAGE_REPO)$(IMAGE_NAME):$(MANIFEST_TAG)

.PHONY: push-mcp-images
push-mcp-images:
	@for build_arch in $(TARGET_ARCHITECTURES); do \
		make push-mcp-image \
			BUILD_ARCH=$$build_arch; \
	done
	@make create-and-push-manifest \
		MANIFEST_TAG=$(VERSION_TAG)
	@make create-and-push-manifest \
		MANIFEST_TAG=latest

