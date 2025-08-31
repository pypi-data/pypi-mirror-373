[discord]: https://discord.gg/wF9JHH55Kp

<div align="center">

[![Downloads](https://static.pepy.tech/badge/lanovalopy)](https://pepy.tech/project/lanovalopy)

</div>

# LanoValoPy (Lanore Valorant Python)

LanoValoPy is a python-based wrapper for the following Valorant Rest API:

https://github.com/Henrik-3/unofficial-valorant-api

This API is free and freely accessible for everyone. An API key is optional but not mandatory. This project is NOT being worked on regularly.

This is the first version. There could be some bugs, unexpected exceptions or similar. Please report bugs on our [discord].

### API key

You can request an API key on [Henrik's discord server](https://discord.com/invite/X3GaVkX2YN) <br> It is NOT required to use an API key though!

## Summary

1. [Introduction](#introduction)
2. [Download](#download)
3. [Documentation](#documentation)
4. [Support](#support)

## Introduction

Some requests may take longer.

### Get Account

```python
import asyncio
from lano_valo_py import LanoValoPy
from lano_valo_py.valo_types.valo_enums import MMRVersions, Regions

async def main():
    # Initialize the API client with your token
    api_client = LanoValoPy(henrik_token="YOUR_TOKEN_HERE")

    # Example: Get Account Information
    account_options = AccountFetchOptionsModel(name="LANORE", tag="evil")
    try:
        account_response = await api_client.get_account(account_options)
        print(account_response)
    except Exception as e:
        print(f"Error fetching account: {e}")

if __name__ == "__main__":
    asyncio.run(main())

```

### Get Stored-MMR-History 
```python

from lano_valo_py.valo_types.valo_enums import MMRVersions, Regions
from lano_valo_py.valo_types.valo_models import (
    GetMMRStoredHistoryFilterModel,
    GetMMRStoredHistoryOptionsModel,
    GetMMRStoredHistoryByPUUIDResponseModel
)

import asyncio

from lano_valo_py import LanoValoPy


async def main():
    # Initialize the API client with your token
    api_client = LanoValoPy(henrik_token="You_token_here")

    # Example: Get Stored MMR History

    # Use filter if u have more than 20 match in one episode
    option_filter = GetMMRStoredHistoryFilterModel(
        size=20
    )  # max size one one page is 20, page is 1 by default

    mmr_options = GetMMRStoredHistoryOptionsModel(
        version=MMRVersions.v1,
        region=Regions.eu,
        name="Lanore",
        tag="evil",
        filter=option_filter,
    )
    stored_mmr_history_response = await api_client.get_stored_mmr_history(mmr_options)
    print(stored_mmr_history_response)

    # Example: Get Stored MMR History By PUUID
    mmr_options = GetMMRStoredHistoryByPUUIDResponseModel(
        version=MMRVersions.v1,
        region=Regions.eu,
        puuid="e4122af3-fa8c-582c-847d-42a3868925cd",
        filter=option_filter,
    )
    stored_mmr_history_response = await api_client.get_stored_mmr_history_by_puuid(mmr_options)
    print(stored_mmr_history_response)

```

## Examples

[For more examples](./examples/)

## Supported Endpoints
- Account info
- MMR history
- Match history
- Stored Data
- etc...

## Rate Limits
The unofficial Valorant API has the following limits:
- Basic key: 30 requests per minute
- Advanced key: 90 requests per minute
- Custom key: Limit you requests

### Common Use Cases
- Track player rank over time
- Compare teammates' stats
- Monitor store rotations

## Download

``` bash
pip install lanovalopy@latest

```

## Documentation

# Hosted

The documentation is hosted here: https://Lanxre.github.io/LanoValoPy/

## Support

For support visit my [discord] server