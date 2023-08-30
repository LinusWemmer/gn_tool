FROM python:3.8-slim

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container
COPY . /app

# Install Python dependencies
RUN apt-get update &&  apt-get -y install \
    git \
    swi-prolog \
    sfst \
    unzip \
    wget \
    python3 \
    python3-pexpect \
    python-is-python3

RUN pip install --no-cache-dir flask pexpect

RUN (bash install.sh)

# Make port 80 available to the world outside this container
EXPOSE 80
EXPOSE 4000

# Define environment variable (if needed)
# ENV NAME World

# Run your Flask app when the container launches
CMD ["python", "__init__.py"]
