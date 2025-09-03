import json

from django.http import HttpRequest


def get_data_from_request(request: HttpRequest) -> dict | None:
    if request.method in ["POST", "PUT", "DELETE"]:
        if request.content_type == "application/json":
            data = json.loads(request.body)
        elif request.content_type in [
            "multipart/form-data",
            "application/x-www-form-urlencoded",
        ]:
            data = request.POST.dict() | request.FILES.dict()
        else:
            raise NotImplementedError
    elif request.method == "GET":
        data = request.GET.dict()
    else:
        raise NotImplementedError
    return data
