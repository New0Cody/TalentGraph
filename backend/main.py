from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os

from dotenv import load_dotenv
from neo4j import GraphDatabase


# -------------------------
# Database connection
# -------------------------

load_dotenv()

URI = os.getenv("COGNODB_URI")
USERNAME = os.getenv("COGNODB_USERNAME")
PASSWORD = os.getenv("COGNODB_PASSWORD")

driver = GraphDatabase.driver(
    URI,
    auth=(USERNAME, PASSWORD)
)


# -------------------------
# FastAPI
# -------------------------

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "https://talentgraph-delta.vercel.app/"
],

    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# -------------------------
# Home
# -------------------------

@app.get("/")
def home():
    return {"message": "TalentGraph API is running"}


# -------------------------
# Search request
# -------------------------

class SearchRequest(BaseModel):
    skills: list[str]
    experience: int
    industry: str | None = None


# -------------------------
# Search candidates
# -------------------------

@app.post("/search")
def search_candidates(request: SearchRequest):

    query = """
    MATCH (c:Candidate)-[:WORKED_ON]->(p:Project)-[:IN_DOMAIN]->(i:Industry)

    WHERE c.experience >= $experience
      AND ($industry IS NULL OR i.name = $industry)

    OPTIONAL MATCH (c)-[:HAS_SKILL]->(direct:Skill)

    WITH c,
         p,
         i,
         collect(DISTINCT direct.name) AS candidate_skills

    WITH c,
         p,
         i,
         candidate_skills,
         [skill IN $skills
          WHERE skill IN candidate_skills] AS matched_direct_skills

    OPTIONAL MATCH (c)-[:HAS_SKILL]->(related:Skill)-[:RELATED_TO]->(target:Skill)

    WHERE target.name IN $skills

    WITH c,
         p,
         i,
         candidate_skills,
         matched_direct_skills,
         collect(DISTINCT related.name) AS related_skills

    WHERE size(matched_direct_skills) > 0
       OR size(related_skills) > 0

    RETURN c,
           p,
           i,
           candidate_skills,
           matched_direct_skills,
           related_skills
    """

    records, summary, keys = driver.execute_query(
        query,
        skills=request.skills,
        industry=request.industry,
        experience=request.experience
    )

    results = []

    for record in records:

        candidate = record["c"]

        candidate_skills = record["candidate_skills"]
        direct_skills = record["matched_direct_skills"]
        related_skills = record["related_skills"]

        # -------------------------
        # Skill score
        # -------------------------

        direct_count = len(direct_skills)
        related_count = len(related_skills)

        skill_score = min(
            direct_count * 20 + related_count * 10,
            50
        )

        if direct_count > 0 and related_count > 0:
            match_type = "Direct + related skill match"

        elif direct_count > 0:
            match_type = "Direct skill match"

        else:
            match_type = "Related skill match"

        # -------------------------
        # Domain score
        # -------------------------

        if request.industry:
            domain_score = 25
        else:
            domain_score = 0

        # -------------------------
        # Experience score
        # -------------------------

        experience_score = min(
            candidate["experience"],
            10
        )

        # -------------------------
        # Total score
        # -------------------------

        total_score = (
            skill_score
            + domain_score
            + experience_score
        )

        # -------------------------
        # Explanation
        # -------------------------

        explanation = []

        if direct_skills:
            explanation.append(
                "Directly matches: "
                + ", ".join(direct_skills)
            )

        if related_skills:
            explanation.append(
                "Related skills: "
                + ", ".join(related_skills)
            )

        if request.industry:
            explanation.append(
                f"Worked on {record['p']['name']} "
                f"in {request.industry}"
            )
        else:
            explanation.append(
                f"Worked on {record['p']['name']}"
            )

        explanation.append(
            f"Meets the minimum experience requirement "
            f"with {candidate['experience']} years"
        )

        # -------------------------
        # Result
        # -------------------------

        results.append({
            "id": candidate["id"],
            "name": candidate["name"],
            "location": candidate["location"],
            "experience": candidate["experience"],
            "score": total_score,
            "match_type": match_type,
            "matched_skills": direct_skills,
            "related_skills": related_skills,
            "project": record["p"]["name"],
            "industry": record["i"]["name"],
            "skills": candidate_skills,
            "why_matched": explanation
        })

    # -------------------------
    # Sort
    # -------------------------

    results.sort(
        key=lambda candidate: candidate["score"],
        reverse=True
    )

    return results