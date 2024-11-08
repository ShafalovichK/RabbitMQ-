import pika
import json
import logging

#Инициализация логирования
logging.basicConfig(filename='C:/Users/Asus/Desktop/PP/microservice_architecture/logs/metric_log.log', level=logging.DEBUG)

data = {}

def log_error_to_csv(message_id, y_true, y_pred, error):
    try:
        with open("C:/Users/Asus/Desktop/PP/microservice_architecture/logs/metric_log.csv", mode='a', encoding='utf-8') as file:
            file.write(f"{message_id},{y_true},{y_pred},{error}\n")
            logging.info(f"Записана абсолютная ошибка для id {message_id}: {error}")
    except Exception as e:
        logging.error(f"Ошибка при записи в файл: {e}")

def process_message(ch, method, properties, body):
    global data
    try:
        message = json.loads(body)
        message_id = message.get('id')
        
        if not message_id:
            logging.warning(f"Сообщение не содержит идентификатор id: {message}")
            return
        
        # Используем 'prediction', если 'body' не найден
        if 'body' in message:
            value = message['body']
        elif 'prediction' in message:
            value = message['prediction']
        else:
            logging.warning(f"Сообщение не содержит ключи 'body' или 'prediction': {message}")
            return
        
        # Обработка значений в зависимости от routing_key
        if method.routing_key == 'y_true':
            data[message_id] = data.get(message_id, {})
            data[message_id]['y_true'] = value
        elif method.routing_key == 'y_pred':
            data[message_id] = data.get(message_id, {})
            data[message_id]['y_pred'] = value

        # Если присутствуют обе метки, считаем ошибку
        if 'y_true' in data[message_id] and 'y_pred' in data[message_id]:
            y_true = data[message_id]['y_true']
            y_pred = data[message_id]['y_pred']
            error = abs(y_true - y_pred)
            log_error_to_csv(message_id, y_true, y_pred, error)
            del data[message_id]
    
    except json.JSONDecodeError as e:
        logging.error(f"Ошибка декодирования JSON: {e}")
    except Exception as e:
        logging.error(f"Произошла ошибка при обработке сообщения: {e}")

# Подключение к RabbitMQ и обработка сообщений
connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
channel = connection.channel()

channel.queue_declare(queue='y_true')
channel.queue_declare(queue='y_pred')

channel.basic_consume(queue='y_true', on_message_callback=process_message, auto_ack=True)
channel.basic_consume(queue='y_pred', on_message_callback=process_message, auto_ack=True)

print('...Ожидание сообщений')
channel.start_consuming()
