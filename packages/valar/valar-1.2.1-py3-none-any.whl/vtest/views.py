import json

from ..valar.classes.valar_response import ValarResponse


def valar_test_request(request):
    body = json.loads(request.body)
    return ValarResponse(body)
