# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Annotated, TypedDict

from .._utils import PropertyInfo

__all__ = ["ParamSearchExecuteParams"]


class ParamSearchExecuteParams(TypedDict, total=False):
    produce_clt_manifest: Annotated[str, PropertyInfo(alias="produce-clt-manifest")]
    """
    An optional parameter that, when set to "true", will make the endpoint return a
    text representation of a manifest file that corresponds with the datasets
    queried rather than the original response
    """
