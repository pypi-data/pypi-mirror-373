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

from .._jsii import *

import aws_cdk as _aws_cdk_ceddda9d
import aws_cdk.aws_codebuild as _aws_cdk_aws_codebuild_ceddda9d
import aws_cdk.aws_codepipeline as _aws_cdk_aws_codepipeline_ceddda9d
import aws_cdk.aws_ec2 as _aws_cdk_aws_ec2_ceddda9d
import aws_cdk.aws_ecr as _aws_cdk_aws_ecr_ceddda9d
import aws_cdk.aws_ecs as _aws_cdk_aws_ecs_ceddda9d
import aws_cdk.aws_iam as _aws_cdk_aws_iam_ceddda9d
import aws_cdk.aws_lambda as _aws_cdk_aws_lambda_ceddda9d
import aws_cdk.aws_logs as _aws_cdk_aws_logs_ceddda9d
import aws_cdk.aws_s3 as _aws_cdk_aws_s3_ceddda9d
import constructs as _constructs_77d1e7e8


@jsii.implements(_aws_cdk_ceddda9d.IResource)
class BaseDockerProject(
    _constructs_77d1e7e8.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="shady-island.automation.BaseDockerProject",
):
    '''The base for Linux-based Docker build projects.'''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        build_environment: typing.Union[_aws_cdk_aws_codebuild_ceddda9d.BuildEnvironment, typing.Dict[builtins.str, typing.Any]],
        build_spec: _aws_cdk_aws_codebuild_ceddda9d.BuildSpec,
        repository: _aws_cdk_aws_ecr_ceddda9d.IRepository,
        description: typing.Optional[builtins.str] = None,
        log_retention: typing.Optional[_aws_cdk_aws_logs_ceddda9d.RetentionDays] = None,
        removal_policy: typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy] = None,
        security_groups: typing.Optional[typing.Sequence[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup]] = None,
        subnet_selection: typing.Optional[typing.Union[_aws_cdk_aws_ec2_ceddda9d.SubnetSelection, typing.Dict[builtins.str, typing.Any]]] = None,
        vpc: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IVpc] = None,
    ) -> None:
        '''Creates a new BaseDockerProject.

        :param scope: - The scope in which to define this construct.
        :param id: - The scoped construct ID.
        :param build_environment: Build environment to use for the build.
        :param build_spec: Filename or contents of buildspec in JSON format.
        :param repository: The ECR repository where images are pushed.
        :param description: A description of this CodeBuild project.
        :param log_retention: The duration to retain log entries. Default: - RetentionDays.THREE_MONTHS
        :param removal_policy: The removal policy for this project and its logs.
        :param security_groups: Security groups to associate with the project's network interfaces.
        :param subnet_selection: Where to place the network interfaces within the VPC.
        :param vpc: VPC network to place CodeBuild network interfaces.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__eb4cd3f68a28927dc8e96eb24e7b96185808332c2fe8f897afdc5e1ca9946380)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = BaseDockerProjectProps(
            build_environment=build_environment,
            build_spec=build_spec,
            repository=repository,
            description=description,
            log_retention=log_retention,
            removal_policy=removal_policy,
            security_groups=security_groups,
            subnet_selection=subnet_selection,
            vpc=vpc,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @jsii.member(jsii_name="applyRemovalPolicy")
    def apply_removal_policy(self, policy: _aws_cdk_ceddda9d.RemovalPolicy) -> None:
        '''Apply the given removal policy to this resource.

        The Removal Policy controls what happens to this resource when it stops
        being managed by CloudFormation, either because you've removed it from the
        CDK application or because you've made a change that requires the resource
        to be replaced.

        The resource can be deleted (``RemovalPolicy.DESTROY``), or left in your AWS
        account for data recovery and cleanup later (``RemovalPolicy.RETAIN``).

        :param policy: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__cfce4f825ec93fc3471974bb12955f80569f0dfde3d440a3f52ce93d6a2df412)
            check_type(argname="argument policy", value=policy, expected_type=type_hints["policy"])
        return typing.cast(None, jsii.invoke(self, "applyRemovalPolicy", [policy]))

    @builtins.property
    @jsii.member(jsii_name="buildSpec")
    def build_spec(self) -> _aws_cdk_aws_codebuild_ceddda9d.BuildSpec:
        '''The CodeBuild build spec supplied.'''
        return typing.cast(_aws_cdk_aws_codebuild_ceddda9d.BuildSpec, jsii.get(self, "buildSpec"))

    @builtins.property
    @jsii.member(jsii_name="env")
    def env(self) -> _aws_cdk_ceddda9d.ResourceEnvironment:
        '''The environment this resource belongs to.

        For resources that are created and managed by the CDK
        (generally, those created by creating new class instances like Role, Bucket, etc.),
        this is always the same as the environment of the stack they belong to;
        however, for imported resources
        (those obtained from static methods like fromRoleArn, fromBucketName, etc.),
        that might be different than the stack they were imported into.
        '''
        return typing.cast(_aws_cdk_ceddda9d.ResourceEnvironment, jsii.get(self, "env"))

    @builtins.property
    @jsii.member(jsii_name="logGroup")
    def log_group(self) -> _aws_cdk_aws_logs_ceddda9d.LogGroup:
        '''The log group.'''
        return typing.cast(_aws_cdk_aws_logs_ceddda9d.LogGroup, jsii.get(self, "logGroup"))

    @builtins.property
    @jsii.member(jsii_name="project")
    def project(self) -> _aws_cdk_aws_codebuild_ceddda9d.PipelineProject:
        '''The CodeBuild project.'''
        return typing.cast(_aws_cdk_aws_codebuild_ceddda9d.PipelineProject, jsii.get(self, "project"))

    @builtins.property
    @jsii.member(jsii_name="stack")
    def stack(self) -> _aws_cdk_ceddda9d.Stack:
        '''The stack in which this resource is defined.'''
        return typing.cast(_aws_cdk_ceddda9d.Stack, jsii.get(self, "stack"))


