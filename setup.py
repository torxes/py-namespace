from setuptools import setup


if __name__ == '__main__':
    setup(
        name="pyns",
        version="0.0.1.dev2",
        url="https://github.com/torxes/py-namespace",
        author="Urs Klingsporn",
        author_email="urs.klingsporn@googlemail.com",
        description="Dictionary like namespaces supporting nesting",
        packages=['pyns'],
        zip_safe=False,
        install_requires=[
            'six>=1.11.0',
            'PyYAML>=3.12'
        ],
        tests_require=[
            'pytest>=3.4.0',
        ],
        setup_requires=[
            'pytest-runner>=3.0',
        ]
    )
