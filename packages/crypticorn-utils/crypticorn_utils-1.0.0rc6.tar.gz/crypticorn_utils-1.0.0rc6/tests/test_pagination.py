import pytest
from crypticorn_utils.pagination import (
    FilterParams,
    HeavyPageSortFilterParams,
    HeavyPaginationParams,
    PageFilterParams,
    PageSortFilterParams,
    PageSortParams,
    PaginationParams,
    SortFilterParams,
    SortParams,
)
from pydantic import BaseModel, ValidationError


class Item(BaseModel):
    name: str
    value: int


@pytest.mark.asyncio
async def test_pagination_params():
    # Test default values
    params = PaginationParams[Item]()
    assert params.page == 1
    assert params.page_size == 10

    # Test custom values
    params = PaginationParams[Item](page=2, page_size=20)
    assert params.page == 2
    assert params.page_size == 20

    # Test page_size validation (should be between 1 and 100)
    with pytest.raises(ValidationError):
        PaginationParams[Item](page_size=0)

    with pytest.raises(ValidationError):
        PaginationParams[Item](page_size=101)


@pytest.mark.asyncio
async def test_heavy_pagination_params():
    # Test default values
    params = HeavyPaginationParams[Item]()
    assert params.page == 1
    assert params.page_size == 100

    # Test custom values
    params = HeavyPaginationParams[Item](page=2, page_size=200)
    assert params.page == 2
    assert params.page_size == 200

    # Test page_size validation (should be between 1 and 1000)
    with pytest.raises(ValidationError):
        HeavyPaginationParams[Item](page_size=0)

    with pytest.raises(ValidationError):
        HeavyPaginationParams[Item](page_size=1001)


@pytest.mark.asyncio
async def test_sort_params():
    # Test that SortParams requires BaseModel generic
    with pytest.raises(
        TypeError,
        match="SortParams must be used with a Pydantic BaseModel as a generic parameter",
    ):
        SortParams[int]()

    # Test invalid sort field
    with pytest.raises(
        ValueError,
        match="Invalid field: 'foo'. Must be one of: \\['name', 'value'\\]",
    ):
        SortParams[Item](sort_by="foo", sort_order="asc")

    # Test that sort_by and sort_order must be provided together
    with pytest.raises(
        ValueError, match="sort_order and sort_by must be provided together"
    ):
        SortParams[Item](sort_by="name")

    with pytest.raises(
        ValueError, match="sort_order and sort_by must be provided together"
    ):
        SortParams[Item](sort_order="asc")

    # Test valid combination
    params = SortParams[Item](sort_by="name", sort_order="asc")
    assert params.sort_by == "name"
    assert params.sort_order == "asc"

    # Test default values
    params = SortParams[Item]()
    assert params.sort_by is None
    assert params.sort_order is None


@pytest.mark.asyncio
async def test_sort_order_validation():
    # Test invalid order values - this should be caught by Pydantic's Literal validation
    with pytest.raises(ValidationError):
        SortParams[Item](sort_by="name", sort_order="invalid")

    # Test valid order values
    params = SortParams[Item](sort_by="name", sort_order="asc")
    assert params.sort_order == "asc"

    params = SortParams[Item](sort_by="name", sort_order="desc")
    assert params.sort_order == "desc"


@pytest.mark.asyncio
async def test_filter_params():
    # Test that FilterParams requires BaseModel generic
    with pytest.raises(
        TypeError,
        match="FilterParams must be used with a Pydantic BaseModel as a generic parameter",
    ):
        FilterParams[int](filter_by="name", filter_value="test")

    # Test that filter_value must be provided when filter_by is set
    with pytest.raises(
        ValueError, match="filter_by and filter_value must be provided together"
    ):
        FilterParams[Item](filter_by="name")

    # Test invalid filter field
    with pytest.raises(
        ValueError,
        match="Invalid field: 'foo'. Must be one of: \\['name', 'value'\\]",
    ):
        FilterParams[Item](filter_by="foo", filter_value="test")

    # Test valid filter
    params = FilterParams[Item](filter_by="name", filter_value="test")
    assert params.filter_by == "name"
    assert params.filter_value == "test"

    # Test default values
    params = FilterParams[Item]()
    assert params.filter_by is None
    assert params.filter_value is None


@pytest.mark.asyncio
async def test_sort_filter_params():
    # Test combined functionality
    params = SortFilterParams[Item](
        sort_by="value",
        sort_order="desc",
        filter_by="name",
        filter_value="test",
    )
    assert params.sort_by == "value"
    assert params.sort_order == "desc"
    assert params.filter_by == "name"
    assert params.filter_value == "test"

    # Test default values
    params = SortFilterParams[Item]()
    assert params.sort_by is None
    assert params.sort_order is None
    assert params.filter_by is None
    assert params.filter_value is None

    # Test sort validation still works
    with pytest.raises(
        ValueError, match="sort_order and sort_by must be provided together"
    ):
        SortFilterParams[Item](sort_by="name")

    # Test filter validation still works
    with pytest.raises(
        ValueError, match="filter_by and filter_value must be provided together"
    ):
        SortFilterParams[Item](filter_by="name")


