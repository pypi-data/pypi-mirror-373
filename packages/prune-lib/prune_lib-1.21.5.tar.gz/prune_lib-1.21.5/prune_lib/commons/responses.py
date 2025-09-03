from django.http import HttpResponse


class JsonStringResponse(HttpResponse):
    def __init__(self, content, *args, **kwargs):
        kwargs["content_type"] = "application/json"
        super().__init__(content, *args, **kwargs)
