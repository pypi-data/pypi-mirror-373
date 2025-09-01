
def casting(origin, target):
    if type(origin) != type(target):
        return type(origin)(target)
    else:
        return target
