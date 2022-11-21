name: Markdown Linter

on:
  pull_request:
    branches:
      - main
    paths:
      - '**.md'
      - '!CHANGELOG.md'

permissions:
  checks: write
  contents: write

jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout repository
        uses: actions/checkout
        with:
          fetch-depth: 0
      - name: Run markdownlint
        uses: nosborn/github-action-markdown-cli
        with:
          files: .
