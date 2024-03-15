FROM python:3.10

WORKDIR /backend

COPY . .

RUN pip install -r requirements.txt

EXPOSE 8000

CMD ["uvicorn", "--host", "0.0.0.0", "--port", "8000", "device_manager_app.main:app"]
