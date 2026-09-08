# 1- Create List of 5 numbers and add one more number

numbers = [1, 2, 3 , 4 , 5 ]
print(numbers)
print()
numbers.append(6)
print(numbers)
print()

# 2 Create a tuple of 3 cities and print second city

cities = ("Chakwal" , "Karachi" , "Lahore" )
print(cities[1])
print()

# 3 Create two sets and find their intersection 

setA = {1 , 2 , 3 , 4 , 5}
setB = {3, 2 , 8, 12, 18}
print(setA.intersection(setB))

# 4 Create a Disctionary of your own details and print all keys 

ownStory = {
    "name" : "Ali",
    "rollNo": "22-CE-99",
    "department" : "Computer Engineering",
    "City": "Lahore"
}

print(ownStory)