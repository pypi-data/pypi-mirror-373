# ewokstomo

The **ewokstomo** project is a Python library designed to provide workflow tasks for Tomographic Data Processing using Ewoks (Extensible Workflow System).

## Installation

By default, at the ESRF, `ewokstomo` should be installed on Ewoks workers using an Ansible script by the DAU team.
If you wish to install `ewokstomo` manually, ensure you have Python 3.10+ and `pip` installed. You can install the library directly from PyPI:

```sh
pip install ewokstomo
```

Alternatively, to install from source, clone this repository and run:

```sh
git clone https://gitlab.esrf.fr/workflow/ewoksapps/ewokstomo.git
cd ewokstomo
pip install -e .
```

## Quickstart Guide

### Running an `ewokstomo` Workflow

Most of the time, the workflow will be automatically ran from the Bliss control system.
However if you wish to execute the workflow by hand, you can use the following:

`ewoks execute workflow.json`

Some examples of workflow are found in `ewokstomo/workflows`

## How-To Guides

For detailed instructions on various tasks, please refer to the How-To Guides in the documentation, which cover topics such as:

- Configuration of tomography workflows
- Running workflows locally for testing
- Using the API to run specific tasks (e.g., NXtomo conversion, reconstruction)

## Documentation

Comprehensive documentation, including an API reference, tutorials, and conceptual explanations, can be found in the [doc directory](./doc) or online at the [ReadTheDocs page](https://ewokstomo.readthedocs.io).

## Contributing

Contributions are welcome! To contribute, please:

1. Clone the repository and create a new branch for your feature or fix.
2. Write tests and ensure that the code is well-documented.
3. Submit a merge request for review.

See the [`CONTRIBUTING.md`](./CONTRIBUTING.md) file for more details.

## License

This project is licensed under the MIT License. See the [`LICENSE.md`](./LICENSE.md) file for details.

## Support

If you have any questions or issues, please open an issue on the GitLab repository or contact the support team via a [data processing request ticket](https://requests.esrf.fr/plugins/servlet/desk/portal/41).