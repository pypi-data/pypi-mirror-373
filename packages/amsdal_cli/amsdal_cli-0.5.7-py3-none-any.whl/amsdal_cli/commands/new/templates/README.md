# {{ ctx.application_name }}

This application describes the model schemas, properties, transactions, hooks and modifiers which can be used within AMSDAL Framework to manage data.

# AMSDAL CLI Guide

AMSDAL CLI is a tool that enables the creation of AMSDAL-based applications. With this CLI, you can easily generate the skeletons of the main entities such as models, transactions, properties, and more. Additionally, it allows you to verify your code, apply code formatting, and build the end models.

One of the most useful features of the AMSDAL CLI is the ability to run a local test HTTP server. This server allows you to preview your changes before releasing them to production, ensuring that your code works as expected.

Overall, the AMSDAL CLI is a powerful tool for anyone looking to develop AMSDAL-based applications quickly and efficiently.

## About This Guide

This guide is designed to help you get started with the AMSDAL CLI and create a sample application using it. We will walk you through the entire process of developing an application using the CLI, from installing the tool to generating the necessary entities and running a local test server.

By the end of this guide, you should have a good understanding of how to use the AMSDAL CLI for your own projects and be able to create AMSDAL-based applications with ease.

## Installing AMSDAL CLI

TBD

## Creating a new application

Now that you have installed the AMSDAL CLI, it's time to create your first application using it.

Try to open terminal in any place or folder and enter the `amsdal --help` command. You should see something like:

```
Usage: amsdal [OPTIONS] COMMAND [ARGS]...  

 AMSDAL CLI - a tool that provides the ability to create a new app, generate  
 models, transactions, build, serve, and other useful features for the  
 efficient building of new apps using AMSDAL Framework.  

╭─ Options ────────────────────────────────────────────────────────────────────╮
│ --install-completion          Install completion for the current shell.      │
│ --show-completion             Show completion for the current shell, to copy │
│                               it or customize the installation.              │
│ --help                        Show this message and exit.                    │
╰──────────────────────────────────────────────────────────────────────────────╯
╭─ Commands ───────────────────────────────────────────────────────────────────╮
│ build     Build the app and generate the models and other files.             │
│ generate  Generates application's files such as models, properties,          │
│           transactions, etc.                                                 │
│ new       Generates a new AMSDAL application.                                │
│ serve     Starts a test FastAPI server based on your app's models.           │
│ verify    Verifies all application's files such as models, properties,       │
│           transactions, etc.                                                 │
╰──────────────────────────────────────────────────────────────────────────────╯
```

Note, the list of supported commands can differ due to extending the CLI.

First of all, we recommend to run `amsdal --install-completion` command. It might require to re-open the terminal or even re-login on your machine, but it will provide you ability to use auto-completion for all arguments and options supported by `amsdal` tool.

In order to create a new application we can use the `new` command, let’s take a look help for this command, type `amsdal new --help` in the terminal and press enter. You should see something like:

```
Usage: amsdal new [OPTIONS] APP_NAME OUTPUT_PATH  

 Generates a new AMSDAL application.  

╭─ Arguments ──────────────────────────────────────────────────────────────────╮
│ *    app_name         TEXT  The Application name. For example: MyApplication │
│                             [default: None]                                  │
│                             [required]                                       │
│ *    output_path      PATH  Output path, where the app will be created.      │
│                             [default: None]                                  │
│                             [required]                                       │
╰──────────────────────────────────────────────────────────────────────────────╯
╭─ Options ────────────────────────────────────────────────────────────────────╮
│ --help          Show this message and exit.                                  │
╰──────────────────────────────────────────────────────────────────────────────╯
```

OK, so we need to specify two arguments:

- `app_name` - the application name
- `output_path` - the path where the app will be create

Let’s create our first application using `amsdal new DataManager ~/` command. After executing this command you should see something like:

```
The application is successfully created in /home/user/data_manager
```

Let’s check out what is inside this folder. First of all, navigate to this directory:

```bash
cd ~/data_manager
```

And using `ls -la` let’s see what we have there:

```
- 📄 .amsdal-cli
- 📄 config.yml
- 📄 .gitignore
- 📄 README.md
```

