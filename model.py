import pika
import pickle
import numpy as np
import json
import traceback
import uuid  

# путь к файлу
MODEL_PATH = 'C:/Users/Asus/Desktop/PP/microservice_architecture/model/src/myfile.pkl'

# Читаем файл с сериализованной моделью
try:
    with open(MODEL_PATH, 'rb') as pkl_file:
        regressor = pickle.load(pkl_file)
except FileNotFoundError:
    print(f"Файл {MODEL_PATH} не найден. Проверьте путь и наличие файла.")
    exit(1)
except Exception as e:
    print(f"Ошибка при загрузке модели: {e}")
    traceback.print_exc()
    exit(1)

try:
    # Создаем подключение по адресу RabbitMQ
    connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
    channel = connection.channel()

    # Объявляем очередь features
    channel.queue_declare(queue='features')
    # Объявляем очередь y_pred
    channel.queue_declare(queue='y_pred')

    # Создаем функцию callback для обработки данных из очереди
    def callback(ch, method, properties, body):
        try:
            print(f'Получен вектор признаков: {body}')
            # Загружаем сообщение и извлекаем ID и признаки
            message = json.loads(body)
            message_id = message.get("id")
            features = message.get("body", [])

            # Выполняем предсказание на основе полученных признаков
            pred = regressor.predict(np.array(features).reshape(1, -1))

            # Формируем сообщение с предсказанием и ID
            prediction_message = {
                "id": message_id,
                "prediction": pred[0]
            }

            # Отправляем результат в очередь y_pred
            channel.basic_publish(exchange='',
                                  routing_key='y_pred',
                                  body=json.dumps(prediction_message))
            print(f'Предсказание {pred[0]} с ID {message_id} отправлено в очередь y_pred')
        except Exception as e:
            print(f"Ошибка при обработке сообщения: {e}")
            traceback.print_exc()

    # Извлекаем сообщение из очереди features
    channel.basic_consume(
        queue='features',
        on_message_callback=callback,
        auto_ack=True
    )
    print('...Ожидание сообщений, для выхода нажмите CTRL+C')

    # Запускаем режим ожидания сообщений
    channel.start_consuming()

except pika.exceptions.AMQPConnectionError:
    print('Не удалось подключиться к серверу RabbitMQ. Проверьте, что он запущен.')
except Exception as e:
    print(f"Не удалось подключиться к очереди: {e}")
    traceback.print_exc()
