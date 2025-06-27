package main

import (
	"flag"
	"log"

	"github.com/Maksim646/feedback_analysis/api_gateway_service/config"
	"github.com/Maksim646/feedback_analysis/api_gateway_service/internal/server"
	"github.com/Maksim646/feedback_analysis/pkg/logger"
)

// @contact.name Maxim Adamov
// @contact.url https://github.com/Maksim646
// @contact.email adamov4391@mail.ru
func main() {
	flag.Parse()

	cfg, err := config.InitConfig()
	if err != nil {
		log.Fatal(err)
	}

	appLogger := logger.NewAppLogger(cfg.Logger)
	appLogger.InitLogger()
	appLogger.WithName(cfg.ServiceName)

	s := server.NewServer(appLogger, cfg)
	appLogger.Fatal(s.Run())
}
