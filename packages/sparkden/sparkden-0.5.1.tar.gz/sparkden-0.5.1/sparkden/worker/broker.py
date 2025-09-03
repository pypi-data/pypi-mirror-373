def create_broker():
    from dramatiq.brokers.redis import RedisBroker
    from dramatiq.middleware import AsyncIO, CurrentMessage
    from dramatiq.results import Results
    from dramatiq.results.backends.redis import RedisBackend

    from sparkden.shared.redis import get_redis_client

    redis_client = get_redis_client()
    result_backend = RedisBackend(client=redis_client)

    # This broker instance will be discovered by the dramatiq CLI

    broker = RedisBroker(client=redis_client)
    broker.add_middleware(AsyncIO())
    broker.add_middleware(Results(backend=result_backend))
    broker.add_middleware(CurrentMessage())
    return broker
