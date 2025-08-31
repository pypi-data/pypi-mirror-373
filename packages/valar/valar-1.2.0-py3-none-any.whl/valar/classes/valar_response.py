from django.http import JsonResponse


class ValarResponse(JsonResponse):
    def __init__(self, data=True, message='', code='info'):
        self.message = message
        self.code = code
        super(ValarResponse, self).__init__(data, safe=False)
