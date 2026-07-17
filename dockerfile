FROM python:3.11-slim
LABEL key="Controle de Estoque"

WORKDIR /app

COPY requirements.txt .
RUN python -m pip install --upgrade pip && pip install -r requirements.txt

COPY app.py .

EXPOSE 8503

CMD ["streamlit", "run", "main.py", "--server.port", "8501", "--server.address", "0.0.0.0"]



