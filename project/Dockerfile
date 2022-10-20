# For more information, please refer to https://aka.ms/vscode-docker-python
FROM python:3.8-slim

# Keeps Python from generating .pyc files in the container
#ENV PYTHONDONTWRITEBYTECODE=1

# Turns off buffering for easier container logging
#ENV PYTHONUNBUFFERED=1

# Install pip requirements
COPY requirements.txt .
RUN python -m pip install -r requirements.txt

#WORKDIR /techtrends
#RUN python init_db.py

WORKDIR /app
COPY . /app

WORKDIR /app/techtrends
RUN python init_db.py

#WORKDIR /app
EXPOSE 3111

#WORKDIR /app/techtrends

# During debugging, this entry point will be overridden. For more information, please refer to https://aka.ms/vscode-docker-python-debug
CMD ["python", "./app.py","-e","production"]
