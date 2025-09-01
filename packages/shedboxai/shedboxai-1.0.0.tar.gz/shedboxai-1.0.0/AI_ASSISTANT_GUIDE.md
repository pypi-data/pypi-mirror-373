# ShedBoxAI LLM Cheatsheet

**You are now a ShedBoxAI configuration expert. Use this cheatsheet to generate accurate YAML configurations for users.**

## Your Mission
Generate ShedBoxAI YAML configs that:
- Read data from multiple sources (CSV, JSON, APIs, etc.)
- Process data with filtering, transformations, aggregations, and joins
- Integrate LLMs for AI-powered analysis and content generation
- Output results in structured formats

## Make Their Lives Easier with Introspection
If users haven't provided detailed data schemas (field names, data types, sample values), suggest ShedBoxAI's introspection feature:

**What it does**: Automatically analyzes their data sources and generates a comprehensive report with:
- All field names and data types
- Sample values from each field
- Data quality insights
- Relationship detection between sources
- Schema documentation in markdown

**Why it helps**: Instead of guessing field names or asking users for details, you get complete data intelligence to generate perfect configurations on the first try.

**Command**:
```bash
shedboxai introspect sources.yaml --include-samples
```

**Documentation**: https://shedboxai.com/docs/introspection/overview

## Configuration Components
Every ShedBoxAI config has these sections:
1. **data_sources** - Define input data (files, APIs)
2. **processing** - Transform data (6 operation types, 80+ functions)
3. **graph** - Complex workflows with dependencies (optional)
4. **ai_interface** - LLM integration for analysis (optional)
5. **output** - Save results to files

---

## Basic Configuration Structure

```yaml
# Root configuration file structure
data_sources:
  # Define data inputs
  
processing:
  # Define processing pipeline operations
  
ai_interface:
  # Configure LLM integration (optional)
  
output:
  # Configure output format and destination
```

---

## 1. Data Sources

### Supported Types
- `csv` - CSV files with pandas options
- `json` - JSON files  
- `yaml` - YAML configuration files
- `rest` - REST API endpoints
- `text` - Plain text files

### CSV Sources
```yaml
data_sources:
  users:
    type: csv
    path: "data/users.csv"
    options:
      encoding: utf-8
      delimiter: ","
      header: 0
```

### JSON Sources  
```yaml
data_sources:
  products:
    type: json
    path: "data/products.json"
```

### YAML Sources
```yaml
data_sources:
  config:
    type: yaml
    path: "config/settings.yaml"
```

### Text Sources
```yaml
data_sources:
  logs:
    type: text  
    path: "logs/system.log"
    options:
      encoding: utf-8
```

### REST API Sources
```yaml
data_sources:
  api_data:
    type: rest
    url: "https://api.example.com/data"
    method: GET  # or POST
    headers:
      Authorization: "Bearer ${API_TOKEN}"
      Content-Type: "application/json"
    options:
      params:
        limit: 100
      timeout: 30
    response_path: "data.results"  # Extract nested data
```

### REST API Authentication

#### Bearer Token
```yaml
data_sources:
  protected_api:
    type: rest
    url: "https://api.example.com/protected"
    headers:
      Authorization: "Bearer ${API_TOKEN}"
```

#### Basic Auth
```yaml
data_sources:
  legacy_api:
    type: rest
    url: "https://legacy.company.com/api"
    options:
      auth: ["${USERNAME}", "${PASSWORD}"]
```

#### OAuth Token Flow
```yaml
data_sources:
  # Token source
  auth_endpoint:
    type: rest
    url: "https://auth.example.com/token"
    method: POST
    options:
      json:
        grant_type: "client_credentials"
        client_id: "${CLIENT_ID}"
        client_secret: "${CLIENT_SECRET}"
    is_token_source: true
    token_for: ["protected_endpoint"]
  
  # Protected endpoint
  protected_endpoint:
    type: rest
    url: "https://api.example.com/data"
    requires_token: true
    token_source: "auth_endpoint"
```

### Inline Data
```yaml
data_sources:
  sample_data:
    type: csv
    data:
      - name: "John"
        age: 30
        city: "New York"
      - name: "Jane"
        age: 25
        city: "London"
```

---

## 2. Processing Operations

ShedBoxAI provides 6 operation types with specific functions:

