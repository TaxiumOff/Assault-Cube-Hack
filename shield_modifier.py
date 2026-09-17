import pymem

# init
pm = pymem.Pymem("ac_client.exe")

# variables
shield_address = 0x00861938

# reading memory
shield = pm.read_int(shield_address)
print("Current shield :",shield)

shield_num = int(input("How many shield you want ? "))
pm.write_int(shield_address, shield_num)