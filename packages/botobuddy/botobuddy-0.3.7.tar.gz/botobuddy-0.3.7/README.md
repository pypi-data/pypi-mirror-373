# A Collection of Extension Functions Based on Boto3

## Supported CLI Commands

### DynamoDB Commands
- **truncate-table**: Truncate a DynamoDB table by deleting all its items.

### S3 Commands
- **delete-bucket**: Clean and delete an S3 bucket completely, including all objects and versions.
- **ls**: List all objects in an S3 bucket. The same as `aws s3 ls`, but useful with `--assume-role`.
- **view-dict**: View a dictionary stored in an S3 bucket as a JSON object.

### Route 53 Commands
- **export-hosted-zone**: Export all resource record sets from a specified hosted zone.
- **import-hosted-zone**: Import resource record sets into a specified hosted zone from a file, skipping NS and SOA records.


### SageMaker Commands
- **human-effort**: Generate a report on the human effort that a SageMaker job required.


## Noteable Functions and Classes

### `botobuddy.utils.dslice`

This function is used to slice a dictionary into a new dictionary, using the keys to define the slice.
Each key can be a string, or a dictionary with the following keys:
- `k`: the key to slice
- `c`: the cast or conversion function
- `d`: the default value
- `n`: the name of the key in the result dictionary

### `botobuddy.s3.S3Uri`

This class is used to represent an S3 URI, and provides methods to parse and manipulate it.

## Development Environment Quickstart

```pwsh
uv sync
uv run botobuddy --help
```

## Session Configuration

This library uses the `session_config` transversely for AWS Session configuration and other general configuration parameters, generally supplied to the CLI.

This is a dictionary with the following keys, all optional:

- `profile`: The AWS profile to use.
- `region`: The AWS region to use.
- `assume_role`: The AWS role to assume.