@jsii.data_type(
    jsii_type="shady-island.automation.CommonDockerProps",
    jsii_struct_bases=[],
    name_mapping={
        "repository": "repository",
        "description": "description",
        "log_retention": "logRetention",
        "removal_policy": "removalPolicy",
        "security_groups": "securityGroups",
        "subnet_selection": "subnetSelection",
        "vpc": "vpc",
    },
)
class CommonDockerProps:
    def __init__(
        self,
        *,
        repository: _aws_cdk_aws_ecr_ceddda9d.IRepository,
        description: typing.Optional[builtins.str] = None,
        log_retention: typing.Optional[_aws_cdk_aws_logs_ceddda9d.RetentionDays] = None,
        removal_policy: typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy] = None,
        security_groups: typing.Optional[typing.Sequence[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup]] = None,
        subnet_selection: typing.Optional[typing.Union[_aws_cdk_aws_ec2_ceddda9d.SubnetSelection, typing.Dict[builtins.str, typing.Any]]] = None,
        vpc: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IVpc] = None,
    ) -> None:
        '''Common Docker build properties.

        :param repository: The ECR repository where images are pushed.
        :param description: A description of this CodeBuild project.
        :param log_retention: The duration to retain log entries. Default: - RetentionDays.THREE_MONTHS
        :param removal_policy: The removal policy for this project and its logs.
        :param security_groups: Security groups to associate with the project's network interfaces.
        :param subnet_selection: Where to place the network interfaces within the VPC.
        :param vpc: VPC network to place CodeBuild network interfaces.
        '''
        if isinstance(subnet_selection, dict):
            subnet_selection = _aws_cdk_aws_ec2_ceddda9d.SubnetSelection(**subnet_selection)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4f0a6c70505e3cc3734a6cdc646578bbc44f54a8e031c316e0293b2c9f1dfdd5)
            check_type(argname="argument repository", value=repository, expected_type=type_hints["repository"])
            check_type(argname="argument description", value=description, expected_type=type_hints["description"])
            check_type(argname="argument log_retention", value=log_retention, expected_type=type_hints["log_retention"])
            check_type(argname="argument removal_policy", value=removal_policy, expected_type=type_hints["removal_policy"])
            check_type(argname="argument security_groups", value=security_groups, expected_type=type_hints["security_groups"])
            check_type(argname="argument subnet_selection", value=subnet_selection, expected_type=type_hints["subnet_selection"])
            check_type(argname="argument vpc", value=vpc, expected_type=type_hints["vpc"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "repository": repository,
        }
        if description is not None:
            self._values["description"] = description
        if log_retention is not None:
            self._values["log_retention"] = log_retention
        if removal_policy is not None:
            self._values["removal_policy"] = removal_policy
        if security_groups is not None:
            self._values["security_groups"] = security_groups
        if subnet_selection is not None:
            self._values["subnet_selection"] = subnet_selection
        if vpc is not None:
            self._values["vpc"] = vpc

    @builtins.property
    def repository(self) -> _aws_cdk_aws_ecr_ceddda9d.IRepository:
        '''The ECR repository where images are pushed.'''
        result = self._values.get("repository")
        assert result is not None, "Required property 'repository' is missing"
        return typing.cast(_aws_cdk_aws_ecr_ceddda9d.IRepository, result)

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        '''A description of this CodeBuild project.'''
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def log_retention(
        self,
    ) -> typing.Optional[_aws_cdk_aws_logs_ceddda9d.RetentionDays]:
        '''The duration to retain log entries.

        :default: - RetentionDays.THREE_MONTHS
        '''
        result = self._values.get("log_retention")
        return typing.cast(typing.Optional[_aws_cdk_aws_logs_ceddda9d.RetentionDays], result)

    @builtins.property
    def removal_policy(self) -> typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy]:
        '''The removal policy for this project and its logs.'''
        result = self._values.get("removal_policy")
        return typing.cast(typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy], result)

    @builtins.property
    def security_groups(
        self,
    ) -> typing.Optional[typing.List[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup]]:
        '''Security groups to associate with the project's network interfaces.'''
        result = self._values.get("security_groups")
        return typing.cast(typing.Optional[typing.List[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup]], result)

    @builtins.property
    def subnet_selection(
        self,
    ) -> typing.Optional[_aws_cdk_aws_ec2_ceddda9d.SubnetSelection]:
        '''Where to place the network interfaces within the VPC.'''
        result = self._values.get("subnet_selection")
        return typing.cast(typing.Optional[_aws_cdk_aws_ec2_ceddda9d.SubnetSelection], result)

    @builtins.property
    def vpc(self) -> typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IVpc]:
        '''VPC network to place CodeBuild network interfaces.'''
        result = self._values.get("vpc")
        return typing.cast(typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IVpc], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CommonDockerProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ContainerImagePipeline(
    _constructs_77d1e7e8.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="shady-island.automation.ContainerImagePipeline",
):
    '''Allows images pushed to an ECR repo to trigger updates to an ECS service.

    This construct produces a CodePipeline pipeline using the "ECR Source"
    action, an "ECS Deploy" action, and a custom Lambda handler in between that
    transforms the JSON from the "Source" action into the JSON needed for the
    "Deploy" action.
    '''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        container: builtins.str,
        repository: _aws_cdk_aws_ecr_ceddda9d.IRepository,
        service: _aws_cdk_aws_ecs_ceddda9d.IBaseService,
        artifact_bucket: typing.Optional[_aws_cdk_aws_s3_ceddda9d.IBucket] = None,
        pipeline_type: typing.Optional[_aws_cdk_aws_codepipeline_ceddda9d.PipelineType] = None,
        tag: typing.Optional[builtins.str] = None,
    ) -> None:
        '''Creates a new ContainerImagePipeline.

        :param scope: - The scope in which to define this construct.
        :param id: - The scoped construct ID.
        :param container: The name of the container in the task definition to update.
        :param repository: The ECR repository where images will be pushed.
        :param service: The ECS service to update when an image is pushed to the ECR repository.
        :param artifact_bucket: A custom bucket for artifacts. Default: - A new bucket will be created
        :param pipeline_type: The pipeline type (V1 or V2). Default: - V1
        :param tag: The container image tag to observe for changes in the ECR repository. Default: - "latest"
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__cedb29f5ea4e41db2040cf196e8fb5c9c4a295ca5a54967d23de3d82284bb5a4)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = ContainerImagePipelineProps(
            container=container,
            repository=repository,
            service=service,
            artifact_bucket=artifact_bucket,
            pipeline_type=pipeline_type,
            tag=tag,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @builtins.property
    @jsii.member(jsii_name="pipeline")
    def pipeline(self) -> _aws_cdk_aws_codepipeline_ceddda9d.Pipeline:
        '''The CodePipeline pipeline.'''
        return typing.cast(_aws_cdk_aws_codepipeline_ceddda9d.Pipeline, jsii.get(self, "pipeline"))


@jsii.data_type(
    jsii_type="shady-island.automation.ContainerImagePipelineProps",
    jsii_struct_bases=[],
    name_mapping={
        "container": "container",
        "repository": "repository",
        "service": "service",
        "artifact_bucket": "artifactBucket",
        "pipeline_type": "pipelineType",
        "tag": "tag",
    },
)
class ContainerImagePipelineProps:
    def __init__(
        self,
        *,
        container: builtins.str,
        repository: _aws_cdk_aws_ecr_ceddda9d.IRepository,
        service: _aws_cdk_aws_ecs_ceddda9d.IBaseService,
        artifact_bucket: typing.Optional[_aws_cdk_aws_s3_ceddda9d.IBucket] = None,
        pipeline_type: typing.Optional[_aws_cdk_aws_codepipeline_ceddda9d.PipelineType] = None,
        tag: typing.Optional[builtins.str] = None,
    ) -> None:
        '''Properties for the ContainerImagePipeline constructor.

        :param container: The name of the container in the task definition to update.
        :param repository: The ECR repository where images will be pushed.
        :param service: The ECS service to update when an image is pushed to the ECR repository.
        :param artifact_bucket: A custom bucket for artifacts. Default: - A new bucket will be created
        :param pipeline_type: The pipeline type (V1 or V2). Default: - V1
        :param tag: The container image tag to observe for changes in the ECR repository. Default: - "latest"
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a82c69c46656ae83e2077c89d799ffb8536b4ddcc17b205a38a2221073be2e48)
            check_type(argname="argument container", value=container, expected_type=type_hints["container"])
            check_type(argname="argument repository", value=repository, expected_type=type_hints["repository"])
            check_type(argname="argument service", value=service, expected_type=type_hints["service"])
            check_type(argname="argument artifact_bucket", value=artifact_bucket, expected_type=type_hints["artifact_bucket"])
            check_type(argname="argument pipeline_type", value=pipeline_type, expected_type=type_hints["pipeline_type"])
            check_type(argname="argument tag", value=tag, expected_type=type_hints["tag"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "container": container,
            "repository": repository,
            "service": service,
        }
        if artifact_bucket is not None:
            self._values["artifact_bucket"] = artifact_bucket
        if pipeline_type is not None:
            self._values["pipeline_type"] = pipeline_type
        if tag is not None:
            self._values["tag"] = tag

    @builtins.property
    def container(self) -> builtins.str:
        '''The name of the container in the task definition to update.'''
        result = self._values.get("container")
        assert result is not None, "Required property 'container' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def repository(self) -> _aws_cdk_aws_ecr_ceddda9d.IRepository:
        '''The ECR repository where images will be pushed.'''
        result = self._values.get("repository")
        assert result is not None, "Required property 'repository' is missing"
        return typing.cast(_aws_cdk_aws_ecr_ceddda9d.IRepository, result)

    @builtins.property
    def service(self) -> _aws_cdk_aws_ecs_ceddda9d.IBaseService:
        '''The ECS service to update when an image is pushed to the ECR repository.'''
        result = self._values.get("service")
        assert result is not None, "Required property 'service' is missing"
        return typing.cast(_aws_cdk_aws_ecs_ceddda9d.IBaseService, result)

    @builtins.property
    def artifact_bucket(self) -> typing.Optional[_aws_cdk_aws_s3_ceddda9d.IBucket]:
        '''A custom bucket for artifacts.

        :default: - A new bucket will be created
        '''
        result = self._values.get("artifact_bucket")
        return typing.cast(typing.Optional[_aws_cdk_aws_s3_ceddda9d.IBucket], result)

    @builtins.property
    def pipeline_type(
        self,
    ) -> typing.Optional[_aws_cdk_aws_codepipeline_ceddda9d.PipelineType]:
        '''The pipeline type (V1 or V2).

        :default: - V1
        '''
        result = self._values.get("pipeline_type")
        return typing.cast(typing.Optional[_aws_cdk_aws_codepipeline_ceddda9d.PipelineType], result)

    @builtins.property
    def tag(self) -> typing.Optional[builtins.str]:
        '''The container image tag to observe for changes in the ECR repository.

        :default: - "latest"
        '''
        result = self._values.get("tag")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ContainerImagePipelineProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class FunctionCodeUpdater(
    _constructs_77d1e7e8.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="shady-island.automation.FunctionCodeUpdater",
):
    '''Automates deployments of Lambda function code.

    In order to guarantee the least amount of privilege to the principal sending
    new code revisions to S3 (e.g. a GitHub Action, a CodeBuild project), you can
    use this construct to call the ``UpdateFunctionCode`` action of the Lambda API
    any time a new revision is added to a bucket (which must support versioning).
    '''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        bucket: _aws_cdk_aws_s3_ceddda9d.IBucket,
        object_key: builtins.str,
        target: _aws_cdk_aws_lambda_ceddda9d.IFunction,
    ) -> None:
        '''Creates a new FunctionCodeUpdater.

        :param scope: - The scope in which to define this construct.
        :param id: - The scoped construct ID.
        :param bucket: The bucket to monitor for changes.
        :param object_key: The object within the bucket to monitor (e.g. my-application/code.zip).
        :param target: The Lambda function to update.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f33a0905023521597d28cee93114601f3e35da34b9eff4df0ee5fd59350ad1e3)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = FunctionCodeUpdaterProps(
            bucket=bucket, object_key=object_key, target=target
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @jsii.member(jsii_name="grantPutCode")
    def grant_put_code(
        self,
        identity: _aws_cdk_aws_iam_ceddda9d.IGrantable,
    ) -> _aws_cdk_aws_iam_ceddda9d.Grant:
        '''Grants ``s3:PutObject*`` and ``s3:AbortObject*`` permissions for the S3 object key of the Lambda function code.

        If encryption is used, permission to use the key to encrypt uploaded files
        will also be granted to the same principal.

        :param identity: - The principal.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8dbf24b39a405557c0b908319842dd0572a414219a6984055ab05854fb4231eb)
            check_type(argname="argument identity", value=identity, expected_type=type_hints["identity"])
        return typing.cast(_aws_cdk_aws_iam_ceddda9d.Grant, jsii.invoke(self, "grantPutCode", [identity]))


