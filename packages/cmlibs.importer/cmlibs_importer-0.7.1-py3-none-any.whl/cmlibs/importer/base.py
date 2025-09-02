import os.path


def valid(inputs, description):
    if type(inputs) == list:
        if type(inputs) != type(description):
            return False

        if len(inputs) != len(description):
            return False

        for index, input_ in enumerate(inputs):
            if "mimetype" in description[index]:
                if not os.path.isfile(input_):
                    return False
    else:
        if "mimetype" in description:
            if not os.path.isfile(inputs):
                return False

    return True
