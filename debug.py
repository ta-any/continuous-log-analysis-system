import queue

def inspect_queue(q):
    """Получить информацию об очереди"""
    return {
        'size': q.qsize(),
        'empty': q.empty(),
        'full': q.full(),
        'maxsize': q.maxsize if hasattr(q, 'maxsize') else 'unlimited'
    }
