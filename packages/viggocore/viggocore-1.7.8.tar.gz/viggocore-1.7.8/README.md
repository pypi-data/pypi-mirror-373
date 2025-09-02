[![Build Status](https://travis-ci.org/samueldmq/viggocore.svg?branch=master)](https://travis-ci.org/samueldmq/viggocore-ansible) [![Code Climate](https://codeclimate.com/github/samueldmq/viggocore/badges/gpa.svg)](https://codeclimate.com/github/samueldmq/viggocore) [![Test Coverage](https://codeclimate.com/github/samueldmq/viggocore/badges/coverage.svg)](https://codeclimate.com/github/samueldmq/viggocore/coverage) [![Issue Count](https://codeclimate.com/github/samueldmq/viggocore/badges/issue_count.svg)](https://codeclimate.com/github/samueldmq/viggocore)

Português Brasileiro | [English](https://github.com/objetorelacional/viggocore/blob/documentacao/README_en.md)

# ViggoCore

O Viggocore é um framework open source para criação de API REST. Ele foi
criado para dar poder ao desenvolvedor, permitindo focar no desenvolvimento do
produto e das regras de negócio em vez de problemas de engenharia.

## Começe do básico

Vamos criar um projeto básico. Primeiro, crie um arquivo chamado 'app.py' com
o seguinte conteúdo:

```python
import viggocore

system = viggocore.System()
system.run()
```

Abra um terminal e rode os seguintes comandos:

```bash
$ pip install viggocore
$ python3 app.py
```

Sua API está rodando e pronta para ser consumida. Vamos testar com uma requisição:

```bash
$ curl -i http://127.0.0.1:5000/
HTTP/1.0 200 OK
Content-Type: text/html; charset=utf-8
Content-Length: 5
Server: Werkzeug/1.0.1 Python/3.7.3
Date: Thu, 15 Oct 2020 13:08:19 GMT

1.0.0%
```

Com a sua API criada, siga para nossa [documentação](https://viggocore.readthedocs.io/en/latest/) e aproveite o poder e a facilidade
do viggocore no seu negócio ou na sua nova ideia.
