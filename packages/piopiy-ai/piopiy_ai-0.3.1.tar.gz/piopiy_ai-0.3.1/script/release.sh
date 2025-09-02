# build
python -m pip install --upgrade build twine
rm -rf dist build *.egg-info
python -m build
python -m twine check dist/*

# upload to TestPyPI

python -m twine upload  dist/*

# (optional) tag release
git tag "v$(python - <<'PY'\nimport re, pathlib;print(re.search(r'^version\\s*=\\s*\"([^\"]+)\"', pathlib.Path('pyproject.toml').read_text(), re.M).group(1))\nPY)"
git push --tags

