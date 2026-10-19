# Contributing to PMI

PMI is a local-development prototype. Small, reviewable improvements with clear reproduction steps are welcome.

## Before changing code

Read [the README](README.md), especially the architecture and current limitations. Use a branch for your change and keep it focused. Discuss large design changes in an issue first.

Useful areas include JWT secret configuration, active-reference regression coverage, path-based document IDs, dependency reproducibility, and evaluation of retrieval quality.

## Local development

Follow the README setup from the repository root. Use a small public or synthetic test repository and local test accounts. Never commit tokens, real credentials, private repository exports, chat databases, or personal data.

Semantic reasoning sends context to an external model provider. Run it only with data you are authorized to share. The DevOps entry point posts a real PR comment, so use a designated test PR only when that action is intended.

## Validation

There is currently no tracked automated test suite. For documentation changes, verify every path, command, configuration name, and feature claim against the implementation.

For behavior changes, add focused regression tests where practical and document how to run them. Follow the README's manual smoke procedure for affected flows. Report the environment, checks performed, results, and checks not run. Do not describe a syntax check as end-to-end validation.

## Pull requests

Explain the problem, resulting behavior, and validation. Include reproduction steps for fixes and any configuration or data-format changes. Avoid unrelated formatting changes and retain existing contributor attribution.

If reporting a security issue, avoid publishing credentials or private data in a public issue. Contact the maintainer through the profile linked in the README to arrange an appropriate disclosure channel.

## Licensing

This repository does not currently contain a license file. Do not introduce a license or third-party material without confirming the applicable ownership and permissions with the maintainer.
