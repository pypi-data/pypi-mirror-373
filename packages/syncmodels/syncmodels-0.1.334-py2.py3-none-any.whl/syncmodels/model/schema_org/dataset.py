# from __future__ import annotations

from pydantic import Field, AnyUrl
from typing import Optional, Union, Any, List

# dynamic registering
from .definitions import register_model, model_dependence

# basic definitions
from .definitions import Text, DefinedTerm, URL, PropertyValue


# base imports
from .creativework import CreativeWork


@register_model
class Dataset(CreativeWork):
    """A body of structured information describing some topic s of interest"""

    distribution: Optional[
        Union["DataDownload", str, List["DataDownload"], List[str]]
    ] = Field(
        None,
        description="A downloadable form of this dataset at a specific location in a specific format This property can be repeated if different variations are available There is no expectation that different downloadable distributions must contain exactly equivalent information see also DCAT on this point Different distributions might include or exclude different subsets of the entire dataset for example",
    )
    includedInDataCatalog: Optional[
        Union["DataCatalog", str, List["DataCatalog"], List[str]]
    ] = Field(
        None,
        description="A data catalog which contains this dataset Supersedes catalog includedDataCatalog Inverse property dataset",
    )
    issn: Optional[Union[str, List[str]]] = Field(
        None,
        description="The International Standard Serial Number ISSN that identifies this serial publication You can repeat this property to identify different formats of or the linking ISSN ISSN L for this serial publication",
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
    variableMeasured: Optional[
        Union[
            "Property",
            "StatisticalVariable",
            str,
            List["Property"],
            List["StatisticalVariable"],
            List[str],
        ]
    ] = Field(
        None,
        description="The variableMeasured property can indicate repeated as necessary the variables that are measured in some dataset either described as text or as pairs of identifier and description using PropertyValue or more explicitly as a StatisticalVariable",
    )


# parent dependences
model_dependence("Dataset", "CreativeWork")


# attribute dependences
model_dependence(
    "Dataset",
    "DataCatalog",
    "DataDownload",
    "MeasurementMethodEnum",
    "Property",
    "StatisticalVariable",
)
