import uuid


class Snowflake:
    @staticmethod
    def next_id():
        hex = uuid.uuid4().hex
        uuid_int = int(hex, 16)
        uuid_str = str(uuid_int).zfill(32)
        id_str = uuid_str[:19]
        return str(int(id_str))
