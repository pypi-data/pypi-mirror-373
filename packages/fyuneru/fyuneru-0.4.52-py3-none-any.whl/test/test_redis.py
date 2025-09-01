from fyuneru.redis import generate_redis_key


def test_generate_redis_key():
    print(generate_redis_key("test"))


test_generate_redis_key()
