from flask import Flask, request
from solace.messaging.messaging_service import MessagingService
from solace.messaging.config.transport_security_strategy import TLS
from solace.messaging.config.retry_strategy import RetryStrategy
from solace.messaging.resources.topic import Topic
from solace.messaging.publisher.direct_message_publisher import DirectMessagePublisher
from solace.messaging.receiver.direct_message_receiver import DirectMessageReceiver
from solace.messaging.resources.topic_subscription import TopicSubscription
from solace.messaging.receiver.message_receiver import MessageHandler

import json

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

# create a topic subscription for receiving user created events
# topic_subscription = messaging_service.subscribe()
publisher = messaging_service.create_direct_message_publisher_builder().build()
publisher.start()
print('Publisher started')

# Create a Solace messaging service for receiving messages
# receiver = DirectMessageReceiver.builder().from_connection(messaging_service).build()
# receiver.start()

@app.route('/user/create_user', methods=['POST'])
def create_user():
    user_data = request.get_json()
    print(user_data)
    destination = Topic.of("user/create_user")
    # Publish the user data to the messaging service
    publisher.publish(message = json.dumps(user_data), destination=destination)

    return "User created successfully!"

# @receiver.receive("user/create_user_response")
# def create_user_response(msg):
#     response_data = json.loads(msg.get_binary_attachment().data.decode('utf-8'))
#     print(response_data)

if __name__ == '__main__':
    app.run(debug=True)
