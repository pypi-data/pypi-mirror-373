from peek_core_api._private.storage.DeclarativeBase import DeclarativeBase
from peek_core_api._private.storage.DeclarativeBase import loadStorageTuples
from peek_plugin_base.storage.AlembicEnvBase import AlembicEnvBase

loadStorageTuples()

alembicEnv = AlembicEnvBase(DeclarativeBase.metadata)
alembicEnv.run()
