# Use an official Python runtime as a parent image
FROM python:3.9

# Set the working directory in the container
WORKDIR /app

# Copy the rest of the application source code into the container at /app
COPY . /app/


# Create a directory for SSH keys
RUN mkdir -p ~/.ssh

# Copy the SSH private key passed as a build argument into the image
ARG SSH_PRIVATE_KEY
RUN echo "$SSH_PRIVATE_KEY" > ~/.ssh/id_rsa && \
    chmod 600 ~/.ssh/id_rsa

# Set permissions for the known_hosts file if needed
RUN touch ~/.ssh/known_hosts && \
    ssh-keyscan gitlab.com >> ~/.ssh/known_hosts

# Install any needed packages
RUN pip3 install .
