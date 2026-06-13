from slowapi import Limiter
from slowapi.util import get_remote_address

# Tek bir paylaşılan Limiter örneği.
# Hem main.py (app.state.limiter) hem de router'lar (@limiter.limit) bunu kullanır.
# Aynı örnek olmazsa SlowAPI dekoratörleri çalışmaz.
limiter = Limiter(key_func=get_remote_address)