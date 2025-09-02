import pytest

from shopify_client.client import Client, ListCollections, ListProducts
from shopify_client.input_types import (
    CollectionDeleteInput,
    CollectionInput,
    ProductCreateInput,
    ProductDeleteInput,
    ProductUpdateInput,
)

pytestmark = [pytest.mark.asyncio, pytest.mark.integration]


async def test_list_products(shopify_client: Client):
    res = await shopify_client.list_products()
    assert isinstance(res, ListProducts)


async def test_list_collections(shopify_client: Client):
    res = await shopify_client.list_collections()
    assert isinstance(res, ListCollections)


async def test_crud_product(shopify_client: Client):
    res = await shopify_client.create_product(
        product=ProductCreateInput(title="Test Product"), media=[]
    )
    assert res.productCreate
    assert res.productCreate.product
    id = res.productCreate.product.id

    res = await shopify_client.get_product(id=id)
    assert res.product
    assert res.product.id == id
    assert res.product.title == "Test Product"

    res = await shopify_client.update_product(
        product=ProductUpdateInput(id=id, title="New Title")
    )
    assert res.productUpdate

    res = await shopify_client.get_product(id=id)
    assert res.product
    assert res.product.id == id
    assert res.product.title == "New Title"

    res = await shopify_client.delete_product(input=ProductDeleteInput(id=id))
    assert res.productDelete
    assert res.productDelete.deletedProductId == id

    res = await shopify_client.get_product(id=id)
    assert res.product is None


async def test_crud_collection(shopify_client: Client):
    res = await shopify_client.create_collection(
        input=CollectionInput(title="Test Collection", handle="test-collection")
    )
    assert res.collectionCreate
    assert res.collectionCreate.collection
    assert res.collectionCreate.collection.id
    id = res.collectionCreate.collection.id

    res = await shopify_client.get_collection(id=id)
    assert res.collection
    assert res.collection.id == id
    assert res.collection.title == "Test Collection"
    assert res.collection.handle == "test-collection"

    res = await shopify_client.update_collection(
        input=CollectionInput(id=id, title="New Title", handle="new-title")
    )
    assert res.collectionUpdate
    assert res.collectionUpdate.collection
    assert res.collectionUpdate.collection.id == id
    assert res.collectionUpdate.collection.title == "New Title"

    res = await shopify_client.get_collection(id=id)
    assert res.collection
    assert res.collection.id == id
    assert res.collection.title == "New Title"
    assert res.collection.handle == "new-title"
    assert res.collection.products.edges == []

    res = await shopify_client.create_product(
        product=ProductCreateInput(title="Test Product"), media=[]
    )
    assert res.productCreate
    assert res.productCreate.product
    product_id = res.productCreate.product.id

    res = await shopify_client.add_product_to_collection(id=id, productIds=[product_id])
    assert res

    res = await shopify_client.get_collection(id=id)
    assert res.collection
    edges = res.collection.products.edges
    assert len(edges) == 1
    assert edges[0].node.id == product_id
    assert edges[0].node.title == "Test Product"

    res = await shopify_client.remove_product_from_collection(
        id=id, productIds=[product_id]
    )
    assert res

    res = await shopify_client.delete_product(input=ProductDeleteInput(id=product_id))
    assert res

    res = await shopify_client.delete_collection(input=CollectionDeleteInput(id=id))
    assert res

    res = await shopify_client.get_collection(id=id)
    assert res.collection is None