Not so much but don’t worry we will generate everything else later.

The `.amsdal-cli` it is configuration for AMSDAL CLI for you current app. It stores the configuration in JSON format and should looks like:

```
{
    "config_path": "./config.yml",
    "http_port": 8080,
    "check_model_exists": true,
    "json_indent": 4
}
```

Where the `config_path` it’s a path to the default AMSDAL `config.yml` that was also generated automatically. The `http_port` is the port where will be hosted the test server. The `check_model_exists` stores a boolean value and affects the generate commands. The `json_indent` stores the indentation configuration (how many spaces) for formatting JSON files. These options we will learn more deeply below. For now, you need to know that this file is essential for AMSDAL CLI. By this file, CLI detects the application. You should not remove or rename this file.

The `README.md` contains this guide. You can change this file as you wish.

OK, it’s time to create our first model.

## Generating models

Now that we have created a new AMSDAL application, let's generate a first model using the AMSDAL CLI. Run the following command:

```
amsdal generate model Person --format json
```

<aside>
⚠️ Note any other commands except the `new` should be executed only from the folder of your application. So make sure you are inside the `~/data_manager` folder.

</aside>

<aside>
⚠️ The `--format` option is required and currently it supports only `json`. It means the models will be generated in JSON format.

</aside>

Perfect! If we will check the directory of our application we will se that now we have there new folders and files:

```
- 📁 models
  - 📁 person
    - 📄 model.json
```

The `model.json` will have the following JSON content:

```
{
    "title": "Person",
    "type": "object",
    "properties": {},
    "required": [],
    "indexed": []
}
```

You should be familiar with this file if you have already worked with AMSDAL.

The `amsdal generate model` also provides ability to generate the properties. Let’s re-generate this model and add some properties to our model:

```
amsdal generate model Person -attrs "first_name:string last_name:string email:string:required:index age:number:default=21" --format json
```

If we will run this command you will see the confirmation message:

```
The file "~/data_manager/models/person/model.json" already exists. Would you like to overwrite it? [y/N]:
```

Type `y` and press enter. Now, if will check our model `cat models/person/model.json` it will contain the following:

```json
{
    "title": "Person",
    "type": "object",
    "properties": {
        "first_name": {
            "title": "first_name",
            "type": "string"
        },
        "last_name": {
            "title": "last_name",
            "type": "string"
        },
        "email": {
            "title": "email",
            "type": "string"
        },
        "age": {
            "title": "age",
            "type": "number",
            "default": 21.0
        }
    },
    "required": [
        "email"
    ],
    "indexed": [
        "email"
    ]
}
```

You can change this models manually as usually by adding new properties etc.

Let’s generate a new model using the following command:

```
amsdal generate model PersonProfile -attrs "bio:string phone:string person:belongs-to:Person:required friends:dict:string:Person family:has-many:Person" --format json
```

Let’s check out what we have in generated file by `cat models/person_profile/model.json`:

```json
{
    "title": "PersonProfile",
    "type": "object",
    "properties": {
        "bio": {
            "title": "bio",
            "type": "string"
        },
        "phone": {
            "title": "phone",
            "type": "string"
        },
        "person": {
            "title": "person",
            "type": "Person"
        },
        "friends": {
            "title": "friends",
            "type": "dict",
            "items": {
                "key_type": "string",
                "value_type": "Person"
            }
        },
        "family": {
            "title": "family",
            "type": "array",
            "items": {
                "type": "Person"
            }
        }
    },
    "required": [
        "person"
    ],
    "indexed": []
}
```

Perfect!

Let’s now generate a custom property.

## Generating custom properties

Run `amsdal generate property --model Person full_name` command.

It will generate a new file `models/person/properties/full_name.py` with following content:

```python
@property
def full_name(self):
    # TODO: implementation here
    ...
```

Cool, let’s add implementation for this property. Change it to the following:

```python
@property
def full_name(self):
    return f"{self.first_name} {self.last_name}"
```

Now we have custom property `full_name` for Person model. We can generate the properties as much as we won't for any of our models.

