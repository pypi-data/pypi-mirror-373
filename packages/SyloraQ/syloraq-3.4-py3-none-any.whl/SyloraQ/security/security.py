from SyloraQ.module import runwithin,decode_base64,reverse_string,shiftinwin,replace,SQNode,boa,shiftinwin,Jbtc,Jctb,encode_base64,decode_base64,reverse_string
import os,hashlib,math,random
from typing import Optional, List

class inviShade: # Obfuscated to enhance security and mitigate the risk of algorithm reverse engineering or data compromise.
    def encode(text):return runwithin(decode_base64(reverse_string(shiftinwin(-8381,SQNode("inviSenc")))),"DEcode.ec()",text)
    def decode(text):return runwithin(decode_base64(reverse_string(shiftinwin(-8381,SQNode("inviSenc")))),"DEcode.dc()",text)

def hex2byte(hex_str: str) -> bytes:return bytes.fromhex(hex_str)
def gf_mul(a, b):
    p = 0
    for _ in range(8):
        if b & 1:p ^= a
        hi_bit_set = a & 0x80
        a <<= 1
        a &= 0xFF
        if hi_bit_set:a ^= 0x1B
        b >>= 1
    return p
def gf_inv(a):
    if a == 0:
        return 0
    lm, hm = 1, 0
    low, high = a, 0x11B
    while low > 1:
        ratio = high // low
        nm = hm ^ gf_mul(lm, ratio)
        new = high ^ gf_mul(low, ratio)
        hm, lm = lm, nm
        high, low = low, new
    return lm & 0xFF
def rotate_left(byte, count):return ((byte << count) | (byte >> (8 - count))) & 0xFF
def affine_transform(byte):
    b = byte
    res = b ^ rotate_left(b, 1) ^ rotate_left(b, 2) ^ rotate_left(b, 3) ^ rotate_left(b, 4) ^ 0x63
    return res & 0xFF
def compute_inv_sbox(sbox):
    inv_sbox = [0]*256
    for i, val in enumerate(sbox):inv_sbox[val] = i
    return inv_sbox
SBOX = [0x63, 0x7c, 0x77, 0x7b, 0xf2, 0x6b, 0x6f, 0xc5,0x30, 0x01, 0x67, 0x2b, 0xfe, 0xd7, 0xab, 0x76,0xca, 0x82, 0xc9, 0x7d, 0xfa, 0x59, 0x47, 0xf0,0xad, 0xd4, 0xa2, 0xaf, 0x9c, 0xa4, 0x72, 0xc0,0xb7, 0xfd, 0x93, 0x26, 0x36, 0x3f, 0xf7, 0xcc,0x34, 0xa5, 0xe5, 0xf1, 0x71, 0xd8, 0x31, 0x15,0x04, 0xc7, 0x23, 0xc3, 0x18, 0x96, 0x05, 0x9a,0x07, 0x12, 0x80, 0xe2, 0xeb, 0x27, 0xb2, 0x75,0x09, 0x83, 0x2c, 0x1a, 0x1b, 0x6e, 0x5a, 0xa0,0x52, 0x3b, 0xd6, 0xb3, 0x29, 0xe3, 0x2f, 0x84,0x53, 0xd1, 0x00, 0xed, 0x20, 0xfc, 0xb1, 0x5b,0x6a, 0xcb, 0xbe, 0x39, 0x4a, 0x4c, 0x58, 0xcf,0xd0, 0xef, 0xaa, 0xfb, 0x43, 0x4d, 0x33, 0x85,0x45, 0xf9, 0x02, 0x7f, 0x50, 0x3c, 0x9f, 0xa8,0x51, 0xa3, 0x40, 0x8f, 0x92, 0x9d, 0x38, 0xf5,0xbc, 0xb6, 0xda, 0x21, 0x10, 0xff, 0xf3, 0xd2,0xcd, 0x0c, 0x13, 0xec, 0x5f, 0x97, 0x44, 0x17,0xc4, 0xa7, 0x7e, 0x3d, 0x64, 0x5d, 0x19, 0x73,0x60, 0x81, 0x4f, 0xdc, 0x22, 0x2a, 0x90, 0x88,0x46, 0xee, 0xb8, 0x14, 0xde, 0x5e, 0x0b, 0xdb,0xe0, 0x32, 0x3a, 0x0a, 0x49, 0x06, 0x24, 0x5c,0xc2, 0xd3, 0xac, 0x62, 0x91, 0x95, 0xe4, 0x79,0xe7, 0xc8, 0x37, 0x6d, 0x8d, 0xd5, 0x4e, 0xa9,0x6c, 0x56, 0xf4, 0xea, 0x65, 0x7a, 0xae, 0x08,0xba, 0x78, 0x25, 0x2e, 0x1c, 0xa6, 0xb4, 0xc6,0xe8, 0xdd, 0x74, 0x1f, 0x4b, 0xbd, 0x8b, 0x8a,0x70, 0x3e, 0xb5, 0x66, 0x48, 0x03, 0xf6, 0x0e,0x61, 0x35, 0x57, 0xb9, 0x86, 0xc1, 0x1d, 0x9e,0xe1, 0xf8, 0x98, 0x11, 0x69, 0xd9, 0x8e, 0x94,0x9b, 0x1e, 0x87, 0xe9, 0xce, 0x55, 0x28, 0xdf,0x8c, 0xa1, 0x89, 0x0d, 0xbf, 0xe6, 0x42, 0x68,0x41, 0x99, 0x2d, 0x0f, 0xb0, 0x54, 0xbb, 0x16,];INV_SBOX = compute_inv_sbox(SBOX);RCON = [0x00,0x01, 0x02, 0x04, 0x08,0x10, 0x20, 0x40, 0x80,0x1B, 0x36,]
def xor_bytes(a, b):return bytes(x ^ y for x, y in zip(a, b))
def pad_pkcs7(data):
    pad_len = 16 - (len(data) % 16)
    return data + bytes([pad_len]*pad_len)
