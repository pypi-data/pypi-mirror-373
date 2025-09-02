"""
SQLAlchemy-based search service for Memori v2.0
Provides cross-database full-text search capabilities
"""

from datetime import datetime
from typing import Any, Dict, List, Optional

from loguru import logger
from sqlalchemy import and_, desc, or_, text
from sqlalchemy.orm import Session

from .models import LongTermMemory, ShortTermMemory


class SearchService:
    """Cross-database search service using SQLAlchemy"""

    def __init__(self, session: Session, database_type: str):
        self.session = session
        self.database_type = database_type

    def search_memories(
        self,
        query: str,
        namespace: str = "default",
        category_filter: Optional[List[str]] = None,
        limit: int = 10,
        memory_types: Optional[List[str]] = None,
    ) -> List[Dict[str, Any]]:
        """
        Search memories across different database backends

        Args:
            query: Search query string
            namespace: Memory namespace
            category_filter: List of categories to filter by
            limit: Maximum number of results
            memory_types: Types of memory to search ('short_term', 'long_term', or both)

        Returns:
            List of memory dictionaries with search metadata
        """
        if not query or not query.strip():
            return self._get_recent_memories(
                namespace, category_filter, limit, memory_types
            )

        results = []

        # Determine which memory types to search
        search_short_term = not memory_types or "short_term" in memory_types
        search_long_term = not memory_types or "long_term" in memory_types

        try:
            # Try database-specific full-text search first
            if self.database_type == "sqlite":
                results = self._search_sqlite_fts(
                    query,
                    namespace,
                    category_filter,
                    limit,
                    search_short_term,
                    search_long_term,
                )
            elif self.database_type == "mysql":
                results = self._search_mysql_fulltext(
                    query,
                    namespace,
                    category_filter,
                    limit,
                    search_short_term,
                    search_long_term,
                )
            elif self.database_type == "postgresql":
                results = self._search_postgresql_fts(
                    query,
                    namespace,
                    category_filter,
                    limit,
                    search_short_term,
                    search_long_term,
                )

            # If no results or full-text search failed, fall back to LIKE search
            if not results:
                results = self._search_like_fallback(
                    query,
                    namespace,
                    category_filter,
                    limit,
                    search_short_term,
                    search_long_term,
                )

        except Exception as e:
            logger.warning(f"Full-text search failed: {e}, falling back to LIKE search")
            results = self._search_like_fallback(
                query,
                namespace,
                category_filter,
                limit,
                search_short_term,
                search_long_term,
            )

        return self._rank_and_limit_results(results, limit)

    def _search_sqlite_fts(
        self,
        query: str,
        namespace: str,
        category_filter: Optional[List[str]],
        limit: int,
        search_short_term: bool,
        search_long_term: bool,
    ) -> List[Dict[str, Any]]:
        """Search using SQLite FTS5"""
        try:
            # Build FTS query
            fts_query = f'"{query.strip()}"'

            # Build category filter
            category_clause = ""
            params = {"fts_query": fts_query, "namespace": namespace}

            if category_filter:
                category_placeholders = ",".join(
                    [f":cat_{i}" for i in range(len(category_filter))]
                )
                category_clause = (
                    f"AND fts.category_primary IN ({category_placeholders})"
                )
                for i, cat in enumerate(category_filter):
                    params[f"cat_{i}"] = cat

            # SQLite FTS5 search query
            sql_query = f"""
                SELECT
                    fts.memory_id, fts.memory_type, fts.category_primary,
                    CASE
                        WHEN fts.memory_type = 'short_term' THEN st.processed_data
                        WHEN fts.memory_type = 'long_term' THEN lt.processed_data
                    END as processed_data,
                    CASE
                        WHEN fts.memory_type = 'short_term' THEN st.importance_score
                        WHEN fts.memory_type = 'long_term' THEN lt.importance_score
                        ELSE 0.5
                    END as importance_score,
                    CASE
                        WHEN fts.memory_type = 'short_term' THEN st.created_at
                        WHEN fts.memory_type = 'long_term' THEN lt.created_at
                    END as created_at,
                    fts.summary,
                    rank as search_score,
                    'sqlite_fts5' as search_strategy
                FROM memory_search_fts fts
                LEFT JOIN short_term_memory st ON fts.memory_id = st.memory_id AND fts.memory_type = 'short_term'
                LEFT JOIN long_term_memory lt ON fts.memory_id = lt.memory_id AND fts.memory_type = 'long_term'
                WHERE memory_search_fts MATCH :fts_query AND fts.namespace = :namespace
                {category_clause}
                ORDER BY rank, importance_score DESC
                LIMIT {limit}
            """

            result = self.session.execute(text(sql_query), params)
            return [dict(row) for row in result]

        except Exception as e:
            logger.debug(f"SQLite FTS5 search failed: {e}")
            # Roll back the transaction to recover from error state
            self.session.rollback()
            return []

    def _search_mysql_fulltext(
        self,
        query: str,
        namespace: str,
        category_filter: Optional[List[str]],
        limit: int,
        search_short_term: bool,
        search_long_term: bool,
    ) -> List[Dict[str, Any]]:
        """Search using MySQL FULLTEXT"""
        results = []

        try:
            # Search short-term memory if requested
            if search_short_term:
                short_query = self.session.query(ShortTermMemory).filter(
                    ShortTermMemory.namespace == namespace
                )

                # Add FULLTEXT search
                fulltext_condition = text(
                    "MATCH(searchable_content, summary) AGAINST(:query IN NATURAL LANGUAGE MODE)"
                ).params(query=query)
                short_query = short_query.filter(fulltext_condition)

                # Add category filter
                if category_filter:
                    short_query = short_query.filter(
                        ShortTermMemory.category_primary.in_(category_filter)
                    )

                # Add relevance score
                short_results = self.session.execute(
                    short_query.statement.add_columns(
                        text(
                            "MATCH(searchable_content, summary) AGAINST(:query IN NATURAL LANGUAGE MODE) as search_score"
                        ).params(query=query),
                        text("'short_term' as memory_type"),
                        text("'mysql_fulltext' as search_strategy"),
                    )
                ).fetchall()

                results.extend([dict(row) for row in short_results])

            # Search long-term memory if requested
            if search_long_term:
                long_query = self.session.query(LongTermMemory).filter(
                    LongTermMemory.namespace == namespace
                )

                # Add FULLTEXT search
                fulltext_condition = text(
                    "MATCH(searchable_content, summary) AGAINST(:query IN NATURAL LANGUAGE MODE)"
                ).params(query=query)
                long_query = long_query.filter(fulltext_condition)

                # Add category filter
                if category_filter:
                    long_query = long_query.filter(
                        LongTermMemory.category_primary.in_(category_filter)
                    )

                # Add relevance score
                long_results = self.session.execute(
                    long_query.statement.add_columns(
                        text(
                            "MATCH(searchable_content, summary) AGAINST(:query IN NATURAL LANGUAGE MODE) as search_score"
                        ).params(query=query),
                        text("'long_term' as memory_type"),
                        text("'mysql_fulltext' as search_strategy"),
                    )
                ).fetchall()

                results.extend([dict(row) for row in long_results])

            return results

        except Exception as e:
            logger.debug(f"MySQL FULLTEXT search failed: {e}")
            # Roll back the transaction to recover from error state
            self.session.rollback()
            return []

    def _search_postgresql_fts(
        self,
        query: str,
        namespace: str,
        category_filter: Optional[List[str]],
        limit: int,
        search_short_term: bool,
        search_long_term: bool,
    ) -> List[Dict[str, Any]]:
        """Search using PostgreSQL tsvector"""
        results = []

        try:
            # Prepare query for tsquery - handle spaces and special characters
            # Convert simple query to tsquery format (join words with &)
            tsquery_text = " & ".join(query.split())

            # Search short-term memory if requested
            if search_short_term:
                short_query = self.session.query(ShortTermMemory).filter(
                    ShortTermMemory.namespace == namespace
                )

                # Add tsvector search
                ts_query = text(
                    "search_vector @@ to_tsquery('english', :query)"
                ).params(query=tsquery_text)
                short_query = short_query.filter(ts_query)

                # Add category filter
                if category_filter:
                    short_query = short_query.filter(
                        ShortTermMemory.category_primary.in_(category_filter)
                    )

                # Add relevance score
                short_results = self.session.execute(
                    short_query.statement.add_columns(
                        text(
                            "ts_rank(search_vector, to_tsquery('english', :query)) as search_score"
                        ).params(query=tsquery_text),
                        text("'short_term' as memory_type"),
                        text("'postgresql_fts' as search_strategy"),
                    ).order_by(text("search_score DESC"))
                ).fetchall()

                results.extend([dict(row) for row in short_results])

            # Search long-term memory if requested
            if search_long_term:
                long_query = self.session.query(LongTermMemory).filter(
                    LongTermMemory.namespace == namespace
                )

                # Add tsvector search
                ts_query = text(
                    "search_vector @@ to_tsquery('english', :query)"
                ).params(query=tsquery_text)
                long_query = long_query.filter(ts_query)

                # Add category filter
                if category_filter:
                    long_query = long_query.filter(
                        LongTermMemory.category_primary.in_(category_filter)
                    )

                # Add relevance score
                long_results = self.session.execute(
                    long_query.statement.add_columns(
                        text(
                            "ts_rank(search_vector, to_tsquery('english', :query)) as search_score"
                        ).params(query=tsquery_text),
                        text("'long_term' as memory_type"),
                        text("'postgresql_fts' as search_strategy"),
                    ).order_by(text("search_score DESC"))
                ).fetchall()

                results.extend([dict(row) for row in long_results])

            return results

        except Exception as e:
            logger.debug(f"PostgreSQL FTS search failed: {e}")
            # Roll back the transaction to recover from error state
            self.session.rollback()
            return []

    def _search_like_fallback(
        self,
        query: str,
        namespace: str,
        category_filter: Optional[List[str]],
        limit: int,
        search_short_term: bool,
        search_long_term: bool,
    ) -> List[Dict[str, Any]]:
        """Fallback LIKE-based search"""
        results = []
        search_pattern = f"%{query}%"

        # Search short-term memory
        if search_short_term:
            short_query = self.session.query(ShortTermMemory).filter(
                and_(
                    ShortTermMemory.namespace == namespace,
                    or_(
                        ShortTermMemory.searchable_content.like(search_pattern),
                        ShortTermMemory.summary.like(search_pattern),
                    ),
                )
            )

            if category_filter:
                short_query = short_query.filter(
                    ShortTermMemory.category_primary.in_(category_filter)
                )

            short_results = (
                short_query.order_by(
                    desc(ShortTermMemory.importance_score),
                    desc(ShortTermMemory.created_at),
                )
                .limit(limit)
                .all()
            )

            for result in short_results:
                memory_dict = {
                    "memory_id": result.memory_id,
                    "memory_type": "short_term",
                    "processed_data": result.processed_data,
                    "importance_score": result.importance_score,
                    "created_at": result.created_at,
                    "summary": result.summary,
                    "category_primary": result.category_primary,
                    "search_score": 0.4,  # Fixed score for LIKE search
                    "search_strategy": f"{self.database_type}_like_fallback",
                }
                results.append(memory_dict)

        # Search long-term memory
        if search_long_term:
            long_query = self.session.query(LongTermMemory).filter(
                and_(
                    LongTermMemory.namespace == namespace,
                    or_(
                        LongTermMemory.searchable_content.like(search_pattern),
                        LongTermMemory.summary.like(search_pattern),
                    ),
                )
            )

            if category_filter:
                long_query = long_query.filter(
                    LongTermMemory.category_primary.in_(category_filter)
                )

            long_results = (
                long_query.order_by(
                    desc(LongTermMemory.importance_score),
                    desc(LongTermMemory.created_at),
                )
                .limit(limit)
                .all()
            )

            for result in long_results:
                memory_dict = {
                    "memory_id": result.memory_id,
                    "memory_type": "long_term",
                    "processed_data": result.processed_data,
                    "importance_score": result.importance_score,
                    "created_at": result.created_at,
                    "summary": result.summary,
                    "category_primary": result.category_primary,
                    "search_score": 0.4,  # Fixed score for LIKE search
                    "search_strategy": f"{self.database_type}_like_fallback",
                }
                results.append(memory_dict)

        return results

    def _get_recent_memories(
        self,
        namespace: str,
        category_filter: Optional[List[str]],
        limit: int,
        memory_types: Optional[List[str]],
    ) -> List[Dict[str, Any]]:
        """Get recent memories when no search query is provided"""
        results = []

        search_short_term = not memory_types or "short_term" in memory_types
        search_long_term = not memory_types or "long_term" in memory_types

        # Get recent short-term memories
        if search_short_term:
            short_query = self.session.query(ShortTermMemory).filter(
                ShortTermMemory.namespace == namespace
            )

            if category_filter:
                short_query = short_query.filter(
                    ShortTermMemory.category_primary.in_(category_filter)
                )

            short_results = (
                short_query.order_by(desc(ShortTermMemory.created_at))
                .limit(limit // 2)
                .all()
            )

            for result in short_results:
                memory_dict = {
                    "memory_id": result.memory_id,
                    "memory_type": "short_term",
                    "processed_data": result.processed_data,
                    "importance_score": result.importance_score,
                    "created_at": result.created_at,
                    "summary": result.summary,
                    "category_primary": result.category_primary,
                    "search_score": 1.0,
                    "search_strategy": "recent_memories",
                }
                results.append(memory_dict)

        # Get recent long-term memories
        if search_long_term:
            long_query = self.session.query(LongTermMemory).filter(
                LongTermMemory.namespace == namespace
            )

            if category_filter:
                long_query = long_query.filter(
                    LongTermMemory.category_primary.in_(category_filter)
                )

            long_results = (
                long_query.order_by(desc(LongTermMemory.created_at))
                .limit(limit // 2)
                .all()
            )

            for result in long_results:
                memory_dict = {
                    "memory_id": result.memory_id,
                    "memory_type": "long_term",
                    "processed_data": result.processed_data,
                    "importance_score": result.importance_score,
                    "created_at": result.created_at,
                    "summary": result.summary,
                    "category_primary": result.category_primary,
                    "search_score": 1.0,
                    "search_strategy": "recent_memories",
                }
                results.append(memory_dict)

        return results

    def _rank_and_limit_results(
        self, results: List[Dict[str, Any]], limit: int
    ) -> List[Dict[str, Any]]:
        """Rank and limit search results"""
        # Calculate composite score
        for result in results:
            search_score = result.get("search_score", 0.4)
            importance_score = result.get("importance_score", 0.5)
            recency_score = self._calculate_recency_score(result.get("created_at"))

            # Weighted composite score
            result["composite_score"] = (
                search_score * 0.5 + importance_score * 0.3 + recency_score * 0.2
            )

        # Sort by composite score and limit
        results.sort(key=lambda x: x.get("composite_score", 0), reverse=True)
        return results[:limit]

    def _calculate_recency_score(self, created_at) -> float:
        """Calculate recency score (0-1, newer = higher)"""
        try:
            if not created_at:
                return 0.0

            if isinstance(created_at, str):
                created_at = datetime.fromisoformat(created_at.replace("Z", "+00:00"))

            days_old = (datetime.now() - created_at).days
            return max(0, 1 - (days_old / 30))  # Full score for recent, 0 after 30 days
        except:
            return 0.0
