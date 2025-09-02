import os

PG_TEST_HOST = os.getenv('PG_TEST_HOST', os.getenv('POSTGRES_HOST', 'localhost'))
PG_TEST_PORT = os.getenv('PG_TEST_PORT', os.getenv('POSTGRES_PORT', '5432'))
PG_TEST_USER = os.getenv('PG_TEST_USER', os.getenv('POSTGRES_USER', 'postgres'))
PG_TEST_PASSWORD = os.getenv('PG_TEST_PASSWORD', os.getenv('POSTGRES_PASSWORD', 'example'))
