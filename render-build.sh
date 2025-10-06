#!/usr/bin/env bash
# render-build.sh

echo "Instalando dependências..."
pip install -r requirements.txt

echo "Rodando migrações..."
python manage.py migrate --noinput

echo "Coletando arquivos estáticos..."
python manage.py collectstatic --noinput

echo "Build concluído com sucesso!"
