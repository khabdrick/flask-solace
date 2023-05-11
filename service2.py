import time
from flask import Flask, request
from solace.messaging.errors.pubsubplus_client_error import PubSubPlusClientError
from solace.messaging.messaging_service import MessagingService
from solace.messaging.resources.topic_subscription import TopicSubscription
from solace.messaging.config.transport_security_strategy import TLS
from solace.messaging.config.retry_strategy import RetryStrategy
from solace.messaging.receiver.message_receiver import MessageHandler, InboundMessage
import json
from solace.messaging.message import Message

app = Flask(__name__)

broker_props = {
  "solace.messaging.transport.host": "tcps://mr-connection-31ivs620nqh.messaging.solace.cloud:55443",
  "solace.messaging.service.vpn-name": "test",
  "solace.messaging.authentication.scheme.basic.username": "solace-cloud-client",
  "solace.messaging.authentication.scheme.basic.password": "ne1rfnknchsrt3cb1tjdbi2ltr",
}
transport_security = TLS.create() \
  .with_certificate_validation(True, validate_server_name=False,
        trust_store_file_path=".")

messaging_service = MessagingService.builder().from_properties(broker_props)\
  .with_reconnection_retry_strategy(RetryStrategy.parametrized_retry(20,3))\
  .with_transport_security_strategy(transport_security).build() 


messaging_service.connect()


# create an empty array to store the user data
users = []
out_payload = []
# define the topic for user creation requests and responses
CREATE_USER_TOPIC = ["user/create_user"]
destination = TopicSubscription.of(CREATE_USER_TOPIC)
# CREATE_USER_RESPONSE_TOPIC = "user/create_user_response"
# Handle received messages
class MessageHandlerImpl(MessageHandler):
    def on_message(self, message: InboundMessage):
        # Check if the payload is a String or Byte, decode if its the later
        payload = message.get_payload_as_string() if message.get_payload_as_string() != None else message.get_payload_as_bytes()
        # print("\n" + f"Message Payload String: {payload} \n")

        out_payload.append(payload)
        # return payload


topics_sub = []
for t in CREATE_USER_TOPIC:
    topics_sub.append(TopicSubscription.of(t))

# Build a Receiver with the given topics and start it
direct_receiver = messaging_service.create_direct_message_receiver_builder()\
                        .with_subscriptions(topics_sub)\
                        .build()

direct_receiver.start()
time.sleep(4)


try:
    # Callback for received messages
    message_handler = MessageHandlerImpl()
    direct_receiver.receive_async(message_handler)
    print(direct_receiver.receive_message(message_handler))
    
    
    try: 
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print('\nDisconnecting Messaging Service')
finally:
    print('\nTerminating receiver')
    direct_receiver.terminate()
    print('\nDisconnecting Messaging Service')
    messaging_service.disconnect()

@app.route("/")
def index():
    return "User Service 2"

@app.route("/users", methods=["GET"])
def get_users():
    return json.dumps(users)

if __name__ == "__main__":
    app.run(debug=True, port=5001)
