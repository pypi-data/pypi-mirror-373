"""
Knowledge Plugin
===============

SK-native knowledge management plugin for the Reasoning Kernel.
"""

import logging

from semantic_kernel.functions import kernel_function

from ..services import RedisService

logger = logging.getLogger(__name__)


class KnowledgePlugin:
    """
    SK-native plugin for knowledge storage and retrieval operations.

    This plugin provides semantic kernel functions for managing
    knowledge in the reasoning system.
    """

    def __init__(self, redis_service: RedisService):
        """
        Initialize knowledge plugin.

        Args:
            redis_service: Redis service for knowledge storage
        """
        self.redis = redis_service
        self.namespace = "knowledge"

    @kernel_function(name="store_knowledge", description="Store knowledge in the system")
    async def store_knowledge(
        self, content: str, title: str = "", category: str = "general", tags: str = "", source: str = ""
    ) -> str:
        """
        Store knowledge content in the system.

        Args:
            content: The knowledge content to store
            title: Optional title for the knowledge
            category: Category of knowledge (default: general)
            tags: Comma-separated tags for the knowledge
            source: Source of the knowledge

        Returns:
            Knowledge ID if successful, empty string if failed
        """
        try:
            # Prepare metadata
            metadata = {
                "title": title,
                "category": category,
                "tags": [tag.strip() for tag in tags.split(",") if tag.strip()],
                "source": source,
                "type": "knowledge",
            }

            # Store in Redis with knowledge namespace
            knowledge_id = await self.redis.store(content, self.namespace, metadata)

            if knowledge_id:
                logger.info(f"Stored knowledge: {knowledge_id}")
                return f"Knowledge stored successfully with ID: {knowledge_id}"
            else:
                logger.error("Failed to store knowledge")
                return "Failed to store knowledge"

        except Exception as e:
            logger.error(f"Error storing knowledge: {e}")
            return f"Error storing knowledge: {str(e)}"

    @kernel_function(name="search_knowledge", description="Search for knowledge in the system")
    async def search_knowledge(self, query: str, category: str = "", limit: str = "10") -> str:
        """
        Search for knowledge in the system.

        Args:
            query: Search query
            category: Optional category filter
            limit: Maximum number of results (default: 10)

        Returns:
            JSON string of search results
        """
        try:
            # Convert limit to int with validation
            try:
                result_limit = int(limit)
                if result_limit <= 0:
                    result_limit = 10
            except ValueError:
                result_limit = 10

            # Search in knowledge namespace
            if category:
                # Category-specific search
                search_query = f"{query} category:{category}"
            else:
                search_query = query

            results = await self.redis.search(search_query, self.namespace, result_limit)

            if results:
                # Format results for readability
                formatted_results = []
                for result in results:
                    formatted_result = {
                        "id": result.get("id", "unknown"),
                        "title": result.get("metadata", {}).get("title", "Untitled"),
                        "category": result.get("metadata", {}).get("category", "general"),
                        "content": (
                            result.get("content", "")[:200] + "..."
                            if len(result.get("content", "")) > 200
                            else result.get("content", "")
                        ),
                        "tags": result.get("metadata", {}).get("tags", []),
                        "source": result.get("metadata", {}).get("source", ""),
                    }
                    formatted_results.append(formatted_result)

                logger.info(f"Found {len(formatted_results)} knowledge results for query: {query}")

                # Return as formatted string for SK compatibility
                result_str = f"Found {len(formatted_results)} knowledge items:\n\n"
                for i, result in enumerate(formatted_results, 1):
                    result_str += f"{i}. {result['title']} [{result['category']}]\n"
                    result_str += f"   Content: {result['content']}\n"
                    if result["tags"]:
                        result_str += f"   Tags: {', '.join(result['tags'])}\n"
                    if result["source"]:
                        result_str += f"   Source: {result['source']}\n"
                    result_str += "\n"

                return result_str.strip()
            else:
                logger.info(f"No knowledge found for query: {query}")
                return f"No knowledge found for query: {query}"

        except Exception as e:
            logger.error(f"Error searching knowledge: {e}")
            return f"Error searching knowledge: {str(e)}"

    @kernel_function(name="get_knowledge", description="Get specific knowledge by ID")
    async def get_knowledge(self, knowledge_id: str) -> str:
        """
        Retrieve specific knowledge by ID.

        Args:
            knowledge_id: The knowledge ID to retrieve

        Returns:
            Knowledge content or error message
        """
        try:
            # Construct the Redis key
            key = f"{self.namespace}:{knowledge_id}"

            # Get from Redis
            knowledge_data = await self.redis.get_json(key)

            if knowledge_data:
                content = knowledge_data.get("content", "")
                metadata = knowledge_data.get("metadata", {})

                result = f"Knowledge ID: {knowledge_id}\n"
                result += f"Title: {metadata.get('title', 'Untitled')}\n"
                result += f"Category: {metadata.get('category', 'general')}\n"
                result += f"Source: {metadata.get('source', 'Unknown')}\n"
                if metadata.get("tags"):
                    result += f"Tags: {', '.join(metadata['tags'])}\n"
                result += f"\nContent:\n{content}"

                logger.info(f"Retrieved knowledge: {knowledge_id}")
                return result
            else:
                logger.warning(f"Knowledge not found: {knowledge_id}")
                return f"Knowledge not found with ID: {knowledge_id}"

        except Exception as e:
            logger.error(f"Error retrieving knowledge: {e}")
            return f"Error retrieving knowledge: {str(e)}"

    @kernel_function(name="list_knowledge_categories", description="List all knowledge categories")
    async def list_knowledge_categories(self) -> str:
        """
        List all available knowledge categories.

        Returns:
            List of categories as formatted string
        """
        try:
            # Search for all knowledge items
            all_knowledge = await self.redis.search("*", self.namespace, 1000)

            # Extract unique categories
            categories = set()
            for item in all_knowledge:
                category = item.get("metadata", {}).get("category", "general")
                if category:
                    categories.add(category)

            if categories:
                category_list = sorted(list(categories))
                logger.info(f"Found {len(category_list)} knowledge categories")

                result = f"Available Knowledge Categories ({len(category_list)}):\n\n"
                for i, category in enumerate(category_list, 1):
                    result += f"{i}. {category}\n"

                return result.strip()
            else:
                logger.info("No knowledge categories found")
                return "No knowledge categories found"

        except Exception as e:
            logger.error(f"Error listing categories: {e}")
            return f"Error listing categories: {str(e)}"

    @kernel_function(name="delete_knowledge", description="Delete knowledge by ID")
    async def delete_knowledge(self, knowledge_id: str) -> str:
        """
        Delete specific knowledge by ID.

        Args:
            knowledge_id: The knowledge ID to delete

        Returns:
            Success or error message
        """
        try:
            # Construct the Redis key
            key = f"{self.namespace}:{knowledge_id}"

            # Check if exists first
            exists = await self.redis.exists(key)
            if not exists:
                return f"Knowledge not found with ID: {knowledge_id}"

            # Delete from Redis
            deleted = await self.redis.delete(key)

            if deleted:
                logger.info(f"Deleted knowledge: {knowledge_id}")
                return f"Knowledge deleted successfully: {knowledge_id}"
            else:
                logger.error(f"Failed to delete knowledge: {knowledge_id}")
                return f"Failed to delete knowledge: {knowledge_id}"

        except Exception as e:
            logger.error(f"Error deleting knowledge: {e}")
            return f"Error deleting knowledge: {str(e)}"

    @kernel_function(name="get_knowledge_stats", description="Get knowledge system statistics")
    async def get_knowledge_stats(self) -> str:
        """
        Get statistics about the knowledge system.

        Returns:
            Statistics as formatted string
        """
        try:
            # Get all knowledge items
            all_knowledge = await self.redis.search("*", self.namespace, 1000)
            total_items = len(all_knowledge)

            # Count by category
            category_counts = {}
            total_size = 0

            for item in all_knowledge:
                # Count by category
                category = item.get("metadata", {}).get("category", "general")
                category_counts[category] = category_counts.get(category, 0) + 1

                # Calculate approximate size
                content = item.get("content", "")
                total_size += len(content)

            # Format results
            result = "Knowledge System Statistics:\n\n"
            result += f"Total Items: {total_items}\n"
            result += f"Total Content Size: {total_size:,} characters\n"
            result += f"Average Item Size: {total_size // max(total_items, 1):,} characters\n\n"

            if category_counts:
                result += "Items by Category:\n"
                for category, count in sorted(category_counts.items()):
                    result += f"  {category}: {count}\n"

            logger.info(f"Generated knowledge stats: {total_items} items")
            return result.strip()

        except Exception as e:
            logger.error(f"Error getting knowledge stats: {e}")
            return f"Error getting knowledge stats: {str(e)}"


# Factory function
def create_knowledge_plugin(redis_service: RedisService) -> KnowledgePlugin:
    """Create a knowledge plugin instance."""
    return KnowledgePlugin(redis_service)
