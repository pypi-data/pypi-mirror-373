#!/usr/bin/env python3

import asyncio
import sys
import logging
from .server_fixed import main

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Server stopped by user", file=sys.stderr)
    except Exception as e:
        print(f"Server failed to start: {e}", file=sys.stderr)
        sys.exit(1)