# from __future__ import annotations

from pydantic import Field, AnyUrl
from typing import Optional, Union, Any, List

# dynamic registering
from .definitions import register_model, model_dependence

# basic definitions
from .definitions import DefinedTerm, Text, URL


# base imports
from .creativework import CreativeWork


@register_model
class DataCatalog(CreativeWork):
    """A collection of datasets"""

    dataset: Optional[Union["Dataset", str, List["Dataset"], List[str]]] = Field(
        None,
        description="A dataset contained in this catalog Inverse property includedInDataCatalog",
    )
    measurementMethod: Optional[
        Union["MeasurementMethodEnum", str, List["MeasurementMethodEnum"], List[str]]
    ] = Field(
        None,
        description="A subproperty of measurementTechnique that can be used for specifying specific methods in particular via MeasurementMethodEnum",
    )
    measurementTechnique: Optional[
        Union["MeasurementMethodEnum", str, List["MeasurementMethodEnum"], List[str]]
    ] = Field(
        None,
        description="A technique method or technology used in an Observation StatisticalVariable or Dataset or DataDownload DataCatalog corresponding to the method used for measuring the corresponding variable s for datasets described using variableMeasured for Observation a StatisticalVariable Often but not necessarily each variableMeasured will have an explicit representation as or mapping to an property such as those defined in Schema org or other RDF vocabularies and knowledge graphs In that case the subproperty of variableMeasured called measuredProperty is applicable The measurementTechnique property helps when extra clarification is needed about how a measuredProperty was measured This is oriented towards scientific and scholarly dataset publication but may have broader applicability it is not intended as a full representation of measurement but can often serve as a high level summary for dataset discovery For example if variableMeasured is molecule concentration measurementTechnique could be mass spectrometry or nmr spectroscopy or colorimetry or immunofluorescence If the variableMeasured is depression rating the measurementTechnique could be Zung Scale or HAM D or Beck Depression Inventory If there are several variableMeasured properties recorded for some given data object use a PropertyValue for each variableMeasured and attach the corresponding measurementTechnique The value can also be from an enumeration organized as a MeasurementMetholdEnumeration",
    )


# parent dependences
model_dependence("DataCatalog", "CreativeWork")


# attribute dependences
model_dependence(
    "DataCatalog",
    "Dataset",
    "MeasurementMethodEnum",
)
