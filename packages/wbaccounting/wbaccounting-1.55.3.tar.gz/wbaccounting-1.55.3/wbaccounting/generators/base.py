import abc
from contextlib import suppress
from datetime import date
from importlib import import_module
from typing import Callable, Iterable

from django.conf import settings
from django.db.models import QuerySet
from wbcore.contrib.currency.models import Currency
from wbcore.contrib.directory.models import Entry

from wbaccounting.models.booking_entry import BookingEntry

GENERATE_BOOKING_ENTRIES = Callable[[date, date, Entry], list[BookingEntry]]


def register_generator(name: str) -> Callable:
    def decorator(func: Callable) -> Callable:
        setattr(func, "_is_booking_entry_generator", True)
        setattr(func, "_booking_entry_generator_name", name)
        return func

    return decorator


def get_all_booking_entry_choices() -> Iterable[tuple[str, str]]:
    for app in settings.INSTALLED_APPS:
        with suppress(ModuleNotFoundError):
            import_module(f"{app}.generators")

    for subclass in AbstractBookingEntryGenerator.__subclasses__():
        yield f"{subclass.__module__}.{subclass.__name__}", subclass.TITLE


class AbstractBookingEntryGenerator(abc.ABC):
    """
    An abstract base class designed to define a template for generating and managing
    booking entries within a financial or accounting system.

    This class outlines the necessary operations for generating a series of booking
    entries based on a given date range and counterparty, as well as merging backlinks
    for the generated booking entries.

    Attributes:
        TITLE (str): A class-level attribute that provides a title or a descriptive name for the
                     generator implementation. This should be overridden in concrete subclasses
                     to provide a specific title.
    """

    TITLE = ""

    @staticmethod
    @abc.abstractmethod
    def generate_booking_entries(from_date: date, to_date: date, counterparty: Entry) -> Iterable[BookingEntry]:
        """
        Generates a sequence of booking entries for a specified date range and counterparty.

        This abstract method must be implemented by subclasses to provide the logic for
        generating booking entries based on the provided criteria.

        Args:
            from_date (date): The start date of the period for which booking entries are to be generated.
            to_date (date): The end date of the period for which booking entries are to be generated.
            counterparty (Entry): The counterparty associated with the booking entries to be generated.

        Returns:
            Iterable[BookingEntry]: A sequence of BookingEntry instances generated for the specified
                                    criteria.

        Raises:
            NotImplementedError: If the method is not implemented in a subclass.
        """
        raise NotImplementedError()

    @staticmethod
    @abc.abstractmethod
    def merge_backlinks(booking_entries: QuerySet[BookingEntry]) -> dict:
        """
        Merges backlinks for a collection of booking entries, to consolidate
        related entries to insert a single backling in an invoice.

        This abstract method should be implemented by subclasses to provide specific
        logic for merging or updating backlinks of booking entries.

        Args:
            booking_entries (Iterable[BookingEntry]): A sequence of BookingEntry instances
                                                     to be merged or updated.

        Returns:
            dict: A dictionary or other structured data indicating the results of the
                  merge operation, specific to the implementation.

        Raises:
            NotImplementedError: If the method is not implemented in a subclass.
        """
        raise NotImplementedError()


def generate_booking_entries(
    _class: type[AbstractBookingEntryGenerator], from_date: date, to_date: date, counterparty: Entry
):
    booking_entries = _class.generate_booking_entries(from_date, to_date, counterparty)
    for booking_entry in booking_entries:
        booking_entry.save()


class TestGenerator(AbstractBookingEntryGenerator):
    TITLE = "Test Generator"

    @staticmethod
    def generate_booking_entries(from_date: date, to_date: date, counterparty: Entry) -> Iterable[BookingEntry]:
        yield BookingEntry(
            title="Test Booking Entry",
            counterparty=counterparty,
            booking_date=date.today(),
            reference_date=date.today(),
            net_value=100,
            currency=Currency.objects.first(),
        )

    @staticmethod
    def merge_backlinks(booking_entries: Iterable[BookingEntry]) -> dict:
        return {}
