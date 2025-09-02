# from __future__ import annotations

from pydantic import Field, AnyUrl
from typing import Optional, Union, Any, List

# dynamic registering
from .definitions import register_model, model_dependence


# base imports
from .product import Product


@register_model
class ProductModel(Product):
    """A datasheet or vendor specification of a product in the sense of a prototypical description"""

    isVariantOf: Optional[
        Union[
            "ProductGroup",
            "ProductModel",
            str,
            List["ProductGroup"],
            List["ProductModel"],
            List[str],
        ]
    ] = Field(
        None,
        description="Indicates the kind of product that this is a variant of In the case of ProductModel this is a pointer from a ProductModel to a base product from which this product is a variant It is safe to infer that the variant inherits all product features from the base model unless defined locally This is not transitive In the case of a ProductGroup the group description also serves as a template representing a set of Products that vary on explicitly defined specific dimensions only so it defines both a set of variants as well as which values distinguish amongst those variants When used with ProductGroup this property can apply to any Product included in the group Inverse property hasVariant",
    )
    predecessorOf: Optional[
        Union["ProductModel", str, List["ProductModel"], List[str]]
    ] = Field(
        None,
        description="A pointer from a previous often discontinued variant of the product to its newer variant",
    )
    successorOf: Optional[
        Union["ProductModel", str, List["ProductModel"], List[str]]
    ] = Field(
        None,
        description="A pointer from a newer variant of a product to its previous often discontinued predecessor",
    )


# parent dependences
model_dependence("ProductModel", "Product")


# attribute dependences
model_dependence(
    "ProductModel",
    "ProductGroup",
)
