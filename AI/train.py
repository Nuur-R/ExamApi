import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, LabelEncoder
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense
import joblib

def create_and_train_model(X_train, y_train_encoded, X_test, y_test_encoded):
    # Buat model
    model = Sequential()
    model.add(Dense(64, input_dim=X_train.shape[1], activation='relu'))
    model.add(Dense(32, activation='relu'))
    model.add(Dense(len(np.unique(y_train_encoded)), activation='softmax'))

    model.compile(optimizer='adam', loss='sparse_categorical_crossentropy', metrics=['accuracy'])

    # Latih model
    model.fit(X_train, y_train_encoded, epochs=50, batch_size=2, validation_data=(X_test, y_test_encoded))
    
    return model

# Baca data dari file CSV
data_df = pd.read_csv('sample.csv')

# Pisahkan data menjadi fitur (X) dan label (y)
X = data_df.drop('Bidang_Kemampuan', axis=1)
y = data_df['Bidang_Kemampuan']

# Normalisasi data
scaler = StandardScaler()
X_normalized = scaler.fit_transform(X)

# Inisialisasi LabelEncoder
label_encoder = LabelEncoder()

# Encode label pada data pelatihan
y_encoded = label_encoder.fit_transform(y)

# Pisahkan data menjadi data pelatihan dan pengujian
X_train, X_test, y_train_encoded, y_test_encoded = train_test_split(
    X_normalized,
    y_encoded,
    test_size=0.2, random_state=42
)

# Buat dan latih model
trained_model = create_and_train_model(X_train, y_train_encoded, X_test, y_test_encoded)

# Save scaler
scaler_filename = 'scaler.save'
joblib.dump(scaler, scaler_filename)

# Save label_encoder
label_encoder_filename = 'label_encoder.save'
joblib.dump(label_encoder, label_encoder_filename)

# Save the model to a file
model_filename = 'quiz_model.h5'
trained_model.save(model_filename)
