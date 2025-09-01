from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional, Dict, Any
from myreze.store.product import Product
from myreze.store.provider import ProductProvider
from myreze.data import MyrezeDataPackage, Geometry, Time
import uuid


class OrderRequest(BaseModel):
    product_id: str
    spatial_region: Dict[str, Any]
    temporal_region: Dict[str, Any]
    visualization: Optional[Dict[str, Any]] = None


class StoreServer:
    """A FastAPI-based store server for MyrezeDataPackages."""

    def __init__(self, provider: ProductProvider):
        self.app = FastAPI(title="Myreze Store")
        self.provider = provider
        self._register_endpoints()

    def _register_endpoints(self):
        @self.app.get("/products")
        async def list_products():
            """List available products."""
            products = await self.provider.get_products()
            return [p.to_dict() for p in products]

        @self.app.post("/orders")
        async def create_order(request: OrderRequest):
            """Create an order for a MyrezeDataPackage."""
            products = await self.provider.get_products()
            product = next(
                (p for p in products if p.product_id == request.product_id), None
            )
            if not product:
                raise HTTPException(status_code=404, detail="Product not found")

            # Validate spatio-temporal region
            if not is_region_valid(request.spatial_region, product.spatial_coverage):
                raise HTTPException(status_code=400, detail="Invalid spatial region")
            if not is_time_valid(request.temporal_region, product.temporal_coverage):
                raise HTTPException(status_code=400, detail="Invalid temporal region")

            # Generate package
            package = await product.generate_package(
                request.spatial_region, request.temporal_region, request.visualization
            )
            return package.to_dict()

    def run(self, host: str = "0.0.0.0", port: int = 8000):
        """Run the FastAPI server."""
        import uvicorn

        uvicorn.run(self.app, host=host, port=port)


def is_region_valid(request_region: Dict[str, Any], coverage: Dict[str, Any]) -> bool:
    """Validate spatial region (placeholder)."""
    # Use myreze.data.Geometry for validation
    return True


def is_time_valid(request_time: Dict[str, Any], coverage: Dict[str, Any]) -> bool:
    """Validate temporal region (placeholder)."""
    # Use myreze.data.Time for validation
    return True
