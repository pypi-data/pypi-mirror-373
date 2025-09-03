from __future__ import annotations

from collections import defaultdict
from collections.abc import Sequence
from dataclasses import dataclass
from dataclasses import field
from decimal import ROUND_HALF_UP
from decimal import Decimal
from decimal import localcontext
from sys import float_info
from typing import Annotated
from typing import Literal
from typing import cast
from typing import overload

from docnote import ClcNote

from finnr._types import DateLike
from finnr._types import Singleton
from finnr.money import Money


@dataclass(slots=True, frozen=True)
class Currency:
    code_alpha3: Annotated[
        str,
        ClcNote('''For all ISO currencies, this is the ISO 4217 alpha-3
            currency code. If implementing custom currencies as part of your
            own ``CurrencySet``, this can be anything you want, but:
            ++  it must uniquely identify the currency
            ++  it must be uppercase-only for ``CurrencySet`` to find it in
                any of its lookup functions.''')]

    code_num: Annotated[
        int,
        ClcNote('''For all ISO currencies, this is the ISO 4217 numeric
            currency code. If implementing custom currencies as part of your
            own ``CurrencySet``, this can be anything you want, but it must
            uniquely identify the currency.''')]

    minor_unit_denominator: Annotated[
        int | None | Literal[Singleton.UNKNOWN],
        ClcNote('''The minor unit denominator is used (only) when rounding
            ``Money`` amounts. It determines the minimal fractional unit of
            the currency. For example, with USD or EUR, both of which can be
            broken into 100 cents, it would be 100.

            A value of ``None`` indicates that the currency amounts are
            continuous and cannot be rounded; this is the case with some
            units of account.

            If unknown, then rounding will be a no-op, simply returning a
            copy of the ``Money`` object with the same ``amount``.''')]

    entities: Annotated[
        frozenset[str],
        ClcNote('''For all ISO currencies, this will be a set of strings,
            each containing the ISO 3166 alpha-2 country code. This is
            provided on a best-effort basis, intended primarily for reference,
            and may not be entirely correct.

            If the country no longer exists, it will instead be the 4-letter
            ISO 3166-3 code.

            It may also be empty (for example, for commodities and units of
            account).

            If implementing custom currencies as part of your own
            ``CurrencySet``, this can be truly anything. It is not used
            internally by finnr.''')
        ] = field(compare=False)

    name: Annotated[
        str | Literal[Singleton.UNKNOWN],
        ClcNote('''For all ISO currencies, this is the common name of the
            currency, in English. This is provided on a best-effort basis,
            intended primarily for reference, and may not be entirely correct.

            If implementing custom currencies as part of your own
            ``CurrencySet``, this can be truly anything. It is not used
            internally by finnr.''')
        ] = field(compare=False)

    approx_active_from: Annotated[
        DateLike | Literal[Singleton.UNKNOWN],
        ClcNote('''For all ISO currencies, this is the approximate first date
            of use of the currency. This is provided on a best-effort basis,
            intended primarily for reference, and may not be entirely correct.
            In many cases, the date given may be more precise than the actual
            phase-out of the currency.

            This is used purely to calculate the ``is_active`` property and
            ``was_active_at`` function.

            If implementing custom currencies as part of your own
            ``CurrencySet``, you must set the ``approx_active_from``
            appropriately for the desired behavior of those two properties.''')
        ] = field(compare=False)

    approx_active_until: Annotated[
        DateLike | Literal[Singleton.UNKNOWN] | None,
        ClcNote('''For all ISO currencies, this is the approximate last date
            of use of the currency. This is provided on a best-effort basis,
            intended primarily for reference, and may not be entirely correct.
            In many cases, the date given may be more precise than the actual
            phase-out of the currency.

            This is used purely to calculate the ``is_active`` property and
            ``was_active_at`` function.

            If implementing custom currencies as part of your own
            ``CurrencySet``, you must set the ``approx_active_until``
            appropriately for the desired behavior of those two properties.''')
        ] = field(compare=False)

    @property
    def is_active(self) -> bool:
        """Returns ``True`` if, and only if, the currency is currently
        active -- ie, if ``approx_active_until`` is None. Note that this
        will return **``False``** if ``approx_active_until`` is unknown.
        """
        return self.approx_active_until is None

    def mint(
            self,
            amount: Decimal | float | str | tuple[int, Sequence[int], int],
            *,
            heal_float: Annotated[
                bool,
                ClcNote('''If ``True`` (the default), this will truncate the
                    resulting decimal amount to the maximum safe float value,
                    as determined by ``sys.float_info.dig``. Note that this
                    only has an effect if the passed ``amount`` is a float!
                    ''')
                ] = True,
            quantize_to_minor: Annotated[
                bool,
                ClcNote('''If ``True`` (**not** the default), this will
                    immediately round or "pad" (ie, quantize) the resulting
                    decimal amount to a single unit of the minor unit of the
                    currency. For example, ``12.345 EUR`` would be rounded to
                    ``12.35 EUR``, or ``1.2 EUR`` "padded" to ``1.20 EUR``.
                    ''')
                ] = False,
            rounding: Annotated[
                str,
                ClcNote('''If ``quantize_to_minor`` is ``True``, this can be
                    used to control the rounding behavior of the quantization
                    operation.

                    Otherwise, this is ignored.''')
                ] = ROUND_HALF_UP
            ) -> Money:
        """Creates a Money instance for the current currency, using the
        passed amount.
        """
        if heal_float and isinstance(amount, float):
            dec_amount = _heal_float(Decimal(amount))
        elif isinstance(amount, Decimal):
            dec_amount = amount
        else:
            dec_amount = Decimal(amount)

        if quantize_to_minor:
            currency_metadata = self._metadata
            # If this is None, it means either that the currency is continuous
            # (eg a fictional unit of account), or that the minor unit is
            # unknown; in both of those cases, we'll skip rounding and simply
            # use the original dec_amount. Otherwise, we've work to do!
            if currency_metadata.minor_quantizor is not None:
                dec_amount = dec_amount.quantize(
                    currency_metadata.minor_quantizor,
                    rounding=rounding)

                if not currency_metadata.is_decimal:
                    # Note that this must be int, or the minor_quantizor
                    # would be None.
                    minor_denom = cast(int, self.minor_unit_denominator)
                    # This seems a little aroundabout, but we're doing it this
                    # way so that we can respect the passed rounding behavior.
                    # Otherwise it would probably be faster to do this via mod.
                    shifted_amount = dec_amount * minor_denom
                    with localcontext() as ctx:
                        ctx.rounding = rounding
                        # Note that the zero here is necessary to keep it a
                        # decimal, otherwise we'll end up with an int
                        rounded_shifted_amount = round(shifted_amount, 0)

                    dec_amount = rounded_shifted_amount / minor_denom

        return Money(
            amount=dec_amount,
            currency=self)

    # TODO (Note that this gets a bit complicated due to Unknowns):
    # def was_active_at(self, date: DateLike) -> bool:

    _metadata: _CurrencyMetadata = field(init=False, compare=False, repr=False)
    def __post_init__(self):
        if (
            self.minor_unit_denominator is None
            or self.minor_unit_denominator is Singleton.UNKNOWN
        ):
            minor_quantizor = None
            is_decimal = True

        else:
            minor_quantizor = Decimal(1) / self.minor_unit_denominator
            is_decimal = not bool(self.minor_unit_denominator % 10)

        object.__setattr__(self, '_metadata', _CurrencyMetadata(
            minor_quantizor, is_decimal))


