# Implementação da atividade 02 de Aplicações de Algoritmos de Aprendizado de Máquina.

from statsmodels.tsa.ar_model import AR
from statsmodels.tsa.stattools import acf

from sklearn import linear_model

from statsmodels.tsa.seasonal import seasonal_decompose
from sklearn.metrics import mean_squared_error

import argparse
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt


# Instancia o parser.
parser = argparse.ArgumentParser(description='Ferramenta de regressão.', formatter_class=argparse.RawTextHelpFormatter)

# Argumento para o arquivo de entrada.
parser.add_argument('--input', required=True, type=str,
                    help='Uma string que representa um .csv que contém os dados S&P500 para uma ação.')

# Argumento para o arquivo de entrada.
parser.add_argument('--from_index', type=int, default=0,
                    help='Índice do dataset que representa desde onde vai a predição.')

# Argumento para o arquivo de entrada.
parser.add_argument('--to_index', type=int,
                    help='Índice do dataset que representa até onde vai a predição.')

# Argumento para o arquivo de entrada.
parser.add_argument('--field', type=str, default='open',
                    help='Uma string que representa para qual campo se quer a regressão.')

# Argumento para o arquivo de entrada.
parser.add_argument('--window', type=int, default=20,
                    help='um valor inteiro que representa o tamanho da janela que será utilizada para o treinamento'
                         'na predição.')

# Argumento para o arquivo de entrada.
parser.add_argument('--steps', type=int, default=5,
                    help='um valor inteiro que representa o número de passos futuros que serão previstos.')

# Argumento para o arquivo de entrada.
parser.add_argument('--model', type=str, default=5,
                    help='uma string que representa quais modelos serão avaliados, A para AR e L para LR.')

args = parser.parse_args()

# Carrega o arquivo .csv em um dataframe do pandas.
df = pd.read_csv(args.input).dropna()
print('dataframe with ', len(df), ' rows loaded.')
# Seta onde começa a predição.
from_index = args.from_index
# Seta até onde vai a predição.
if(args.to_index):
    to_index = args.to_index
else:
    to_index = len(df)
# Seta o nome do campo que será utilizado na regressão.
field = args.field
# Seta o tamanho das janelas que será utilizada na regressão.
window_size = args.window
# Seta o tamanho do passo que será predito.
step_size = args.steps
# Recupera a série do dataframe de acordo com o nome fornecido como argumento.
series = df[from_index:to_index][field]

all_fields = ['open','volume', 'high', 'low', 'close']

fields_LR_train = all_fields.copy()

fields_LR_train.remove(str(field))

print(fields_LR_train)

seriesLR_train = df[from_index:to_index][fields_LR_train]
seriesLR_test = df[from_index:to_index][str(field)]

# Arrays que armazenam os valores reais e preditos.
y = [None] * (len(series) - window_size)
predicted = [None] * (len(series) - window_size)
predictedLR = [None] * 1300#[None] * (len(series) - window_size)

for i in range(0, (len(series) - window_size), step_size):
    # Recupera uma fatia da série temporal de acordo com o tamanho da janela.
    train_series = series[i:(i + window_size)].values
    
    if 'a' in args.model or 'A' in args.model:
        # Cria um modelo de autoregressão.    
        model = AR(train_series).fit()
        # Prediz os step_size passos na série temporal.
        prediction = model.predict(start=len(train_series), end=(len(train_series) + step_size - 1), dynamic=False)
        # Armazena o valor predito.
        predicted[i:(i + step_size)] = prediction
        
    if 'l' in args.model or 'L' in args.model: 
                
        trainLR = seriesLR_train[i:(i + window_size)].values
        testLR = seriesLR_test[i:(i + window_size)].values
        
        # Cria um modelo de regressão linear.    
        modelLR = linear_model.LinearRegression()
        modelLR.fit(trainLR, testLR)
        
        for k in range(i, i+step_size):
        
            # Prediz os step_size passos na série temporal.
            prediction = modelLR.predict(seriesLR_train[k:k+1].values)
            # Armazena o valor predito.
            predictedLR[k] = prediction

#print(predicted, predictedLR)

y = series[window_size:]
if 'a' in args.model or 'A' in args.model:
    predicted = predicted[:len(y)]
    # Calcula o erro quadrático médio.
    errorAR = mean_squared_error(y.values, predicted)
    # Plota o gráfico diferenciando os valores reais e os valores preditos.
    plt.subplot(2, 1, 1)
    plt.plot(range(len(predicted)), predicted, label='predicted AR')
if 'l' in args.model or 'L' in args.model: 
    predictedLR = predictedLR[:len(y)]
    # Calcula o erro quadrático médio.
    errorLR = mean_squared_error(y.values, predictedLR)
    # Plota o gráfico diferenciando os valores reais e os valores preditos.
    plt.subplot(2, 1, 1)
    plt.plot(range(len(predictedLR)), predictedLR, label='predicted LR')
    
plt.plot(range(len(y)), y, label='y')
plt.legend()
plt.title("Resultados de Regressão para " + (args.input.split('/')[1].split('.')[0]))
plt.xlabel("day")
plt.ylabel("open")

texttitle = 'Erros para ' + (args.input.split('/')[1].split('.')[0]) + ': '

# Plota o gráfico do erro quadratico para cada ponto.
plt.subplot(2, 1, 2)
if 'a' in args.model or 'A' in args.model:
    errorsAR = list(map(lambda x, y: (x - y) * (x - y), y, predicted))

    plt.plot(range(len(errorsAR)), errorsAR, label='erro AR')
    texttitle += 'AR = ' + str(errorAR) + ' '

    
if 'l' in args.model or 'L' in args.model: 
    errorsLR = list(map(lambda x, y: (x - y) * (x - y), y, predictedLR))

    plt.plot(range(len(errorsLR)), errorsLR, label='erro LR')
    
    texttitle += 'LR = ' + str(errorLR) + ' '
#plt.title("Erros de AR para " + (args.input.split('/')[1].split('.')[0]) +
#          " (erro quadrático médio: " + str(errorAR) + ")")

plt.title(texttitle)    
    
plt.legend()
plt.xlabel("day")
plt.ylabel("erro")

plt.show()


# series = pd.Series.from_csv('atividade02/input/NVDA.csv', header=0).dropna()
# series.index = pd.DatetimeIndex(freq='B', start=0, periods=1260)
# result = seasonal_decompose(series, model='multiplicative')
# series.index = pd.DatetimeIndex(freq='B', start=from_index, periods=(to_index - from_index))
# result = seasonal_decompose(series, model='multiplicative')
# print(result.trend)
# print(result.seasonal)
# print(result.resid)
# print(result.observed)
# result.plot()
# plt.show()


#python main.py --input 'input/NVDA.csv' --from_index 0 --to_index 200 --window 10 --step 5 --model l
