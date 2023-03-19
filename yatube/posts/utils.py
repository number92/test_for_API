from django.core.paginator import Paginator


POST_PER_PAGE = 10


def get_paginator(request, *args):
    page_number = request.GET.get('page')
    page_obj = Paginator(*args, POST_PER_PAGE).get_page(page_number)
    return page_obj
