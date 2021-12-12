from django import template
register = template.Library()

@register.filter(name='pet_exists')
def pet_exists(pet_list, index):
    index -= 1  # 引数indexは1-31の日付なので、pet_list.indexとしてはマイナス1
    if pet_list[index] == None:
        return False
    else:
        return True

@register.filter(name='get_pet_picture_url')
def get_pet_picture_url(pet_list, index):
    index -= 1  # 引数indexは1-31の日付なので、pet_list.indexとしてはマイナス1
    if pet_list[index]:
        if pet_list[index].picture:
            return pet_list[index].picture.url
    return None

@register.filter(name='get_pet_count')
def get_pet_count(pet_count_list, index):
    index -= 1  # 引数indexは1-31の日付なので、pet_list.indexとしてはマイナス1
    if pet_count_list[index]:
        return pet_count_list[index]
    return None
