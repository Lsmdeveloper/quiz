echo "Rodando migrações..."
python manage.py migrate --noinput
echo "Coletando arquivos estáticos..."
python manage.py collectstatic --noinput
echo "Deploy concluído com sucesso!"