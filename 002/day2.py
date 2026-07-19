# Type Casting & Input Functions 
# Means changing the type of a variable & input enter by the user 

# age = "34"
# print(type(age))
# age = int(age)
# age = age + 1
# print(age)
# # age = age+1
# print(type(age))


# Input Function how can input enter by the user 

# age = input("Please write your age : ")

# Input always enter in the string format 

# myage = int(age) # You can change the type of the string 


# age1 = int(input("Enter your age : "))
# print(type(age1))


# Variables operators and what operations we apply on it 

# Operators 2 types
# Unary & Binary 

# Operators: + , - , * , / , 
# // for floor divide
print(17 // 3)
print(15/5)

# % remainder operator 
# ** power operator

print(11 % 3)
print(2**3)


# Comparison Operators : Get answer as true or false 
# == equal operator
# != not equal operator
# > greater then 
# < less then 
# >= 
# <=


# Conditional Statements 


# temp = int(input("Enter Temperature: "))
# if temp >= 35:
#     print("It is hot weather")
# else:
#     print("It is not a hot weather ")

marks = int(input("Enter your marks :"))
if marks >= 95:
    print("Your grade is A")
elif marks >= 85 and marks < 95:
    print("Your grade is B")
elif marks >= 75 and marks < 85:
    print("Your grade is B-")
elif marks >= 65 and marks < 75:
    print("Your grade is C")
elif marks >= 55 and marks < 65:
    print("Your grade is D")
else:
    print("You are fail")