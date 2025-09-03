import pika


class AMQPClient:
    """
    A base class for interacting with an AMQP broker using RabbitMQ.

    Attributes:
    - amqp_url (str): The URL for the AMQP broker.
    - exchange (str): The exchange name.
    - exchange_type (str): The type of exchange.
    - params (pika.URLParameters): Parameters for connecting to the AMQP broker.
    - connection (pika.BlockingConnection): The connection to the AMQP broker.
    - channel (pika.Channel): The communication channel to the AMQP broker.
    """

    def __init__(self, amqp_url="amqp://guest:guest@localhost:5672/"):
        """
        Initialize the AMQPClient instance.

        Args:
        - amqp_url (str): The URL for the AMQP broker.
        """
        self.params = pika.URLParameters(amqp_url)
        self.connection = pika.BlockingConnection(self.params)
        self.channel = self.connection.channel()

    def setup_exchange(self, exchange, exchange_type):
        """
        Set up the exchange.

        Args:
        - exchange (str): The exchange name.
        - exchange_type (str): The type of exchange.
        """
        self.exchange = exchange
        self.exchange_type = exchange_type
        self.channel.exchange_declare(
            exchange=exchange, exchange_type=exchange_type, durable=True
        )

    def close(self):
        """Closes the connection to the AMQP broker."""
        self.connection.close()
