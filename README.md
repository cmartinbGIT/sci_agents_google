# AI Climate Scientist for Low-Carbon Technology Design
I built an AI assistant that can reason about carbon capture systems like a junior research engineer:
- Answer questions such as:
    - “What’s the energy penalty (GJ/ton CO₂) for amine scrubbing on a 500 MW coal plant?”
    - “Compare DAC vs post-combustion capture for cost and energy use.”
    - “Given these design constraints, what capture configuration makes sense?”

- Use credible, technical sources: CCS papers, DOE/IEA/IPCC reports, engineering design docs, not random web blogs.
- Do math + physics + engineering reasoning, not just text regurgitation.
- This matters because:
    - Carbon capture is a key lever in many 1.5–2°C climate pathways, but the tech is complex and the literature is scattered across thousands of pages.
    - Engineers/researchers spend huge time searching, reading, and recomputing things (energy balances, costs, efficiencies).
    - A good assistant that can search, reason, calculate, and explain could accelerate research, reduce miscalculations, and help explore more design options faster.
So the core problem is:
**“How can I give people a single interface that can understand carbon-capture questions, retrieve the right technical knowledge, and work through the math/physics to produce defensible answers?”**

### Why agents? -- Why are agents the right solution to this problem
A single monolithic LLM prompt (“be good at everything”) isn’t ideal for this:
- Different skills are needed:
    - Information retrieval (papers, reports, policies).
    - Math-heavy reasoning (equations, unit conversions, optimization).
    - Physics/engineering reasoning (mass & energy balances, process design).

- You want to be able to iterate and improve each skill separately:
    - Tune how retrieval works without touching math.
    - Upgrade the physics agent without breaking the coordinator.

- You often want tooling:
    - RAG over a curated CCS corpus (Vertex AI Search).
    - Code execution for precise numerics.
    - (Later) maybe simulators, spreadsheets, or process models.

- Agents give a natural decomposition:
    - A Coordinator Agent that interprets the user’s question and decides:
        - “Is this mostly math?”
        - “Is this physics/process design?”
        - “Is this literature/policy?”
    - Specialist Workers:
        - MathWorker → math & code execution.
        - PhysicsWorker → physics & engineering calculations.
        - GeneralSciWorker → RAG over CCS corpus (and later web research).
- Tool usage stays localized:
    - RAG tool on GeneralSciWorker.
    - Code executor on Math/Physics.
- The system becomes modular: I can swap models, tools, or agents without rewriting everything.
<img width="1024" height="1024" alt="architecture" src="https://github.com/user-attachments/assets/2f3a4c84-267a-41c3-921f-bb8860130165" />


To sum up, agents let me mirror the way a real team would approach the problem (coordinator + domain experts + tools) and make the system more maintainable and extensible.
