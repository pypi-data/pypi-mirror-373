import re
import time
from datetime import (
    datetime,
)

from django.core.cache import (
    DEFAULT_CACHE_ALIAS,
    cache,
    caches,
)
from django.core.cache.backends.locmem import (
    LocMemCache,
)
from django_redis.cache import (
    RedisCache,
)

from behave_bo.loggers import (
    tests_logger,
)


# Сохранять TTL при дампе DjangoCache с типом бэекенда Redis
DUMP_REDIS_CACHE_WITH_TTL = False


class BehaveLocMemCache(LocMemCache):
    """Cache для использования в тестах. Дополнен методом keys,
    аналогичным методу keys в RedisCache"""

    def keys(self, pattern):
        """
        Метод для получения списка ключей по шаблону из кеша приложения.
        Возвращает ключи без служебного префикса, который добавляется по-умолчанию в методах LocMemCache.

        Args:
            pattern: Регулярное выражение для поиска ключей в кэше
        """
        pattern = pattern.replace('*', '.*')
        res = list()

        with self._lock:
            cache_keys = self._cache.copy()

        for key in cache_keys:
            # получим изначальный ключ удалив из него префикс key_prefix:version:
            pure_key = key.replace(f'{self.key_prefix}:{self.version}:', '', 1)

            if re.match(pattern, pure_key) and not self._has_expired(key):
                res.append(pure_key)

        return res

    def ttl(self, key, version=None):
        """Получение значение ttl для ключа.

        Эмулирует метод django_redis.client.default.DefaultClient.ttl.

        Args:
            key: Значение ключа в кэше;
            version: Версия ключа в кэше.

        Returns:
            ttl ключа или None, если ключ не существует.
        """
        time_to_live = 0

        if self.has_key(key, version=version):
            key = self.make_key(key, version=version)

            if expire_time := self._expire_info.get(key, None):
                time_to_live = int(expire_time - time.time())
            else:
                time_to_live = None

        return time_to_live

    def _cull(self):
        """Удаляет ключи при превышении их количества, задаваемого в настройке MAX_ENTRIES.

        Здесь просто выведем в лог сообщение для отслеживания вызова метода.
        """
        tests_logger.warn(
            f'Превышен лимит количества хранимых ключей, равный {self._max_entries}. '
            f'{len(self._cache) // self._cull_frequency} ключей будет удалено.'
        )
        super()._cull()


def get_cache_backend():
    """"
        Возвращает класс backend'а Django Cache
    """
    cache_backend = caches[DEFAULT_CACHE_ALIAS].__class__

    return cache_backend


def setup_cache_server_db(db_num):
    """
        Устанавливает используемую в redis бд путем замены окончания в переменной _server.
    """
    cache_backend = get_cache_backend()
    if issubclass(cache_backend, RedisCache):
        server_url = cache._server.rsplit('/', 1)[0]
        cache._server = f'{server_url}/{db_num}'


def django_cache_dump():
    """
        Функция сохраняет текущие значения ключей из Django Cache
        и возвращает их в словаре. Формат возвращаемого словаря зависит от
        backend'а которы используется для Django Cache
    """
    cache_backend = get_cache_backend()
    cache_dump = {}
    if issubclass(cache_backend, LocMemCache):
        with cache._lock:
            cache_dump['_cache'] = cache._cache.copy()
            cache_dump['_expire_info'] = cache._expire_info.copy()
    elif issubclass(cache_backend, RedisCache):
        keys = cache.keys('*')
        cache_dump['redis_keys'] = cache.get_many(keys)
        if DUMP_REDIS_CACHE_WITH_TTL:
            cache_dump['redis_ttl'] = {}
            for key in keys:
                cache_dump['redis_ttl'][key] = cache.ttl(key)
            cache_dump['time'] = datetime.now()

    return cache_dump


def django_cache_restore(cache_dump):
    """
        Функция принимает на вход снимок Django Cache,
        полученный в django_cache_dump(), и восстанавливает состояние кеша
        на основании этого снимка.
    """
    cache_backend = get_cache_backend()
    if issubclass(cache_backend, LocMemCache):
        with cache._lock:
            if all(k in cache_dump for k in ('_cache', '_expire_info')):
                cache._cache = cache_dump.get('_cache')
                cache._expire_info = cache_dump.get('_expire_info')
    elif issubclass(cache_backend, RedisCache):
        cache.clear()
        if not DUMP_REDIS_CACHE_WITH_TTL:
            cache.set_many(cache_dump.get('redis_keys', {}))
        else:
            time_passed = (datetime.now() - cache_dump['time']).total_seconds()
            for key, value in cache_dump['redis_keys'].items():
                old_ttl = cache_dump['redis_ttl'].get(key, 0)
                new_ttl = int(max(old_ttl - time_passed, 0))
                cache.add(key, value, timeout=new_ttl)
