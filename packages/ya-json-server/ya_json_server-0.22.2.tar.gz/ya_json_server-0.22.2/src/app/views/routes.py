from typing import Annotated

from fastapi import APIRouter, Query, UploadFile

from app.config import DB_JSON_FILENAME
from app.controllers.resources import ResourcesController

router = APIRouter()

resources_ctlr = ResourcesController()


@router.get(
    "/",
    summary="Get list of resources.",
    tags=["API"],
    response_description="Resources names and their total number of items.",
)
async def get_resources_list() -> list[dict]:
    return resources_ctlr.get_resources_list()


@router.get(
    "/{resource}",
    summary="Get all the data of the resource.",
    tags=["API"],
)
async def get_resource_data(
    resource,
    page: Annotated[int, Query(gt=0)] = resources_ctlr.page,
    limit: Annotated[
        int,
        Query(
            ge=10, description="The maximum number of items to retrieve for each page."
        ),
    ] = resources_ctlr.limit,
):
    return resources_ctlr.get_resource_data(resource, page, limit)


resource_id_description = """

| status | results
| ------ | -------
|  200   | OK. Response data of the **id** like (e.g: `id`, `ceoUserId`, `idProduct`) attribute in the data structure<sup>*</sup>.
|  404   | The `resource` requested not found.
|  404   | The `resource` requested has not an **id** like attribute.
|  404   | Data not found for the `resource`/`id`. *It only checks for the first **id** like atribute.*

\\* Let's suppose this sample structure and data:  
```json
{
  "stoke-exchange": [
    {
      "company": "Chuchu e Melão S/A",
      "city": "Belo Horizonte",
      "ceoUserId": '99273502-9448-4197-abc4-422d4c792264',
      "state": "Minas Gerais",
      "id": 19,
      "country": "Brasil",
      "postcode": 40256,
      "idProduct": 19,
      "priceTag": "45,593,820",
      "shareValue": "617.00"
    }
  ]
}
```

So, for the following requests:

1. `/stoke-exchange/17`: it is not found, `ceoUserId == 17` does not matches.
2. `/stoke-exchange/19`: it is not found, `ceoUserId == 19` does not matches.
3. `/stoke-exchange/99273502-9448-4197-abc4-422d4c792264`: **it is found**, `ceoUserId == "99273502-9448-4197-abc4-422d4c792264"` matches.

And the other way round for the structure and data also works, e.g.:  
```json
{
  "stoke-exchange": [
    {
      "company": "Chuchu e Melão S/A",
      "city": "Belo Horizonte",
      "idProduct": 19,
      "state": "Minas Gerais",
      "id": 17,
      "country": "Brasil",
      "ceoUserId": '99273502-9448-4197-abc4-422d4c792264',
      "postcode": 40256,
      "priceTag": "45,593,820",
      "shareValue": "617.00"
    }
  ]
}
```

Requests:
1. `/stoke-exchange/99273502-9448-4197-abc4-422d4c792264`: it is not found.
2. `/stoke-exchange/17`: it is not found.
3. `/stoke-exchange/19`: **it is found**, `idProduct == 19` matches.

"""


@router.get(
    "/{resource}/{id}",
    summary="Get the resource ID data.",
    description=resource_id_description,
    tags=["API"],
)
async def get_resources_by_id(resource, id: int | str):
    return resources_ctlr.retrieve_resources_by_id(resource, id)


@router.put(
    "/upload",
    summary=f"Update DB JSON file ({DB_JSON_FILENAME}) from CSV file content.",
    description="""
    
    """,
    tags=["API"],
)
async def create_json_file_from_csv(csv_file: UploadFile):
    response = await resources_ctlr.update_db_json_from_csv(csv_file)
    return response
