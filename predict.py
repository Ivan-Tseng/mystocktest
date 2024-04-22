
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.preprocessing import MinMaxScaler
from keras.models import Sequential
from keras.layers import LSTM, Dense, Dropout
from twstock import Stock
import datetime
import yfinance as yf


# Load data 這裡使用了 yfinance 函式庫下載了股票的收盤價格和成交量數據。(Yfinance)
dflstm = yf.download("2449.TW", start="1993-06-15", end=datetime.date.today())
price_data = dflstm["Close"].values
volume_data = dflstm["Volume"].values

# stock = Stock('2330')
# dflstm = stock
# price_data = dflstm["close"].values
# volume_data = dflstm["transaction"].values


# stock = Stock(stock_cannt_read)
# data2 = stock.fetch_from(2002,1)
# df2 = pd.DataFrame(data2)


# Feature Scaling 使用 MinMaxScaler 對價格和成交量數據進行特徵縮放，將它們縮放到 [0, 1] 的範圍內
sc_price = MinMaxScaler(feature_range=(0, 1))
sc_volume = MinMaxScaler(feature_range=(0, 1))
scaled_price = sc_price.fit_transform(price_data.reshape(-1, 1))
scaled_volume = sc_volume.fit_transform(volume_data.reshape(-1, 1))

# Combine price and volume data 將經過特徵縮放的價格和成交量數據組合成一個特徵數組
scaled_features = np.concatenate((scaled_price, scaled_volume), axis=1)

# Create training data 創建用於訓練 LSTM 模型的數據集，將最近60天的價格和成交量數據作為特徵，並將下一天的價格作為目標。
X_train = []
y_train = []
for i in range(60, len(scaled_features)):
    X_train.append(scaled_features[i-60:i, :])  # Use the last 60 days' price and volume data
    y_train.append(scaled_price[i, 0])  # Predict the next day's price
X_train, y_train = np.array(X_train), np.array(y_train)

# Build the LSTM model 構建了一個包含多層 LSTM 層和 Dropout 層的序列模型
regressor = Sequential()
regressor.add(LSTM(units=50, return_sequences=True, input_shape=(X_train.shape[1], X_train.shape[2])))
regressor.add(Dropout(0.2))
regressor.add(LSTM(units=50, return_sequences=True))
regressor.add(Dropout(0.2))
regressor.add(LSTM(units=50, return_sequences=True))
regressor.add(Dropout(0.2))
regressor.add(LSTM(units=50))
regressor.add(Dropout(0.2))
regressor.add(Dense(units=1))

# Compile the model 使用 Adam 優化器編譯模型，並使用均方誤差作為損失函數。
regressor.compile(optimizer='adam', loss='mean_squared_error')

# Train the model 對模型進行訓練，訓練過程中使用了 3 個 epochs 和批量大小為 32
regressor.fit(X_train, y_train, epochs=100, batch_size=32)

# Prepare test data  準備測試數據：
real_stock_price = dflstm["Close"].values.reshape(-1, 1)
real_volume = dflstm["Volume"].values.reshape(-1, 1)
scaled_real_price = sc_price.transform(real_stock_price)
scaled_real_volume = sc_volume.transform(real_volume)
scaled_real_features = np.concatenate((scaled_real_price, scaled_real_volume), axis=1)
X_test = []
for i in range(60, len(scaled_real_features)):
    X_test.append(scaled_real_features[i-60:i, :])
X_test = np.array(X_test)

# Predictions 進行預測： 使用訓練好的模型對測試集進行預測，並使用逆轉換將預測值轉換為原始股價。
predicted_stock_price = regressor.predict(X_test)
predicted_stock_price = sc_price.inverse_transform(predicted_stock_price)

# Visualize the results 可視化結果：使用 Matplotlib 可視化真實股價和預測股價。
plt.plot(real_stock_price[60:], color='red', label='Real Stock Price')
plt.plot(predicted_stock_price, color='blue', label='Predicted Stock Price')
plt.title('Stock Price Prediction')
plt.xlabel('Time')
plt.ylabel('Stock Price')
plt.legend()
plt.show()
