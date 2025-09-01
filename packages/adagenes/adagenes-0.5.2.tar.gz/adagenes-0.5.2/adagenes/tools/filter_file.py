import adagenes as ag


def get_magic_filter_object(filter_model):
    if "=" in filter_model:
        sep = "="
    elif ">" in filter_model:
        sep = ">"
        is_numeric = True
        magic_obj = ag.NumberFilter()
    elif "<" in filter_model:
        sep = "<"
        is_numeric = True
        magic_obj = ag.NumberFilter()
    elements = filter_model.split(sep)
    if len(elements) > 1:
        feature = elements[0]
        value = elements[1]

        # get filter object
        if is_numeric is False:
            try:
                value = float(value)
                is_numeric = True
                magic_obj = ag.NumberFilter()
            except:
                magic_obj = ag.TextFilter()
    return magic_obj

def filter_file(filter_model, infile, outfile):
    """

    :param filter_model:
    :param infile:
    :param outfile:
    :return:
    """
    is_numeric = False
    #if "AND" in filter_model:
    #    elements = filter_model.split("AND")
    #    if len(elements) > 1:
    #        model1 = elements[0]
    #        magic_obj1 = get_magic_filter_object(model1)
    #        model2 = elements[1]
    #        magic_obj2 = get_magic_filter_object(model2)
    #elif "OR" in filter_model:
    #    pass
    #else:
    #    magic_obj = get_magic_filter_object(filter_model)
    magic_obj = ag.NumberAndTextFilter(filter=filter_model)

    ag.process_file(infile, outfile, magic_obj)


