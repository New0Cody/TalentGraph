import json
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


def load_json(filename):
    with open(filename, "r", encoding="utf-8") as file:
        return json.load(file)


def create_candidate(candidate):

    query = """
    MERGE (c:Candidate {
        id: $id,
        name: $name,
        experience: $experience,
        location: $location
    })

    WITH c

    UNWIND $skills AS skill_name

    MERGE (s:Skill {
        name: skill_name
    })

    MERGE (c)-[:HAS_SKILL]->(s)

    WITH DISTINCT c

    UNWIND $projects AS project_data

    MERGE (p:Project {
        name: project_data.name
    })

    MERGE (i:Industry {
        name: project_data.industry
    })

    MERGE (c)-[:WORKED_ON]->(p)

    MERGE (p)-[:IN_DOMAIN]->(i)

    RETURN 1 AS success
    """

    driver.execute_query(
        query,
        id=candidate["id"],
        name=candidate["name"],
        experience=candidate["experience"],
        location=candidate["location"],
        skills=candidate["skills"],
        projects=candidate["projects"]
    )
def create_skill_relationships():

    relationships = load_json("../data/skill_relationships.json")

    query = """
    MERGE (s1:Skill {
        name: $skill
    })

    WITH s1

    UNWIND $related_to AS related_skill

    MERGE (s2:Skill {
        name: related_skill
    })

    MERGE (s1)-[:RELATED_TO]->(s2)

    RETURN 1 AS success
    """

    for relationship in relationships:

        driver.execute_query(
            query,
            skill=relationship["skill"],
            related_to=relationship["related_to"]
        )

def seed_database():

    candidates = load_json("../data/candidates.json")

    for candidate in candidates:
        create_candidate(candidate)
    create_skill_relationships()
    print("Candidates seeded successfully!")


if __name__ == "__main__":
    seed_database()