import os

class FairdConfig:
    def __init__(self, config_file):
        self.config = {}
        self.load_config(config_file)

    def load_config(self, config_file):
        if not os.path.exists(config_file):
            raise FileNotFoundError(f"faird配置文件 {config_file} 不存在")
        with open(config_file, 'r', encoding='utf-8') as file:
            for line in file:
                line = line.strip()
                if line and not line.startswith('#') and not line.startswith('['):
                    key, value = line.split('=', 1)
                    self.config[key.strip()] = value.strip()

    def get(self, key, default=None):
        return self.config.get(key, default)

    @property
    def name(self):
        return self.get('host.name')

    @property
    def title(self):
        return self.get('host.title')

    @property
    def position(self):
        pos = self.get('host.position')
        return tuple(map(float, pos.split(','))) if pos else None

    @property
    def location(self):
        return self.get('host.location')

    @property
    def domain(self):
        return self.get('host.domain')

    @property
    def port(self):
        return int(self.get('host.port', 0))

    @property
    def external_domain(self):
        return self.get('host.external.domain')

    @property
    def external_port(self):
        return int(self.get('host.external.port', 0))

    @property
    def controld_address(self):
        return self.get('controld.address', '')

    @property
    def domain_id(self):
        return self.get('domain_id', '')

    @property
    def register_to_controld(self):
        return self.get('register_to_controld', 'false').lower()

    @property
    def public_key(self):
        return self.get('public_key')

    @property
    def log_path(self):
        return self.get('log.path')

    @property
    def metacat_url(self):
        return self.get('metacat_url')

    @property
    def metacat_token(self):
        return self.get('metacat_token')

    @property
    def access_mode(self):
        return self.get('access_mode', 'neo4j')

    @property
    def mongo_db_url(self):
        return self.get('mongo_db_url')

    @property
    def storage_local_path(self):
        return self.get('storage.local.path')

    @property
    def instrument_info(self):
        return self.get('instrument.info')

    @property
    def network_link_info(self):
        return self.get('network.link.info')

    @property
    def neo4j_url(self):
        return self.get('neo4j_url')

    @property
    def neo4j_user(self):
        return self.get('neo4j_user')

    @property
    def neo4j_password(self):
        return self.get('neo4j_password')

    @property
    def data_mongodb_host(self):
        return self.get('data.mongodb.host', '')

    @property
    def data_mongodb_port(self):
        return self.get('data.mongodb.port', '')

    @property
    def data_mongodb_database(self):
        return self.get('data.mongodb.database', '')

    @property
    def data_mongodb_collection(self):
        return self.get('data.mongodb.collection', '')

    @property
    def data_mongodb_username(self):
        return self.get('data.mongodb.username', '')

    @property
    def data_mongodb_password(self):
        return self.get('data.mongodb.password', '')

    @property
    def dataset_base_path_field(self):
        return self.get('dataset.base.path.field', '')

class FairdConfigManager:
    _config = None

    @classmethod
    def load_config(cls, config_file):
        cls._config = FairdConfig(config_file)

    @classmethod
    def get_config(cls):
        if cls._config is None:
            raise Exception("Faird Config not loaded")
        return cls._config