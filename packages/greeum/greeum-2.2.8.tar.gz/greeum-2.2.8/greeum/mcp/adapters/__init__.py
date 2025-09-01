"""
Greeum MCP 서버 어댑터 패키지
- 환경별 최적화된 MCP 서버 구현
- 공통 인터페이스 기반 어댑터 패턴
"""

from .base_adapter import BaseAdapter

__all__ = ['BaseAdapter']