# SlugKit Pattern Examples by Use Case

## Web Development

### URL Slugs
```
// Blog posts
"{adjective:+pos}-{noun}-{number:4d}"
→ "amazing-tutorial-2024"

// Product pages  
"{adjective:<8}-{noun:+tech}-{verb:<6}"
→ "smart-server-deploy"

// Category slugs
"{adjective:+tech}/{noun:+object}"
→ "advanced/database"
```

### User Handles & IDs
```
// Readable user handles
"{adjective:<7}{noun:<8}{number:2d}"
→ "smartuser42"

// Anonymous usernames
"{adjective:+pos}-{noun:+animal}-{number:3d}"
→ "happy-dolphin-127"

// API keys (readable part)
"{adjective}-{noun}-{number:4x}"
→ "secure-token-a1b2"
```

### CSS & JavaScript
```
// CSS class names
"{adjective:<6}-{noun:<8}-component"
→ "smart-button-component"

// JavaScript variables
"{verb}<6{Noun}<8Config"
→ "loadButtonConfig"

// Component names
"{Adjective}{Noun}Widget"
→ "SmartDatabaseWidget"
```

### API Endpoints
```
// RESTful endpoints
"/api/{noun:+tech}/{adjective:<6}-{noun:<8}/{number:4d}"
→ "/api/users/active-sessions/2024"

// Webhook URLs
"/hooks/{adjective:+tech}-{noun}/{number:8x}"
→ "/hooks/secure-payment/a1b2c3d4"
```

## DevOps & Infrastructure

### Server & Service Naming
```
// Server hostnames
"{adjective:+tech}<6-{noun:+tech}<8-{number:2d}"
→ "prod-database-01"

// Kubernetes pods
"{noun:+tech}-{adjective}-{number:4x}"
→ "webapp-stable-f3a7"

// Docker containers
"{adjective:+tech}/{noun:+tech}:{number:1d}.{number:1d}"
→ "stable/webapp:2.1"
```

### Environment & Configuration
```
// Environment names
"{ADJECTIVE:+tech}_{NOUN}_ENV"
→ "PROD_DATABASE_ENV"

// Config files
"{noun:<8}-{adjective:+tech}.{domain:+tld}"
→ "database-secure.conf"

// Backup naming
"backup-{noun:+tech}-{number:2d}{number:2d}{number:4d}-{number:4x}"
→ "backup-postgres-31122024-a1f3"
```

### Monitoring & Logging
```
// Log files
"{noun:+tech}-{adjective:+tech}-{number:2d}{number:2d}.log"
→ "webapp-error-1225.log"

// Metric names
"{noun:+tech}.{adjective}.{verb}.count"
→ "database.active.connections.count"

// Alert names
"{ADJECTIVE:+neg} {NOUN:+tech} {verb:+neg}"
→ "CRITICAL DATABASE FAILURE"
```

## Database & Data

### Table & Column Names
```
// Table names
"{noun:+tech}_{adjective:+tech}"
→ "users_active"

// Column identifiers  
"{noun:<8}_{verb:<6}_at"
→ "account_created_at"

// Index names
"idx_{noun:+tech}_{adjective:+tech}_{number:2d}"
→ "idx_users_active_01"
```

### Test Data Generation
```
// User emails
"{adjective:<7}.{noun:<8}@{noun:<6}.{domain:+com}"
→ "smart.database@test.com"

// Phone numbers (template)
"+1-{number:3d}-{number:3d}-{number:4d}"
→ "+1-555-123-4567"

// Addresses
"{number:3d} {Adjective} {Noun} Street"
→ "123 Smart Database Street"
```

### Database Seeding
```
// Company names
"{Adjective} {Noun} {noun:+tech}"
→ "Smart Database Solutions"

// Product names
"{adjective:+pos} {noun:+tech} {number:1d}.{number:1d}"
→ "Amazing Platform 2.1"

// Department codes
"{ADJECTIVE:<4}_{NOUN:+tech:<6}"
→ "PROD_WEBAPP"
```

## Testing & QA

### Test Case IDs
```
// Test identifiers
"test_{noun:+tech}_{verb}_{number:3d}"
→ "test_database_connect_042"

// Scenario names
"Given {adjective} {noun}, when {verb}, then {verb}"
→ "Given active user, when login, then succeed"

// Mock data labels
"{adjective:+pos}_{noun:+tech}_{number:2d}"
→ "valid_account_01"
```

### Performance Testing
```
// Load test names
"load_{noun:+tech}_{number:3d}_{adjective:+tech}"
→ "load_api_100_concurrent"

// Benchmark IDs
"bench_{verb}_{noun:+tech}_{number:4x}"
→ "bench_query_database_a1f3"
```

### Error Simulation
```
// Error messages
"Error {number:3d}: {adjective:+neg} {noun:+tech} {verb:+neg}"
→ "Error 500: broken database connection failed"

// Exception names
"{Adjective}{Noun}Exception"
→ "InvalidDatabaseException"

// Failure scenarios
"{noun:+tech} {verb:+neg} after {number:2d} {noun:+time}"
→ "connection timeout after 30 seconds"
```

## Documentation & Content

### Technical Writing
```
// Guide titles
"## {Adjective:+pos} {Noun} Guide"
→ "## Complete Database Guide"

// Tutorial steps
"Step {number:1d}: {Verb} the {noun:+tech}"
→ "Step 3: Configure the server"

// Code examples
"// {Adjective} {noun:+tech} implementation"
→ "// Simple database implementation"
```

