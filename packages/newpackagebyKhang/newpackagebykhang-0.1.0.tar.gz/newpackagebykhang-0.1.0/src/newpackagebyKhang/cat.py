class Dog:
    def __init__(self, name, age):
        self.__name = name
        self.__age = age
    def describe(self):
        print(f"{self.__name}, age: {self.__age}")
