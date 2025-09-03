# Yet Another JSON Server

[![image](https://gitlab.com/adrianovieira/ya-json-server/badges/main/pipeline.svg)](https://gitlab.com/adrianovieira/ya-json-server/-/pipelines)
[![image](https://gitlab.com/adrianovieira/ya-json-server/badges/main/coverage.svg?job=job::tests::api&key_text=coverage)](https://gitlab.com/adrianovieira/ya-json-server/-/jobs/artifacts/main/browse?job=job::tests::api)

## Introduction

A REST API for JSON content with zero coding.

Technologies::

- Python 3.13+
- FastAPI 0.116+

## Getting started

This project has two options to have your data available for the API.  
1. Create a JSON file with your resources data.  
    So, use the docker image and define the file as volume for the API.
2. Upload a CSV file into the API which will converte it to a JSON file, and 
    the file name is used as the _resource_ name.  
  For awhile, this option will updata the JSON file as a whole.

**JSON file simple sample data structures**:  
(e.g.: `my-db-data.json`)  

Case with one "resources" (`posts`).  
```json
{
    "posts": [
    {
      "id": 1,
      "title": "json-server",
      "author": "Adriano Vieira"
    }
  ]
}
```  
        
or

<details open>
<summary>
<i>Multiple "resources" (`posts`, `comments`, `products`, and `stoke-exchange`).</i>
👈🏽
</summary>

```json
{
  "posts": [ {"id": 1, "title": "json-server", "author": "Adriano Vieira" } ],
  "comments": [ {"id": 1, "body": "some comment", "postId": 1 } ],
  "products": [
    {
      "productId": 375,
      "title": "Dress",
      "brand": "Adidas",
      "price": 40,
      "reviewScore": 1.0431592108,
      "color": "Black",
      "size": "XL",
      "image": "http://products.net/img/"
    }
  ],
  "stoke-exchange": [
    {
      "company": "Chuchu e Melão S/A",
      "city": "Belo Horizonte",
      "ceoUserId": "99273502-9448-4197-abc4-422d4c792264",
      "state": "Minas Gerais",
      "id": 17,
      "country": "Brasil",
      "postcode": 40256,
      "idProduct": 19,
      "priceTag": "45,593,820",
      "shareValue": "617.00"
    }
  ]
}
```
</details>

<br />

**For those examples**:
- **the "*resources*"**: `posts`, `comments`, `products`, and `stoke-exchange` are the
_resources_ enpoints that you would make requests on the API.
- **the "*requests*"**: `posts/1`, `comments/1`, `products/375`, and
`stoke-exchange/99273502-9448-4197-abc4-422d4c792264` will get a valid responses data.
  - But the requests: `stoke-exchange/17` and `stoke-exchange/19` will get error 
  response   
(_read the [OpenAPI Document](https://gitlab.com/adrianovieira/ya-json-server/-/blob/main/docs/openapi.json) for details_).

### Making requests

You can use the Docker image from the project, e.g.:

```shell
docker run --detach -p 80:8000 -v ./my-db-data.json:/home/worker/data/db.json \
    registry.gitlab.com/adrianovieira/ya-json-server:v1.0
```

| endpoints              | summary                                    |
| ---------------------- | ------------------------------------------ |
| `GET /`                | Get list of resources.                     |
| `GET /{resource}`      | Get all the data of the resource.          |
| `GET /{resource}/{id}` | Get the resource ID data.                  |
| `PUT /upload`          | Update DB JSON file from CSV file content. |
| `...`                  |

Check the
[OpenAPI Document](https://gitlab.com/adrianovieira/ya-json-server/-/blob/main/docs/openapi.json)
to read the full description for each endpoint.

You also can access the documentation for the running API at
http://api.localhost/docs

## License

> Apache License 2.0
