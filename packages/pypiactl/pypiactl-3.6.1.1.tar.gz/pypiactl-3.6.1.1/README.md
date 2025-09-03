# pypiactl

`pypiactl` is a wrapper for the command-line interface (CLI) to the Private Internet Access (PIA) client. Its intent is to offer all functionality of `piactl` to its users. Additionally, it allows the user to optionally gain insight into debug logs and set operation timeouts.

## Disclaimer

**`pypiactl` is in no way affiliated with Private Internet Access, Inc.** It is offered as a convenience to the Python development community, and should be used with discretion and the knowledge that **`pypiactl` is not endorsed, maintained, or supported by Private Internet Access, Inc.**

## Requirements

- Must use Python 3.7 or newer.
- The PIA desktop client (and therefore the [CLI](https://helpdesk.privateinternetaccess.com/kb/articles/pia-desktop-command-line-interface-2)) must be installed.
  - Please use the version of this library that matches your CLI's version. 
  - You can check your CLI's version with `piactl -v`

## Features

- [Simple configuration](#simple-configuration)
- [Checking CLI version](#checking-cli-version)
- [Connecting and disconnecting](#connecting-and-disconnecting)
- [Robust command results](#robust-command-results)
- [Logging in and out](#logging-in-and-out)
- [Background daemon control](#background-daemon-control)
- [Information types](#information-types)
- [Retrieving information](#retrieving-information)
- [Monitoring information](#monitoring-information)
- [Changing settings](#changing-settings)
- [Resetting settings](#resetting-settings)
- [Dedicated IP management](#dedicated-ip-management)

### Simple configuration

Users interact with `pypiactl` through the `PIA` object. The `PIA` object has little state, other than the active monitors (we'll get to that) and configuration. `PIA` can be configured like so:

```python
from pypiactl import PIA, PIAConfig

pia = PIA(PIAConfig(
    executable_path="/usr/local/bin/piactl",
    one_shot_timeout_in_s=10,
    debug_option=True
))
```

`PIA` configuration is completely optional, as will be demonstrated in the following examples. If you'd like to configure `one_shot_timeout_in_s` and `debug_option` on a more granular basis, you can pass them (as `timeout_in_s` and `debug_option`, respectively) into any of this library's methods (except for `PIA.version()`, `PIA.monitor.attach()`, and `PIA.monitor.detach()`).

### Checking CLI version

After initializing `PIA`, the first order of business is ensuring the CLI's version matches the library's version. You can print the CLI's version like so:

```python
from pypiactl import PIA

pia = PIA()

print(pia.version())
```

### Connecting and disconnecting

Assuming CLI version checks out, connecting and disconnecting using `PIA` is as simple as:

```python
from pypiactl import PIA

pia = PIA()

pia.connect()

# Do super cool thing!

pia.disconnect()
```

There are common reasons why these commands could fail. But how would you know if one of these commands failed, and why?

### Robust command results

Many of the library's methods return an instance of `PIACommandResult`:

#### `PIACommandResult` Attributes

<table>
  <tr>
    <th>Name</th>
    <th>Type</th>
    <th>Description</th>
  </tr>
  <tr>
    <td><code>status</code></td>
    <td>Typically <code><a href="#piacommandstatus-values">PIACommandStatus</a></code></td>
    <td>An enum conveying that the command succeeded, or why it didn't.</td>
  </tr>
  <tr>
    <td><code>data</code></td>
    <td>Varies</td>
    <td>The data the command retrieves/returns, if any. Otherwise, type is <code>None</code>.</td>
  </tr>
  <tr>
    <td><code>logs</code></td>
    <td><code>str</code> or <code>None</code></td>
    <td>The command's output and error logs.</td>
  </tr>
</table>

This begs the question, what are the values of `PIACommandStatus`?

#### `PIACommandStatus` Values

- `SUCCESS`
- `INVALID_ARGS`
- `TIMEOUT`
- `CONNECTION_LOST`
- `REQUIRES_CLIENT` (Means the PIA client is not running and the background daemon isn't enabled)
- `NOT_LOGGED_IN`
- `UNKNOWN_SETTING`
- `DEDICATED_IP_TOKEN_EXPIRED`
- `DEDICATED_IP_TOKEN_INVALID`
- `TEMP_FILE_ERROR` (Issues creating, writing to, and/or reading from a temp file)
- `OTHER_ERROR`

### Logging in and out

As previously mentioned, there are common reasons why the library may fail to connect or disconnect. The most critical is not being logged into PIA. The user can provide their credentials to log in through two different means.

The first is by writing their username and password in a text file like so:

```
p0000000
(yourpassword)
```

and passing in its path like so:

```python
from pypiactl import PIA

pia = PIA()

pia.login(credentials_file="super_secret_file.txt")
```

The second is by creating an instance of `PIACredentials`:

#### `PIACredentials` Attributes

<table>
  <tr>
    <th>Name</th>
    <th>Type</th>
    <th>Description</th>
  </tr>
  <tr>
    <td><code>username</code></td>
    <td><code>str</code></td>
    <td>PIA username (ex. <code>p0000000</code>)</td>
  </tr>
  <tr>
    <td><code>password</code></td>
    <td><code>str</code></td>
    <td>PIA password (ex. <code>(yourpassword)</code>)</td>
  </tr>
</table>

and passing it into `PIA` like so:

```python
from pypiactl import PIA, PIACredentials

pia = PIA()

pia.login(credentials=PIACredentials(
    username="p0000000",
    password="(yourpassword)"
))
```

Alternatively, the user can log out of PIA like so:

```python
from pypiactl import PIA

pia = PIA()

pia.logout()
```

### Background daemon control

Another reason the library might not be able to control connections is if (1) the PIA client is not running and (2) the background daemon isn't enabled. The second factor is easy to resolve within the library, like so:

```python
from pypiactl import PIA

pia = PIA()

pia.background.enable()

# Do cool VPN operations

pia.background.disable()
```

### Information types

Once the user is able to establish connections, they may wish to retrieve information about the connection, or perhaps change daemon settings which influence new connections (ex. the connection's region and protocol). To discuss this, we must first introduce the `PIAInformationType`. It is an enum used to describe pieces of information or settings to retrieve, monitor, and/or change.

#### `PIAInformationType` Values

<table>
  <tr>
    <th>Name</th>
    <th>Type</th>
    <th>Description</th>
  </tr>
  <tr>
    <td><code>ALLOW_LAN</code></td>
    <td><code>bool</code></td>
    <td>Whether to allow LAN traffic</td>
  </tr>
  <tr>
    <td><code>CONNECTION_STATE</code></td>
    <td><code><a href="#piaconnectionstate-values">PIAConnectionState</a></code></td>
    <td>VPN connection state</td>
  </tr>
  <tr>
    <td><code>DEBUG_LOGGING</code></td>
    <td><code>bool</code></td>
    <td>State of debug logging setting</td>
  </tr>
  <tr>
    <td><code>PORT_FORWARD</code></td>
    <td><code>int</code> or <code><a href="#piaportforwardstatus-values">PIAPortForwardStatus</a></code></td>
    <td>Forwarded port number if available, or the status of the request to forward a port</td>
  </tr>
  <tr>
    <td><code>PROTOCOL</code></td>
    <td><code><a href="#piaprotocol-values">PIAProtocol</a></code></td>
    <td>VPN connection protocol</td>
  </tr>
  <tr>
    <td><code>PUB_IP</code></td>
    <td><code><a href="https://docs.python.org/3/library/ipaddress.html#ipaddress.IPv4Address">ipaddress.IPv4Address</a></code> or <code>None</code></td>
    <td>Current public IP address</td>
  </tr>
  <tr>
    <td><code>REGION</code></td>
    <td><code>str</code></td>
    <td>Name of a region (or "auto)</td>
  </tr>
  <tr>
    <td><code>REGIONS</code></td>
    <td><code>set[str]</code></td>
    <td>List all available regions</td>
  </tr>
  <tr>
    <td><code>REQUEST_PORT_FORWARD</code></td>
    <td><code>bool</code></td>
    <td>Whether a forwarded port will be requested on the next connection attempt</td>
  </tr>
  <tr>
    <td><code>VPN_IP</code></td>
    <td><code><a href="https://docs.python.org/3/library/ipaddress.html#ipaddress.IPv4Address">ipaddress.IPv4Address</a></code> or <code>None</code></td>
    <td>Current VPN IP address</td>
  </tr>
</table>

#### `PIAConnectionState` Values

- `DISCONNECTED`
- `CONNECTING`
- `CONNECTED`
- `INTERRUPTED`
- `RECONNECTING`
- `DISCONNECTING_TO_RECONNECT`
- `DISCONNECTING`
- `UNKNOWN`

#### `PIAPortForwardStatus` Values

- `INACTIVE`
- `ATTEMPTING`
- `FAILED`
- `UNAVAILABLE`
- `UNKNOWN`

#### `PIAProtocol` Values

- `OPENVPN`
- `WIREGUARD`
- `UNKNOWN`

### Retrieving information

Any [`PIAInformationType`](#piainformationtype-values) value can be retrieved using the library like so:

```python
from pypiactl import PIA, PIAInformationType

pia = PIA()

print(pia.get(PIAInformationType.CONNECTION_STATE))
```

The type of the `data` attribute of the [`PIACommandResult`](#piacommandresult-attributes) instance that `PIA.get()` returns depends on the given [`PIAInformationType`](#piainformationtype-values).

### Monitoring information

Any [`PIAInformationType`](#piainformationtype-values) (except for `PIAInformationType.REGIONS`) can be monitored using the libary like so:

```python
import ipaddress
import time

from pypiactl import PIA, PIAInformationType

pia = PIA()

def observer(ip: ipaddress.IPv4Address):
    print(f"Public IP of VPN: {ip}")

pia.monitor.attach(PIAInformationType.VPN_IP, observer)

pia.connect()

# Within this time, observer() will be called with VPN's IP
time.sleep(5)

pia.disconnect()

# Within this time, observer() should be called with `None`

pia.monitor.detach(PIAInformationType.VPN_IP, observer)
```

Similarly to [retrieving information](#retrieving-information), the type of the value that the function passed into `PIA.monitor.attach()` is called with depends on the given [`PIAInformationType`](#piainformationtype-values).

### Changing settings

Any of the following [`PIAInformationType`](#piainformationtype-values) values can be updated:

- `PIAInformationType.ALLOW_LAN`
- `PIAInformationType.DEBUG_LOGGING`
- `PIAInformationType.PROTOCOL`
- `PIAInformationType.REGION`
- `PIAInformationType.REQUEST_PORT_FORWARD`

Like so:

```python
from pypiactl import PIA, PIAInformationType

pia = PIA()

pia.set(PIAInformationType.REGION, "jp-streaming-optimized")
```

The correct type for the given value depends on the [`PIAInformationType`](#piainformationtype-values) being updated.

### Resetting settings

The user can reset all settings (ports, protocols, etc.) to their defaults like so:

```python
from pypiactl import PIA

pia = PIA()

pia.reset_settings()
```

### Dedicated IP management

Finally, the user can manage dedicated IPs using the library. The user can provide their token through two different means.

The first is by writing their token in a text file like so:

```
DIP20000000000000000000000000000
```

and passing in its path like so:

```python
from pypiactl import PIA

pia = PIA()

pia.dedicated_ip.add(token_file="dedicated_ip_token.txt")
```

The second is by directly passing the token into `PIA` like so:

```python
from pypiactl import PIA

pia = PIA()

pia.dedicated_ip.add(token="DIP20000000000000000000000000000")
```

Alternatively, the user can remove a dedicated IP like so:

```python
from pypiactl import PIA

pia = PIA()

pia.dedicated_ip.remove("dedicated-sweden-000.000.000.000")
```

## Contributing

Any and all contributions are welcome! Please begin by [opening a new issue](https://github.com/LumaDevelopment/pypiactl/issues/new/choose) on the repository.

## License

`pypiactl` is licensed under the [GNU General Public License v2](LICENSE).
