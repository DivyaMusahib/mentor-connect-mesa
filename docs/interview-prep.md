# Mentor Connect — Technical Associate Interview Preparation Notes

## 1. Key Architectural Decisions & Justifications

### Q1: Why did you separate FastAPI and n8n rather than writing Google Calendar API calls in Python?
- **Answer**:
  > "Google Calendar and Gmail APIs involve extensive OAuth credential rotation, webhook renewal callbacks, and brittle token refresh cycles. Moving these integrations into n8n Cloud leverages native, audited OAuth nodes and visual workflow monitoring, keeping the FastAPI backend focused purely on business rules, database transactions, and security boundaries. Furthermore, changes to email templates or notification delays can be adjusted in n8n without redeploying backend code."

### Q2: Why did you choose full-context matching in Gemini rather than a Vector Database (RAG)?
- **Answer**:
  > "For 50 mentors (~14 KB total payload), a vector database introduces chunking loss, embedding drift, latency, and unnecessary infrastructure complexity. Passing the full catalogue of verified mentor records into Gemini 2.5 Flash preserves complete cross-attribute reasoning (e.g., matching a mentor with specific Edtech background AND n8n automation experience). It also allows strict Pydantic validation where unknown mentor IDs are discarded immediately."

### Q3: How do you handle failure if n8n Cloud or a transcription provider is down?
- **Answer**:
  > "We designed a circuit-breaking fallback layer. All integration requests record an `AutomationEvent` in PostgreSQL with an idempotency key. If n8n or an external webhook times out, the backend gracefully falls back to a simulated state, returns recoverable data to the user, and flags the failure in the Mesa Admin dashboard with a single-click retry operation."

### Q4: How do you prevent hallucinated mentor recommendations?
- **Answer**:
  > "We enforce three defensive layers:
  > 1. Pydantic v2 output schema validation.
  > 2. An authoritative database lookup that discards any ID returned by the model that does not exist in our 50-mentor catalogue.
  > 3. Populating all display fields (name, company, sector, tools) exclusively from the verified database record rather than model text."

### Q5: Why is the frontend built in pure JavaScript instead of TypeScript?
- **Answer**:
  > "Per the assignment constraints and interview design requirements, using pure JavaScript (.jsx) ensures readable, transparent code that can be articulated clearly without unnecessary TypeScript compilation abstractions or type gymnastics, while still maintaining high component modularity and JSDoc contracts where useful."
