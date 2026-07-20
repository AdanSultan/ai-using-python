# Loops : Do a task multiple times repeatingly 
# Also used for searching an element in the list 

# for i in range(3):
#     print("Learning python ")

# Print a sentence as  character by character 

# for sentence in "Iamlearningpython:":
#     print(sentence)

# i = 4
# rows = i
# cols = i
# matrix = []

# for i in range(rows):
#     row = []
#     for c in range(cols):
#         row.append(0)
#     matrix.append(row)   

# for row in matrix:       
#     print(' '.join(map(str, row)))

# While loop:

# count = 1 
# while(count <= 5):
#     print(count)
#     count += 1

# Nested Loop 

# A loop inside loop is known as nested loop 

# used for grid , pattern for matrix peration we used nested loops 

# for i in range(3):
#     print("Outer loop")
#     for j in range(3):
#         print("   Inner loop")

# How we iterate Loops over data strucures 
# string 

# count = 0
# for char in "banana":
#     if char == "a":
#         count += 1
# print("Total 'a' count is :", count)

# how to use loops on disctinaries 

student = { 'name':'Adan', 'age': 23 , 'grade': 'A'}

# for key in student:
#     # print(key) 
#     # print(student[key])
#     print(key,":" , student[key])


student_list = [
   {"name": "Ali", "Age": 23, "grade": "A"},
   { "name": "Hassan", "Age": 22, "grade": "B"}
]
for student in student_list:
    print(f"Name: { student.get('name', '' )} | Grade: {student.get('grade', '')}")


# Define & calling Functions 

# A function is a reusable block of code that perfoms a specific tasks 

def learn():
   print("Learning about functions ")
   sum = 1 + 3
   print(sum)
learn()


def Name(name):
   print("My name is :" , name)

Name('Ali')

Name('Sara ')

learn()