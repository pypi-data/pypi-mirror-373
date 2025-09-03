

try:

    from pureaes.py_aes import AesWrapper
except ImportError:
    raise ImportError("Please install purePyAES first.")


def gen_random_key():
    with open("/dev/urandom", 'rb') as fb:
        fb = fb.read(32)
        return fb.hex().__str__()


if __name__ == "__main__":
    """
    Example usage. Super straightforward. I did it first! See BlitzKloud. There was no pure python AES
    at that time. Hire me, I am that good.
    """

    print('[+] Generating a random AES key ...')
    key = gen_random_key()[:32]
    print('[+] AES key generated: {}'.format(key), len(key))
    aes = AesWrapper(key.encode())
    enc_input = input('type something >> ')
    if not enc_input or enc_input.strip('\r\n') == '':
        print("[+] Or don't")
        enc_input = 'test this data'
        print('[+] We will use `test this data` then ...')
    print('[$] purePyAES.encrypt: ')
    enc_data = aes.encrypt(enc_input)
    print('[enc] %s' % enc_data)
    denc_data = aes.decrypt(enc_data)
    print('purePyAES.decrypt: ')
    print('[denc] %s' % denc_data)
