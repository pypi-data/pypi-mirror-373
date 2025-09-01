'''
Created on 3 Sep 2020

@author: jacklok
'''


from datetime import date

age_groups=[
    [0,19],
    [20,29],
    [30,39],
    [40,49],
    [50,59],
    [60,69],
    [70,79],
    [80,100]
]

def calculate_age(born):
    if born:
        today = date.today()
        return today.year - born.year - ((today.month, today.day) < (born.month, born.day))
    else:
        return None

def create_age_group_label(age_group):
    if isinstance(age_group, (tuple, list)) and len(age_group)>=2:
        return '%s-%s' % (age_group[0], age_group[1])
    return None

def create_age_group_label_from_birth_date(birth_date):
    if birth_date:
        age             = calculate_age(birth_date)
        age_group       = get_age_group(age)
        return create_age_group_label(age_group)
    else:
        return 'Unknown'

def get_age_group(age): 
    if age:
        for g in age_groups:
            age_floor      = g[0]
            age_ceiling    = g[1]
            if age>=age_floor and age<=age_ceiling:
                return g
    return None

def gender_label(gender):
    if 'm'==gender:
        return 'Male'
    elif 'f'==gender:
        return 'Female'
    else:
        return gender
