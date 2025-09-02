r'''
# `data_opentelekomcloud_tms_resource_instances_v1`

Refer to the Terraform Registry for docs: [`data_opentelekomcloud_tms_resource_instances_v1`](https://registry.terraform.io/providers/opentelekomcloud/opentelekomcloud/1.36.46/docs/data-sources/tms_resource_instances_v1).
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

from .._jsii import *

import cdktf as _cdktf_9a9027ec
import constructs as _constructs_77d1e7e8


class DataOpentelekomcloudTmsResourceInstancesV1(
    _cdktf_9a9027ec.TerraformDataSource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-opentelekomcloud.dataOpentelekomcloudTmsResourceInstancesV1.DataOpentelekomcloudTmsResourceInstancesV1",
):
    '''Represents a {@link https://registry.terraform.io/providers/opentelekomcloud/opentelekomcloud/1.36.46/docs/data-sources/tms_resource_instances_v1 opentelekomcloud_tms_resource_instances_v1}.'''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id_: builtins.str,
        *,
        resource_types: typing.Sequence[builtins.str],
        tags: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["DataOpentelekomcloudTmsResourceInstancesV1Tags", typing.Dict[builtins.str, typing.Any]]]],
        id: typing.Optional[builtins.str] = None,
        project_id: typing.Optional[builtins.str] = None,
        without_any_tag: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
        count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
        depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
        for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
        lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
        provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
        provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    ) -> None:
        '''Create a new {@link https://registry.terraform.io/providers/opentelekomcloud/opentelekomcloud/1.36.46/docs/data-sources/tms_resource_instances_v1 opentelekomcloud_tms_resource_instances_v1} Data Source.

        :param scope: The scope in which to define this construct.
        :param id_: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param resource_types: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/opentelekomcloud/opentelekomcloud/1.36.46/docs/data-sources/tms_resource_instances_v1#resource_types DataOpentelekomcloudTmsResourceInstancesV1#resource_types}.
        :param tags: tags block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/opentelekomcloud/opentelekomcloud/1.36.46/docs/data-sources/tms_resource_instances_v1#tags DataOpentelekomcloudTmsResourceInstancesV1#tags}
        :param id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/opentelekomcloud/opentelekomcloud/1.36.46/docs/data-sources/tms_resource_instances_v1#id DataOpentelekomcloudTmsResourceInstancesV1#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param project_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/opentelekomcloud/opentelekomcloud/1.36.46/docs/data-sources/tms_resource_instances_v1#project_id DataOpentelekomcloudTmsResourceInstancesV1#project_id}.
        :param without_any_tag: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/opentelekomcloud/opentelekomcloud/1.36.46/docs/data-sources/tms_resource_instances_v1#without_any_tag DataOpentelekomcloudTmsResourceInstancesV1#without_any_tag}.
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0273037f3e403e2c6f80fd017018bc120767e3c9eb3b31cdcd76b33a41287993)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id_", value=id_, expected_type=type_hints["id_"])
        config = DataOpentelekomcloudTmsResourceInstancesV1Config(
            resource_types=resource_types,
            tags=tags,
            id=id,
            project_id=project_id,
            without_any_tag=without_any_tag,
            connection=connection,
            count=count,
            depends_on=depends_on,
            for_each=for_each,
            lifecycle=lifecycle,
            provider=provider,
            provisioners=provisioners,
        )

        jsii.create(self.__class__, self, [scope, id_, config])

    @jsii.member(jsii_name="generateConfigForImport")
    @builtins.classmethod
    def generate_config_for_import(
        cls,
        scope: _constructs_77d1e7e8.Construct,
        import_to_id: builtins.str,
        import_from_id: builtins.str,
        provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
    ) -> _cdktf_9a9027ec.ImportableResource:
        '''Generates CDKTF code for importing a DataOpentelekomcloudTmsResourceInstancesV1 resource upon running "cdktf plan ".

        :param scope: The scope in which to define this construct.
        :param import_to_id: The construct id used in the generated config for the DataOpentelekomcloudTmsResourceInstancesV1 to import.
        :param import_from_id: The id of the existing DataOpentelekomcloudTmsResourceInstancesV1 that should be imported. Refer to the {@link https://registry.terraform.io/providers/opentelekomcloud/opentelekomcloud/1.36.46/docs/data-sources/tms_resource_instances_v1#import import section} in the documentation of this resource for the id to use
        :param provider: ? Optional instance of the provider where the DataOpentelekomcloudTmsResourceInstancesV1 to import is found.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__46b3991b93090114811a25c5c8a3ba55c8065281a42b0f5edab6ee6b0f8b3d62)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument import_to_id", value=import_to_id, expected_type=type_hints["import_to_id"])
            check_type(argname="argument import_from_id", value=import_from_id, expected_type=type_hints["import_from_id"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
        return typing.cast(_cdktf_9a9027ec.ImportableResource, jsii.sinvoke(cls, "generateConfigForImport", [scope, import_to_id, import_from_id, provider]))

    @jsii.member(jsii_name="putTags")
    def put_tags(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["DataOpentelekomcloudTmsResourceInstancesV1Tags", typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__eb4ad03f4550e1f139516bf86dc5cf055909d94ed7dfeeb6640f759cb21a53a2)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putTags", [value]))

    @jsii.member(jsii_name="resetId")
    def reset_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetId", []))

    @jsii.member(jsii_name="resetProjectId")
    def reset_project_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetProjectId", []))

    @jsii.member(jsii_name="resetWithoutAnyTag")
    def reset_without_any_tag(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetWithoutAnyTag", []))

    @jsii.member(jsii_name="synthesizeAttributes")
    def _synthesize_attributes(self) -> typing.Mapping[builtins.str, typing.Any]:
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.invoke(self, "synthesizeAttributes", []))

    @jsii.member(jsii_name="synthesizeHclAttributes")
    def _synthesize_hcl_attributes(self) -> typing.Mapping[builtins.str, typing.Any]:
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.invoke(self, "synthesizeHclAttributes", []))

    @jsii.python.classproperty
    @jsii.member(jsii_name="tfResourceType")
    def TF_RESOURCE_TYPE(cls) -> builtins.str:
        return typing.cast(builtins.str, jsii.sget(cls, "tfResourceType"))

    @builtins.property
    @jsii.member(jsii_name="resources")
    def resources(self) -> "DataOpentelekomcloudTmsResourceInstancesV1ResourcesList":
        return typing.cast("DataOpentelekomcloudTmsResourceInstancesV1ResourcesList", jsii.get(self, "resources"))

    @builtins.property
    @jsii.member(jsii_name="tags")
    def tags(self) -> "DataOpentelekomcloudTmsResourceInstancesV1TagsList":
        return typing.cast("DataOpentelekomcloudTmsResourceInstancesV1TagsList", jsii.get(self, "tags"))

    @builtins.property
    @jsii.member(jsii_name="idInput")
    def id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "idInput"))

    @builtins.property
    @jsii.member(jsii_name="projectIdInput")
    def project_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "projectIdInput"))

    @builtins.property
    @jsii.member(jsii_name="resourceTypesInput")
    def resource_types_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "resourceTypesInput"))

    @builtins.property
    @jsii.member(jsii_name="tagsInput")
    def tags_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["DataOpentelekomcloudTmsResourceInstancesV1Tags"]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["DataOpentelekomcloudTmsResourceInstancesV1Tags"]]], jsii.get(self, "tagsInput"))

    @builtins.property
    @jsii.member(jsii_name="withoutAnyTagInput")
    def without_any_tag_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "withoutAnyTagInput"))

    @builtins.property
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @id.setter
    def id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ea8b4012d55e3630324d3b589e81dba6a6927ceade58e5a4fd7b9e23435879f4)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "id", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="projectId")
    def project_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "projectId"))

    @project_id.setter
    def project_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__52806c7aada77d1f95cc0173e514c44e9263f50085b7ba9ad77c3841f0861207)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "projectId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="resourceTypes")
    def resource_types(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "resourceTypes"))

    @resource_types.setter
    def resource_types(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7549bf01a2541a51f47b374528ea75ed0e23abaf7a15e3b4dcd4fe50e0f0b7a6)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "resourceTypes", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="withoutAnyTag")
    def without_any_tag(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "withoutAnyTag"))

    @without_any_tag.setter
    def without_any_tag(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__74d20f749ccec42cb4e802f5585572dcdd9994da70c39ded4ed272d9a6b6adc8)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "withoutAnyTag", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-opentelekomcloud.dataOpentelekomcloudTmsResourceInstancesV1.DataOpentelekomcloudTmsResourceInstancesV1Config",
    jsii_struct_bases=[_cdktf_9a9027ec.TerraformMetaArguments],
    name_mapping={
        "connection": "connection",
        "count": "count",
        "depends_on": "dependsOn",
        "for_each": "forEach",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "provisioners": "provisioners",
        "resource_types": "resourceTypes",
        "tags": "tags",
        "id": "id",
        "project_id": "projectId",
        "without_any_tag": "withoutAnyTag",
    },
)
class DataOpentelekomcloudTmsResourceInstancesV1Config(
    _cdktf_9a9027ec.TerraformMetaArguments,
):
    def __init__(
        self,
        *,
        connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
        count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
        depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
        for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
        lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
        provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
        provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
        resource_types: typing.Sequence[builtins.str],
        tags: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["DataOpentelekomcloudTmsResourceInstancesV1Tags", typing.Dict[builtins.str, typing.Any]]]],
        id: typing.Optional[builtins.str] = None,
        project_id: typing.Optional[builtins.str] = None,
        without_any_tag: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    ) -> None:
        '''
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        :param resource_types: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/opentelekomcloud/opentelekomcloud/1.36.46/docs/data-sources/tms_resource_instances_v1#resource_types DataOpentelekomcloudTmsResourceInstancesV1#resource_types}.
        :param tags: tags block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/opentelekomcloud/opentelekomcloud/1.36.46/docs/data-sources/tms_resource_instances_v1#tags DataOpentelekomcloudTmsResourceInstancesV1#tags}
        :param id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/opentelekomcloud/opentelekomcloud/1.36.46/docs/data-sources/tms_resource_instances_v1#id DataOpentelekomcloudTmsResourceInstancesV1#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param project_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/opentelekomcloud/opentelekomcloud/1.36.46/docs/data-sources/tms_resource_instances_v1#project_id DataOpentelekomcloudTmsResourceInstancesV1#project_id}.
        :param without_any_tag: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/opentelekomcloud/opentelekomcloud/1.36.46/docs/data-sources/tms_resource_instances_v1#without_any_tag DataOpentelekomcloudTmsResourceInstancesV1#without_any_tag}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = _cdktf_9a9027ec.TerraformResourceLifecycle(**lifecycle)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e30bb29a4d23e67e019030c4cd4fe40fec3299cb6f5ba2539230b5012f33aaf2)
            check_type(argname="argument connection", value=connection, expected_type=type_hints["connection"])
            check_type(argname="argument count", value=count, expected_type=type_hints["count"])
            check_type(argname="argument depends_on", value=depends_on, expected_type=type_hints["depends_on"])
            check_type(argname="argument for_each", value=for_each, expected_type=type_hints["for_each"])
            check_type(argname="argument lifecycle", value=lifecycle, expected_type=type_hints["lifecycle"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
            check_type(argname="argument provisioners", value=provisioners, expected_type=type_hints["provisioners"])
            check_type(argname="argument resource_types", value=resource_types, expected_type=type_hints["resource_types"])
            check_type(argname="argument tags", value=tags, expected_type=type_hints["tags"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument project_id", value=project_id, expected_type=type_hints["project_id"])
            check_type(argname="argument without_any_tag", value=without_any_tag, expected_type=type_hints["without_any_tag"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "resource_types": resource_types,
            "tags": tags,
        }
        if connection is not None:
            self._values["connection"] = connection
        if count is not None:
            self._values["count"] = count
        if depends_on is not None:
            self._values["depends_on"] = depends_on
        if for_each is not None:
            self._values["for_each"] = for_each
        if lifecycle is not None:
            self._values["lifecycle"] = lifecycle
        if provider is not None:
            self._values["provider"] = provider
        if provisioners is not None:
            self._values["provisioners"] = provisioners
        if id is not None:
            self._values["id"] = id
        if project_id is not None:
            self._values["project_id"] = project_id
        if without_any_tag is not None:
            self._values["without_any_tag"] = without_any_tag

    @builtins.property
    def connection(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, _cdktf_9a9027ec.WinrmProvisionerConnection]]:
        '''
        :stability: experimental
        '''
        result = self._values.get("connection")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, _cdktf_9a9027ec.WinrmProvisionerConnection]], result)

    @builtins.property
    def count(
        self,
    ) -> typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]]:
        '''
        :stability: experimental
        '''
        result = self._values.get("count")
        return typing.cast(typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]], result)

    @builtins.property
    def depends_on(
        self,
    ) -> typing.Optional[typing.List[_cdktf_9a9027ec.ITerraformDependable]]:
        '''
        :stability: experimental
        '''
        result = self._values.get("depends_on")
        return typing.cast(typing.Optional[typing.List[_cdktf_9a9027ec.ITerraformDependable]], result)

    @builtins.property
    def for_each(self) -> typing.Optional[_cdktf_9a9027ec.ITerraformIterator]:
        '''
        :stability: experimental
        '''
        result = self._values.get("for_each")
        return typing.cast(typing.Optional[_cdktf_9a9027ec.ITerraformIterator], result)

    @builtins.property
    def lifecycle(self) -> typing.Optional[_cdktf_9a9027ec.TerraformResourceLifecycle]:
        '''
        :stability: experimental
        '''
        result = self._values.get("lifecycle")
        return typing.cast(typing.Optional[_cdktf_9a9027ec.TerraformResourceLifecycle], result)

    @builtins.property
    def provider(self) -> typing.Optional[_cdktf_9a9027ec.TerraformProvider]:
        '''
        :stability: experimental
        '''
        result = self._values.get("provider")
        return typing.cast(typing.Optional[_cdktf_9a9027ec.TerraformProvider], result)

    @builtins.property
    def provisioners(
        self,
    ) -> typing.Optional[typing.List[typing.Union[_cdktf_9a9027ec.FileProvisioner, _cdktf_9a9027ec.LocalExecProvisioner, _cdktf_9a9027ec.RemoteExecProvisioner]]]:
        '''
        :stability: experimental
        '''
        result = self._values.get("provisioners")
        return typing.cast(typing.Optional[typing.List[typing.Union[_cdktf_9a9027ec.FileProvisioner, _cdktf_9a9027ec.LocalExecProvisioner, _cdktf_9a9027ec.RemoteExecProvisioner]]], result)

    @builtins.property
    def resource_types(self) -> typing.List[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/opentelekomcloud/opentelekomcloud/1.36.46/docs/data-sources/tms_resource_instances_v1#resource_types DataOpentelekomcloudTmsResourceInstancesV1#resource_types}.'''
        result = self._values.get("resource_types")
        assert result is not None, "Required property 'resource_types' is missing"
        return typing.cast(typing.List[builtins.str], result)

    @builtins.property
    def tags(
        self,
    ) -> typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["DataOpentelekomcloudTmsResourceInstancesV1Tags"]]:
        '''tags block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/opentelekomcloud/opentelekomcloud/1.36.46/docs/data-sources/tms_resource_instances_v1#tags DataOpentelekomcloudTmsResourceInstancesV1#tags}
        '''
        result = self._values.get("tags")
        assert result is not None, "Required property 'tags' is missing"
        return typing.cast(typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["DataOpentelekomcloudTmsResourceInstancesV1Tags"]], result)

    @builtins.property
    def id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/opentelekomcloud/opentelekomcloud/1.36.46/docs/data-sources/tms_resource_instances_v1#id DataOpentelekomcloudTmsResourceInstancesV1#id}.

        Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2.
        If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        '''
        result = self._values.get("id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def project_id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/opentelekomcloud/opentelekomcloud/1.36.46/docs/data-sources/tms_resource_instances_v1#project_id DataOpentelekomcloudTmsResourceInstancesV1#project_id}.'''
        result = self._values.get("project_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def without_any_tag(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/opentelekomcloud/opentelekomcloud/1.36.46/docs/data-sources/tms_resource_instances_v1#without_any_tag DataOpentelekomcloudTmsResourceInstancesV1#without_any_tag}.'''
        result = self._values.get("without_any_tag")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataOpentelekomcloudTmsResourceInstancesV1Config(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-opentelekomcloud.dataOpentelekomcloudTmsResourceInstancesV1.DataOpentelekomcloudTmsResourceInstancesV1Resources",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataOpentelekomcloudTmsResourceInstancesV1Resources:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataOpentelekomcloudTmsResourceInstancesV1Resources(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataOpentelekomcloudTmsResourceInstancesV1ResourcesList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-opentelekomcloud.dataOpentelekomcloudTmsResourceInstancesV1.DataOpentelekomcloudTmsResourceInstancesV1ResourcesList",
):
    def __init__(
        self,
        terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
        terraform_attribute: builtins.str,
        wraps_set: builtins.bool,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        :param wraps_set: whether the list is wrapping a set (will add tolist() to be able to access an item via an index).
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__45c690c8cbbf336743b7e1f64b53e2a3860b1d2e3b073400c5ff75f08b04f080)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "DataOpentelekomcloudTmsResourceInstancesV1ResourcesOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0c20ce44b24d85eaa6288912fd209a13e6442e0efa30f6fe47306fd2523a08aa)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("DataOpentelekomcloudTmsResourceInstancesV1ResourcesOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b504db2c333cd52e79a67aea57bc99f38124b5b982a919007a61a4c421c5739f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "terraformAttribute", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="terraformResource")
    def _terraform_resource(self) -> _cdktf_9a9027ec.IInterpolatingParent:
        '''The parent resource.'''
        return typing.cast(_cdktf_9a9027ec.IInterpolatingParent, jsii.get(self, "terraformResource"))

    @_terraform_resource.setter
    def _terraform_resource(self, value: _cdktf_9a9027ec.IInterpolatingParent) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__43f91fda2314d6fac9b2e8cb5f97282e5446351efeb0f39b9961030c4ea28cf8)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "terraformResource", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="wrapsSet")
    def _wraps_set(self) -> builtins.bool:
        '''whether the list is wrapping a set (will add tolist() to be able to access an item via an index).'''
        return typing.cast(builtins.bool, jsii.get(self, "wrapsSet"))

    @_wraps_set.setter
    def _wraps_set(self, value: builtins.bool) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__91d42dd75a686bb5f7406288268252342bc1e4093f2c5866f36e303f01aebd52)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]


