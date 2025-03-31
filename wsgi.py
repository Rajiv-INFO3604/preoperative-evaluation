import click, pytest, sys
from flask import Flask, render_template
from flask.cli import with_appcontext, AppGroup


from App.database import db, get_migrate
from App.main import create_app
from App.controllers import *

# This commands file allow you to create convenient CLI commands for testing controllers

app = create_app()
migrate = get_migrate(app)

# This command creates and initializes the database
@app.cli.command("init", help="Creates and initializes the database")
def initialize():
    initialize_db()


@app.errorhandler(404)
def not_found(e):
    return render_template('404.html'), 404

'''
User Commands
'''

# Commands can be organized using groups

# create a group, it would be the first argument of the command
# eg : flask user <command>
user_cli = AppGroup('user', help='User object commands')

# Then define the command and any parameters and annotate it with the group (@)
# @user_cli.command("create", help="Creates a user")
# @click.argument("username", default="rob")
# @click.argument("password", default="robpass")
# def create_user_command(username, password):
#     print(f'{username} created!')

# this command will be : flask user create bob bobpass

@user_cli.command("list", help="Lists users in the database")
@click.argument("format", default="string")
def list_user_command(format):
    if format == 'string':
        print(get_all_patients())
    else:
        print(get_all_users_json())

app.cli.add_command(user_cli) # add the group to the cli

patient_cli = AppGroup('patient', help='Patient object commands')

@patient_cli.command("create", help="Creates a patient")
@click.argument("firstname", default="rob")
@click.argument("lastname", default="rob")
@click.argument("username", default="rob")
@click.argument("password", default="rob")
@click.argument("email", default="rob")
@click.argument("phone_number", default="rob")
def create_patient_command(firstname, lastname, username, password, email, phone_number):
    patient = create_patient(firstname, lastname, username, password, email, phone_number)
    print(f'{patient.firstname} created!')

app.cli.add_command(patient_cli)


'''
Test Commands
'''

test = AppGroup('test', help='Testing commands')

@test.command("user", help="Run User tests")
@click.argument("type", default="all")
def user_tests_command(type):
    if type == "unit":
        sys.exit(pytest.main(["-k", "UserUnitTests"]))
    elif type == "int":
        sys.exit(pytest.main(["-k", "UserIntegrationTests"]))
    else:
        sys.exit(pytest.main(["-k", "App"]))

app.cli.add_command(test)