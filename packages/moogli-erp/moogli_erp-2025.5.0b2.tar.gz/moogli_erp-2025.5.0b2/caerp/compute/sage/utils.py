from caerp.utils.compat import Iterable
from typing import Tuple


def fix_sage_ordering(items: Iterable[dict]) -> Iterable[dict]:
    """
    Ensure the line ordering of an export suits sage.

    For that, make sure each G-line is followed by all its matching A-line(s).

    Requirements:
    - Each A-line is anotated with a '_general_counterpart' key containing its general row.
    - if two A-line got groupped, their G-lines should have been grouped together also

    Considerations:
    - slicing/insertion with large python lists costs O(n), so we try avoiding it.

    The algorithm consists into two passes, one to detect orphans, and one to
    all items (incl. orphans) in the right order.
    """
    # First pass (no not defer yielding to be sure to have collected all orphans)
    anotated = list(_track_analytical_orphans(items))

    # Second pass
    for i in _with_orphans_inplace(anotated):
        yield i


def _track_analytical_orphans(items: Iterable[dict]) -> Iterable[dict]:
    """
    - For well-placed lines, will yield them as they come
    - For orphaned analytical lines, will list them in a list under the
      '_analytic_orphans' key on their reference row.
    """

    last_yielded_g = None

    for item in items:
        if item["type_"] == "A":
            g_counterpart = item["_general_counterpart"]
            if id(last_yielded_g) == id(g_counterpart):
                # A-line is following its G-line, everything OK for sage
                yield item
            else:
                try:
                    g_counterpart["_analytic_orphans"].append(item)
                except KeyError:
                    g_counterpart["_analytic_orphans"] = [item]
        else:  # G
            yield item
            last_yielded_g = item


def _with_orphans_inplace(items: Iterable[dict]) -> Iterable[dict]:
    """
    Flatten a list containing nested orphans

    Input format is data as yielded by _track_analytical_orphans
    """
    queued_orphans = []
    for item in items:
        if item["type_"] == "G":
            # Flush orphans before issuing a new G-line
            # not before, to preserve ordering as much as possible.
            for orphan_item in queued_orphans:
                yield orphan_item
            yield item
            queued_orphans = item.pop("_analytic_orphans", [])
        else:  # A
            yield item
    for orphan_item in queued_orphans:
        yield orphan_item


def add_entries_amounts(entry1: dict, entry2: dict) -> Tuple[int, int]:
    """
    We consider than either debit or credit is set on each entry.

    Sum two book entries, and returns either a debit or a credit.
    """
    d1 = entry1.get("debit")
    d2 = entry2.get("debit")
    c1 = entry1.get("credit")
    c2 = entry2.get("credit")
    debit, credit = "", ""

    assert not c1 or not d1, "Invalid entry {entry1}"
    assert not c2 or not d2, "Invalid entry {entry2}"

    if d1 and d2:
        debit = d1 + d2
    elif c1 and c2:
        credit = c1 + c2
    elif c1 and d2:
        credit = c1 - d2
    elif d1 and c2:
        debit = d1 - c2

    return debit, credit


def normalize_entry(entry: dict):
    """Force positive debit/credit

    entry will be modified inplace and returned (mutation)

    >>> normalize_entry(dict(debit=12))
    dict(debit=12)
    >>> normalize_entry(debit=-12)
    dict(credit=12)
    >>> normalize_entry(credit=-12)
    dict(debit=12)
    """
    credit = entry.get("credit")
    debit = entry.get("debit")

    assert (
        not credit or not debit
    ), f"entry should not have both a credit and debit: {entry}"

    if debit and debit < 0:
        entry["credit"] = -debit
        del entry["debit"]

    if credit and credit < 0:
        entry["debit"] = -credit
        del entry["credit"]

    return entry