@jsii.data_type(
    jsii_type="shady-island.automation.FunctionCodeUpdaterProps",
    jsii_struct_bases=[],
    name_mapping={"bucket": "bucket", "object_key": "objectKey", "target": "target"},
)
class FunctionCodeUpdaterProps:
    def __init__(
        self,
        *,
        bucket: _aws_cdk_aws_s3_ceddda9d.IBucket,
        object_key: builtins.str,
        target: _aws_cdk_aws_lambda_ceddda9d.IFunction,
    ) -> None:
        '''Constructor properties for FunctionCodeUpdater.

        :param bucket: The bucket to monitor for changes.
        :param object_key: The object within the bucket to monitor (e.g. my-application/code.zip).
        :param target: The Lambda function to update.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__19f46ec283cf845783c22e4264d22e7ba242c3d2c1ccb328e80a86024cb13ec3)
            check_type(argname="argument bucket", value=bucket, expected_type=type_hints["bucket"])
            check_type(argname="argument object_key", value=object_key, expected_type=type_hints["object_key"])
            check_type(argname="argument target", value=target, expected_type=type_hints["target"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "bucket": bucket,
            "object_key": object_key,
            "target": target,
        }

    @builtins.property
    def bucket(self) -> _aws_cdk_aws_s3_ceddda9d.IBucket:
        '''The bucket to monitor for changes.'''
        result = self._values.get("bucket")
        assert result is not None, "Required property 'bucket' is missing"
        return typing.cast(_aws_cdk_aws_s3_ceddda9d.IBucket, result)

    @builtins.property
    def object_key(self) -> builtins.str:
        '''The object within the bucket to monitor (e.g. my-application/code.zip).'''
        result = self._values.get("object_key")
        assert result is not None, "Required property 'object_key' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def target(self) -> _aws_cdk_aws_lambda_ceddda9d.IFunction:
        '''The Lambda function to update.'''
        result = self._values.get("target")
        assert result is not None, "Required property 'target' is missing"
        return typing.cast(_aws_cdk_aws_lambda_ceddda9d.IFunction, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "FunctionCodeUpdaterProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class LinuxDockerBuildProject(
    BaseDockerProject,
    metaclass=jsii.JSIIMeta,
    jsii_type="shady-island.automation.LinuxDockerBuildProject",
):
    '''Sets up a standardized Docker build project.

    This project accepts the following optional environment variables:

    - IMAGE_LABELS: JSON-formatted object of container labels and their values.
    - BUILD_ARGS: JSON-formatted object of build arguments and their values.
    - IMAGE_TAG: Optional. The image tag (e.g. Git commit ID) (default: build
      number).
    '''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        build_directory: typing.Optional[builtins.str] = None,
        build_image: typing.Optional[_aws_cdk_aws_codebuild_ceddda9d.IBuildImage] = None,
        compute_type: typing.Optional[_aws_cdk_aws_codebuild_ceddda9d.ComputeType] = None,
        dockerfile: typing.Optional[builtins.str] = None,
        enable_cache: typing.Optional[builtins.bool] = None,
        push_latest: typing.Optional[builtins.bool] = None,
        test_commands: typing.Optional[typing.Sequence[builtins.str]] = None,
        repository: _aws_cdk_aws_ecr_ceddda9d.IRepository,
        description: typing.Optional[builtins.str] = None,
        log_retention: typing.Optional[_aws_cdk_aws_logs_ceddda9d.RetentionDays] = None,
        removal_policy: typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy] = None,
        security_groups: typing.Optional[typing.Sequence[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup]] = None,
        subnet_selection: typing.Optional[typing.Union[_aws_cdk_aws_ec2_ceddda9d.SubnetSelection, typing.Dict[builtins.str, typing.Any]]] = None,
        vpc: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IVpc] = None,
    ) -> None:
        '''Creates a new LinuxDockerBuildProject.

        :param scope: - The scope in which to define this construct.
        :param id: - The scoped construct ID.
        :param build_directory: The build context directory. Default: - The current directory (.)
        :param build_image: The CodeBuild build image to use. Default: - LinuxBuildImage.STANDARD_7_0
        :param compute_type: The type of compute to use for this build. Default: - ComputeType.SMALL
        :param dockerfile: The filename of the Dockerfile. Default: - Dockerfile
        :param enable_cache: Whether to enable build caching. Default: - false
        :param push_latest: Whether to push a "latest" tag. Default: - true
        :param test_commands: Commands used to test the image once built.
        :param repository: The ECR repository where images are pushed.
        :param description: A description of this CodeBuild project.
        :param log_retention: The duration to retain log entries. Default: - RetentionDays.THREE_MONTHS
        :param removal_policy: The removal policy for this project and its logs.
        :param security_groups: Security groups to associate with the project's network interfaces.
        :param subnet_selection: Where to place the network interfaces within the VPC.
        :param vpc: VPC network to place CodeBuild network interfaces.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__909eca6f21237a8f8575d0aaa02a029242a95ef0ddf952a76fb2554f93527f99)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = LinuxDockerBuildProjectProps(
            build_directory=build_directory,
            build_image=build_image,
            compute_type=compute_type,
            dockerfile=dockerfile,
            enable_cache=enable_cache,
            push_latest=push_latest,
            test_commands=test_commands,
            repository=repository,
            description=description,
            log_retention=log_retention,
            removal_policy=removal_policy,
            security_groups=security_groups,
            subnet_selection=subnet_selection,
            vpc=vpc,
        )

        jsii.create(self.__class__, self, [scope, id, props])


