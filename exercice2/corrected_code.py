class Tank:
    ARMOR_TYPES = {
        "chobham": 100,
        "composite": 50,
        "ceramic": 50,
        "steel": 0,
    }
    
    def __init__(self, armor, penetration, armor_type):
        self.armor = armor
        self.penetration = penetration
        self.armor_type = armor_type

        if armor_type not in self.ARMOR_TYPES:
            raise ValueError(f'Invalid armor type: {armor_type}, must be one of the following types: {", ".join(list(self.ARMOR_TYPES.keys()))}')
        
        self.name = "Tank"

    def set_name(self, name):
        self.name = name

    def vulnerable(self, tank):
        real_armor = self.armor
        real_armor += self.ARMOR_TYPES[self.armor_type]

        return real_armor <= tank.penetration
    
    def swap_armor(self, othertank):
        self.armor, othertank.armor = othertank.armor, self.armor
        return othertank
    
    def __repr__(self):
        return self.name.lower().replace(' ', '-')
    
m1_1 = Tank(600, 670, 'chobham')
m1_1.set_name("Abrams M1A1")
m1_2 = Tank(620, 670, 'chobham')
m1_2.set_name("Abrams M1A2")

if m1_1.vulnerable(m1_2):
    print(f"{m1_1} is vulnerable to {m1_2}")

m1_1.swap_armor(m1_2)

tanks = []
for i in range(5):
    tank = Tank(400, 400, 'steel')
    tanks.append(tank)

for index, tank in enumerate(tanks):
    tank.set_name('Tank' + str(index) + "_Small")

test = []
for tank in tanks:
    test.append(tank.vulnerable(m1_1))

def test_tank_safe(shooter, test_vehicles=None):
    if test_vehicles is None:
        test_vehicles = []

    safe_tanks = []
    for tank in test_vehicles:
        safe_tanks.append(not tank.vulnerable(shooter))

    if any(safe_tanks):
        print("At least one tank is safe")
    else:
        print("No tank is safe")

test_tank_safe(m1_1, tanks)