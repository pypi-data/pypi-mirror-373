"""Contains constructors for test data: ip_location(), etc."""

from typing import TYPE_CHECKING

from faker import Faker

from .core import config

if TYPE_CHECKING:
    from .iowrapper import ConfigIOWrapper


__all__ = ["ip_locations", "customer_data", "order_records"]


def ip_locations(
    number_of_addresses: int = 10, seed: int | None = None
) -> "ConfigIOWrapper":
    """
    Returns a fake mapping of IP addresses to the real-world geographic
    locations of the Internet-connected devices.

    Parameters
    ----------
    number_of_addresses : int, optional
        Number of ip addresses, by default 10.
    seed : int | None, optional
        Seed value, by default None.

    Returns
    -------
    ConfigIOWrapper
        Config object.

    """
    faker = Faker()
    faker.seed_instance(seed)
    mapping = {}
    for _ in range(number_of_addresses):
        mapping[faker.ipv4()] = [faker.city()] + faker.address().splitlines()
    return config(mapping)


def customer_data(
    number_of_customers: int = 3, seed: int | None = None
) -> "ConfigIOWrapper":
    """
    Returns a fake mapping of customers' names to their data, including
    their names, emails, phone, numbers, addresses, and order records.

    Parameters
    ----------
    number_of_customers : int, optional
        Number of customers, by default 3.
    seed : int | None, optional
        Seed value, by default None.

    Returns
    -------
    ConfigIOWrapper
        Config object.

    """
    faker = Faker()
    faker.seed_instance(seed)
    data = {}
    for _ in range(number_of_customers):
        name = faker.name()
        data[name] = {
            "name": name,
            "email": faker.email(),
            "phone_number": faker.phone_number(),
            "address": [faker.city()] + faker.address().splitlines(),
            "order_records": [
                {
                    "order_id": faker.uuid4(),
                    "product_id": faker.md5(),
                    "quantity": faker.pyint(1, 1000),
                    "unit_price": faker.pyfloat(3, 2, True),
                    "date": str(faker.date_this_year()),
                    "completed": faker.pybool(),
                }
                for __ in range(faker.pyint(min_value=1, max_value=10))
            ],
        }
    return config(data)


def order_records(
    number_of_orders: int = 3, seed: int | None = None
) -> "ConfigIOWrapper":
    """
    Returns a fake list of order records, including order-ids,
    product-ids, quantities, unit prices, trading dates,
    completed-or-not boolean numbers, and the customer info mappings.

    Parameters
    ----------
    number_of_orders : int, optional
        Number of orders, by default 3.
    seed : int | None, optional
        Seed value, by default None.

    Returns
    -------
    ConfigIOWrapper
        Config object.

    """
    faker = Faker()
    faker.seed_instance(seed)
    data = []
    for _ in range(number_of_orders):
        name = faker.name()
        data.append(
            {
                "order_id": faker.uuid4(),
                "product_id": faker.md5(),
                "quantity": faker.pyint(1, 1000),
                "unit_price": faker.pyfloat(3, 2, True),
                "date": str(faker.date_this_year()),
                "completed": faker.pybool(),
                "customer_info": {
                    "name": name,
                    "email": faker.email(),
                    "phone_number": faker.phone_number(),
                    "address": [faker.city()] + faker.address().splitlines(),
                },
            }
        )
    return config(data)
