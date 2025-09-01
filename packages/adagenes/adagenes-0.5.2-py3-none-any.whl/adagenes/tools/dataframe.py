import pandas as pd
import adagenes


#def load_file_as_df()

def as_dataframe(bframe, features:list=None):
    """
    Returns a biomarker frame as a Pandas dataframe

    :param adagenes.BiomarkerFrame bframe: Biomarker frame object
    :param list features
    :return: Pandas dataframe containing biomarker frame data
    """
    index = []

    if features is None:
        features = []
        for var in bframe.data:
            for feature in bframe.data[var].keys():
                if (isinstance(bframe.data[var][feature], str)):
                    if feature not in features:
                        features.append(feature)

    data = {}
    for feature in features:
        data[feature] = []

    for var in bframe.data.keys():
        for feature in features:
            if feature in bframe.data[var]:
                data[feature].append(bframe.data[var][feature])
            else:
                data[feature].append("")
        index.append(var)

    print(data)
    print(index)
    print(features)
    df = pd.DataFrame(data=data, index=index,columns=features)
    return df
