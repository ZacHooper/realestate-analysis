FROM prefecthq/prefect

RUN mkdir -p /usr/src/app
WORKDIR /usr/src/app

COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN pip install -e .

CMD [ "python", "flows/orchestration.py" ]
