r'''
# cdk-s3-vectors

![AWS CDK v2](https://img.shields.io/badge/AWS%20CDK-v2-orange.svg?style=for-the-badge)
![npm version](https://img.shields.io/npm/v/cdk-s3-vectors.svg?style=for-the-badge)
![PyPI version](https://img.shields.io/pypi/v/cdk-s3-vectors.svg?style=for-the-badge)
![NuGet version](https://img.shields.io/nuget/v/bimnett.CdkS3Vectors.svg?style=for-the-badge)
![Maven Central](https://img.shields.io/maven-central/v/io.github.bimnett/cdk-s3-vectors.svg?style=for-the-badge)

> **⚠️ Maintenance Notice**: This library is intended as a temporary solution and will only be maintained until AWS CloudFormation and CDK introduce native support for Amazon S3 Vectors. Once native support is available, users are encouraged to migrate to the official AWS constructs.

## Reference Documentation

[Amazon S3 Vectors User Guide](https://docs.aws.amazon.com/AmazonS3/latest/userguide/s3-vectors.html)

## Supported Languages

| Language | Package |
|----------|---------|
| ![Python Logo](https://docs.aws.amazon.com/cdk/api/latest/img/python32.png) Python | `cdk-s3-vectors` |
| ![TypeScript Logo](https://docs.aws.amazon.com/cdk/api/latest/img/typescript32.png) TypeScript | `cdk-s3-vectors` |
| ![Java Logo](https://docs.aws.amazon.com/cdk/api/latest/img/java32.png) Java | `io.github.bimnett:cdk-s3-vectors` |
| ![.NET Logo](https://docs.aws.amazon.com/cdk/api/latest/img/dotnet32.png) .NET | `bimnett.CdkS3Vectors` |

## Overview

Amazon S3 Vectors is in preview release and provides native vector storage and similarity search capabilities within Amazon S3.

This AWS CDK construct library provides high-level constructs for Amazon S3 Vectors, enabling you to create vector buckets, indexes, and knowledge bases for AI/ML applications.

The library includes three main constructs:

* **Bucket**: Creates S3 vector buckets with optional encryption
* **Index**: Creates vector indexes within buckets for similarity search
* **KnowledgeBase**: Creates Amazon Bedrock knowledge bases using S3 Vectors as the vector store

**IMPORTANT:** The `constructs` library version must be >= 10.0.5.

## Examples

For complete, deployable examples in all supported languages, see the [examples directory](examples/).

## Bucket Construct Props

| Name | Type | Description |
|------|------|-------------|
| `vectorBucketName` | `string` | The name of the vector bucket to create. |
| `encryptionConfiguration?` | `EncryptionConfiguration` | Optional encryption configuration for the vector bucket. Defaults to AES256. |

## Index Construct Props

| Name | Type | Description |
|------|------|-------------|
| `vectorBucketName` | `string` | The name of the vector bucket to create the index in. |
| `indexName` | `string` | The name of the vector index to create. |
| `dataType` | `'float32'` | The data type of the vectors in the index. |
| `dimension` | `number` | The dimensions of the vectors (1-4096). |
| `distanceMetric` | `'euclidean' \| 'cosine'` | The distance metric for similarity search. |
| `metadataConfiguration?` | `MetadataConfiguration` | Optional metadata configuration for the index. |

## KnowledgeBase Construct Props

| Name | Type | Description |
|------|------|-------------|
| `knowledgeBaseName` | `string` | The name of the knowledge base to create. |
| `knowledgeBaseConfiguration` | `KnowledgeBaseConfiguration` | Vector embeddings configuration details. |
| `vectorBucketArn` | `string` | The ARN of the S3 vector bucket. |
| `indexArn` | `string` | The ARN of the vector index. |
| `description?` | `string` | Optional description of the knowledge base. |
| `clientToken?` | `string` | Optional idempotency token (≥33 characters). |

## Pattern Properties

| Name | Type | Description |
|------|------|-------------|
| `vectorBucketName` | `string` | Returns the name of the created vector bucket |
| `vectorBucketArn` | `string` | Returns the ARN of the created vector bucket |
| `indexArn` | `string` | Returns the ARN of the created vector index |
| `indexName` | `string` | Returns the name of the created vector index |
| `knowledgeBaseId` | `string` | Returns the ID of the created knowledge base |
| `knowledgeBaseArn` | `string` | Returns the ARN of the created knowledge base |

## Default Settings

Out of the box implementation of the constructs without any override will set the following defaults:

### Amazon S3 Vector Bucket

* Server-side encryption with Amazon S3 managed keys (SSE-S3) using AES256
* Least privilege IAM permissions for vector operations
* Custom resource handlers for bucket lifecycle management

### Vector Index

* Support for float32 data type vectors
* Configurable dimensions (1-4096)
* Choice of euclidean or cosine distance metrics
* Optional metadata configuration for enhanced search capabilities

### Amazon Bedrock Knowledge Base

* Integration with S3 Vectors as the vector store
* Configurable embedding models
* IAM role with least privilege permissions
* Support for various embedding data types and dimensions

## Architecture

![Architecture Diagram](./architecture.png)

## License

This project is licensed under the Apache License 2.0. See [LICENSE](LICENSE) file for details.
'''
from pkgutil import extend_path
__path__ = extend_path(__path__, __name__)

