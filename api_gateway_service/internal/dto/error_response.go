package dto

type ErrorResponse struct {
	Message string `json:"message" validate:"required,min=1,max=500"`
}
