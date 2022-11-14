# This dockerfile is only meant for local development
FROM python:3.9-slim


# Prevent Python from copying pyc files to the container
ENV PYTHONDONTWRITEBYTECODE 1
# Ensures that Python output is logged to the terminal, making it possible to monitor Django logs in realtime
ENV PYTHONUNBUFFERED 1


# Move to folder
WORKDIR /opt/webbinspace


# Install and upgrade the pip version that is in the container
RUN pip install --upgrade pip

# Copy the requirements.txt file into the work directory in the container
COPY requirements.txt .
RUN pip install -r requirements.txt


# Copy all the project source code to the working directory in the container
COPY . .

COPY docker-entrypoint.sh .
ENTRYPOINT ["./docker-entrypoint.sh"]

# Set the executable commands in the container
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]