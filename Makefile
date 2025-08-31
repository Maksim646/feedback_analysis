PROTO_FILES := proto/link/link.proto
GEN_DIR := ./gen/go

PROTOC ?= protoc
PROTOC_VERSION_EXPECTED := 25

PROTOC_GEN_GO ?= protoc-gen-go
PROTOC_GEN_GO_GRPC ?= protoc-gen-go-grpc




.PHONY:

run_all:
	make kafka-up
	wait
	make run_api_gateway &
	wait
	make run_nlp_worker &
	wait
	make run_reader_service &
	wait


run_api_gateway:
	go run api_gateway_service/cmd/main.go -config=./api_gateway_service/config/config.yaml

run_writer_microservice:
	go run writer_service/cmd/main.go -config=./writer_service/config/config.yaml

run_reader_microservice:
	go run reader_service/cmd/main.go -config=./reader_service/config/config.yaml

run_nlp_worker:
	docker stop mongodb && docker rm mongodb
	cd proto/nlp_worker
	docker run -d --name mongodb -p 27017:27017 -e MONGO_INITDB_ROOT_USERNAME=admin -e MONGO_INITDB_ROOT_PASSWORD=admin mongo:latest
	cd proto/nlp_worker && ./start.sh

run_reader_service:
	sudo lsof -i :5004 || true
	cd reader_service && go run cmd/main.go -config=./config/config.yaml



# ==============================================================================
# KAFKA
kafka-up:
	docker compose -f kafka/docker-compose.yml up -d --build

# Останавливает и удаляет контейнеры
kafka-down:
	docker compose -f kafka/docker-compose.yml down -v

# Смотреть логи всех контейнеров Kafka
kafka-logs:
	docker compose -f kafka/docker-compose.yml logs -f

# ==============================================================================
# Docker

docker_dev:
	@echo Starting local docker dev compose
	docker-compose -f docker-compose.yaml up --build

local:
	@echo Starting local docker compose
	docker-compose -f docker-compose.yml up -d --build


# ==============================================================================
# Docker support

FILES := $(shell docker ps -aq)

down-local:
	docker stop $(FILES)
	docker rm $(FILES)

clean:
	docker system prune -f

logs-local:
	docker logs -f $(FILES)


# ==============================================================================
# Modules support

tidy:
	go mod tidy

deps-reset:
	git checkout -- go.mod
	go mod tidy

deps-upgrade:
	go get -u -t -d -v ./...
	go mod tidy

deps-cleancache:
	go clean -modcache


# ==============================================================================
# Linters https://golangci-lint.run/usage/install/

run-linter:
	@echo Starting linters
	golangci-lint run ./...

# ==============================================================================
# PPROF

pprof_heap:
	go tool pprof -http :8006 http://localhost:6060/debug/pprof/heap?seconds=10

pprof_cpu:
	go tool pprof -http :8006 http://localhost:6060/debug/pprof/profile?seconds=10

pprof_allocs:
	go tool pprof -http :8006 http://localhost:6060/debug/pprof/allocs?seconds=10



# ==============================================================================
# Go migrate postgresql https://github.com/golang-migrate/migrate

DB_NAME = feedback_analysis
DB_HOST = localhost
DB_PORT = 5432
SSL_MODE = disable

force_db:
	migrate -database postgres://postgres:postgres@$(DB_HOST):$(DB_PORT)/$(DB_NAME)?sslmode=$(SSL_MODE) -path migrations force 1

version_db:
	migrate -database postgres://postgres:postgres@$(DB_HOST):$(DB_PORT)/$(DB_NAME)?sslmode=$(SSL_MODE) -path migrations version

migrate_up:
	migrate -database postgres://postgres:postgres@$(DB_HOST):$(DB_PORT)/$(DB_NAME)?sslmode=$(SSL_MODE) -path migrations up 1

migrate_down:
	migrate -database postgres://postgres:postgres@$(DB_HOST):$(DB_PORT)/$(DB_NAME)?sslmode=$(SSL_MODE) -path migrations down 1


# ==============================================================================
# MongoDB

mongo:
	cd ./scripts && mongo admin -u admin -p admin < init.js


# ==============================================================================
# Swagger

swagger:
	@echo Starting swagger generating
	swag init -g */*/*.go
	

# ==============================================================================
# Proto

proto_kafka:
	@echo Generating kafka proto
	cd proto/kafka && protoc --go_out=. --go-grpc_opt=require_unimplemented_servers=false --go-grpc_out=. kafka.proto

proto_nlp_worker_reader:
	@echo Generating Python gRPC code for nlp_worker
	cd proto/nlp_worker && \
	python3 -m grpc_tools.protoc \
		--proto_path=. \
		--python_out=. \
		--grpc_python_out=. \
		proto/nlp_worker_reader/nlp_worker_reader.proto


proto_reader:
	@echo Generating product reader microservice proto
	cd reader_service/proto/feedback_reader && protoc --go_out=. --go-grpc_opt=require_unimplemented_servers=false --go-grpc_out=. feedback_reader.proto

proto_writer:
	@echo Generating product writer microservice proto
	cd writer_service/proto/product_writer && protoc --go_out=. --go-grpc_opt=require_unimplemented_servers=false --go-grpc_out=. product_writer.proto

proto_writer_message:
	@echo Generating product writer messages microservice proto
	cd writer_service/proto/product_writer && protoc --go_out=. --go-grpc_opt=require_unimplemented_servers=false --go-grpc_out=. product_writer_messages.proto



proto_reader_message:
	@echo Generating product reader messages microservice proto
	cd reader_service/proto/feedback_reader && protoc --go_out=. --go-grpc_opt=require_unimplemented_servers=false --go-grpc_out=. feedback_reader_messages.proto

proto_feedback_reader:
	@echo Generating feedback reader microservice proto
	cd proto/feedback_reader && protoc --go_out=. --go-grpc_opt=require_unimplemented_servers=false --go-grpc_out=. feedback_reader.proto

proto_feedback_reader_message:
	@echo Generating feedback reader messages microservice proto
	cd proto/feedback_reader && protoc --go_out=. --go-grpc_opt=require_unimplemented_servers=false --go-grpc_out=. feedback_reader_messages.proto