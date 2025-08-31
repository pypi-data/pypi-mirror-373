
# Running Sage_AI Tests

## Step 1: Configure `config.ts`
Copy the example config file:

```bash
cp tests/config-example.ts tests/config.ts
```
## Step 2: Add Configs

Update `tests/config.ts` with your API key and other required configs.

## Step 3: Install & Run Tests

Navigate to the UI tests folder, install dependencies, and run the tests:

```bash
cd jupyter-sage-agent-internal/ui-tests
jlpm install
jlpm run test
```
