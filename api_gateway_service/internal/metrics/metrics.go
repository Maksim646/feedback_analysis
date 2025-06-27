package metrics

import (
	"fmt"

	"github.com/Maksim646/feedback_analysis/api_gateway_service/config"
	"github.com/prometheus/client_golang/prometheus"
	"github.com/prometheus/client_golang/prometheus/promauto"
)

type ApiGatewayMetrics struct {
	SuccessHttpRequests    prometheus.Counter
	ErrorHttpRequests      prometheus.Counter
	RequestDuration        prometheus.Histogram
	KafkaPublishErrors     prometheus.Counter
	KafkaMessagesPublished prometheus.Counter
	SearchFeedbackRequests prometheus.Counter
	PostFeedbackRequests   prometheus.Counter
	GetFeedbackRequests    prometheus.Counter
}

func NewApiGatewayMetrics(cfg *config.Config) *ApiGatewayMetrics {
	return &ApiGatewayMetrics{
		SuccessHttpRequests: promauto.NewCounter(prometheus.CounterOpts{
			Name: fmt.Sprintf("%s_success_http_requests_total", cfg.ServiceName),
			Help: "The total number of successful HTTP requests",
		}),
		ErrorHttpRequests: promauto.NewCounter(prometheus.CounterOpts{
			Name: fmt.Sprintf("%s_error_http_requests_total", cfg.ServiceName),
			Help: "The total number of error HTTP requests",
		}),
		RequestDuration: promauto.NewHistogram(prometheus.HistogramOpts{
			Name:    fmt.Sprintf("%s_http_request_duration_seconds", cfg.ServiceName),
			Help:    "Histogram of HTTP request durations in seconds",
			Buckets: prometheus.DefBuckets,
		}),
		KafkaPublishErrors: promauto.NewCounter(prometheus.CounterOpts{
			Name: fmt.Sprintf("%s_kafka_publish_errors_total", cfg.ServiceName),
			Help: "The total number of Kafka publish errors",
		}),
		KafkaMessagesPublished: promauto.NewCounter(prometheus.CounterOpts{
			Name: fmt.Sprintf("%s_kafka_messages_published_total", cfg.ServiceName),
			Help: "The total number of Kafka messages published",
		}),
		SearchFeedbackRequests: promauto.NewCounter(prometheus.CounterOpts{
			Name: fmt.Sprintf("%s_search_feedback_requests_total", cfg.ServiceName),
			Help: "The total number of search feedback requests",
		}),
		PostFeedbackRequests: promauto.NewCounter(prometheus.CounterOpts{
			Name: fmt.Sprintf("%s_post_feedback_requests_total", cfg.ServiceName),
			Help: "The total number of post feedback requests",
		}),
		GetFeedbackRequests: promauto.NewCounter(prometheus.CounterOpts{
			Name: fmt.Sprintf("%s_feedback_get_requests_total", cfg.ServiceName),
			Help: "The total number of GET /feedback/stats requests",
		}),
	}
}
