"""
World Model Plugin
=================

SK-native world model management plugin for the Reasoning Kernel.
"""

import logging

from semantic_kernel.functions import kernel_function

from ..services import RedisService

logger = logging.getLogger(__name__)


class WorldModelPlugin:
    """
    SK-native plugin for world model operations.

    This plugin provides semantic kernel functions for managing
    world models in the reasoning system.
    """

    def __init__(self, redis_service: RedisService):
        """
        Initialize world model plugin.

        Args:
            redis_service: Redis service for world model storage
        """
        self.redis = redis_service
        self.namespace = "world_model"

    @kernel_function(name="create_world_model", description="Create a new world model")
    async def create_world_model(
        self, name: str, description: str = "", domain: str = "general", context: str = ""
    ) -> str:
        """
        Create a new world model.

        Args:
            name: Name of the world model
            description: Description of the world model
            domain: Domain area for the model (default: general)
            context: Initial context or constraints

        Returns:
            Success message with model ID
        """
        try:
            # Prepare world model data
            world_model_data = {
                "name": name,
                "description": description,
                "domain": domain,
                "context": context,
                "entities": [],
                "relationships": [],
                "constraints": [],
                "assumptions": [],
                "created_at": self._get_timestamp(),
            }

            # Store in Redis with world model namespace
            metadata = {"name": name, "domain": domain, "type": "world_model"}

            model_id = await self.redis.store(
                content=str(world_model_data), namespace=self.namespace, metadata=metadata
            )

            if model_id:
                logger.info(f"Created world model: {name} (ID: {model_id})")
                return f"World model '{name}' created successfully with ID: {model_id}"
            else:
                logger.error(f"Failed to create world model: {name}")
                return f"Failed to create world model: {name}"

        except Exception as e:
            logger.error(f"Error creating world model: {e}")
            return f"Error creating world model: {str(e)}"

    @kernel_function(name="update_world_model", description="Update an existing world model")
    async def update_world_model(
        self, model_id: str, entities: str = "", relationships: str = "", constraints: str = "", assumptions: str = ""
    ) -> str:
        """
        Update an existing world model with new information.

        Args:
            model_id: ID of the world model to update
            entities: Comma-separated list of entities to add
            relationships: Comma-separated list of relationships
            constraints: Comma-separated list of constraints
            assumptions: Comma-separated list of assumptions

        Returns:
            Success or error message
        """
        try:
            # Get existing model
            key = f"{self.namespace}:{model_id}"
            model_data = await self.redis.get_json(key)

            if not model_data:
                return f"World model not found with ID: {model_id}"

            # Parse the stored content (it's stored as string)
            import ast

            try:
                content = ast.literal_eval(model_data.get("content", "{}"))
            except (ValueError, SyntaxError):
                content = {"entities": [], "relationships": [], "constraints": [], "assumptions": []}

            # Add new entities
            if entities:
                new_entities = [e.strip() for e in entities.split(",") if e.strip()]
                if "entities" not in content:
                    content["entities"] = []
                content["entities"].extend(new_entities)
                content["entities"] = list(set(content["entities"]))  # Remove duplicates

            # Add new relationships
            if relationships:
                new_relationships = [r.strip() for r in relationships.split(",") if r.strip()]
                if "relationships" not in content:
                    content["relationships"] = []
                content["relationships"].extend(new_relationships)
                content["relationships"] = list(set(content["relationships"]))

            # Add new constraints
            if constraints:
                new_constraints = [c.strip() for c in constraints.split(",") if c.strip()]
                if "constraints" not in content:
                    content["constraints"] = []
                content["constraints"].extend(new_constraints)
                content["constraints"] = list(set(content["constraints"]))

            # Add new assumptions
            if assumptions:
                new_assumptions = [a.strip() for a in assumptions.split(",") if a.strip()]
                if "assumptions" not in content:
                    content["assumptions"] = []
                content["assumptions"].extend(new_assumptions)
                content["assumptions"] = list(set(content["assumptions"]))

            # Update timestamp
            content["updated_at"] = self._get_timestamp()

            # Store updated model
            success = await self.redis.set_json(key, {**model_data, "content": str(content)})

            if success:
                logger.info(f"Updated world model: {model_id}")
                return f"World model updated successfully: {model_id}"
            else:
                return f"Failed to update world model: {model_id}"

        except Exception as e:
            logger.error(f"Error updating world model: {e}")
            return f"Error updating world model: {str(e)}"

    @kernel_function(name="get_world_model", description="Get a world model by ID")
    async def get_world_model(self, model_id: str) -> str:
        """
        Retrieve a world model by ID.

        Args:
            model_id: The world model ID to retrieve

        Returns:
            World model information as formatted string
        """
        try:
            key = f"{self.namespace}:{model_id}"
            model_data = await self.redis.get_json(key)

            if not model_data:
                return f"World model not found with ID: {model_id}"

            # Parse the content
            import ast

            try:
                content = ast.literal_eval(model_data.get("content", "{}"))
            except (ValueError, SyntaxError):
                content = {}

            metadata = model_data.get("metadata", {})

            # Format output
            result = f"World Model: {metadata.get('name', 'Unnamed')}\n"
            result += f"ID: {model_id}\n"
            result += f"Domain: {metadata.get('domain', 'general')}\n"
            result += f"Description: {content.get('description', 'No description')}\n"
            result += f"Context: {content.get('context', 'No context')}\n\n"

            # Entities
            entities = content.get("entities", [])
            if entities:
                result += f"Entities ({len(entities)}):\n"
                for i, entity in enumerate(entities, 1):
                    result += f"  {i}. {entity}\n"
                result += "\n"

            # Relationships
            relationships = content.get("relationships", [])
            if relationships:
                result += f"Relationships ({len(relationships)}):\n"
                for i, rel in enumerate(relationships, 1):
                    result += f"  {i}. {rel}\n"
                result += "\n"

            # Constraints
            constraints = content.get("constraints", [])
            if constraints:
                result += f"Constraints ({len(constraints)}):\n"
                for i, constraint in enumerate(constraints, 1):
                    result += f"  {i}. {constraint}\n"
                result += "\n"

            # Assumptions
            assumptions = content.get("assumptions", [])
            if assumptions:
                result += f"Assumptions ({len(assumptions)}):\n"
                for i, assumption in enumerate(assumptions, 1):
                    result += f"  {i}. {assumption}\n"
                result += "\n"

            # Timestamps
            if content.get("created_at"):
                result += f"Created: {content['created_at']}\n"
            if content.get("updated_at"):
                result += f"Updated: {content['updated_at']}\n"

            logger.info(f"Retrieved world model: {model_id}")
            return result.strip()

        except Exception as e:
            logger.error(f"Error retrieving world model: {e}")
            return f"Error retrieving world model: {str(e)}"

    @kernel_function(name="list_world_models", description="List all world models")
    async def list_world_models(self, domain: str = "") -> str:
        """
        List all world models, optionally filtered by domain.

        Args:
            domain: Optional domain filter

        Returns:
            List of world models as formatted string
        """
        try:
            # Search for world models
            if domain:
                search_query = f"domain:{domain}"
            else:
                search_query = "*"

            models = await self.redis.search(search_query, self.namespace, 100)

            if models:
                result = f"World Models ({len(models)}):\n\n"

                for i, model in enumerate(models, 1):
                    model_id = model.get("id", "unknown")
                    metadata = model.get("metadata", {})
                    name = metadata.get("name", "Unnamed")
                    model_domain = metadata.get("domain", "general")

                    # Parse content for summary
                    try:
                        import ast

                        content = ast.literal_eval(model.get("content", "{}"))
                        entity_count = len(content.get("entities", []))
                        rel_count = len(content.get("relationships", []))
                    except (ValueError, SyntaxError):
                        entity_count = 0
                        rel_count = 0

                    result += f"{i}. {name} [{model_domain}]\n"
                    result += f"   ID: {model_id}\n"
                    result += f"   Entities: {entity_count}, Relationships: {rel_count}\n\n"

                logger.info(f"Listed {len(models)} world models")
                return result.strip()
            else:
                filter_text = f" in domain '{domain}'" if domain else ""
                logger.info(f"No world models found{filter_text}")
                return f"No world models found{filter_text}"

        except Exception as e:
            logger.error(f"Error listing world models: {e}")
            return f"Error listing world models: {str(e)}"

    @kernel_function(name="query_world_model", description="Query a world model for information")
    async def query_world_model(self, model_id: str, query: str, query_type: str = "general") -> str:
        """
        Query a world model for specific information.

        Args:
            model_id: ID of the world model to query
            query: The query to execute
            query_type: Type of query (entities, relationships, constraints, assumptions, general)

        Returns:
            Query results as formatted string
        """
        try:
            # Get the world model
            key = f"{self.namespace}:{model_id}"
            model_data = await self.redis.get_json(key)

            if not model_data:
                return f"World model not found with ID: {model_id}"

            # Parse content
            import ast

            try:
                content = ast.literal_eval(model_data.get("content", "{}"))
            except (ValueError, SyntaxError):
                content = {}

            metadata = model_data.get("metadata", {})
            query_lower = query.lower()

            results = []

            # Query based on type
            if query_type == "entities" or query_type == "general":
                entities = content.get("entities", [])
                matching_entities = [e for e in entities if query_lower in e.lower()]
                if matching_entities:
                    results.append(f"Matching Entities: {', '.join(matching_entities)}")

            if query_type == "relationships" or query_type == "general":
                relationships = content.get("relationships", [])
                matching_relationships = [r for r in relationships if query_lower in r.lower()]
                if matching_relationships:
                    results.append(f"Matching Relationships: {', '.join(matching_relationships)}")

            if query_type == "constraints" or query_type == "general":
                constraints = content.get("constraints", [])
                matching_constraints = [c for c in constraints if query_lower in c.lower()]
                if matching_constraints:
                    results.append(f"Matching Constraints: {', '.join(matching_constraints)}")

            if query_type == "assumptions" or query_type == "general":
                assumptions = content.get("assumptions", [])
                matching_assumptions = [a for a in assumptions if query_lower in a.lower()]
                if matching_assumptions:
                    results.append(f"Matching Assumptions: {', '.join(matching_assumptions)}")

            if results:
                model_name = metadata.get("name", "Unnamed")
                result = f"Query Results for '{model_name}' (Query: '{query}'):\n\n"
                result += "\n".join(results)

                logger.info(f"Queried world model {model_id} with query: {query}")
                return result
            else:
                logger.info(f"No matches found for query '{query}' in model {model_id}")
                return f"No matches found for query '{query}' in the world model"

        except Exception as e:
            logger.error(f"Error querying world model: {e}")
            return f"Error querying world model: {str(e)}"

    @kernel_function(name="delete_world_model", description="Delete a world model")
    async def delete_world_model(self, model_id: str) -> str:
        """
        Delete a world model by ID.

        Args:
            model_id: The world model ID to delete

        Returns:
            Success or error message
        """
        try:
            key = f"{self.namespace}:{model_id}"

            # Check if exists first
            exists = await self.redis.exists(key)
            if not exists:
                return f"World model not found with ID: {model_id}"

            # Delete from Redis
            deleted = await self.redis.delete(key)

            if deleted:
                logger.info(f"Deleted world model: {model_id}")
                return f"World model deleted successfully: {model_id}"
            else:
                logger.error(f"Failed to delete world model: {model_id}")
                return f"Failed to delete world model: {model_id}"

        except Exception as e:
            logger.error(f"Error deleting world model: {e}")
            return f"Error deleting world model: {str(e)}"

    def _get_timestamp(self) -> str:
        """Get current timestamp."""
        from datetime import datetime

        return datetime.now().isoformat()


# Factory function
def create_world_model_plugin(redis_service: RedisService) -> WorldModelPlugin:
    """Create a world model plugin instance."""
    return WorldModelPlugin(redis_service)
