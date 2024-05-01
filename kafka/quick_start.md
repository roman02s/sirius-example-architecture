
Список топиков:
```bash
kafka-topics --list --bootstrap-server localhost:29092
```
****


Создание топика:
```bash
kafka-topics --create --topic user-inputs --bootstrap-server localhost:29092
kafka-topics --create --topic assistant-responses --bootstrap-server localhost:29092

```

Вход в producer консоль топика, из которой можно добавить новые записи в топик:
```bash
kafka-console-consumer --topic user-inputs --bootstrap-server localhost:29092
kafka-console-consumer --topic assistant-responses --bootstrap-server localhost:29092
```
