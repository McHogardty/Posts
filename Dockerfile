# Use python 3.6
FROM python:3.6

# Set the working directory to /posts
WORKDIR /app

# Copy the posts app into the working directory
ADD . /app

# Install any packages
RUN pip install --trusted-host pypi.python.org -r requirements.txt

# Make sure port 5000 is open.
EXPOSE 80

# Run
CMD ["python", "./run.py"]