import abc
import builtins
import datetime
import enum
import typing

import jsii
import publication
import typing_extensions

import typeguard
from importlib.metadata import version as _metadata_package_version
TYPEGUARD_MAJOR_VERSION = int(_metadata_package_version('typeguard').split('.')[0])

def check_type(argname: str, value: object, expected_type: typing.Any) -> typing.Any:
    if TYPEGUARD_MAJOR_VERSION <= 2:
        return typeguard.check_type(argname=argname, value=value, expected_type=expected_type) # type:ignore
    else:
        if isinstance(value, jsii._reference_map.InterfaceDynamicProxy): # pyright: ignore [reportAttributeAccessIssue]
           pass
        else:
            if TYPEGUARD_MAJOR_VERSION == 3:
                typeguard.config.collection_check_strategy = typeguard.CollectionCheckStrategy.ALL_ITEMS # type:ignore
                typeguard.check_type(value=value, expected_type=expected_type) # type:ignore
            else:
                typeguard.check_type(value=value, expected_type=expected_type, collection_check_strategy=typeguard.CollectionCheckStrategy.ALL_ITEMS) # type:ignore

from ._jsii import *

import aws_cdk.aws_iam as _aws_cdk_aws_iam_ceddda9d
import aws_cdk.aws_kms as _aws_cdk_aws_kms_ceddda9d
import constructs as _constructs_77d1e7e8


