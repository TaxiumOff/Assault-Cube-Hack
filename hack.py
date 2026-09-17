import pymem

# init
pm = pymem.Pymem("ac_client.exe")

def shield_hack(num):
    # variables
    shield_address = 0x00861938

    # reading memory
    shield = pm.read_int(shield_address)
    print("Current shield :",shield)

    pm.write_int(shield_address, num)

def bullet_hack(num):
    """ 
    Increase the bullet number
    """
    # variables
    bullet_address = 0x0070D4F8

    # reading memory
    bullet = pm.read_int(bullet_address)
    print("Current bullet :",bullet)

    pm.write_int(bullet_address, num)
    
def health_hack(num):
    """ 
    Increase the health points
    """
    # variables
    health_address = 0x0070D4A4

    # reading memory
    health = pm.read_int(health_address)
    print("Current health :",health)

    pm.write_int(health_address, num)


while True:
    param = input("What do you want to modify ? (bullet:1 ; health:2 ; shield:3) : ")
    if param == "1":
        num = int(input("How many bullet do you want ?"))
        bullet_hack(num)
    elif param == "2":
        num = int(input("How many health points do you want ?"))
        health_hack(num)
    elif param == "3":
        num = int(input("How many health points do you want ?"))
        shield_hack(num)
    else:
        print("Error please retry")