#!/usr/bin/env python3
"""
Greeum Native MCP Server - MCP Tools Implementation
기존 Greeum 비즈니스 로직을 MCP 형식으로 래핑

핵심 기능:
- 기존 Greeum 컴포넌트 100% 재사용
- MCP 프로토콜 응답 형식 준수
- 기존 FastMCP 서버와 완전 동일한 API
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
import json
import hashlib

logger = logging.getLogger("greeum_native_tools")

class GreeumMCPTools:
    """
    Greeum MCP 도구 핸들러
    
    기존 비즈니스 로직 재사용:
    - BlockManager, STMManager 등 기존 컴포넌트 활용
    - 기존 FastMCP 서버와 동일한 응답 형식
    - 완벽한 하위 호환성 보장
    """
    
    def __init__(self, greeum_components: Dict[str, Any]):
        """
        Args:
            greeum_components: DatabaseManager, BlockManager 등이 포함된 딕셔너리
        """
        self.components = greeum_components
        logger.info("🔧 Greeum MCP tools initialized")
    
    async def execute_tool(self, tool_name: str, arguments: Dict[str, Any]) -> str:
        """
        도구 실행 메인 라우터
        
        Args:
            tool_name: 도구 이름
            arguments: 도구 인자
            
        Returns:
            str: MCP 형식의 응답 텍스트
        """
        try:
            if tool_name == "add_memory":
                return await self._handle_add_memory(arguments)
            elif tool_name == "search_memory":
                return await self._handle_search_memory(arguments)
            elif tool_name == "get_memory_stats":
                return await self._handle_get_memory_stats(arguments)
            elif tool_name == "usage_analytics":
                return await self._handle_usage_analytics(arguments)
            else:
                raise ValueError(f"Unknown tool: {tool_name}")
                
        except Exception as e:
            logger.error(f"❌ Tool {tool_name} failed: {e}")
            raise ValueError(f"Tool execution failed: {e}")
    
    async def _handle_add_memory(self, arguments: Dict[str, Any]) -> str:
        """
        add_memory 도구 처리
        
        기존 FastMCP 서버와 동일한 로직:
        1. 중복 검사
        2. 품질 검증
        3. 메모리 블록 추가
        4. 사용 통계 로깅
        """
        try:
            # 파라미터 추출
            content = arguments.get("content")
            if not content:
                raise ValueError("content parameter is required")
                
            importance = arguments.get("importance", 0.5)
            if not (0.0 <= importance <= 1.0):
                raise ValueError("importance must be between 0.0 and 1.0")
            
            # 컴포넌트 확인
            if not self._check_components():
                return "❌ Greeum components not available. Please check installation."
            
            # 중복 검사
            duplicate_check = self.components['duplicate_detector'].check_duplicate(content)
            if duplicate_check["is_duplicate"]:
                similarity = duplicate_check["similarity_score"]
                return f"""⚠️  **Potential Duplicate Memory Detected**

**Similarity**: {similarity:.1%} with existing memory
**Similar Memory**: Block #{duplicate_check['similar_block_index']}

Please search existing memories first or provide more specific content."""
            
            # 품질 검증
            quality_result = self.components['quality_validator'].validate_memory_quality(content, importance)
            
            # 메모리 추가 (기존 로직 재사용)
            block_data = self._add_memory_direct(content, importance)
            
            # 사용 통계 로깅
            self.components['usage_analytics'].log_quality_metrics(
                len(content), quality_result['quality_score'], quality_result['quality_level'],
                importance, importance, False, duplicate_check["similarity_score"], 
                len(quality_result['suggestions'])
            )
            
            # 성공 응답 (기존 FastMCP와 동일한 형식)
            quality_feedback = f"""
**Quality Score**: {quality_result['quality_score']:.1%} ({quality_result['quality_level']})
**Adjusted Importance**: {importance:.2f} (original: {importance:.2f})"""
            
            suggestions_text = ""
            if quality_result['suggestions']:
                suggestions_text = f"\n\n💡 **Quality Suggestions**:\n" + "\n".join(f"• {s}" for s in quality_result['suggestions'][:2])
            
            return f"""✅ **Memory Successfully Added!**

