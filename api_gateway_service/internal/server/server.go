package server

import (
	"context"

	"github.com/Maksim646/feedback_analysis/api_gateway_service/config"

	"github.com/Maksim646/feedback_analysis/api_gateway_service/internal/client"
	v1 "github.com/Maksim646/feedback_analysis/api_gateway_service/internal/feedbacks/delivery/http/v1"
	"github.com/Maksim646/feedback_analysis/api_gateway_service/internal/feedbacks/service"
	"github.com/Maksim646/feedback_analysis/api_gateway_service/internal/metrics"
	"github.com/Maksim646/feedback_analysis/api_gateway_service/internal/middlewares"

	"github.com/Maksim646/feedback_analysis/pkg/interceptors"
	"github.com/Maksim646/feedback_analysis/pkg/kafka"
	"github.com/Maksim646/feedback_analysis/pkg/logger"
	"github.com/Maksim646/feedback_analysis/pkg/tracing"

	"os"
	"os/signal"
	"syscall"

	readerService "github.com/Maksim646/feedback_analysis/proto/feedback_reader"

	"github.com/go-playground/validator"
	"github.com/labstack/echo/v4"
	"github.com/opentracing/opentracing-go"
)

type server struct {
	log  logger.Logger
	cfg  *config.Config
	v    *validator.Validate
	mw   middlewares.MiddlewareManager
	im   interceptors.InterceptorManager
	echo *echo.Echo
	ps   *service.FeedbackService
	m    *metrics.ApiGatewayMetrics
}

func NewServer(log logger.Logger, cfg *config.Config) *server {
	return &server{log: log, cfg: cfg, echo: echo.New(), v: validator.New()}
}

func (s *server) Run() error {
	ctx, cancel := signal.NotifyContext(context.Background(), os.Interrupt, syscall.SIGTERM, syscall.SIGINT)
	defer cancel()

	s.mw = middlewares.NewMiddlewareManager(s.log, s.cfg)
	s.im = interceptors.NewInterceptorManager(s.log)
	s.m = metrics.NewApiGatewayMetrics(s.cfg)

	readerServiceConn, err := client.NewReaderServiceConn(ctx, s.cfg, s.im)
	if err != nil {
		return err
	}
	defer readerServiceConn.Close() // nolint: errcheck
	rsClient := readerService.NewFeedbackReaderClient(readerServiceConn)

	kafkaProducer := kafka.NewProducer(s.log, s.cfg.Kafka.Brokers)
	defer kafkaProducer.Close() // nolint: errcheck

	s.ps = service.NewFeedbackService(s.log, s.cfg, kafkaProducer, rsClient)

	feedbackHandlers := v1.NewFeedbacksHandlers(s.echo.Group(s.cfg.Http.FeedbacksPath), s.log, s.mw, s.cfg, s.ps, s.v, s.m)
	feedbackHandlers.MapRoutes()

	go func() {
		if err := s.runHttpServer(); err != nil {
			s.log.Errorf(" s.runHttpServer: %v", err)
			cancel()
		}
	}()
	s.log.Infof("API Gateway is listening on PORT: %s", s.cfg.Http.Port)

	s.runMetrics(cancel)
	s.runHealthCheck(ctx)

	if s.cfg.Jaeger.Enable {
		tracer, closer, err := tracing.NewJaegerTracer(s.cfg.Jaeger)
		if err != nil {
			return err
		}
		defer closer.Close() // nolint: errcheck
		opentracing.SetGlobalTracer(tracer)
	}

	<-ctx.Done()
	if err := s.echo.Server.Shutdown(ctx); err != nil {
		s.log.WarnMsg("echo.Server.Shutdown", err)
	}

	return nil
}
