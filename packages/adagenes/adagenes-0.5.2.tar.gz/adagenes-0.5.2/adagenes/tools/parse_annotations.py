

def get_max_value(score, get_max = True):
    values = score.split(";")
    score_max = 0.0
    # score_max = ""
    for val in values:
        if (val != "") and (val != "."):
            if is_numeric_score(val) is True:
                if isinstance(score, str):
                    score_max = float(val)
                else:
                    if get_max is True:
                        if float(val) > score_max:
                            score_max = float(val)
                    else:
                        if float(val) < score_max:
                            score_max = float(val)
            else:
                pass
                #return val
        else:
            print("null value: ",score)
    return score_max

def is_numeric_score(inputString):
    if isinstance(inputString,str):
        return any(char.isdigit() for char in inputString)
    elif isinstance(inputString,float):
        return True

