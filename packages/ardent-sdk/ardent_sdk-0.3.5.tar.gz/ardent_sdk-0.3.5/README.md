# Ardent SDK

Python SDK for Ardent AI - Simplify your data engineering tasks.

## Installation

bash
pip install ardent-sdk

## Quick Start

python
from ardent import ArdentClient
Using context manager
with ArdentClient("your-api-key") as client:
# Create a new job
job = client.create_job("Create a hello world program")
# Execute the job
result = client.execute_job(
job_id=job["id"],
message="Create a hello world program",
files_share_name=job["files_share_name"],
user_id=job["userID"]
)
print(result)
Or without context manager
client = ArdentClient("your-api-key")
try:
job = client.create_job("Hello world")
# ... use the client
finally:
client.close()


## Error Handling

The SDK provides several exception types:
- `ArdentError`: Base exception class
- `ArdentAPIError`: Raised when API requests fail
- `ArdentAuthError`: Raised for authentication issues
- `ArdentValidationError`: Raised for invalid input

## License

This project is licensed under the MIT License - see the LICENSE file for details.

