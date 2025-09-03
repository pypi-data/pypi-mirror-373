r'''
# AWS Secure Log Bucket

[![GitHub](https://img.shields.io/github/license/yicr/aws-secure-log-bucket?style=flat-square)](https://github.com/yicr/aws-secure-log-bucket/blob/main/LICENSE)
[![npm (scoped)](https://img.shields.io/npm/v/@gammarers/aws-secure-log-bucket?style=flat-square)](https://www.npmjs.com/package/@gammarers/aws-secure-log-bucket)
[![PyPI](https://img.shields.io/pypi/v/gammarers.aws-secure-log-bucket?style=flat-square)](https://pypi.org/project/gammarers.aws-secure-log-bucket/)
[![Nuget](https://img.shields.io/nuget/v/Gammarers.CDK.AWS.SecureLogBucket?style=flat-square)](https://www.nuget.org/packages/Gammarers.CDK.AWS.SecureLogBucket/)
[![GitHub Workflow Status (branch)](https://img.shields.io/github/actions/workflow/status/yicr/aws-secure-log-bucket/release.yml?branch=main&label=release&style=flat-square)](https://github.com/yicr/aws-secure-log-bucket/actions/workflows/release.yml)
[![GitHub release (latest SemVer)](https://img.shields.io/github/v/release/yicr/aws-secure-log-bucket?sort=semver&style=flat-square)](https://github.com/yicr/aws-secure-log-bucket/releases)

[![View on Construct Hub](https://constructs.dev/badge?package=@gammarers/aws-secure-log-bucket)](https://constructs.dev/packages/@gammarers/aws-secure-log-bucket)

secure multiple transition phases in a single lifecycle policy bucket.

## Lifecycle rule

The storage class will be changed with the following lifecycle configuration.

| Storage Class       | Default transition after days |
| ------------------- |------------------------------ |
| INFREQUENT_ACCESS   | 400 days                      |
| GLACIER             | 720 days                      |
| DEEP_ARCHIVE        | 980 days                      |

## Additional Properties

| **Name** | **Type** | **Default** | **Description** |
| --- | --- | --- | --- |
| logBucketType | SecureLogBucketType | SecureLogBucketType.NORMAL | The type of the bucket. Available types: NORMAL, VPC_FLOW_LOG |
| vpcFlowLog | VPCFlowLog | - | **⚠️ Deprecated**: This property is deprecated. Use the `logBucketType` property instead. Configuration for VPC Flow Log bucket settings. |

## Install

### TypeScript

#### install by npm

```shell
npm install @gammarers/aws-secure-log-bucket
```

#### install by yarn

```shell
yarn add @gammarers/aws-secure-log-bucket
```

### Python

```shell
pip install gammarers.aws-secure-log-bucket
```

### C# / .NET

```shell
dotnet add package Gammarers.CDK.AWS.SecureLogBucket
```

## Example

### Normal log Bucket

```python
import { SecureLogBucket } from '@gammarers/aws-secure-log-bucket';

new SecureLogBucket(stack, 'SecureLogBucket');
```

### VPC Flow Log Bucket

```python
import { SecureLogBucket } from '@gammarers/aws-secure-log-bucket';

new SecureLogBucket(stack, 'SecureFlowLogBucket', {
  logBucketType: SecureLogBucketType.VPC_FLOW_LOG,
  bucketObjectKeyPrefix: [
    'example-prefix-a',
    'example-prefix-b',
  ],
});
```

## License

This project is licensed under the Apache-2.0 License.
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

import aws_cdk as _aws_cdk_ceddda9d
import aws_cdk.aws_iam as _aws_cdk_aws_iam_ceddda9d
import aws_cdk.aws_kms as _aws_cdk_aws_kms_ceddda9d
import aws_cdk.aws_s3 as _aws_cdk_aws_s3_ceddda9d
import constructs as _constructs_77d1e7e8
import gammarers.aws_secure_bucket as _gammarers_aws_secure_bucket_0aa7e232


@jsii.data_type(
    jsii_type="@gammarers/aws-secure-log-bucket.LifecycleStorageClassTransition",
    jsii_struct_bases=[],
    name_mapping={
        "transition_step_deep_archive": "transitionStepDeepArchive",
        "transition_step_glacier": "transitionStepGlacier",
        "transition_step_infrequent_access": "transitionStepInfrequentAccess",
    },
)
class LifecycleStorageClassTransition:
    def __init__(
        self,
        *,
        transition_step_deep_archive: typing.Optional[typing.Union["TransitionStep", typing.Dict[builtins.str, typing.Any]]] = None,
        transition_step_glacier: typing.Optional[typing.Union["TransitionStep", typing.Dict[builtins.str, typing.Any]]] = None,
        transition_step_infrequent_access: typing.Optional[typing.Union["TransitionStep", typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param transition_step_deep_archive: 
        :param transition_step_glacier: 
        :param transition_step_infrequent_access: 
        '''
        if isinstance(transition_step_deep_archive, dict):
            transition_step_deep_archive = TransitionStep(**transition_step_deep_archive)
        if isinstance(transition_step_glacier, dict):
            transition_step_glacier = TransitionStep(**transition_step_glacier)
        if isinstance(transition_step_infrequent_access, dict):
            transition_step_infrequent_access = TransitionStep(**transition_step_infrequent_access)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__398cdc8180a48893a387e0c7a96e9f07d78c1a6e3628db3d88eacb7e76407eef)
            check_type(argname="argument transition_step_deep_archive", value=transition_step_deep_archive, expected_type=type_hints["transition_step_deep_archive"])
            check_type(argname="argument transition_step_glacier", value=transition_step_glacier, expected_type=type_hints["transition_step_glacier"])
            check_type(argname="argument transition_step_infrequent_access", value=transition_step_infrequent_access, expected_type=type_hints["transition_step_infrequent_access"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if transition_step_deep_archive is not None:
            self._values["transition_step_deep_archive"] = transition_step_deep_archive
        if transition_step_glacier is not None:
            self._values["transition_step_glacier"] = transition_step_glacier
        if transition_step_infrequent_access is not None:
            self._values["transition_step_infrequent_access"] = transition_step_infrequent_access

    @builtins.property
    def transition_step_deep_archive(self) -> typing.Optional["TransitionStep"]:
        result = self._values.get("transition_step_deep_archive")
        return typing.cast(typing.Optional["TransitionStep"], result)

    @builtins.property
    def transition_step_glacier(self) -> typing.Optional["TransitionStep"]:
        result = self._values.get("transition_step_glacier")
        return typing.cast(typing.Optional["TransitionStep"], result)

    @builtins.property
    def transition_step_infrequent_access(self) -> typing.Optional["TransitionStep"]:
        result = self._values.get("transition_step_infrequent_access")
        return typing.cast(typing.Optional["TransitionStep"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "LifecycleStorageClassTransition(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class SecureLogBucket(
    _gammarers_aws_secure_bucket_0aa7e232.SecureBucket,
    metaclass=jsii.JSIIMeta,
    jsii_type="@gammarers/aws-secure-log-bucket.SecureLogBucket",
):
    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        props: typing.Optional[typing.Union[typing.Union["SecureNormalLogBucketProps", typing.Dict[builtins.str, typing.Any]], typing.Union["SecureVpcFlowLogBucketProps", typing.Dict[builtins.str, typing.Any]]]] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param props: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__631e2fc5db951a1d650e81f02732903146ef035c7350dab2c626b18ea9b5b593)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument props", value=props, expected_type=type_hints["props"])
        jsii.create(self.__class__, self, [scope, id, props])


@jsii.enum(jsii_type="@gammarers/aws-secure-log-bucket.SecureLogBucketType")
class SecureLogBucketType(enum.Enum):
    NORMAL = "NORMAL"
    VPC_FLOW_LOG = "VPC_FLOW_LOG"


@jsii.data_type(
    jsii_type="@gammarers/aws-secure-log-bucket.SecureNormalLogBucketProps",
    jsii_struct_bases=[_gammarers_aws_secure_bucket_0aa7e232.SecureBucketProps],
    name_mapping={
        "access_control": "accessControl",
        "auto_delete_objects": "autoDeleteObjects",
        "block_public_access": "blockPublicAccess",
        "bucket_key_enabled": "bucketKeyEnabled",
        "bucket_name": "bucketName",
        "cors": "cors",
        "encryption": "encryption",
        "encryption_key": "encryptionKey",
        "enforce_ssl": "enforceSSL",
        "event_bridge_enabled": "eventBridgeEnabled",
        "intelligent_tiering_configurations": "intelligentTieringConfigurations",
        "inventories": "inventories",
        "lifecycle_rules": "lifecycleRules",
        "metrics": "metrics",
        "minimum_tls_version": "minimumTLSVersion",
        "notifications_handler_role": "notificationsHandlerRole",
        "notifications_skip_destination_validation": "notificationsSkipDestinationValidation",
        "object_lock_default_retention": "objectLockDefaultRetention",
        "object_lock_enabled": "objectLockEnabled",
        "object_ownership": "objectOwnership",
        "public_read_access": "publicReadAccess",
        "removal_policy": "removalPolicy",
        "replication_rules": "replicationRules",
        "server_access_logs_bucket": "serverAccessLogsBucket",
        "server_access_logs_prefix": "serverAccessLogsPrefix",
        "target_object_key_format": "targetObjectKeyFormat",
        "transfer_acceleration": "transferAcceleration",
        "transition_default_minimum_object_size": "transitionDefaultMinimumObjectSize",
        "versioned": "versioned",
        "website_error_document": "websiteErrorDocument",
        "website_index_document": "websiteIndexDocument",
        "website_redirect": "websiteRedirect",
        "website_routing_rules": "websiteRoutingRules",
        "bucket_type": "bucketType",
        "is_cloud_front_origin_bucket": "isCloudFrontOriginBucket",
        "is_pipeline_artifact_bucket": "isPipelineArtifactBucket",
        "lifecycle_storage_class_transition": "lifecycleStorageClassTransition",
        "log_bucket_type": "logBucketType",
        "vpc_flow_log": "vpcFlowLog",
    },
)
class SecureNormalLogBucketProps(
    _gammarers_aws_secure_bucket_0aa7e232.SecureBucketProps,
):
    def __init__(
        self,
        *,
        access_control: typing.Optional[_aws_cdk_aws_s3_ceddda9d.BucketAccessControl] = None,
        auto_delete_objects: typing.Optional[builtins.bool] = None,
        block_public_access: typing.Optional[_aws_cdk_aws_s3_ceddda9d.BlockPublicAccess] = None,
        bucket_key_enabled: typing.Optional[builtins.bool] = None,
        bucket_name: typing.Optional[builtins.str] = None,
        cors: typing.Optional[typing.Sequence[typing.Union[_aws_cdk_aws_s3_ceddda9d.CorsRule, typing.Dict[builtins.str, typing.Any]]]] = None,
        encryption: typing.Optional[_aws_cdk_aws_s3_ceddda9d.BucketEncryption] = None,
        encryption_key: typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey] = None,
        enforce_ssl: typing.Optional[builtins.bool] = None,
        event_bridge_enabled: typing.Optional[builtins.bool] = None,
        intelligent_tiering_configurations: typing.Optional[typing.Sequence[typing.Union[_aws_cdk_aws_s3_ceddda9d.IntelligentTieringConfiguration, typing.Dict[builtins.str, typing.Any]]]] = None,
        inventories: typing.Optional[typing.Sequence[typing.Union[_aws_cdk_aws_s3_ceddda9d.Inventory, typing.Dict[builtins.str, typing.Any]]]] = None,
        lifecycle_rules: typing.Optional[typing.Sequence[typing.Union[_aws_cdk_aws_s3_ceddda9d.LifecycleRule, typing.Dict[builtins.str, typing.Any]]]] = None,
        metrics: typing.Optional[typing.Sequence[typing.Union[_aws_cdk_aws_s3_ceddda9d.BucketMetrics, typing.Dict[builtins.str, typing.Any]]]] = None,
        minimum_tls_version: typing.Optional[jsii.Number] = None,
        notifications_handler_role: typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole] = None,
        notifications_skip_destination_validation: typing.Optional[builtins.bool] = None,
        object_lock_default_retention: typing.Optional[_aws_cdk_aws_s3_ceddda9d.ObjectLockRetention] = None,
        object_lock_enabled: typing.Optional[builtins.bool] = None,
        object_ownership: typing.Optional[_aws_cdk_aws_s3_ceddda9d.ObjectOwnership] = None,
        public_read_access: typing.Optional[builtins.bool] = None,
        removal_policy: typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy] = None,
        replication_rules: typing.Optional[typing.Sequence[typing.Union[_aws_cdk_aws_s3_ceddda9d.ReplicationRule, typing.Dict[builtins.str, typing.Any]]]] = None,
        server_access_logs_bucket: typing.Optional[_aws_cdk_aws_s3_ceddda9d.IBucket] = None,
        server_access_logs_prefix: typing.Optional[builtins.str] = None,
        target_object_key_format: typing.Optional[_aws_cdk_aws_s3_ceddda9d.TargetObjectKeyFormat] = None,
        transfer_acceleration: typing.Optional[builtins.bool] = None,
        transition_default_minimum_object_size: typing.Optional[_aws_cdk_aws_s3_ceddda9d.TransitionDefaultMinimumObjectSize] = None,
        versioned: typing.Optional[builtins.bool] = None,
        website_error_document: typing.Optional[builtins.str] = None,
        website_index_document: typing.Optional[builtins.str] = None,
        website_redirect: typing.Optional[typing.Union[_aws_cdk_aws_s3_ceddda9d.RedirectTarget, typing.Dict[builtins.str, typing.Any]]] = None,
        website_routing_rules: typing.Optional[typing.Sequence[typing.Union[_aws_cdk_aws_s3_ceddda9d.RoutingRule, typing.Dict[builtins.str, typing.Any]]]] = None,
        bucket_type: typing.Optional[_gammarers_aws_secure_bucket_0aa7e232.SecureBucketType] = None,
        is_cloud_front_origin_bucket: typing.Optional[builtins.bool] = None,
        is_pipeline_artifact_bucket: typing.Optional[builtins.bool] = None,
        lifecycle_storage_class_transition: typing.Optional[typing.Union[LifecycleStorageClassTransition, typing.Dict[builtins.str, typing.Any]]] = None,
        log_bucket_type: typing.Optional[SecureLogBucketType] = None,
        vpc_flow_log: typing.Optional[typing.Union["VPCFlowLog", typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param access_control: Specifies a canned ACL that grants predefined permissions to the bucket. Default: BucketAccessControl.PRIVATE
        :param auto_delete_objects: Whether all objects should be automatically deleted when the bucket is removed from the stack or when the stack is deleted. Requires the ``removalPolicy`` to be set to ``RemovalPolicy.DESTROY``. **Warning** if you have deployed a bucket with ``autoDeleteObjects: true``, switching this to ``false`` in a CDK version *before* ``1.126.0`` will lead to all objects in the bucket being deleted. Be sure to update your bucket resources by deploying with CDK version ``1.126.0`` or later **before** switching this value to ``false``. Setting ``autoDeleteObjects`` to true on a bucket will add ``s3:PutBucketPolicy`` to the bucket policy. This is because during bucket deletion, the custom resource provider needs to update the bucket policy by adding a deny policy for ``s3:PutObject`` to prevent race conditions with external bucket writers. Default: false
        :param block_public_access: The block public access configuration of this bucket. Default: - CloudFormation defaults will apply. New buckets and objects don't allow public access, but users can modify bucket policies or object permissions to allow public access
        :param bucket_key_enabled: Whether Amazon S3 should use its own intermediary key to generate data keys. Only relevant when using KMS for encryption. - If not enabled, every object GET and PUT will cause an API call to KMS (with the attendant cost implications of that). - If enabled, S3 will use its own time-limited key instead. Only relevant, when Encryption is not set to ``BucketEncryption.UNENCRYPTED``. Default: - false
        :param bucket_name: Physical name of this bucket. Default: - Assigned by CloudFormation (recommended).
        :param cors: The CORS configuration of this bucket. Default: - No CORS configuration.
        :param encryption: The kind of server-side encryption to apply to this bucket. If you choose KMS, you can specify a KMS key via ``encryptionKey``. If encryption key is not specified, a key will automatically be created. Default: - ``KMS`` if ``encryptionKey`` is specified, or ``S3_MANAGED`` otherwise.
        :param encryption_key: External KMS key to use for bucket encryption. The ``encryption`` property must be either not specified or set to ``KMS`` or ``DSSE``. An error will be emitted if ``encryption`` is set to ``UNENCRYPTED`` or ``S3_MANAGED``. Default: - If ``encryption`` is set to ``KMS`` and this property is undefined, a new KMS key will be created and associated with this bucket.
        :param enforce_ssl: Enforces SSL for requests. S3.5 of the AWS Foundational Security Best Practices Regarding S3. Default: false
        :param event_bridge_enabled: Whether this bucket should send notifications to Amazon EventBridge or not. Default: false
        :param intelligent_tiering_configurations: Intelligent Tiering Configurations. Default: No Intelligent Tiiering Configurations.
        :param inventories: The inventory configuration of the bucket. Default: - No inventory configuration
        :param lifecycle_rules: Rules that define how Amazon S3 manages objects during their lifetime. Default: - No lifecycle rules.
        :param metrics: The metrics configuration of this bucket. Default: - No metrics configuration.
        :param minimum_tls_version: Enforces minimum TLS version for requests. Requires ``enforceSSL`` to be enabled. Default: No minimum TLS version is enforced.
        :param notifications_handler_role: The role to be used by the notifications handler. Default: - a new role will be created.
        :param notifications_skip_destination_validation: Skips notification validation of Amazon SQS, Amazon SNS, and Lambda destinations. Default: false
        :param object_lock_default_retention: The default retention mode and rules for S3 Object Lock. Default retention can be configured after a bucket is created if the bucket already has object lock enabled. Enabling object lock for existing buckets is not supported. Default: no default retention period
        :param object_lock_enabled: Enable object lock on the bucket. Enabling object lock for existing buckets is not supported. Object lock must be enabled when the bucket is created. Default: false, unless objectLockDefaultRetention is set (then, true)
        :param object_ownership: The objectOwnership of the bucket. Default: - No ObjectOwnership configuration. By default, Amazon S3 sets Object Ownership to ``Bucket owner enforced``. This means ACLs are disabled and the bucket owner will own every object.
        :param public_read_access: Grants public read access to all objects in the bucket. Similar to calling ``bucket.grantPublicAccess()`` Default: false
        :param removal_policy: Policy to apply when the bucket is removed from this stack. Default: - The bucket will be orphaned.
        :param replication_rules: A container for one or more replication rules. Default: - No replication
        :param server_access_logs_bucket: Destination bucket for the server access logs. Default: - If "serverAccessLogsPrefix" undefined - access logs disabled, otherwise - log to current bucket.
        :param server_access_logs_prefix: Optional log file prefix to use for the bucket's access logs. If defined without "serverAccessLogsBucket", enables access logs to current bucket with this prefix. Default: - No log file prefix
        :param target_object_key_format: Optional key format for log objects. Default: - the default key format is: [DestinationPrefix][YYYY]-[MM]-[DD]-[hh]-[mm]-[ss]-[UniqueString]
        :param transfer_acceleration: Whether this bucket should have transfer acceleration turned on or not. Default: false
        :param transition_default_minimum_object_size: Indicates which default minimum object size behavior is applied to the lifecycle configuration. To customize the minimum object size for any transition you can add a filter that specifies a custom ``objectSizeGreaterThan`` or ``objectSizeLessThan`` for ``lifecycleRules`` property. Custom filters always take precedence over the default transition behavior. Default: - TransitionDefaultMinimumObjectSize.VARIES_BY_STORAGE_CLASS before September 2024, otherwise TransitionDefaultMinimumObjectSize.ALL_STORAGE_CLASSES_128_K.
        :param versioned: Whether this bucket should have versioning turned on or not. Default: false (unless object lock is enabled, then true)
        :param website_error_document: The name of the error document (e.g. "404.html") for the website. ``websiteIndexDocument`` must also be set if this is set. Default: - No error document.
        :param website_index_document: The name of the index document (e.g. "index.html") for the website. Enables static website hosting for this bucket. Default: - No index document.
        :param website_redirect: Specifies the redirect behavior of all requests to a website endpoint of a bucket. If you specify this property, you can't specify "websiteIndexDocument", "websiteErrorDocument" nor , "websiteRoutingRules". Default: - No redirection.
        :param website_routing_rules: Rules that define when a redirect is applied and the redirect behavior. Default: - No redirection rules.
        :param bucket_type: The type of the bucket. Default: SecureBucketType.DEFAULT
        :param is_cloud_front_origin_bucket: (deprecated) If your are using it as the CloudFront origin bucket, set it to true. Default: false
        :param is_pipeline_artifact_bucket: (deprecated) If you are setting a custom Qualifier and using it as the artifact bucket for the CDK pipeline, set it to true. Default: false
        :param lifecycle_storage_class_transition: 
        :param log_bucket_type: The type of the bucket. Default: SecureLogBucketType.NORMAL
        :param vpc_flow_log: 
        '''
        if isinstance(website_redirect, dict):
            website_redirect = _aws_cdk_aws_s3_ceddda9d.RedirectTarget(**website_redirect)
        if isinstance(lifecycle_storage_class_transition, dict):
            lifecycle_storage_class_transition = LifecycleStorageClassTransition(**lifecycle_storage_class_transition)
        if isinstance(vpc_flow_log, dict):
            vpc_flow_log = VPCFlowLog(**vpc_flow_log)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c95a530793a173bfc4ba531e27cd2e424336eac2091debbb3ab7cd15dfa79018)
            check_type(argname="argument access_control", value=access_control, expected_type=type_hints["access_control"])
            check_type(argname="argument auto_delete_objects", value=auto_delete_objects, expected_type=type_hints["auto_delete_objects"])
            check_type(argname="argument block_public_access", value=block_public_access, expected_type=type_hints["block_public_access"])
            check_type(argname="argument bucket_key_enabled", value=bucket_key_enabled, expected_type=type_hints["bucket_key_enabled"])
            check_type(argname="argument bucket_name", value=bucket_name, expected_type=type_hints["bucket_name"])
            check_type(argname="argument cors", value=cors, expected_type=type_hints["cors"])
            check_type(argname="argument encryption", value=encryption, expected_type=type_hints["encryption"])
            check_type(argname="argument encryption_key", value=encryption_key, expected_type=type_hints["encryption_key"])
            check_type(argname="argument enforce_ssl", value=enforce_ssl, expected_type=type_hints["enforce_ssl"])
            check_type(argname="argument event_bridge_enabled", value=event_bridge_enabled, expected_type=type_hints["event_bridge_enabled"])
            check_type(argname="argument intelligent_tiering_configurations", value=intelligent_tiering_configurations, expected_type=type_hints["intelligent_tiering_configurations"])
            check_type(argname="argument inventories", value=inventories, expected_type=type_hints["inventories"])
            check_type(argname="argument lifecycle_rules", value=lifecycle_rules, expected_type=type_hints["lifecycle_rules"])
            check_type(argname="argument metrics", value=metrics, expected_type=type_hints["metrics"])
            check_type(argname="argument minimum_tls_version", value=minimum_tls_version, expected_type=type_hints["minimum_tls_version"])
            check_type(argname="argument notifications_handler_role", value=notifications_handler_role, expected_type=type_hints["notifications_handler_role"])
            check_type(argname="argument notifications_skip_destination_validation", value=notifications_skip_destination_validation, expected_type=type_hints["notifications_skip_destination_validation"])
            check_type(argname="argument object_lock_default_retention", value=object_lock_default_retention, expected_type=type_hints["object_lock_default_retention"])
            check_type(argname="argument object_lock_enabled", value=object_lock_enabled, expected_type=type_hints["object_lock_enabled"])
            check_type(argname="argument object_ownership", value=object_ownership, expected_type=type_hints["object_ownership"])
            check_type(argname="argument public_read_access", value=public_read_access, expected_type=type_hints["public_read_access"])
            check_type(argname="argument removal_policy", value=removal_policy, expected_type=type_hints["removal_policy"])
            check_type(argname="argument replication_rules", value=replication_rules, expected_type=type_hints["replication_rules"])
            check_type(argname="argument server_access_logs_bucket", value=server_access_logs_bucket, expected_type=type_hints["server_access_logs_bucket"])
            check_type(argname="argument server_access_logs_prefix", value=server_access_logs_prefix, expected_type=type_hints["server_access_logs_prefix"])
            check_type(argname="argument target_object_key_format", value=target_object_key_format, expected_type=type_hints["target_object_key_format"])
            check_type(argname="argument transfer_acceleration", value=transfer_acceleration, expected_type=type_hints["transfer_acceleration"])
            check_type(argname="argument transition_default_minimum_object_size", value=transition_default_minimum_object_size, expected_type=type_hints["transition_default_minimum_object_size"])
            check_type(argname="argument versioned", value=versioned, expected_type=type_hints["versioned"])
            check_type(argname="argument website_error_document", value=website_error_document, expected_type=type_hints["website_error_document"])
            check_type(argname="argument website_index_document", value=website_index_document, expected_type=type_hints["website_index_document"])
            check_type(argname="argument website_redirect", value=website_redirect, expected_type=type_hints["website_redirect"])
            check_type(argname="argument website_routing_rules", value=website_routing_rules, expected_type=type_hints["website_routing_rules"])
            check_type(argname="argument bucket_type", value=bucket_type, expected_type=type_hints["bucket_type"])
            check_type(argname="argument is_cloud_front_origin_bucket", value=is_cloud_front_origin_bucket, expected_type=type_hints["is_cloud_front_origin_bucket"])
            check_type(argname="argument is_pipeline_artifact_bucket", value=is_pipeline_artifact_bucket, expected_type=type_hints["is_pipeline_artifact_bucket"])
            check_type(argname="argument lifecycle_storage_class_transition", value=lifecycle_storage_class_transition, expected_type=type_hints["lifecycle_storage_class_transition"])
            check_type(argname="argument log_bucket_type", value=log_bucket_type, expected_type=type_hints["log_bucket_type"])
            check_type(argname="argument vpc_flow_log", value=vpc_flow_log, expected_type=type_hints["vpc_flow_log"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if access_control is not None:
            self._values["access_control"] = access_control
        if auto_delete_objects is not None:
            self._values["auto_delete_objects"] = auto_delete_objects
        if block_public_access is not None:
            self._values["block_public_access"] = block_public_access
        if bucket_key_enabled is not None:
            self._values["bucket_key_enabled"] = bucket_key_enabled
        if bucket_name is not None:
            self._values["bucket_name"] = bucket_name
        if cors is not None:
            self._values["cors"] = cors
        if encryption is not None:
            self._values["encryption"] = encryption
        if encryption_key is not None:
            self._values["encryption_key"] = encryption_key
        if enforce_ssl is not None:
            self._values["enforce_ssl"] = enforce_ssl
        if event_bridge_enabled is not None:
            self._values["event_bridge_enabled"] = event_bridge_enabled
        if intelligent_tiering_configurations is not None:
            self._values["intelligent_tiering_configurations"] = intelligent_tiering_configurations
        if inventories is not None:
            self._values["inventories"] = inventories
        if lifecycle_rules is not None:
            self._values["lifecycle_rules"] = lifecycle_rules
        if metrics is not None:
            self._values["metrics"] = metrics
        if minimum_tls_version is not None:
            self._values["minimum_tls_version"] = minimum_tls_version
        if notifications_handler_role is not None:
            self._values["notifications_handler_role"] = notifications_handler_role
        if notifications_skip_destination_validation is not None:
            self._values["notifications_skip_destination_validation"] = notifications_skip_destination_validation
        if object_lock_default_retention is not None:
            self._values["object_lock_default_retention"] = object_lock_default_retention
        if object_lock_enabled is not None:
            self._values["object_lock_enabled"] = object_lock_enabled
        if object_ownership is not None:
            self._values["object_ownership"] = object_ownership
        if public_read_access is not None:
            self._values["public_read_access"] = public_read_access
        if removal_policy is not None:
            self._values["removal_policy"] = removal_policy
        if replication_rules is not None:
            self._values["replication_rules"] = replication_rules
        if server_access_logs_bucket is not None:
            self._values["server_access_logs_bucket"] = server_access_logs_bucket
        if server_access_logs_prefix is not None:
            self._values["server_access_logs_prefix"] = server_access_logs_prefix
        if target_object_key_format is not None:
            self._values["target_object_key_format"] = target_object_key_format
        if transfer_acceleration is not None:
            self._values["transfer_acceleration"] = transfer_acceleration
        if transition_default_minimum_object_size is not None:
            self._values["transition_default_minimum_object_size"] = transition_default_minimum_object_size
        if versioned is not None:
            self._values["versioned"] = versioned
        if website_error_document is not None:
            self._values["website_error_document"] = website_error_document
        if website_index_document is not None:
            self._values["website_index_document"] = website_index_document
        if website_redirect is not None:
            self._values["website_redirect"] = website_redirect
        if website_routing_rules is not None:
            self._values["website_routing_rules"] = website_routing_rules
        if bucket_type is not None:
            self._values["bucket_type"] = bucket_type
        if is_cloud_front_origin_bucket is not None:
            self._values["is_cloud_front_origin_bucket"] = is_cloud_front_origin_bucket
        if is_pipeline_artifact_bucket is not None:
            self._values["is_pipeline_artifact_bucket"] = is_pipeline_artifact_bucket
        if lifecycle_storage_class_transition is not None:
            self._values["lifecycle_storage_class_transition"] = lifecycle_storage_class_transition
        if log_bucket_type is not None:
            self._values["log_bucket_type"] = log_bucket_type
        if vpc_flow_log is not None:
            self._values["vpc_flow_log"] = vpc_flow_log

    @builtins.property
    def access_control(
        self,
    ) -> typing.Optional[_aws_cdk_aws_s3_ceddda9d.BucketAccessControl]:
        '''Specifies a canned ACL that grants predefined permissions to the bucket.

        :default: BucketAccessControl.PRIVATE
        '''
        result = self._values.get("access_control")
        return typing.cast(typing.Optional[_aws_cdk_aws_s3_ceddda9d.BucketAccessControl], result)

    @builtins.property
    def auto_delete_objects(self) -> typing.Optional[builtins.bool]:
        '''Whether all objects should be automatically deleted when the bucket is removed from the stack or when the stack is deleted.

        Requires the ``removalPolicy`` to be set to ``RemovalPolicy.DESTROY``.

        **Warning** if you have deployed a bucket with ``autoDeleteObjects: true``,
        switching this to ``false`` in a CDK version *before* ``1.126.0`` will lead to
        all objects in the bucket being deleted. Be sure to update your bucket resources
        by deploying with CDK version ``1.126.0`` or later **before** switching this value to ``false``.

        Setting ``autoDeleteObjects`` to true on a bucket will add ``s3:PutBucketPolicy`` to the
        bucket policy. This is because during bucket deletion, the custom resource provider
        needs to update the bucket policy by adding a deny policy for ``s3:PutObject`` to
        prevent race conditions with external bucket writers.

        :default: false
        '''
        result = self._values.get("auto_delete_objects")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def block_public_access(
        self,
    ) -> typing.Optional[_aws_cdk_aws_s3_ceddda9d.BlockPublicAccess]:
        '''The block public access configuration of this bucket.

        :default: - CloudFormation defaults will apply. New buckets and objects don't allow public access, but users can modify bucket policies or object permissions to allow public access

        :see: https://docs.aws.amazon.com/AmazonS3/latest/dev/access-control-block-public-access.html
        '''
        result = self._values.get("block_public_access")
        return typing.cast(typing.Optional[_aws_cdk_aws_s3_ceddda9d.BlockPublicAccess], result)

    @builtins.property
    def bucket_key_enabled(self) -> typing.Optional[builtins.bool]:
        '''Whether Amazon S3 should use its own intermediary key to generate data keys.

        Only relevant when using KMS for encryption.

        - If not enabled, every object GET and PUT will cause an API call to KMS (with the
          attendant cost implications of that).
        - If enabled, S3 will use its own time-limited key instead.

        Only relevant, when Encryption is not set to ``BucketEncryption.UNENCRYPTED``.

        :default: - false
        '''
        result = self._values.get("bucket_key_enabled")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def bucket_name(self) -> typing.Optional[builtins.str]:
        '''Physical name of this bucket.

        :default: - Assigned by CloudFormation (recommended).
        '''
        result = self._values.get("bucket_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def cors(self) -> typing.Optional[typing.List[_aws_cdk_aws_s3_ceddda9d.CorsRule]]:
        '''The CORS configuration of this bucket.

        :default: - No CORS configuration.

        :see: https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-s3-bucket-cors.html
        '''
        result = self._values.get("cors")
        return typing.cast(typing.Optional[typing.List[_aws_cdk_aws_s3_ceddda9d.CorsRule]], result)

    @builtins.property
    def encryption(self) -> typing.Optional[_aws_cdk_aws_s3_ceddda9d.BucketEncryption]:
        '''The kind of server-side encryption to apply to this bucket.

        If you choose KMS, you can specify a KMS key via ``encryptionKey``. If
        encryption key is not specified, a key will automatically be created.

        :default: - ``KMS`` if ``encryptionKey`` is specified, or ``S3_MANAGED`` otherwise.
        '''
        result = self._values.get("encryption")
        return typing.cast(typing.Optional[_aws_cdk_aws_s3_ceddda9d.BucketEncryption], result)

    @builtins.property
    def encryption_key(self) -> typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey]:
        '''External KMS key to use for bucket encryption.

        The ``encryption`` property must be either not specified or set to ``KMS`` or ``DSSE``.
        An error will be emitted if ``encryption`` is set to ``UNENCRYPTED`` or ``S3_MANAGED``.

        :default:

        - If ``encryption`` is set to ``KMS`` and this property is undefined,
        a new KMS key will be created and associated with this bucket.
        '''
        result = self._values.get("encryption_key")
        return typing.cast(typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey], result)

    @builtins.property
    def enforce_ssl(self) -> typing.Optional[builtins.bool]:
        '''Enforces SSL for requests.

        S3.5 of the AWS Foundational Security Best Practices Regarding S3.

        :default: false

        :see: https://docs.aws.amazon.com/config/latest/developerguide/s3-bucket-ssl-requests-only.html
        '''
        result = self._values.get("enforce_ssl")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def event_bridge_enabled(self) -> typing.Optional[builtins.bool]:
        '''Whether this bucket should send notifications to Amazon EventBridge or not.

        :default: false
        '''
        result = self._values.get("event_bridge_enabled")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def intelligent_tiering_configurations(
        self,
    ) -> typing.Optional[typing.List[_aws_cdk_aws_s3_ceddda9d.IntelligentTieringConfiguration]]:
        '''Intelligent Tiering Configurations.

        :default: No Intelligent Tiiering Configurations.

        :see: https://docs.aws.amazon.com/AmazonS3/latest/userguide/intelligent-tiering.html
        '''
        result = self._values.get("intelligent_tiering_configurations")
        return typing.cast(typing.Optional[typing.List[_aws_cdk_aws_s3_ceddda9d.IntelligentTieringConfiguration]], result)

    @builtins.property
    def inventories(
        self,
    ) -> typing.Optional[typing.List[_aws_cdk_aws_s3_ceddda9d.Inventory]]:
        '''The inventory configuration of the bucket.

        :default: - No inventory configuration

        :see: https://docs.aws.amazon.com/AmazonS3/latest/dev/storage-inventory.html
        '''
        result = self._values.get("inventories")
        return typing.cast(typing.Optional[typing.List[_aws_cdk_aws_s3_ceddda9d.Inventory]], result)

    @builtins.property
    def lifecycle_rules(
        self,
    ) -> typing.Optional[typing.List[_aws_cdk_aws_s3_ceddda9d.LifecycleRule]]:
        '''Rules that define how Amazon S3 manages objects during their lifetime.

        :default: - No lifecycle rules.
        '''
        result = self._values.get("lifecycle_rules")
        return typing.cast(typing.Optional[typing.List[_aws_cdk_aws_s3_ceddda9d.LifecycleRule]], result)

    @builtins.property
    def metrics(
        self,
    ) -> typing.Optional[typing.List[_aws_cdk_aws_s3_ceddda9d.BucketMetrics]]:
        '''The metrics configuration of this bucket.

        :default: - No metrics configuration.

        :see: https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-s3-bucket-metricsconfiguration.html
        '''
        result = self._values.get("metrics")
        return typing.cast(typing.Optional[typing.List[_aws_cdk_aws_s3_ceddda9d.BucketMetrics]], result)

    @builtins.property
    def minimum_tls_version(self) -> typing.Optional[jsii.Number]:
        '''Enforces minimum TLS version for requests.

        Requires ``enforceSSL`` to be enabled.

        :default: No minimum TLS version is enforced.

        :see: https://docs.aws.amazon.com/AmazonS3/latest/userguide/amazon-s3-policy-keys.html#example-object-tls-version
        '''
        result = self._values.get("minimum_tls_version")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def notifications_handler_role(
        self,
    ) -> typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole]:
        '''The role to be used by the notifications handler.

        :default: - a new role will be created.
        '''
        result = self._values.get("notifications_handler_role")
        return typing.cast(typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole], result)

    @builtins.property
    def notifications_skip_destination_validation(
        self,
    ) -> typing.Optional[builtins.bool]:
        '''Skips notification validation of Amazon SQS, Amazon SNS, and Lambda destinations.

        :default: false
        '''
        result = self._values.get("notifications_skip_destination_validation")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def object_lock_default_retention(
        self,
    ) -> typing.Optional[_aws_cdk_aws_s3_ceddda9d.ObjectLockRetention]:
        '''The default retention mode and rules for S3 Object Lock.

        Default retention can be configured after a bucket is created if the bucket already
        has object lock enabled. Enabling object lock for existing buckets is not supported.

        :default: no default retention period

        :see: https://docs.aws.amazon.com/AmazonS3/latest/userguide/object-lock-overview.html#object-lock-bucket-config-enable
        '''
        result = self._values.get("object_lock_default_retention")
        return typing.cast(typing.Optional[_aws_cdk_aws_s3_ceddda9d.ObjectLockRetention], result)

    @builtins.property
    def object_lock_enabled(self) -> typing.Optional[builtins.bool]:
        '''Enable object lock on the bucket.

        Enabling object lock for existing buckets is not supported. Object lock must be
        enabled when the bucket is created.

        :default: false, unless objectLockDefaultRetention is set (then, true)

        :see: https://docs.aws.amazon.com/AmazonS3/latest/userguide/object-lock-overview.html#object-lock-bucket-config-enable
        '''
        result = self._values.get("object_lock_enabled")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def object_ownership(
        self,
    ) -> typing.Optional[_aws_cdk_aws_s3_ceddda9d.ObjectOwnership]:
        '''The objectOwnership of the bucket.

        :default:

        - No ObjectOwnership configuration. By default, Amazon S3 sets Object Ownership to ``Bucket owner enforced``.
        This means ACLs are disabled and the bucket owner will own every object.

        :see: https://docs.aws.amazon.com/AmazonS3/latest/dev/about-object-ownership.html
        '''
        result = self._values.get("object_ownership")
        return typing.cast(typing.Optional[_aws_cdk_aws_s3_ceddda9d.ObjectOwnership], result)

    @builtins.property
    def public_read_access(self) -> typing.Optional[builtins.bool]:
        '''Grants public read access to all objects in the bucket.

        Similar to calling ``bucket.grantPublicAccess()``

        :default: false
        '''
        result = self._values.get("public_read_access")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def removal_policy(self) -> typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy]:
        '''Policy to apply when the bucket is removed from this stack.

        :default: - The bucket will be orphaned.
        '''
        result = self._values.get("removal_policy")
        return typing.cast(typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy], result)

    @builtins.property
    def replication_rules(
        self,
    ) -> typing.Optional[typing.List[_aws_cdk_aws_s3_ceddda9d.ReplicationRule]]:
        '''A container for one or more replication rules.

        :default: - No replication
        '''
        result = self._values.get("replication_rules")
        return typing.cast(typing.Optional[typing.List[_aws_cdk_aws_s3_ceddda9d.ReplicationRule]], result)

    @builtins.property
    def server_access_logs_bucket(
        self,
    ) -> typing.Optional[_aws_cdk_aws_s3_ceddda9d.IBucket]:
        '''Destination bucket for the server access logs.

        :default: - If "serverAccessLogsPrefix" undefined - access logs disabled, otherwise - log to current bucket.
        '''
        result = self._values.get("server_access_logs_bucket")
        return typing.cast(typing.Optional[_aws_cdk_aws_s3_ceddda9d.IBucket], result)

    @builtins.property
    def server_access_logs_prefix(self) -> typing.Optional[builtins.str]:
        '''Optional log file prefix to use for the bucket's access logs.

        If defined without "serverAccessLogsBucket", enables access logs to current bucket with this prefix.

        :default: - No log file prefix
        '''
        result = self._values.get("server_access_logs_prefix")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def target_object_key_format(
        self,
    ) -> typing.Optional[_aws_cdk_aws_s3_ceddda9d.TargetObjectKeyFormat]:
        '''Optional key format for log objects.

        :default: - the default key format is: [DestinationPrefix][YYYY]-[MM]-[DD]-[hh]-[mm]-[ss]-[UniqueString]
        '''
        result = self._values.get("target_object_key_format")
        return typing.cast(typing.Optional[_aws_cdk_aws_s3_ceddda9d.TargetObjectKeyFormat], result)

    @builtins.property
    def transfer_acceleration(self) -> typing.Optional[builtins.bool]:
        '''Whether this bucket should have transfer acceleration turned on or not.

        :default: false
        '''
        result = self._values.get("transfer_acceleration")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def transition_default_minimum_object_size(
        self,
    ) -> typing.Optional[_aws_cdk_aws_s3_ceddda9d.TransitionDefaultMinimumObjectSize]:
        '''Indicates which default minimum object size behavior is applied to the lifecycle configuration.

        To customize the minimum object size for any transition you can add a filter that specifies a custom
        ``objectSizeGreaterThan`` or ``objectSizeLessThan`` for ``lifecycleRules`` property. Custom filters always
        take precedence over the default transition behavior.

        :default:

        - TransitionDefaultMinimumObjectSize.VARIES_BY_STORAGE_CLASS before September 2024,
        otherwise TransitionDefaultMinimumObjectSize.ALL_STORAGE_CLASSES_128_K.
        '''
        result = self._values.get("transition_default_minimum_object_size")
        return typing.cast(typing.Optional[_aws_cdk_aws_s3_ceddda9d.TransitionDefaultMinimumObjectSize], result)

    @builtins.property
    def versioned(self) -> typing.Optional[builtins.bool]:
        '''Whether this bucket should have versioning turned on or not.

        :default: false (unless object lock is enabled, then true)
        '''
        result = self._values.get("versioned")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def website_error_document(self) -> typing.Optional[builtins.str]:
        '''The name of the error document (e.g. "404.html") for the website. ``websiteIndexDocument`` must also be set if this is set.

        :default: - No error document.
        '''
        result = self._values.get("website_error_document")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def website_index_document(self) -> typing.Optional[builtins.str]:
        '''The name of the index document (e.g. "index.html") for the website. Enables static website hosting for this bucket.

        :default: - No index document.
        '''
        result = self._values.get("website_index_document")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def website_redirect(
        self,
    ) -> typing.Optional[_aws_cdk_aws_s3_ceddda9d.RedirectTarget]:
        '''Specifies the redirect behavior of all requests to a website endpoint of a bucket.

        If you specify this property, you can't specify "websiteIndexDocument", "websiteErrorDocument" nor , "websiteRoutingRules".

        :default: - No redirection.
        '''
        result = self._values.get("website_redirect")
        return typing.cast(typing.Optional[_aws_cdk_aws_s3_ceddda9d.RedirectTarget], result)

    @builtins.property
    def website_routing_rules(
        self,
    ) -> typing.Optional[typing.List[_aws_cdk_aws_s3_ceddda9d.RoutingRule]]:
        '''Rules that define when a redirect is applied and the redirect behavior.

        :default: - No redirection rules.
        '''
        result = self._values.get("website_routing_rules")
        return typing.cast(typing.Optional[typing.List[_aws_cdk_aws_s3_ceddda9d.RoutingRule]], result)

    @builtins.property
    def bucket_type(
        self,
    ) -> typing.Optional[_gammarers_aws_secure_bucket_0aa7e232.SecureBucketType]:
        '''The type of the bucket.

        :default: SecureBucketType.DEFAULT
        '''
        result = self._values.get("bucket_type")
        return typing.cast(typing.Optional[_gammarers_aws_secure_bucket_0aa7e232.SecureBucketType], result)

    @builtins.property
    def is_cloud_front_origin_bucket(self) -> typing.Optional[builtins.bool]:
        '''(deprecated) If your are using it as the CloudFront origin bucket, set it to true.

        :default: false

        :deprecated: This property is deprecated. Use the bucketType property instead.

        :stability: deprecated
        '''
        result = self._values.get("is_cloud_front_origin_bucket")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def is_pipeline_artifact_bucket(self) -> typing.Optional[builtins.bool]:
        '''(deprecated) If you are setting a custom Qualifier and using it as the artifact bucket for the CDK pipeline, set it to true.

        :default: false

        :deprecated: This property is deprecated. Use the bucketType property instead.

        :stability: deprecated
        '''
        result = self._values.get("is_pipeline_artifact_bucket")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def lifecycle_storage_class_transition(
        self,
    ) -> typing.Optional[LifecycleStorageClassTransition]:
        result = self._values.get("lifecycle_storage_class_transition")
        return typing.cast(typing.Optional[LifecycleStorageClassTransition], result)

    @builtins.property
    def log_bucket_type(self) -> typing.Optional[SecureLogBucketType]:
        '''The type of the bucket.

        :default: SecureLogBucketType.NORMAL
        '''
        result = self._values.get("log_bucket_type")
        return typing.cast(typing.Optional[SecureLogBucketType], result)

    @builtins.property
    def vpc_flow_log(self) -> typing.Optional["VPCFlowLog"]:
        '''
        :deprecated: This property is deprecated. Use the bucketType property instead.

        :stability: deprecated
        '''
        result = self._values.get("vpc_flow_log")
        return typing.cast(typing.Optional["VPCFlowLog"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "SecureNormalLogBucketProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@gammarers/aws-secure-log-bucket.SecureVpcFlowLogBucketProps",
    jsii_struct_bases=[_gammarers_aws_secure_bucket_0aa7e232.SecureBucketProps],
    name_mapping={
        "access_control": "accessControl",
        "auto_delete_objects": "autoDeleteObjects",
        "block_public_access": "blockPublicAccess",
        "bucket_key_enabled": "bucketKeyEnabled",
        "bucket_name": "bucketName",
        "cors": "cors",
        "encryption": "encryption",
        "encryption_key": "encryptionKey",
        "enforce_ssl": "enforceSSL",
        "event_bridge_enabled": "eventBridgeEnabled",
        "intelligent_tiering_configurations": "intelligentTieringConfigurations",
        "inventories": "inventories",
        "lifecycle_rules": "lifecycleRules",
        "metrics": "metrics",
        "minimum_tls_version": "minimumTLSVersion",
        "notifications_handler_role": "notificationsHandlerRole",
        "notifications_skip_destination_validation": "notificationsSkipDestinationValidation",
        "object_lock_default_retention": "objectLockDefaultRetention",
        "object_lock_enabled": "objectLockEnabled",
        "object_ownership": "objectOwnership",
        "public_read_access": "publicReadAccess",
        "removal_policy": "removalPolicy",
        "replication_rules": "replicationRules",
        "server_access_logs_bucket": "serverAccessLogsBucket",
        "server_access_logs_prefix": "serverAccessLogsPrefix",
        "target_object_key_format": "targetObjectKeyFormat",
        "transfer_acceleration": "transferAcceleration",
        "transition_default_minimum_object_size": "transitionDefaultMinimumObjectSize",
        "versioned": "versioned",
        "website_error_document": "websiteErrorDocument",
        "website_index_document": "websiteIndexDocument",
        "website_redirect": "websiteRedirect",
        "website_routing_rules": "websiteRoutingRules",
        "bucket_type": "bucketType",
        "is_cloud_front_origin_bucket": "isCloudFrontOriginBucket",
        "is_pipeline_artifact_bucket": "isPipelineArtifactBucket",
        "log_bucket_type": "logBucketType",
        "bucket_object_key_prefix": "bucketObjectKeyPrefix",
        "lifecycle_storage_class_transition": "lifecycleStorageClassTransition",
        "vpc_flow_log": "vpcFlowLog",
    },
)
class SecureVpcFlowLogBucketProps(
    _gammarers_aws_secure_bucket_0aa7e232.SecureBucketProps,
):
    def __init__(
        self,
        *,
        access_control: typing.Optional[_aws_cdk_aws_s3_ceddda9d.BucketAccessControl] = None,
        auto_delete_objects: typing.Optional[builtins.bool] = None,
        block_public_access: typing.Optional[_aws_cdk_aws_s3_ceddda9d.BlockPublicAccess] = None,
        bucket_key_enabled: typing.Optional[builtins.bool] = None,
        bucket_name: typing.Optional[builtins.str] = None,
        cors: typing.Optional[typing.Sequence[typing.Union[_aws_cdk_aws_s3_ceddda9d.CorsRule, typing.Dict[builtins.str, typing.Any]]]] = None,
        encryption: typing.Optional[_aws_cdk_aws_s3_ceddda9d.BucketEncryption] = None,
        encryption_key: typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey] = None,
        enforce_ssl: typing.Optional[builtins.bool] = None,
        event_bridge_enabled: typing.Optional[builtins.bool] = None,
        intelligent_tiering_configurations: typing.Optional[typing.Sequence[typing.Union[_aws_cdk_aws_s3_ceddda9d.IntelligentTieringConfiguration, typing.Dict[builtins.str, typing.Any]]]] = None,
        inventories: typing.Optional[typing.Sequence[typing.Union[_aws_cdk_aws_s3_ceddda9d.Inventory, typing.Dict[builtins.str, typing.Any]]]] = None,
        lifecycle_rules: typing.Optional[typing.Sequence[typing.Union[_aws_cdk_aws_s3_ceddda9d.LifecycleRule, typing.Dict[builtins.str, typing.Any]]]] = None,
        metrics: typing.Optional[typing.Sequence[typing.Union[_aws_cdk_aws_s3_ceddda9d.BucketMetrics, typing.Dict[builtins.str, typing.Any]]]] = None,
        minimum_tls_version: typing.Optional[jsii.Number] = None,
        notifications_handler_role: typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole] = None,
        notifications_skip_destination_validation: typing.Optional[builtins.bool] = None,
        object_lock_default_retention: typing.Optional[_aws_cdk_aws_s3_ceddda9d.ObjectLockRetention] = None,
        object_lock_enabled: typing.Optional[builtins.bool] = None,
        object_ownership: typing.Optional[_aws_cdk_aws_s3_ceddda9d.ObjectOwnership] = None,
        public_read_access: typing.Optional[builtins.bool] = None,
        removal_policy: typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy] = None,
        replication_rules: typing.Optional[typing.Sequence[typing.Union[_aws_cdk_aws_s3_ceddda9d.ReplicationRule, typing.Dict[builtins.str, typing.Any]]]] = None,
        server_access_logs_bucket: typing.Optional[_aws_cdk_aws_s3_ceddda9d.IBucket] = None,
        server_access_logs_prefix: typing.Optional[builtins.str] = None,
        target_object_key_format: typing.Optional[_aws_cdk_aws_s3_ceddda9d.TargetObjectKeyFormat] = None,
        transfer_acceleration: typing.Optional[builtins.bool] = None,
        transition_default_minimum_object_size: typing.Optional[_aws_cdk_aws_s3_ceddda9d.TransitionDefaultMinimumObjectSize] = None,
        versioned: typing.Optional[builtins.bool] = None,
        website_error_document: typing.Optional[builtins.str] = None,
        website_index_document: typing.Optional[builtins.str] = None,
        website_redirect: typing.Optional[typing.Union[_aws_cdk_aws_s3_ceddda9d.RedirectTarget, typing.Dict[builtins.str, typing.Any]]] = None,
        website_routing_rules: typing.Optional[typing.Sequence[typing.Union[_aws_cdk_aws_s3_ceddda9d.RoutingRule, typing.Dict[builtins.str, typing.Any]]]] = None,
        bucket_type: typing.Optional[_gammarers_aws_secure_bucket_0aa7e232.SecureBucketType] = None,
        is_cloud_front_origin_bucket: typing.Optional[builtins.bool] = None,
        is_pipeline_artifact_bucket: typing.Optional[builtins.bool] = None,
        log_bucket_type: SecureLogBucketType,
        bucket_object_key_prefix: typing.Optional[typing.Sequence[builtins.str]] = None,
        lifecycle_storage_class_transition: typing.Optional[typing.Union[LifecycleStorageClassTransition, typing.Dict[builtins.str, typing.Any]]] = None,
        vpc_flow_log: typing.Optional[typing.Union["VPCFlowLog", typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param access_control: Specifies a canned ACL that grants predefined permissions to the bucket. Default: BucketAccessControl.PRIVATE
        :param auto_delete_objects: Whether all objects should be automatically deleted when the bucket is removed from the stack or when the stack is deleted. Requires the ``removalPolicy`` to be set to ``RemovalPolicy.DESTROY``. **Warning** if you have deployed a bucket with ``autoDeleteObjects: true``, switching this to ``false`` in a CDK version *before* ``1.126.0`` will lead to all objects in the bucket being deleted. Be sure to update your bucket resources by deploying with CDK version ``1.126.0`` or later **before** switching this value to ``false``. Setting ``autoDeleteObjects`` to true on a bucket will add ``s3:PutBucketPolicy`` to the bucket policy. This is because during bucket deletion, the custom resource provider needs to update the bucket policy by adding a deny policy for ``s3:PutObject`` to prevent race conditions with external bucket writers. Default: false
        :param block_public_access: The block public access configuration of this bucket. Default: - CloudFormation defaults will apply. New buckets and objects don't allow public access, but users can modify bucket policies or object permissions to allow public access
        :param bucket_key_enabled: Whether Amazon S3 should use its own intermediary key to generate data keys. Only relevant when using KMS for encryption. - If not enabled, every object GET and PUT will cause an API call to KMS (with the attendant cost implications of that). - If enabled, S3 will use its own time-limited key instead. Only relevant, when Encryption is not set to ``BucketEncryption.UNENCRYPTED``. Default: - false
        :param bucket_name: Physical name of this bucket. Default: - Assigned by CloudFormation (recommended).
        :param cors: The CORS configuration of this bucket. Default: - No CORS configuration.
        :param encryption: The kind of server-side encryption to apply to this bucket. If you choose KMS, you can specify a KMS key via ``encryptionKey``. If encryption key is not specified, a key will automatically be created. Default: - ``KMS`` if ``encryptionKey`` is specified, or ``S3_MANAGED`` otherwise.
        :param encryption_key: External KMS key to use for bucket encryption. The ``encryption`` property must be either not specified or set to ``KMS`` or ``DSSE``. An error will be emitted if ``encryption`` is set to ``UNENCRYPTED`` or ``S3_MANAGED``. Default: - If ``encryption`` is set to ``KMS`` and this property is undefined, a new KMS key will be created and associated with this bucket.
        :param enforce_ssl: Enforces SSL for requests. S3.5 of the AWS Foundational Security Best Practices Regarding S3. Default: false
        :param event_bridge_enabled: Whether this bucket should send notifications to Amazon EventBridge or not. Default: false
        :param intelligent_tiering_configurations: Intelligent Tiering Configurations. Default: No Intelligent Tiiering Configurations.
        :param inventories: The inventory configuration of the bucket. Default: - No inventory configuration
        :param lifecycle_rules: Rules that define how Amazon S3 manages objects during their lifetime. Default: - No lifecycle rules.
        :param metrics: The metrics configuration of this bucket. Default: - No metrics configuration.
        :param minimum_tls_version: Enforces minimum TLS version for requests. Requires ``enforceSSL`` to be enabled. Default: No minimum TLS version is enforced.
        :param notifications_handler_role: The role to be used by the notifications handler. Default: - a new role will be created.
        :param notifications_skip_destination_validation: Skips notification validation of Amazon SQS, Amazon SNS, and Lambda destinations. Default: false
        :param object_lock_default_retention: The default retention mode and rules for S3 Object Lock. Default retention can be configured after a bucket is created if the bucket already has object lock enabled. Enabling object lock for existing buckets is not supported. Default: no default retention period
        :param object_lock_enabled: Enable object lock on the bucket. Enabling object lock for existing buckets is not supported. Object lock must be enabled when the bucket is created. Default: false, unless objectLockDefaultRetention is set (then, true)
        :param object_ownership: The objectOwnership of the bucket. Default: - No ObjectOwnership configuration. By default, Amazon S3 sets Object Ownership to ``Bucket owner enforced``. This means ACLs are disabled and the bucket owner will own every object.
        :param public_read_access: Grants public read access to all objects in the bucket. Similar to calling ``bucket.grantPublicAccess()`` Default: false
        :param removal_policy: Policy to apply when the bucket is removed from this stack. Default: - The bucket will be orphaned.
        :param replication_rules: A container for one or more replication rules. Default: - No replication
        :param server_access_logs_bucket: Destination bucket for the server access logs. Default: - If "serverAccessLogsPrefix" undefined - access logs disabled, otherwise - log to current bucket.
        :param server_access_logs_prefix: Optional log file prefix to use for the bucket's access logs. If defined without "serverAccessLogsBucket", enables access logs to current bucket with this prefix. Default: - No log file prefix
        :param target_object_key_format: Optional key format for log objects. Default: - the default key format is: [DestinationPrefix][YYYY]-[MM]-[DD]-[hh]-[mm]-[ss]-[UniqueString]
        :param transfer_acceleration: Whether this bucket should have transfer acceleration turned on or not. Default: false
        :param transition_default_minimum_object_size: Indicates which default minimum object size behavior is applied to the lifecycle configuration. To customize the minimum object size for any transition you can add a filter that specifies a custom ``objectSizeGreaterThan`` or ``objectSizeLessThan`` for ``lifecycleRules`` property. Custom filters always take precedence over the default transition behavior. Default: - TransitionDefaultMinimumObjectSize.VARIES_BY_STORAGE_CLASS before September 2024, otherwise TransitionDefaultMinimumObjectSize.ALL_STORAGE_CLASSES_128_K.
        :param versioned: Whether this bucket should have versioning turned on or not. Default: false (unless object lock is enabled, then true)
        :param website_error_document: The name of the error document (e.g. "404.html") for the website. ``websiteIndexDocument`` must also be set if this is set. Default: - No error document.
        :param website_index_document: The name of the index document (e.g. "index.html") for the website. Enables static website hosting for this bucket. Default: - No index document.
        :param website_redirect: Specifies the redirect behavior of all requests to a website endpoint of a bucket. If you specify this property, you can't specify "websiteIndexDocument", "websiteErrorDocument" nor , "websiteRoutingRules". Default: - No redirection.
        :param website_routing_rules: Rules that define when a redirect is applied and the redirect behavior. Default: - No redirection rules.
        :param bucket_type: The type of the bucket. Default: SecureBucketType.DEFAULT
        :param is_cloud_front_origin_bucket: (deprecated) If your are using it as the CloudFront origin bucket, set it to true. Default: false
        :param is_pipeline_artifact_bucket: (deprecated) If you are setting a custom Qualifier and using it as the artifact bucket for the CDK pipeline, set it to true. Default: false
        :param log_bucket_type: The type of the bucket.
        :param bucket_object_key_prefix: The prefix of the bucket object key.
        :param lifecycle_storage_class_transition: 
        :param vpc_flow_log: 
        '''
        if isinstance(website_redirect, dict):
            website_redirect = _aws_cdk_aws_s3_ceddda9d.RedirectTarget(**website_redirect)
        if isinstance(lifecycle_storage_class_transition, dict):
            lifecycle_storage_class_transition = LifecycleStorageClassTransition(**lifecycle_storage_class_transition)
        if isinstance(vpc_flow_log, dict):
            vpc_flow_log = VPCFlowLog(**vpc_flow_log)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9aed33a1a2e1b54e7597978ca72b67501e3d4d4e21debd3c1e146df889f7a0ef)
            check_type(argname="argument access_control", value=access_control, expected_type=type_hints["access_control"])
            check_type(argname="argument auto_delete_objects", value=auto_delete_objects, expected_type=type_hints["auto_delete_objects"])
            check_type(argname="argument block_public_access", value=block_public_access, expected_type=type_hints["block_public_access"])
            check_type(argname="argument bucket_key_enabled", value=bucket_key_enabled, expected_type=type_hints["bucket_key_enabled"])
            check_type(argname="argument bucket_name", value=bucket_name, expected_type=type_hints["bucket_name"])
            check_type(argname="argument cors", value=cors, expected_type=type_hints["cors"])
            check_type(argname="argument encryption", value=encryption, expected_type=type_hints["encryption"])
            check_type(argname="argument encryption_key", value=encryption_key, expected_type=type_hints["encryption_key"])
            check_type(argname="argument enforce_ssl", value=enforce_ssl, expected_type=type_hints["enforce_ssl"])
            check_type(argname="argument event_bridge_enabled", value=event_bridge_enabled, expected_type=type_hints["event_bridge_enabled"])
            check_type(argname="argument intelligent_tiering_configurations", value=intelligent_tiering_configurations, expected_type=type_hints["intelligent_tiering_configurations"])
            check_type(argname="argument inventories", value=inventories, expected_type=type_hints["inventories"])
            check_type(argname="argument lifecycle_rules", value=lifecycle_rules, expected_type=type_hints["lifecycle_rules"])
            check_type(argname="argument metrics", value=metrics, expected_type=type_hints["metrics"])
            check_type(argname="argument minimum_tls_version", value=minimum_tls_version, expected_type=type_hints["minimum_tls_version"])
            check_type(argname="argument notifications_handler_role", value=notifications_handler_role, expected_type=type_hints["notifications_handler_role"])
            check_type(argname="argument notifications_skip_destination_validation", value=notifications_skip_destination_validation, expected_type=type_hints["notifications_skip_destination_validation"])
            check_type(argname="argument object_lock_default_retention", value=object_lock_default_retention, expected_type=type_hints["object_lock_default_retention"])
            check_type(argname="argument object_lock_enabled", value=object_lock_enabled, expected_type=type_hints["object_lock_enabled"])
            check_type(argname="argument object_ownership", value=object_ownership, expected_type=type_hints["object_ownership"])
            check_type(argname="argument public_read_access", value=public_read_access, expected_type=type_hints["public_read_access"])
            check_type(argname="argument removal_policy", value=removal_policy, expected_type=type_hints["removal_policy"])
            check_type(argname="argument replication_rules", value=replication_rules, expected_type=type_hints["replication_rules"])
            check_type(argname="argument server_access_logs_bucket", value=server_access_logs_bucket, expected_type=type_hints["server_access_logs_bucket"])
            check_type(argname="argument server_access_logs_prefix", value=server_access_logs_prefix, expected_type=type_hints["server_access_logs_prefix"])
            check_type(argname="argument target_object_key_format", value=target_object_key_format, expected_type=type_hints["target_object_key_format"])
            check_type(argname="argument transfer_acceleration", value=transfer_acceleration, expected_type=type_hints["transfer_acceleration"])
            check_type(argname="argument transition_default_minimum_object_size", value=transition_default_minimum_object_size, expected_type=type_hints["transition_default_minimum_object_size"])
            check_type(argname="argument versioned", value=versioned, expected_type=type_hints["versioned"])
            check_type(argname="argument website_error_document", value=website_error_document, expected_type=type_hints["website_error_document"])
            check_type(argname="argument website_index_document", value=website_index_document, expected_type=type_hints["website_index_document"])
            check_type(argname="argument website_redirect", value=website_redirect, expected_type=type_hints["website_redirect"])
            check_type(argname="argument website_routing_rules", value=website_routing_rules, expected_type=type_hints["website_routing_rules"])
            check_type(argname="argument bucket_type", value=bucket_type, expected_type=type_hints["bucket_type"])
            check_type(argname="argument is_cloud_front_origin_bucket", value=is_cloud_front_origin_bucket, expected_type=type_hints["is_cloud_front_origin_bucket"])
            check_type(argname="argument is_pipeline_artifact_bucket", value=is_pipeline_artifact_bucket, expected_type=type_hints["is_pipeline_artifact_bucket"])
            check_type(argname="argument log_bucket_type", value=log_bucket_type, expected_type=type_hints["log_bucket_type"])
            check_type(argname="argument bucket_object_key_prefix", value=bucket_object_key_prefix, expected_type=type_hints["bucket_object_key_prefix"])
            check_type(argname="argument lifecycle_storage_class_transition", value=lifecycle_storage_class_transition, expected_type=type_hints["lifecycle_storage_class_transition"])
            check_type(argname="argument vpc_flow_log", value=vpc_flow_log, expected_type=type_hints["vpc_flow_log"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "log_bucket_type": log_bucket_type,
        }
        if access_control is not None:
            self._values["access_control"] = access_control
        if auto_delete_objects is not None:
            self._values["auto_delete_objects"] = auto_delete_objects
        if block_public_access is not None:
            self._values["block_public_access"] = block_public_access
        if bucket_key_enabled is not None:
            self._values["bucket_key_enabled"] = bucket_key_enabled
        if bucket_name is not None:
            self._values["bucket_name"] = bucket_name
        if cors is not None:
            self._values["cors"] = cors
        if encryption is not None:
            self._values["encryption"] = encryption
        if encryption_key is not None:
            self._values["encryption_key"] = encryption_key
        if enforce_ssl is not None:
            self._values["enforce_ssl"] = enforce_ssl
        if event_bridge_enabled is not None:
            self._values["event_bridge_enabled"] = event_bridge_enabled
        if intelligent_tiering_configurations is not None:
            self._values["intelligent_tiering_configurations"] = intelligent_tiering_configurations
        if inventories is not None:
            self._values["inventories"] = inventories
        if lifecycle_rules is not None:
            self._values["lifecycle_rules"] = lifecycle_rules
        if metrics is not None:
            self._values["metrics"] = metrics
        if minimum_tls_version is not None:
            self._values["minimum_tls_version"] = minimum_tls_version
        if notifications_handler_role is not None:
            self._values["notifications_handler_role"] = notifications_handler_role
        if notifications_skip_destination_validation is not None:
            self._values["notifications_skip_destination_validation"] = notifications_skip_destination_validation
        if object_lock_default_retention is not None:
            self._values["object_lock_default_retention"] = object_lock_default_retention
        if object_lock_enabled is not None:
            self._values["object_lock_enabled"] = object_lock_enabled
        if object_ownership is not None:
            self._values["object_ownership"] = object_ownership
        if public_read_access is not None:
            self._values["public_read_access"] = public_read_access
        if removal_policy is not None:
            self._values["removal_policy"] = removal_policy
        if replication_rules is not None:
            self._values["replication_rules"] = replication_rules
        if server_access_logs_bucket is not None:
            self._values["server_access_logs_bucket"] = server_access_logs_bucket
        if server_access_logs_prefix is not None:
            self._values["server_access_logs_prefix"] = server_access_logs_prefix
        if target_object_key_format is not None:
            self._values["target_object_key_format"] = target_object_key_format
        if transfer_acceleration is not None:
            self._values["transfer_acceleration"] = transfer_acceleration
        if transition_default_minimum_object_size is not None:
            self._values["transition_default_minimum_object_size"] = transition_default_minimum_object_size
        if versioned is not None:
            self._values["versioned"] = versioned
        if website_error_document is not None:
            self._values["website_error_document"] = website_error_document
        if website_index_document is not None:
            self._values["website_index_document"] = website_index_document
        if website_redirect is not None:
            self._values["website_redirect"] = website_redirect
        if website_routing_rules is not None:
            self._values["website_routing_rules"] = website_routing_rules
        if bucket_type is not None:
            self._values["bucket_type"] = bucket_type
        if is_cloud_front_origin_bucket is not None:
            self._values["is_cloud_front_origin_bucket"] = is_cloud_front_origin_bucket
        if is_pipeline_artifact_bucket is not None:
            self._values["is_pipeline_artifact_bucket"] = is_pipeline_artifact_bucket
        if bucket_object_key_prefix is not None:
            self._values["bucket_object_key_prefix"] = bucket_object_key_prefix
        if lifecycle_storage_class_transition is not None:
            self._values["lifecycle_storage_class_transition"] = lifecycle_storage_class_transition
        if vpc_flow_log is not None:
            self._values["vpc_flow_log"] = vpc_flow_log

    @builtins.property
    def access_control(
        self,
    ) -> typing.Optional[_aws_cdk_aws_s3_ceddda9d.BucketAccessControl]:
        '''Specifies a canned ACL that grants predefined permissions to the bucket.

        :default: BucketAccessControl.PRIVATE
        '''
        result = self._values.get("access_control")
        return typing.cast(typing.Optional[_aws_cdk_aws_s3_ceddda9d.BucketAccessControl], result)

    @builtins.property
    def auto_delete_objects(self) -> typing.Optional[builtins.bool]:
        '''Whether all objects should be automatically deleted when the bucket is removed from the stack or when the stack is deleted.

        Requires the ``removalPolicy`` to be set to ``RemovalPolicy.DESTROY``.

        **Warning** if you have deployed a bucket with ``autoDeleteObjects: true``,
        switching this to ``false`` in a CDK version *before* ``1.126.0`` will lead to
        all objects in the bucket being deleted. Be sure to update your bucket resources
        by deploying with CDK version ``1.126.0`` or later **before** switching this value to ``false``.

        Setting ``autoDeleteObjects`` to true on a bucket will add ``s3:PutBucketPolicy`` to the
        bucket policy. This is because during bucket deletion, the custom resource provider
        needs to update the bucket policy by adding a deny policy for ``s3:PutObject`` to
        prevent race conditions with external bucket writers.

        :default: false
        '''
        result = self._values.get("auto_delete_objects")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def block_public_access(
        self,
    ) -> typing.Optional[_aws_cdk_aws_s3_ceddda9d.BlockPublicAccess]:
        '''The block public access configuration of this bucket.

        :default: - CloudFormation defaults will apply. New buckets and objects don't allow public access, but users can modify bucket policies or object permissions to allow public access

        :see: https://docs.aws.amazon.com/AmazonS3/latest/dev/access-control-block-public-access.html
        '''
        result = self._values.get("block_public_access")
        return typing.cast(typing.Optional[_aws_cdk_aws_s3_ceddda9d.BlockPublicAccess], result)

    @builtins.property
    def bucket_key_enabled(self) -> typing.Optional[builtins.bool]:
        '''Whether Amazon S3 should use its own intermediary key to generate data keys.

        Only relevant when using KMS for encryption.

        - If not enabled, every object GET and PUT will cause an API call to KMS (with the
          attendant cost implications of that).
        - If enabled, S3 will use its own time-limited key instead.

        Only relevant, when Encryption is not set to ``BucketEncryption.UNENCRYPTED``.

        :default: - false
        '''
        result = self._values.get("bucket_key_enabled")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def bucket_name(self) -> typing.Optional[builtins.str]:
        '''Physical name of this bucket.

        :default: - Assigned by CloudFormation (recommended).
        '''
        result = self._values.get("bucket_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def cors(self) -> typing.Optional[typing.List[_aws_cdk_aws_s3_ceddda9d.CorsRule]]:
        '''The CORS configuration of this bucket.

        :default: - No CORS configuration.

        :see: https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-s3-bucket-cors.html
        '''
        result = self._values.get("cors")
        return typing.cast(typing.Optional[typing.List[_aws_cdk_aws_s3_ceddda9d.CorsRule]], result)

    @builtins.property
    def encryption(self) -> typing.Optional[_aws_cdk_aws_s3_ceddda9d.BucketEncryption]:
        '''The kind of server-side encryption to apply to this bucket.

        If you choose KMS, you can specify a KMS key via ``encryptionKey``. If
        encryption key is not specified, a key will automatically be created.

        :default: - ``KMS`` if ``encryptionKey`` is specified, or ``S3_MANAGED`` otherwise.
        '''
        result = self._values.get("encryption")
        return typing.cast(typing.Optional[_aws_cdk_aws_s3_ceddda9d.BucketEncryption], result)

    @builtins.property
    def encryption_key(self) -> typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey]:
        '''External KMS key to use for bucket encryption.

        The ``encryption`` property must be either not specified or set to ``KMS`` or ``DSSE``.
        An error will be emitted if ``encryption`` is set to ``UNENCRYPTED`` or ``S3_MANAGED``.

        :default:

        - If ``encryption`` is set to ``KMS`` and this property is undefined,
        a new KMS key will be created and associated with this bucket.
        '''
        result = self._values.get("encryption_key")
        return typing.cast(typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey], result)

    @builtins.property
    def enforce_ssl(self) -> typing.Optional[builtins.bool]:
        '''Enforces SSL for requests.

        S3.5 of the AWS Foundational Security Best Practices Regarding S3.

        :default: false

        :see: https://docs.aws.amazon.com/config/latest/developerguide/s3-bucket-ssl-requests-only.html
        '''
        result = self._values.get("enforce_ssl")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def event_bridge_enabled(self) -> typing.Optional[builtins.bool]:
        '''Whether this bucket should send notifications to Amazon EventBridge or not.

        :default: false
        '''
        result = self._values.get("event_bridge_enabled")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def intelligent_tiering_configurations(
        self,
    ) -> typing.Optional[typing.List[_aws_cdk_aws_s3_ceddda9d.IntelligentTieringConfiguration]]:
        '''Intelligent Tiering Configurations.

        :default: No Intelligent Tiiering Configurations.

        :see: https://docs.aws.amazon.com/AmazonS3/latest/userguide/intelligent-tiering.html
        '''
        result = self._values.get("intelligent_tiering_configurations")
        return typing.cast(typing.Optional[typing.List[_aws_cdk_aws_s3_ceddda9d.IntelligentTieringConfiguration]], result)

    @builtins.property
    def inventories(
        self,
    ) -> typing.Optional[typing.List[_aws_cdk_aws_s3_ceddda9d.Inventory]]:
        '''The inventory configuration of the bucket.

        :default: - No inventory configuration

        :see: https://docs.aws.amazon.com/AmazonS3/latest/dev/storage-inventory.html
        '''
        result = self._values.get("inventories")
        return typing.cast(typing.Optional[typing.List[_aws_cdk_aws_s3_ceddda9d.Inventory]], result)

    @builtins.property
    def lifecycle_rules(
        self,
    ) -> typing.Optional[typing.List[_aws_cdk_aws_s3_ceddda9d.LifecycleRule]]:
        '''Rules that define how Amazon S3 manages objects during their lifetime.

        :default: - No lifecycle rules.
        '''
        result = self._values.get("lifecycle_rules")
        return typing.cast(typing.Optional[typing.List[_aws_cdk_aws_s3_ceddda9d.LifecycleRule]], result)

    @builtins.property
    def metrics(
        self,
    ) -> typing.Optional[typing.List[_aws_cdk_aws_s3_ceddda9d.BucketMetrics]]:
        '''The metrics configuration of this bucket.

        :default: - No metrics configuration.

        :see: https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-s3-bucket-metricsconfiguration.html
        '''
        result = self._values.get("metrics")
        return typing.cast(typing.Optional[typing.List[_aws_cdk_aws_s3_ceddda9d.BucketMetrics]], result)

    @builtins.property
    def minimum_tls_version(self) -> typing.Optional[jsii.Number]:
        '''Enforces minimum TLS version for requests.

        Requires ``enforceSSL`` to be enabled.

        :default: No minimum TLS version is enforced.

        :see: https://docs.aws.amazon.com/AmazonS3/latest/userguide/amazon-s3-policy-keys.html#example-object-tls-version
        '''
        result = self._values.get("minimum_tls_version")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def notifications_handler_role(
        self,
    ) -> typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole]:
        '''The role to be used by the notifications handler.

        :default: - a new role will be created.
        '''
        result = self._values.get("notifications_handler_role")
        return typing.cast(typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole], result)

    @builtins.property
    def notifications_skip_destination_validation(
        self,
    ) -> typing.Optional[builtins.bool]:
        '''Skips notification validation of Amazon SQS, Amazon SNS, and Lambda destinations.

        :default: false
        '''
        result = self._values.get("notifications_skip_destination_validation")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def object_lock_default_retention(
        self,
    ) -> typing.Optional[_aws_cdk_aws_s3_ceddda9d.ObjectLockRetention]:
        '''The default retention mode and rules for S3 Object Lock.

        Default retention can be configured after a bucket is created if the bucket already
        has object lock enabled. Enabling object lock for existing buckets is not supported.

        :default: no default retention period

        :see: https://docs.aws.amazon.com/AmazonS3/latest/userguide/object-lock-overview.html#object-lock-bucket-config-enable
        '''
        result = self._values.get("object_lock_default_retention")
        return typing.cast(typing.Optional[_aws_cdk_aws_s3_ceddda9d.ObjectLockRetention], result)

    @builtins.property
    def object_lock_enabled(self) -> typing.Optional[builtins.bool]:
        '''Enable object lock on the bucket.

        Enabling object lock for existing buckets is not supported. Object lock must be
        enabled when the bucket is created.

        :default: false, unless objectLockDefaultRetention is set (then, true)

        :see: https://docs.aws.amazon.com/AmazonS3/latest/userguide/object-lock-overview.html#object-lock-bucket-config-enable
        '''
        result = self._values.get("object_lock_enabled")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def object_ownership(
        self,
    ) -> typing.Optional[_aws_cdk_aws_s3_ceddda9d.ObjectOwnership]:
        '''The objectOwnership of the bucket.

        :default:

        - No ObjectOwnership configuration. By default, Amazon S3 sets Object Ownership to ``Bucket owner enforced``.
        This means ACLs are disabled and the bucket owner will own every object.

        :see: https://docs.aws.amazon.com/AmazonS3/latest/dev/about-object-ownership.html
        '''
        result = self._values.get("object_ownership")
        return typing.cast(typing.Optional[_aws_cdk_aws_s3_ceddda9d.ObjectOwnership], result)

    @builtins.property
    def public_read_access(self) -> typing.Optional[builtins.bool]:
        '''Grants public read access to all objects in the bucket.

        Similar to calling ``bucket.grantPublicAccess()``

        :default: false
        '''
        result = self._values.get("public_read_access")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def removal_policy(self) -> typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy]:
        '''Policy to apply when the bucket is removed from this stack.

        :default: - The bucket will be orphaned.
        '''
        result = self._values.get("removal_policy")
        return typing.cast(typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy], result)

    @builtins.property
    def replication_rules(
        self,
    ) -> typing.Optional[typing.List[_aws_cdk_aws_s3_ceddda9d.ReplicationRule]]:
        '''A container for one or more replication rules.

        :default: - No replication
        '''
        result = self._values.get("replication_rules")
        return typing.cast(typing.Optional[typing.List[_aws_cdk_aws_s3_ceddda9d.ReplicationRule]], result)

    @builtins.property
    def server_access_logs_bucket(
        self,
    ) -> typing.Optional[_aws_cdk_aws_s3_ceddda9d.IBucket]:
        '''Destination bucket for the server access logs.

        :default: - If "serverAccessLogsPrefix" undefined - access logs disabled, otherwise - log to current bucket.
        '''
        result = self._values.get("server_access_logs_bucket")
        return typing.cast(typing.Optional[_aws_cdk_aws_s3_ceddda9d.IBucket], result)

    @builtins.property
    def server_access_logs_prefix(self) -> typing.Optional[builtins.str]:
        '''Optional log file prefix to use for the bucket's access logs.

        If defined without "serverAccessLogsBucket", enables access logs to current bucket with this prefix.

        :default: - No log file prefix
        '''
        result = self._values.get("server_access_logs_prefix")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def target_object_key_format(
        self,
    ) -> typing.Optional[_aws_cdk_aws_s3_ceddda9d.TargetObjectKeyFormat]:
        '''Optional key format for log objects.

        :default: - the default key format is: [DestinationPrefix][YYYY]-[MM]-[DD]-[hh]-[mm]-[ss]-[UniqueString]
        '''
        result = self._values.get("target_object_key_format")
        return typing.cast(typing.Optional[_aws_cdk_aws_s3_ceddda9d.TargetObjectKeyFormat], result)

    @builtins.property
    def transfer_acceleration(self) -> typing.Optional[builtins.bool]:
        '''Whether this bucket should have transfer acceleration turned on or not.

        :default: false
        '''
        result = self._values.get("transfer_acceleration")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def transition_default_minimum_object_size(
        self,
    ) -> typing.Optional[_aws_cdk_aws_s3_ceddda9d.TransitionDefaultMinimumObjectSize]:
        '''Indicates which default minimum object size behavior is applied to the lifecycle configuration.

        To customize the minimum object size for any transition you can add a filter that specifies a custom
        ``objectSizeGreaterThan`` or ``objectSizeLessThan`` for ``lifecycleRules`` property. Custom filters always
        take precedence over the default transition behavior.

        :default:

        - TransitionDefaultMinimumObjectSize.VARIES_BY_STORAGE_CLASS before September 2024,
        otherwise TransitionDefaultMinimumObjectSize.ALL_STORAGE_CLASSES_128_K.
        '''
        result = self._values.get("transition_default_minimum_object_size")
        return typing.cast(typing.Optional[_aws_cdk_aws_s3_ceddda9d.TransitionDefaultMinimumObjectSize], result)

    @builtins.property
    def versioned(self) -> typing.Optional[builtins.bool]:
        '''Whether this bucket should have versioning turned on or not.

        :default: false (unless object lock is enabled, then true)
        '''
        result = self._values.get("versioned")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def website_error_document(self) -> typing.Optional[builtins.str]:
        '''The name of the error document (e.g. "404.html") for the website. ``websiteIndexDocument`` must also be set if this is set.

        :default: - No error document.
        '''
        result = self._values.get("website_error_document")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def website_index_document(self) -> typing.Optional[builtins.str]:
        '''The name of the index document (e.g. "index.html") for the website. Enables static website hosting for this bucket.

        :default: - No index document.
        '''
        result = self._values.get("website_index_document")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def website_redirect(
        self,
    ) -> typing.Optional[_aws_cdk_aws_s3_ceddda9d.RedirectTarget]:
        '''Specifies the redirect behavior of all requests to a website endpoint of a bucket.

        If you specify this property, you can't specify "websiteIndexDocument", "websiteErrorDocument" nor , "websiteRoutingRules".

        :default: - No redirection.
        '''
        result = self._values.get("website_redirect")
        return typing.cast(typing.Optional[_aws_cdk_aws_s3_ceddda9d.RedirectTarget], result)

    @builtins.property
    def website_routing_rules(
        self,
    ) -> typing.Optional[typing.List[_aws_cdk_aws_s3_ceddda9d.RoutingRule]]:
        '''Rules that define when a redirect is applied and the redirect behavior.

        :default: - No redirection rules.
        '''
        result = self._values.get("website_routing_rules")
        return typing.cast(typing.Optional[typing.List[_aws_cdk_aws_s3_ceddda9d.RoutingRule]], result)

    @builtins.property
    def bucket_type(
        self,
    ) -> typing.Optional[_gammarers_aws_secure_bucket_0aa7e232.SecureBucketType]:
        '''The type of the bucket.

        :default: SecureBucketType.DEFAULT
        '''
        result = self._values.get("bucket_type")
        return typing.cast(typing.Optional[_gammarers_aws_secure_bucket_0aa7e232.SecureBucketType], result)

    @builtins.property
    def is_cloud_front_origin_bucket(self) -> typing.Optional[builtins.bool]:
        '''(deprecated) If your are using it as the CloudFront origin bucket, set it to true.

        :default: false

        :deprecated: This property is deprecated. Use the bucketType property instead.

        :stability: deprecated
        '''
        result = self._values.get("is_cloud_front_origin_bucket")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def is_pipeline_artifact_bucket(self) -> typing.Optional[builtins.bool]:
        '''(deprecated) If you are setting a custom Qualifier and using it as the artifact bucket for the CDK pipeline, set it to true.

        :default: false

        :deprecated: This property is deprecated. Use the bucketType property instead.

        :stability: deprecated
        '''
        result = self._values.get("is_pipeline_artifact_bucket")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def log_bucket_type(self) -> SecureLogBucketType:
        '''The type of the bucket.'''
        result = self._values.get("log_bucket_type")
        assert result is not None, "Required property 'log_bucket_type' is missing"
        return typing.cast(SecureLogBucketType, result)

    @builtins.property
    def bucket_object_key_prefix(self) -> typing.Optional[typing.List[builtins.str]]:
        '''The prefix of the bucket object key.'''
        result = self._values.get("bucket_object_key_prefix")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def lifecycle_storage_class_transition(
        self,
    ) -> typing.Optional[LifecycleStorageClassTransition]:
        result = self._values.get("lifecycle_storage_class_transition")
        return typing.cast(typing.Optional[LifecycleStorageClassTransition], result)

    @builtins.property
    def vpc_flow_log(self) -> typing.Optional["VPCFlowLog"]:
        '''
        :deprecated: This property is deprecated. Use the bucketType property instead.

        :stability: deprecated
        '''
        result = self._values.get("vpc_flow_log")
        return typing.cast(typing.Optional["VPCFlowLog"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "SecureVpcFlowLogBucketProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@gammarers/aws-secure-log-bucket.TransitionStep",
    jsii_struct_bases=[],
    name_mapping={"days": "days", "enabled": "enabled"},
)
class TransitionStep:
    def __init__(
        self,
        *,
        days: typing.Optional[jsii.Number] = None,
        enabled: typing.Optional[builtins.bool] = None,
    ) -> None:
        '''
        :param days: 
        :param enabled: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5a702dd63e304d15c23da1ad797c12f793ea2238260cc60e3de73c794b178e3c)
            check_type(argname="argument days", value=days, expected_type=type_hints["days"])
            check_type(argname="argument enabled", value=enabled, expected_type=type_hints["enabled"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if days is not None:
            self._values["days"] = days
        if enabled is not None:
            self._values["enabled"] = enabled

    @builtins.property
    def days(self) -> typing.Optional[jsii.Number]:
        result = self._values.get("days")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def enabled(self) -> typing.Optional[builtins.bool]:
        result = self._values.get("enabled")
        return typing.cast(typing.Optional[builtins.bool], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "TransitionStep(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@gammarers/aws-secure-log-bucket.VPCFlowLog",
    jsii_struct_bases=[],
    name_mapping={
        "bucket_object_key_prefix": "bucketObjectKeyPrefix",
        "enable": "enable",
    },
)
class VPCFlowLog:
    def __init__(
        self,
        *,
        bucket_object_key_prefix: typing.Optional[typing.Sequence[builtins.str]] = None,
        enable: typing.Optional[builtins.bool] = None,
    ) -> None:
        '''
        :param bucket_object_key_prefix: 
        :param enable: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8eeb09671264c572c1387bdf62e8c460e0b9212f7ad7f76dec28f30788e2e1cc)
            check_type(argname="argument bucket_object_key_prefix", value=bucket_object_key_prefix, expected_type=type_hints["bucket_object_key_prefix"])
            check_type(argname="argument enable", value=enable, expected_type=type_hints["enable"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if bucket_object_key_prefix is not None:
            self._values["bucket_object_key_prefix"] = bucket_object_key_prefix
        if enable is not None:
            self._values["enable"] = enable

    @builtins.property
    def bucket_object_key_prefix(self) -> typing.Optional[typing.List[builtins.str]]:
        result = self._values.get("bucket_object_key_prefix")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def enable(self) -> typing.Optional[builtins.bool]:
        result = self._values.get("enable")
        return typing.cast(typing.Optional[builtins.bool], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "VPCFlowLog(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "LifecycleStorageClassTransition",
    "SecureLogBucket",
    "SecureLogBucketType",
    "SecureNormalLogBucketProps",
    "SecureVpcFlowLogBucketProps",
    "TransitionStep",
    "VPCFlowLog",
]

publication.publish()

def _typecheckingstub__398cdc8180a48893a387e0c7a96e9f07d78c1a6e3628db3d88eacb7e76407eef(
    *,
    transition_step_deep_archive: typing.Optional[typing.Union[TransitionStep, typing.Dict[builtins.str, typing.Any]]] = None,
    transition_step_glacier: typing.Optional[typing.Union[TransitionStep, typing.Dict[builtins.str, typing.Any]]] = None,
    transition_step_infrequent_access: typing.Optional[typing.Union[TransitionStep, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__631e2fc5db951a1d650e81f02732903146ef035c7350dab2c626b18ea9b5b593(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    props: typing.Optional[typing.Union[typing.Union[SecureNormalLogBucketProps, typing.Dict[builtins.str, typing.Any]], typing.Union[SecureVpcFlowLogBucketProps, typing.Dict[builtins.str, typing.Any]]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c95a530793a173bfc4ba531e27cd2e424336eac2091debbb3ab7cd15dfa79018(
    *,
    access_control: typing.Optional[_aws_cdk_aws_s3_ceddda9d.BucketAccessControl] = None,
    auto_delete_objects: typing.Optional[builtins.bool] = None,
    block_public_access: typing.Optional[_aws_cdk_aws_s3_ceddda9d.BlockPublicAccess] = None,
    bucket_key_enabled: typing.Optional[builtins.bool] = None,
    bucket_name: typing.Optional[builtins.str] = None,
    cors: typing.Optional[typing.Sequence[typing.Union[_aws_cdk_aws_s3_ceddda9d.CorsRule, typing.Dict[builtins.str, typing.Any]]]] = None,
    encryption: typing.Optional[_aws_cdk_aws_s3_ceddda9d.BucketEncryption] = None,
    encryption_key: typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey] = None,
    enforce_ssl: typing.Optional[builtins.bool] = None,
    event_bridge_enabled: typing.Optional[builtins.bool] = None,
    intelligent_tiering_configurations: typing.Optional[typing.Sequence[typing.Union[_aws_cdk_aws_s3_ceddda9d.IntelligentTieringConfiguration, typing.Dict[builtins.str, typing.Any]]]] = None,
    inventories: typing.Optional[typing.Sequence[typing.Union[_aws_cdk_aws_s3_ceddda9d.Inventory, typing.Dict[builtins.str, typing.Any]]]] = None,
    lifecycle_rules: typing.Optional[typing.Sequence[typing.Union[_aws_cdk_aws_s3_ceddda9d.LifecycleRule, typing.Dict[builtins.str, typing.Any]]]] = None,
    metrics: typing.Optional[typing.Sequence[typing.Union[_aws_cdk_aws_s3_ceddda9d.BucketMetrics, typing.Dict[builtins.str, typing.Any]]]] = None,
    minimum_tls_version: typing.Optional[jsii.Number] = None,
    notifications_handler_role: typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole] = None,
    notifications_skip_destination_validation: typing.Optional[builtins.bool] = None,
    object_lock_default_retention: typing.Optional[_aws_cdk_aws_s3_ceddda9d.ObjectLockRetention] = None,
    object_lock_enabled: typing.Optional[builtins.bool] = None,
    object_ownership: typing.Optional[_aws_cdk_aws_s3_ceddda9d.ObjectOwnership] = None,
    public_read_access: typing.Optional[builtins.bool] = None,
    removal_policy: typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy] = None,
    replication_rules: typing.Optional[typing.Sequence[typing.Union[_aws_cdk_aws_s3_ceddda9d.ReplicationRule, typing.Dict[builtins.str, typing.Any]]]] = None,
    server_access_logs_bucket: typing.Optional[_aws_cdk_aws_s3_ceddda9d.IBucket] = None,
    server_access_logs_prefix: typing.Optional[builtins.str] = None,
    target_object_key_format: typing.Optional[_aws_cdk_aws_s3_ceddda9d.TargetObjectKeyFormat] = None,
    transfer_acceleration: typing.Optional[builtins.bool] = None,
    transition_default_minimum_object_size: typing.Optional[_aws_cdk_aws_s3_ceddda9d.TransitionDefaultMinimumObjectSize] = None,
    versioned: typing.Optional[builtins.bool] = None,
    website_error_document: typing.Optional[builtins.str] = None,
    website_index_document: typing.Optional[builtins.str] = None,
    website_redirect: typing.Optional[typing.Union[_aws_cdk_aws_s3_ceddda9d.RedirectTarget, typing.Dict[builtins.str, typing.Any]]] = None,
    website_routing_rules: typing.Optional[typing.Sequence[typing.Union[_aws_cdk_aws_s3_ceddda9d.RoutingRule, typing.Dict[builtins.str, typing.Any]]]] = None,
    bucket_type: typing.Optional[_gammarers_aws_secure_bucket_0aa7e232.SecureBucketType] = None,
    is_cloud_front_origin_bucket: typing.Optional[builtins.bool] = None,
    is_pipeline_artifact_bucket: typing.Optional[builtins.bool] = None,
    lifecycle_storage_class_transition: typing.Optional[typing.Union[LifecycleStorageClassTransition, typing.Dict[builtins.str, typing.Any]]] = None,
    log_bucket_type: typing.Optional[SecureLogBucketType] = None,
    vpc_flow_log: typing.Optional[typing.Union[VPCFlowLog, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9aed33a1a2e1b54e7597978ca72b67501e3d4d4e21debd3c1e146df889f7a0ef(
    *,
    access_control: typing.Optional[_aws_cdk_aws_s3_ceddda9d.BucketAccessControl] = None,
    auto_delete_objects: typing.Optional[builtins.bool] = None,
    block_public_access: typing.Optional[_aws_cdk_aws_s3_ceddda9d.BlockPublicAccess] = None,
    bucket_key_enabled: typing.Optional[builtins.bool] = None,
    bucket_name: typing.Optional[builtins.str] = None,
    cors: typing.Optional[typing.Sequence[typing.Union[_aws_cdk_aws_s3_ceddda9d.CorsRule, typing.Dict[builtins.str, typing.Any]]]] = None,
    encryption: typing.Optional[_aws_cdk_aws_s3_ceddda9d.BucketEncryption] = None,
    encryption_key: typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey] = None,
    enforce_ssl: typing.Optional[builtins.bool] = None,
    event_bridge_enabled: typing.Optional[builtins.bool] = None,
    intelligent_tiering_configurations: typing.Optional[typing.Sequence[typing.Union[_aws_cdk_aws_s3_ceddda9d.IntelligentTieringConfiguration, typing.Dict[builtins.str, typing.Any]]]] = None,
    inventories: typing.Optional[typing.Sequence[typing.Union[_aws_cdk_aws_s3_ceddda9d.Inventory, typing.Dict[builtins.str, typing.Any]]]] = None,
    lifecycle_rules: typing.Optional[typing.Sequence[typing.Union[_aws_cdk_aws_s3_ceddda9d.LifecycleRule, typing.Dict[builtins.str, typing.Any]]]] = None,
    metrics: typing.Optional[typing.Sequence[typing.Union[_aws_cdk_aws_s3_ceddda9d.BucketMetrics, typing.Dict[builtins.str, typing.Any]]]] = None,
    minimum_tls_version: typing.Optional[jsii.Number] = None,
    notifications_handler_role: typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole] = None,
    notifications_skip_destination_validation: typing.Optional[builtins.bool] = None,
    object_lock_default_retention: typing.Optional[_aws_cdk_aws_s3_ceddda9d.ObjectLockRetention] = None,
    object_lock_enabled: typing.Optional[builtins.bool] = None,
    object_ownership: typing.Optional[_aws_cdk_aws_s3_ceddda9d.ObjectOwnership] = None,
    public_read_access: typing.Optional[builtins.bool] = None,
    removal_policy: typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy] = None,
    replication_rules: typing.Optional[typing.Sequence[typing.Union[_aws_cdk_aws_s3_ceddda9d.ReplicationRule, typing.Dict[builtins.str, typing.Any]]]] = None,
    server_access_logs_bucket: typing.Optional[_aws_cdk_aws_s3_ceddda9d.IBucket] = None,
    server_access_logs_prefix: typing.Optional[builtins.str] = None,
    target_object_key_format: typing.Optional[_aws_cdk_aws_s3_ceddda9d.TargetObjectKeyFormat] = None,
    transfer_acceleration: typing.Optional[builtins.bool] = None,
    transition_default_minimum_object_size: typing.Optional[_aws_cdk_aws_s3_ceddda9d.TransitionDefaultMinimumObjectSize] = None,
    versioned: typing.Optional[builtins.bool] = None,
    website_error_document: typing.Optional[builtins.str] = None,
    website_index_document: typing.Optional[builtins.str] = None,
    website_redirect: typing.Optional[typing.Union[_aws_cdk_aws_s3_ceddda9d.RedirectTarget, typing.Dict[builtins.str, typing.Any]]] = None,
    website_routing_rules: typing.Optional[typing.Sequence[typing.Union[_aws_cdk_aws_s3_ceddda9d.RoutingRule, typing.Dict[builtins.str, typing.Any]]]] = None,
    bucket_type: typing.Optional[_gammarers_aws_secure_bucket_0aa7e232.SecureBucketType] = None,
    is_cloud_front_origin_bucket: typing.Optional[builtins.bool] = None,
    is_pipeline_artifact_bucket: typing.Optional[builtins.bool] = None,
    log_bucket_type: SecureLogBucketType,
    bucket_object_key_prefix: typing.Optional[typing.Sequence[builtins.str]] = None,
    lifecycle_storage_class_transition: typing.Optional[typing.Union[LifecycleStorageClassTransition, typing.Dict[builtins.str, typing.Any]]] = None,
    vpc_flow_log: typing.Optional[typing.Union[VPCFlowLog, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5a702dd63e304d15c23da1ad797c12f793ea2238260cc60e3de73c794b178e3c(
    *,
    days: typing.Optional[jsii.Number] = None,
    enabled: typing.Optional[builtins.bool] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8eeb09671264c572c1387bdf62e8c460e0b9212f7ad7f76dec28f30788e2e1cc(
    *,
    bucket_object_key_prefix: typing.Optional[typing.Sequence[builtins.str]] = None,
    enable: typing.Optional[builtins.bool] = None,
) -> None:
    """Type checking stubs"""
    pass
