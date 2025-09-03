# `nbitk`: Naturalis BioInformatics ToolKit

This project is intended as a foundational toolkit for bioinformatics research at Naturalis Biodiversity Center. The 
toolkit is written in Python and is designed to be easy to use and easy to extend.

## Who is this for?

The principal users and developers of this toolkit are the bioinformaticians at Naturalis Biodiversity Center.
In addition, developers and data engineers of Naturalis's Core Sequence Cloud use some of the functionality
to enact service calls for data validation. Lastly, researchers may find this toolkit useful for operating
on biodiversity data, access remote services, and run command line tools via wrappers. Design changes and 
feature requests should therefore be discussed with the bioinformatics team.

## Installation from PyPI

The toolkit and its python dependencies can be installed from PyPI. This results in a lightweight installation
that has only the python stack but not any command line tools. This is typically what you need when running
service clients. The install is as follows:

```bash
pip install nbitk
```

## Installation from BioConda

In addition, there is a release on BioConda, that additionally includes any command line tools
for which the toolkit contains wrappers. That release can also be installed directly, resulting
in both the core python toolkit as well as command line tools (i.e. you do NOT have to do both
pip and conda, just one or the other dependening on whether you need to run command line tools,
for which you would use the conda release). This is installed as follows:

```bash
conda install nbitk
```

NOTE: the [environment.yml](environment.yml) is here for the [unit testing pipeline](.gitlab-ci.yml) 
so that tool wrappers can be tested as well. Its only other use is to help prepare an updated release 
on BioConda. Otherwise there is no end-user function for it.

## Preparing releases

### PyPI

To release on PyPI, all that needs to happen is to tag a version, and then the release is pushed
out automatically. Things to keep in mind:

- Ensure that the release is of sufficient quality (coding style, comments, pydoc, all tests pass)
- Use [semantic versioning](https://semver.org/) to tag the release

### BioConda

To release on BioConda, an overview of the steps involved is as follows:

1. Fork the BioConda recipes [repo](https://github.com/bioconda/bioconda-recipes/)
2. Update the recipes/nbitk/meta.yml in your fork, specifically:
   - Update the version number   
   - Update the run requirements to include everything from the pyproject.toml and environment.yml
   - Update the SHA256 hash to match that version. The easiest way to obtain this is to go to
     https://pypi.org/project/nbitk/#files and click on 'view details' for the release.
3. Post a pull request to BioConda, with 'Update nbitk' in the title
4. Address any problems detected by BioConda's CI tools
5. If all is fine, tag the PR thread for review by a human, and wait
6. Once a human shows up, address their feedback (be nice: they're volunteers!)
7. When the human is happy, they will merge the update into BioConda

## Usage

The toolkit is meant for programmatic use. It is not intended to be used as a command line tool. Consult the
various modules and classes for documentation on how to use the toolkit. In addition, the scripts in the 
`tests` directory provide examples of how to use the toolkit.

## License

This project is licensed under the Apache 2.0 License - see the [LICENSE](LICENSE) file for details.

## Contributing

Please read [CONTRIBUTING.md](CONTRIBUTING.md) for details on our code of conduct, and the process for 
submitting pull requests to us.