@dataclass(slots=True)
class _CurrencyMetadata:
    """Currency metadata is calculated on currency instances as a
    performance optimization (and also, because it makes the logic
    cleaner).
    """
    minor_quantizor: Decimal | None
    is_decimal: bool


class CurrencySet(frozenset[Currency]):
    """``CurrencySet``s are a ``frozenset[Currency]`` subclass that
    contain convenience methods for finding currencies and creating
    ``Money`` objects based on the currency codes known to the
    ``CurrencySet``.

    If desired, you can implement custom currencies simply by creating
    your own ``CurrencySet`` with whatever ``Currency`` objects you
    want. Note that all ``Currency`` objects within a ``CurrencySet``
    **must** have unique alpha and numeric codes.
    """
    _by_alpha3: dict[str, Currency]
    _by_num: dict[int, list[Currency]]

    def __init__(self, *args, **kwargs):
        self._by_alpha3 = alpha_lookup = {}
        self._by_num = num_lookup = defaultdict(list)

        for currency in self:
            if currency.code_alpha3 in alpha_lookup:
                raise ValueError(
                    'Duplicate currency code (alpha)!', currency.code_alpha3)

            # We're using get here because we want to avoid mutation unless
            # it's going to be added in
            if (dupes := num_lookup.get(currency.code_num, [])):
                sortkeys = {
                    _sortkey_most_recently_active(dupe)
                    for dupe in dupes}
                if _sortkey_most_recently_active(currency) in sortkeys:
                    raise ValueError(
                        'Duplicate currency code (num) with overlapping '
                        + 'active dates!',
                        currency.code_num, currency.code_alpha3)

            alpha_lookup[currency.code_alpha3] = currency
            num_lookup[currency.code_num].append(currency)

        num_lookup.default_factory = None
        # This is important! We use this for retrieval, to make sure we always
        # get the most recently active if no specific date was provided
        for by_num_list in num_lookup.values():
            by_num_list.sort(
                key=_sortkey_most_recently_active,
                reverse=True)

    def __call__(
            self,
            amount: Decimal | float | str | tuple[int, Sequence[int], int],
            code_alpha3: str,
            *,
            heal_float: Annotated[
                bool,
                ClcNote('''If ``True`` (the default), this will truncate the
                    resulting decimal amount to the maximum safe float value,
                    as determined by ``sys.float_info.dig``. Note that this
                    only has an effect if the passed ``amount`` is a float!
                    ''')
                ] = True,
            quantize_to_minor: Annotated[
                bool,
                ClcNote('''If ``True`` (**not** the default), this will
                    immediately round or "pad" (ie, quantize) the resulting
                    decimal amount to a single unit of the minor unit of the
                    currency. For example, ``12.345 EUR`` would be rounded to
                    ``12.35 EUR``, or ``1.2 EUR`` "padded" to ``1.20 EUR``.
                    ''')
                ] = False,
            rounding: Annotated[
                str,
                ClcNote('''If ``quantize_to_minor`` is ``True``, this can be
                    used to control the rounding behavior of the quantization
                    operation.

                    Otherwise, this is ignored.''')
                ] = ROUND_HALF_UP
            ) -> Money:
        """Mints a new instance of the currency. Arguments have the same
        meaning as ``Currency.mint``.
        """
        try:
            currency = self._by_alpha3[code_alpha3.upper()]
        except KeyError as exc:
            exc.add_note('Invalid currency code for this CurrencySet!')
            raise exc

        return currency.mint(
            amount,
            heal_float=heal_float,
            quantize_to_minor=quantize_to_minor,
            rounding=rounding)

    @overload
    def get[T](self, code: str, default: T = None) -> Currency | T: ...
    @overload
    def get[T](
            self,
            code: int,
            default: T = None,
            *,
            on_date: DateLike | None = None,
            ) -> Currency | T: ...

    def get[T](
            self,
            code: str | int,
            default: T = None,
            *,
            on_date: DateLike | None = None,
            ) -> Currency | T:
        """Finds a currency from the currency set based on either the
        alpha3 or numeric code. This has the same semantics as
        ``dict.get``, in that it will return the provided ``default``
        value if no match is found (and if no explicit default is
        passed, this will return ``None``).

        Note that numeric codes aren't necessarily unique across all
        time (at least for ISO). As such, if you want to look up a
        currency based on its numeric code, you should specify a
        date for clarity. If none is specified, we'll return the
        currency that was most recently active (which, in most case,
        will be the currently-active currency with that code).
        """
        if isinstance(code, str):
            return self._by_alpha3.get(code.upper(), default)

        elif isinstance(code, int):
            if code not in self._by_num:
                return default

            for_all_nums = self._by_num[code]
            if on_date is None:
                return for_all_nums[0]

            else:
                currency = _get_on_specific_date(for_all_nums, on_date)
                if currency is None:
                    return default
                else:
                    return currency

        else:
            raise TypeError('Code must be either string or integer!', code)


