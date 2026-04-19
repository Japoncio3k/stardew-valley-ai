### Requirement: Stardew Valley datasource returns mock game information
The datasource SHALL accept a free-text query string and return a structured response containing mocked Stardew Valley game information relevant to common query categories (characters, crops, fishing, mines, etc.).

#### Scenario: Query about a character
- **WHEN** the datasource is called with a query containing a character name (e.g., "Penny")
- **THEN** it SHALL return a dict with at least `category`, `name`, and `description` fields populated with plausible mock data

#### Scenario: Query about farming
- **WHEN** the datasource is called with a query about crops or farming
- **THEN** it SHALL return mock information about a Stardew Valley crop or farming mechanic

#### Scenario: Any query returns a non-empty response
- **WHEN** the datasource is called with any non-empty query string
- **THEN** it SHALL return a non-empty dict (never None or empty dict)

### Requirement: Use case wraps datasource and formats output
The use case SHALL call the datasource and return a human-readable string summary of the retrieved information, suitable for passing directly to the LLM as tool output.

#### Scenario: Use case returns a string
- **WHEN** the use case is called with a query string
- **THEN** it SHALL return a non-empty string describing the Stardew Valley information

#### Scenario: Use case handles datasource response
- **WHEN** the datasource returns a dict with category and description
- **THEN** the use case SHALL format it into a readable sentence or paragraph
