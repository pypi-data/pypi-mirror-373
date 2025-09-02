# Nuclia Models

This repository contains some of the public models used in [Nuclia SDK](https://github.com/nuclia/nuclia.py). You can import and use these models with the Nuclia Python SDK.

## Installation

To install the Nuclia Python SDK and use the models from this repository:

```bash
pip install nuclia-sdk
```

## How to Use

To use one of the public models in your project, simply import it from the Nuclia SDK:

```python
from nuclia import sdk
from nuclia_models.common.pagination import Pagination
from nuclia_models.events.activity_logs import ActivityLogsQuery, EventType

kb = sdk.NucliaKB()
query = ActivityLogsQuery(
    year_month="2024-10",
    show=["id", "date", "question", "answer"],
    filters={
        "question": {"ilike": "user question"},
        "feedback_good": {"eq": True}
    },
    pagination=Pagination(limit=10)
)
kb.logs.query(type=EventType.CHAT, query=query)
```

Refer to the [Nuclia Python SDK documentation](https://docs.nuclia.dev/docs/develop/python-sdk/kb#logs) for more details on available models and their usage.

## Versioning and PR Conventions

We follow [Semantic Versioning (SemVer)](https://semver.org/) to manage version numbers in this repository. Here's how versions are bumped automatically based on the PR titles:

- **MAJOR** version: Incremented when there are incompatible API changes. Triggered if the PR title starts with `breaking`.
- **MINOR** version: Incremented when adding functionality in a backward-compatible manner. Triggered if the PR title starts with `feature`.
- **PATCH** version: Incremented for backward-compatible bug fixes. Triggered if the PR title starts with `fix`.

### Example PR Conventions:

- PR title: `fix: resolve issue with model output`
  - This will bump the PATCH version and automatically update the `CHANGELOG.md`.

- PR title: `feature: add support for new model`
  - This will bump the MINOR version and update the `CHANGELOG.md`.

- PR title: `breaking: change API response format`
  - This will bump the MAJOR version and update the `CHANGELOG.md`.

## Automatic Changelog Updates

When a PR is merged, the version is updated based on the title, and the `CHANGELOG.md` is automatically updated with the following format:

```
## [version] - YYYY-MM-DD
### Title:
Description of the PR (if provided)
```

If no description is provided, the changelog entry will only include the title.
