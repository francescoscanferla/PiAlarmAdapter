# Script PowerShell per eseguire i comandi coverage
coverage run --source=app -m unittest discover
coverage report --include="app/*" --show-missing
