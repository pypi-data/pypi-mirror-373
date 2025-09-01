from .sql import iSQLSession


class PostgreSQLSession(iSQLSession):
    "Based on PostgreSQL, change methods as needed"


PostgreSQLSession.register_itself(r"postgresql://")