@pytest.mark.asyncio
async def test_page_filter_params():
    # Test combined functionality
    params = PageFilterParams[Item](
        page=2,
        page_size=20,
        filter_by="name",
        filter_value="test",
    )
    assert params.page == 2
    assert params.page_size == 20
    assert params.filter_by == "name"
    assert params.filter_value == "test"

    # Test default values
    params = PageFilterParams[Item]()
    assert params.page == 1
    assert params.page_size == 10
    assert params.filter_by is None
    assert params.filter_value is None

    # Test filter validation still works
    with pytest.raises(
        ValueError, match="filter_by and filter_value must be provided together"
    ):
        PageFilterParams[Item](filter_by="name")


@pytest.mark.asyncio
async def test_page_sort_params():
    # Test combined functionality
    params = PageSortParams[Item](
        page=2,
        page_size=20,
        sort_by="value",
        sort_order="desc",
    )
    assert params.page == 2
    assert params.page_size == 20
    assert params.sort_by == "value"
    assert params.sort_order == "desc"

    # Test default values
    params = PageSortParams[Item]()
    assert params.page == 1
    assert params.page_size == 10
    assert params.sort_by is None
    assert params.sort_order is None

    # Test sort validation still works
    with pytest.raises(
        ValueError, match="sort_order and sort_by must be provided together"
    ):
        PageSortParams[Item](sort_by="name")


@pytest.mark.asyncio
async def test_page_sort_filter_params():
    # Test combined functionality
    params = PageSortFilterParams[Item](
        page=2,
        page_size=20,
        sort_by="value",
        sort_order="desc",
        filter_by="name",
        filter_value="test",
    )
    assert params.page == 2
    assert params.page_size == 20
    assert params.sort_by == "value"
    assert params.sort_order == "desc"
    assert params.filter_by == "name"
    assert params.filter_value == "test"

    # Test default values
    params = PageSortFilterParams[Item]()
    assert params.page == 1
    assert params.page_size == 10
    assert params.sort_by is None
    assert params.sort_order is None
    assert params.filter_by is None
    assert params.filter_value is None

    # Test sort validation still works
    with pytest.raises(
        ValueError, match="sort_order and sort_by must be provided together"
    ):
        PageSortFilterParams[Item](sort_by="name")

    # Test filter validation still works
    with pytest.raises(
        ValueError, match="filter_by and filter_value must be provided together"
    ):
        PageSortFilterParams[Item](filter_by="name")


@pytest.mark.asyncio
async def test_heavy_page_sort_filter_params():
    # Test combined functionality
    params = HeavyPageSortFilterParams[Item](
        page=2,
        page_size=200,
        sort_by="value",
        sort_order="desc",
        filter_by="name",
        filter_value="test",
    )
    assert params.page == 2
    assert params.page_size == 200
    assert params.sort_by == "value"
    assert params.sort_order == "desc"
    assert params.filter_by == "name"
    assert params.filter_value == "test"

    # Test default values
    params = HeavyPageSortFilterParams[Item]()
    assert params.page == 1
    assert params.page_size == 100
    assert params.sort_by is None
    assert params.sort_order is None
    assert params.filter_by is None
    assert params.filter_value is None

    # Test page_size validation (should be between 1 and 1000)
    with pytest.raises(ValidationError):
        HeavyPageSortFilterParams[Item](page_size=0)

    with pytest.raises(ValidationError):
        HeavyPageSortFilterParams[Item](page_size=1001)


@pytest.mark.asyncio
async def test_field_type_validation():
    # Test that invalid type for filter_value raises error
    with pytest.raises(
        ValueError, match="Expected <class 'int'> for field value, got <class 'str'>"
    ):
        PageSortFilterParams[Item](
            filter_by="value", filter_value="not_a_number"
        )  # tries to coerce to int, but fails

    # Test that valid type works
    params = PageSortFilterParams[Item](
        filter_by="value", filter_value="42"
    )  # in fact it should be an int but it comes as a string anyways from the request. the type is enforced by the model validator
    assert params.filter_value == 42

    # Test type coercion
    params = PageSortFilterParams[Item](filter_by="name", filter_value="1")
    assert (
        params.filter_value == "1"
    )  # since name is a str, it will be coerced to a string

    params = PageSortFilterParams[Item](filter_by="name", filter_value="test")
    assert params.filter_value == "test"
