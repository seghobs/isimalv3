import random
import string


def android_id():
    # ID uzunluğunu belirtin
    # ID uzunluğunu belirtin
    id_length = 16

    # Rastgele bir ID oluşturun
    characters = string.ascii_lowercase + string.digits
    random_id = ''.join(random.choice(characters) for _ in range(id_length))

    print(random_id)
    return random_id

ol = android_id()

print("Android id:", ol)