def _get_on_specific_date(
        bynum_list: list[Currency],
        target_date: DateLike
        ) -> Currency | None:
    """Use this to find a currency defined on a particular date. Returns
    None if there wasn't any there.
    """
    for currency in bynum_list:
        # Note that this relies upon the bynum_list sorting to work!
        if (
            currency.approx_active_until is None
            or currency.approx_active_until is Singleton.UNKNOWN
            or (
                _quickcomp_datelike(target_date)
                <= _quickcomp_datelike(currency.approx_active_until))
        ):
            if currency.approx_active_from is Singleton.UNKNOWN:
                return currency
            elif (
                _quickcomp_datelike(target_date)
                >= _quickcomp_datelike(currency.approx_active_from)
            ):
                return currency


def _quickcomp_datelike(datelike: DateLike) -> int:
    """Uses bitshifts to create a quick comparison value for a datelike.
    """
    return datelike.day + (datelike.month << 5) + (datelike.year << 9)


def _sortkey_most_recently_active(currency: Currency):
    """Use this as a sort key for date-likes. A value of None is used
    for "no date yet", and is therefore most recent. A value of
    "unknown" is interpreted as -1 (ie, before all time).
    """
    datelike = currency.approx_active_until
    if datelike is None:
        return (float('inf'), float('inf'), float('inf'))
    if datelike is Singleton.UNKNOWN:
        return (-1, -1, -1)
    else:
        return (datelike.year, datelike.month, datelike.day)


def heal_float(dec: Decimal) -> Decimal:
    """Given a decimal constructed from a float, **truncates** it to
    the maximum safe precision of a float, as determined by
    ``sys.float_info.dig``.

    Note: if truncation was required, this returns a new decimal object.
    If no trunction was required, it will return the original decimal
    object back.
    """
    max_safe_digits = float_info.dig
    sign, digits, exp = dec.as_tuple()
    digit_count = len(digits)

    if digit_count > max_safe_digits:
        if isinstance(exp, int):
            return Decimal((
                sign,
                digits[:max_safe_digits],
                exp + (digit_count - max_safe_digits)))

        # This is impossible, but it solves type checking problems.
        # Details: exponent can return 'F' (+/- infinity), 'n' (NaN), or
        # 'N' (sNaN) -- or an integer, which is handled above. However:
        # ++  all of these values are safe from floats as-is
        # ++  even if they weren't, the number of digits is zero, so it's
        #     always more than max_safe_digits
        # So even if you actually do have Decimal(float('inf')) -- first of
        # all, congrats on the infinite money hack, but more importantly --
        # we **still** won't reach this code branch.
        else:
            return dec

    else:
        return dec


# just so that we have an alternate name in places where we want to take
# ``heal_float`` as an argument
_heal_float = heal_float
