from flask import Flask, request
from solace.messaging.messaging_service import MessagingService
from solace.messaging.config.transport_security_strategy import TLS
from solace.messaging.config.retry_strategy import RetryStrategy
from solace.messaging.resources.topic import Topic
import json

app = Flask(__name__)

# Define the connection properties for the Solace broker
broker_props = {
    "solace.messaging.transport.host": "tcps://xx-xxxxxxx-xxxxx.messaging.solace.cloud:55443",
    "solace.messaging.service.vpn-name": "test",
    "solace.messaging.authentication.scheme.basic.username": "solace-cloud-client",
    "solace.messaging.authentication.scheme.basic.password": "xxxxxxxxxxx",
}

# Configure transport security with TLS
transport_security = TLS.create().with_certificate_validation(
    True, validate_server_name=False, trust_store_file_path="."
)

# Create a MessagingService instance
messaging_service = (
    MessagingService.builder()
    .from_properties(broker_props)
    .with_reconnection_retry_strategy(RetryStrategy.parametrized_retry(20, 3))
    .with_transport_security_strategy(transport_security)
    .build()
)

# Connect to the Solace broker
messaging_service.connect()

# Create a direct message publisher
publisher = messaging_service.create_direct_message_publisher_builder().build()
publisher.start()
print("Publisher started")

# Define the route for creating a user
@app.route("/user/create_user", methods=["POST"])
def create_user():
    user_data = request.get_json()
    print(user_data)
    # create a topic subscription for receiving user created events
    destination = Topic.of("user/create_user")
    # Publish the user data to the messaging service
    publisher.publish(message=json.dumps(user_data), destination=destination)

    return "User created successfully!"


if __name__ == "__main__":
    app.run(debug=True)
