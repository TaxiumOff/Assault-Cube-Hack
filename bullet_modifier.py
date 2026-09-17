import pymem

# init
pm = pymem.Pymem("ac_client.exe")

# variables
bullet_address = 0x0070D4F8

# reading memory
bullet = pm.read_int(bullet_address)
print("Current bullet :",bullet)

bullet_num = int(input("How many bullet you want ? "))
pm.write_int(bullet_address, bullet_num)