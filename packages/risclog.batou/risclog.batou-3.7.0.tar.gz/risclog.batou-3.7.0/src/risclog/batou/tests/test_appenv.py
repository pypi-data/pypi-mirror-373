import mock
from risclog.batou.appenv import Requirements


@mock.patch.object(Requirements, 'userenvhash')
def test_requirements_component(userenvhash, root):
    userenvhash.return_value = '1234567890'

    with open('requirements.txt', 'w') as f:
        f.write(
            """\
six==1.14.0
requests
-e/tmp/mypackage
-egit+https://github.com/flyingcircus/batou
mypackage[test]
"""
        )

    root.component += Requirements('requirements.lock')
    root.component.deploy()

    assert [
        '# Created by batou. Do not edit manually.',
        '# 1234567890',
        '-e/tmp/mypackage',
        '-egit+https://github.com/flyingcircus/batou',
        'mypackage[test]',
        'requests',
        'six==1.14.0',
    ] == open('requirements.lock', 'r').read().splitlines()

    root.component += Requirements(
        'requirements.lock',
        find_links=['https://download.example.com'],
        pinnings={'requests': '1.0', 'mypackage': '0.2'},
        editable_packages={'six': '/usr/dev/six'},
        additional_requirements=['pytest', 'pytest-flake8'],
        python_preferences=['3.7', '3.9', '3.8'],
    )
    root.component.deploy()

    assert [
        '# Created by batou. Do not edit manually.',
        '# appenv-python-preference: 3.7,3.9,3.8',
        '# 1234567890',
        '-f https://download.example.com',
        '-e/tmp/mypackage',
        '-e/usr/dev/six',
        '-egit+https://github.com/flyingcircus/batou',
        'mypackage[test]==0.2',
        'pytest',
        'pytest-flake8',
        'requests==1.0',
    ] == open('requirements.lock', 'r').read().splitlines()

    root.component += Requirements(
        'requirements.lock',
        pinnings={'six': '1.12.1'},
    )
    root.component.deploy()

    assert [
        '# Created by batou. Do not edit manually.',
        '# 1234567890',
        '-e/tmp/mypackage',
        '-egit+https://github.com/flyingcircus/batou',
        'mypackage[test]',
        'requests',
        'six==1.14.0',
    ] == open('requirements.lock', 'r').read().splitlines()


@mock.patch.object(Requirements, 'userenvhash')
def test_requirements_component_mixed_case_pinnigs(userenvhash, root):
    userenvhash.return_value = '1234567890'
    with open('requirements.txt', 'w') as f:
        f.write(
            """\
SQLAlchemy
factory_boy
importlib-metadata
openAPI_spec-validator
"""
        )

    root.component += Requirements(
        'requirements.lock',
        pinnings={
            'sqlalchemy': '1.4.48',
            'factory-boy': '3.2.0',
            'importlib_metadata': '4.8.1',
            'OPENapi-spec_validator': '0.2.4',
        },
    )
    root.component.deploy()

    assert [
        '# Created by batou. Do not edit manually.',
        '# 1234567890',
        'factory-boy==3.2.0',
        'importlib-metadata==4.8.1',
        'openapi-spec-validator==0.2.4',
        'sqlalchemy==1.4.48',
    ] == open('requirements.lock', 'r').read().splitlines()
