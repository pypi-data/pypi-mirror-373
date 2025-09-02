class SignalReceiver:
    def __init__(self):
        self.received_data = None

    def receive_data(self, data):
        self.received_data = data