### Build

#FROM python:3.12.9-alpine3.21 AS build
FROM python:3.12.11-alpine3.22 AS build

# Install to build python requirements
RUN apk update \
    && apk --no-cache --update add build-base \
    && apk --update add alpine-sdk \
    && apk add libffi-dev \
    && apk add postgresql-dev gcc python3-dev musl-dev \
    && apk add protobuf-dev

# Add tools
RUN apk --no-cache add bash \
    && apk --no-cache add nano \
    && apk --no-cache add curl

# Create user
RUN addgroup appuser \
    && adduser -G appuser -s /bin/bash -D appuser

# Create /code folder
RUN mkdir /code \
    && chown -R appuser:appuser /code

# Switch to user appuser
USER appuser

# Create python venv and install requirements
COPY --chown=appuser ./requirements.txt /code/docker_controller/requirements.txt
WORKDIR /code/docker_controller
RUN python -m venv /code/env \
    && source /code/env/bin/activate \
    && pip install -r requirements.txt



### Runtime

#FROM python:3.12.9-alpine3.21 AS runtime
FROM python:3.12.11-alpine3.22 AS runtime

# Install for python requirements
#RUN apk update \
#    && apk --no-cache add libstdc++ \
#    && apk --no-cache add postgresql-dev gcc python3-dev musl-dev

# Add tools
RUN apk --no-cache add bash \
    && apk --no-cache add nano \
    && apk --no-cache add curl

# Create and switch to user appuser as in build
RUN addgroup appuser \
    && adduser -G appuser -s /bin/bash -D appuser
USER appuser

# Copy /code from build
COPY --chown=appuser --from=build /code /code

# Copy docker controller sources
COPY --chown=appuser ./rest /code/docker_controller

# Activate permanently python venv
ENV PATH=/code/env/bin:$PATH

WORKDIR /code/docker_controller
CMD ["sh", "-c", "uvicorn run:app --host 0.0.0.0 --port $HOLADO_DOCKER_CONTROLLER_PORT"]

