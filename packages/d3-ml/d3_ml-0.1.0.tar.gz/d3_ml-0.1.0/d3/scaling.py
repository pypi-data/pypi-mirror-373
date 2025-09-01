from sklearn.preprocessing import StandardScaler, MinMaxScaler

def scale_standard(df):
    scaler = StandardScaler()
    return scaler.fit_transform(df)

def scale_minmax(df):
    scaler = MinMaxScaler()
    return scaler.fit_transform(df)
