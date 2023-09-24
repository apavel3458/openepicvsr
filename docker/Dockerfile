FROM python:3.9
WORKDIR /app
RUN apt-get update
RUN apt-get install -y vim
RUN pip install matplotlib plotly numpy pandas jupyter openpyxl Levenshtein
RUN echo ":set mouse=v" >> ~/.vimrc
ENTRYPOINT ["docker/entrypoint.sh"]
