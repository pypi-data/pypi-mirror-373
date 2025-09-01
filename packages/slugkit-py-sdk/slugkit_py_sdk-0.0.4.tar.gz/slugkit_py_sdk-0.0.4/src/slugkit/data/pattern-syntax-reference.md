# SlugKit Pattern Syntax Reference

## Overview

SlugKit patterns are powerful template strings that can generate anything from simple slugs to complex structured text. Patterns combine **placeholders** (words in curly braces) with **arbitrary literal text** including whitespace, punctuation, and complete sentences.

## Basic Structure [^1]

```ebnf
pattern := ARBITRARY, { placeholder, ARBITRARY }, [ global_settings ]
```

**Key Principle**: Any text outside placeholders is preserved exactly as written.

- **ARBITRARY**: Any text except `{`, `}`, `\` (unless escaped)
- **placeholder**: Word generators in `{}`
- **global_settings**: Pattern-wide settings in `[]`

## Placeholders

### Basic Syntax
```ebnf
placeholder := '{' (selector | number_gen | special_char_gen) '}'
selector    := kind ['@' lang] [':', [tags] [length_constraint] [options]]
```

Three types of placeholders:
1. **Word selectors**: `{adjective}`, `{noun}`, etc. [^2]
2. **Number generators**: `{number:4d}`, `{number:3x}`
3. **Special character generators**: `{special:2}`, `{special:1-4}`

### Word Types
| Type | Description | Examples |
|------|-------------|----------|
| `{adjective}` | Descriptive words | fast, brilliant, complex |
| `{noun}` | Objects, concepts, people | server, database, manager |
| `{verb}` | Action words | deploy, analyze, configure |
| `{adverb}` | Manner descriptors | quickly, efficiently, carefully |
| `{domain}` | Internet domains | com, org, tech, dev |
| `{shell}` | Command-line tools | git, docker, npm, curl |

### Casing Control
The case of the dictionary name controls the output casing:

```
{noun}     → lowercase: "server"
{NOUN}     → UPPERCASE: "SERVER" 
{Noun}     → Title Case: "Server"
{nOuN}     → Mixed case following pattern: "SeRvEr"
```

**Impact on Capacity**: Mixed casing dramatically increases pattern capacity as all possible case combinations are generated. Capacity calculation for mixed case patterns is not yet fully implemented.

Examples:
```
{adjective}-{NOUN}     → "fast-SERVER"
{Verb} the {noun}      → "Deploy the database"  
{AdJeCtIvE} {nOuN}     → "FaSt sErVeR"
```

### Constraints (Inside Braces)

**Important**: For word selectors, constraints must follow this exact order:
```
{word_type:tags length_constraints options}
```

#### Tag Filters [^2]
```ebnf
tags        := (include_tag | exclude_tag)*
include_tag := '+' tag
exclude_tag := '-' tag
```

```
{adjective:+positive}          // Include positive words
{noun:-nsfw}                   // Exclude NSFW words
{adjective:+tech-negative}     // Include tech, exclude negative
{noun:+animal+object}          // Include both animal and object tags
```

**Tag syntax**: Tags are identifiers (letters, numbers, underscores). Multiple tags can be combined with `+` for inclusion and `-` for exclusion.

Common tags:
- **Emotional**: `+pos`, `+neg`, `+emo`, `+neut`
- **Content**: `+nsfw` (opt-in), `+det`, `+obj`
- **Domain-specific**: `+tech`, `+animal`, `+food`, `+person`

#### Length Constraints
```ebnf
length_constraint := comparison_op length
comparison_op     := '==' | '!=' | '<' | '<=' | '>' | '>='
```

```
{word:<8}      // Maximum 7 characters (less than 8)
{word:>3}      // Minimum 4 characters (greater than 3)
{word:<=6}     // 6 characters or fewer  
{word:>=4}     // 4 characters or more
{word:==5}     // Exactly 5 characters
{word:!=7}     // Not 7 characters
```

**Note**: `<8` means "less than 8", so max 7 characters. `>3` means "greater than 3", so min 4 characters.

#### Options
```ebnf
options      := option (',' option)*
option       := identifier '=' option_value
option_value := tag | number
```

⚠️ **Note**: Options are currently not supported and are reserved for future releases.

Options will provide additional configuration for word selectors:
```
{noun:option1=value1,option2=value2}    // Future functionality
```

#### Combined Constraints
Currently supported constraints must be in the exact order: **tags → length** (options reserved for future)
```
{adjective:+pos<6}              // ✅ Correct: tags first, then length
{noun:+tech-nsfw>=4}            // ✅ Correct: tags, then length  
{verb:<8+action}                // ❌ Wrong: length before tags
{noun:>=4+animal}               // ❌ Wrong: length before tags
{adjective:+pos<6,opt=val}      // ❌ Not yet supported: options
```

### Number Generators
```ebnf
number_gen := 'number' ':' length [(',' number_base) | number_base_short]
```

```
{number:3d}     // 3-digit decimal: 123
{number:4x}     // 4-digit lowercase hex: a1b2  
{number:4X}     // 4-digit uppercase hex: A1B2
{number:2r}     // 2-character lowercase Roman: ii
{number:3R}     // 3-character uppercase Roman: XII
```

**Long form with comma**:
```
{number:3,dec}   // Same as {number:3d}
{number:4,hex}   // Same as {number:4x}
{number:2,HEX}   // Same as {number:2X}
{number:3,roman} // Same as {number:3r}
{number:2,ROMAN} // Same as {number:2R}
```

**Supported bases**: `dec`, `hex`, `HEX`, `roman`, `ROMAN`

### Special Character Generators
```ebnf
special_char_gen := 'special' [':' number ['-' length]]
```

```
{special}        // Single special character: @
{special:2}      // Exactly 2 special characters: @#
{special:1-4}    // 1 to 4 special characters: &!@
```

### Global Settings
```ebnf
global_settings := '[' ['@' lang] [tags] [length_constraint] [options] ']'
```

Apply settings to ALL placeholders in the pattern:
```
{adjective}-{noun}[@en:+pos-nsfw<6]
{verb} {noun} {adverb}[+tech>=4]
```

**Components**:
- `@en` - Language for all word selectors
- `+pos-nsfw` - Include positive, exclude NSFW for all words  
- `<6` - Maximum 5 characters for all words (< 6)
- Options apply to all compatible placeholders

**Note**: Global settings don't affect number or special character generators, only word selectors.

## Escaping

```ebnf
ESCAPED_CHAR  := escape_symbol ('{' | '}' | escape_symbol)
escape_symbol := '\'
```

Use backslash `\` to include literal braces and backslashes:
```
\{            // Literal { character
\}            // Literal } character  
\\            // Literal \ character
```

Examples:
```
"The \{system\} uses {noun}"     → "The {system} uses database"
"Path: C:\\{noun}\\file"         → "Path: C:\server\file"  
"Price: \$\{number:2d\}"         → "Price: ${42}"
```

**Important**: Only `{`, `}`, and `\` need escaping. All other characters are literal.

## Pattern Examples

### Simple Slugs
```
{adjective}-{noun}                    → "fast-server"
{adjective:<6}-{noun:<8}-{number:3d}  → "quick-database-127"  
{verb:>=5}-{noun:+tech}               → "deploy-microservice"
```

### Natural Language
```
"The {adjective:+pos} {noun:+animal} {verb} {adverb}"
→ "The brilliant cat leaps gracefully"

