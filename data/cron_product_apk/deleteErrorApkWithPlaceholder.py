import redis

red = redis.Redis(db=3)

for apk in red.smembers("ios"):
    if "(placeholder)" in apk.lower():
        red.srem("ios",apk)
