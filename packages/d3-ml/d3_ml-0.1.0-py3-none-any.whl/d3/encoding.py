from sklearn.preprocessing import LabelEncoder, OneHotEncoder

def encode_labels(series):
    le = LabelEncoder()
    return le.fit_transform(series)

def one_hot_encode(df, column):
    return pd.get_dummies(df, columns=[column])
