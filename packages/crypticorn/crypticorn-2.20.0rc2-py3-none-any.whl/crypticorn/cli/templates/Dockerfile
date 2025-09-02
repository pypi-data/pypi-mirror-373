FROM python:3.11.5

# This line is used to allow the cache to be busted (only busts in CI)
ARG CACHEBUST=1
COPY ./requirements.txt /code/requirements.txt

WORKDIR /code
# set API_ENV in .env
# API_ENV=local
# add to compose file
# build:
#     context: .
#     dockerfile: src/api/Dockerfile
#     args:
#       - API_ENV=${API_ENV}
# environment:
#     - API_ENV=${API_ENV}
#
# and to the workflow:
# env:
#     API_ENV: ${{ github.ref == 'refs/heads/main' && 'prod' || 'dev' }}
# and in the docker build:
#     build-args: |
#       CACHEBUST=${{ github.run_id }} # invalidates dependency cache on every workflow run

ARG API_ENV

# use this before code migration to crypticorn 3.x and crypticorn-utils 1.x
# RUN if [ "$API_ENV" != "prod" ]; then \
#     pip install --pre 'crypticorn<3.0.0'; \
#     pip install --pre 'crypticorn-utils<1.0.0'; \
#     fi

# use this after code migration
RUN if [ "$API_ENV" != "prod" ]; then \
    pip install --pre crypticorn; \
    pip install --pre crypticorn-utils; \
    fi

RUN pip install --no-cache-dir -r requirements.txt

COPY ./src /code/src

CMD ["uvicorn", "src.api.main:app", "--host", "0.0.0.0", "--port", "3000"]
