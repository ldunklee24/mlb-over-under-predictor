import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
import joblib

def train_model():
    df = pd.read_csv('games.csv')

    # Target: Over/Under based on betting line
    df['label'] = (df['actual_total_runs'] > df['betting_line']).astype(int)

    features = ['home_runs', 'away_runs', 'home_era', 'away_era', 'betting_line']
    X = df[features]
    y = df['label']

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)
    acc = accuracy_score(y_test, y_pred)
    print(f"Model Accuracy: {acc:.2f}")

    # Save model
    joblib.dump(model, 'model.pkl')

if __name__ == "__main__":
    train_model()