class DataOpentelekomcloudTmsResourceInstancesV1ResourcesOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-opentelekomcloud.dataOpentelekomcloudTmsResourceInstancesV1.DataOpentelekomcloudTmsResourceInstancesV1ResourcesOutputReference",
):
    def __init__(
        self,
        terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
        terraform_attribute: builtins.str,
        complex_object_index: jsii.Number,
        complex_object_is_from_set: builtins.bool,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        :param complex_object_index: the index of this item in the list.
        :param complex_object_is_from_set: whether the list is wrapping a set (will add tolist() to be able to access an item via an index).
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c20b28e4d7edfbb586a986caba3b895375327c0b8f76fbe06c4e91615d62f5b8)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @builtins.property
    @jsii.member(jsii_name="projectId")
    def project_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "projectId"))

    @builtins.property
    @jsii.member(jsii_name="projectName")
    def project_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "projectName"))

    @builtins.property
    @jsii.member(jsii_name="resourceId")
    def resource_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "resourceId"))

    @builtins.property
    @jsii.member(jsii_name="resourceName")
    def resource_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "resourceName"))

    @builtins.property
    @jsii.member(jsii_name="resourceType")
    def resource_type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "resourceType"))

    @builtins.property
    @jsii.member(jsii_name="tags")
    def tags(self) -> _cdktf_9a9027ec.StringMap:
        return typing.cast(_cdktf_9a9027ec.StringMap, jsii.get(self, "tags"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[DataOpentelekomcloudTmsResourceInstancesV1Resources]:
        return typing.cast(typing.Optional[DataOpentelekomcloudTmsResourceInstancesV1Resources], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataOpentelekomcloudTmsResourceInstancesV1Resources],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9454097271b2cac9d7023b72cfadcc92203fb0a0c9a9c0737325c7646d55b62c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-opentelekomcloud.dataOpentelekomcloudTmsResourceInstancesV1.DataOpentelekomcloudTmsResourceInstancesV1Tags",
    jsii_struct_bases=[],
    name_mapping={"key": "key", "values": "values"},
)
class DataOpentelekomcloudTmsResourceInstancesV1Tags:
    def __init__(
        self,
        *,
        key: builtins.str,
        values: typing.Sequence[builtins.str],
    ) -> None:
        '''
        :param key: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/opentelekomcloud/opentelekomcloud/1.36.46/docs/data-sources/tms_resource_instances_v1#key DataOpentelekomcloudTmsResourceInstancesV1#key}.
        :param values: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/opentelekomcloud/opentelekomcloud/1.36.46/docs/data-sources/tms_resource_instances_v1#values DataOpentelekomcloudTmsResourceInstancesV1#values}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0113d6b848f31291a45c3c9d44192fe2ea1ddfcadede15686b32a8875f0986d9)
            check_type(argname="argument key", value=key, expected_type=type_hints["key"])
            check_type(argname="argument values", value=values, expected_type=type_hints["values"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "key": key,
            "values": values,
        }

    @builtins.property
    def key(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/opentelekomcloud/opentelekomcloud/1.36.46/docs/data-sources/tms_resource_instances_v1#key DataOpentelekomcloudTmsResourceInstancesV1#key}.'''
        result = self._values.get("key")
        assert result is not None, "Required property 'key' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def values(self) -> typing.List[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/opentelekomcloud/opentelekomcloud/1.36.46/docs/data-sources/tms_resource_instances_v1#values DataOpentelekomcloudTmsResourceInstancesV1#values}.'''
        result = self._values.get("values")
        assert result is not None, "Required property 'values' is missing"
        return typing.cast(typing.List[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataOpentelekomcloudTmsResourceInstancesV1Tags(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataOpentelekomcloudTmsResourceInstancesV1TagsList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-opentelekomcloud.dataOpentelekomcloudTmsResourceInstancesV1.DataOpentelekomcloudTmsResourceInstancesV1TagsList",
):
    def __init__(
        self,
        terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
        terraform_attribute: builtins.str,
        wraps_set: builtins.bool,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        :param wraps_set: whether the list is wrapping a set (will add tolist() to be able to access an item via an index).
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__431f80c36def6e7da4d74f2e913fa87e3d7575e3a0c4cb40530cb9a70d225fe8)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "DataOpentelekomcloudTmsResourceInstancesV1TagsOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__02bb3869f22e244eff64a25733e6780d4b52a6a0e87787a5c1f80e289bd29c33)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("DataOpentelekomcloudTmsResourceInstancesV1TagsOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__113c177c9a34aa037ff9aec9f8d811ab2dfcee3fd7441bfa1f8787d9129189c2)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "terraformAttribute", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="terraformResource")
    def _terraform_resource(self) -> _cdktf_9a9027ec.IInterpolatingParent:
        '''The parent resource.'''
        return typing.cast(_cdktf_9a9027ec.IInterpolatingParent, jsii.get(self, "terraformResource"))

    @_terraform_resource.setter
    def _terraform_resource(self, value: _cdktf_9a9027ec.IInterpolatingParent) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__035a712f9c95857d6a536412065b69216d6eda60ec9a4aee62f4caadf752b69b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "terraformResource", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="wrapsSet")
    def _wraps_set(self) -> builtins.bool:
        '''whether the list is wrapping a set (will add tolist() to be able to access an item via an index).'''
        return typing.cast(builtins.bool, jsii.get(self, "wrapsSet"))

    @_wraps_set.setter
    def _wraps_set(self, value: builtins.bool) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__04bf1bf26984194aad8516b8f63e41cb49eab2e18a7701eb08c48ac4371b2d4a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataOpentelekomcloudTmsResourceInstancesV1Tags]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataOpentelekomcloudTmsResourceInstancesV1Tags]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataOpentelekomcloudTmsResourceInstancesV1Tags]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__658946794d58b949ca073a44256caba0e644efa0f05d631287f590b6562432e1)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class DataOpentelekomcloudTmsResourceInstancesV1TagsOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-opentelekomcloud.dataOpentelekomcloudTmsResourceInstancesV1.DataOpentelekomcloudTmsResourceInstancesV1TagsOutputReference",
):
    def __init__(
        self,
        terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
        terraform_attribute: builtins.str,
        complex_object_index: jsii.Number,
        complex_object_is_from_set: builtins.bool,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        :param complex_object_index: the index of this item in the list.
        :param complex_object_is_from_set: whether the list is wrapping a set (will add tolist() to be able to access an item via an index).
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2a4f2ea99853a1ae1fda9fb2872ad929d5d9d7e2d7b66f0b0560caa5167883e8)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @builtins.property
    @jsii.member(jsii_name="keyInput")
    def key_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "keyInput"))

    @builtins.property
    @jsii.member(jsii_name="valuesInput")
    def values_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "valuesInput"))

    @builtins.property
    @jsii.member(jsii_name="key")
    def key(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "key"))

    @key.setter
    def key(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__087c133433fe79661632cc7081fb61e696f0466b253ffe82aceda1174889cd7e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "key", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="values")
    def values(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "values"))

    @values.setter
    def values(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__73f2f8c366b0b4b18ae4cab5c2eadbb86791908ba7ba1ac21545ab5b98923a3b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "values", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataOpentelekomcloudTmsResourceInstancesV1Tags]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataOpentelekomcloudTmsResourceInstancesV1Tags]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataOpentelekomcloudTmsResourceInstancesV1Tags]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__aace7b1f8f96b958ec6bf7ecd81c757c459e729ff3f38a1fe95adb153d66957d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


