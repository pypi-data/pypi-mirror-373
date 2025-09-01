from datetime import datetime
from enum import Enum
from typing import Any, Dict, Iterator, List, Optional
from uuid import UUID

from pydantic import AnyUrl, BaseModel, ConfigDict, Field, TypeAdapter

# --- Enums ---------------------------------------------------------------


class ProductType(str, Enum):
    PRODUCT = "Product"
    SERVICE = "Service"


class TaxClassification(str, Enum):
    TAXED = "Taxed"
    EXCLUDED = "Excluded"


class TaxType(str, Enum):
    IVA = "IVA"
    RETEFUENTE = "Retefuente"
    AD_VALOREM = "AdValorem"
    IMPOCONSUMO = "Impoconsumo"


# --- Small value objects -------------------------------------------------


class Pagination(BaseModel):
    page: int
    page_size: int
    total_results: int


class AccountGroup(BaseModel):
    id: int
    name: str


class Tax(BaseModel):
    id: int
    name: str
    type: TaxType
    percentage: float


class PriceListItem(BaseModel):
    position: int
    name: str
    value: float


class CurrencyPrice(BaseModel):
    currency_code: str
    price_list: List[PriceListItem]


class Unit(BaseModel):
    code: str
    name: str


class Warehouse(BaseModel):
    id: int
    name: str
    quantity: float


class Metadata(BaseModel):
    created: datetime
    last_updated: Optional[datetime] = None


class LinkRef(BaseModel):
    href: AnyUrl


class Links(BaseModel):
    self: LinkRef
    next: Optional[LinkRef] = None


# Accept known fields (barcode, brand, tariff, model) and ignore/allow others
class AdditionalFields(BaseModel):
    model_config = ConfigDict(extra="ignore")  # tolerate unknown keys
    barcode: Optional[str] = None
    brand: Optional[str] = None
    tariff: Optional[str] = None
    model: Optional[str] = None


# --- Main product item ---------------------------------------------------


class Product(BaseModel):
    model_config = ConfigDict(extra="ignore")  # ignore unexpected fields

    id: UUID
    code: str
    name: str

    account_group: AccountGroup
    type: ProductType
    stock_control: bool
    active: bool

    tax_classification: TaxClassification
    tax_included: bool
    tax_consumption_value: Optional[float] = None
    taxes: Optional[List[Tax]] = None

    prices: Optional[List[CurrencyPrice]] = None

    unit: Unit
    unit_label: Optional[str] = None
    reference: Optional[str] = None
    description: Optional[str] = None

    additional_fields: Optional[AdditionalFields] = None

    available_quantity: float
    warehouses: List[Warehouse]

    metadata: Metadata


# --- Top-level API response ---------------------------------------------


class ProductsResponse(BaseModel):
    model_config = ConfigDict(
        extra="ignore",
        populate_by_name=True,  # allow using field names instead of aliases
    )

    pagination: Pagination
    results: List[Product]
    links: Links = Field(alias="_links")


class ProductsResource:
    def __init__(self, *, _request, base_url: str):
        self._request = _request
        self._base = f"{base_url}/v1/products"

    def list(self, *, created_start: Optional[str] = None) -> Iterator[Product]:
        params: Dict[str, Any] = {}

        if created_start:
            params["created_start"] = created_start

        r = self._request("GET", self._base, params=params)
        data = r.json()
        items = data.get("results") or data.get("data") or []
        products = TypeAdapter(list[Product]).validate_python(items)

        yield from products
