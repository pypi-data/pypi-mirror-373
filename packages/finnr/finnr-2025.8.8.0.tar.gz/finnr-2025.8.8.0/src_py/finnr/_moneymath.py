"""THIS MODULE IS 100% AUTOMATICALLY GENERATED VIA THE CODEGEN SIDECAR
(See sidecars_py).

Do not modify it directly.

Some notes:
++  We want to strictly separate the codegen from any custom
    implementation as part of the ``Money`` object, so this module
    contains ONLY money math.
++  The circular injection of ``Money`` is simply the most performant
    way to access the Money object.
++  Note that decimal doesn't implement augmented operations; therefore,
    we have to be careful to reference the non-augmented methods within
    the template
++  There are some things that are marked as overloads that could have
    been converted into a separate template for unions, since they
    aren't actually overloads (eg ``__mod__``), but rather,
    ``other: _Scalar | Money -> Money``. These used to be actual
    overloads, but I changed them when I realized they didn't make any
    sense like that. Might be worth cleaning them up later, but for now,
    it's not hurting anything.
"""
from __future__ import annotations

import typing
from decimal import Context
from decimal import Decimal
from typing import Protocol
from typing import Self
from typing import overload

from finnr.exceptions import MismatchedCurrency
from finnr.exceptions import MoneyRequired
from finnr.exceptions import ScalarRequired

if typing.TYPE_CHECKING:
    from finnr.currency import Currency

    # Note: at runtime, this gets injected by the money module itself, so
    # that the value is available at runtime
    from finnr.money import Money

type _Scalar = Decimal | int


