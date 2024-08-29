
class MyClass:

    def __init__(self):
        self._the_secret = 3

    def secret(self):
        return self._the_secret

    def encrypt(self, text):
        assert len(text) > self.secret()
        # not really encrypting, just for test
        return text[self.secret()]

