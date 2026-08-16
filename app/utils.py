from flask import request

def get_pagination_params(default_limit=20, max_limit=100):
    try:
        page = int(request.args.get("page", 1))
    except ValueError:
        page = 1

    try:
        limit = int(request.args.get("limit", default_limit))
    except ValueError:
        limit = default_limit

    if page < 1:
        page = 1

    if limit < 1:
        limit = default_limit

    if limit > max_limit:
        limit = max_limit

    return page, limit


def pagination_meta(pagination):
    return {
        "page": pagination.page,
        "limit": pagination.per_page,
        "total": pagination.total,
        "pages": pagination.pages,
        "has_next": pagination.has_next,
        "has_prev": pagination.has_prev,
    }