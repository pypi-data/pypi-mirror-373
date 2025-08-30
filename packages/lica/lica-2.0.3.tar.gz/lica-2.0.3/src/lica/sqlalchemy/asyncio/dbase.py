# ----------------------------------------------------------------------
# Copyright (c) 2024 Rafael Gonzalez.
#
# See the LICENSE file for details
# ----------------------------------------------------------------------

# --------------------
# System wide imports
# -------------------

from typing import Tuple, Any

# ---------------------
# Third party libraries
# ---------------------

import decouple
from sqlalchemy.engine.base import Engine
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

def create_engine_sessionclass(env_var: str = "DATABASE_URL", tag: str = None) -> Tuple[Engine,Any]:
	url = decouple.config(env_var)
	if tag:
		# 'check_same_thread' is only needed in SQLite ....
		engine = create_async_engine(url, logging_name=tag, connect_args={"check_same_thread": False})
	else:
		engine = create_async_engine(url, connect_args={"check_same_thread": False})
	Session = async_sessionmaker(engine, expire_on_commit=False)
	return engine, Session

__all__ = ["create_engine_sessionclass"]
