from __future__ import annotations

from linkmerce.common.api import run_with_duckdb, update_options

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Iterable, Literal
    from linkmerce.common.extract import JsonObject
    from linkmerce.common.load import DuckDBConnection
    import datetime as dt


def get_module(name: str) -> str:
    return (".smartstore.api" + name) if name.startswith('.') else name


def get_options(request_delay: float | int = 1.01) -> dict:
    return dict(CursorAll = dict(delay=request_delay))


def get_variables(
        client_id: str,
        client_secret: str,
    ) -> dict:
    return dict(client_id=client_id, client_secret=client_secret)


def order(
        client_id: str,
        client_secret: str,
        start_date: dt.date | str,
        end_date: dt.date | str | Literal[":start_date:"] = ":start_date:",
        range_type: Literal["PAYED_DATETIME","ORDERING_CONFIRM","DELIVERY_OPERATED","DELIVERY_COMPLETED","PURCHASE_DECISION_COMPLETED"] = "PAYED_DATETIME",
        product_order_status: Iterable[str] = list(),
        claim_status: Iterable[str] = list(),
        place_order_status: str = list(),
        page_start: int = 1,
        retry_count: int = 5,
        request_delay: float | int = 1.01,
        connection: DuckDBConnection | None = None,
        return_type: Literal["csv","json","parquet","raw","none"] = "json",
        extract_options: dict = dict(),
        transform_options: dict = dict(),
    ) -> JsonObject:
    """`tables = {'default': 'data'}`"""
    # from linkmerce.core.smartstore.api.order.extract import Order
    # from linkmerce.core.smartstore.api.order.transform import Order
    components = (get_module(".order"), "Order", "Order")
    args = (start_date, end_date, range_type, product_order_status, claim_status, place_order_status, page_start, retry_count)
    extract_options = update_options(extract_options,
        options = get_options(request_delay),
        variables = get_variables(client_id, client_secret))
    options = dict(extract_options=extract_options, transform_options=transform_options)
    return run_with_duckdb(*components, connection, "sync", return_type, args, **options)


def product_order(
        client_id: str,
        client_secret: str,
        start_date: dt.date | str,
        end_date: dt.date | str | Literal[":start_date:"] = ":start_date:",
        range_type: Literal["PAYED_DATETIME","ORDERING_CONFIRM","DELIVERY_OPERATED","DELIVERY_COMPLETED","PURCHASE_DECISION_COMPLETED"] = "PAYED_DATETIME",
        product_order_status: Iterable[str] = list(),
        claim_status: Iterable[str] = list(),
        place_order_status: str = list(),
        page_start: int = 1,
        retry_count: int = 5,
        request_delay: float | int = 1.01,
        connection: DuckDBConnection | None = None,
        return_type: Literal["csv","json","parquet","raw","none"] = "json",
        extract_options: dict = dict(),
        transform_options: dict = dict(),
    ) -> dict[str,JsonObject]:
    """`tables = {'order': 'smartstore_order', 'option': 'smartstore_option'}`"""
    # from linkmerce.core.smartstore.api.order.extract import ProductOrder
    # from linkmerce.core.smartstore.api.order.transform import ProductOrder
    components = (get_module(".order"), "ProductOrder", "ProductOrder")
    args = (start_date, end_date, range_type, product_order_status, claim_status, place_order_status, page_start, retry_count)
    extract_options = update_options(extract_options,
        options = get_options(request_delay),
        variables = get_variables(client_id, client_secret))
    options = dict(extract_options=extract_options, transform_options=transform_options)
    return run_with_duckdb(*components, connection, "sync", return_type, args, **options)


def order_status(
        client_id: str,
        client_secret: str,
        start_date: dt.date | str,
        end_date: dt.date | str | Literal[":start_date:"] = ":start_date:",
        last_changed_type: str | None = None,
        retry_count: int = 5,
        request_delay: float | int = 1.01,
        connection: DuckDBConnection | None = None,
        return_type: Literal["csv","json","parquet","raw","none"] = "json",
        extract_options: dict = dict(),
        transform_options: dict = dict(),
    ) -> JsonObject:
    """`tables = {'default': 'data'}`"""
    # from linkmerce.core.smartstore.api.order.extract import OrderStatus
    # from linkmerce.core.smartstore.api.order.transform import OrderStatus
    components = (get_module(".order"), "OrderStatus", "OrderStatus")
    args = (start_date, end_date, last_changed_type, retry_count)
    extract_options = update_options(extract_options,
        options = get_options(request_delay),
        variables = get_variables(client_id, client_secret))
    options = dict(extract_options=extract_options, transform_options=transform_options)
    return run_with_duckdb(*components, connection, "sync", return_type, args, **options)