### Blog & Marketing
```
// Article titles
"How to {verb} {adjective:+pos} {noun:+tech} in {number:2d} minutes"
→ "How to deploy amazing applications in 15 minutes"

// Social media
"{Adjective:+pos} {noun:+tech}! {verb:+pos} your {noun} {adverb:+pos} 🚀"
→ "Amazing platform! Scale your business efficiently 🚀"

// Newsletter subjects
"{Adjective:+pos} {noun}: {verb:+pos} {number:2d}% {adjective:+pos}"
→ "Weekly Update: Boost 25% performance"
```

## Gaming & Entertainment

### Character & World Generation
```
// Character names
"{adjective:+fantasy} {noun:+person} the {adjective:+pos}"
→ "Mighty Warrior the Brave"

// Location names
"The {adjective:+fantasy} {noun:+location} of {noun:+fantasy}"
→ "The Ancient Castle of Dragons"

// Item names
"{adjective:+pos} {noun:+fantasy} of {noun:+concept}"
→ "Legendary Sword of Power"
```

### Game Development
```
// Asset names
"{adjective}_{noun:+object}_{number:3d}"
→ "rusty_sword_042"

// Level identifiers
"level_{number:2d}_{adjective:+difficulty}_{noun:+location}"
→ "level_05_hard_dungeon"

// Achievement names
"{adjective:+pos} {noun:+action}"
→ "Ultimate Victory"
```

## E-commerce & Business

### Product Management
```
// SKUs
"{adjective:<4}-{noun:+product}<6-{number:4d}"
→ "FAST-LAPTOP-2024"

// Inventory codes
"{ADJECTIVE:+tech:<4}_{NOUN:<6}_{NUMBER:6x}"
→ "PROD_SERVER_A1B2C3"

// Coupon codes
"{adjective:+pos}{number:2d}{adjective:+tech}"
→ "SAVE25SECURE"
```

### Customer Service
```
// Ticket IDs
"TKT-{adjective:+tech}-{number:6d}"
→ "TKT-URGENT-123456"

// Case numbers
"{noun:+tech}-{number:4d}-{adjective:+priority}"
→ "BILLING-4567-HIGH"

// Reference codes
"REF_{ADJECTIVE:<4}_{NUMBER:8x}"
→ "REF_HELP_A1B2C3D4"
```

## Security & Authentication

### Access Control
```
// Permission names
"{verb}_{noun:+tech}_{adjective:+security}"
→ "read_database_secure"

// Role identifiers
"{adjective:+tech}_{noun:+person}"
→ "admin_user"

// Session tokens (readable part)
"sess_{adjective:+tech}_{number:8x}"
→ "sess_secure_a1b2c3d4"
```

### Audit & Compliance
```
// Log entries
"[{number:2d}/{number:2d}/{number:4d}] {ADJECTIVE} {noun:+tech} {verb:+security}"
→ "[31/12/2024] FAILED database authentication"

// Compliance codes
"{ADJECTIVE:+security}_{NOUN:+tech}_{NUMBER:4d}"
→ "GDPR_DATA_2024"
```

## Advanced Pattern Techniques

### Multi-line Templates
```
"version: {number:1d}.{number:1d}.{number:2d}
name: {adjective}-{noun}
description: {adjective:+pos} {noun:+tech} for {verb}<6
maintainer: {Noun:+person} Team
status: {adjective:+tech}"

→ "version: 2.1.15
name: secure-platform
description: amazing solution for deploy
maintainer: Engineering Team  
status: stable"
```

### Conditional-like Patterns with Global Settings
```
// All positive tech terms
"{noun} {verb} {adjective} {noun}[+pos+tech]"
→ "platform deploys amazing solution"

// German technical terms (if supported)
"{noun} {verb} {noun}[@de+tech]"
→ "Datenbank verwendet System"

// Short professional terms
"{adjective} {noun} {verb}[+professional<6]"
→ "smart system works"
```

### Complex Casing Scenarios
```
// PascalCase components
"{Adjective}{Noun}{Verb}Component"
→ "SmartDatabaseQueryComponent"

// snake_case variables
"{adjective}_{noun}_{verb}_config"
→ "secure_database_connect_config"

// SCREAMING_SNAKE_CASE constants
"{ADJECTIVE}_{NOUN}_{NUMBER:4d}"
→ "MAX_DATABASE_1000"

// Mixed enterprise naming
"{AdJeCtIvE}_{nOuN}_v{NUMBER:1d}"
→ "SmArT_sErVeR_v2"
```

## Performance & Capacity Planning

### High-Volume Patterns (Large Capacity)
```
// Billions of combinations
"{adjective}-{noun}-{number:6x}"
→ Capacity: ~708M × 16M = 11+ trillion combinations

// Moderate capacity with constraints
"{adjective:<6}-{noun:+tech<8}-{number:3d}"  
→ More manageable capacity with better performance
```

### Low-Volume Patterns (Specific Use Cases)
```
// Limited but meaningful
"{adjective:+pos<5}-{noun:+tech==4}-{number:2d}"
→ Fewer combinations, highly constrained output
```

### Capacity Impact Examples
```
// Standard casing
"{noun}-{adjective}" 
→ ~708M combinations

// Mixed casing (capacity multiplier)
"{NoUn}-{AdJeCtIvE}"
→ Exponentially more combinations (2^8 × 708M+)
```

---

**Pro Tips:**
- Use `validate_pattern()` to check capacity before generation
- Combine `dictionary_info()` and `dictionary_tags()` to understand available words
- Test patterns with small `count` values first
- Consider length constraints for UI/database field limits
- Use global settings for consistent theming across complex patterns
