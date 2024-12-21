

# CarConnectivity Command Line Interface
[![GitHub sourcecode](https://img.shields.io/badge/Source-GitHub-green)](https://github.com/tillsteinbach/CarConnectivity-cli/)
[![GitHub release (latest by date)](https://img.shields.io/github/v/release/tillsteinbach/CarConnectivity-cli)](https://github.com/tillsteinbach/CarConnectivity-cli/releases/latest)
[![GitHub](https://img.shields.io/github/license/tillsteinbach/CarConnectivity-cli)](https://github.com/tillsteinbach/CarConnectivity-cli/blob/master/LICENSE)
[![GitHub issues](https://img.shields.io/github/issues/tillsteinbach/CarConnectivity-cli)](https://github.com/tillsteinbach/CarConnectivity-cli/issues)
[![Donate at PayPal](https://img.shields.io/badge/Donate-PayPal-2997d8)](https://www.paypal.com/donate?hosted_button_id=2BVFF5GJ9SXAJ)
[![Sponsor at Github](https://img.shields.io/badge/Sponsor-GitHub-28a745)](https://github.com/sponsors/tillsteinbach)

## CarConnectivity will become the successor of [WeConnect-python](https://github.com/tillsteinbach/WeConnect-python) in 2025 with similar functionality but support for other brands beyond Volkswagen!

## Supported Car Brands
CarConenctivity uses a plugin architecture to enable access to the services of various brands. Currently known plugins are:

| Brand      | Connector                                                                                                     |
|------------|---------------------------------------------------------------------------------------------------------------|
| Skoda      | [CarConnectivity-connector-skoda](https://github.com/tillsteinbach/CarConnectivity-connector-skoda)           |
| Volkswagen | [CarConnectivity-connector-volkswagen](https://github.com/tillsteinbach/CarConnectivity-connector-volkswagen) |

If you know of a connector not listed here let me know and I will add it to the list.
If you are a python developer and willing to implement a connector for a brand not listed here, let me know and I try to support you as good as possible

## Configuration
In your carconnectivity.json configuration add a section for the connectors you like to use like this:
```
{
    "carConnectivity": {
        "connectors": [
            {
                "type": "volkswagen",
                "config": {
                    "username": "test@test.de"
                    "password": "testpassword123"
                }
            },
            {
                "type": "skoda",
                "config": {
                    "username": "test@test.de"
                    "password": "testpassword123"
                }
            }
        ]
    }
}
```
The detailed configuration options of the connectors can be found in their README files.