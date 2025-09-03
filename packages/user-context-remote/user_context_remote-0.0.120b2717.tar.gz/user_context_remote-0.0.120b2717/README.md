# python-package-template  

To create local package and remote package layers (not to create GraphQL and REST-API layers)

# directory structure

Root directory should have only .github/, ,gitignore, README.md and the project directory (i.e.
location_local_python_package same as repo) - This will allow is to easily switch to mono repo<br>
/location_local<br>
/location_local/get_country_name<br>
/location_local/get_country_name/src<br>
/location_local/get_country_name/src/get_country_name.py<br>
/location_local/get_country_name/tests<br>
/location_local/get_country_name/tests/test_get_country_name.py<br>

# database Python scripts in /db folder

Please place <table-name>.py in /db<br>
No need for seperate file for _ml table<br>
Please delete the example file if not needed<br>

# Create the files to create the database schema, tables, view and populate Meta Data and Test Date

/db/<table-name>.py - CREATE SCHEMA ... CREATE TABLE ... CREATE VIEW ...<br>
/db/<table-name>_insert.py to create records

# Update the setup.py (i.e.name, version)

# Please create test directory inside the directory of the project i.e. /<project-name>/tests

# Update the serverless.yml in the root directory

provider:
stage: play1

Update the endpoints in serverless.yml

# Working with VS Code

Please make sure you push to the repo launch.json fie that enables to run and debug the code<br>

# Permissions 
Make sure to give permissions to the user for 'person_table' and 'location_table'

# Unit-Test

We prefer using pytest and not unittest package<br>

Please create pytest.init in the project directory and not in the root directory

```
[pytest]
markers =
    test: custom mark for tests
```