@jsii.data_type(
    jsii_type="shady-island.automation.LinuxDockerBuildProjectProps",
    jsii_struct_bases=[CommonDockerProps],
    name_mapping={
        "repository": "repository",
        "description": "description",
        "log_retention": "logRetention",
        "removal_policy": "removalPolicy",
        "security_groups": "securityGroups",
        "subnet_selection": "subnetSelection",
        "vpc": "vpc",
        "build_directory": "buildDirectory",
        "build_image": "buildImage",
        "compute_type": "computeType",
        "dockerfile": "dockerfile",
        "enable_cache": "enableCache",
        "push_latest": "pushLatest",
        "test_commands": "testCommands",
    },
)
class LinuxDockerBuildProjectProps(CommonDockerProps):
    def __init__(
        self,
        *,
        repository: _aws_cdk_aws_ecr_ceddda9d.IRepository,
        description: typing.Optional[builtins.str] = None,
        log_retention: typing.Optional[_aws_cdk_aws_logs_ceddda9d.RetentionDays] = None,
        removal_policy: typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy] = None,
        security_groups: typing.Optional[typing.Sequence[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup]] = None,
        subnet_selection: typing.Optional[typing.Union[_aws_cdk_aws_ec2_ceddda9d.SubnetSelection, typing.Dict[builtins.str, typing.Any]]] = None,
        vpc: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IVpc] = None,
        build_directory: typing.Optional[builtins.str] = None,
        build_image: typing.Optional[_aws_cdk_aws_codebuild_ceddda9d.IBuildImage] = None,
        compute_type: typing.Optional[_aws_cdk_aws_codebuild_ceddda9d.ComputeType] = None,
        dockerfile: typing.Optional[builtins.str] = None,
        enable_cache: typing.Optional[builtins.bool] = None,
        push_latest: typing.Optional[builtins.bool] = None,
        test_commands: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''Constructor properties for LinuxDockerBuildProject.

        :param repository: The ECR repository where images are pushed.
        :param description: A description of this CodeBuild project.
        :param log_retention: The duration to retain log entries. Default: - RetentionDays.THREE_MONTHS
        :param removal_policy: The removal policy for this project and its logs.
        :param security_groups: Security groups to associate with the project's network interfaces.
        :param subnet_selection: Where to place the network interfaces within the VPC.
        :param vpc: VPC network to place CodeBuild network interfaces.
        :param build_directory: The build context directory. Default: - The current directory (.)
        :param build_image: The CodeBuild build image to use. Default: - LinuxBuildImage.STANDARD_7_0
        :param compute_type: The type of compute to use for this build. Default: - ComputeType.SMALL
        :param dockerfile: The filename of the Dockerfile. Default: - Dockerfile
        :param enable_cache: Whether to enable build caching. Default: - false
        :param push_latest: Whether to push a "latest" tag. Default: - true
        :param test_commands: Commands used to test the image once built.
        '''
        if isinstance(subnet_selection, dict):
            subnet_selection = _aws_cdk_aws_ec2_ceddda9d.SubnetSelection(**subnet_selection)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e66d96a5149c80670c420d3151babfa0c3429e2e1e22cee09b1ca9746f9c54ee)
            check_type(argname="argument repository", value=repository, expected_type=type_hints["repository"])
            check_type(argname="argument description", value=description, expected_type=type_hints["description"])
            check_type(argname="argument log_retention", value=log_retention, expected_type=type_hints["log_retention"])
            check_type(argname="argument removal_policy", value=removal_policy, expected_type=type_hints["removal_policy"])
            check_type(argname="argument security_groups", value=security_groups, expected_type=type_hints["security_groups"])
            check_type(argname="argument subnet_selection", value=subnet_selection, expected_type=type_hints["subnet_selection"])
            check_type(argname="argument vpc", value=vpc, expected_type=type_hints["vpc"])
            check_type(argname="argument build_directory", value=build_directory, expected_type=type_hints["build_directory"])
            check_type(argname="argument build_image", value=build_image, expected_type=type_hints["build_image"])
            check_type(argname="argument compute_type", value=compute_type, expected_type=type_hints["compute_type"])
            check_type(argname="argument dockerfile", value=dockerfile, expected_type=type_hints["dockerfile"])
            check_type(argname="argument enable_cache", value=enable_cache, expected_type=type_hints["enable_cache"])
            check_type(argname="argument push_latest", value=push_latest, expected_type=type_hints["push_latest"])
            check_type(argname="argument test_commands", value=test_commands, expected_type=type_hints["test_commands"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "repository": repository,
        }
        if description is not None:
            self._values["description"] = description
        if log_retention is not None:
            self._values["log_retention"] = log_retention
        if removal_policy is not None:
            self._values["removal_policy"] = removal_policy
        if security_groups is not None:
            self._values["security_groups"] = security_groups
        if subnet_selection is not None:
            self._values["subnet_selection"] = subnet_selection
        if vpc is not None:
            self._values["vpc"] = vpc
        if build_directory is not None:
            self._values["build_directory"] = build_directory
        if build_image is not None:
            self._values["build_image"] = build_image
        if compute_type is not None:
            self._values["compute_type"] = compute_type
        if dockerfile is not None:
            self._values["dockerfile"] = dockerfile
        if enable_cache is not None:
            self._values["enable_cache"] = enable_cache
        if push_latest is not None:
            self._values["push_latest"] = push_latest
        if test_commands is not None:
            self._values["test_commands"] = test_commands

    @builtins.property
    def repository(self) -> _aws_cdk_aws_ecr_ceddda9d.IRepository:
        '''The ECR repository where images are pushed.'''
        result = self._values.get("repository")
        assert result is not None, "Required property 'repository' is missing"
        return typing.cast(_aws_cdk_aws_ecr_ceddda9d.IRepository, result)

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        '''A description of this CodeBuild project.'''
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def log_retention(
        self,
    ) -> typing.Optional[_aws_cdk_aws_logs_ceddda9d.RetentionDays]:
        '''The duration to retain log entries.

        :default: - RetentionDays.THREE_MONTHS
        '''
        result = self._values.get("log_retention")
        return typing.cast(typing.Optional[_aws_cdk_aws_logs_ceddda9d.RetentionDays], result)

    @builtins.property
    def removal_policy(self) -> typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy]:
        '''The removal policy for this project and its logs.'''
        result = self._values.get("removal_policy")
        return typing.cast(typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy], result)

    @builtins.property
    def security_groups(
        self,
    ) -> typing.Optional[typing.List[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup]]:
        '''Security groups to associate with the project's network interfaces.'''
        result = self._values.get("security_groups")
        return typing.cast(typing.Optional[typing.List[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup]], result)

    @builtins.property
    def subnet_selection(
        self,
    ) -> typing.Optional[_aws_cdk_aws_ec2_ceddda9d.SubnetSelection]:
        '''Where to place the network interfaces within the VPC.'''
        result = self._values.get("subnet_selection")
        return typing.cast(typing.Optional[_aws_cdk_aws_ec2_ceddda9d.SubnetSelection], result)

    @builtins.property
    def vpc(self) -> typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IVpc]:
        '''VPC network to place CodeBuild network interfaces.'''
        result = self._values.get("vpc")
        return typing.cast(typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IVpc], result)

    @builtins.property
    def build_directory(self) -> typing.Optional[builtins.str]:
        '''The build context directory.

        :default: - The current directory (.)
        '''
        result = self._values.get("build_directory")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def build_image(
        self,
    ) -> typing.Optional[_aws_cdk_aws_codebuild_ceddda9d.IBuildImage]:
        '''The CodeBuild build image to use.

        :default: - LinuxBuildImage.STANDARD_7_0
        '''
        result = self._values.get("build_image")
        return typing.cast(typing.Optional[_aws_cdk_aws_codebuild_ceddda9d.IBuildImage], result)

    @builtins.property
    def compute_type(
        self,
    ) -> typing.Optional[_aws_cdk_aws_codebuild_ceddda9d.ComputeType]:
        '''The type of compute to use for this build.

        :default: - ComputeType.SMALL
        '''
        result = self._values.get("compute_type")
        return typing.cast(typing.Optional[_aws_cdk_aws_codebuild_ceddda9d.ComputeType], result)

    @builtins.property
    def dockerfile(self) -> typing.Optional[builtins.str]:
        '''The filename of the Dockerfile.

        :default: - Dockerfile
        '''
        result = self._values.get("dockerfile")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def enable_cache(self) -> typing.Optional[builtins.bool]:
        '''Whether to enable build caching.

        :default: - false
        '''
        result = self._values.get("enable_cache")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def push_latest(self) -> typing.Optional[builtins.bool]:
        '''Whether to push a "latest" tag.

        :default: - true
        '''
        result = self._values.get("push_latest")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def test_commands(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Commands used to test the image once built.'''
        result = self._values.get("test_commands")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "LinuxDockerBuildProjectProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class LinuxDockerManifestProject(
    BaseDockerProject,
    metaclass=jsii.JSIIMeta,
    jsii_type="shady-island.automation.LinuxDockerManifestProject",
):
    '''Sets up a standardized Docker manifest build project.

    This project accepts the following variables:

    - LATEST_TAG: Optional. The tag to push (default: "latest").
    - MANIFEST_CUSTOM_TAG: Optional. The tag to push, in addition to $LATEST_TAG.
    '''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        tag_variable_names: typing.Sequence[builtins.str],
        build_image: typing.Optional[_aws_cdk_aws_codebuild_ceddda9d.IBuildImage] = None,
        compute_type: typing.Optional[_aws_cdk_aws_codebuild_ceddda9d.ComputeType] = None,
        repository: _aws_cdk_aws_ecr_ceddda9d.IRepository,
        description: typing.Optional[builtins.str] = None,
        log_retention: typing.Optional[_aws_cdk_aws_logs_ceddda9d.RetentionDays] = None,
        removal_policy: typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy] = None,
        security_groups: typing.Optional[typing.Sequence[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup]] = None,
        subnet_selection: typing.Optional[typing.Union[_aws_cdk_aws_ec2_ceddda9d.SubnetSelection, typing.Dict[builtins.str, typing.Any]]] = None,
        vpc: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IVpc] = None,
    ) -> None:
        '''Creates a new LinuxDockerManifestProject.

        :param scope: - The scope in which to define this construct.
        :param id: - The scoped construct ID.
        :param tag_variable_names: The names of environment variables that contain the image hashes to add.
        :param build_image: The CodeBuild build image to use. Default: - LinuxBuildImage.STANDARD_7_0
        :param compute_type: The type of compute to use for this build. Default: - ComputeType.SMALL
        :param repository: The ECR repository where images are pushed.
        :param description: A description of this CodeBuild project.
        :param log_retention: The duration to retain log entries. Default: - RetentionDays.THREE_MONTHS
        :param removal_policy: The removal policy for this project and its logs.
        :param security_groups: Security groups to associate with the project's network interfaces.
        :param subnet_selection: Where to place the network interfaces within the VPC.
        :param vpc: VPC network to place CodeBuild network interfaces.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__bccbd0494bb69ae19da7cbf563f1cd1d1365f4a1d6bd7c2e9a5b8f6f2d8bfc2a)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = LinuxDockerManifestProjectProps(
            tag_variable_names=tag_variable_names,
            build_image=build_image,
            compute_type=compute_type,
            repository=repository,
            description=description,
            log_retention=log_retention,
            removal_policy=removal_policy,
            security_groups=security_groups,
            subnet_selection=subnet_selection,
            vpc=vpc,
        )

        jsii.create(self.__class__, self, [scope, id, props])


