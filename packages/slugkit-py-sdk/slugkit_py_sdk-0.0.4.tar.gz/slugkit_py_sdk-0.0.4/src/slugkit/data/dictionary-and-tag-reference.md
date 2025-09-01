# SlugKit Dictionary & Tag Reference

**Complete guide to SlugKit's word dictionaries, content tags, and filtering strategies.**

## Word Dictionaries Overview

SlugKit provides 6 main word dictionaries with rich tagging for precise content control:

```
📊 Use dictionary_info() to see current word counts
📋 Use dictionary_tags() to see all available tags
```

### Available Dictionaries

| Dictionary | Count | Description | Examples |
|------------|-------|-------------|----------|
| **adjective** | ~17,082 | Descriptive words | fast, brilliant, secure, broken |
| **noun** | ~41,469 | Objects, concepts, people | server, database, user, platform |
| **verb** | ~8,405 | Action words | deploy, connect, analyze, configure |
| **adverb** | ~3,619 | Manner descriptors | quickly, efficiently, securely |
| **domain** | ~9,183 | Internet domains | com, org, tech, dev, aws |
| **shell** | ~2,137 | Command-line tools | git, docker, npm, curl, ssh |

## Tag System

Tags allow precise filtering of word content by theme, emotion, appropriateness, and domain.

### Emotional Tags

Control the emotional tone of generated content:

#### Adjectives & Adverbs
```
+pos    → Positive: amazing, brilliant, secure, fast
+neg    → Negative: broken, failed, slow, unstable  
+emo    → Emotional: passionate, thrilling, devastating
+neut   → Neutral: standard, regular, basic, normal
+det    → Detached: systematic, mechanical, procedural
```

#### Nouns & Verbs
```
+pos    → Positive concepts: success, achievement, growth
+neg    → Negative concepts: failure, error, breakdown
+emo    → Emotional concepts: passion, excitement, fear
+neut   → Neutral concepts: system, process, method
+det    → Detached concepts: mechanism, procedure, protocol
```

### Content Appropriateness

Control content suitability for different audiences:

```
+nsfw   → Not Safe For Work (opt-in only): explicit content
-nsfw   → Exclude NSFW content (recommended for production)
+obj    → Objective, professional tone
```

**⚠️ NSFW Content**: NSFW-tagged words are opt-in only. Use `+nsfw` explicitly to include them.

### Domain-Specific Tags

#### Technology & Business
```
+tech     → Technology: server, database, API, cloud, deploy
+business → Business: revenue, client, strategy, market
+science  → Scientific: research, analysis, hypothesis, data
+medical  → Medical: diagnosis, treatment, patient, clinic
```

#### Object Categories (Nouns)
```
+animal   → Animals: dolphin, eagle, tiger, wolf
+person   → People: manager, developer, user, admin  
+object   → Physical objects: server, desk, car, building
+artifact → Human-made items: software, document, tool
+substance → Materials: metal, wood, plastic, liquid
+food     → Food items: pizza, coffee, bread, salad
+building → Structures: office, warehouse, factory, home
+vehicle  → Transportation: car, truck, plane, ship
+device   → Electronic devices: phone, laptop, router
+material → Raw materials: steel, concrete, fabric
+currency → Money/financial: dollar, euro, bitcoin, cash
+plant    → Flora: tree, flower, grass, leaf
+drink    → Beverages: coffee, tea, water, juice
```

#### Action Categories (Verbs)
```
+action   → Physical actions: run, jump, build, move
+change   → Transformation: convert, modify, update, evolve  
+travel   → Movement: navigate, journey, migrate, explore
+be       → State of being: exist, remain, become, stay
+have     → Possession: own, contain, include, hold
+make     → Creation: build, generate, create, produce
+create   → Creative actions: design, compose, invent
+destroy  → Destructive actions: delete, remove, break
+take     → Taking actions: grab, acquire, capture
+give     → Giving actions: provide, share, offer
+imagine  → Mental actions: think, dream, visualize
```

#### Content Categories
```
+content  → Information content: article, document, data
+information → Data/knowledge: facts, statistics, records
+concept  → Abstract ideas: theory, principle, philosophy  
+idea     → Thoughts: concept, notion, plan, strategy
+emotion  → Feelings: joy, anger, fear, excitement
+feeling  → Sensations: warmth, pain, comfort, tension
+music    → Musical terms: song, rhythm, melody, beat
+art      → Artistic concepts: painting, sculpture, design
+fantasy  → Fantasy elements: dragon, magic, wizard, quest
```

#### Domains & Technology
```
+com      → Commercial domains: business, corporate TLDs
+org      → Organization domains: non-profit, community TLDs
+io       → Tech domains: developer-friendly TLDs
+edu      → Educational domains: academic institutions
+gov      → Government domains: official organizations
+tld      → Top-level domains: com, org, net, gov
+sld      → Second-level domains: company, product names
+sub      → Subdomain parts: www, api, blog, shop
```

## Tag Filtering Strategies

### Include Multiple Tags
```
{noun:+tech+object}           → Tech objects: server, router, database
{adjective:+pos+tech}         → Positive tech terms: amazing, secure, fast
{verb:+action+tech}           → Tech actions: deploy, configure, optimize
```

### Exclude Unwanted Content
```
{adjective:-neg-nsfw}         → No negative or NSFW words
{noun:+tech-animal}           → Tech terms, but no animals
{verb:-destroy-neg}           → No destructive or negative actions
```

### Complex Combinations
```
{adjective:+pos+tech-emo<8}   → Positive tech adjectives, not emotional, max 7 chars
{noun:+object+tech-nsfw>=4}   → Tech objects, family-friendly, min 4 chars
{verb:+change+tech-destroy}   → Change-related tech verbs, not destructive
```

