package repository

import (
	"context"
	// "github.com/Maksim646/feedback_analysis/pkg/utils"
	"github.com/Maksim646/feedback_analysis/reader_service/internal/models"
	uuid "github.com/satori/go.uuid"
)

type Repository interface {
	CreateFeedback(ctx context.Context, feedback *models.FeedbackAnalyzed) (*models.FeedbackAnalyzed, error)
	// UpdateProduct(ctx context.Context, product *models.FeedbackAnalyzed) (*models.FeedbackAnalyzed, error)
	// DeleteProduct(ctx context.Context, uuid uuid.UUID) error

	GetFeedbackById(ctx context.Context, uuid uuid.UUID) (*models.FeedbackAnalyzed, error)
	// Search(ctx context.Context, search string, pagination *utils.Pagination) (*models.FeedbackAnalyzedsList, error)
}

type CacheRepository interface {
	PutFeedbackAnalyzed(ctx context.Context, key string, feedback *models.FeedbackAnalyzed)
	GetFeedbackAnalyzed(ctx context.Context, key string) (*models.FeedbackAnalyzed, error)
	DelFeedbackAnalyzed(ctx context.Context, key string)
	DelAllFeedbackAnalyzed(ctx context.Context)
}
