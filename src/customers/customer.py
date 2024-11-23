import os
from functools import wraps

import psycopg


def get_connection():
    host = os.getenv("DB_HOST", "localhost")
    port = os.getenv("DB_PORT", "5432")
    username = os.getenv("DB_USERNAME", "test")
    password = os.getenv("DB_PASSWORD", "test")
    database = os.getenv("DB_NAME", "postgres")
    return psycopg.connect(
        f"host={host} dbname={database} user={username} password={password} port={port}"
    )


class Customer:
    def __init__(self, cust_id, name, email):
        self.id = cust_id
        self.name = name
        self.email = email

    def __str__(self):
        return f"Customer({self.id}, {self.name}, {self.email})"


def with_cursor(f):
    @wraps(with_cursor)
    def wrapper(*args, **kwargs):
        with get_connection() as conn:
            with conn.cursor() as cur:
                return f(*args, **kwargs, cur=cur)

    return wrapper


@with_cursor
def create_table(cur):
    cur.execute("""
         CREATE TABLE customers (
             id serial PRIMARY KEY,
             name varchar not null,
             email varchar not null unique)
         """)


@with_cursor
def create_customer(name, email, *, cur):
    cur.execute("INSERT INTO customers (name, email) VALUES (%s, %s)", (name, email))


@with_cursor
def get_all_customers(cur) -> list[Customer]:
    cur.execute("SELECT * FROM customers")
    return [Customer(cid, name, email) for cid, name, email in cur]


@with_cursor
def get_customer_by_email(email, *, cur) -> Customer:
    cur.execute("SELECT id, name, email FROM customers WHERE email = %s", (email,))
    (cid, name, email) = cur.fetchone()
    return Customer(cid, name, email)


@with_cursor
def delete_all_customers(cur):
    cur.execute("DELETE FROM customers")
