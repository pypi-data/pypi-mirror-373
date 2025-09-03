class KeyType:
    PUBLIC_KEY = "PUBLIC_KEY"
    SHARED_KEY = "SHARED_KEY"
    SELF_KEY = "SELF_KEY"
    PRIVATE_HIDDEN_KEY = "PRIVATE_HIDDEN_KEY"


class KeyStringUtil:
    def __init__(self, full_key_name):
        self._full_key_name = full_key_name
        self._key_name = None
        self._key_type = None
        self._namespace = None
        self._shared_by = None
        self._shared_with = None
        self._is_cached = False
        self._is_hidden = False

        self._evaluate(full_key_name)

    def get_full_key_name(self):
        return self._full_key_name

    def get_key_name(self):
        return self._key_name

    def get_namespace(self):
        return self._namespace

    def get_key_type(self):
        return self._key_type

    def get_shared_by(self):
        return self._shared_by

    def get_shared_with(self):
        return self._shared_with

    def is_cached(self):
        return self._is_cached

    def is_hidden(self):
        return self._is_hidden

    def _evaluate(self, full_key_name):
        split1 = full_key_name.split(":")
        
        if len(split1) > 1:
            if split1[0] == "public" or (split1[0] == "cached" and split1[1] == "public"):
                self._key_type = KeyType.PUBLIC_KEY
            elif split1[0] == "private" or split1[0] == "privatekey":
                self._key_type = KeyType.PRIVATE_HIDDEN_KEY
                self._is_hidden = True

            if split1[0].startswith("@") or split1[1].startswith("@"):
                if self._key_type is None:
                    self._key_type = KeyType.SHARED_KEY
                if split1[0].startswith("@"):
                    self._shared_with = split1[0][1:]
                else:
                    self._shared_with = split1[1][1:]

            split2 = split1[-1].split("@")
            self._key_name = split2[0]
            self._shared_by = split2[1]

            if split1[0] == "cached":
                self._is_cached = True

            if self._shared_by == self._shared_with:
                self._key_type = KeyType.SELF_KEY
        else:
            if split1[0].startswith("_"):
                self._key_type = KeyType.PRIVATE_HIDDEN_KEY
            else:
                self._key_type = KeyType.SELF_KEY

            split2 = split1[0].split("@")
            self._key_name = split2[0]
            self._shared_by = split2[1]

            if self._key_name.startswith("shared_key"):
                self._namespace = None

        if self._shared_by is not None:
            self._shared_by = "@" + self._shared_by
        if self._shared_with is not None:
            self._shared_with = "@" + self._shared_with
        if not self._is_hidden:
            self._is_hidden = self._key_name.startswith("_")
