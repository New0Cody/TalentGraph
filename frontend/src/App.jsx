import { useState } from "react";
import "./App.css";

function App() {
  const [skills, setSkills] = useState("");
  const [industry, setIndustry] = useState("");
  const [experience, setExperience] = useState("");

  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  async function searchCandidates() {
    setLoading(true);
    setError("");
    setResults([]);

    try {
      const skillList = skills
        .split(",")
        .map((skill) => skill.trim())
        .filter((skill) => skill.length > 0);

      const response = await fetch("http://127.0.0.1:8000/search", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          skills: skillList,
          experience: Number(experience),
          industry: industry.trim() || null,
        }),
      });

      if (!response.ok) {
        throw new Error("Search failed");
      }

      const data = await response.json();

      setResults(data);
    } catch (error) {
      console.error(error);
      setError("Unable to connect to TalentGraph backend.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="app">
      <header className="hero">
        <div className="logo">TalentGraph</div>

        <h1>Find the right candidate.</h1>

        <p>
          Discover talent through skills, projects and industry relationships.
        </p>
      </header>

      <section className="search-box">
        <div className="field">
          <label>Skills</label>

          <input
            type="text"
            placeholder="e.g. React, AWS, Python"
            value={skills}
            onChange={(e) => setSkills(e.target.value)}
          />
        </div>

        <div className="field">
          <label>Industry (optional)</label>

          <input
            type="text"
            placeholder="e.g. E-commerce"
            value={industry}
            onChange={(e) => setIndustry(e.target.value)}
          />
        </div>

        <div className="field">
          <label>Minimum Experience</label>

          <input
            type="number"
            min="0"
            placeholder="e.g. 3"
            value={experience}
            onChange={(e) => setExperience(e.target.value)}
          />
        </div>

        <button
          className="search-button"
          onClick={searchCandidates}
          disabled={loading}
        >
          {loading ? "Searching..." : "Find Candidates"}
        </button>
      </section>

      {error && <div className="error">{error}</div>}

      {results.length > 0 && (
        <section className="results-section">
          <div className="results-header">
            <div>
              <h2>Search Results</h2>

              <p>Candidates ranked by graph relevance</p>
            </div>

            <span className="result-count">{results.length} candidates</span>
          </div>

          <div className="results">
            {results.map((candidate, index) => (
              <div className="candidate-card" key={candidate.id}>
                <div className="candidate-header">
                  <div>
                    <div className="rank">
                      {index === 0 && "🥇"}
                      {index === 1 && "🥈"}
                      {index === 2 && "🥉"}
                    </div>

                    <h2>{candidate.name}</h2>

                    <span className="match-type">{candidate.match_type}</span>
                  </div>

                  <div className="score">
                    <strong>{candidate.score}</strong>
                    <span>/100</span>
                  </div>
                </div>

                <div className="candidate-info">
                  <span>📍 {candidate.location}</span>
                  <span>💼 {candidate.experience} years</span>
                  <span>📁 {candidate.project}</span>
                  <span>🏢 {candidate.industry}</span>
                </div>

                <div className="skills-section">
                  <h3>Skills</h3>

                  <div className="skill-list">
                    {candidate.skills.map((skill) => (
                      <span className="skill-tag" key={skill}>
                        {skill}
                      </span>
                    ))}
                  </div>
                </div>

                <div className="explanation">
                  <h3>Why matched?</h3>

                  <ul>
                    {candidate.why_matched.map((reason, index) => (
                      <li key={index}>{reason}</li>
                    ))}
                  </ul>
                </div>
              </div>
            ))}
          </div>
        </section>
      )}

      {!loading && !error && results.length === 0 && skills && experience && (
        <div className="no-results">No matching candidates found.</div>
      )}
    </div>
  );
}

export default App;
