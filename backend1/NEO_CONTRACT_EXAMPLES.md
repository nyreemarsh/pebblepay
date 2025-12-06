# Neo Contract Generator - Usage Examples

## API Endpoints

### 1. Generate Contract

**POST** `/api/neo/generate_contract`

Generate a Neo smart contract from a JSON specification.

**Request Body:**
```json
{
  "contract_name": "EscrowContract",
  "actions": [
    {
      "type": "store_value",
      "key": "sender",
      "value_type": "UInt160"
    },
    {
      "type": "store_value",
      "key": "recipient",
      "value_type": "UInt160"
    },
    {
      "type": "store_value",
      "key": "amount",
      "value_type": "int"
    },
    {
      "type": "release_payment",
      "from": "sender",
      "to": "recipient",
      "amount_key": "amount"
    }
  ]
}
```

**Response:**
```json
{
  "status": "success",
  "contract_name": "EscrowContract",
  "file_path": "/path/to/contracts/EscrowContract.py",
  "source_code": "from boa3.builtin import ..."
}
```

### 2. Compile Contract

**POST** `/api/neo/compile_contract`

Compile a generated contract using the Boa compiler.

**Request Body:**
```json
{
  "contract_name": "EscrowContract"
}
```

**Response:**
```json
{
  "status": "success",
  "contract_name": "EscrowContract",
  "nef_path": "/path/to/contracts/EscrowContract.nef",
  "manifest_path": "/path/to/contracts/EscrowContract.manifest.json",
  "compiler_output": "..."
}
```

### 3. List Contracts

**GET** `/api/neo/contracts`

List all generated contracts.

**Response:**
```json
{
  "contracts": [
    {
      "name": "EscrowContract",
      "file_path": "/path/to/contracts/EscrowContract.py",
      "exists": true,
      "nef_exists": true,
      "manifest_exists": true
    }
  ]
}
```

### 4. Get Contract Source

**GET** `/api/neo/contracts/{contract_name}`

Get the source code of a generated contract.

**Response:**
```json
{
  "contract_name": "EscrowContract",
  "source_code": "from boa3.builtin import ...",
  "file_path": "/path/to/contracts/EscrowContract.py"
}
```

## Example Contract Specifications

### Escrow Contract
```json
{
  "contract_name": "EscrowContract",
  "actions": [
    {
      "type": "store_value",
      "key": "sender",
      "value_type": "UInt160"
    },
    {
      "type": "store_value",
      "key": "recipient",
      "value_type": "UInt160"
    },
    {
      "type": "store_value",
      "key": "amount",
      "value_type": "int"
    },
    {
      "type": "release_payment",
      "from": "sender",
      "to": "recipient",
      "amount_key": "amount"
    }
  ]
}
```

### Token Transfer Contract
```json
{
  "contract_name": "TokenTransfer",
  "actions": [
    {
      "type": "store_value",
      "key": "token_contract",
      "value_type": "UInt160"
    },
    {
      "type": "store_value",
      "key": "recipient",
      "value_type": "UInt160"
    },
    {
      "type": "store_value",
      "key": "amount",
      "value_type": "int"
    },
    {
      "type": "transfer_token",
      "token_contract": "token_contract",
      "from": "sender",
      "to": "recipient",
      "amount_key": "amount"
    }
  ]
}
```

## Testing with cURL

```bash
# Generate a contract
curl -X POST http://localhost:8000/api/neo/generate_contract \
  -H "Content-Type: application/json" \
  -d '{
    "contract_name": "EscrowContract",
    "actions": [
      {
        "type": "store_value",
        "key": "sender",
        "value_type": "UInt160"
      },
      {
        "type": "release_payment",
        "from": "sender",
        "to": "recipient",
        "amount_key": "amount"
      }
    ]
  }'

# Compile the contract
curl -X POST http://localhost:8000/api/neo/compile_contract \
  -H "Content-Type: application/json" \
  -d '{
    "contract_name": "EscrowContract"
  }'

# List all contracts
curl http://localhost:8000/api/neo/contracts

# Get contract source
curl http://localhost:8000/api/neo/contracts/EscrowContract
```

## Notes

- Contracts are saved to `backend/contracts/` directory
- The Boa compiler must be installed: `pip install boa3`
- Generated contracts follow Neo Boa constraints (no f-strings, limited Python features)
- All public methods use `@public` decorator
- Storage operations use `Storage.get()` and `Storage.put()`


