from collections import defaultdict
from dataclasses import dataclass
import argparse
import json
import sys


def filter_events_by_name(events, excludes):
    return [e for e in events if e["name"] not in excludes]


def count_events(events, excludes=[]):
    exclude_events = [
        # "top",
        # "query.main",
        "fireducks.core.evaluate",
        "fireducks_ext.execute",
        "fire::ExecuteBEF",
    ]

    events = filter_events_by_name(events, exclude_events)

    dur = defaultdict(float)
    cnt = defaultdict(int)
    ex = 0
    for e in events:
        if e["name"] in excludes:
            ex += e["dur"]
        else:
            dur[e["name"]] += e["dur"]
            cnt[e["name"]] += 1

    elapsed = max([e["dur"] for e in events])
    return dur, cnt, elapsed - ex


def is_kernel(name):
    return (
        name.startswith("fireducks.")
        or name.startswith("tfrt.")
        or name.startswith("tfrt_test.")
    )


def count_traces(traces, out=sys.stderr, limit=10):
    def _print(*args, **kwargs):
        print(*args, **kwargs, file=out)

    @dataclass
    class Event:
        name: str
        duration: float = 0.0
        count: int = 0

    dic = {}  # name: Event
    elapsed = 0
    for levents in traces:
        ldur, lcnt, lelapsed = count_events(levents)

        elapsed += lelapsed
        for name in ldur:
            if name not in dic:
                dic[name] = Event(name)
            dic[name].duration += ldur[name]
            dic[name].count += lcnt[name]

    events = dic.values()
    events = list(reversed(sorted(events, key=lambda e: e.duration)))
    # remove kernel trace
    events = [e for e in events if not e.name.startswith("kernel:")]

    fallbacks = [e for e in events if e.name.startswith("fallback:")]
    kernels = [e for e in events if is_kernel(e.name)]
    others = [e for e in events if e not in fallbacks and e not in kernels]

    def print_tot(name, events, elapsed):
        dur = sum([e.duration for e in events])
        cnt = sum([e.count for e in events])
        _print(
            f"{name:12}{dur/1e6:12.3f} sec {dur*1e2/elapsed:6.2f}% {cnt:8d}"
        )

    _print(f"elapsed     {elapsed/1e6:12.3f} sec")
    print_tot("kernels", kernels, elapsed)
    print_tot("fallbacks", fallbacks, elapsed)

    def print_events(events, elapsed, namelen):
        for e in events:
            _print(
                f"{e.name:{namelen}}{e.duration/1e6:12.3f}"
                f"{e.duration*1e2/elapsed:8.2f}% {e.count:10d}"
            )

    if limit > 0:
        kernels = kernels[0:limit]
        fallbacks = fallbacks[0:limit]
        others = others[0:limit]

    namelen = max([len(e.name) for e in kernels + fallbacks + others])

    # header
    _print(f"{'':{namelen}}{'duration sec':13}{'ratio':9} {'count':10}")

    _print("== kernel ==")
    print_events(kernels, elapsed, namelen)
    _print("== fallback ==")
    print_events(fallbacks, elapsed, namelen)
    _print("== other == ")
    print_events(others, elapsed, namelen)


def print_profile(js: str):
    obj = json.loads(js)
    traces = [e for e in obj["traceEvents"] if "pid" in e]
    count_traces([traces], sys.stderr)
