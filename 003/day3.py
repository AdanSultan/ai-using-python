# Loops : Do a task multiple times repeatingly 
# Also used for searching an element in the list 

# for i in range(3):
#     print("Learning python ")

# Print a sentence as  character by character 

# for sentence in "Iamlearningpython:":
#     print(sentence)

i = 4
rows = i
cols = i
matrix = []

for i in range(rows):
    row = []
    for c in range(cols):
        row.append(0)
    matrix.append(row)   

for row in matrix:       
    print(''.join(map(str, row)))

# While loop:

count = 1 
while(count <= 5):
    print(count)
    count += 1