from setuptools import setup, find_packages

setup(
    name='nbitk',
    packages=find_packages(),
    use_scm_version={
        'fallback_version': '0.0.0+dev',
    },
    setup_requires=['setuptools_scm'],
)