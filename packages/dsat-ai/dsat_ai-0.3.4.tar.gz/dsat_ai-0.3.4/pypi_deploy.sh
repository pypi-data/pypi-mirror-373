rm -rf dist/ build/
python -m build
python -m twine upload dist/*

echo "Deployment complete."
