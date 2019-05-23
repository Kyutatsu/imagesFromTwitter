from django.shortcuts import render
from django.http import HttpResponse


def index(request):
    return HttpResponse("Hello")


def get_token(request):
    return HttpResponse('get_token')