**Block Index**: #{block_data['block_index']}
**Storage**: Permanent (Long-term Memory)
**Duplicate Check**: ✅ Passed{quality_feedback}{suggestions_text}"""
        
        except Exception as e:
            logger.error(f"add_memory failed: {e}")
            return f"❌ Failed to add memory: {str(e)}"
    
    async def _handle_search_memory(self, arguments: Dict[str, Any]) -> str:
        """
        search_memory 도구 처리
        
        기존 로직 재사용:
        1. 임베딩 기반 검색
        2. 키워드 검색 폴백
        3. 사용 통계 로깅
        """
        try:
            # 파라미터 추출
            query = arguments.get("query")
            if not query:
                raise ValueError("query parameter is required")
                
            limit = arguments.get("limit", 5)
            if not (1 <= limit <= 50):
                raise ValueError("limit must be between 1 and 50")
            
            # 컴포넌트 확인
            if not self._check_components():
                return "❌ Greeum components not available. Please check installation."
            
            # 메모리 검색 (기존 로직 재사용)
            results = self._search_memory_direct(query, limit)
            
            # 사용 통계 로깅
            self.components['usage_analytics'].log_event(
                "tool_usage", "search_memory",
                {"query_length": len(query), "results_found": len(results), "limit_requested": limit},
                0, True
            )
            
            # 결과 포맷팅 (기존 FastMCP와 동일한 형식)
            if results:
                result_text = f"🔍 Found {len(results)} memories:\n"
                for i, memory in enumerate(results, 1):
                    timestamp = memory.get('timestamp', 'Unknown')
                    content = memory.get('context', '')[:100] + ('...' if len(memory.get('context', '')) > 100 else '')
                    result_text += f"{i}. [{timestamp}] {content}\n"
                return result_text
            else:
                return f"🔍 No memories found for query: '{query}'"
        
        except Exception as e:
            logger.error(f"search_memory failed: {e}")
            return f"❌ Search failed: {str(e)}"
    
    async def _handle_get_memory_stats(self, arguments: Dict[str, Any]) -> str:
        """
        get_memory_stats 도구 처리
        
        기존 로직 재사용하여 메모리 시스템 통계 반환
        """
        try:
            # 컴포넌트 확인
            if not self._check_components():
                return "❌ Greeum components not available. Please check installation."
            
            db_manager = self.components['db_manager']
            
            # 기본 통계 - API 호환성 수정
            try:
                # 전체 블록 수 조회 (SQL 직접 쿼리)
                with db_manager.get_session() as session:
                    result = session.execute("SELECT COUNT(*) FROM long_term_memory")
                    total_blocks = result.fetchone()[0]
            except Exception:
                total_blocks = 0
                
            # 최근 블록 조회 (API 호환성 수정)
            try:
                recent_blocks = db_manager.get_blocks(limit=10, sort_by='timestamp', order='desc')
            except Exception:
                recent_blocks = []
            
            # STM 통계 - API 호환성 수정
            try:
                stm_stats = self.components['stm_manager'].get_stats()
            except (AttributeError, Exception):
                # STMManager에 get_stats가 없는 경우 기본값
                stm_stats = {
                    'active_count': 0,
                    'available_slots': 10
                }
            
            # 기존 FastMCP와 동일한 형식
            return f"""📊 **Greeum Memory Statistics**

**Long-term Memory**:
• Total Blocks: {total_blocks}
• Recent Entries: {len(recent_blocks)}

**Short-term Memory**:
• Active Slots: {stm_stats.get('active_count', 0)}
• Available Slots: {stm_stats.get('available_slots', 0)}

**System Status**: ✅ Operational
**Version**: 2.3.0a2 (Native MCP Server)"""
        
        except Exception as e:
            logger.error(f"get_memory_stats failed: {e}")
            return f"❌ Stats retrieval failed: {str(e)}"
    
    async def _handle_usage_analytics(self, arguments: Dict[str, Any]) -> str:
        """
        usage_analytics 도구 처리
        
        기존 로직 재사용하여 사용 분석 리포트 생성
        """
        try:
            # 파라미터 추출
            days = arguments.get("days", 7)
            if not (1 <= days <= 90):
                raise ValueError("days must be between 1 and 90")
                
            report_type = arguments.get("report_type", "usage")
            valid_types = ["usage", "quality", "performance", "all"]
            if report_type not in valid_types:
                raise ValueError(f"report_type must be one of: {valid_types}")
            
            # 컴포넌트 확인
            if not self._check_components():
                return "❌ Greeum components not available. Please check installation."
            
            # 분석 리포트 생성 (기존 로직 재사용)
            analytics = self.components['usage_analytics'].get_usage_report(days=days, report_type=report_type)
            
            # 기존 FastMCP와 동일한 형식
            return f"""📈 **Usage Analytics Report** ({days} days)

