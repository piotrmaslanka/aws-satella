from aws_satella import start_if_not_started

__all__ = ['AWSSatellaMiddleware']


class AWSSatellaMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        from django import conf
        start_if_not_started(**conf.settings.AWS_SATELLA_MIDDLEWARE_CONSTRUCTOR)
        return self.get_response(request)
