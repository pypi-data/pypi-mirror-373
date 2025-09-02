import argparse
import logging
import time

from .client import ClientResolver
from .server import ServerResolver, ServerDestination


def main():
    parser = argparse.ArgumentParser(description="Resolve a matrix server name")
    parser.add_argument("--quiet", "-q", action="count", help="Suppress logging output. Pass twice to only output resolved destinations.")
    parser.add_argument("--client-only", "-c", action="store_true", help="Only perform client resolution")
    parser.add_argument("--server-only", "-s", action="store_true", help="Only perform server resolution")
    parser.add_argument("--timed", "-t", action="store_true", help="Output the time taken for each resolution step")
    parser.add_argument("--versions", "-v", action="store_true", help="Print server version information")
    parser.add_argument("server_name", type=str, help="The matrix server name to resolve")
    args = parser.parse_args()

    cr = ClientResolver()
    sr = ServerResolver()
    if args.quiet is None:
        logging.basicConfig(
            level=logging.INFO,
            format="[%(levelname)s\t%(name)s]\t %(message)s",
        )
        logging.getLogger("resolvematrix").setLevel(logging.DEBUG)

    resolves: dict[str, None | ServerDestination | str] = {"client": None, "server": None}
    timings: dict[str, None | float] = {"server": None, "client": None}
    if not args.client_only:
        n = time.perf_counter()
        resolves["server"] = sr.resolve(args.server_name)
        timings["server"] = time.perf_counter() - n
    if not args.server_only:
        n = time.perf_counter()
        resolves["client"] = cr.resolve(args.server_name)
        timings["client"] = time.perf_counter() - n

    if args.quiet == 2:
        for key, value in resolves.items():
            if value is not None:
                print(value)
    else:
        if args.quiet is None:
            print()  # differentiate from logging output
        for key, value in resolves.items():
            if value is not None:
                print(f"{key} destination: {value}")

        if args.timed:
            for key, value in timings.items():
                if resolves[key] is not None:
                    print(f"{key} resolution took {value:.3f} seconds")

        if args.versions:
            print()
            if resolves["client"] is not None:
                if isinstance(resolves["client"], str):
                    ver = cr.get_client_versions(resolves["client"])
                    print(f"{args.server_name} supports spec versions {', '.join(repr(v) for v in ver.versions)}")
                    for feature, support in ver.unstable_features.items():
                        if support:
                            print(f"  - supports unstable feature {feature!r}")
            if resolves["server"] is not None:
                if isinstance(resolves["server"], ServerDestination):
                    name, version = sr.get_server_version(resolves["server"])
                    print(f"{args.server_name} is running {name!r} version {version!r}")
                    keys = sr.get_server_keys(resolves["server"])
                    print(f"  - has {len(keys.verify_keys)} active signing keys ({', '.join(keys.verify_keys)})")
                    print(f"  - has {len(keys.old_verified_keys)} expired signing keys ({', '.join(keys.old_verified_keys)})")
