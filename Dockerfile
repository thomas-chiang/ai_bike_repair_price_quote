FROM python:3.13.5-slim


WORKDIR /app

# Copy the FastAPI application code into the container
COPY . /app

# install necessary system dependencies
RUN pip install --upgrade pip
COPY requirements.txt .
RUN pip install -r requirements.txt

# expose specific port for external access
EXPOSE 8080

# start fastapi application using uvicorn
CMD uvicorn main:app --host=0.0.0.0 --port=$PORT