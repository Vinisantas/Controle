import os
from dotenv import load_dotenv
import psycopg2
load_dotenv()
conexao = psycopg2.connect(
    host=os.getenv('PG_HOST'),
    port=os.getenv('PG_PORT'),
    user=os.getenv('PG_USER'),
    password=os.getenv('PG_PASSWORD'),
    dbname=os.getenv('PG_DATABASE'),
    connect_timeout=5,
)
print('CONEXAO_OK')
conexao.close()
