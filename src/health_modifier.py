import pymem


# init
pm = pymem.Pymem("ac_client.exe")

# variables
# Don't forget to change the value
health_address = 0x0070D4A4

# reading memory
health = pm.read_int(health_address)
print("Current health :",health)

health_num = int(input("How many health you want ? "))
pm.write_int(health_address, health_num)