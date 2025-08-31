package repository

import (
	"context"
	"encoding/json"

	"github.com/Maksim646/feedback_analysis/pkg/logger"
	"github.com/Maksim646/feedback_analysis/reader_service/config"
	"github.com/Maksim646/feedback_analysis/reader_service/internal/models"
	"github.com/go-redis/redis/v8"
	"github.com/opentracing/opentracing-go"
	"github.com/pkg/errors"
)

const (
	redisFeedbackPrefixKey = "reader:feedback"
)

type redisRepository struct {
	log         logger.Logger
	cfg         *config.Config
	redisClient redis.UniversalClient
}

func NewRedisRepository(log logger.Logger, cfg *config.Config, redisClient redis.UniversalClient) *redisRepository {
	return &redisRepository{log: log, cfg: cfg, redisClient: redisClient}
}

func (r *redisRepository) PutFeedback(ctx context.Context, key string, feedbackAnalyzed *models.FeedbackAnalyzed) {
	span, ctx := opentracing.StartSpanFromContext(ctx, "redisRepository.PutFeedbackAnalyzed")
	defer span.Finish()

	feedbackAnalyzesBytes, err := json.Marshal(feedbackAnalyzed)
	if err != nil {
		r.log.WarnMsg("json.Marshal", err)
		return
	}

	if err := r.redisClient.HSetNX(ctx, r.getRedisFeedbackPrefixKey(), key, feedbackAnalyzesBytes).Err(); err != nil {
		r.log.WarnMsg("redisClient.HSetNX", err)
		return
	}
	r.log.Debugf("HSetNX prefix: %s, key: %s", r.getRedisFeedbackPrefixKey(), key)
}

func (r *redisRepository) GetFeedback(ctx context.Context, key string) (*models.FeedbackAnalyzed, error) {
	span, ctx := opentracing.StartSpanFromContext(ctx, "redisRepository.GetFeedbackAnalyzed")
	defer span.Finish()

	feedbackAnalyzesBytes, err := r.redisClient.HGet(ctx, r.getRedisFeedbackPrefixKey(), key).Bytes()
	if err != nil {
		if err != redis.Nil {
			r.log.WarnMsg("redisClient.HGet", err)
		}
		return nil, errors.Wrap(err, "redisClient.HGet")
	}

	var feedback models.FeedbackAnalyzed
	if err := json.Unmarshal(feedbackAnalyzesBytes, &feedback); err != nil {
		return nil, err
	}

	r.log.Debugf("HGet prefix: %s, key: %s", r.getRedisFeedbackPrefixKey(), key)
	return &feedback, nil
}

// func (r *redisRepository) DelProduct(ctx context.Context, key string) {
// 	if err := r.redisClient.HDel(ctx, r.getRedisProductPrefixKey(), key).Err(); err != nil {
// 		r.log.WarnMsg("redisClient.HDel", err)
// 		return
// 	}
// 	r.log.Debugf("HDel prefix: %s, key: %s", r.getRedisProductPrefixKey(), key)
// }

// func (r *redisRepository) DelAllProducts(ctx context.Context) {
// 	if err := r.redisClient.Del(ctx, r.getRedisProductPrefixKey()).Err(); err != nil {
// 		r.log.WarnMsg("redisClient.HDel", err)
// 		return
// 	}
// 	r.log.Debugf("Del key: %s", r.getRedisProductPrefixKey())
// }

func (r *redisRepository) getRedisFeedbackPrefixKey() string {
	if r.cfg.ServiceSettings.RedisFeedbackPrefixKey != "" {
		return r.cfg.ServiceSettings.RedisFeedbackPrefixKey
	}

	return redisFeedbackPrefixKey
}
