from aws_satella import start_if_not_started
import sys

__all__ = ['AWSSatellaMiddleware']


class AWSSatellaMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.is_testing = sys.argv[1:2] == ['test']

    def __call__(self, request):
        from django import conf
        if not self.is_testing:
            start_if_not_started(**conf.settings.AWS_SATELLA_MIDDLEWARE_CONSTRUCTOR)
        return self.get_response(request)