Moreover, if you remember, we have `check_model_exists` in `.amsdal-cli` configuration file. If we will set it to `false`, we will be able to generate properties (and other entities) even if we don’t have the model JSON field yet. Let’s try it, make sure you have this configuration:

```json
{
    "config_path": "./config.yml",
    "http_port": 8080,
    "check_model_exists": false,
    "json_indent": 4
}
```

And try to generate property for non-existing model:

```bash
amsdal generate property --model Address country_name
```

It will successfully create `./models/address/properties/country_name.py` file.

Let’s try now generate a modifier!

## Generating modifiers

The modifier, it’s predefined methods that allows you to override some specific built-in methods or properties of you end models. Currently we support these modifiers:

- constructor
- display_name
- version_name

Let’s try to generate the constructor modifier for PersonProfile model:

```bash
amsdal generate modifier --model PersonProfile constructor
```

It will generate the `./models/person_profile/modifiers/constructor.py` file with the following content:

```python
def __init__(self, *args, **kwargs):
    # TODO: implementation here
    super().__init__(*args, **kwargs)
```

Let’s implement the business logic that will make sure the age cannot be less the 21:

```python
def __init__(self, *args, **kwargs):
    age = kwargs.get("age") or 0

    if age < 21:
        kwargs["age"] = 21

    super().__init__(*args, **kwargs)
```

Perfect! You can generate any of available modifiers for your models.

Now, let’s generate a hook.

## Generating hooks

Hooks are actions that are triggered before or after certain events occur in the AMSDAL framework. They allow you to customize the behavior of your application by executing custom code in response to specific events, such as creating or updating a model instance. Hooks can be used to perform a variety of tasks, such as validating data, sending notifications, or updating related models.

Currently we support the following hooks:

- on_create
- on_update
- on_migrate

Let’s create our first hook for Person model:

```bash
amsdal generate hook --model Person on_create
```

 It will generate the `./models/person/hooks/on_create.py`:

```python
async def on_create(self):
    # TODO: implementation here
    ...
```

Let’s implement this hook and add the following business logic:

```python
async def on_create(self):
    from models.user.PersonProfile import PersonProfile

    # Create automatically PersonProfile for each new Person
    PersonProfile(
        person=self,
        bio="",
        phone="",
        friends={},
        family=[],
    )
```

Note, `from models.user.PersonProfile import PersonProfile` it is how we can import our models, although it is not yet generated (we have only schema of the future model in JSON format).

Cool, now each time the new person will be created, the corresponding profile will be created for this person as well.

Now, let’s try to generate transaction!

## Generating transactions

Run the following command:

```bash
amsdal generate transaction MarkBestFriends
```

It will generate the `./transactions/mark_best_friends.py` file:

```python
from amsdal.core.classes.base import transaction


@transaction(name='MarkBestFriends')
async def mark_best_friends():
    # TODO: implementation here
    ...
```

Let’s assume we need to have a migration that accepts two persons and make them as a best friends. So we need to add the following implementation for our transaction:

```python
from models.user.Person import Person
from models.user.PersonProfile import PersonProfile

from amsdal.amsdal_core.connection.connection_filter import Filter, FilterType
from amsdal.amsdal_core.objects.service import AmsdalObjectsApi
from amsdal.core.classes.base import transaction


@transaction(name='MarkBestFriends')
async def mark_best_friends(
    first_person: Person,
    second_person: Person,
):
    first_profile = await get_profile_by_person(person=first_person)
    second_profile = await get_profile_by_person(person=second_person)

    if not first_profile or not second_profile:
        return

    await first_profile.async_new_version(friends={"best": second_person})
    await second_profile.async_new_version(friends={"best": first_person})

async def get_profile_by_person(person: Person):
    api = AmsdalObjectsApi()
    profiles: list[PersonProfile] = await api.async_get_amsdal_objects_basemodel(
        PersonProfile.__name__,
        [
            Filter(
                key="person",
                filter_type=FilterType.eq,
                target=str(person.build_reference(is_latest=person.get_metadata().is_latest)),
            ),
        ],
    )

    return next(iter(profile for profile in profiles if profile._metadata.is_latest), None)
```

Perfect! We are ready to verify our files.

## Verifying the application