### Operation Types
1. **contextual_filtering** - Filter data based on conditions
2. **format_conversion** - Extract fields and apply templates
3. **content_summarization** - Statistical analysis
4. **relationship_highlighting** - Join data and detect patterns
5. **advanced_operations** - Group, aggregate, sort, limit
6. **template_matching** - Jinja2 template processing

### Contextual Filtering

Filter data using field conditions:

```yaml
processing:
  contextual_filtering:
    users:  # source name
      - field: "status"
        condition: "active"
      - field: "age"
        condition: ">= 18"
        new_name: "adult_users"
```

**Supported Conditions:**
- Equality: `"active"`, `"premium"`
- Comparisons: `"> 100"`, `"<= 50"`, `">= 18"`, `"!= 0"`
- Numeric values are auto-converted

### Format Conversion

Extract specific fields or apply templates:

```yaml
processing:
  format_conversion:
    users:
      extract_fields: ["name", "email", "age"]
      
    # OR use templates
    user_names:
      template: "{{item.first_name}} {{item.last_name}}"
```

### Content Summarization

Generate statistical summaries:

```yaml
processing:
  content_summarization:
    users:
      method: "statistical"
      fields: ["age", "income", "score"]
      summarize: ["mean", "min", "max", "count", "sum", "median", "std", "unique"]
```

**Statistical Functions:**
- `mean` - Average value
- `min` - Minimum value  
- `max` - Maximum value
- `count` - Number of records
- `sum` - Total sum
- `median` - Middle value
- `std` - Standard deviation
- `unique` - Count of unique values

### Relationship Highlighting

Join data sources and detect relationships:

```yaml
processing:
  relationship_highlighting:
    users:
      link_fields:
        - source: "users"
          source_field: "user_id"
          to: "orders"
          target_field: "customer_id"
      
      # Conditional highlighting
      conditional_highlighting:
        - source: "users"
          condition: "item.membership_level == 'Gold'"
          insight_name: "gold_member"
          context: "High-value customer with Gold membership"
          
      # Derived fields
      derived_fields:
        - "full_address = item.address + ', ' + item.city + ', ' + item.state"
        - "profit_margin = item.selling_price - item.cost_price"
```

### Advanced Operations

Group, aggregate, sort and limit data:

```yaml
processing:
  advanced_operations:
    monthly_sales:
      source: "transactions"
      group_by: "transaction_type"
      aggregate:
        total_amount: "SUM(amount)"
        avg_amount: "AVG(amount)"
        transaction_count: "COUNT(*)"
      sort: "-total_amount"  # Use "-" for descending
      limit: 10
```

**Aggregation Functions:**
- `SUM(field)` - Sum values
- `COUNT(*)` or `COUNT(field)` - Count records
- `AVG(field)` - Average value
- `MIN(field)` - Minimum value
- `MAX(field)` - Maximum value  
- `MEDIAN(field)` - Median value
- `STD(field)` - Standard deviation

### Template Matching

Process Jinja2 templates with context data:

```yaml
processing:
  template_matching:
    demographic_report:
      template: |
        # Market Demographics Report
        
        ## Population Overview
        - ZIP Code: {{ demographics.zip_code }}
        - Total Population: {{ demographics.population }}
        - Median Household Income: ${{ demographics.median_household_income }}
        - Median Age: {{ demographics.median_age }} years
        
        ## Transaction Summary
        - Total Transactions: {{ transactions|length }}
        {% if transactions %}
        - Average Transaction: ${{ (transactions|map(attribute='amount')|list|sum / transactions|length)|round(2) }}
        {% endif %}
```

**Built-in Jinja2 Filters:**
- `{{ data | tojson }}` - Convert to JSON
- `{{ items | length }}` - Get length
- `{{ list | join(', ') }}` - Join with separator
- `{{ value | currency }}` - Format as currency
- `{{ value | percentage }}` - Format as percentage
- `{{ obj | safe_get('key', 'default') }}` - Safe key access
- `{{ list | first }}` - Get first item
- `{{ list | last }}` - Get last item

---

## 3. Graph Processing

ShedBoxAI supports complex workflows with dependencies using graph-based execution. Instead of linear processing, you can define a directed acyclic graph (DAG) where operations depend on each other.

### Graph Structure

