import re
from typing import Optional, Type as TypingType, TypeVar, Any, Dict, List
from uuid import UUID
from datetime import datetime

from ... import types as Type

T = TypeVar('T', bound=Type.CalorIAModel)

class RecipeMixin:
    """Mixin class that provides recipe-related MongoDB operations."""

    # No __init__ needed as it will use the parent class's __init__

    def create_recipe(self, recipe: Type.Recipe) -> Optional[Any]:
        """Create a new recipe in the recipes collection.

        Args:
            recipe: Recipe model instance

        Returns:
            The inserted_id if successful, None otherwise
        """
        return self.create_document("recipes", recipe)

    def get_recipe_by_id(self, recipe_id: UUID) -> Optional[Type.Recipe]:
        """Retrieve a recipe by its ID.

        Args:
            recipe_id: UUID of the recipe to retrieve

        Returns:
            Recipe instance if found, None otherwise
        """
        query = {"id": str(recipe_id)}  # Convert UUID to string for MongoDB query
        return self.get_document("recipes", query, Type.Recipe)

    def get_all_recipes(self, skip: int = 0, limit: Optional[int] = None,
                       category: Optional[str] = None, difficulty: Optional[str] = None) -> List[Type.Recipe]:
        """Get all recipes with optional filtering and pagination.

        Args:
            skip: Number of recipes to skip for pagination (default: 0)
            limit: Maximum number of recipes to return (default: None for all recipes)
            category: Filter by recipe category (name or slug)
            difficulty: Filter by difficulty level

        Returns:
            List of Recipe instances
        """
        try:
            db = self.get_db_connection()
            if db is None:
                return []

            collection = db["recipes"]

            # Build query based on filters
            query = {}

            # Handle category filtering - convert category name to category_id
            if category:
                # Try to find the category by slug first, then by name
                category_obj = self.get_category_by_slug(category.lower().replace(' ', '_'))
                if not category_obj:
                    # Try to find by name (case-insensitive)
                    categories = self.get_all_categories()
                    for cat in categories:
                        if cat.name.lower() == category.lower():
                            category_obj = cat
                            break

                if category_obj:
                    query["category_id"] = str(category_obj.id)
                else:
                    # If category not found, return empty list
                    return []

            if difficulty:
                query["difficulty"] = difficulty

            cursor = collection.find(query)

            # Sort recipes by creation date (newest first)
            cursor = cursor.sort("created_at", -1)

            # Apply pagination
            cursor = cursor.skip(skip)
            if limit is not None:
                cursor = cursor.limit(limit)

            recipes = []
            for doc in cursor:
                if '_id' in doc:
                    del doc['_id']
                try:
                    recipe = Type.Recipe.from_dict(doc)
                    recipes.append(recipe)
                except Exception as e:
                    print(f"Error parsing recipe: {e}")
                    continue

            return recipes
        except Exception as e:
            print(f"Error getting recipes: {e}")
            return []

    def update_recipe(self, recipe_id: UUID, recipe_data: Dict[str, Any]) -> bool:
        """Update a recipe by its ID.

        Args:
            recipe_id: UUID of the recipe to update
            recipe_data: Data to update (will be wrapped in $set)

        Returns:
            True if update was successful, False otherwise
        """
        query = {"id": str(recipe_id)}  # Convert UUID to string for MongoDB query

        # Add updated_at timestamp
        recipe_data["updated_at"] = datetime.now()

        return self.update_document("recipes", query, recipe_data)

    def delete_recipe(self, recipe_id: UUID) -> bool:
        """Delete a recipe by its ID.

        Args:
            recipe_id: UUID of the recipe to delete

        Returns:
            True if deletion was successful, False otherwise
        """
        query = {"id": str(recipe_id)}  # Convert UUID to string for MongoDB query
        return self.delete_document("recipes", query)

    def search_recipes(self, search_term: str, skip: int = 0, limit: Optional[int] = 20,
                       category: Optional[str] = None, difficulty: Optional[str] = None,
                       tags: Optional[List[str]] = None) -> List[Type.Recipe]:
        """Search recipes by name, description, tags, or ingredients with optional filters.

        Args:
            search_term: Term to search for in recipe names, descriptions, tags, and ingredients
            skip: Number of recipes to skip for pagination (default: 0)
            limit: Maximum number of recipes to return (default: 20, None for no limit)
            category: Filter by recipe category (name or slug)
            difficulty: Filter by difficulty level
            tags: Filter by specific tag names

        Returns:
            List of matching Recipe instances
        """
        try:
            db = self.get_db_connection()
            if db is None:
                return []

            collection = db["recipes"]

            # Create regex pattern for case-insensitive search
            search_pattern = {"$regex": search_term, "$options": "i"}

            # Build base query for search in name, description, tags, and ingredients
            search_query = {
                "$or": [
                    {"name": search_pattern},
                    {"description": search_pattern},
                    {"legacy_tags": {"$elemMatch": search_pattern}},  # Search in legacy tags
                    {"ingredients.ingredient.name": search_pattern}
                ]
            }

            # Handle category filtering - convert category name to category_id
            if category:
                # Try to find the category by slug first, then by name
                category_obj = self.get_category_by_slug(category.lower().replace(' ', '_'))
                if not category_obj:
                    # Try to find by name (case-insensitive)
                    categories = self.get_all_categories()
                    for cat in categories:
                        if cat.name.lower() == category.lower():
                            category_obj = cat
                            break

                if category_obj:
                    search_query["category_id"] = str(category_obj.id)
                else:
                    # If category not found, return empty list
                    return []

            # Add difficulty filter if provided
            if difficulty:
                search_query["difficulty"] = difficulty

            # Handle tags filtering - convert tag names to tag_ids
            if tags:
                tag_ids = []
                for tag_name in tags:
                    # Try to find the tag by slug first, then by name
                    tag_obj = self.get_tag_by_slug(tag_name.lower().replace(' ', '-'))
                    if not tag_obj:
                        # Try to find by name (case-insensitive)
                        all_tags = self.get_all_tags()
                        for tag in all_tags:
                            if tag.name.lower() == tag_name.lower():
                                tag_obj = tag
                                break

                    if tag_obj:
                        tag_ids.append(str(tag_obj.id))

                if tag_ids:
                    search_query["tag_ids"] = {"$in": tag_ids}

            cursor = collection.find(search_query)

            # Sort by relevance (creation date as proxy)
            cursor = cursor.sort("created_at", -1)

            # Apply pagination
            cursor = cursor.skip(skip)
            if limit is not None:
                cursor = cursor.limit(limit)

            recipes = []
            for doc in cursor:
                if '_id' in doc:
                    del doc['_id']
                try:
                    recipe = Type.Recipe.from_dict(doc)
                    recipes.append(recipe)
                except Exception as e:
                    print(f"Error parsing recipe: {e}")
                    continue

            return recipes
        except Exception as e:
            print(f"Error searching recipes with term '{search_term}': {e}")
            return []

    def get_recipes_by_category(self, category: str, skip: int = 0, limit: Optional[int] = None) -> List[Type.Recipe]:
        """Get recipes by category.

        Args:
            category: Recipe category to filter by
            skip: Number of recipes to skip for pagination
            limit: Maximum number of recipes to return

        Returns:
            List of Recipe instances in the specified category
        """
        return self.get_all_recipes(skip=skip, limit=limit, category=category)

    def get_recipes_by_difficulty(self, difficulty: str, skip: int = 0, limit: Optional[int] = None) -> List[Type.Recipe]:
        """Get recipes by difficulty level.

        Args:
            difficulty: Difficulty level to filter by
            skip: Number of recipes to skip for pagination
            limit: Maximum number of recipes to return

        Returns:
            List of Recipe instances with the specified difficulty
        """
        return self.get_all_recipes(skip=skip, limit=limit, difficulty=difficulty)

    def get_recipes_by_tags(self, tags: List[str], skip: int = 0, limit: Optional[int] = None) -> List[Type.Recipe]:
        """Get recipes that have any of the specified tags.

        Args:
            tags: List of tag names to search for
            skip: Number of recipes to skip for pagination
            limit: Maximum number of recipes to return

        Returns:
            List of Recipe instances that match any of the tags
        """
        try:
            db = self.get_db_connection()
            if db is None:
                return []

            collection = db["recipes"]

            # Convert tag names to tag_ids
            tag_ids = []
            for tag_name in tags:
                # Try to find the tag by slug first, then by name
                tag_obj = self.get_tag_by_slug(tag_name.lower().replace(' ', '-'))
                if not tag_obj:
                    # Try to find by name (case-insensitive)
                    all_tags = self.get_all_tags()
                    for tag in all_tags:
                        if tag.name.lower() == tag_name.lower():
                            tag_obj = tag
                            break

                if tag_obj:
                    tag_ids.append(str(tag_obj.id))

            if not tag_ids:
                # If no valid tags found, return empty list
                return []

            # Query for recipes that have any of the specified tag_ids
            query = {"tag_ids": {"$in": tag_ids}}

            cursor = collection.find(query)

            # Sort by creation date
            cursor = cursor.sort("created_at", -1)

            # Apply pagination
            cursor = cursor.skip(skip)
            if limit is not None:
                cursor = cursor.limit(limit)

            recipes = []
            for doc in cursor:
                if '_id' in doc:
                    del doc['_id']
                try:
                    recipe = Type.Recipe.from_dict(doc)
                    recipes.append(recipe)
                except Exception as e:
                    print(f"Error parsing recipe: {e}")
                    continue

            return recipes
        except Exception as e:
            print(f"Error getting recipes by tags: {e}")
            return []

    def count_recipes(self, search_term: Optional[str] = None, category: Optional[str] = None,
                     difficulty: Optional[str] = None, tags: Optional[List[str]] = None) -> int:
        """Count recipes with optional search and filter criteria.

        Args:
            search_term: Term to search for in recipe names, descriptions, tags, and ingredients
            category: Filter by recipe category (name or slug)
            difficulty: Filter by difficulty level
            tags: Filter by specific tag names

        Returns:
            Total count of matching recipes
        """
        try:
            db = self.get_db_connection()
            if db is None:
                return 0

            collection = db["recipes"]

            # Build query based on parameters
            query = {}

            if search_term:
                # Create regex pattern for case-insensitive search
                search_pattern = {"$regex": search_term, "$options": "i"}

                # Build search query
                query["$or"] = [
                    {"name": search_pattern},
                    {"description": search_pattern},
                    {"legacy_tags": {"$elemMatch": search_pattern}},  # Search in legacy tags
                    {"ingredients.ingredient.name": search_pattern}
                ]

            # Handle category filtering - convert category name to category_id
            if category:
                # Try to find the category by slug first, then by name
                category_obj = self.get_category_by_slug(category.lower().replace(' ', '_'))
                if not category_obj:
                    # Try to find by name (case-insensitive)
                    categories = self.get_all_categories()
                    for cat in categories:
                        if cat.name.lower() == category.lower():
                            category_obj = cat
                            break

                if category_obj:
                    query["category_id"] = str(category_obj.id)
                else:
                    # If category not found, return 0
                    return 0

            if difficulty:
                query["difficulty"] = difficulty

            # Handle tags filtering - convert tag names to tag_ids
            if tags:
                tag_ids = []
                for tag_name in tags:
                    # Try to find the tag by slug first, then by name
                    tag_obj = self.get_tag_by_slug(tag_name.lower().replace(' ', '-'))
                    if not tag_obj:
                        # Try to find by name (case-insensitive)
                        all_tags = self.get_all_tags()
                        for tag in all_tags:
                            if tag.name.lower() == tag_name.lower():
                                tag_obj = tag
                                break

                    if tag_obj:
                        tag_ids.append(str(tag_obj.id))

                if tag_ids:
                    query["tag_ids"] = {"$in": tag_ids}

            return collection.count_documents(query)

        except Exception as e:
            print(f"Error counting recipes: {e}")
            return 0

    def get_popular_recipes(self, limit: int = 10) -> List[Type.Recipe]:
        """Get popular recipes (could be based on usage, ratings, etc.).

        Args:
            limit: Maximum number of recipes to return

        Returns:
            List of popular Recipe instances
        """
        # For now, return most recently created recipes as a proxy for popularity
        # In the future, this could be based on actual usage statistics
        return self.get_all_recipes(limit=limit)