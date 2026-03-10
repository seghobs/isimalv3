import random
import string


def android_id():
    """Rastgele 16 karakterli Android ID üretir"""
    id_length = 16
    characters = string.ascii_lowercase + string.digits
    return ''.join(random.choice(characters) for _ in range(id_length))
