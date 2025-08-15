FROM golang:1.23.2-alpine AS build

# Установка git и CompileDaemon
RUN apk add --no-cache git


WORKDIR /app

ENV CONFIG=docker
ENV GOPROXY=direct

COPY .. /app

RUN go mod download

# Стартуем через CompileDaemon
ENTRYPOINT ["/go/bin/CompileDaemon", "--build=go build -o main reader_service/cmd/main.go", "--command=./main"]
