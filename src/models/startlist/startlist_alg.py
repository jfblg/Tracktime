
def order_from_the_middle(data_list):
    list_length = len(data_list)
    if list_length % 2 == 0:
        new_index = get_index_even_count(list_length)
    else:
        new_index = get_index_odd_count(list_length)

    new_order_data_list = []
    for index in new_index:
        new_order_data_list.append(data_list[index])

    return [data_list[index] for index in new_index]

def get_index_odd_count(length):

    new_index_list = []
    x = length - 1
    for index in range(0, length):

        new_index_list.append(x)

        if x == 0:
            x += 1
        elif x % 2 == 0:
            x -= 2
        else:
            x += 2

    return new_index_list


def get_index_even_count(length):

    new_index_list = []
    x = length

    for index in range(0, length):

        if x == 0:
            x += 1
        elif x % 2 == 0:
            x -= 2
        else:
            x += 2

        new_index_list.append(x)

    return new_index_list