"Error {number:3d}: {ADJECTIVE} {NOUN} could not {verb} the {Noun}"  
→ "Error 404: BROKEN CONNECTION could not reach the Server"
```

### Structured Templates
```
"server_name: {adjective}-{noun}
port: {number:4d}
debug: {adjective:+tech}"

→ "server_name: fast-proxy
port: 8080
debug: verbose"
```

### Command-Line Examples
```
"git {verb:<6} {adjective}-{noun}-{number:4x}"
→ "git commit feature-auth-a1b2"

"docker run -p {number:4d}:{number:4d} {adjective}/{noun}"
→ "docker run -p 8080:3000 stable/webapp"
```

### Email Addresses
```
"{adjective:<6}.{noun:<8}@{noun:<6}.{domain:+com}"
→ "smart.database@tech.com"
```

### Configuration Files
```
"[database]
host = {noun:<8}.local
port = {number:4d}
timeout = {number:2d}s
ssl = {adjective:+tech}"

→ "[database]
host = postgres.local  
port = 5432
timeout = 30s
ssl = enabled"
```

## Best Practices

### 1. Always Validate First
```
Use validate_pattern() before forge(), mint(), or other operations
```

### 2. Use Length Constraints for Predictable Output
```
{noun:<8}-{adjective:<6}    // Bounded length (max 7 + max 5 + 1 = 13 chars)
vs
{noun}-{adjective}          // Variable length (could be very long)
```

**Remember**: `<8` means "less than 8", so maximum 7 characters.

### 3. Apply Appropriate Tags
```
{adjective:+pos}-{noun:+tech}     // Professional, positive tech terms
{noun:+animal}-{verb:+action}     // Animal action combinations
```

### 4. Leverage Global Settings for Consistency
```
{adjective}-{noun}-{verb}[+tech<8]   // All tech words, max 7 chars (< 8)
{noun} and {noun}[@en:>=4]           // English words, min 4 chars
```

### 5. Consider Your Use Case
- **Slugs**: Short, constrained patterns
- **Sentences**: Natural language with appropriate tags
- **Templates**: Mix literals with strategic placeholders
- **Commands**: Realistic tool names and parameters

## Common Patterns

### Common Patterns

### Web Development
```
"{adjective}-{noun}-api"              → "fast-user-api"
"{NOUN:<6}-v{number:1d}.{number:1d}"  → "WEBAPP-v2.1"  
"{Adjective}{Noun}Service"            → "FastUserService"
```

### DevOps
```
"deploy {Noun} to {adjective}-env"           → "deploy Service to staging-env"
"backup-{noun}-{number:2d}{number:2d}{number:4d}" → "backup-db-15122024"
"{ADJECTIVE}_{NOUN}_CONFIG"                  → "PROD_DATABASE_CONFIG"
```

### Testing Data
```
"user_{number:4d}@{noun}.{domain:+com}"     → "user_1234@test.com"
"The {Adjective} test {verb} {adverb}"      → "The Comprehensive test passes successfully"
"{FirstName} {LastName}"                    → "Smart Database" (using mixed casing)
```

### Documentation
```
"## {adjective:+pos} {noun} Guide
This {noun} will help you {verb} {adverb}."

