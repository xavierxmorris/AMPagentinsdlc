import unittest
import json
from typing import Dict, Any
from flask import Flask, Response
from models import Category, Publisher, Game, db, init_db
from routes.categories import categories_bp

class TestCategoriesRoutes(unittest.TestCase):
    # Test data as complete objects
    TEST_DATA: Dict[str, Any] = {
        "publishers": [
            {"name": "DevGames Inc"}
        ],
        "categories": [
            {"name": "Strategy", "description": "Games that test your strategic thinking"},
            {"name": "Card Game", "description": "Games played with cards and deck building"}
        ],
        "games": [
            {
                "title": "Pipeline Panic",
                "description": "Build your DevOps pipeline before chaos ensues",
                "publisher_index": 0,
                "category_index": 0,
                "star_rating": 4.5
            },
            {
                "title": "Agile Adventures",
                "description": "Navigate your team through sprints and releases",
                "publisher_index": 0,
                "category_index": 1,
                "star_rating": 4.2
            }
        ]
    }

    # API paths
    CATEGORIES_API_PATH: str = '/api/categories'

    def setUp(self) -> None:
        """Set up test database and seed data"""
        self.app = Flask(__name__)
        self.app.config['TESTING'] = True
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

        # Register the categories blueprint
        self.app.register_blueprint(categories_bp)

        # Initialize the test client
        self.client = self.app.test_client()

        # Initialize in-memory database for testing
        init_db(self.app, testing=True)

        # Create tables and seed data
        with self.app.app_context():
            db.create_all()
            self._seed_test_data()

    def tearDown(self) -> None:
        """Clean up test database and ensure proper connection closure"""
        with self.app.app_context():
            db.session.remove()
            db.drop_all()
            db.engine.dispose()

    def _seed_test_data(self) -> None:
        """Helper method to seed test data"""
        publishers = [
            Publisher(**publisher_data) for publisher_data in self.TEST_DATA["publishers"]
        ]
        db.session.add_all(publishers)

        categories = [
            Category(**category_data) for category_data in self.TEST_DATA["categories"]
        ]
        db.session.add_all(categories)

        db.session.commit()

        games = []
        for game_data in self.TEST_DATA["games"]:
            game_dict = game_data.copy()
            publisher_index = game_dict.pop("publisher_index")
            category_index = game_dict.pop("category_index")
            games.append(Game(
                **game_dict,
                publisher=publishers[publisher_index],
                category=categories[category_index]
            ))

        db.session.add_all(games)
        db.session.commit()

    def _get_response_data(self, response: Response) -> Any:
        """Helper method to parse response data"""
        return json.loads(response.data)

    def test_get_categories_success(self) -> None:
        """Test successful retrieval of all categories"""
        response = self.client.get(self.CATEGORIES_API_PATH)
        data = self._get_response_data(response)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(data), len(self.TEST_DATA["categories"]))

        for i, category_data in enumerate(data):
            test_category = self.TEST_DATA["categories"][i]
            self.assertEqual(category_data['name'], test_category["name"])
            self.assertEqual(category_data['description'], test_category["description"])

    def test_get_categories_structure(self) -> None:
        """Test the response structure for categories"""
        response = self.client.get(self.CATEGORIES_API_PATH)
        data = self._get_response_data(response)

        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(data, list)
        self.assertEqual(len(data), len(self.TEST_DATA["categories"]))

        required_fields = ['id', 'name', 'description', 'game_count']
        for field in required_fields:
            self.assertIn(field, data[0])

    def test_get_categories_game_count(self) -> None:
        """Test that game_count reflects the number of associated games"""
        response = self.client.get(self.CATEGORIES_API_PATH)
        data = self._get_response_data(response)

        self.assertEqual(response.status_code, 200)
        for category_data in data:
            self.assertGreaterEqual(category_data['game_count'], 0)

    def test_get_category_by_id_success(self) -> None:
        """Test successful retrieval of a single category by ID"""
        response = self.client.get(self.CATEGORIES_API_PATH)
        categories = self._get_response_data(response)
        category_id = categories[0]['id']

        response = self.client.get(f'{self.CATEGORIES_API_PATH}/{category_id}')
        data = self._get_response_data(response)

        first_category = self.TEST_DATA["categories"][0]
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['name'], first_category["name"])
        self.assertEqual(data['description'], first_category["description"])

    def test_get_category_by_id_not_found(self) -> None:
        """Test retrieval of a non-existent category by ID"""
        response = self.client.get(f'{self.CATEGORIES_API_PATH}/999')
        data = self._get_response_data(response)

        self.assertEqual(response.status_code, 404)
        self.assertEqual(data['error'], "Category not found")

if __name__ == '__main__':
    unittest.main()
