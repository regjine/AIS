import bcrypt
my_password = "secret4901"
password_bytes = my_password.encode('utf-8')
hashed = bcrypt.hashpw(password_bytes, bcrypt.gensalt())

print("\nHashed password:")
print(hashed.decode('utf-8'))
print()