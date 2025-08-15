package client

import (
	"context"
	"time"

	"github.com/Maksim646/feedback_analysis/api_gateway_service/config"
	"github.com/Maksim646/feedback_analysis/pkg/interceptors"
	grpc_retry "github.com/grpc-ecosystem/go-grpc-middleware/retry"
	"google.golang.org/grpc"
	"google.golang.org/grpc/codes"
)

const (
	backoffLinear  = 100 * time.Millisecond
	backoffRetries = 3
)

func NewNlpWorkerClient(ctx context.Context, cfg *config.Config, im interceptors.InterceptorManager) (*grpc.ClientConn, error) {
	opts := []grpc_retry.CallOption{
		grpc_retry.WithBackoff(grpc_retry.BackoffLinear(backoffLinear)),
		grpc_retry.WithCodes(codes.Unavailable, codes.DeadlineExceeded),
		grpc_retry.WithMax(backoffRetries),
	}

	conn, err := grpc.DialContext(
		ctx,
		cfg.Grpc.NlpWorkerServicePort,
		grpc.WithChainUnaryInterceptor(
			im.ClientRequestLoggerInterceptor(),
			grpc_retry.UnaryClientInterceptor(opts...),
		),
		grpc.WithInsecure(),
	)
	if err != nil {
		return nil, err
	}

	return conn, nil
}
