from pathlib import Path

from rich import print
from rich.progress import Progress, track

from arkindex_cli.auth import Profiles
from arkindex_cli.utils import Timer


def benchmark_top_levels(client):
    """Load the first page of top level elements for all corpora"""

    # List all available corpus
    corpora = client.request("ListCorpus")

    total = 0
    with Timer() as timer:
        # Get the first page of top level elements
        for corpus in track(corpora, description="Listing top level elements"):
            elements = client.request(
                "ListElements", corpus=corpus["id"], top_level=True
            )

            total += elements["count"]

    print(
        f"Loaded {total} top level elements from {len(corpora)} corpora in {timer.delta}"
    )


TESTS = {
    "top-levels": benchmark_top_levels,
}


def add_benchmark_parser(subcommands) -> None:
    parser = subcommands.add_parser(
        "benchmark",
        description="Run a set of benchmark tests on an Arkindex instance",
        help="Run a set of benchmark tests on an Arkindex instance",
    )
    parser.add_argument(
        "-t",
        "--test",
        dest="tests",
        nargs="+",
        choices=TESTS.keys(),
        type=str,
        help="Limit tests to run on the instance",
    )
    parser.add_argument(
        "-l",
        "--list",
        dest="list_tests",
        action="store_true",
        default=False,
        help="List all the available tests",
    )
    parser.set_defaults(func=run)


def run(
    tests: list[str] | None = [],
    list_tests: bool = False,
    profile_slug: str | None = None,
    gitlab_secure_file: Path | None = None,
) -> int:
    # List all available benchmark tests
    if list_tests:
        print("[red]Available benchmarks:")
        for test in TESTS.keys():
            print(test)
        return

    # Connect to instance
    with Progress(transient=True) as progress:
        progress.add_task(start=False, description="Loading API client")
        profiles = Profiles(gitlab_secure_file)
        client = profiles.get_api_client_or_exit(profile_slug)

    # By default, run all tests
    if not tests:
        tests = TESTS.keys()

    for test_name in tests:
        print(f"[blue]Running {test_name} ...")
        stats = TESTS[test_name](client)
        print(stats)
