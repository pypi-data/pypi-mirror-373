class Person:
    def __init__(self, name, age, uni, living_place, working):
        self.name = name
        self.age = age
        self.uni = uni
        self.living_place = living_place
        self.linkedin = "https://www.linkedin.com/in/edwardkao6413/"
        self.working = working

    def update_info(self):
        print("Hello, I am {}. I am {} yrs old, and have been graduated from {}. Currently, I live in {}, and my linkedin is {}, working in {}.".format(self.name, self.age, self.uni, self.living_place, self.linkedin, self.working))

