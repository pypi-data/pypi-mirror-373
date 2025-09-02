from hashids import Hashids


class HashController:
    def __init__(self):
        self._hashids = Hashids(salt="7013b24ca9ff46188a1fbbb1fd0129e0")

    @property
    def encode(self):
        return self._hashids.encode

    @property
    def decode(self):
        return self._hashids.decode


CoreApiPluginHasher = HashController()
