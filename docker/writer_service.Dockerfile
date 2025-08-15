FROM golang:1.23.2-alpine

# Установим git и wget
RUN apk add --no-cache git wget

WORKDIR /app

ENV CONFIG=docker
ENV GOPROXY=direct
ENV GOSUMDB=off

COPY .. /app

RUN go mod download

CMD ["CompileDaemon", "--build=go build -o main .", "--command=./main"]
