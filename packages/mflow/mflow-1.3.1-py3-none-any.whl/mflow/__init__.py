from __future__ import annotations

from importlib import metadata
from typing import Optional

from . import constants

try: 
	__version__ = metadata.version("mflow")
except Exception:
	__version__ = getattr(constants, "VERSION", "0.0.0")

__all__ = ["__version__", "main"]


def main(argv: Optional[list[str]] = None) -> int:
	import sys
	from aiohttp import web
	from .config import init_var
	from .app import init_app

	if argv is not None:
		original_argv = sys.argv
		sys.argv = [original_argv[0], *argv]
	else:
		original_argv = None

	try:
		ok = init_var()
		if not ok:
			return 2
		web.run_app(init_app(), host="0.0.0.0", port=constants.PORT)
		return 0
	except KeyboardInterrupt:
		return 130
	finally:
		if original_argv is not None:
			sys.argv = original_argv


if __name__ == "__main__":  # 允许 python -m mflow 直接运行
	raise SystemExit(main())

