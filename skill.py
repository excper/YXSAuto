class Skill:
    def __init__(self, skill_name):
        self.name = skill_name
        self.type = skill_name.value[1]
        self.useful = True

    def __repr__(self):
        return self.name.value[0].__repr__()

    def __str__(self):
        return self.name.value[0].__str__()