__all__ = [
    "DataOpentelekomcloudTmsResourceInstancesV1",
    "DataOpentelekomcloudTmsResourceInstancesV1Config",
    "DataOpentelekomcloudTmsResourceInstancesV1Resources",
    "DataOpentelekomcloudTmsResourceInstancesV1ResourcesList",
    "DataOpentelekomcloudTmsResourceInstancesV1ResourcesOutputReference",
    "DataOpentelekomcloudTmsResourceInstancesV1Tags",
    "DataOpentelekomcloudTmsResourceInstancesV1TagsList",
    "DataOpentelekomcloudTmsResourceInstancesV1TagsOutputReference",
]

publication.publish()

def _typecheckingstub__0273037f3e403e2c6f80fd017018bc120767e3c9eb3b31cdcd76b33a41287993(
    scope: _constructs_77d1e7e8.Construct,
    id_: builtins.str,
    *,
    resource_types: typing.Sequence[builtins.str],
    tags: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[DataOpentelekomcloudTmsResourceInstancesV1Tags, typing.Dict[builtins.str, typing.Any]]]],
    id: typing.Optional[builtins.str] = None,
    project_id: typing.Optional[builtins.str] = None,
    without_any_tag: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
    count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
    depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
    for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
    lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
    provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__46b3991b93090114811a25c5c8a3ba55c8065281a42b0f5edab6ee6b0f8b3d62(
    scope: _constructs_77d1e7e8.Construct,
    import_to_id: builtins.str,
    import_from_id: builtins.str,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__eb4ad03f4550e1f139516bf86dc5cf055909d94ed7dfeeb6640f759cb21a53a2(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[DataOpentelekomcloudTmsResourceInstancesV1Tags, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ea8b4012d55e3630324d3b589e81dba6a6927ceade58e5a4fd7b9e23435879f4(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__52806c7aada77d1f95cc0173e514c44e9263f50085b7ba9ad77c3841f0861207(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7549bf01a2541a51f47b374528ea75ed0e23abaf7a15e3b4dcd4fe50e0f0b7a6(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__74d20f749ccec42cb4e802f5585572dcdd9994da70c39ded4ed272d9a6b6adc8(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e30bb29a4d23e67e019030c4cd4fe40fec3299cb6f5ba2539230b5012f33aaf2(
    *,
    connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
    count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
    depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
    for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
    lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
    provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    resource_types: typing.Sequence[builtins.str],
    tags: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[DataOpentelekomcloudTmsResourceInstancesV1Tags, typing.Dict[builtins.str, typing.Any]]]],
    id: typing.Optional[builtins.str] = None,
    project_id: typing.Optional[builtins.str] = None,
    without_any_tag: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__45c690c8cbbf336743b7e1f64b53e2a3860b1d2e3b073400c5ff75f08b04f080(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0c20ce44b24d85eaa6288912fd209a13e6442e0efa30f6fe47306fd2523a08aa(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b504db2c333cd52e79a67aea57bc99f38124b5b982a919007a61a4c421c5739f(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__43f91fda2314d6fac9b2e8cb5f97282e5446351efeb0f39b9961030c4ea28cf8(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__91d42dd75a686bb5f7406288268252342bc1e4093f2c5866f36e303f01aebd52(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c20b28e4d7edfbb586a986caba3b895375327c0b8f76fbe06c4e91615d62f5b8(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9454097271b2cac9d7023b72cfadcc92203fb0a0c9a9c0737325c7646d55b62c(
    value: typing.Optional[DataOpentelekomcloudTmsResourceInstancesV1Resources],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0113d6b848f31291a45c3c9d44192fe2ea1ddfcadede15686b32a8875f0986d9(
    *,
    key: builtins.str,
    values: typing.Sequence[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__431f80c36def6e7da4d74f2e913fa87e3d7575e3a0c4cb40530cb9a70d225fe8(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__02bb3869f22e244eff64a25733e6780d4b52a6a0e87787a5c1f80e289bd29c33(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__113c177c9a34aa037ff9aec9f8d811ab2dfcee3fd7441bfa1f8787d9129189c2(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__035a712f9c95857d6a536412065b69216d6eda60ec9a4aee62f4caadf752b69b(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__04bf1bf26984194aad8516b8f63e41cb49eab2e18a7701eb08c48ac4371b2d4a(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__658946794d58b949ca073a44256caba0e644efa0f05d631287f590b6562432e1(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataOpentelekomcloudTmsResourceInstancesV1Tags]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2a4f2ea99853a1ae1fda9fb2872ad929d5d9d7e2d7b66f0b0560caa5167883e8(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__087c133433fe79661632cc7081fb61e696f0466b253ffe82aceda1174889cd7e(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__73f2f8c366b0b4b18ae4cab5c2eadbb86791908ba7ba1ac21545ab5b98923a3b(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__aace7b1f8f96b958ec6bf7ecd81c757c459e729ff3f38a1fe95adb153d66957d(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataOpentelekomcloudTmsResourceInstancesV1Tags]],
) -> None:
    """Type checking stubs"""
    pass
