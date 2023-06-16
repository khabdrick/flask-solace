import time
from flask import Flask
from solace.messaging.messaging_service import MessagingService
from solace.messaging.resources.topic_subscription import TopicSubscription
from solace.messaging.config.transport_security_strategy import TLS
from solace.messaging.config.retry_strategy import RetryStrategy
from solace.messaging.receiver.message_receiver import MessageHandler, InboundMessage
import json

app = Flask(__name__)

broker_props = {
    "solace.messaging.transport.host": "tcps://xx-xxxxxxx-xxxxx.messaging.solace.cloud:55443",
    "solace.messaging.service.vpn-name": "test",
    "solace.messaging.authentication.scheme.basic.username": "solace-cloud-client",
    "solace.messaging.authentication.scheme.basic.password": "xxxxxxxxxxx",
}
transport_security = TLS.create().with_certificate_validation(
    True, validate_server_name=False, trust_store_file_path="."
)

messaging_service = (
    MessagingService.builder()
    .from_properties(broker_props)
    .with_reconnection_retry_strategy(RetryStrategy.parametrized_retry(20, 3))
    .with_transport_security_strategy(transport_security)
    .build()
)

# create an empty array to store the user data
out_payload = []
# define the topic for user creation requests and responses
CREATE_USER_TOPIC = ["user/create_user"]

# Handle received messages
class MessageHandlerImpl(MessageHandler):
    def on_message(self, message: InboundMessage):
        # Check if the payload is a String or Byte, decode if its the later
        topic = message.get_destination_name()
        payload = (
            message.get_payload_as_string()
            if message.get_payload_as_string() != None
            else message.get_payload_as_bytes()
        )
        print("\n" + f"Message Payload String: {payload} \n")
        print("\n" + f"Message Topic: {topic} \n")

        # Convert the payload to a dictionary
        message_dict = json.loads(payload)
        # Append the message dictionary to the output payload list
        out_payload.append(message_dict)


messaging_service.connect()

# Create topic subscriptions
topics_sub = []
for t in CREATE_USER_TOPIC:
    topics_sub.append(TopicSubscription.of(t))
# Create a direct message receiver and start it
direct_receiver = (
    messaging_service.create_direct_message_receiver_builder()
    .with_subscriptions(topics_sub)
    .build()
)
direct_receiver.start()

# Sleep for 4 seconds to allow time for message reception
time.sleep(4)

# Receive messages asynchronously using the message handler
message_handler = MessageHandlerImpl()
direct_receiver.receive_async(message_handler)


@app.route("/")
def index():
    return out_payload


if __name__ == "__main__":
    app.run(debug=True, port=5001)
