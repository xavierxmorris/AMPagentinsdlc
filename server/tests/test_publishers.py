import unittest
import json
from typing import Dict, Any
from flask import Flask, Response
from models import Publisher, Category, Game, db, init_db
from routes.publishers import publishers_bp

class TestPublishersRoutes(unittest.TestCase):
    # Test data as complete objects
    TEST_DATA: Dict[str, Any] = {
        "publishers": [
            {"name": "DevGames Inc", "description": "A publisher of developer-themed games"},
            {"name": "Scrum Masters", "description": "Makers of agile-inspired games"}
        ],
        "categories": [
            {"name": "Strategy"}
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
                "publisher_index": 1,
                "category_index": 0,
                "star_rating": 4.2
            }
        ]
    }

    # API paths
    PUBLISHERS_API_PATH: str = '/api/publishers'

    def setUp(self) -> None:
        """Set up test database and seed data"""
        self.app = Flask(__name__)
        self.app.config['TESTING'] = True
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

        # Register the publishers blueprint
        self.app.register_blueprint(publishers_bp)

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

    def test_get_publishers_success(self) -> None:
        """Test successful retrieval of all publishers"""
        response = self.client.get(self.PUBLISHERS_API_PATH)
        data = self._get_response_data(response)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(data), len(self.TEST_DATA["publishers"]))

        for i, publisher_data in enumerate(data):
            test_publisher = self.TEST_DATA["publishers"][i]
            self.assertEqual(publisher_data['name'], test_publisher["name"])
            self.assertEqual(publisher_data['description'], test_publisher["description"])

    def test_get_publishers_structure(self) -> None:
        """Test the response structure for publishers"""
        response = self.client.get(self.PUBLISHERS_API_PATH)
        data = self._get_response_data(response)

        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(data, list)
        self.assertEqual(len(data), len(self.TEST_DATA["publishers"]))

        required_fields = ['id', 'name', 'description', 'game_count']
        for field in required_fields:
            self.assertIn(field, data[0])

    def test_get_publishers_game_count(self) -> None:
        """Test that game_count reflects the number of associated games"""
        response = self.client.get(self.PUBLISHERS_API_PATH)
        data = self._get_response_data(response)

        self.assertEqual(response.status_code, 200)
        for publisher_data in data:
            self.assertGreaterEqual(publisher_data['game_count'], 0)

    def test_get_publisher_by_id_success(self) -> None:
        """Test successful retrieval of a single publisher by ID"""
        response = self.client.get(self.PUBLISHERS_API_PATH)
        publishers = self._get_response_data(response)
        publisher_id = publishers[0]['id']

        response = self.client.get(f'{self.PUBLISHERS_API_PATH}/{publisher_id}')
        data = self._get_response_data(response)

        first_publisher = self.TEST_DATA["publishers"][0]
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['name'], first_publisher["name"])
        self.assertEqual(data['description'], first_publisher["description"])

    def test_get_publisher_by_id_not_found(self) -> None:
        """Test retrieval of a non-existent publisher by ID"""
        response = self.client.get(f'{self.PUBLISHERS_API_PATH}/999')
        data = self._get_response_data(response)

        self.assertEqual(response.status_code, 404)
        self.assertEqual(data['error'], "Publisher not found")

if __name__ == '__main__':
    unittest.main()
