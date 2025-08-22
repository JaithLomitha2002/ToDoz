FROM python:3.11-slim

WORKDIR /app

COPY . /app

# Install dependencies
RUN pip install --upgrade pip
RUN pip install flask flask_sqlalchemy flask_login werkzeug
RUN pip install -r requirements.txt

# If you have a requirements.txt, use:
# RUN pip install -r requirements.txt

EXPOSE 5000

CMD ["python", "app.py"]