# NocoDB Updater Library

A Python library for synchronizing data with NocoDB.

## Features

- Synchronize data from external sources to NocoDB tables
- Support for custom data mapping
- Automatic handling of record creation and updates
- Link records between tables based on relationships in external data
- Support for both v1 and v2 NocoDB API versions

## Installation

```bash
pip install shops-nocodb-updater
```

For development:

```bash
pip install -e .
```

## Usage

### Basic Usage

```python
import asyncio
from shops_nocodb_updater import NocodbClient, synchronize_records

async def main():
    # Initialize the client
    client = NocodbClient(
        nocodb_host="https://your-nocodb-instance.com",
        api_key="your-api-key",
        project_id="your-project-id",
        api_version="v1"  # or "v2" for newer NocoDB instances
    )
    
    # Sync data to a table
    data = [
        {"id": "1", "name": "Item 1", "price": 10.99},
        {"id": "2", "name": "Item 2", "price": 20.99}
    ]
    
    # Sync the data
    id_map = await synchronize_records(
        client, 
        "your-table-id", 
        data, 
        external_id_field="external_id"
    )
    
    print(f"Synchronized {len(id_map)} records")

if __name__ == "__main__":
    asyncio.run(main())
```

### Using Models

```python
import asyncio
from pydantic import BaseModel
from typing import Optional
from shops_nocodb_updater import NocodbClient

# Define your models
class Product(BaseModel):
    __tableid__ = "your-product-table-id"
    __external_id_field__ = "external_id"
    
    id: str
    name: str
    price: float
    description: Optional[str] = None
    
    @staticmethod
    def __mapper__(data: dict) -> dict:
        """Map product data to NocoDB format"""
        return {
            "name": data.get("name", ""),
            "price": data.get("price", 0),
            "description": data.get("description", "")
        }

async def main():
    # Initialize the client
    client = NocodbClient(
        nocodb_host="https://your-nocodb-instance.com",
        api_key="your-api-key",
        project_id="your-project-id"
    )
    
    # Your data
    products_data = [
        {"id": "1", "name": "Product 1", "price": 10.99},
        {"id": "2", "name": "Product 2", "price": 20.99}
    ]
    
    # Sync products
    product_id_map = await client.sync_records(Product, products_data)
    
    print(f"Synchronized {len(product_id_map)} products")

if __name__ == "__main__":
    asyncio.run(main())
```

### Linking Records

```python
import asyncio
from pydantic import BaseModel
from typing import Optional
from shops_nocodb_updater import NocodbClient

# Define your models
class Category(BaseModel):
    __tableid__ = "your-category-table-id"
    __external_id_field__ = "external_id"
    
    id: str
    name: str

class Product(BaseModel):
    __tableid__ = "your-product-table-id"
    __external_id_field__ = "external_id"
    
    id: str
    name: str
    category_id: str

async def main():
    # Initialize the client
    client = NocodbClient(
        nocodb_host="https://your-nocodb-instance.com",
        api_key="your-api-key",
        project_id="your-project-id"
    )
    
    # Your data
    categories_data = [
        {"id": "cat1", "name": "Category 1"},
        {"id": "cat2", "name": "Category 2"}
    ]
    
    products_data = [
        {"id": "prod1", "name": "Product 1", "category_id": "cat1"},
        {"id": "prod2", "name": "Product 2", "category_id": "cat2"}
    ]
    
    # Sync categories and products
    category_id_map = await client.sync_records(Category, categories_data)
    product_id_map = await client.sync_records(Product, products_data)
    
    # Link products to categories
    await client.link_synced_records(
        model=Product,
        link_column="Category",  # The column name in NocoDB that links to categories
        target_model=Category,
        external_data=products_data,
        source_id_map=product_id_map,
        target_id_map=category_id_map,
        link_field="category_id"  # The field in products_data that contains the category ID
    )
    
    print("Sync and linking completed")

if __name__ == "__main__":
    asyncio.run(main())
```

## API Version Support

This library supports both v1 and v2 of the NocoDB API:

- **v1 API**: Used in older NocoDB instances (default)
- **v2 API**: Used in newer NocoDB instances

You can specify the API version when initializing the client:

```python
client = NocodbClient(
    nocodb_host="https://your-nocodb-instance.com",
    api_key="your-api-key",
    project_id="your-project-id",
    api_version="v2"  # Use "v1" for older instances
)
```

## Examples

See the `examples` directory for more detailed examples:

- `examples/all_in_one_sync.py`: Complete example of syncing categories and products and linking them together
- `examples/real_sync/data/`: Contains sample JSON data for testing

## License

MIT 