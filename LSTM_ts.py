class LSTM_TS(object):
  def __init__(self,y,window_size = 12):
    self.ts = y
    self.lb = window_size   

  def plot(self):
    plt.style.use('seaborn-notebook')
    plt.plot(self.ts,color='b',linewidth = 1)
    plt.ylabel('# Bikes')
    
  def create_LSTM_model(self,units = 64):
    
    self.model = Sequential()
    self.model.add(LSTM(units,input_shape = (self.lb,1)))
    self.model.add(Dense(1))
    
    self.model.compile(optimizer = 'adam', loss = 'mse')
  
  def __processData(self,data):
    
    X,y = [],[]
    
    for i in range(len(data) - self.lb -1):
      X.append(data[i:(i+self.lb)])
      y.append(data[(i+self.lb)])
      
    return np.array(X),np.array(y)
    
    
  def train_LSTM_model(self,epochs = 100):
    data = self.ts.values
    scl = MinMaxScaler()
    data = data.reshape(data.shape[0],1)
    data = scl.fit_transform(data)
    self.X, self.y = self.__processData(data)
    
    X_train, X_test = self.X[:int(self.X.shape[0]*0.75)], self.X[int(self.X.shape[0]*0.75):]
    y_train, y_test = self.y[:int(self.y.shape[0]*0.75)], self.y[int(self.y.shape[0]*0.75):]
    
    X_train = X_train.reshape((X_train.shape[0],X_train.shape[1],1))
    X_test = X_test.reshape((X_test.shape[0],X_test.shape[1],1))
    
    print("Start training LSTM model...")
    history = self.model.fit(X_train,y_train,epochs = epochs,verbose = 0, validation_data = (X_test,y_test), shuffle = False)
    print("Training process is done.")
    
    plt.style.use('seaborn-notebook')
    plt.figure(figsize = (16,10))
    plt.subplot(2,2,1)
    plt.plot(history.history['loss'], label = "Training Loss")
    plt.plot(history.history['val_loss'], label = "Validation_Loss")
    plt.xlabel('Epoch')
    plt.ylabel('Loss')
    plt.title("Loss function")
    plt.legend(loc='best')
    
    train_pred = self.model.predict(X_train)
    test_pred = self.model.predict(X_test)
    
    self.train_pred  = scl.inverse_transform(train_pred)
    self.test_pred = scl.inverse_transform(test_pred)
    self.y_train = scl.inverse_transform(y_train.reshape(-1,1))
    self.y_test = scl.inverse_transform(y_test.reshape(-1,1))
    
    train_rmse = np.round(np.sqrt(mean_squared_error(self.y_train,self.train_pred)),2)
    plt.subplot(2,2,2)
    plt.plot(self.y_train,color='k',label="original series")
    plt.plot(self.train_pred,color='r',label="predicted series")
    plt.title("Prediction of # Bikes on Training Set, RMSE = {}".format(train_rmse))
    plt.legend(loc='best')
    
    test_rmse = np.round(np.sqrt(mean_squared_error(self.y_test,self.test_pred)),2)
    plt.subplot(2,2,3)
    plt.plot(self.y_test,color='k',label="original series")
    plt.plot(self.test_pred,color='r',label="predicted series")
    plt.title("Prediction of # Bikes on Test Set, RMSE = {}".format(test_rmse))
    plt.legend(loc='best')
    

  def oos_forecast(self,start_at = 3000,future = 500):
    data = self.ts.values
    scl = MinMaxScaler()
    data = data.reshape(data.shape[0],1)
    data = scl.fit_transform(data)
    
    X1 = self.X[:start_at][-1]
   
    prediction = []
    
    for i in range(future): 
      pred = self.model.predict(X1.reshape(1,self.lb,1))
      X1 = np.concatenate((X1, pred), axis=None)[1:]
      X1 = X1.reshape(X1.shape[0],1)
      pred = scl.inverse_transform(pred.reshape(1,-1))
      prediction = np.concatenate((prediction, pred), axis=None)
      
    
    plt.style.use('seaborn-notebook') 
    plt.figure(figsize = (16,6))
    plt.plot(np.arange(0,(start_at+future),1),self.ts[:(start_at+future)], 'k.',label="Observations")
    plt.plot(np.arange(self.lb,start_at,1),self.train_pred[:(start_at-self.lb)],'b.',label = 'Prediction')
    plt.plot(np.arange(start_at,start_at+future,1),prediction, 'r.',label="Out of sampel forecast")
    plt.title("Out of Sample Forecast for {} hours by Trained Model".format(np.round((future*5)/60)))
    plt.ylabel('# Bikes')
    plt.legend(loc="best")