class Bucket(
    _constructs_77d1e7e8.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="cdk-s3-vectors.Bucket",
):
    '''Amazon S3 Vectors is in preview release for Amazon S3 and is subject to change.

    Creates a vector bucket in the specified AWS Region.
    '''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        vector_bucket_name: builtins.str,
        encryption_configuration: typing.Optional[typing.Union["EncryptionConfiguration", typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param scope: - Represents the scope for all resources.
        :param id: - Scope-unique id.
        :param vector_bucket_name: The name of the vector bucket to create.
        :param encryption_configuration: The encryption configuration for the vector bucket. By default, if you don't specify, all new vectors in Amazon S3 vector buckets use server-side encryption with Amazon S3 managed keys (SSE-S3), specifically ``AES256``.

        :access: public
        :summary: Creates a new Bucket construct for S3 Vectors.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d9edaa1f1d98c4e02d97a4d945867723d647f8ef0343b131abd700709de33f44)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = BucketProps(
            vector_bucket_name=vector_bucket_name,
            encryption_configuration=encryption_configuration,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @jsii.member(jsii_name="grantListIndexes")
    def grant_list_indexes(self, grantee: _aws_cdk_aws_iam_ceddda9d.IGrantable) -> None:
        '''Grants permissions to list indexes within this vector bucket.

        :param grantee: The principal to grant permissions to.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8814e5c8e5cb68de67f35adc2539fb1a03640369cd2dba8ad67aa9075df651c3)
            check_type(argname="argument grantee", value=grantee, expected_type=type_hints["grantee"])
        return typing.cast(None, jsii.invoke(self, "grantListIndexes", [grantee]))

    @builtins.property
    @jsii.member(jsii_name="vectorBucketArn")
    def vector_bucket_arn(self) -> builtins.str:
        '''The ARN (Amazon Resource Name) of the created S3 vector bucket.'''
        return typing.cast(builtins.str, jsii.get(self, "vectorBucketArn"))

    @builtins.property
    @jsii.member(jsii_name="vectorBucketName")
    def vector_bucket_name(self) -> builtins.str:
        '''The name of the vector bucket to create.'''
        return typing.cast(builtins.str, jsii.get(self, "vectorBucketName"))


@jsii.data_type(
    jsii_type="cdk-s3-vectors.BucketProps",
    jsii_struct_bases=[],
    name_mapping={
        "vector_bucket_name": "vectorBucketName",
        "encryption_configuration": "encryptionConfiguration",
    },
)
class BucketProps:
    def __init__(
        self,
        *,
        vector_bucket_name: builtins.str,
        encryption_configuration: typing.Optional[typing.Union["EncryptionConfiguration", typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param vector_bucket_name: The name of the vector bucket to create.
        :param encryption_configuration: The encryption configuration for the vector bucket. By default, if you don't specify, all new vectors in Amazon S3 vector buckets use server-side encryption with Amazon S3 managed keys (SSE-S3), specifically ``AES256``.
        '''
        if isinstance(encryption_configuration, dict):
            encryption_configuration = EncryptionConfiguration(**encryption_configuration)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a054e26758b0a9a16ccef134921b9212892a6bc377a074e9cf09885d976fcb25)
            check_type(argname="argument vector_bucket_name", value=vector_bucket_name, expected_type=type_hints["vector_bucket_name"])
            check_type(argname="argument encryption_configuration", value=encryption_configuration, expected_type=type_hints["encryption_configuration"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "vector_bucket_name": vector_bucket_name,
        }
        if encryption_configuration is not None:
            self._values["encryption_configuration"] = encryption_configuration

    @builtins.property
    def vector_bucket_name(self) -> builtins.str:
        '''The name of the vector bucket to create.'''
        result = self._values.get("vector_bucket_name")
        assert result is not None, "Required property 'vector_bucket_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def encryption_configuration(self) -> typing.Optional["EncryptionConfiguration"]:
        '''The encryption configuration for the vector bucket.

        By default, if you don't specify, all new vectors in Amazon S3 vector buckets use
        server-side encryption with Amazon S3 managed keys (SSE-S3), specifically ``AES256``.
        '''
        result = self._values.get("encryption_configuration")
        return typing.cast(typing.Optional["EncryptionConfiguration"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "BucketProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="cdk-s3-vectors.EncryptionConfiguration",
    jsii_struct_bases=[],
    name_mapping={"sse_type": "sseType", "kms_key": "kmsKey"},
)
class EncryptionConfiguration:
    def __init__(
        self,
        *,
        sse_type: builtins.str,
        kms_key: typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey] = None,
    ) -> None:
        '''
        :param sse_type: The server-side encryption type. Must be ``AES256`` or ``aws:kms``. By default, if you don't specify, all new vectors in Amazon S3 vector buckets use server-side encryption with Amazon S3 managed keys (SSE-S3), specifically ``AES256``.
        :param kms_key: The AWS Key Management Service (KMS) customer managed key to use for server-side encryption. This parameter is allowed if and **only** if ``sseType`` is set to ``aws:kms``.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6075852e4f05906863e2721cf995bb40fc90be9628f5a7115420fdc6da6d0035)
            check_type(argname="argument sse_type", value=sse_type, expected_type=type_hints["sse_type"])
            check_type(argname="argument kms_key", value=kms_key, expected_type=type_hints["kms_key"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "sse_type": sse_type,
        }
        if kms_key is not None:
            self._values["kms_key"] = kms_key

    @builtins.property
    def sse_type(self) -> builtins.str:
        '''The server-side encryption type. Must be ``AES256`` or ``aws:kms``.

        By default, if you don't specify, all new vectors in Amazon S3 vector buckets use
        server-side encryption with Amazon S3 managed keys (SSE-S3), specifically ``AES256``.
        '''
        result = self._values.get("sse_type")
        assert result is not None, "Required property 'sse_type' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def kms_key(self) -> typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey]:
        '''The AWS Key Management Service (KMS) customer managed key to use for server-side encryption.

        This parameter is allowed if and **only** if ``sseType`` is set to ``aws:kms``.
        '''
        result = self._values.get("kms_key")
        return typing.cast(typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "EncryptionConfiguration(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class Index(
    _constructs_77d1e7e8.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="cdk-s3-vectors.Index",
):
    '''Amazon S3 Vectors is in preview release for Amazon S3 and is subject to change.

    Creates a vector index within a vector bucket.
    To specify the vector bucket, you must use either the vector bucket name or the vector bucket ARN (Amazon Resource Name).
    '''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        data_type: builtins.str,
        dimension: jsii.Number,
        distance_metric: builtins.str,
        index_name: builtins.str,
        vector_bucket_name: builtins.str,
        metadata_configuration: typing.Optional[typing.Union["MetadataConfiguration", typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param scope: - Represents the scope for all resources.
        :param id: - Scope-unique id.
        :param data_type: The data type of the vectors in the index. Must be 'float32'
        :param dimension: The dimensions of the vectors to be inserted into the vector index.
        :param distance_metric: The distance metric to be used for similarity search.
        :param index_name: The name of the vector index to create.
        :param vector_bucket_name: The name of the vector bucket to create the vector index in.
        :param metadata_configuration: The metadata configuration for the vector index.

        :access: public
        :summary: Creates a new Index construct for S3 Vectors.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c834b9e75dfc8505f4fc568e315d2057bda8849922d0debaa6c30e9c8537bd52)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = IndexProps(
            data_type=data_type,
            dimension=dimension,
            distance_metric=distance_metric,
            index_name=index_name,
            vector_bucket_name=vector_bucket_name,
            metadata_configuration=metadata_configuration,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @jsii.member(jsii_name="grantWrite")
    def grant_write(self, grantee: _aws_cdk_aws_iam_ceddda9d.IGrantable) -> None:
        '''Grants write permissions (add/delete vectors) to the index.

        :param grantee: The principal to grant permissions to.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d6c4913a61661037683d4776f5f1bd99d02cd6371d75fe6539d0e020bdbc87b9)
            check_type(argname="argument grantee", value=grantee, expected_type=type_hints["grantee"])
        return typing.cast(None, jsii.invoke(self, "grantWrite", [grantee]))

    @builtins.property
    @jsii.member(jsii_name="indexArn")
    def index_arn(self) -> builtins.str:
        '''The ARN (Amazon Resource Name) of the S3 Vector index.'''
        return typing.cast(builtins.str, jsii.get(self, "indexArn"))

    @builtins.property
    @jsii.member(jsii_name="indexName")
    def index_name(self) -> builtins.str:
        '''The name of the index.'''
        return typing.cast(builtins.str, jsii.get(self, "indexName"))


@jsii.data_type(
    jsii_type="cdk-s3-vectors.IndexProps",
    jsii_struct_bases=[],
    name_mapping={
        "data_type": "dataType",
        "dimension": "dimension",
        "distance_metric": "distanceMetric",
        "index_name": "indexName",
        "vector_bucket_name": "vectorBucketName",
        "metadata_configuration": "metadataConfiguration",
    },
)
class IndexProps:
    def __init__(
        self,
        *,
        data_type: builtins.str,
        dimension: jsii.Number,
        distance_metric: builtins.str,
        index_name: builtins.str,
        vector_bucket_name: builtins.str,
        metadata_configuration: typing.Optional[typing.Union["MetadataConfiguration", typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param data_type: The data type of the vectors in the index. Must be 'float32'
        :param dimension: The dimensions of the vectors to be inserted into the vector index.
        :param distance_metric: The distance metric to be used for similarity search.
        :param index_name: The name of the vector index to create.
        :param vector_bucket_name: The name of the vector bucket to create the vector index in.
        :param metadata_configuration: The metadata configuration for the vector index.
        '''
        if isinstance(metadata_configuration, dict):
            metadata_configuration = MetadataConfiguration(**metadata_configuration)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8edf26480d672ff3ff838d0b11805136f699e8f46b061bbec3b0dfc9d9205ad8)
            check_type(argname="argument data_type", value=data_type, expected_type=type_hints["data_type"])
            check_type(argname="argument dimension", value=dimension, expected_type=type_hints["dimension"])
            check_type(argname="argument distance_metric", value=distance_metric, expected_type=type_hints["distance_metric"])
            check_type(argname="argument index_name", value=index_name, expected_type=type_hints["index_name"])
            check_type(argname="argument vector_bucket_name", value=vector_bucket_name, expected_type=type_hints["vector_bucket_name"])
            check_type(argname="argument metadata_configuration", value=metadata_configuration, expected_type=type_hints["metadata_configuration"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "data_type": data_type,
            "dimension": dimension,
            "distance_metric": distance_metric,
            "index_name": index_name,
            "vector_bucket_name": vector_bucket_name,
        }
        if metadata_configuration is not None:
            self._values["metadata_configuration"] = metadata_configuration

    @builtins.property
    def data_type(self) -> builtins.str:
        '''The data type of the vectors in the index.

        Must be 'float32'
        '''
        result = self._values.get("data_type")
        assert result is not None, "Required property 'data_type' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def dimension(self) -> jsii.Number:
        '''The dimensions of the vectors to be inserted into the vector index.'''
        result = self._values.get("dimension")
        assert result is not None, "Required property 'dimension' is missing"
        return typing.cast(jsii.Number, result)

    @builtins.property
    def distance_metric(self) -> builtins.str:
        '''The distance metric to be used for similarity search.'''
        result = self._values.get("distance_metric")
        assert result is not None, "Required property 'distance_metric' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def index_name(self) -> builtins.str:
        '''The name of the vector index to create.'''
        result = self._values.get("index_name")
        assert result is not None, "Required property 'index_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def vector_bucket_name(self) -> builtins.str:
        '''The name of the vector bucket to create the vector index in.'''
        result = self._values.get("vector_bucket_name")
        assert result is not None, "Required property 'vector_bucket_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def metadata_configuration(self) -> typing.Optional["MetadataConfiguration"]:
        '''The metadata configuration for the vector index.'''
        result = self._values.get("metadata_configuration")
        return typing.cast(typing.Optional["MetadataConfiguration"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "IndexProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class KnowledgeBase(
    _constructs_77d1e7e8.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="cdk-s3-vectors.KnowledgeBase",
):
    '''Creates a Amazon Bedrock knowledge base with S3 Vectors as the underlying vector store.

    To create a knowledge base, you must first set up and configure a S3 Vectors bucket and index.
    For more information, see `Set up a knowledge base <https://docs.aws.amazon.com/bedrock/latest/userguide/knowlege-base-prereq.html>`_.
    '''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        index_arn: builtins.str,
        knowledge_base_configuration: typing.Union["KnowledgeBaseConfiguration", typing.Dict[builtins.str, typing.Any]],
        knowledge_base_name: builtins.str,
        vector_bucket_arn: builtins.str,
        client_token: typing.Optional[builtins.str] = None,
        description: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param scope: - Represents the scope for all resources.
        :param id: - Scope-unique id.
        :param index_arn: The ARN (Amazon Resource Name) of the vector index used for the knowledge base. This ARN identifies the specific vector index resource within Amazon Bedrock.
        :param knowledge_base_configuration: Contains details about the vector embeddings configuration of the knowledge base.
        :param knowledge_base_name: The name of the knowledge base to create.
        :param vector_bucket_arn: The ARN (Amazon Resource Name) of the S3 bucket where vector embeddings are stored. This bucket contains the vector data used by the knowledge base.
        :param client_token: A unique, case-sensitive identifier to ensure that the API request completes no more than one time. Must have length greater than or equal to 33. If this token matches a previous request, Amazon Bedrock ignores the request, but does not return an error. For more information, see `Ensuring Idempotency <https://docs.aws.amazon.com/AWSEC2/latest/APIReference/Run_Instance_Idempotency.html>`_.
        :param description: A description of the knowledge base.

        :access: public
        :summary: Creates a new Bedrock knowledge base construct with S3 Vectors as the vector store.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b667231f867e1b93db172642113dea5a66a4d7c85fc14f36be44417317c4c4bf)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = KnowledgeBaseProps(
            index_arn=index_arn,
            knowledge_base_configuration=knowledge_base_configuration,
            knowledge_base_name=knowledge_base_name,
            vector_bucket_arn=vector_bucket_arn,
            client_token=client_token,
            description=description,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @jsii.member(jsii_name="grantIngestion")
    def grant_ingestion(self, grantee: _aws_cdk_aws_iam_ceddda9d.IGrantable) -> None:
        '''Grants permission to start an ingestion job for the knowledge base.

        :param grantee: The principal to grant permissions to.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__60b335d0d151b90bf31bd147e61bf09a0672e75b9d7a4570d5710ccd7717e5ab)
            check_type(argname="argument grantee", value=grantee, expected_type=type_hints["grantee"])
        return typing.cast(None, jsii.invoke(self, "grantIngestion", [grantee]))

    @builtins.property
    @jsii.member(jsii_name="knowledgeBaseArn")
    def knowledge_base_arn(self) -> builtins.str:
        '''The Amazon Resource Name (ARN) of the knowledge base.'''
        return typing.cast(builtins.str, jsii.get(self, "knowledgeBaseArn"))

    @builtins.property
    @jsii.member(jsii_name="knowledgeBaseId")
    def knowledge_base_id(self) -> builtins.str:
        '''The ID of the knowledge base.'''
        return typing.cast(builtins.str, jsii.get(self, "knowledgeBaseId"))


@jsii.data_type(
    jsii_type="cdk-s3-vectors.KnowledgeBaseConfiguration",
    jsii_struct_bases=[],
    name_mapping={
        "embedding_model_arn": "embeddingModelArn",
        "dimensions": "dimensions",
        "embedding_data_type": "embeddingDataType",
    },
)
class KnowledgeBaseConfiguration:
    def __init__(
        self,
        *,
        embedding_model_arn: builtins.str,
        dimensions: typing.Optional[builtins.str] = None,
        embedding_data_type: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param embedding_model_arn: The ARN (Amazon Resource Name) of the model used to create vector embeddings for the knowledge base.
        :param dimensions: The dimensions details for the vector configuration used on the Bedrock embeddings model. Must be supported by the chosen embedding model.
        :param embedding_data_type: The data type for the vectors when using a model to convert text into vector embeddings. The model must support the specified data type for vector embeddings. Floating-point (float32) is the default data type, and is supported by most models for vector embeddings. See `Supported embeddings models <https://docs.aws.amazon.com/bedrock/latest/userguide/knowledge-base-supported.html>`_ for information on the available models and their vector data types.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2417f7a0db3af0479d50240f2ea1107a97381024a9c10d2a2d221f0931804432)
            check_type(argname="argument embedding_model_arn", value=embedding_model_arn, expected_type=type_hints["embedding_model_arn"])
            check_type(argname="argument dimensions", value=dimensions, expected_type=type_hints["dimensions"])
            check_type(argname="argument embedding_data_type", value=embedding_data_type, expected_type=type_hints["embedding_data_type"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "embedding_model_arn": embedding_model_arn,
        }
        if dimensions is not None:
            self._values["dimensions"] = dimensions
        if embedding_data_type is not None:
            self._values["embedding_data_type"] = embedding_data_type

    @builtins.property
    def embedding_model_arn(self) -> builtins.str:
        '''The ARN (Amazon Resource Name) of the model used to create vector embeddings for the knowledge base.'''
        result = self._values.get("embedding_model_arn")
        assert result is not None, "Required property 'embedding_model_arn' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def dimensions(self) -> typing.Optional[builtins.str]:
        '''The dimensions details for the vector configuration used on the Bedrock embeddings model.

        Must be supported by the chosen embedding model.
        '''
        result = self._values.get("dimensions")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def embedding_data_type(self) -> typing.Optional[builtins.str]:
        '''The data type for the vectors when using a model to convert text into vector embeddings.

        The model must support the specified data type for vector embeddings.

        Floating-point (float32) is the default data type, and is supported by most models for vector embeddings.
        See `Supported embeddings models <https://docs.aws.amazon.com/bedrock/latest/userguide/knowledge-base-supported.html>`_
        for information on the available models and their vector data types.
        '''
        result = self._values.get("embedding_data_type")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "KnowledgeBaseConfiguration(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="cdk-s3-vectors.KnowledgeBaseProps",
    jsii_struct_bases=[],
    name_mapping={
        "index_arn": "indexArn",
        "knowledge_base_configuration": "knowledgeBaseConfiguration",
        "knowledge_base_name": "knowledgeBaseName",
        "vector_bucket_arn": "vectorBucketArn",
        "client_token": "clientToken",
        "description": "description",
    },
)
class KnowledgeBaseProps:
    def __init__(
        self,
        *,
        index_arn: builtins.str,
        knowledge_base_configuration: typing.Union[KnowledgeBaseConfiguration, typing.Dict[builtins.str, typing.Any]],
        knowledge_base_name: builtins.str,
        vector_bucket_arn: builtins.str,
        client_token: typing.Optional[builtins.str] = None,
        description: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param index_arn: The ARN (Amazon Resource Name) of the vector index used for the knowledge base. This ARN identifies the specific vector index resource within Amazon Bedrock.
        :param knowledge_base_configuration: Contains details about the vector embeddings configuration of the knowledge base.
        :param knowledge_base_name: The name of the knowledge base to create.
        :param vector_bucket_arn: The ARN (Amazon Resource Name) of the S3 bucket where vector embeddings are stored. This bucket contains the vector data used by the knowledge base.
        :param client_token: A unique, case-sensitive identifier to ensure that the API request completes no more than one time. Must have length greater than or equal to 33. If this token matches a previous request, Amazon Bedrock ignores the request, but does not return an error. For more information, see `Ensuring Idempotency <https://docs.aws.amazon.com/AWSEC2/latest/APIReference/Run_Instance_Idempotency.html>`_.
        :param description: A description of the knowledge base.
        '''
        if isinstance(knowledge_base_configuration, dict):
            knowledge_base_configuration = KnowledgeBaseConfiguration(**knowledge_base_configuration)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c8bd95204a2a934a97444dd9e200751aa36cd7805b211c4289b15c2999c0f397)
            check_type(argname="argument index_arn", value=index_arn, expected_type=type_hints["index_arn"])
            check_type(argname="argument knowledge_base_configuration", value=knowledge_base_configuration, expected_type=type_hints["knowledge_base_configuration"])
            check_type(argname="argument knowledge_base_name", value=knowledge_base_name, expected_type=type_hints["knowledge_base_name"])
            check_type(argname="argument vector_bucket_arn", value=vector_bucket_arn, expected_type=type_hints["vector_bucket_arn"])
            check_type(argname="argument client_token", value=client_token, expected_type=type_hints["client_token"])
            check_type(argname="argument description", value=description, expected_type=type_hints["description"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "index_arn": index_arn,
            "knowledge_base_configuration": knowledge_base_configuration,
            "knowledge_base_name": knowledge_base_name,
            "vector_bucket_arn": vector_bucket_arn,
        }
        if client_token is not None:
            self._values["client_token"] = client_token
        if description is not None:
            self._values["description"] = description

    @builtins.property
    def index_arn(self) -> builtins.str:
        '''The ARN (Amazon Resource Name) of the vector index used for the knowledge base.

        This ARN identifies the specific vector index resource within Amazon Bedrock.
        '''
        result = self._values.get("index_arn")
        assert result is not None, "Required property 'index_arn' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def knowledge_base_configuration(self) -> KnowledgeBaseConfiguration:
        '''Contains details about the vector embeddings configuration of the knowledge base.'''
        result = self._values.get("knowledge_base_configuration")
        assert result is not None, "Required property 'knowledge_base_configuration' is missing"
        return typing.cast(KnowledgeBaseConfiguration, result)

    @builtins.property
    def knowledge_base_name(self) -> builtins.str:
        '''The name of the knowledge base to create.'''
        result = self._values.get("knowledge_base_name")
        assert result is not None, "Required property 'knowledge_base_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def vector_bucket_arn(self) -> builtins.str:
        '''The ARN (Amazon Resource Name) of the S3 bucket where vector embeddings are stored.

        This bucket contains the vector data used by the knowledge base.
        '''
        result = self._values.get("vector_bucket_arn")
        assert result is not None, "Required property 'vector_bucket_arn' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def client_token(self) -> typing.Optional[builtins.str]:
        '''A unique, case-sensitive identifier to ensure that the API request completes no more than one time.

        Must have length greater than or equal to 33.

        If this token matches a previous request, Amazon Bedrock ignores the request, but does not return an error.
        For more information, see `Ensuring Idempotency <https://docs.aws.amazon.com/AWSEC2/latest/APIReference/Run_Instance_Idempotency.html>`_.
        '''
        result = self._values.get("client_token")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        '''A description of the knowledge base.'''
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "KnowledgeBaseProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="cdk-s3-vectors.MetadataConfiguration",
    jsii_struct_bases=[],
    name_mapping={"non_filterable_metadata_keys": "nonFilterableMetadataKeys"},
)
class MetadataConfiguration:
    def __init__(
        self,
        *,
        non_filterable_metadata_keys: typing.Sequence[builtins.str],
    ) -> None:
        '''
        :param non_filterable_metadata_keys: Non-filterable metadata keys allow you to enrich vectors with additional context during storage and retrieval. Unlike default metadata keys, these keys can't be used as query filters. Non-filterable metadata keys can be retrieved but can't be searched, queried, or filtered. You can access non-filterable metadata keys of your vectors after finding the vectors. For more information about non-filterable metadata keys, see `Vectors <https://docs.aws.amazon.com/AmazonS3/latest/userguide/s3-vectors-vectors.html>`_ and `Limitations and restrictions <https://docs.aws.amazon.com/AmazonS3/latest/userguide/s3-vectors-limitations.html>`_ in the *Amazon S3 User Guide*.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0f2996b3bd63b1f119458ffe16ae65f6c7fa768cb29d192df1a909f5796093aa)
            check_type(argname="argument non_filterable_metadata_keys", value=non_filterable_metadata_keys, expected_type=type_hints["non_filterable_metadata_keys"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "non_filterable_metadata_keys": non_filterable_metadata_keys,
        }

    @builtins.property
    def non_filterable_metadata_keys(self) -> typing.List[builtins.str]:
        '''Non-filterable metadata keys allow you to enrich vectors with additional context during storage and retrieval.

        Unlike default metadata keys, these keys can't be used as query filters.

        Non-filterable metadata keys can be retrieved but can't be searched, queried, or filtered.
        You can access non-filterable metadata keys of your vectors after finding the vectors.
        For more information about non-filterable metadata keys, see
        `Vectors <https://docs.aws.amazon.com/AmazonS3/latest/userguide/s3-vectors-vectors.html>`_ and
        `Limitations and restrictions <https://docs.aws.amazon.com/AmazonS3/latest/userguide/s3-vectors-limitations.html>`_
        in the *Amazon S3 User Guide*.
        '''
        result = self._values.get("non_filterable_metadata_keys")
        assert result is not None, "Required property 'non_filterable_metadata_keys' is missing"
        return typing.cast(typing.List[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "MetadataConfiguration(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "Bucket",
    "BucketProps",
    "EncryptionConfiguration",
    "Index",
    "IndexProps",
    "KnowledgeBase",
    "KnowledgeBaseConfiguration",
    "KnowledgeBaseProps",
    "MetadataConfiguration",
]

publication.publish()

def _typecheckingstub__d9edaa1f1d98c4e02d97a4d945867723d647f8ef0343b131abd700709de33f44(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    vector_bucket_name: builtins.str,
    encryption_configuration: typing.Optional[typing.Union[EncryptionConfiguration, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8814e5c8e5cb68de67f35adc2539fb1a03640369cd2dba8ad67aa9075df651c3(
    grantee: _aws_cdk_aws_iam_ceddda9d.IGrantable,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a054e26758b0a9a16ccef134921b9212892a6bc377a074e9cf09885d976fcb25(
    *,
    vector_bucket_name: builtins.str,
    encryption_configuration: typing.Optional[typing.Union[EncryptionConfiguration, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6075852e4f05906863e2721cf995bb40fc90be9628f5a7115420fdc6da6d0035(
    *,
    sse_type: builtins.str,
    kms_key: typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c834b9e75dfc8505f4fc568e315d2057bda8849922d0debaa6c30e9c8537bd52(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    data_type: builtins.str,
    dimension: jsii.Number,
    distance_metric: builtins.str,
    index_name: builtins.str,
    vector_bucket_name: builtins.str,
    metadata_configuration: typing.Optional[typing.Union[MetadataConfiguration, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d6c4913a61661037683d4776f5f1bd99d02cd6371d75fe6539d0e020bdbc87b9(
    grantee: _aws_cdk_aws_iam_ceddda9d.IGrantable,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8edf26480d672ff3ff838d0b11805136f699e8f46b061bbec3b0dfc9d9205ad8(
    *,
    data_type: builtins.str,
    dimension: jsii.Number,
    distance_metric: builtins.str,
    index_name: builtins.str,
    vector_bucket_name: builtins.str,
    metadata_configuration: typing.Optional[typing.Union[MetadataConfiguration, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b667231f867e1b93db172642113dea5a66a4d7c85fc14f36be44417317c4c4bf(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    index_arn: builtins.str,
    knowledge_base_configuration: typing.Union[KnowledgeBaseConfiguration, typing.Dict[builtins.str, typing.Any]],
    knowledge_base_name: builtins.str,
    vector_bucket_arn: builtins.str,
    client_token: typing.Optional[builtins.str] = None,
    description: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__60b335d0d151b90bf31bd147e61bf09a0672e75b9d7a4570d5710ccd7717e5ab(
    grantee: _aws_cdk_aws_iam_ceddda9d.IGrantable,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2417f7a0db3af0479d50240f2ea1107a97381024a9c10d2a2d221f0931804432(
    *,
    embedding_model_arn: builtins.str,
    dimensions: typing.Optional[builtins.str] = None,
    embedding_data_type: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c8bd95204a2a934a97444dd9e200751aa36cd7805b211c4289b15c2999c0f397(
    *,
    index_arn: builtins.str,
    knowledge_base_configuration: typing.Union[KnowledgeBaseConfiguration, typing.Dict[builtins.str, typing.Any]],
    knowledge_base_name: builtins.str,
    vector_bucket_arn: builtins.str,
    client_token: typing.Optional[builtins.str] = None,
    description: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0f2996b3bd63b1f119458ffe16ae65f6c7fa768cb29d192df1a909f5796093aa(
    *,
    non_filterable_metadata_keys: typing.Sequence[builtins.str],
) -> None:
    """Type checking stubs"""
    pass