def unpad_pkcs7(data):
    pad_len = data[-1]
    if pad_len < 1 or pad_len > 16:raise ValueError("Invalid PKCS7 padding")
    if data[-pad_len:] != bytes([pad_len]*pad_len):raise ValueError("Invalid PKCS7 padding")
    return data[:-pad_len]
def sub_word(word):return bytes(SBOX[b] for b in word)
def rot_word(word):return word[1:] + word[:1]
def key_expansion(key):
    Nk = 4
    Nr = 10
    Nb = 4
    w = [key[i*4:(i+1)*4] for i in range(Nk)]
    for i in range(Nk, Nb*(Nr+1)):
        temp = w[i-1]
        if i % Nk == 0:temp = xor_bytes(sub_word(rot_word(temp)), bytes([RCON[i//Nk], 0,0,0]))
        w.append(xor_bytes(w[i-Nk], temp))
    return w
def add_round_key(state, round_key):return bytes(s ^ k for s,k in zip(state, round_key))
def sub_bytes(state):return bytes(SBOX[b] for b in state)
def inv_sub_bytes(state):return bytes(INV_SBOX[b] for b in state)
def shift_rows(state):
    new_state = bytearray(16)
    for r in range(4):
        for c in range(4):new_state[4*c + r] = state[4*((c + r) %4) + r]
    return bytes(new_state)
def inv_shift_rows(state):
    new_state = bytearray(16)
    for r in range(4):
        for c in range(4):new_state[4*c + r] = state[4*((c - r) %4) + r]
    return bytes(new_state)
def xtime(a):return ((a <<1) ^ 0x1B) & 0xFF if (a & 0x80) else (a << 1)
def mix_single_column(a):
    t = a[0] ^ a[1] ^ a[2] ^ a[3]
    u = a[0]
    a0 = a[0] ^ t ^ xtime(a[0] ^ a[1])
    a1 = a[1] ^ t ^ xtime(a[1] ^ a[2])
    a2 = a[2] ^ t ^ xtime(a[2] ^ a[3])
    a3 = a[3] ^ t ^ xtime(a[3] ^ u)
    return bytes([a0 & 0xFF, a1 & 0xFF, a2 & 0xFF, a3 & 0xFF])
def mix_columns(state):
    new_state = bytearray(16)
    for c in range(4):
        col = state[c*4:c*4+4]
        mixed = mix_single_column(col)
        new_state[c*4:c*4+4] = mixed
    return bytes(new_state)
def inv_mix_columns(state):
    new_state = bytearray(16)
    for c in range(4):
        a = list(state[c*4:c*4+4])
        u = gf_mul(a[0], 0x0e) ^ gf_mul(a[1], 0x0b) ^ gf_mul(a[2], 0x0d) ^ gf_mul(a[3], 0x09)
        v = gf_mul(a[0], 0x09) ^ gf_mul(a[1], 0x0e) ^ gf_mul(a[2], 0x0b) ^ gf_mul(a[3], 0x0d)
        w = gf_mul(a[0], 0x0d) ^ gf_mul(a[1], 0x09) ^ gf_mul(a[2], 0x0e) ^ gf_mul(a[3], 0x0b)
        x = gf_mul(a[0], 0x0b) ^ gf_mul(a[1], 0x0d) ^ gf_mul(a[2], 0x09) ^ gf_mul(a[3], 0x0e)
        new_state[c*4:c*4+4] = bytes([u,v,w,x])
    return bytes(new_state)
def encrypt_block(block, round_keys):
    state = block
    state = add_round_key(state, b''.join(round_keys[0:4]))
    for rnd in range(1, 10):
        state = sub_bytes(state)
        state = shift_rows(state)
        state = mix_columns(state)
        state = add_round_key(state, b''.join(round_keys[rnd*4:(rnd+1)*4]))
    state = sub_bytes(state)
    state = shift_rows(state)
    state = add_round_key(state, b''.join(round_keys[40:44]))
    return state
def decrypt_block(block, round_keys):
    state = block
    state = add_round_key(state, b''.join(round_keys[40:44]))
    for rnd in range(9, 0, -1):
        state = inv_shift_rows(state)
        state = inv_sub_bytes(state)
        state = add_round_key(state, b''.join(round_keys[rnd*4:(rnd+1)*4]))
        state = inv_mix_columns(state)
    state = inv_shift_rows(state)
    state = inv_sub_bytes(state)
    state = add_round_key(state, b''.join(round_keys[0:4]))
    return state
def aes_cbc_encrypt(plaintext, key, iv):
    if len(key) != 16:raise ValueError("Key must be 16 bytes")
    if len(iv) != 16:raise ValueError("IV must be 16 bytes")
    round_keys = key_expansion(key)
    plaintext = pad_pkcs7(plaintext)
    blocks = [plaintext[i:i+16] for i in range(0, len(plaintext), 16)]
    ciphertext = b""
    prev = iv
    for block in blocks:
        block = xor_bytes(block, prev)
        encrypted = encrypt_block(block, round_keys)
        ciphertext += encrypted
        prev = encrypted
    return ciphertext
def aes_cbc_decrypt(ciphertext, key, iv):
    if len(key) != 16:raise ValueError("Key must be 16 bytes")
    if len(iv) != 16:raise ValueError("IV must be 16 bytes")
    if len(ciphertext) % 16 != 0:raise ValueError("Ciphertext length must be multiple of 16")
    round_keys = key_expansion(key)
    blocks = [ciphertext[i:i+16] for i in range(0, len(ciphertext), 16)]
    plaintext = b""
    prev = iv
    for block in blocks:
        decrypted = decrypt_block(block, round_keys)
        plaintext_block = xor_bytes(decrypted, prev)
        plaintext += plaintext_block
        prev = block
    return unpad_pkcs7(plaintext)
class ZypherTrail:
    @staticmethod
    def encode(string, max_row=5):
        min_row=0
        height = max_row - min_row + 1
        width = len(string)
        grid = [[' ' for _ in range(width)] for _ in range(height)]
        row = min_row
        direction = 1
        for col, char in enumerate(string):
            grid[row][col] = char
            row += direction
            if row > max_row:
                row = max_row - 1
                direction = -1
            elif row < min_row:
                row = min_row + 1
                direction = 1
        return '\n'.join(''.join(row) for row in grid)
    @staticmethod
    def decode(encoded_str):
        grid = encoded_str.split('\n')
        height = len(grid)
        width = len(grid[0]) if height > 0 else 0
        row = 0
        direction = 1
        result = []
        for col in range(width):
            char = grid[row][col]
            result.append(char)
            row += direction
            if row >= height:
                row = height - 2
                direction = -1
            elif row < 0:
                row = 1
                direction = 1
        return ''.join(result)
class FinalLockerCipher:
    def __init__(self, key): 
        if isinstance(key, str):
            key = key.encode()
        self.key = key
    def _permute(self, byte, i):
        return (byte ^ self.key[i % len(self.key)] ^ (i * 149) % 256) % 256
    def encrypt(self, data: bytes) -> bytes:
        return bytes([self._permute(b, i) for i, b in enumerate(data)])
    def decrypt(self, data: bytes) -> bytes:
        return self.encrypt(data)

class Q1:
    @staticmethod
    def encrypt(string: str, key: bytes = b"0123456789abcdef"):
        iv = os.urandom(16)
        plaintext = string.encode()
        ct_bytes  = aes_cbc_encrypt(plaintext, key, iv)
        rotated_iv     = shiftinwin(len(str(key)), iv)
        rotated_iv_hex = rotated_iv.hex()
        payload = f"{ct_bytes.hex()}:::{rotated_iv_hex}"
        return ZypherTrail.encode(payload)

    @staticmethod
    def decrypt(encrypted: str, key: bytes = b"0123456789abcdef"):
        recovered = ZypherTrail.decode(encrypted)
        cipher_hex, iv_hex = recovered.split(":::", 1)
        ct_bytes = bytes.fromhex(cipher_hex)
        rotated_iv = bytes.fromhex(iv_hex)
        iv = shiftinwin(-len(str(key)), rotated_iv)
        return aes_cbc_decrypt(ct_bytes, key, iv)

class Q2:
    @staticmethod
    def encrypt(string:str,key:int=8381):return reverse_string(shiftinwin(key,encode_base64(ZypherTrail.encode(Jctb(string)))))
    @staticmethod
    def decyrpt(string:str,key):return Jbtc(ZypherTrail.decode(decode_base64(shiftinwin(-key,reverse_string(string)))))
class Q3:
    @staticmethod
    def encode(string:str,key:str):
        Flc = FinalLockerCipher(key)
        return Flc.encrypt(string.encode()).hex()
    @staticmethod
    def decode(string: str, key: str):
        Flc = FinalLockerCipher(key)
        return Flc.decrypt(hex2byte(string)).decode()
def derive_key_bytes(password: str, salt: bytes = b'hello_from_syloraq', iterations: int = 100_000, key_len: int = 16) -> bytes:return hashlib.pbkdf2_hmac('sha256', password.encode(), salt, iterations, dklen=key_len)

class Quasar:
    def encrypt(plaintext, password_str="securekey", key_int=8381):salt = b'ujHUhuUHhhuH';key_bytes = derive_key_bytes(password_str, salt);layer3 = Q3.encode((plaintext), password_str);layer2 = Q2.encrypt(layer3, key_int);layer1 = Q1.encrypt(layer2, key_bytes);return layer1
    def decrypt(encrypted, password_str="securekey", key_int=8381):salt = b'ujHUhuUHhhuH';key_bytes = derive_key_bytes(password_str, salt);layer1 = Q1.decrypt(encrypted, key_bytes);layer2 = Q2.decyrpt(layer1, key_int);layer3 = Q3.decode(layer2, password_str);return layer3

class CoLine:
    @staticmethod
    def encode(input_str: str,cols: int,shifttype: str,line_idx: Optional[int] = None,col_idx: Optional[int] = None) -> str:
        total = math.ceil(len(input_str) / cols) * cols
        data = list(input_str.ljust(total))
        grid: List[List[str]] = [data[i:i+cols] for i in range(0, total, cols)]
        rows = len(grid)
        if shifttype == 'line' and line_idx:
            r = line_idx - 1
            if 0 <= r < rows:
                row = grid[r]
                grid[r] = [row[-1]] + row[:-1]
        elif shifttype == 'column' and col_idx:
            c = col_idx - 1
            if 0 <= c < cols:
                col_vals = [grid[r][c] for r in range(rows)]
                new_col = [col_vals[-1]] + col_vals[:-1]
                for r in range(rows):grid[r][c] = new_col[r]
        result = ''.join(cell for row in grid for cell in row)
        return result.rstrip()
    @staticmethod
    def decode(input_str: str, cols: int, shifttype: str, line_idx: Optional[int] = None, col_idx: Optional[int] = None) -> str:
        total = math.ceil(len(input_str) / cols) * cols
        data = list(input_str.ljust(total))
        grid: List[List[str]] = [data[i:i+cols] for i in range(0, total, cols)]
        rows = len(grid)
        if shifttype == 'line' and line_idx:
            r = line_idx - 1
            if 0 <= r < rows:
                row = grid[r]
                grid[r] = row[1:] + [row[0]]
        elif shifttype == 'column' and col_idx:
            c = col_idx - 1
            if 0 <= c < cols:
                col_vals = [grid[r][c] for r in range(rows)]
                new_col = col_vals[1:] + [col_vals[0]]
                for r in range(rows):grid[r][c] = new_col[r]
        result = ''.join(cell for row in grid for cell in row)
        return result.rstrip()

class ParseShield:
    invisible_chars = ['\u200B','\u200C','\u200D','\u2060','\uFEFF','\u034F','\u180B','\u180C','\u180D','\u180E','\uFE00','\uFE01','\uFE02','\uFE03','\uFE04','\uFE05','\uFE06','\uFE07','\uFE08','\uFE09','\uFE0A','\uFE0B','\uFE0C','\uFE0D','\uFE0E','\uFE0F','\U000E017F']
    @staticmethod
    def encode(input_text: str, expansion_factor: int = 5) -> str:
        encoded = []
        for ch in input_text:
            encoded.append(ch)
            for _ in range(random.randint(1, expansion_factor)):encoded.append(random.choice(ParseShield.invisible_chars))
        return ''.join(encoded)
    @staticmethod
    def decode(input_text):return ''.join(ch for ch in input_text if ch not in ParseShield.invisible_chars)