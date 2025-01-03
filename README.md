

# CarConnectivity Command Line Interface
[![GitHub sourcecode](https://img.shields.io/badge/Source-GitHub-green)](https://github.com/tillsteinbach/CarConnectivity-cli/)
[![GitHub release (latest by date)](https://img.shields.io/github/v/release/tillsteinbach/CarConnectivity-cli)](https://github.com/tillsteinbach/CarConnectivity-cli/releases/latest)
[![GitHub](https://img.shields.io/github/license/tillsteinbach/CarConnectivity-cli)](https://github.com/tillsteinbach/CarConnectivity-cli/blob/master/LICENSE)
[![GitHub issues](https://img.shields.io/github/issues/tillsteinbach/CarConnectivity-cli)](https://github.com/tillsteinbach/CarConnectivity-cli/issues)
[![PyPI - Downloads](https://img.shields.io/pypi/dm/carconnectivity-cli?label=PyPI%20Downloads)](https://pypi.org/project/carconnectivity-cli/)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/carconnectivity-cli)](https://pypi.org/project/carconnectivity-cli/)
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

## How to use
Start by creating a carconnectivity.json configuration file

### Configuration
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

### How to use the commandline interface
Start carconnectivity-cli from the commandline, by default you will enter the interactive shell:
```bash
carconnectivity-cli mycarconnectivity_config.json
```
You get all the usage information by using the --help command
```bash
carconnectivity-cli mycarconnectivity_config.json --help
```
With the "list" command you can get a list of all available information you can query (use "list -s" if you want to see which attributes can be changed)
```bash
carconnectivity-cli mycarconnectivity_config.json list
/garage/WVWABCE1ZSD057394
/garage/WVWABCE1ZSD057394/vin
/garage/WVWABCE1ZSD057394/type
/garage/WVWABCE1ZSD057394/odometer
/garage/WVWABCE1ZSD057394/model
/garage/WVWABCE1ZSD057394/name
...
```
You can then pass the addresses to the "get" command:
```bash
carconnectivity-cli mycarconnectivity_config.json get /garage/WVWABCE1ZSD057394/model
ID.3
```
or the "set" command:
```bash
carconnectivity-cli mycarconnectivity_config.json /garage/WVWABCE1ZSD057394/climatisation/command stop
```
The "events" command allows you to monitor what is happening on the WeConnect Interface:
```bash
carconnectivity-cli mycarconnectivity_config.json events
2021-05-26 16:49:58.698570: /garage/WVWABCE1ZSD057394/doors/lock_state: new value: unlocked
2021-05-26 16:49:58.698751: /garage/WVWABCE1ZSD057394/doors/bonnet/lock_state: new value: unknown lock state
2021-05-26 16:49:58.698800: /garage/WVWABCE1ZSD057394/doors/bonnet/open_state: new value: closed
2021-05-26 16:49:58.698980: /garage/WVWABCE1ZSD057394/doors/frontLeft/lock_state: new value: unlocked
2021-05-26 16:49:58.699056: /garage/WVWABCE1ZSD057394/doors/frontLeft/open_state: new value: closed
```

### S-PIN
For some commands (e.g. locking/unlocking supported on some cars) you need in addition to your login the so called S-PIN, you can provide it with the spin config option:

### Interactive Shell
You can also use an interactive shell:
```
carconnectivity-cli --username user@mail.de --password test123 shell
Welcome! Type ? to list commands
user@mail.de@weconnect-sh:/$update
update done
user@mail.de@weconnect-sh:/$cd garage
user@mail.de@weconnect-sh:/garage$ ls
..
WVWABCE1ZSD057394
WVWABCE13SD057505
user@mail.de@weconnect-sh:/garage$ cd /garage/WVWABCE13SD057505/status/parkingPosition
user@mail.de@weconnect-sh:/garage/WVWABCE13SD057505/status/parkingPosition$ cat
[parkingPosition] (last captured 2021-06-01T19:05:04+00:00)
	Latitude: 51.674535
	Longitude: 16.154376
user@mail.de@weconnect-sh:/garage/WVWABCE13SD057505/parking/parkingPosition$ exit
Bye
```
### Caching
By default carconnectivity-cli will cache (store) the data for 300 seconds before retrieving new data from the servers. This makes carconnectivity-cli more responsive and at the same time does not cause unneccessary requests to the vw servers. If you want to increase the cache duration use max_age config option. If you do not want to cache use no_cache option. Please use the no_cache option with care. You are generating traffic with subsequent requests. If you request too often you might be blocked for some time until you can generate requests again.

### Credentials
If you do not want to provide your username or password all the time you have to create a ".netrc" file at the appropriate location (usually this is your home folder):
```
machine volkswagen.de
login test@test.de
password testpassword123
```
You can also provide the location of the netrc file in the configuration.

The optional S-PIN needed for some commands can be provided in the account section:
```
# For WeConnect
machine volkswagen.de
login test@test.de
password testpassword123
account 1234
```

## Tested with
- Volkswagen ID.3 Modelyear 2021
- Volkswagen Passat GTE Modelyear 2021
- Skoda Enyaq RS Modelyear 2025

## Reporting Issues
Please feel free to open an issue at [GitHub Issue page](https://github.com/tillsteinbach/carconnectivity-cli/issues) to report problems you found.

### Known Issues
- The Tool is in alpha state and may change unexpectedly at any time!

## Related Projects:
- [WeConnect-MQTT](https://github.com/tillsteinbach/WeConnect-mqtt): MQTT Client that publishes data from CarConnectivity to any MQTT broker.
- [CarConnectivity](https://github.com/tillsteinbach/CarConnectivity): The underlying python API behind CarConnectivity-cli. If you are a developer and want to implement an application or service with vehicle telemetry data you can use [CarConnectivity-Library](https://github.com/tillsteinbach/CarConnectivity).