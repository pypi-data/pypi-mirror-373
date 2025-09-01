# SlugKit Quick Start Guide

**Get started with SlugKit in 5 minutes for AI agents! Generate human-readable IDs, slugs, and structured content.**

## Step 1: Understand the Basics (30 seconds)

SlugKit uses **patterns** - templates with placeholders that generate random but readable content:

```
{adjective}-{noun}           → "fast-server"
{verb} {adjective} {noun}    → "deploy amazing platform" 
Error {number:3d}: {noun}    → "Error 404: database"
```

**Key Point**: Anything outside `{}` is kept exactly as written. Anything inside `{}` gets replaced.

## Step 2: Validate Your First Pattern (1 minute)

**Before creating a pattern** always start your session with obtaining actual available dictionary and tag data (`dictionary_info()`, `dictionary_tags()`)
**Always start with validation** to check syntax and see what you'll get:

```
📚 Use: validate_pattern(pattern)
```

**Try these examples:**

```
✅ validate_pattern("{adjective}-{noun}")
→ Capacity: 708M combinations, max length: 55 chars

✅ validate_pattern("user-{number:4d}@example.com") 
→ Capacity: 10K combinations, max length: 25 chars

❌ validate_pattern("{adjective<6}-{noun}")
→ Invalid: constraints go INSIDE braces after a colon: {adjective:<6}
```

## Step 3: Generate Content (2 minutes)

### Option A: Custom Generation (`forge`)
Perfect for one-off generation or custom patterns:

```
🔨 forge(pattern, count=5, seed="test")
```

**Examples:**
```
forge("{adjective}-{noun}", count=3, seed="demo")
→ ["smart-server", "fast-database", "secure-platform"]

forge("deploy {noun} to {adjective} environment", count=2)
→ ["deploy webapp to staging environment", "deploy api to production environment"]
```

### Option B: Series Generation (`mint`)
Perfect for production apps needing guaranteed unique IDs:

```
⚡ mint(count=5, series_slug="your-series")
```

**First, check available series:**
```
series_list()
→ ["hotly-curly-gouge-d4ac", "wanly-final-adobo-b55f", ...]

series_info("hotly-curly-gouge-d4ac")  
→ Pattern: "{adjective:<8}-{noun:<8}-{number:3d}"
→ Capacity: 38.8 billion combinations
```

**Then mint from series:**
```
mint(count=3, series_slug="hotly-curly-gouge-d4ac")
→ ["soupy-stoop-142", "bobtail-ousting-083", "imposed-gramps-024"]
```

## Step 4: Essential Pattern Syntax (2 minutes)

### Basic Placeholders
```
{adjective}    → descriptive words: fast, smart, secure
{noun}         → things: server, database, user  
{verb}         → actions: deploy, connect, analyze
{number:4d}    → 4-digit numbers: 0123, 5678, 9999
```

### Control Output Length
```
{adjective:<8}     → max 7 chars (< 8): "smart", "secure"
{noun:>=4}         → min 4 chars: "server", "platform" 
{noun:==5}         → exactly 5 chars: "users", "login"
```

### Filter by Theme
```
{adjective:+pos}     → positive words: amazing, brilliant
{noun:+tech}         → tech words: server, database, API
{adjective:+tech-neg} → tech words, not negative
```

### Control Casing
```
{noun}      → lowercase: "server"
{NOUN}      → UPPERCASE: "SERVER"  
{Noun}      → Title Case: "Server"
{nOuN}      → Mixed case: "SeRvEr"
```

## Step 5: Your First Real Patterns

### Web Development
```
// URL slugs
forge("{adjective:+pos}-{noun:+tech}-{number:4d}", count=3)
→ ["amazing-platform-2024", "brilliant-server-1847", "smart-database-9032"]

// API endpoints  
forge("/api/{noun:+tech}/{adjective:<6}-{noun:+object}", count=2)
→ ["/api/users/active-session", "/api/data/secure-token"]
```

### User-Friendly IDs
```
// Customer support tickets
forge("TKT-{adjective:+tech}-{number:6d}", count=3, seed="support")
→ ["TKT-urgent-123456", "TKT-secure-789012", "TKT-stable-345678"]

// Readable user handles
forge("{adjective:+pos}<6{noun:+animal}<8", count=3)  
→ ["smart<6dolphin<8", "happy<6eagle<8", "bright<6tiger<8"]
```

### Configuration & DevOps
```
// Server names
forge("{adjective:+tech}<6-{noun:+tech}<8-{number:2d}", count=3)
→ ["prod<6-database<8-01", "stage<6-webapp<8-02", "dev<6-cache<8-03"]

// Environment variables
forge("{ADJECTIVE:+tech}_{NOUN:+tech}_CONFIG", count=2)
→ ["PROD_DATABASE_CONFIG", "TEST_WEBAPP_CONFIG"]
```

## Common Mistakes to Avoid

### ❌ Wrong Constraint Placement
```
{adjective}<8     → This adds literal "<8" text
{adjective:+tech<8+pos} → Wrong order: length before tags
```

### ✅ Correct Syntax
```
{adjective:<8}    → Correct: max 7 characters  
{adjective:+tech+pos<8} → Correct: tags first, then length
```

### ❌ Forgetting Validation
```
forge("{adjective-noun}")  → Invalid syntax, will error
```

### ✅ Always Validate First
```
validate_pattern("{adjective}-{noun}")  → Check first!
forge("{adjective}-{noun}")             → Then generate
```

## Next Steps

### Explore Available Words
```
dictionary_info()    → See all word types (adjective, noun, verb, etc.)
dictionary_tags()    → See all available tags (+pos, +tech, +animal, etc.)
```

### Preview Before Using Series
```
slice(count=5, series_slug="your-series")  → Preview without consuming
mint(count=5, series_slug="your-series")   → Actually generate and consume
```

### Check Performance
```
series_info("your-series")  → See capacity and current usage
stats("your-series")        → See generation performance metrics
```

## Advanced Quick Examples

### Multi-line Templates
```
pattern = """server: {adjective:+tech}-{noun:+tech}
port: {number:4d}  
status: {adjective:+pos}
debug: {adjective:+tech}"""

forge(pattern, count=1)
→ ["server: secure-database\nport: 5432\nstatus: amazing\ndebug: stable"]
```

### Mixed Casing for Code
```
// PascalCase components
forge("{Adjective}{Noun}Component", count=2)
→ ["SmartDatabaseComponent", "FastServerComponent"]

// camelCase variables  
forge("{adjective}{Noun}Config", count=2)
→ ["smartDatabaseConfig", "fastServerConfig"]
```

### Natural Language
```
forge("The {adjective:+pos} {noun:+animal} {verb} over the {adjective} {noun}", count=2)
→ ["The brilliant dolphin leaps over the rusty fence", 
   "The amazing eagle soars over the broken tower"]
```

## Essential Commands Summary

```
# Always start here
validate_pattern("{your-pattern}")

# Generate custom content  
forge("{pattern}", count=N, seed="optional")

# Use managed series
series_list()                    # See available series
series_info("series-name")       # Check series details  
slice(count=N, series="name")    # Preview
mint(count=N, series="name")     # Generate unique IDs

# Understand your options
dictionary_info()                # Available word types
dictionary_tags()                # Available tag filters
```

**You're ready! Start with simple patterns like `{adjective}-{noun}` and gradually add constraints and complexity as needed.**

---
📚 **Full Documentation**: Use `get_help_topic("pattern-syntax-reference.md")` for complete syntax guide
🎯 **More Examples**: Use `get_help_topic("pattern-examples.md")` for use-case specific patterns
