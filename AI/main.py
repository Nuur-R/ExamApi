import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, LabelEncoder
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense

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

# Encode label pada data pelatihan dan pengujian
y_encoded = label_encoder.fit_transform(y)

# Pisahkan data menjadi data pelatihan dan pengujian
X_train, X_test, y_train_encoded, y_test_encoded = train_test_split(
    X_normalized,
    y_encoded,
    test_size=0.2, random_state=42
)

# Buat model
model = Sequential()
model.add(Dense(64, input_dim=X_train.shape[1], activation='relu'))
model.add(Dense(32, activation='relu'))
model.add(Dense(len(np.unique(y)), activation='softmax'))

model.compile(optimizer='adam', loss='sparse_categorical_crossentropy', metrics=['accuracy'])

# Latih model
model.fit(X_train, y_train_encoded, epochs=50, batch_size=2, validation_data=(X_test, y_test_encoded))

# Prediksi
new_input = np.array([[3,4,5,2,4,5,2,3]])
new_input_normalized = scaler.transform(new_input)
predictions = model.predict(new_input_normalized)
predicted_class_index = np.argmax(predictions, axis=1)
predicted_class = label_encoder.inverse_transform(predicted_class_index)[0]

print("Jenis Kecerdasan Prediksi:", predicted_class)
