import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import time

while True:
    try:
        # чтение данных
        df = pd.read_csv("C:/Users/Asus/Desktop/PP/microservice_architecture/logs/metric_log.csv", header=None)
        
        # Печать первых строк данных для диагностики
        print(f"Первыe строки данных:\n{df.head()}")
        
        
        df['absolute_error'] = df.iloc[:, 3]
        
        # Построение гистограммы и кривой плотности
        plt.figure(figsize=(10, 6))
        
        # Гистограмма
        plt.hist(df['absolute_error'], bins=20, color='skyblue', edgecolor='black', density=True, alpha=0.6)
        
        # Кривая плотности
        sns.kdeplot(df['absolute_error'], color='red', lw=2) 
        
        plt.title('Распределение абсолютных ошибок с кривой плотности')
        plt.xlabel('Абсолютная ошибка')
        plt.ylabel('Плотность')
        
        # Сохранение графика
        plt.savefig("C:/Users/Asus/Desktop/PP/microservice_architecture/logs/error_distribution.png")
        plt.close()
        
        #задержка перед следующим обновлением
        time.sleep(10)
    except Exception as e:
        print(f"Ошибка при построении гистограммы: {e}")
        time.sleep(10)  # задержка при ошибке
