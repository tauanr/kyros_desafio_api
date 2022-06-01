Necessario docker e docker-compose

Para rodar basta docker-compose up


Existem 3 endpoints (/adduser, /login, /data) que pode ser testados com os seguintes comandos:

curl -v -d '{"email": "example@example.com", "password": "password"}' -H 'Content-Type: application/json'  http://127.0.0.1:5000/adduser


curl -v -d '{"email": "example@example.com", "password": "password"}' -H 'Content-Type: application/json'  http://127.0.0.1:5000/login


curl -v -H 'Content-Type: application/json' -H 'x-access-token:${token}' http://127.0.0.1:5000/data