AMSDAL CLI provides the command that allows to verify your create files. Let’s run `amsdal verify`. This command only checks syntax errors in your python and JSON files. We also can verify building of end models by using the following option:

```bash
amsdal verify --building
```

You will see something like this:

```
Syntax checking... OK!
Pre-building app...
Building model "PersonProfile"... OK!
Building modifiers...
Processing ./data_manager/models/person_profile/modifiers/constructor.py...
OK!
Building model "Person"... OK!
Building properties...
Processing ./data_manager/models/person/properties/full_name.py...
OK!
Building hooks...
Processing ./data_manager/models/person/hooks/on_create.py...
OK!
Neither Python nor JSON model was not found in "./data_manager/models/address". Skipped!
Building transactions... OK!
OK!
Verifying models... OK!
```

As you can see, now it checks syntax and also building of your all models, properties and other entities.

<aside>
🔥 Note, the `./data_manager/models/address` directory was skipped due to missing the model itself.

</aside>

Let’s adjust our Person model and add into, for example, `indexes` undefined property `is_active`:

```json
{
    "title": "Person",
    "type": "object",
    "properties": {
        "first_name": {
            "title": "first_name",
            "type": "string"
        },
        "last_name": {
            "title": "last_name",
            "type": "string"
        },
        "email": {
            "title": "email",
            "type": "string"
        },
        "age": {
            "title": "age",
            "type": "number",
            "default": 21.0
        }
    },
    "required": [
        "email"
    ],
    "indexed": [
        "email",
        "is_active"
    ]
}
```

And try to run verify command with building again:

```bash
amsdal verify --building
```

You will see the corresponding error message:

```
Verifying models... Failed: Property is_active marked as indexed but wasn't found in class schema's properties.
```

Let’s fix it and add this property by changing the schema of Person model to the following:

```json
{
    "title": "Person",
    "type": "object",
    "properties": {
        "first_name": {
            "title": "first_name",
            "type": "string"
        },
        "last_name": {
            "title": "last_name",
            "type": "string"
        },
        "email": {
            "title": "email",
            "type": "string"
        },
        "age": {
            "title": "age",
            "type": "number",
            "default": 21.0
        },
        "is_active": {
            "title": "is_active",
            "type": "boolean",
            "default": true
        }
    },
    "required": [
        "email"
    ],
    "indexed": [
        "email",
        "is_active"
    ]
}
```

Run the verify command again. You should see that verification was done successfully.

Perfect! Now it’s time to run test server to test our models manually using the frontend app.

## Running the test server

Just run the following command from the root directory of our project:

```bash
amsdal serve
```

You will see something like this:

```
INFO:     Started server process [149586]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://localhost:8080 (Press CTRL+C to quit)
```

It means everything were generated properly and the test server was started successfully.

Now you can navigate to [http://localhost:8080/docs](http://localhost:8080/docs) in you browser to view API documentation.

<aside>
⚠️ Currently, it does not support the hot-reloading. So each time you make changes in your application you need to re-run the test server.

</aside>

Now we are also able to use [https://localhost.portal.amsdal.com/](https://localhost.portal.amsdal.com/) portal that links to our locally running test server and try to create Person record.

<aside>
⚠️ By default, it will create the following user credentials that you can use for signing in on [https://localhost.portal.amsdal.com/](https://localhost.portal.amsdal.com/):
Email: **admin@amsdal.com**
Password: **adminpassword**

</aside>

## Building the end models

Now, after manual testing we are ready to build our end models and files for production. AMSDAL CLI provide the build command that you can use for this.

Let’s run the following command:

```bash
amsdal build ~/release
```

This command will create the folder `release` in you `$HOME` directory and place there all necessary models and files. Let’s see what we have there right now using `ls ~/release/` command:

```bash
- 📄 config.yml  
- 📄 data-manager.sqlite  
- 📁 models
- - 📄 __init__.py
- - 📁 core
- - - ...
- - 📁 user
- - - 📄 __init__.py
- - - 📄 Person.py
- - - 📄 PersonProfile.py
- - - 📄 transactions.py
```

The `./models/core` will contain all built-in generated models that are required for AMSDAL core framework.

Your models and transactions.py will be placed into `./models/user` directory.
