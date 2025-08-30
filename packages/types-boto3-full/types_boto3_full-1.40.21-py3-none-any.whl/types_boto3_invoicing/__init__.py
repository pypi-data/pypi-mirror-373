"""
Main interface for invoicing service.

[Documentation](https://youtype.github.io/types_boto3_docs/types_boto3_invoicing/)

Copyright 2025 Vlad Emelianov

Usage::

    ```python
    from boto3.session import Session
    from types_boto3_invoicing import (
        Client,
        InvoicingClient,
        ListInvoiceSummariesPaginator,
        ListInvoiceUnitsPaginator,
    )

    session = Session()
    client: InvoicingClient = session.client("invoicing")

    list_invoice_summaries_paginator: ListInvoiceSummariesPaginator = client.get_paginator("list_invoice_summaries")
    list_invoice_units_paginator: ListInvoiceUnitsPaginator = client.get_paginator("list_invoice_units")
    ```
"""

from .client import InvoicingClient
from .paginator import ListInvoiceSummariesPaginator, ListInvoiceUnitsPaginator

Client = InvoicingClient


__all__ = (
    "Client",
    "InvoicingClient",
    "ListInvoiceSummariesPaginator",
    "ListInvoiceUnitsPaginator",
)
