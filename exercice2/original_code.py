class Tank:
    def __init__(self, armor, penetration, armor_type):
        self.armor = armor
        self.penetration = penetration
        self.armor_type = armor_type
        if not (armor_type == 'chobham' or armor_type == 'composite' or armor_type == 'ceramic'):
            raise Exception('Invalid armor type %s' % (armor_type))
        self.tank = "Tank"

    def set_name(self, name):
        self.name = name

    def vulnerable(self, tank):
        real_armor = self.armor
        if self.armor_type == 'chobham':
            real_armor += 100
        elif self.armor_type == 'composite':
            real_armor += 50
        elif self.armor_type == 'ceramic':
            real_armor += 50
        if real_armor <= tank.penetration: return True
        return False

    def swap_armor(self, othertank):
        tmp = othertank.armor
        othertank.armor = self.armor
        self.armor = tmp
        return othertank

    def __repr__(self):
        tmp = self.name.lower()
        tmp = self.name.replace(' ', '-')
        return tmp


m1_1 = Tank(600, 670, 'chobham')
m1_2 = Tank(620, 670, 'chobham')
if m1_1.vulnerable(m1_2) is True:
    print('Vulnerable to self')
m1_1.swap_armor(m1_2)
tanks = []
for i in range(5):
    tanks.append(Tank(400, 400, 'steel'))
index = 0
for tank in tanks:
    tank.set_name('Tank' + str(index) + "_Small")
    index += 1
test = []
index = 0
while index < len(tanks):
    test.append(tanks[i].vulnerable(m1_1))


def test_tank_safe(shooter, test_vehicles=[]):
    at_least_one_safe = False
    for t in test:
        if t:
            at_least_one_safe = True
    if at_least_one_safe:
        print("A tank is safe")
    else:
        print("No tank is safe")


test_tank_safe(m1_1, tanks)