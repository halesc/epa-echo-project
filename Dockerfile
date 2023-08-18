FROM python:3.11.4-slim

LABEL MAINTAINER="Chris Hales <halesc@seattleu.edu>, Mikayla Davis <mdavis@seattleu.edu>, and Matt Brodie <mbrodie@seattleu.edu>"

WORKDIR /app

COPY . .

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 8501

HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health

ENTRYPOINT ["streamlit", "run", "src/main.py", "--server.port=8501", "--server.address=0.0.0.0"]