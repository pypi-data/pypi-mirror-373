# Todo: Remove all usages of this, because it's redundant
#   In python empty strings are already falsy
def str_not_empty(string: str) -> bool:
    if string:
        if string == "":
            return False
        else:
            return True
    return False

# Todo: If functions are correctly typed, this is redundant
def str_is_none_or_empty(string: str) -> bool:
    return not str_not_empty(string)
