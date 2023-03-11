from django.core.paginator import Paginator


POST_PER_PAGE = 10


def get_paginator(request, post_list):
    page_number = request.GET.get('page')
    page_obj = Paginator(post_list, POST_PER_PAGE).get_page(page_number)
    return page_obj
