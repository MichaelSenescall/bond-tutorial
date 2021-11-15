FROM python:3.9-slim-buster as base

# Setup virtual environment
ENV VIRTUAL_ENV=/opt/venv
RUN python3 -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

# Setup working directory
RUN mkdir /app
WORKDIR /app

# Copy code into Docker container
COPY app.py ./
COPY /.streamlit ./.streamlit
COPY /data ./data

# Install dependencies
COPY requirements.txt ./
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt && \
    rm -rf requirements.txt

# Start server
CMD streamlit run app.py --server.port $PORT