class MoneyMathImpl(Protocol):
    amount: Decimal
    currency: Currency

    def __init__(self, amount: Decimal, currency: Currency): ...

    ###########################################################
    # These are all dynamically codegen'd
    ###########################################################

    def __mul__(self, other: _Scalar) -> Money:
        try:
            return self.currency.mint(self.amount.__mul__(other))
        except TypeError as exc:
            raise ScalarRequired(other) from exc

    def __rmul__(self, other: _Scalar) -> Money:
        try:
            return self.currency.mint(self.amount.__rmul__(other))
        except TypeError as exc:
            raise ScalarRequired(other) from exc

    def __add__(self, other: Money) -> Money:
        try:
            if self.currency != other.currency:
                raise MismatchedCurrency(self.currency, other.currency)

            return self.currency.mint(self.amount.__add__(other.amount))

        except AttributeError as exc:
            raise MoneyRequired(other) from exc

    def __sub__(self, other: Money) -> Money:
        try:
            if self.currency != other.currency:
                raise MismatchedCurrency(self.currency, other.currency)

            return self.currency.mint(self.amount.__sub__(other.amount))

        except AttributeError as exc:
            raise MoneyRequired(other) from exc

    def __imul__(self, other: _Scalar) -> Self:
        try:
            self.amount = self.amount.__mul__(other)
            return self
        except TypeError as exc:
            raise ScalarRequired(other) from exc

    def __iadd__(self, other: Money) -> Self:
        try:
            if self.currency != other.currency:
                raise MismatchedCurrency(self.currency, other.currency)

            self.amount = self.amount.__add__(other.amount)
            return self

        except AttributeError as exc:
            raise MoneyRequired(other) from exc

    def __isub__(self, other: Money) -> Self:
        try:
            if self.currency != other.currency:
                raise MismatchedCurrency(self.currency, other.currency)

            self.amount = self.amount.__sub__(other.amount)
            return self

        except AttributeError as exc:
            raise MoneyRequired(other) from exc

    @overload
    def __truediv__(self, other: Money) -> Decimal: ...
    @overload
    def __truediv__(self, other: _Scalar) -> Money: ...
    def __truediv__(self, other: Money | _Scalar) -> Money | Decimal:
        if isinstance(other, Money):
            if self.currency != other.currency:
                raise MismatchedCurrency(self.currency, other.currency)

            return self.amount.__truediv__(other.amount)

        else:
            return self.currency.mint(self.amount.__truediv__(other))

    @overload
    def __floordiv__(self, other: Money) -> Decimal: ...
    @overload
    def __floordiv__(self, other: _Scalar) -> Money: ...
    def __floordiv__(self, other: Money | _Scalar) -> Money | Decimal:
        if isinstance(other, Money):
            if self.currency != other.currency:
                raise MismatchedCurrency(self.currency, other.currency)

            return self.amount.__floordiv__(other.amount)

        else:
            return self.currency.mint(self.amount.__floordiv__(other))

    @overload
    def __mod__(self, other: Money) -> Money: ...
    @overload
    def __mod__(self, other: _Scalar) -> Money: ...
    def __mod__(self, other: Money | _Scalar) -> Money:
        if isinstance(other, Money):
            if self.currency != other.currency:
                raise MismatchedCurrency(self.currency, other.currency)

            return self.currency.mint(self.amount.__mod__(other.amount))

        else:
            return self.currency.mint(self.amount.__mod__(other))

    def __itruediv__(self, other: _Scalar) -> Self:
        try:
            self.amount = self.amount.__truediv__(other)
            return self
        except TypeError as exc:
            raise ScalarRequired(other) from exc

    def __ifloordiv__(self, other: _Scalar) -> Self:
        try:
            self.amount = self.amount.__floordiv__(other)
            return self
        except TypeError as exc:
            raise ScalarRequired(other) from exc

    def __imod__(self, other: _Scalar) -> Self:
        try:
            self.amount = self.amount.__mod__(other)
            return self
        except TypeError as exc:
            raise ScalarRequired(other) from exc

    def __round__(self) -> Money:
        return self.currency.mint(self.amount.__round__())

    def __trunc__(self) -> Money:
        return self.currency.mint(self.amount.__trunc__())

    def __floor__(self) -> Money:
        return self.currency.mint(self.amount.__floor__())

    def __ceil__(self) -> Money:
        return self.currency.mint(self.amount.__ceil__())

    def __int__(self) -> int:
        return self.amount.__int__()

    def __float__(self) -> float:
        return self.amount.__float__()

    def __neg__(self) -> Money:
        return self.currency.mint(self.amount.__neg__())

    def __pos__(self) -> Money:
        return self.currency.mint(self.amount.__pos__())

    def __abs__(self) -> Money:
        return self.currency.mint(self.amount.__abs__())

    def compare(
            self,
            other: Money,
            context: Context | None = None
            ) -> _Scalar:
        try:
            if self.currency != other.currency:
                raise MismatchedCurrency(self.currency, other.currency)

            return self.amount.compare(
                other.amount, context=context)

        except AttributeError as exc:
            raise MoneyRequired(other) from exc

    def compare_signal(
            self,
            other: Money,
            context: Context | None = None
            ) -> _Scalar:
        try:
            if self.currency != other.currency:
                raise MismatchedCurrency(self.currency, other.currency)

            return self.amount.compare_signal(
                other.amount, context=context)

        except AttributeError as exc:
            raise MoneyRequired(other) from exc

    def compare_total(
            self,
            other: Money,
            context: Context | None = None
            ) -> _Scalar:
        try:
            if self.currency != other.currency:
                raise MismatchedCurrency(self.currency, other.currency)

            return self.amount.compare_total(
                other.amount, context=context)

        except AttributeError as exc:
            raise MoneyRequired(other) from exc

    def compare_total_mag(
            self,
            other: Money,
            context: Context | None = None
            ) -> _Scalar:
        try:
            if self.currency != other.currency:
                raise MismatchedCurrency(self.currency, other.currency)

            return self.amount.compare_total_mag(
                other.amount, context=context)

        except AttributeError as exc:
            raise MoneyRequired(other) from exc

    @overload
    def remainder_near(
            self,
            other: Money,
            context: Context | None = None
            ) -> Money: ...
    @overload
    def remainder_near(
            self,
            other: _Scalar,
            context: Context | None = None
            ) -> Money: ...
    def remainder_near(
            self,
            other: Money | _Scalar,
            context: Context | None = None
            ) -> Money:
        if isinstance(other, Money):
            if self.currency != other.currency:
                raise MismatchedCurrency(self.currency, other.currency)

            return self.currency.mint(
                self.amount.remainder_near(
                other.amount, context=context))

        else:
            return self.currency.mint(
                self.amount.remainder_near(other, context=context))

    def shift(
            self,
            other: _Scalar,
            context: Context | None = None
            ) -> Money:
        try:
            return self.currency.mint(
                self.amount.shift(other, context=context))
        except TypeError as exc:
            raise ScalarRequired(other) from exc

    def scaleb(
            self,
            other: _Scalar,
            context: Context | None = None
            ) -> Money:
        try:
            return self.currency.mint(
                self.amount.scaleb(other, context=context))
        except TypeError as exc:
            raise ScalarRequired(other) from exc

    def rotate(
            self,
            other: _Scalar,
            context: Context | None = None
            ) -> Money:
        try:
            return self.currency.mint(
                self.amount.rotate(other, context=context))
        except TypeError as exc:
            raise ScalarRequired(other) from exc

    def same_quantum(
            self,
            other: Money,
            context: Context | None = None
            ) -> bool:
        try:
            if self.currency != other.currency:
                raise MismatchedCurrency(self.currency, other.currency)

            return self.amount.same_quantum(
                other.amount, context=context)

        except AttributeError as exc:
            raise MoneyRequired(other) from exc

    def next_minus(self, context: Context | None = None) -> Money:
        return self.currency.mint(self.amount.next_minus(context=context))

    def next_plus(self, context: Context | None = None) -> Money:
        return self.currency.mint(self.amount.next_plus(context=context))

    def normalize(self, context: Context | None = None) -> Money:
        return self.currency.mint(self.amount.normalize(context=context))

    def is_finite(self) -> bool:
        return self.amount.is_finite()

    def is_infinite(self) -> bool:
        return self.amount.is_infinite()

    def is_nan(self) -> bool:
        return self.amount.is_nan()

    def is_qnan(self) -> bool:
        return self.amount.is_qnan()

    def is_signed(self) -> bool:
        return self.amount.is_signed()

    def is_snan(self) -> bool:
        return self.amount.is_snan()

    def is_zero(self) -> bool:
        return self.amount.is_zero()

    def next_toward(
            self,
            other: Money,
            context: Context | None = None
            ) -> Money:
        try:
            if self.currency != other.currency:
                raise MismatchedCurrency(self.currency, other.currency)

            return self.currency.mint(
                self.amount.next_toward(other.amount, context=context))

        except AttributeError as exc:
            raise MoneyRequired(other) from exc

    def max(
            self,
            other: Money,
            context: Context | None = None
            ) -> Money:
        try:
            if self.currency != other.currency:
                raise MismatchedCurrency(self.currency, other.currency)

            return self.currency.mint(
                self.amount.max(other.amount, context=context))

        except AttributeError as exc:
            raise MoneyRequired(other) from exc

    def max_mag(
            self,
            other: Money,
            context: Context | None = None
            ) -> Money:
        try:
            if self.currency != other.currency:
                raise MismatchedCurrency(self.currency, other.currency)

            return self.currency.mint(
                self.amount.max_mag(other.amount, context=context))

        except AttributeError as exc:
            raise MoneyRequired(other) from exc

    def min(
            self,
            other: Money,
            context: Context | None = None
            ) -> Money:
        try:
            if self.currency != other.currency:
                raise MismatchedCurrency(self.currency, other.currency)

            return self.currency.mint(
                self.amount.min(other.amount, context=context))

        except AttributeError as exc:
            raise MoneyRequired(other) from exc

    def min_mag(
            self,
            other: Money,
            context: Context | None = None
            ) -> Money:
        try:
            if self.currency != other.currency:
                raise MismatchedCurrency(self.currency, other.currency)

            return self.currency.mint(
                self.amount.min_mag(other.amount, context=context))

        except AttributeError as exc:
            raise MoneyRequired(other) from exc

    def copy_sign(
            self,
            other: Money,
            context: Context | None = None
            ) -> Money:
        try:
            if self.currency != other.currency:
                raise MismatchedCurrency(self.currency, other.currency)

            return self.currency.mint(
                self.amount.copy_sign(other.amount, context=context))

        except AttributeError as exc:
            raise MoneyRequired(other) from exc

    ###########################################################
    # The rest of the math methods are unique and special-cased
    # (but still created within codegen)
    ###########################################################

    @overload
    def __divmod__(self, other: Money) -> tuple[Decimal, Money]: ...
    @overload
    def __divmod__(self, other: Decimal | int) -> tuple[Money, Money]: ...
    def __divmod__(
            self,
            other: Decimal | int | Money
            ) -> tuple[Decimal | Money, Money]:
        if isinstance(other, Money):
            if self.currency != other.currency:
                raise MismatchedCurrency(self.currency, other.currency)

            quotient, remainder = self.amount.__divmod__(other.amount)
            return quotient, Money(amount=remainder, currency=self.currency)

        else:
            quotient, remainder = self.amount.__divmod__(other)
            return (
                Money(amount=quotient, currency=self.currency),
                Money(amount=remainder, currency=self.currency))

    def adjusted(self) -> int:
        return self.amount.adjusted()

    def fma(
            self,
            other: Decimal | int,
            third: Money,
            context=None
            ) -> Money:
        if self.currency != third.currency:
            raise MismatchedCurrency(self.currency, third.currency)

        return Money(
            amount=self.amount.fma(other, third.amount),
            currency=self.currency)

    # Note: special-cased because of the rounding argument
    def quantize(
            self,
            exp: Decimal | int | Money,
            rounding: str | None = None,
            context: Context | None = None,
            ) -> Money:
        if isinstance(exp, Money):
            if self.currency != exp.currency:
                raise MismatchedCurrency(self.currency, exp.currency)

            return Money(
                amount=self.amount.quantize(
                    exp.amount,
                    rounding=rounding,
                    context=context),
                currency=self.currency)

        else:
            return Money(
                amount=self.amount.quantize(
                    exp,
                    rounding=rounding,
                    context=context),
                currency=self.currency)