@jsii.data_type(
    jsii_type="shady-island.automation.LinuxDockerManifestProjectProps",
    jsii_struct_bases=[CommonDockerProps],
    name_mapping={
        "repository": "repository",
        "description": "description",
        "log_retention": "logRetention",
        "removal_policy": "removalPolicy",
        "security_groups": "securityGroups",
        "subnet_selection": "subnetSelection",
        "vpc": "vpc",
        "tag_variable_names": "tagVariableNames",
        "build_image": "buildImage",
        "compute_type": "computeType",
    },
)
class LinuxDockerManifestProjectProps(CommonDockerProps):
    def __init__(
        self,
        *,
        repository: _aws_cdk_aws_ecr_ceddda9d.IRepository,
        description: typing.Optional[builtins.str] = None,
        log_retention: typing.Optional[_aws_cdk_aws_logs_ceddda9d.RetentionDays] = None,
        removal_policy: typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy] = None,
        security_groups: typing.Optional[typing.Sequence[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup]] = None,
        subnet_selection: typing.Optional[typing.Union[_aws_cdk_aws_ec2_ceddda9d.SubnetSelection, typing.Dict[builtins.str, typing.Any]]] = None,
        vpc: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IVpc] = None,
        tag_variable_names: typing.Sequence[builtins.str],
        build_image: typing.Optional[_aws_cdk_aws_codebuild_ceddda9d.IBuildImage] = None,
        compute_type: typing.Optional[_aws_cdk_aws_codebuild_ceddda9d.ComputeType] = None,
    ) -> None:
        '''Constructor properties for LinuxDockerManifestProject.

        :param repository: The ECR repository where images are pushed.
        :param description: A description of this CodeBuild project.
        :param log_retention: The duration to retain log entries. Default: - RetentionDays.THREE_MONTHS
        :param removal_policy: The removal policy for this project and its logs.
        :param security_groups: Security groups to associate with the project's network interfaces.
        :param subnet_selection: Where to place the network interfaces within the VPC.
        :param vpc: VPC network to place CodeBuild network interfaces.
        :param tag_variable_names: The names of environment variables that contain the image hashes to add.
        :param build_image: The CodeBuild build image to use. Default: - LinuxBuildImage.STANDARD_7_0
        :param compute_type: The type of compute to use for this build. Default: - ComputeType.SMALL
        '''
        if isinstance(subnet_selection, dict):
            subnet_selection = _aws_cdk_aws_ec2_ceddda9d.SubnetSelection(**subnet_selection)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__fa5e66545b7e16d979bc26daec435428b33dcdf5349620a5ede4d0c7402ce57d)
            check_type(argname="argument repository", value=repository, expected_type=type_hints["repository"])
            check_type(argname="argument description", value=description, expected_type=type_hints["description"])
            check_type(argname="argument log_retention", value=log_retention, expected_type=type_hints["log_retention"])
            check_type(argname="argument removal_policy", value=removal_policy, expected_type=type_hints["removal_policy"])
            check_type(argname="argument security_groups", value=security_groups, expected_type=type_hints["security_groups"])
            check_type(argname="argument subnet_selection", value=subnet_selection, expected_type=type_hints["subnet_selection"])
            check_type(argname="argument vpc", value=vpc, expected_type=type_hints["vpc"])
            check_type(argname="argument tag_variable_names", value=tag_variable_names, expected_type=type_hints["tag_variable_names"])
            check_type(argname="argument build_image", value=build_image, expected_type=type_hints["build_image"])
            check_type(argname="argument compute_type", value=compute_type, expected_type=type_hints["compute_type"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "repository": repository,
            "tag_variable_names": tag_variable_names,
        }
        if description is not None:
            self._values["description"] = description
        if log_retention is not None:
            self._values["log_retention"] = log_retention
        if removal_policy is not None:
            self._values["removal_policy"] = removal_policy
        if security_groups is not None:
            self._values["security_groups"] = security_groups
        if subnet_selection is not None:
            self._values["subnet_selection"] = subnet_selection
        if vpc is not None:
            self._values["vpc"] = vpc
        if build_image is not None:
            self._values["build_image"] = build_image
        if compute_type is not None:
            self._values["compute_type"] = compute_type

    @builtins.property
    def repository(self) -> _aws_cdk_aws_ecr_ceddda9d.IRepository:
        '''The ECR repository where images are pushed.'''
        result = self._values.get("repository")
        assert result is not None, "Required property 'repository' is missing"
        return typing.cast(_aws_cdk_aws_ecr_ceddda9d.IRepository, result)

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        '''A description of this CodeBuild project.'''
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def log_retention(
        self,
    ) -> typing.Optional[_aws_cdk_aws_logs_ceddda9d.RetentionDays]:
        '''The duration to retain log entries.

        :default: - RetentionDays.THREE_MONTHS
        '''
        result = self._values.get("log_retention")
        return typing.cast(typing.Optional[_aws_cdk_aws_logs_ceddda9d.RetentionDays], result)

    @builtins.property
    def removal_policy(self) -> typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy]:
        '''The removal policy for this project and its logs.'''
        result = self._values.get("removal_policy")
        return typing.cast(typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy], result)

    @builtins.property
    def security_groups(
        self,
    ) -> typing.Optional[typing.List[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup]]:
        '''Security groups to associate with the project's network interfaces.'''
        result = self._values.get("security_groups")
        return typing.cast(typing.Optional[typing.List[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup]], result)

    @builtins.property
    def subnet_selection(
        self,
    ) -> typing.Optional[_aws_cdk_aws_ec2_ceddda9d.SubnetSelection]:
        '''Where to place the network interfaces within the VPC.'''
        result = self._values.get("subnet_selection")
        return typing.cast(typing.Optional[_aws_cdk_aws_ec2_ceddda9d.SubnetSelection], result)

    @builtins.property
    def vpc(self) -> typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IVpc]:
        '''VPC network to place CodeBuild network interfaces.'''
        result = self._values.get("vpc")
        return typing.cast(typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IVpc], result)

    @builtins.property
    def tag_variable_names(self) -> typing.List[builtins.str]:
        '''The names of environment variables that contain the image hashes to add.'''
        result = self._values.get("tag_variable_names")
        assert result is not None, "Required property 'tag_variable_names' is missing"
        return typing.cast(typing.List[builtins.str], result)

    @builtins.property
    def build_image(
        self,
    ) -> typing.Optional[_aws_cdk_aws_codebuild_ceddda9d.IBuildImage]:
        '''The CodeBuild build image to use.

        :default: - LinuxBuildImage.STANDARD_7_0
        '''
        result = self._values.get("build_image")
        return typing.cast(typing.Optional[_aws_cdk_aws_codebuild_ceddda9d.IBuildImage], result)

    @builtins.property
    def compute_type(
        self,
    ) -> typing.Optional[_aws_cdk_aws_codebuild_ceddda9d.ComputeType]:
        '''The type of compute to use for this build.

        :default: - ComputeType.SMALL
        '''
        result = self._values.get("compute_type")
        return typing.cast(typing.Optional[_aws_cdk_aws_codebuild_ceddda9d.ComputeType], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "LinuxDockerManifestProjectProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="shady-island.automation.BaseDockerProjectProps",
    jsii_struct_bases=[CommonDockerProps],
    name_mapping={
        "repository": "repository",
        "description": "description",
        "log_retention": "logRetention",
        "removal_policy": "removalPolicy",
        "security_groups": "securityGroups",
        "subnet_selection": "subnetSelection",
        "vpc": "vpc",
        "build_environment": "buildEnvironment",
        "build_spec": "buildSpec",
    },
)
class BaseDockerProjectProps(CommonDockerProps):
    def __init__(
        self,
        *,
        repository: _aws_cdk_aws_ecr_ceddda9d.IRepository,
        description: typing.Optional[builtins.str] = None,
        log_retention: typing.Optional[_aws_cdk_aws_logs_ceddda9d.RetentionDays] = None,
        removal_policy: typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy] = None,
        security_groups: typing.Optional[typing.Sequence[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup]] = None,
        subnet_selection: typing.Optional[typing.Union[_aws_cdk_aws_ec2_ceddda9d.SubnetSelection, typing.Dict[builtins.str, typing.Any]]] = None,
        vpc: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IVpc] = None,
        build_environment: typing.Union[_aws_cdk_aws_codebuild_ceddda9d.BuildEnvironment, typing.Dict[builtins.str, typing.Any]],
        build_spec: _aws_cdk_aws_codebuild_ceddda9d.BuildSpec,
    ) -> None:
        '''Constructor properties for BaseDockerProject.

        :param repository: The ECR repository where images are pushed.
        :param description: A description of this CodeBuild project.
        :param log_retention: The duration to retain log entries. Default: - RetentionDays.THREE_MONTHS
        :param removal_policy: The removal policy for this project and its logs.
        :param security_groups: Security groups to associate with the project's network interfaces.
        :param subnet_selection: Where to place the network interfaces within the VPC.
        :param vpc: VPC network to place CodeBuild network interfaces.
        :param build_environment: Build environment to use for the build.
        :param build_spec: Filename or contents of buildspec in JSON format.
        '''
        if isinstance(subnet_selection, dict):
            subnet_selection = _aws_cdk_aws_ec2_ceddda9d.SubnetSelection(**subnet_selection)
        if isinstance(build_environment, dict):
            build_environment = _aws_cdk_aws_codebuild_ceddda9d.BuildEnvironment(**build_environment)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__780701f8db35a696cc3c20655d208abef546e4b4291478c5e4ab4bc06969eec8)
            check_type(argname="argument repository", value=repository, expected_type=type_hints["repository"])
            check_type(argname="argument description", value=description, expected_type=type_hints["description"])
            check_type(argname="argument log_retention", value=log_retention, expected_type=type_hints["log_retention"])
            check_type(argname="argument removal_policy", value=removal_policy, expected_type=type_hints["removal_policy"])
            check_type(argname="argument security_groups", value=security_groups, expected_type=type_hints["security_groups"])
            check_type(argname="argument subnet_selection", value=subnet_selection, expected_type=type_hints["subnet_selection"])
            check_type(argname="argument vpc", value=vpc, expected_type=type_hints["vpc"])
            check_type(argname="argument build_environment", value=build_environment, expected_type=type_hints["build_environment"])
            check_type(argname="argument build_spec", value=build_spec, expected_type=type_hints["build_spec"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "repository": repository,
            "build_environment": build_environment,
            "build_spec": build_spec,
        }
        if description is not None:
            self._values["description"] = description
        if log_retention is not None:
            self._values["log_retention"] = log_retention
        if removal_policy is not None:
            self._values["removal_policy"] = removal_policy
        if security_groups is not None:
            self._values["security_groups"] = security_groups
        if subnet_selection is not None:
            self._values["subnet_selection"] = subnet_selection
        if vpc is not None:
            self._values["vpc"] = vpc

    @builtins.property
    def repository(self) -> _aws_cdk_aws_ecr_ceddda9d.IRepository:
        '''The ECR repository where images are pushed.'''
        result = self._values.get("repository")
        assert result is not None, "Required property 'repository' is missing"
        return typing.cast(_aws_cdk_aws_ecr_ceddda9d.IRepository, result)

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        '''A description of this CodeBuild project.'''
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def log_retention(
        self,
    ) -> typing.Optional[_aws_cdk_aws_logs_ceddda9d.RetentionDays]:
        '''The duration to retain log entries.

        :default: - RetentionDays.THREE_MONTHS
        '''
        result = self._values.get("log_retention")
        return typing.cast(typing.Optional[_aws_cdk_aws_logs_ceddda9d.RetentionDays], result)

    @builtins.property
    def removal_policy(self) -> typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy]:
        '''The removal policy for this project and its logs.'''
        result = self._values.get("removal_policy")
        return typing.cast(typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy], result)

    @builtins.property
    def security_groups(
        self,
    ) -> typing.Optional[typing.List[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup]]:
        '''Security groups to associate with the project's network interfaces.'''
        result = self._values.get("security_groups")
        return typing.cast(typing.Optional[typing.List[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup]], result)

    @builtins.property
    def subnet_selection(
        self,
    ) -> typing.Optional[_aws_cdk_aws_ec2_ceddda9d.SubnetSelection]:
        '''Where to place the network interfaces within the VPC.'''
        result = self._values.get("subnet_selection")
        return typing.cast(typing.Optional[_aws_cdk_aws_ec2_ceddda9d.SubnetSelection], result)

    @builtins.property
    def vpc(self) -> typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IVpc]:
        '''VPC network to place CodeBuild network interfaces.'''
        result = self._values.get("vpc")
        return typing.cast(typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IVpc], result)

    @builtins.property
    def build_environment(self) -> _aws_cdk_aws_codebuild_ceddda9d.BuildEnvironment:
        '''Build environment to use for the build.'''
        result = self._values.get("build_environment")
        assert result is not None, "Required property 'build_environment' is missing"
        return typing.cast(_aws_cdk_aws_codebuild_ceddda9d.BuildEnvironment, result)

    @builtins.property
    def build_spec(self) -> _aws_cdk_aws_codebuild_ceddda9d.BuildSpec:
        '''Filename or contents of buildspec in JSON format.'''
        result = self._values.get("build_spec")
        assert result is not None, "Required property 'build_spec' is missing"
        return typing.cast(_aws_cdk_aws_codebuild_ceddda9d.BuildSpec, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "BaseDockerProjectProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "BaseDockerProject",
    "BaseDockerProjectProps",
    "CommonDockerProps",
    "ContainerImagePipeline",
    "ContainerImagePipelineProps",
    "FunctionCodeUpdater",
    "FunctionCodeUpdaterProps",
    "LinuxDockerBuildProject",
    "LinuxDockerBuildProjectProps",
    "LinuxDockerManifestProject",
    "LinuxDockerManifestProjectProps",
]

