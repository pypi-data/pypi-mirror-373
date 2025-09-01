import re
from datetime import date, timedelta
from locale import format_string, localeconv
from math import ceil, floor, log10
from typing import Any, Callable, Iterable, Iterator, Literal, Sequence, TypeVar, overload
from urllib.parse import parse_qs, urlencode, urlsplit, urlunsplit


_T = TypeVar("_T")
_NT = TypeVar("_NT", int, float)


def append_query_to_url(url: str, params: dict, conditional_params: dict | None = None, safe: str = '') -> str:
    """
    Adds GET query from `params` to `url`, or appends it if there already is
    one.

    `conditional_params` will only be used if GET params with those keys are
    not already present in the original url or in `params`.

    Return the new url.
    """
    parts = urlsplit(url)
    conditional_params = conditional_params or {}
    qs = {
        **conditional_params,
        **parse_qs(parts.query),
        **params,
    }
    parts = parts._replace(query=urlencode(qs, doseq=True, safe=safe))
    return urlunsplit(parts)


def can_coerce_to_int(value: Any) -> bool:
    return to_int(value) is not None


def circulate(lst: Iterable[_T], rounds: int) -> list[_T]:
    """
    Shifts `lst` left `rounds` times. Good for e.g. circulating colours in
    a graph.
    """
    if not isinstance(lst, list):
        lst = list(lst)
    if lst and rounds:
        for _ in range(rounds):
            val = lst.pop(0)
            lst.append(val)
    return lst


def coerce_between(value: _NT, min_value: _NT, max_value: _NT) -> _NT:
    if value < min_value:
        return min_value
    if value > max_value:
        return max_value
    return value


def daterange(start_date: date, end_date: date) -> Iterator[date]:
    """
    Iterates the dates between `start_date` (inclusive) and `end_date`
    (exclusive).
    """
    for n in range(int((end_date - start_date).days)):
        yield start_date + timedelta(days=n)


def filter_values_not_null(d: dict) -> dict:
    return {k: v for k, v in d.items() if v is not None}


def first_not_null(*values: _T | None) -> _T:
    ret = first_not_null_or_null(*values)
    if ret is None:
        raise TypeError("All values are None")
    return ret


def first_not_null_or_null(*values: _T | None) -> _T | None:
    for value in values:
        if value is not None:
            return value
    return None


def getitem_nullable(seq: Iterable[_T], idx: int, cond: Callable[[_T], bool] | None = None) -> _T | None:
    """
    If `seq` has an item at position `idx`, return that item. Otherwise return
    None. Similar to how QuerySet's first() & last() operate.

    With `cond` set, it first filters `seq` for items where this function
    evaluates as True, then tries to get item `idx` from the resulting list.

    Example:

    seq = [23, 43, 12, 56, 75, 1]
    second_even = getitem_nullable(seq, 1, lambda item: item % 2 == 0)
    # second_even == 56
    seq = [1, 2, 3, 5, 7]
    second_even = getitem_nullable(seq, 1, lambda item: item % 2 == 0)
    # second_even == None
    """
    try:
        if cond is None:
            return list(seq)[idx]
        return [item for item in seq if cond(item)][idx]
    except IndexError:
        return None


@overload
def getitem0(seq: Iterable[_T], cond: Callable[[_T], bool] | None, nullable: Literal[False]) -> _T: ...


@overload
def getitem0(seq: Iterable[_T], cond: Callable[[_T], bool] | None, nullable: Literal[True]) -> _T | None: ...


def getitem0(seq, cond=None, nullable=False):
    """
    @raises IndexError
    """
    try:
        if cond is None:
            return list(seq)[0]
        return [item for item in seq if cond(item)][0]
    except IndexError as e:
        if nullable:
            return None
        raise e


def getitem0_nullable(seq: Iterable[_T], cond: Callable[[_T], bool] | None = None) -> _T | None:
    return getitem0(seq, cond, True)


def group_by(sequence: Sequence[_T], pred: Callable[[_T], Any]) -> dict[Any, list[_T]]:
    """
    Groups `sequence` by the result of `pred` on each item. Returns dict with
    those results as keys and sublists of `sequence` as values.
    """
    result: dict[Any, list[_T]] = {}
    for item in sequence:
        key = pred(item)
        if key not in result:
            result[key] = [item]
        else:
            result[key].append(item)
    return result


def group_dicts(
    dicts: Iterable[dict[str, _T]],
    keys: list[str],
    data_key: str = "data",
) -> list[dict[str, _T | list[dict[str, _T]]]]:
    """
    In:
        dicts = [
            {"slug": "musikensmakt", "name": "Musikens Makt", "date": "2025-04-01", "count": 60},
            {"slug": "musikensmakt", "name": "Musikens Makt", "date": "2025-04-02", "count": 64},
            {"slug": "apanap", "name": "Apan Ap", "date": "2025-04-01", "count": 2},
        ]
        keys = ["slug", "name"]
        data_key = "dätä"
    Out: [
        {
            "slug": "musikensmakt",
            "name": "Musikens Makt",
            "dätä": [{"date": "2025-04-01", "count": 60}, {"date": "2025-04-02", "count": 64}],
        },
        {
            "slug": "apanap",
            "name": "Apan Ap",
            "dätä": [{"date": "2025-04-01", "count": 2}],
        },
    ]
    """
    result: dict[tuple[_T, ...], list] = {}

    for d in dicts:
        dd = d.copy()
        d_key = tuple(d[key] for key in keys)
        if d_key not in result:
            result[d_key] = []
        for key in keys:
            del dd[key]
        result[d_key].append(dd)

    return [{data_key: v, **{keys[i]: k[i] for i in range(len(keys))}} for k, v in result.items()]


