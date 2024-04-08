from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import rsa, padding

# Generate a public/private key pair
def generate_key_pair():
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
        backend=default_backend()
    )
    public_key = private_key.public_key()
    return private_key, public_key

# Encrypt data with a public key
def encrypt_data(public_key, data):
    encrypted_data = public_key.encrypt(
        data,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )
    return encrypted_data

# Decrypt data with a private key
def decrypt_data(private_key, encrypted_data):
    decrypted_data = private_key.decrypt(
        encrypted_data,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )
    return decrypted_data

# Example usage
def main():
    # Generate key pair
    private_key, public_key = generate_key_pair()

    # Data to be encrypted
    original_data = b"Hello, World!"

    # Encrypt data with public key
    encrypted_data = encrypt_data(public_key, original_data)

    # Decrypt data with private key
    decrypted_data = decrypt_data(private_key, encrypted_data)

    # Ensure decryption worked correctly
    assert decrypted_data == original_data

    print("Original data:", original_data)
    print("Encrypted data:", encrypted_data)
    print("Decrypted data:", decrypted_data.decode('utf-8'))

if __name__ == "__main__":
    main()