# ResolveMatrix

ResolveMatrix is a Python library providing the utilities required to resolve both client and server to server
API endpoints. It fully conforms to the Matrix specification outlined
[in the client-to-server specification](https://spec.matrix.org/v1.15/client-server-api/#server-discovery) and
[server-to-server specification](https://spec.matrix.org/v1.15/server-server-api/#server-discovery).

## Installing

You can install the latest release from PyPI:

```bash
pip install --pre resolvematrix
```

Or get the latest via Git:

```bash
pip install git+https://codeberg.org/timedout/resolvematrix.git
```

## Usage

### Command line

You can use the command `mxresolve` to resolve a server name from the command line:

```bash
$ mxresolve continuwuity.rocks
[DEBUG  resolvematrix.server]    requesting well-known for 'continuwuity.rocks'
[INFO   httpx]   HTTP Request: GET https://continuwuity.rocks/.well-known/matrix/server "HTTP/1.1 200 OK"
[DEBUG  resolvematrix.server]    'continuwuity.rocks' is delegated to 'continuwuity.rocks:443'
[DEBUG  resolvematrix.server]    delegated hostname 'continuwuity.rocks' for 'continuwuity.rocks' includes explicit port, skipping SRV lookup
[DEBUG  resolvematrix.client]    Resolving well-known for continuwuity.rocks
[INFO   httpx]   HTTP Request: GET https://continuwuity.rocks/.well-known/matrix/client "HTTP/1.1 200 OK"
[DEBUG  resolvematrix.client]    Validating resolved base URL https://continuwuity.rocks for continuwuity.rocks
[INFO   httpx]   HTTP Request: GET https://continuwuity.rocks/_matrix/client/versions "HTTP/1.1 200 OK"
[DEBUG  resolvematrix.client]    Client versions at https://continuwuity.rocks: versions=['r0.0.1', 'r0.1.0', 'r0.2.0', 'r0.3.0', 'r0.4.0', 'r0.5.0', 'r0.6.0', 'r0.6.1', 'v1.1', 'v1.2', 'v1.3', 'v1.4', 'v1.5', 'v1.8', 'v1.11', 'v1.12', 'v1.13', 'v1.14'] unstable_features={'org.matrix.e2e_cross_signing': True, 'org.matrix.msc2285.stable': True, 'org.matrix.msc2836': True, 'org.matrix.msc2946': True, 'org.matrix.msc3026.busy_presence': True, 'org.matrix.msc3575': True, 'org.matrix.msc3827': True, 'org.matrix.msc3916.stable': True, 'org.matrix.msc3952_intentional_mentions': True, 'org.matrix.msc4180': True, 'org.matrix.simplified_msc3575': True, 'uk.half-shot.msc2666.query_mutual_rooms': True, 'uk.tcpip.msc4133': True, 'us.cloke.msc4175': True}

client destination: https://continuwuity.rocks
server destination: ServerDestination(hostname='continuwuity.rocks:443', host_header='continuwuity.rocks:443', sni='continuwuity.rocks')
```

### Client to Server

You can resolve a server name as follows:

```python
import resolvematrix

resolver = resolvematrix.ClientResolver()
result = resolver.resolve("example.com")
print(result)  # "https://matrix.example.com"

# You can also use the server_from_user_id helper utility to extract the server name from a user ID:
result = resolver.resolve(resolvematrix.server_from_user_id("@alice:example.com"))
print(result)  # "https://matrix.example.com"

# And even manually pass a server URL!
result = resolver.resolve("https://matrix.example.com")
print(result)  # "https://matrix.example.com"
```

### Server to Server

You can resolve a server name as follows:

```python
import resolvematrix

resolver = resolvematrix.ServerResolver()
result = resolver.resolve("matrix.org")
print(repr(result))  # "ServerDestination(hostname='matrix-federation.matrix.org:443', host_header='matrix-federation.matrix.org:443', sni='matrix-federation.matrix.org')"

# You then need to do a little bit of wrangling to get an actual connection.
import httpx

response = resolver.client.get(
    f"{result.base_url}/_matrix/federation/v1/version",
    headers={"Host": result.host_header},
    extensions={"sni_hostname": result.sni} if result.sni else {},
).raise_for_status()

# Other libraries may have different ways of specifying SNI and custom Host headers.
# See also: https://stackoverflow.com/a/77743443
```

## Contact

Talk to me in my matrix room: [#ontopic:timedout.uk](https://matrix.to/#/#ontopic:timedout.uk).
