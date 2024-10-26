# 병원 조회 API

<a href="http://cataractserver.hunian.site/docs">Go to Swagger UI</a>

## Endpoint

```
POST /hospital
```

## Request

- Method : POST
- Content-Type : application/json

Request Body Example (JSON):

```
{
  "latitude": 37.7749,
  "longitude": -122.4194,
  "limit": 5
}
```

| parameter	| Type	| Description |
| --- | --- | --- |
| latitude	| float	| Latitude of the user’s location. |
| longitude	| float	| Longitude of the user’s location. |
| limit | integer | (Optional) Number of hospitals to return. |

## Response

- Status Code : 200 OK
- Content-Type : application/json

Response Body Example (JSON):

```
{
  "hospitals": [
    {
      "id": 1,
      "name": "City Hospital",
      "address": "123 Main St, San Francisco, CA",
      "latitude": 37.7741,
      "longitude": -122.4179,
      "distance_km": 1.2
    },
    {
      "id": 2,
      "name": "General Medical Center",
      "address": "456 Elm St, San Francisco, CA",
      "latitude": 37.7732,
      "longitude": -122.4200,
      "distance_km": 0.8
    }
  ]
}
```

| Field	| Type | Description |
| --- | --- | --- |
| id | integer | Unique identifier of the hospital. |
| name | string	| Name of the hospital. |
| address | string | Address of the hospital. |
| latitude | float | Latitude of the hospital’s location. |
| longitude	| float	| Longitude of the hospital’s location. |
| distance_km | float | Distance from the given location (in km). |