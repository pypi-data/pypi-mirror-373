import os

import dotenv
import pytest

from shopify_client.client import Client

dotenv.load_dotenv()


@pytest.fixture
def shopify_client() -> Client:
    shop_domain = os.environ["TEST_SHOPIFY_DOMAIN"]
    access_token = os.environ["TEST_SHOPIFY_ACCESS_TOKEN"]
    return Client(
        url=f"https://{shop_domain}/admin/api/2024-01/graphql.json",
        headers={
            "X-Shopify-Access-Token": access_token,
            "Content-Type": "application/json",
        },
    )
