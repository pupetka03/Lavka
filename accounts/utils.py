



def paginator(objects, page, page_size):
    count = len(objects)
    max_pages = (count + page_size - 1) // page_size
    start = page * page_size
    end = start + page_size

    return objects[start:end]