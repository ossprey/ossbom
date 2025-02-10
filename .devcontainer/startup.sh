#!/bin/bash 
# Setup poetry
pip install poetry

# Git Config
git config --global push.default current
git config pull.rebase false

# Add Pre Push Hooks
cp .githooks/pre-push .git/hooks/pre-push
chmod a+x .git/hooks/pre-push

poetry install