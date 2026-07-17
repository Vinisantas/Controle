FROM python:3.11-slim
LABEL key="Controle de Estoque"

WORKDIR /app

COPY requirements.txt .
RUN python -m pip install --upgrade pip && pip install -r requirements.txt

COPY . .

EXPOSE 8503

CMD ["streamlit", "run", "app.py", "--server.port", "8503", "--server.address", "0.0.0.0"]