from rest_framework import status
from rest_framework.response import Response


def HTTP_REQUEST(code, messages="") -> Response:
    return Response({"messages": f"{messages}",
                     "code": code},
                    status=code)


def HTTP_400_BAD_REQUEST(messages="") -> Response:
    return HTTP_REQUEST(status.HTTP_400_BAD_REQUEST, f"Validation Failed : {messages}")
