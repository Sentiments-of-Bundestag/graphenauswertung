from apscheduler.schedulers.background import BackgroundScheduler
import flask_caching

from os import system


class Cache():
    cache = None

    known_cache_keys = set()

    def __init__(self, app, cache_type="redis"):
        config = {
            "CACHE_TYPE": cache_type,
            "CACHE_DEFAULT_TIMEOUT": 3600,  # 1 hour,
            "CACHE_REDIS_HOST": "redis",
        }

        if __name__ == '__main__':
            config['CACHE_TYPE'] = 'simple'

        app.config.from_mapping(config)
        self.cache = flask_caching.Cache(app)

        scheduler = BackgroundScheduler()
        scheduler.add_job(self.update_cache, 'interval', minutes=60)
        scheduler.start()

    def update_cache(self):
        print('update cache')
        print(self.known_cache_keys)
        for key in self.known_cache_keys:
            system('curl http://localhost:5000' + key + ' > /dev/null 2>&1 &')

    def generate_cache_key(self, request):
        cache_key = request.full_path
        self.known_cache_keys.add(cache_key)
        return cache_key
