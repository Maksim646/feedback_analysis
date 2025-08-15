import grpc
from concurrent import futures
import time
import logging

import reader_service_pb2
import reader_service_pb2_grpc

class NlpWorkerServicer(reader_service_pb2_grpc.ReaderServiceServicer):
    def CreateFeedbackAnalysis(self, request, context):
        text = request.text.lower()

        # Простая логика ключевых слов
        keywords = self.extract_keywords(text)

        # Простейший сентимент-анализ
        sentiment = "neutral"
        if any(w in text for w in ["good", "great", "love"]):
            sentiment = "positive"
        elif any(w in text for w in ["bad", "hate", "terrible"]):
            sentiment = "negative"

        response = reader_service_pb2.CreateFeedbackAnalysisRes(
            feedback_id=request.feedback_id,
            feedback_source=request.feedback_source,
            text=request.text,
            created_at=request.created_at,
            keywords=keywords,
            sentiment=sentiment
        )
        return response

    def extract_keywords(self, text):
        words = text.split()
        keywords = set()
        for w in words:
            if len(w) > 4:
                keywords.add(w)
        return ", ".join(keywords)

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    reader_service_pb2_grpc.add_ReaderServiceServicer_to_server(NlpWorkerServicer(), server)
    server.add_insecure_port('[::]:50052')
    server.start()
    logging.info("NLP Worker (Python) gRPC server started on port 50052")
    try:
        while True:
            time.sleep(86400)
    except KeyboardInterrupt:
        server.stop(0)

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    serve()