## Content Strategy by Use Case

### Professional/Business Content
```
# Recommended tags
{adjective:+pos+obj-nsfw}     → professional, positive, appropriate
{noun:+business+tech-nsfw}    → business/tech focused, clean
{verb:+action+change-destroy} → constructive actions only

# Example pattern
"{adjective:+pos+obj} {noun:+tech} {verb:+action} {adverb:+pos}"
→ "secure platform deploys efficiently"
```

### Family-Friendly Content
```
# Always exclude NSFW
{adjective:-nsfw+pos}         → positive, clean adjectives
{noun:+animal+object-nsfw}    → animals and objects, family-safe
{verb:+action+change-destroy-nsfw} → constructive, clean verbs

# Example pattern  
"{adjective:+pos-nsfw} {noun:+animal-nsfw} {verb:+action-nsfw}"
→ "happy dolphin jumps"
```

### Technical Documentation
```
# Focus on objective, technical terms
{adjective:+tech+obj-emo}     → technical, unemotional
{noun:+tech+object+device}    → tech equipment and systems  
{verb:+tech+change+action}    → technical operations

# Example pattern
"{verb:+tech} {adjective:+tech} {noun:+tech+object}"
→ "configure secure server"
```

### Creative/Marketing Content
```
# Allow emotional, positive language
{adjective:+pos+emo}          → exciting, emotional positivity
{noun:+concept+idea+object}   → broad creative concepts
{verb:+create+action+change}  → dynamic, creative actions

# Example pattern
"The {adjective:+pos+emo} {noun:+concept} will {verb:+create} {adjective:+pos} {noun:+object}"
→ "The amazing platform will generate brilliant solutions"
```

### Gaming/Fantasy Content
```
# Include fantasy and creative elements
{adjective:+fantasy+emo}      → magical, dramatic descriptors
{noun:+fantasy+animal+person} → fantasy characters and creatures
{verb:+action+imagine+destroy} → dramatic fantasy actions

# Example pattern
"{adjective:+fantasy} {noun:+fantasy+person} {verb:+action} the {adjective:+neg} {noun:+fantasy}"
→ "Mystical wizard defeats the evil dragon"
```

## Language Support

### Current Language Tags
```
@en    → English (default)
@es    → Spanish (if available)
@fr    → French (if available)  
@de    → German (if available)
```

**Note**: Language support varies by dictionary. Use `dictionary_info()` to check availability.

### Usage Examples
```
{adjective@en}-{noun@en}      → Force English words
{noun@es} and {noun@fr}       → Mix Spanish and French
{adjective}-{noun}[@de]       → German words globally
```

## Special Dictionary Features

### Domain Dictionary Categories
The domain dictionary includes real internet domains organized by:

#### By Level
```
+tld     → Top-level: com, org, net, edu, gov
+sld     → Second-level: company names, brands
+sub     → Subdomain parts: www, api, mail, blog  
```

#### By Type
```
+com     → Commercial: business domains
+org     → Organization: non-profits, communities
+edu     → Educational: schools, universities
+gov     → Government: official agencies
+io      → Tech: developer-focused domains
+aws     → Cloud: AWS service domains
+cloud   → Cloud providers: various cloud services
```

#### By Region
```
+us, +uk, +de, +fr, +jp, +cn, +au → Country-specific TLDs
```

### Shell Dictionary Organization
Command-line tools organized by category:

```
+dev     → Development: git, npm, pip, cargo
+system  → System admin: systemctl, crontab, mount
+network → Networking: curl, wget, ssh, ping
+data    → Data processing: awk, sed, grep, sort
+archive → Compression: tar, zip, gzip, unzip
```

## Best Practices

### Production Applications
1. **Always exclude NSFW**: Use `-nsfw` in all patterns
2. **Use positive/neutral tone**: `+pos` or `+neut` for user-facing content
3. **Be domain-specific**: `+tech` for technical contexts, `+business` for corporate
4. **Control length**: Use length constraints for UI/database limits

### Testing & Development  
1. **Use diverse tags**: Test with different emotional tones
2. **Include edge cases**: Try `+neg` content for error scenarios
3. **Validate thoroughly**: Check capacity impact of tag combinations
4. **Consider caching**: Tag filtering can impact performance

### Content Strategy
1. **Match your audience**: Family-friendly vs. professional vs. technical
2. **Consistent theming**: Use global settings for pattern-wide consistency
3. **Cultural sensitivity**: Consider international audiences with language tags
4. **Brand alignment**: Choose tags that match your brand voice

## Advanced Tag Techniques

### Tag Hierarchies
Some tags work better together:
```
+tech+obj        → Technical, objective (great for APIs)
+pos+business    → Positive business language (marketing)
+action+change   → Dynamic transformation language
+animal+fantasy  → Mythical creatures and magical animals
```

### Performance Considerations
```
# More specific = better performance
{noun:+tech+object<8}         → Highly filtered, fast
{noun}                        → Broad selection, slower with large sets
{noun:+animal+fantasy+emo}    → Multiple tags, moderate performance
```

### Capacity Impact
```
# Check capacity before using
validate_pattern("{noun:+tech}")     → Smaller subset, lower capacity
validate_pattern("{noun}")           → Full dictionary, higher capacity
validate_pattern("{noun:+rare+specific}") → Very specific, very low capacity
```

---

**💡 Pro Tips:**
- Start broad, then add constraints: `{noun}` → `{noun:+tech}` → `{noun:+tech-nsfw<8}`
- Use `dictionary_tags()` regularly to discover new filtering options
- Test tag combinations with small `count` values first
- Consider your content strategy when choosing emotional tags
- Remember that more tags = smaller word selection but more targeted content
