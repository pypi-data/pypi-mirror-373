def train_test_split(df, target, test_size=0.2):
    from sklearn.model_selection import train_test_split
    X = df.drop(target, axis=1)
    y = df[target]
    return train_test_split(X, y, test_size=test_size, random_state=42)
