#!/usr/bin/env python3
"""
Kafka Producer for Testing Feedback Analysis
Sends test feedback messages to Kafka for processing
"""

import json
import time
import uuid
from datetime import datetime
from kafka import KafkaProducer
from kafka.errors import KafkaError


class FeedbackProducer:
    """Producer for sending feedback messages to Kafka"""
    
    def __init__(self, bootstrap_servers=['localhost:9092']):
        self.producer = KafkaProducer(
            bootstrap_servers=bootstrap_servers,
            value_serializer=lambda x: json.dumps(x).encode('utf-8'),
            key_serializer=lambda x: x.encode('utf-8') if x else None
        )
        self.topic = 'feedback_raw'
        
    def send_feedback(self, feedback_data):
        """Send a feedback message to Kafka"""
        try:
            # Generate unique ID if not provided
            if 'id' not in feedback_data:
                feedback_data['id'] = str(uuid.uuid4())
            
            # Add timestamp if not provided
            if 'timestamp' not in feedback_data:
                feedback_data['timestamp'] = datetime.now().isoformat()
            
            # Send to Kafka
            future = self.producer.send(
                self.topic,
                key=feedback_data['id'],
                value=feedback_data
            )
            
            # Wait for send to complete
            record_metadata = future.get(timeout=10)
            
            print(f"✅ Sent feedback {feedback_data['id']} to {self.topic}: {record_metadata}")
            return True
            
        except KafkaError as e:
            print(f"❌ Failed to send feedback: {e}")
            return False
    
    def send_test_messages(self):
        """Send predefined test messages"""
        test_messages = [
            {
                "text": "This product is absolutely amazing! I love everything about it.",
                "user_id": "user_001",
                "metadata": {"category": "product_review", "rating": 5}
            },
            {
                "text": "Terrible customer service. Waited for hours and got no help.",
                "user_id": "user_002",
                "metadata": {"category": "customer_service", "rating": 1}
            },
            {
                "text": "The app works fine but could use some improvements in the UI.",
                "user_id": "user_003",
                "metadata": {"category": "app_feedback", "rating": 3}
            },
            {
                "text": "Excellent quality and fast delivery. Highly recommended!",
                "user_id": "user_004",
                "metadata": {"category": "product_review", "rating": 5}
            },
            {
                "text": "I'm not sure about this. It seems okay but nothing special.",
                "user_id": "user_005",
                "metadata": {"category": "general_feedback", "rating": 3}
            }
        ]
        
        print(f"📤 Sending {len(test_messages)} test messages...")
        
        for i, message in enumerate(test_messages, 1):
            success = self.send_feedback(message)
            if success:
                print(f"  {i}. Sent: {message['text'][:50]}...")
            time.sleep(1)  # Small delay between messages
    
    def send_custom_message(self):
        """Send a custom message from user input"""
        print("\n📝 Enter custom feedback message:")
        text = input("Feedback text: ").strip()
        if not text:
            print("❌ No text provided")
            return
        
        user_id = input("User ID (optional): ").strip() or f"user_{int(time.time())}"
        category = input("Category (optional): ").strip() or "general_feedback"
        rating = input("Rating 1-5 (optional): ").strip()
        
        try:
            rating = int(rating) if rating else None
        except ValueError:
            rating = None
        
        message = {
            "text": text,
            "user_id": user_id,
            "metadata": {
                "category": category,
                "rating": rating
            }
        }
        
        success = self.send_feedback(message)
        if success:
            print("✅ Custom message sent successfully!")
    
    def close(self):
        """Close the producer"""
        self.producer.close()


def main():
    """Main function"""
    print("🚀 Kafka Feedback Producer")
    print("=" * 40)
    
    try:
        producer = FeedbackProducer()
        
        while True:
            print("\n📤 Choose an option:")
            print("1. Send test messages")
            print("2. Send custom message")
            print("3. Exit")
            
            choice = input("\nEnter your choice (1-3): ").strip()
            
            if choice == '1':
                producer.send_test_messages()
            elif choice == '2':
                producer.send_custom_message()
            elif choice == '3':
                print("👋 Goodbye!")
                break
            else:
                print("❌ Invalid choice. Please try again.")
                
    except KeyboardInterrupt:
        print("\n\n👋 Shutting down...")
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        if 'producer' in locals():
            producer.close()


if __name__ == "__main__":
    main()

