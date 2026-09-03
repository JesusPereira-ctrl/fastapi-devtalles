# my_list = [1, 2, 3, 4, 5]
# addition = 0

# for number in my_list:
#     print(number)
#     addition += number

# print(addition)

for index, number in enumerate(list(range(100))):
    print(index, number * 2)
