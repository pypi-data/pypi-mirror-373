# Install New Environment

## Anaconda

To install a new Anaconda environment, open Terminal and run:
`bash "new_env.sh"`.
If using windows, open git bash and run the above line.

* To create a new environment without the default packages set by the `.condarc` file, run:\
`conda create --name <env_name> --no-default-packages`

* To remove the environment, run:
`conda remove --name <env_name> --all`

* To roll back an environment to its initial state, run:
  `conda install --rev 0`

Then, restart PyCharm and change the PyCharm Python interpreter in Settings > Project > 
Python Interpreter > Add Interpreter > Conda Environment > Use Existing Environment > "MYENV" > Apply.

To clear the cache, run:\
`conda clean --all -y`

## pip
Get version requirements from `pip_requirements_in.txt` and save them to `pip_requirements.txt` using pip-tools:\
`pip-compile pip_requirements_in.txt --max-rounds 100 --output-file pip_requirements.txt`

Create a new virtual environment:\
`python -m venv "myvenv"`

Activate the virtual environment:\
`source "myvenv/bin/activate"` (Linux/Mac)\
`"myvenv\Scripts\activate.bat"` (Windows CMD)\
`& "myvenv\Scripts\Activate.ps1"` (Windows PowerShell)


To install using pip, run:\
`python -m pip install -r "requirements.txt" -U --progress-bar on`


To save the `requirements` file, run:\
`pip freeze => "pip_requirements.txt"`

To clear the cache, run:\
`pip cache purge`

## Poetry

To install Poetry, run:\
`curl -sSL https://install.python-poetry.org | python -` (Linux/Mac)
`(Invoke-WebRequest -Uri https://install.python-poetry.org -UseBasicParsing).Content | py -` (Windows PowerShell)

Add Poetry to the PATH:
`%APPDATA%\Python\Scripts`

Add the `export` plugin:\
`poetry self add poetry-plugin-export`

To create new `pyproject.toml` and `poetry.lock` files, run:
`poetry init`
Specify dependencies and versions in the `[projecet]` section, or use `poetry add <package>`.

To update dependencies, run:\
`poetry update`

To export the dependencies to a `requirements.txt` file, run:\
`poetry export -f requirements.txt --output requirements.txt --without-hashes`.
You can then install the dependencies using pip.

To clear the cache, run:\
`poetry cache list`
`poetry cache clear --all [pypi, _default_cache, ...]`
