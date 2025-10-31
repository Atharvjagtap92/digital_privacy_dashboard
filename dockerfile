# Use Python base image
FROM python:3.10-slim

# Set working directory inside container
WORKDIR /app

# Copy dependency list and install them
COPY requirements.txt .
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Copy the rest of the app files
COPY . .

# Expose port where Streamlit runs
EXPOSE 8501

# Run Streamlit app
CMD ["streamlit", "run", "app.py", "--server.port=8501"]
