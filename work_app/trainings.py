from .models import Word


def get_phrasal_verbs_set():
    selected_verbs = Word.objects.filter(mark = "Phrasal verb").values();
    new_array = []
    for verb in selected_verbs:
        splitted_verb = verb.split(" ",1)
        new_array.append(splitted_verb)
    arr_no_duplicates = delete_doubles_from_array(new_array)
    return arr_no_duplicates




def delete_doubles_from_array(my_list):
    my_list.sort()
    total_list = []
    if len(my_list) == 0:
        return total_list
    indexes = [0]
    cur_elem = my_list[0]
    for x in range(1,len(my_list)):
        if my_list[x] == cur_elem:
            continue
        else:
            cur_elem = my_list[x]
            indexes.append(x)
    for x in indexes:
        total_list.append(my_list[x])
    return total_list