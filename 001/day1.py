# print("Day 1 of Again Learning Python ")
# print("Variables are containers in which we can store data just like box. Python sets data type automatically, like integer , float , string. It is an interpreter language ")

studentName = "Sohaib"
Age = 23
Location = "Taxila"
Expertise = "App & Web Developer"
is_passed = True
print(studentName,Age,Location,Expertise)
print("Types:", type(studentName), type(Age), type(Location), type(Expertise))
print()
# Variables Collection in Pythons 

# List : Data will be in order and will be change able 
# Allow duplicates

Fruits = ["Apple" , "Orange" , "Banana" , "Mango"]
print(Fruits)
print(Fruits[0])
print(Fruits[-2])
print()

# Metods in Lists 
# If we create a List and we want to add more items in it we use function such as append, it will add at the end of the list

Fruits.append("Peach")
print(Fruits)
print()

# Insert Function is used to add new value in list but at specific index, the index will be set by the user

Fruits.insert(2,"Mango") 
print(Fruits)
print()

# Pop function use if user want to remove the item in a List
#  it removes item from the last of the list
# If you want to remove specific item you have to tell the index   

Fruits.pop(2)
print(Fruits)
print()

# remove function: is used to remove specific item from the list 
# It takes atleast one argument which user want to remove 

Fruits.remove("Apple")
Fruits.remove("Orange")
Fruits[2] = "Banana" # We can change the List item 
print(Fruits)

print()

# Looping through List 

for fruit in Fruits:
 print(fruit)
 print()

# Similarly there are many pre define function in python lists 

# Tuple : Order Collection of list but it is immutable   

color = ('red' , 'white' , 'green')
print(color[0])

# color[0] = 'black' # It gives error we cannot change the item
# print(color)

# Methods in Tuples 
print()
numbers = ( 1 , 2 , 3 ,"4")
print(numbers.count("4")) # It will tells how many times that number appears in tuple
print()
print(numbers.index(3)) # It will tells us the index of the number or item 
print()
# Set Operations: Data is unordered but duplicates are not allowed in them 

A = {1 , 2 , 3, 3} # It only prints one time 3
print(A)

# Set Operations 
print()

B = {2 , 4 , 5 , 4 , 6}
C = {8 , 4 , 9 , 10}
print(B.union(C)) # Combine all don't repeat duplicates
print()
print(B.intersection(C)) # Takes only common
print()
print(B.difference(C)) # Take value which are in first element but not in second
print()

# Disctionary: Store key valuse pairs
# word with their meaning
# 

student = {
    "studentName" : "Yasir",
    "rollNo" : "66",
    "Location" : "Pindi"
} 
print(student)
print(student["studentName"])
print(student["Location"])
print()

# Methonds in Dictionary 
# We can change any key value here 

student["Location"] = "Lahore"
print(student)
print()

# student.clear() # remove all valuse in the disctionary 
# print(student)

# In loops we use key & value in disctionary to applly loop 

for key , value in student.items():
    print(key, ':' , value)
