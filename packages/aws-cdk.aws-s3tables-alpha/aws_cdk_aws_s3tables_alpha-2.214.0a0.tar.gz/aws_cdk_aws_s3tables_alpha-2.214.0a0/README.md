# Amazon S3 Tables Construct Library

<!--BEGIN STABILITY BANNER-->---


![cdk-constructs: Experimental](https://img.shields.io/badge/cdk--constructs-experimental-important.svg?style=for-the-badge)

> The APIs of higher level constructs in this module are experimental and under active development.
> They are subject to non-backward compatible changes or removal in any future version. These are
> not subject to the [Semantic Versioning](https://semver.org/) model and breaking changes will be
> announced in the release notes. This means that while you may use them, you may need to update
> your source code when upgrading to a newer version of this package.

---
<!--END STABILITY BANNER-->

## Amazon S3 Tables

Amazon S3 Tables deliver the first cloud object store with built-in Apache Iceberg support and streamline storing tabular data at scale.

[Product Page](https://aws.amazon.com/s3/features/tables/) | [User Guide](https://docs.aws.amazon.com/AmazonS3/latest/userguide/s3-tables.html)

## Usage

### Define an S3 Table Bucket

```python
# Build a Table bucket
sample_table_bucket = TableBucket(scope, "ExampleTableBucket",
    table_bucket_name="example-bucket-1",
    # optional fields:
    unreferenced_file_removal=UnreferencedFileRemoval(
        status=UnreferencedFileRemovalStatus.ENABLED,
        noncurrent_days=20,
        unreferenced_days=20
    )
)
```

### Define an S3 Tables Namespace

```python
# Build a namespace
sample_namespace = Namespace(scope, "ExampleNamespace",
    namespace_name="example-namespace-1",
    table_bucket=table_bucket
)
```

### Define an S3 Table

```python
# Build a table
sample_table = Table(scope, "ExampleTable",
    table_name="example_table",
    namespace=namespace,
    open_table_format=OpenTableFormat.ICEBERG,
    without_metadata=True
)

# Build a table with an Iceberg Schema
sample_table_with_schema = Table(scope, "ExampleSchemaTable",
    table_name="example_table_with_schema",
    namespace=namespace,
    open_table_format=OpenTableFormat.ICEBERG,
    iceberg_metadata=IcebergMetadataProperty(
        iceberg_schema=IcebergSchemaProperty(
            schema_field_list=[SchemaFieldProperty(
                name="id",
                type="int",
                required=True
            ), SchemaFieldProperty(
                name="name",
                type="string"
            )
            ]
        )
    ),
    compaction=CompactionProperty(
        status=Status.ENABLED,
        target_file_size_mb=128
    ),
    snapshot_management=SnapshotManagementProperty(
        status=Status.ENABLED,
        max_snapshot_age_hours=48,
        min_snapshots_to_keep=5
    )
)
```

Learn more about table buckets maintenance operations and default behavior from the [S3 Tables User Guide](https://docs.aws.amazon.com/AmazonS3/latest/userguide/s3-table-buckets-maintenance.html)

### Controlling Table Bucket Permissions

```python
# Grant the principal read permissions to the bucket and all tables within
account_id = "123456789012"
table_bucket.grant_read(iam.AccountPrincipal(account_id), "*")

# Grant the role write permissions to the bucket and all tables within
role = iam.Role(stack, "MyRole", assumed_by=iam.ServicePrincipal("sample"))
table_bucket.grant_write(role, "*")

# Grant the user read and write permissions to the bucket and all tables within
table_bucket.grant_read_write(iam.User(stack, "MyUser"), "*")

# Grant permissions to the bucket and a particular table within it
table_id = "6ba046b2-26de-44cf-9144-0c7862593a7b"
table_bucket.grant_read_write(iam.AccountPrincipal(account_id), table_id)

# Add custom resource policy statements
permissions = iam.PolicyStatement(
    effect=iam.Effect.ALLOW,
    actions=["s3tables:*"],
    principals=[iam.ServicePrincipal("example.aws.internal")],
    resources=["*"]
)

table_bucket.add_to_resource_policy(permissions)
```

### Controlling Table Bucket Encryption Settings

S3 TableBuckets have SSE (server-side encryption with AES-256) enabled by default with S3 managed keys.
You can also bring your own KMS key for KMS-SSE or have S3 create a KMS key for you.

If a bucket is encrypted with KMS, grant functions on the bucket will also grant access
to the TableBucket's associated KMS key.

```python
# Provide a user defined KMS Key:
key = kms.Key(scope, "UserKey")
encrypted_bucket = TableBucket(scope, "EncryptedTableBucket",
    table_bucket_name="table-bucket-1",
    encryption=TableBucketEncryption.KMS,
    encryption_key=key
)
# This account principal will also receive kms:Decrypt access to the KMS key
encrypted_bucket.grant_read(iam.AccountPrincipal("123456789012"), "*")

# Use S3 managed server side encryption (default)
encrypted_bucket_default = TableBucket(scope, "EncryptedTableBucketDefault",
    table_bucket_name="table-bucket-3",
    encryption=TableBucketEncryption.S3_MANAGED
)
```

When using KMS encryption (`TableBucketEncryption.KMS`), if no encryption key is provided, CDK will automatically create a new KMS key for the table bucket with necessary permissions.

```python
# If no key is provided, one will be created automatically
encrypted_bucket_auto = TableBucket(scope, "EncryptedTableBucketAuto",
    table_bucket_name="table-bucket-2",
    encryption=TableBucketEncryption.KMS
)
```

### Controlling Table Permissions

```python
# Grant the principal read permissions to the table
account_id = "123456789012"
table.grant_read(iam.AccountPrincipal(account_id))

# Grant the role write permissions to the table
role = iam.Role(stack, "MyRole", assumed_by=iam.ServicePrincipal("sample"))
table.grant_write(role)

# Grant the user read and write permissions to the table
table.grant_read_write(iam.User(stack, "MyUser"))

# Grant an account permissions to the table
table.grant_read_write(iam.AccountPrincipal(account_id))

# Add custom resource policy statements
permissions = iam.PolicyStatement(
    effect=iam.Effect.ALLOW,
    actions=["s3tables:*"],
    principals=[iam.ServicePrincipal("example.aws.internal")],
    resources=["*"]
)

table.add_to_resource_policy(permissions)
```

## Coming Soon

L2 Construct support for:

* KMS encryption support for Tables
