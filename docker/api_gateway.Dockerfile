FROM golang:1.23.2-alpine AS build

# Установим git
RUN apk add --no-cache git

WORKDIR /app

ENV CONFIG=docker
ENV GOPROXY=direct

COPY .. /app

RUN go mod download

# Запуск через CompileDaemon
ENTRYPOINT ["/go/bin/CompileDaemon", "--build=go build -o main api_gateway_service/cmd/main.go", "--command=./main"]