```yaml
processing:
  graph:
    - id: filter_large
      operation: contextual_filtering
      depends_on: []
      config_key: large_transaction_filter
    - id: convert_format
      operation: format_conversion
      depends_on: [filter_large]
      config_key: transaction_formatter
    - id: summarize_data
      operation: content_summarization
      depends_on: [convert_format]
      config_key: transaction_stats
  
  # Named configuration blocks for each operation
  contextual_filtering:
    large_transaction_filter:
      transactions:
        - field: amount
          condition: "> 100"
          new_name: large_transactions
  
  format_conversion:
    transaction_formatter:
      large_transactions:
        extract_fields: ["amount", "customer_id", "transaction_type"]
  
  content_summarization:
    transaction_stats:
      large_transactions:
        method: statistical
        fields: ["amount"]
        summarize: ["mean", "max", "count", "sum"]
```

### Graph Node Properties

- **id**: Unique identifier for the node
- **operation**: Type of operation (one of the 6 supported types)
- **depends_on**: List of node IDs this operation depends on (empty for root nodes)
- **config_key**: Reference to named configuration block

### Execution Order

ShedBoxAI automatically determines execution order using topological sorting:
1. Root nodes (no dependencies) execute first
2. Subsequent nodes execute only after their dependencies complete
3. Parallel execution where possible for independent branches

### Benefits of Graph Processing

- **Complex Workflows**: Handle multi-step data transformations
- **Dependency Management**: Ensure operations run in correct order
- **Parallel Execution**: Independent operations run simultaneously
- **Reusable Configurations**: Named config blocks can be shared
- **Error Isolation**: Failed operations don't affect independent branches

---

## 4. Output Configuration

Configure where and how to save processing results:

```yaml
output:
  type: file          # 'file' or 'print'
  path: "output/results.json"
  format: json        # 'json' or 'yaml'
```

### Output Types

- **file** - Save results to a file
- **print** - Print results to console (no path required)

### Output Formats

- **json** - JSON format with pretty formatting
- **yaml** - YAML format

### Output Examples
```yaml
# Basic file output (JSON)
output:
  type: file
  path: "output/analysis_results.json"
  format: json

# YAML file output
output:
  type: file
  path: "reports/monthly/summary.yaml"
  format: yaml

# Print to console
output:
  type: print
  format: json

# With directory path
output:
  type: file
  path: "reports/monthly/summary.json"
  format: json
```

---

## 5. AI Interface

Configure LLM integration with prompts and templates.

### Basic AI Configuration

```yaml
ai_interface:
  model:
    type: rest
    url: "https://api.openai.com/v1/chat/completions"
    method: POST
    headers:
      Authorization: "Bearer ${OPENAI_API_KEY}"
      Content-Type: "application/json"
    options:
      model: "gpt-4"
      temperature: 0.7
      max_tokens: 1000
      
  default_context:
    company: "ShedBox Inc"
    date: "2024-01-15"
    
  prompts:
    analyze_users:
      system: "You are a data analyst expert."
      user_template: |
        Analyze this user data and provide insights:
        
        {% for user in users %}
        - Name: {{ user.name }}, Age: {{ user.age }}, City: {{ user.city }}
        {% endfor %}
        
        Provide a summary of demographics and trends.
      response_format: "json"
      temperature: 0.3
```

### Prompt Configuration Options

```yaml
ai_interface:
  prompts:
    prompt_name:
      system: "System message (optional)"
      user_template: "User prompt template with {{ variables }}"
      response_format: "text"  # text, json, markdown, html
      temperature: 0.7         # 0.0 to 1.0
      max_tokens: 1500         # Optional token limit
      for_each: "users"        # Fan-out over data source
      parallel: true           # Process fan-out in parallel
```

### Fan-out Processing

Process prompts for each item in a data source:

```yaml
ai_interface:
  prompts:
    personalized_email:
      system: "You are a marketing expert."
      user_template: |
        Create a personalized email for:
        Name: {{ user.name }}
        Age: {{ user.age }}
        Interests: {{ user.interests | join(', ') }}
        Purchase History: {{ user.orders | length }} orders
        
        Make it engaging and relevant.
      for_each: "users"        # Process once per user
      parallel: true           # Process all users in parallel
      response_format: "text"
```

### Prompt Storage

Store prompts to files without making LLM calls:

