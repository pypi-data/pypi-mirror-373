'''
Created on 3 Nov 2020

@author: jacklok
'''
from cryptography.fernet import Fernet
from trexconf.conf import CRYPTO_SECRET_KEY, AES256_SECRET_KEY
import json, logging

from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from Crypto.Random import get_random_bytes 
import base64
import secrets

logger = logging.getLogger('utils')

def encrypt(value, fernet_key=CRYPTO_SECRET_KEY):
    
    if value:
        f = Fernet(fernet_key)
        return f.encrypt(value.encode()).decode('utf-8')
    
def encrypt_json(json_value, fernet_key=CRYPTO_SECRET_KEY):
    
    if json_value:
        f = Fernet(fernet_key)
        return f.encrypt(json.dumps(json_value).encode()).decode('utf-8')
    
def aes_encrypt(message, key=AES256_SECRET_KEY):
    
    if message:
        # Decode the key from Base64
        key = base64.urlsafe_b64decode(key)

        # Verify the key length
        assert len(key) == 32, "Key must be 32 bytes for AES-256."
    
        # Generate a random 16-byte IV
        iv = get_random_bytes(16)
        cipher = AES.new(key, AES.MODE_CBC, iv)
    
        # Pad the message to be a multiple of the AES block size (16 bytes)
        padded_message = pad(message.encode(), AES.block_size)
        
        # Encrypt the padded message
        encrypted_message = cipher.encrypt(padded_message)
    
        # Concatenate IV and encrypted message and encode with Base64
        encrypted_data = base64.urlsafe_b64encode(iv + encrypted_message).decode()
        return encrypted_data  
def aes_encrypt_json(json_value, key=AES256_SECRET_KEY):
    
    if json_value:
        message = json.dumps(json_value)
        
        return aes_encrypt(message, key=key)

def aes_decrypt(encrypted_data, key=AES256_SECRET_KEY):
    # Ensure the key is 32 bytes (256 bits) for AES-256
    #if len(key) != 32:
    #    raise ValueError("Key must be 32 bytes (256 bits) for AES-256.")

    key = base64.urlsafe_b64decode(key)

    # Verify the key length
    assert len(key) == 32, "Key must be 32 bytes for AES-256."

    encrypted_data_bytes = base64.urlsafe_b64decode(encrypted_data)

    # Generate a random 16-byte IV
    iv = encrypted_data_bytes[:16]
    ciphertext = encrypted_data_bytes[16:]

    # Initialize AES cipher for decryption in CBC mode
    cipher = AES.new(key, AES.MODE_CBC, iv)

    # Decrypt and unpad the message
    decrypted_padded_message = cipher.decrypt(ciphertext)
    decrypted_message = unpad(decrypted_padded_message, AES.block_size)

    return decrypted_message.decode() 
    
def aes_decrypt_json(encrypted_data, key=AES256_SECRET_KEY):
    return json.loads(aes_decrypt(encrypted_data, key=key))    
    
def decrypt(value, fernet_key=CRYPTO_SECRET_KEY):
    if value:
        value = str.encode(value)
            
        f = Fernet(fernet_key)
        return f.decrypt(value).decode('utf-8')
    
def decrypt_json(value, fernet_key=CRYPTO_SECRET_KEY):
    json_value_in_str = decrypt(value, fernet_key=fernet_key)
    if json_value_in_str:
        return json.loads(json_value_in_str) 
    
def generate_aes_256_keys(num_keys=1, bytes_count=32):
    keys = []
    for _ in range(num_keys):
        # Generate a 32-byte (256-bit) key
        key = secrets.token_bytes(bytes_count)
        # Optionally encode the key in Base64 for easy sharing
        encoded_key = base64.urlsafe_b64encode(key).decode()
        keys.append(encoded_key)
    return keys        