def index_of_first(sequence: Sequence[_T], pred: Callable[[_T], bool]) -> int:
    """
    Tries to return the index of the first item in `sequence` for which the
    function `pred` returns True. If no such item is found, return -1.
    """
    try:
        return sequence.index(next(filter(pred, sequence)))
    except StopIteration:
        return -1


def int_to_string(value: int | None, locale: str, nbsp: bool = False) -> str:
    """
    Formats an integer with locale-specific thousand separators, which are at
    least correct for Swedish and English locales. (Usage of the functions in
    the built-in `locale` package requires you to run setlocale() multiple
    times, which is not thread safe and may be resource heavy, so we don't do
    that.)
    """
    if value is None:
        return ""
    if locale.lower().startswith("sv"):
        separator = " "
    else:
        separator = ","
    if separator == " " and nbsp:
        separator = "&nbsp;"
    # Neat line of code, huh? :)
    # 1. Use absolute value to get rid of minus sign
    # 2. Reverse str(value) in order to group characters from the end
    # 3. Split it by groups of 3 digits
    # 4. Remove empty values generated by re.split()
    # 5. Re-reverse the digits in each group & join them with separator string
    # 6. Re-reverse the order of the groups
    # 7. Add minus sign if value was negative
    return (
        ("-" if value < 0 else "") +
        separator.join([v[::-1] for v in re.split(r"(\d{3})", str(abs(value))[::-1]) if v][::-1])
    )


def is_truthy(value: Any) -> bool:
    """
    Basically does `bool(value)`, except it also returns False for string
    values "false", "no", and "0" (case insensitive).
    """
    if isinstance(value, str) and value.lower() in ("false", "no", "0"):
        return False
    return bool(value)


def localize_float(
    value: float,
    grouping: bool = True,
    min_decimals: int | None = None,
    max_decimals: int | None = None,
) -> str:
    if max_decimals is None:
        max_decimals = 15

    if min_decimals is not None and min_decimals > max_decimals:
        raise ValueError("min_decimals must be <= max_decimals")
    if 15 < (min_decimals or 0) < 0:
        raise ValueError("min_decimals must be >= 0 and <= 15")
    if 15 < (max_decimals or 0) < 0:
        raise ValueError("max_decimals must be >= 0 and <= 15")

    decimal_separator = localeconv()["decimal_point"]
    ret = format_string("%.*f", (max_decimals, value), grouping=grouping)

    if decimal_separator in ret:
        base, decimals = ret.split(decimal_separator)
        decimals = decimals.rstrip("0").ljust(min_decimals or 0, "0")
        if not decimals:
            return base
        return base + decimal_separator + decimals

    return ret


def nonulls(items: Iterable[_T | None]) -> list[_T]:
    """Just filters away None values from `items`."""
    return [item for item in items if item is not None]


def partition(items: Sequence[_T], length: int) -> Iterator[Sequence[_T]]:
    """Simply splits `items` into subsequences of max `length` items."""
    offset = 0
    while offset == 0 or offset < len(items):
        yield items[offset:offset + length]
        offset += length


def percent_rounded(part: int | float, whole: int | float) -> int:
    if not whole:
        return 0
    return round(part / whole * 100)


def round_to_n(x: int | float, n: int) -> int | float:
    """
    Rounds x to n significant digits. If the result is a whole number, it is
    cast to int, otherwise float is returned.
    """
    if x == 0:
        return x
    result = round(x, -int(floor(log10(abs(x)))) + (n - 1))
    return int(result) if not result % 1 else result


def round_up_timedelta(td: timedelta) -> timedelta:
    """
    If td > 30 min, round up to nearest hour. Otherwise, to nearest 10
    minute mark. Could be extended for higher time units, but nevermind now.
    """
    td_minutes = td.total_seconds() / 60
    if td_minutes > 30:
        return timedelta(hours=ceil(td_minutes / 60))
    if td_minutes >= 10:
        return timedelta(minutes=int(td_minutes / 10) * 10 + 10)
    return timedelta(minutes=10)


def rounded_percentage(part: int | float, whole: int | float, digits=3) -> int | float:
    """Percentage rounded to `digits` significant digits."""
    return round_to_n((part / whole) * 100, digits) if whole != 0 else 0


def strip_url_query(url: str) -> str:
    """Just returns `url` stripped of any GET parameters."""
    parts = urlsplit(url)
    return urlunsplit((parts.scheme, parts.netloc, parts.path, '', parts.fragment))


def to_int(value: Any, default: int | None = None) -> int | None:
    """Like int() but returns a default value instead of raising exception."""
    try:
        return int(value)
    except (ValueError, TypeError):
        return default


def zip_dicts(*dicts: dict) -> dict:
    """
    Combines dicts into one dict. On duplicate keys, dicts later in the
    sequence have priority.
    """
    return {k: v for d in dicts for k, v in d.items()}


def zip_dict_lists(dict_lists: Sequence[Sequence[dict]]) -> Iterator[dict]:
    """
    Zips a list of dict lists and combines them into single dicts.
    I.e. given dict_lists = [
        [{a1: 1, a2: 2}, {b1: 3, b2: 4}],
        [{a3: 5, a4: 6}, {b3: 7, b4: 8}],
    ],
    these dicts will be yielded:
    {a1: 1, a2: 2, a3: 5, a4: 6}
    {b1: 3, b2: 4, b3: 7, b4: 8}
    """
    for dicts in zip(*dict_lists):
        yield zip_dicts(*dicts)