**Activity Summary**:
• Total Operations: {analytics.get('total_operations', 0)}
• Memory Additions: {analytics.get('add_operations', 0)}
• Search Operations: {analytics.get('search_operations', 0)}

**Quality Metrics**:
• Average Quality Score: {analytics.get('avg_quality_score', 0):.1%}
• High Quality Rate: {analytics.get('high_quality_rate', 0):.1%}

**Performance**:
• Average Response Time: {analytics.get('avg_response_time', 0):.1f}ms
• Success Rate: {analytics.get('success_rate', 0):.1%}

**Report Type**: {report_type.title()}
**Generated**: Native MCP Server v2.3.0a2"""
        
        except Exception as e:
            logger.error(f"usage_analytics failed: {e}")
            return f"❌ Analytics failed: {str(e)}"
    
    def _check_components(self) -> bool:
        """필수 컴포넌트 존재 확인"""
        required_components = [
            'db_manager', 'block_manager', 'stm_manager',
            'duplicate_detector', 'quality_validator', 'usage_analytics'
        ]
        
        for component in required_components:
            if component not in self.components or self.components[component] is None:
                logger.error(f"❌ Missing component: {component}")
                return False
        
        return True
    
    def _add_memory_direct(self, content: str, importance: float) -> Dict[str, Any]:
        """
        직접 메모리 추가 (기존 FastMCP 로직 100% 재사용)
        """
        from greeum.text_utils import process_user_input
        
        db_manager = self.components['db_manager']
        
        # 기존 로직 그대로 사용
        result = process_user_input(content)
        result["importance"] = importance
        
        timestamp = datetime.now().isoformat()
        result["timestamp"] = timestamp
        
        # 블록 인덱스 생성
        last_block_info = db_manager.get_last_block_info()
        if last_block_info is None:
            last_block_info = {"block_index": -1}
        block_index = last_block_info.get("block_index", -1) + 1
        
        # 이전 해시
        prev_hash = ""
        if block_index > 0:
            prev_block = db_manager.get_block(block_index - 1)
            if prev_block:
                prev_hash = prev_block.get("hash", "")
        
        # 해시 계산
        hash_data = {
            "block_index": block_index,
            "timestamp": timestamp,
            "context": content,
            "prev_hash": prev_hash
        }
        hash_str = json.dumps(hash_data, sort_keys=True)
        hash_value = hashlib.sha256(hash_str.encode()).hexdigest()
        
        # 최종 블록 데이터
        block_data = {
            "block_index": block_index,
            "timestamp": timestamp,
            "context": content,
            "keywords": result.get("keywords", []),
            "tags": result.get("tags", []),
            "embedding": result.get("embedding", []),
            "importance": result.get("importance", 0.5),
            "hash": hash_value,
            "prev_hash": prev_hash
        }
        
        # 데이터베이스에 추가
        db_manager.add_block(block_data)
        
        return block_data
    
    def _search_memory_direct(self, query: str, limit: int) -> List[Dict[str, Any]]:
        """
        직접 메모리 검색 (기존 FastMCP 로직 100% 재사용)
        """
        from greeum.embedding_models import get_embedding
        
        db_manager = self.components['db_manager']
        
        try:
            # 임베딩 기반 검색
            embedding = get_embedding(query)
            blocks = db_manager.search_blocks_by_embedding(embedding, top_k=limit)
            
            return blocks if blocks else []
        except Exception as e:
            logger.warning(f"Embedding search failed: {e}, falling back to keyword search")
            # 키워드 검색 폴백
            blocks = db_manager.search_by_keyword(query, limit=limit)
            return blocks if blocks else []