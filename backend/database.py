import os

from dotenv import load_dotenv
from neo4j import GraphDatabase

load_dotenv()

URI = os.getenv("COGNODB_URI")
USERNAME = os.getenv("COGNODB_USERNAME")
PASSWORD = os.getenv("COGNODB_PASSWORD")

driver = GraphDatabase.driver(
    URI,
    auth=(USERNAME, PASSWORD)
)


def seed_database():
    driver.execute_query(
        """
        MERGE (typescript:Skill {name: "TypeScript"})
        MERGE (react:Skill {name: "React"})
        MERGE (javascript:Skill {name: "JavaScript"})
        MERGE (python:Skill {name: "Python"})

        MERGE (typescript)-[:RELATED_TO]->(react)
        MERGE (javascript)-[:RELATED_TO]->(react)

        MERGE (ecommerce:Industry {name: "E-commerce"})
        MERGE (fintech:Industry {name: "FinTech"})

        MERGE (shopEasy:Project {name: "ShopEasy"})
        MERGE (banking:Project {name: "Banking Portal"})

        MERGE (priya:Candidate {
            id: "C001",
            name: "Priya Sharma",
            experience: 5,
            location: "Hyderabad"
        })

        MERGE (rahul:Candidate {
            id: "C002",
            name: "Rahul Kumar",
            experience: 4,
            location: "Bangalore"
        })

        MERGE (ananya:Candidate {
            id: "C003",
            name: "Ananya Reddy",
            experience: 6,
            location: "Chennai"
        })

        MERGE (priya)-[:HAS_SKILL]->(typescript)
        MERGE (rahul)-[:HAS_SKILL]->(javascript)
        MERGE (ananya)-[:HAS_SKILL]->(python)

        MERGE (priya)-[:WORKED_ON]->(shopEasy)
        MERGE (rahul)-[:WORKED_ON]->(shopEasy)
        MERGE (ananya)-[:WORKED_ON]->(banking)

        MERGE (shopEasy)-[:IN_DOMAIN]->(ecommerce)
        MERGE (banking)-[:IN_DOMAIN]->(fintech)

        RETURN "Database seeded successfully" AS message
        """
    )

    print("Database seeded successfully!")
if __name__ == "__main__":
    seed_database()