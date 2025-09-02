Informatics Matters Data Manager Job Decoder
============================================

.. image:: https://badge.fury.io/py/im-data-manager-job-decoder.svg
   :target: https://badge.fury.io/py/im-data-manager-job-decoder
   :alt: PyPI package (latest)

.. image:: https://github.com/InformaticsMatters/squonk2-data-manager-job-decoder/actions/workflows/build.yaml/badge.svg
   :target: https://github.com/InformaticsMatters/squonk2-data-manager-job-decoder/actions/workflows/build.yaml
   :alt: Build

.. image:: https://github.com/InformaticsMatters/squonk2-data-manager-job-decoder/actions/workflows/publish.yaml/badge.svg
   :target: https://github.com/InformaticsMatters/squonk2-data-manager-job-decoder/actions/workflows/publish.yaml
   :alt: Publish

A package that simplifies the decoding of encoded text strings and validation
of Job Definitions and Manifests.

Given an encoded string the ``decode()`` method
returns the decoded value or an error.

For example, given the following `jinja2`_ encoded string
``'{{ foo }}, bar={{ bar }}, baz={{ baz }}'`` and variable map
``{'foo': 1, 'bar': 2, 'baz': 3}`` the decoder returns
the string ``'foo=1, bar=2, baz=3'``.

The following encoding/decoding formats are supported: -

- jinja2 (3.0)

The package also provides ``validate_job_schema()`` and
``validate_manifest_schema()`` functions, which can (should) be used to
validate the Manifests and Job definitions against the
built-in schemas.

If you have a Job Definition or Manifest file you can add a reference to the
corresponding schema in this package to your file to help you identify schema
violations prior to deployment. To do this you just need to add a line starting
``# yaml-language-server:`` at the top of your file. For example,
you can link to the **v2.3.0** Job Definition schema by adding the following line::

    # yaml-language-server: $schema=https://raw.githubusercontent.com/InformaticsMatters/squonk2-data-manager-job-decoder/refs/tags/2.3.0/decoder/job-definition-schema.yaml

.. _jinja2: https://jinja.palletsprojects.com/en/3.0.x/

Installation (Python)
=====================

The Job decoder is published on `PyPI`_ and can be installed from
there::

    pip install im-data-manager-job-decoder

Once installed you can validate the definition (expected to be a dictionary
formed from the definition YAML file) with::

    >>> from decoder import decoder
    >>> error: Optional[str] = decoder.validate_manifest_schema(manifest)
    >>> error: Optional[str] = decoder.validate_job_schema(job_definition)

And you can decode encoded fields within the job definition.
Here we're decoding the job's 'command' using a map of variables and their
values::

    >>> decoded, success = decoder.decode(definition['command'],
                                          variables,
                                          'command',
                                          decoder.TextEncoding.JINJA2_3_0)

A method also exists to generate a Data Manger Job documentation URL
for the supported repository types. For example, to get the
auto-generated documentation URL for a job definition hosted in a GitHub
repository you can do this::

    >>> doc_url: str = decoder.get_job_doc_url("github",
                                               collection
                                               job_id,
                                               job_definition,
                                               manifest_url)

We support ``github`` and ``gitlab`` as repository types.

.. _PyPI: https://pypi.org/project/im-data-manager-job-decoder

Get in touch
============

- Report bugs, suggest features or view the source code `on GitHub`_.

.. _on GitHub: https://github.com/informaticsmatters/squonk2-data-manager-job-decoder
