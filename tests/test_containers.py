import os
import pytest
from testcontainers.postgres import PostgresContainer

from src.customers.customer import (
    create_table,
    delete_all_customers,
    create_customer,
    get_all_customers,
    get_customer_by_email,
)


@pytest.fixture(scope="module", autouse=True)
def setup(request):
    if os.getenv("USE_TESTCONTAINERS", 'True') == 'True':
      postgres = PostgresContainer("postgres:17.1-alpine")
      postgres.start()
      request.addfinalizer(lambda: postgres.stop())
      os.environ["DB_CONN"] = postgres.get_connection_url()
      os.environ["DB_HOST"] = postgres.get_container_host_ip()
      os.environ["DB_PORT"] = postgres.get_exposed_port(5432)
      os.environ["DB_USERNAME"] = postgres.username
      os.environ["DB_PASSWORD"] = postgres.password
      os.environ["DB_NAME"] = postgres.dbname
    create_table()


@pytest.fixture(scope="function", autouse=True)
def setup_data():
    delete_all_customers()


def test_get_all_customers():
    create_customer("Siva", "siva@gmail.com")
    create_customer("James", "james@gmail.com")
    customers_list = get_all_customers()
    assert len(customers_list) == 2


def test_get_customer_by_email():
    create_customer("John", "john@gmail.com")
    customer = get_customer_by_email("john@gmail.com")
    assert customer.name == "John"
    assert customer.email == "john@gmail.com"
