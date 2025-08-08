CREATE EXTENSION IF NOT EXISTS citext;
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
DROP TABLE IF EXISTS feedback_analysis CASCADE;


CREATE TABLE feedback_analysis
(
    feedback_id             UUID PRIMARY KEY         DEFAULT uuid_generate_v4(),
    feedback_source         VARCHAR(255)  NOT NULL CHECK ( feedback_source <> '' ),
    text                    VARCHAR(5000) NOT NULL CHECK ( text <> '' ),
    keywords               VARCHAR(500)  NOT NULL CHECK ( keywords <> '' ),
    Sentiment            VARCHAR(50)   NOT NULL CHECK ( Sentiment IN ('positive', 'negative', 'neutral') ),
    created_at  TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);