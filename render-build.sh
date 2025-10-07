#!/usr/bin/env bash
set -e

echo "Instalando dependências..."
pip install -r requirements.txt

echo "Rodando migrações..."
python manage.py migrate --noinput

echo "Criando superusuário (idempotente)..."
python manage.py createsu

echo "Coletando arquivos estáticos..."
python manage.py collectstatic --noinput

echo "Build concluído com sucesso!"
