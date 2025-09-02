# cmsgov

[![test](https://github.com/enorganic/cmsgov/actions/workflows/test.yml/badge.svg?branch=main)](https://github.com/enorganic/cmsgov/actions/workflows/test.yml)

An SDK (software development kit) for CMS.gov APIs. Currently implemented
APIs include:

- [Provider Data](https://data.cms.gov/provider-data/docs)

(more to come)

Please refer to the [documentation](https://cmsgov.enorganic.org) for
usage information.

## Install

You can install this package with pip:

```bash
pip3 install cmsgov
```

## Example Usage

Search for data sets containing the term "psychiatry" in one or more fields:

```python
from cmsgov.provider_data.v1.client import Client as ProviderDataClient

provider_data_client: ProviderDataClient = ProviderDataClient()
provider_data_client.get_search(fulltext="psychiatry")
```
