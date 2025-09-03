import sys

import toml


def extract_dependency_names():
    file_path = './pyproject.toml'
    with open(file_path) as file:
        toml_content = toml.load(file)

    project_dependencies = toml_content.get('project', {}).get('dependencies', [])

    dependency_list = [
        dep.split('==')[0].split('<=')[0].split('~=')[0].split('>=')[0].split('[')[0].split('<')[0]
        for dep in project_dependencies
    ]
    return dependency_list


def check_dependencies():
    flag = True
    dependency_list = extract_dependency_names()
    file_path = './src/amsdal_cli/Third-Party Materials - AMSDAL Dependencies - License Notices.md'
    with open(file_path, encoding='utf-8') as file:
        content = file.read()

    for word in dependency_list:
        if word.startswith('amsdal'):
            continue
        if word not in content:
            print(f'Dependency not found - "{word}"')  # noqa: T201
            flag = False
    if flag is False:
        return sys.exit(1)


if __name__ == '__main__':
    check_dependencies()