publication.publish()

def _typecheckingstub__eb4cd3f68a28927dc8e96eb24e7b96185808332c2fe8f897afdc5e1ca9946380(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    build_environment: typing.Union[_aws_cdk_aws_codebuild_ceddda9d.BuildEnvironment, typing.Dict[builtins.str, typing.Any]],
    build_spec: _aws_cdk_aws_codebuild_ceddda9d.BuildSpec,
    repository: _aws_cdk_aws_ecr_ceddda9d.IRepository,
    description: typing.Optional[builtins.str] = None,
    log_retention: typing.Optional[_aws_cdk_aws_logs_ceddda9d.RetentionDays] = None,
    removal_policy: typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy] = None,
    security_groups: typing.Optional[typing.Sequence[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup]] = None,
    subnet_selection: typing.Optional[typing.Union[_aws_cdk_aws_ec2_ceddda9d.SubnetSelection, typing.Dict[builtins.str, typing.Any]]] = None,
    vpc: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IVpc] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__cfce4f825ec93fc3471974bb12955f80569f0dfde3d440a3f52ce93d6a2df412(
    policy: _aws_cdk_ceddda9d.RemovalPolicy,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4f0a6c70505e3cc3734a6cdc646578bbc44f54a8e031c316e0293b2c9f1dfdd5(
    *,
    repository: _aws_cdk_aws_ecr_ceddda9d.IRepository,
    description: typing.Optional[builtins.str] = None,
    log_retention: typing.Optional[_aws_cdk_aws_logs_ceddda9d.RetentionDays] = None,
    removal_policy: typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy] = None,
    security_groups: typing.Optional[typing.Sequence[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup]] = None,
    subnet_selection: typing.Optional[typing.Union[_aws_cdk_aws_ec2_ceddda9d.SubnetSelection, typing.Dict[builtins.str, typing.Any]]] = None,
    vpc: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IVpc] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__cedb29f5ea4e41db2040cf196e8fb5c9c4a295ca5a54967d23de3d82284bb5a4(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    container: builtins.str,
    repository: _aws_cdk_aws_ecr_ceddda9d.IRepository,
    service: _aws_cdk_aws_ecs_ceddda9d.IBaseService,
    artifact_bucket: typing.Optional[_aws_cdk_aws_s3_ceddda9d.IBucket] = None,
    pipeline_type: typing.Optional[_aws_cdk_aws_codepipeline_ceddda9d.PipelineType] = None,
    tag: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a82c69c46656ae83e2077c89d799ffb8536b4ddcc17b205a38a2221073be2e48(
    *,
    container: builtins.str,
    repository: _aws_cdk_aws_ecr_ceddda9d.IRepository,
    service: _aws_cdk_aws_ecs_ceddda9d.IBaseService,
    artifact_bucket: typing.Optional[_aws_cdk_aws_s3_ceddda9d.IBucket] = None,
    pipeline_type: typing.Optional[_aws_cdk_aws_codepipeline_ceddda9d.PipelineType] = None,
    tag: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f33a0905023521597d28cee93114601f3e35da34b9eff4df0ee5fd59350ad1e3(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    bucket: _aws_cdk_aws_s3_ceddda9d.IBucket,
    object_key: builtins.str,
    target: _aws_cdk_aws_lambda_ceddda9d.IFunction,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8dbf24b39a405557c0b908319842dd0572a414219a6984055ab05854fb4231eb(
    identity: _aws_cdk_aws_iam_ceddda9d.IGrantable,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__19f46ec283cf845783c22e4264d22e7ba242c3d2c1ccb328e80a86024cb13ec3(
    *,
    bucket: _aws_cdk_aws_s3_ceddda9d.IBucket,
    object_key: builtins.str,
    target: _aws_cdk_aws_lambda_ceddda9d.IFunction,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__909eca6f21237a8f8575d0aaa02a029242a95ef0ddf952a76fb2554f93527f99(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    build_directory: typing.Optional[builtins.str] = None,
    build_image: typing.Optional[_aws_cdk_aws_codebuild_ceddda9d.IBuildImage] = None,
    compute_type: typing.Optional[_aws_cdk_aws_codebuild_ceddda9d.ComputeType] = None,
    dockerfile: typing.Optional[builtins.str] = None,
    enable_cache: typing.Optional[builtins.bool] = None,
    push_latest: typing.Optional[builtins.bool] = None,
    test_commands: typing.Optional[typing.Sequence[builtins.str]] = None,
    repository: _aws_cdk_aws_ecr_ceddda9d.IRepository,
    description: typing.Optional[builtins.str] = None,
    log_retention: typing.Optional[_aws_cdk_aws_logs_ceddda9d.RetentionDays] = None,
    removal_policy: typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy] = None,
    security_groups: typing.Optional[typing.Sequence[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup]] = None,
    subnet_selection: typing.Optional[typing.Union[_aws_cdk_aws_ec2_ceddda9d.SubnetSelection, typing.Dict[builtins.str, typing.Any]]] = None,
    vpc: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IVpc] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e66d96a5149c80670c420d3151babfa0c3429e2e1e22cee09b1ca9746f9c54ee(
    *,
    repository: _aws_cdk_aws_ecr_ceddda9d.IRepository,
    description: typing.Optional[builtins.str] = None,
    log_retention: typing.Optional[_aws_cdk_aws_logs_ceddda9d.RetentionDays] = None,
    removal_policy: typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy] = None,
    security_groups: typing.Optional[typing.Sequence[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup]] = None,
    subnet_selection: typing.Optional[typing.Union[_aws_cdk_aws_ec2_ceddda9d.SubnetSelection, typing.Dict[builtins.str, typing.Any]]] = None,
    vpc: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IVpc] = None,
    build_directory: typing.Optional[builtins.str] = None,
    build_image: typing.Optional[_aws_cdk_aws_codebuild_ceddda9d.IBuildImage] = None,
    compute_type: typing.Optional[_aws_cdk_aws_codebuild_ceddda9d.ComputeType] = None,
    dockerfile: typing.Optional[builtins.str] = None,
    enable_cache: typing.Optional[builtins.bool] = None,
    push_latest: typing.Optional[builtins.bool] = None,
    test_commands: typing.Optional[typing.Sequence[builtins.str]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__bccbd0494bb69ae19da7cbf563f1cd1d1365f4a1d6bd7c2e9a5b8f6f2d8bfc2a(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    tag_variable_names: typing.Sequence[builtins.str],
    build_image: typing.Optional[_aws_cdk_aws_codebuild_ceddda9d.IBuildImage] = None,
    compute_type: typing.Optional[_aws_cdk_aws_codebuild_ceddda9d.ComputeType] = None,
    repository: _aws_cdk_aws_ecr_ceddda9d.IRepository,
    description: typing.Optional[builtins.str] = None,
    log_retention: typing.Optional[_aws_cdk_aws_logs_ceddda9d.RetentionDays] = None,
    removal_policy: typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy] = None,
    security_groups: typing.Optional[typing.Sequence[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup]] = None,
    subnet_selection: typing.Optional[typing.Union[_aws_cdk_aws_ec2_ceddda9d.SubnetSelection, typing.Dict[builtins.str, typing.Any]]] = None,
    vpc: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IVpc] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fa5e66545b7e16d979bc26daec435428b33dcdf5349620a5ede4d0c7402ce57d(
    *,
    repository: _aws_cdk_aws_ecr_ceddda9d.IRepository,
    description: typing.Optional[builtins.str] = None,
    log_retention: typing.Optional[_aws_cdk_aws_logs_ceddda9d.RetentionDays] = None,
    removal_policy: typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy] = None,
    security_groups: typing.Optional[typing.Sequence[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup]] = None,
    subnet_selection: typing.Optional[typing.Union[_aws_cdk_aws_ec2_ceddda9d.SubnetSelection, typing.Dict[builtins.str, typing.Any]]] = None,
    vpc: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IVpc] = None,
    tag_variable_names: typing.Sequence[builtins.str],
    build_image: typing.Optional[_aws_cdk_aws_codebuild_ceddda9d.IBuildImage] = None,
    compute_type: typing.Optional[_aws_cdk_aws_codebuild_ceddda9d.ComputeType] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__780701f8db35a696cc3c20655d208abef546e4b4291478c5e4ab4bc06969eec8(
    *,
    repository: _aws_cdk_aws_ecr_ceddda9d.IRepository,
    description: typing.Optional[builtins.str] = None,
    log_retention: typing.Optional[_aws_cdk_aws_logs_ceddda9d.RetentionDays] = None,
    removal_policy: typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy] = None,
    security_groups: typing.Optional[typing.Sequence[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup]] = None,
    subnet_selection: typing.Optional[typing.Union[_aws_cdk_aws_ec2_ceddda9d.SubnetSelection, typing.Dict[builtins.str, typing.Any]]] = None,
    vpc: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IVpc] = None,
    build_environment: typing.Union[_aws_cdk_aws_codebuild_ceddda9d.BuildEnvironment, typing.Dict[builtins.str, typing.Any]],
    build_spec: _aws_cdk_aws_codebuild_ceddda9d.BuildSpec,
) -> None:
    """Type checking stubs"""
    pass