→ "## Comprehensive Database Guide
This tutorial will help you deploy efficiently."
```

## Error Prevention

### Common Mistakes
```
❌ {adjective}<8      // Length constraint outside braces (becomes literal "<8")
✅ {adjective:<8}     // Correct: constraint inside braces

❌ {noun}+tech        // Tag outside braces (becomes literal "+tech")  
✅ {noun:+tech}       // Correct: tag inside braces
```

### Validation Tips
- Constraints go INSIDE braces: `{word:constraint}`
- Arbitrary text goes OUTSIDE braces: `{word} literal text`
- Use `validate_pattern()` to verify syntax and see capacity
- Use `dictionary_tags()` to see available tag filters

## Advanced Features

### Language Selection
```
{adjective@en}-{noun@en}    // Force English words
{noun@es}-{verb@fr}         // Mix languages (if supported)  
{noun}[@de]                 // German words globally
```

### Complex Filtering
```
{adjective:+pos+tech-nsfw<6>=3}    // Positive tech adjectives, 3-5 chars (< 6, >= 3)
{noun:+animal+fantasy!=5}         // Animal/fantasy nouns, not exactly 5 chars
{verb:+action<=8,option1=value}   // Action verbs, max 8 chars, with custom option
```

### Sequence Control  
When using forge() with `sequence` parameter for number generators:
```
{number:3d} generates 3-digit zero-padded numbers in pseudorandom sequence
sequence=0   → 383, 766, 149, 532, 915...
sequence=100 → 630, 664, 498, 322, 15...
sequence=1000 → 383, 766, 149... (same as sequence=0 due to wrapping)
```

**Wrapping**: Sequence values wrap at the generator's capacity (e.g., 1000 for 3-digit decimals). So `sequence=1000` equals `sequence=0` for `{number:3d}`.

---

[^1]: *For formal grammar specification, see the EBNF grammar documentation.*
[^2]: *For available word types and tags, use `dictionary_info()` and `dictionary_tags()`.*