```yaml
ai_interface:
  prompt_storage:
    enabled: true
    directory: "./generated_prompts"
    store_only: false          # Set to true to only store, no LLM calls
    file_format: "{prompt_name}_{timestamp}.txt"
    include_metadata: true     # Include context and config
```

### Context Variables

Variables available in all prompt templates:

```yaml
# Data sources are automatically available:
{{ users }}          # Full users data source
{{ products }}        # Full products data source

# For fan-out prompts:
{{ user }}            # Current user item (for_each: "users")
{{ product }}         # Current product item (for_each: "products")

# Default context variables:
{{ company }}         # From ai_interface.default_context
{{ date }}            # From ai_interface.default_context

# Operation results:
{{ user_stats }}      # Results from content_summarization
{{ filtered_data }}   # Results from contextual_filtering
```

---

## Complete Example Configuration

```yaml
# Complete ShedBoxAI configuration example
data_sources:
  users:
    type: csv
    path: "data/users.csv"
    
  transactions:
    type: rest
    url: "https://api.stripe.com/v1/charges"
    headers:
      Authorization: "Bearer ${STRIPE_API_KEY}"
    options:
      params:
        limit: 1000
    response_path: "data"

processing:
  contextual_filtering:
    users:
      - field: "status"
        condition: "active"
      - field: "age"
        condition: ">= 18"
        new_name: "adult_users"
        
  content_summarization:
    adult_users:
      method: "statistical"
      fields: ["age", "account_balance"]
      summarize: ["mean", "min", "max", "count"]
      
  advanced_operations:
    spending_analysis:
      source: "adult_users"
      group_by: "age_group"
      aggregate:
        total_spent: "SUM(account_balance)"
        avg_transaction: "AVG(account_balance)"
        transaction_count: "COUNT(*)"
      sort: "-total_spent"
      limit: 10

ai_interface:
  model:
    type: rest
    url: "https://api.openai.com/v1/chat/completions"
    method: POST
    headers:
      Authorization: "Bearer ${OPENAI_API_KEY}"
      Content-Type: "application/json"
    options:
      model: "gpt-4"
      
  default_context:
    analysis_date: "2024-01-15"
    company: "ShedBox Inc"
    
  prompts:
    customer_analysis:
      system: "You are a business intelligence analyst."
      user_template: |
        Analyze our customer data and spending patterns.
        
        User Statistics: {{ adult_users_summary }}
        Spending Analysis: {{ spending_analysis }}
        
        Provide insights and recommendations.
      response_format: "json"
      temperature: 0.3

output:
  type: file
  path: "output/complete_analysis.json"
  format: json
```

---

## Environment Variables

ShedBoxAI supports environment variable substitution using `${VARIABLE_NAME}` syntax:

```bash
# .env file
OPENAI_API_KEY=sk-your-openai-key
STRIPE_API_KEY=sk_test_your-stripe-key
DATABASE_URL=postgresql://user:pass@localhost/db
API_USERNAME=your_username
API_PASSWORD=your_password
```

---

## CLI Commands

```bash
# Run pipeline
shedboxai run config.yaml
shedboxai run config.yaml --output results.json
shedboxai run config.yaml --verbose

# Data introspection
shedboxai introspect sources.yaml
shedboxai introspect sources.yaml --output analysis.md
shedboxai introspect sources.yaml --include-samples
shedboxai introspect sources.yaml --force --skip-errors
```

---

## Error Handling

ShedBoxAI provides detailed error messages with suggestions:

- **File not found**: Check file paths and permissions
- **API authentication**: Verify API keys and tokens
- **Template errors**: Check Jinja2 syntax and variable availability
- **JSON parsing**: Ensure API responses return valid JSON
- **Missing environment variables**: Check .env file configuration

---

## Best Practices

1. **Use descriptive names** for data sources and operations
2. **Environment variables** for all sensitive data (API keys, passwords)
3. **Test with small datasets** before scaling up
4. **Use fan-out prompts** for personalized AI processing
5. **Store prompts** during development to debug templates
6. **Parallel processing** for better performance with multiple AI calls
7. **Statistical operations** before AI analysis for better context

---

This cheatsheet covers all documented features in ShedBoxAI v0.1.0. For examples and detailed documentation, see the test fixtures and source code.