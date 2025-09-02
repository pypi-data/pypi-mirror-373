# Data storage and retrieval

`msal` is a python library that utilizes MS graph API (REST API) to interact with MS applications.</br>

for the use of `msal`, we first need an Azure Active Directory, which is associated with a `client_id` to generate `token` to access the applications.</br>

So first of all, we need to get a `client_id` in order to do authentification. To get a `client_id`, I need to register an app on Azura Active Directory (ADD). I don't have the permission to register an app on AAU's AAD.</br>

## REST API

A REST API (also known as RESTful API) is an application programming interface (API or web API) that conforms to the constraints of REST architectural style and allows for interaction with RESTful web services.</br>

REST is not a specification but a set of guidelines on how to <mark>__architect__</mark> a network-connected software system.

1. Stateless
2. Client-server
3. Cacheable
4. Uniform interface
5. Layered system
6. Code on demand

A REST web service provides an API to expose their data to the ouside world

### HTTP methods

REST APIs listen for HTTP methods, like `GET`, `POST`, `DELETE`, to know which operation to perform on the web service's resources. A resource is any data available in the web service that can be accessed and manipulated with HTTP requests.

### Status codes

Once a REST API receives and processes an HTTP request, it will return an HTTP response, including an HTTP status code.</br>

| Code range | Category             |
| :--------- | :------------------- |
| 2xx        | Successful Operation |
| 3xx        | Redirection          |
| 4xx        | Client Error         |
| 5xx        | Server Error         |

### Endpoint

A REST API exposes a set of public URLs that client applications use to access the resources of a web service

| HTTP method |        API endpoint        |       Description       |
| :---------: | :------------------------: | :---------------------: |
|    `GET`    |        `/customers`        | Get a list of customers |
|    `GET`    | `/customers/<customer_id>` |  Get a single customer  |
|   `POST`    |        `/customers`        |  Create a new customer  |


### python consuming API

```python
import requests

api_url = "https://path/to/url"
response = requests.get(api_url)
response.json()
response.status_code
response.headers
```

