r'''
# CDKTF CDK8s

![Status: Tech Preview](https://img.shields.io/badge/status-experimental-EAAA32) [![Releases](https://img.shields.io/github/release/cdktf/cdktf-cdk8s.svg)](https://github.com/cdktf/cdktf-cdk8s/releases)
[![LICENSE](https://img.shields.io/github/license/cdktf/cdktf-cdk8s.svg)](https://github.com/cdktf/cdktf-cdk8s/blob/main/LICENSE)
[![build](https://github.com/cdktf/cdktf-cdk8s/actions/workflows/build.yml/badge.svg)](https://github.com/cdktf/cdktf-cdk8s/actions/workflows/build.yml)

A compatibility layer for using [cdk8s](https://cdk8s.io/) constructs within Terraform CDK.

The cdk8s adapter is in technical preview, which means it's a community supported project. It still requires extensive testing and polishing to mature into a HashiCorp officially supported project. Please [file issues](https://github.com/cdktf/cdktf-cdk8s/issues/new/choose) generously and detail your experience while using the library. We welcome your feedback.

By using the software in this repository, you acknowledge that:

* The cdk8s adapter is still in development, may change, and has not been released as a commercial product by HashiCorp and is not currently supported in any way by HashiCorp.
* The cdk8s adapter is provided on an "as-is" basis, and may include bugs, errors, or other issues.
* The cdk8s adapter is NOT INTENDED FOR PRODUCTION USE, use of the Software may result in unexpected results, loss of data, or other unexpected results, and HashiCorp disclaims any and all liability resulting from use of the cdk8s adapter.
* HashiCorp reserves all rights to make all decisions about the features, functionality and commercial release (or non-release) of the cdk8s adapter, at any time and without any obligation or liability whatsoever.

## Compatibility

* `cdktf` >= 0.21.0
* `cdk8s` >= 2.8.0
* `constructs` >= 10.4.2

## Usage

```python
import { App, TerraformStack } from "cdktf";
import { App as CDK8sApp, Chart } from "cdk8s";
import { CDK8sProvider } from "cdktf-cdk8s";

import { MyCdk8sChart } from "./my-cdk8s-chart";

export class MyKubernetesStack extends TerraformStack {
  constructor(scope: Construct, name: string) {
    super(scope, name);

    const cdk8sApp = new CDK8sApp();

    // Configure your cdk8s application like usual
    new HelloKube(cdk8sApp, "my-chart");

    // For properties see https://registry.terraform.io/providers/hashicorp/kubernetes/latest/docs
    // Extends on the Provider class from @cdktf/provider-kubernetes
    new CDK8sProvider(this, "cdk8s-dev", {
      configPath: "./kubeconfig.yaml",
      configContext: "my-dev-cluster",

      // Only the cdk8sApp property is added
      // There is no need to run synth on the cdk8sApp, this is done by the provider
      cdk8sApp,
    });
  }
}

const app = new App();
new MyStack(app, "cdktf-cdk8s");
app.synth();
```

## Contributing

We welcome your contribution. Please understand that the experimental nature of this repository means that contributing code may be a bit of a moving target. If you have an idea for an enhancement or bug fix, and want to take on the work yourself, please first [create an issue](https://github.com/cdktf/cdktf-cdk8s/issues/new/choose) so that we can discuss the implementation with you before you proceed with the work.

You can review our [contribution guide](https://github.com/cdktf/.github/blob/main/CONTRIBUTING.md) to begin.
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

import cdk8s as _cdk8s_d3d9af27
import cdktf as _cdktf_9a9027ec
import cdktf_cdktf_provider_kubernetes.provider as _cdktf_cdktf_provider_kubernetes_provider_b14d7399
import constructs as _constructs_77d1e7e8


class CDK8sProvider(
    _cdktf_cdktf_provider_kubernetes_provider_b14d7399.KubernetesProvider,
    metaclass=jsii.JSIIMeta,
    jsii_type="cdktf-cdk8s.CDK8sProvider",
):
    '''
    :stability: experimental
    '''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        cdk8s_app: _cdk8s_d3d9af27.App,
        alias: typing.Optional[builtins.str] = None,
        client_certificate: typing.Optional[builtins.str] = None,
        client_key: typing.Optional[builtins.str] = None,
        cluster_ca_certificate: typing.Optional[builtins.str] = None,
        config_context: typing.Optional[builtins.str] = None,
        config_context_auth_info: typing.Optional[builtins.str] = None,
        config_context_cluster: typing.Optional[builtins.str] = None,
        config_path: typing.Optional[builtins.str] = None,
        config_paths: typing.Optional[typing.Sequence[builtins.str]] = None,
        exec: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[_cdktf_cdktf_provider_kubernetes_provider_b14d7399.KubernetesProviderExec, typing.Dict[builtins.str, typing.Any]]]]] = None,
        experiments: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[_cdktf_cdktf_provider_kubernetes_provider_b14d7399.KubernetesProviderExperiments, typing.Dict[builtins.str, typing.Any]]]]] = None,
        host: typing.Optional[builtins.str] = None,
        ignore_annotations: typing.Optional[typing.Sequence[builtins.str]] = None,
        ignore_labels: typing.Optional[typing.Sequence[builtins.str]] = None,
        insecure: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        password: typing.Optional[builtins.str] = None,
        proxy_url: typing.Optional[builtins.str] = None,
        tls_server_name: typing.Optional[builtins.str] = None,
        token: typing.Optional[builtins.str] = None,
        username: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param cdk8s_app: 
        :param alias: Alias name. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/kubernetes/2.37.1/docs#alias KubernetesProvider#alias}
        :param client_certificate: PEM-encoded client certificate for TLS authentication. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/kubernetes/2.37.1/docs#client_certificate KubernetesProvider#client_certificate}
        :param client_key: PEM-encoded client certificate key for TLS authentication. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/kubernetes/2.37.1/docs#client_key KubernetesProvider#client_key}
        :param cluster_ca_certificate: PEM-encoded root certificates bundle for TLS authentication. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/kubernetes/2.37.1/docs#cluster_ca_certificate KubernetesProvider#cluster_ca_certificate}
        :param config_context: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/kubernetes/2.37.1/docs#config_context KubernetesProvider#config_context}.
        :param config_context_auth_info: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/kubernetes/2.37.1/docs#config_context_auth_info KubernetesProvider#config_context_auth_info}.
        :param config_context_cluster: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/kubernetes/2.37.1/docs#config_context_cluster KubernetesProvider#config_context_cluster}.
        :param config_path: Path to the kube config file. Can be set with KUBE_CONFIG_PATH. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/kubernetes/2.37.1/docs#config_path KubernetesProvider#config_path}
        :param config_paths: A list of paths to kube config files. Can be set with KUBE_CONFIG_PATHS environment variable. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/kubernetes/2.37.1/docs#config_paths KubernetesProvider#config_paths}
        :param exec: exec block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/kubernetes/2.37.1/docs#exec KubernetesProvider#exec}
        :param experiments: experiments block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/kubernetes/2.37.1/docs#experiments KubernetesProvider#experiments}
        :param host: The hostname (in form of URI) of Kubernetes master. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/kubernetes/2.37.1/docs#host KubernetesProvider#host}
        :param ignore_annotations: List of Kubernetes metadata annotations to ignore across all resources handled by this provider for situations where external systems are managing certain resource annotations. Each item is a regular expression. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/kubernetes/2.37.1/docs#ignore_annotations KubernetesProvider#ignore_annotations}
        :param ignore_labels: List of Kubernetes metadata labels to ignore across all resources handled by this provider for situations where external systems are managing certain resource labels. Each item is a regular expression. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/kubernetes/2.37.1/docs#ignore_labels KubernetesProvider#ignore_labels}
        :param insecure: Whether server should be accessed without verifying the TLS certificate. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/kubernetes/2.37.1/docs#insecure KubernetesProvider#insecure}
        :param password: The password to use for HTTP basic authentication when accessing the Kubernetes master endpoint. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/kubernetes/2.37.1/docs#password KubernetesProvider#password}
        :param proxy_url: URL to the proxy to be used for all API requests. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/kubernetes/2.37.1/docs#proxy_url KubernetesProvider#proxy_url}
        :param tls_server_name: Server name passed to the server for SNI and is used in the client to check server certificates against. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/kubernetes/2.37.1/docs#tls_server_name KubernetesProvider#tls_server_name}
        :param token: Token to authenticate an service account. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/kubernetes/2.37.1/docs#token KubernetesProvider#token}
        :param username: The username to use for HTTP basic authentication when accessing the Kubernetes master endpoint. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/kubernetes/2.37.1/docs#username KubernetesProvider#username}

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c1318c333a56de3bcab994349ad716a730c79b7743c7f471bcd586a5025ca0ab)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        config = CDK8sProviderConfig(
            cdk8s_app=cdk8s_app,
            alias=alias,
            client_certificate=client_certificate,
            client_key=client_key,
            cluster_ca_certificate=cluster_ca_certificate,
            config_context=config_context,
            config_context_auth_info=config_context_auth_info,
            config_context_cluster=config_context_cluster,
            config_path=config_path,
            config_paths=config_paths,
            exec=exec,
            experiments=experiments,
            host=host,
            ignore_annotations=ignore_annotations,
            ignore_labels=ignore_labels,
            insecure=insecure,
            password=password,
            proxy_url=proxy_url,
            tls_server_name=tls_server_name,
            token=token,
            username=username,
        )

        jsii.create(self.__class__, self, [scope, id, config])


@jsii.data_type(
    jsii_type="cdktf-cdk8s.CDK8sProviderConfig",
    jsii_struct_bases=[
        _cdktf_cdktf_provider_kubernetes_provider_b14d7399.KubernetesProviderConfig
    ],
    name_mapping={
        "alias": "alias",
        "client_certificate": "clientCertificate",
        "client_key": "clientKey",
        "cluster_ca_certificate": "clusterCaCertificate",
        "config_context": "configContext",
        "config_context_auth_info": "configContextAuthInfo",
        "config_context_cluster": "configContextCluster",
        "config_path": "configPath",
        "config_paths": "configPaths",
        "exec": "exec",
        "experiments": "experiments",
        "host": "host",
        "ignore_annotations": "ignoreAnnotations",
        "ignore_labels": "ignoreLabels",
        "insecure": "insecure",
        "password": "password",
        "proxy_url": "proxyUrl",
        "tls_server_name": "tlsServerName",
        "token": "token",
        "username": "username",
        "cdk8s_app": "cdk8sApp",
    },
)
class CDK8sProviderConfig(
    _cdktf_cdktf_provider_kubernetes_provider_b14d7399.KubernetesProviderConfig,
):
    def __init__(
        self,
        *,
        alias: typing.Optional[builtins.str] = None,
        client_certificate: typing.Optional[builtins.str] = None,
        client_key: typing.Optional[builtins.str] = None,
        cluster_ca_certificate: typing.Optional[builtins.str] = None,
        config_context: typing.Optional[builtins.str] = None,
        config_context_auth_info: typing.Optional[builtins.str] = None,
        config_context_cluster: typing.Optional[builtins.str] = None,
        config_path: typing.Optional[builtins.str] = None,
        config_paths: typing.Optional[typing.Sequence[builtins.str]] = None,
        exec: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[_cdktf_cdktf_provider_kubernetes_provider_b14d7399.KubernetesProviderExec, typing.Dict[builtins.str, typing.Any]]]]] = None,
        experiments: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[_cdktf_cdktf_provider_kubernetes_provider_b14d7399.KubernetesProviderExperiments, typing.Dict[builtins.str, typing.Any]]]]] = None,
        host: typing.Optional[builtins.str] = None,
        ignore_annotations: typing.Optional[typing.Sequence[builtins.str]] = None,
        ignore_labels: typing.Optional[typing.Sequence[builtins.str]] = None,
        insecure: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        password: typing.Optional[builtins.str] = None,
        proxy_url: typing.Optional[builtins.str] = None,
        tls_server_name: typing.Optional[builtins.str] = None,
        token: typing.Optional[builtins.str] = None,
        username: typing.Optional[builtins.str] = None,
        cdk8s_app: _cdk8s_d3d9af27.App,
    ) -> None:
        '''
        :param alias: Alias name. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/kubernetes/2.37.1/docs#alias KubernetesProvider#alias}
        :param client_certificate: PEM-encoded client certificate for TLS authentication. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/kubernetes/2.37.1/docs#client_certificate KubernetesProvider#client_certificate}
        :param client_key: PEM-encoded client certificate key for TLS authentication. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/kubernetes/2.37.1/docs#client_key KubernetesProvider#client_key}
        :param cluster_ca_certificate: PEM-encoded root certificates bundle for TLS authentication. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/kubernetes/2.37.1/docs#cluster_ca_certificate KubernetesProvider#cluster_ca_certificate}
        :param config_context: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/kubernetes/2.37.1/docs#config_context KubernetesProvider#config_context}.
        :param config_context_auth_info: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/kubernetes/2.37.1/docs#config_context_auth_info KubernetesProvider#config_context_auth_info}.
        :param config_context_cluster: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/kubernetes/2.37.1/docs#config_context_cluster KubernetesProvider#config_context_cluster}.
        :param config_path: Path to the kube config file. Can be set with KUBE_CONFIG_PATH. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/kubernetes/2.37.1/docs#config_path KubernetesProvider#config_path}
        :param config_paths: A list of paths to kube config files. Can be set with KUBE_CONFIG_PATHS environment variable. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/kubernetes/2.37.1/docs#config_paths KubernetesProvider#config_paths}
        :param exec: exec block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/kubernetes/2.37.1/docs#exec KubernetesProvider#exec}
        :param experiments: experiments block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/kubernetes/2.37.1/docs#experiments KubernetesProvider#experiments}
        :param host: The hostname (in form of URI) of Kubernetes master. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/kubernetes/2.37.1/docs#host KubernetesProvider#host}
        :param ignore_annotations: List of Kubernetes metadata annotations to ignore across all resources handled by this provider for situations where external systems are managing certain resource annotations. Each item is a regular expression. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/kubernetes/2.37.1/docs#ignore_annotations KubernetesProvider#ignore_annotations}
        :param ignore_labels: List of Kubernetes metadata labels to ignore across all resources handled by this provider for situations where external systems are managing certain resource labels. Each item is a regular expression. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/kubernetes/2.37.1/docs#ignore_labels KubernetesProvider#ignore_labels}
        :param insecure: Whether server should be accessed without verifying the TLS certificate. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/kubernetes/2.37.1/docs#insecure KubernetesProvider#insecure}
        :param password: The password to use for HTTP basic authentication when accessing the Kubernetes master endpoint. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/kubernetes/2.37.1/docs#password KubernetesProvider#password}
        :param proxy_url: URL to the proxy to be used for all API requests. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/kubernetes/2.37.1/docs#proxy_url KubernetesProvider#proxy_url}
        :param tls_server_name: Server name passed to the server for SNI and is used in the client to check server certificates against. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/kubernetes/2.37.1/docs#tls_server_name KubernetesProvider#tls_server_name}
        :param token: Token to authenticate an service account. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/kubernetes/2.37.1/docs#token KubernetesProvider#token}
        :param username: The username to use for HTTP basic authentication when accessing the Kubernetes master endpoint. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/kubernetes/2.37.1/docs#username KubernetesProvider#username}
        :param cdk8s_app: 

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__eca8720f2b770ba7124f7697d37cde3f0db7c9415eb821ddccf066e9fa5cec5c)
            check_type(argname="argument alias", value=alias, expected_type=type_hints["alias"])
            check_type(argname="argument client_certificate", value=client_certificate, expected_type=type_hints["client_certificate"])
            check_type(argname="argument client_key", value=client_key, expected_type=type_hints["client_key"])
            check_type(argname="argument cluster_ca_certificate", value=cluster_ca_certificate, expected_type=type_hints["cluster_ca_certificate"])
            check_type(argname="argument config_context", value=config_context, expected_type=type_hints["config_context"])
            check_type(argname="argument config_context_auth_info", value=config_context_auth_info, expected_type=type_hints["config_context_auth_info"])
            check_type(argname="argument config_context_cluster", value=config_context_cluster, expected_type=type_hints["config_context_cluster"])
            check_type(argname="argument config_path", value=config_path, expected_type=type_hints["config_path"])
            check_type(argname="argument config_paths", value=config_paths, expected_type=type_hints["config_paths"])
            check_type(argname="argument exec", value=exec, expected_type=type_hints["exec"])
            check_type(argname="argument experiments", value=experiments, expected_type=type_hints["experiments"])
            check_type(argname="argument host", value=host, expected_type=type_hints["host"])
            check_type(argname="argument ignore_annotations", value=ignore_annotations, expected_type=type_hints["ignore_annotations"])
            check_type(argname="argument ignore_labels", value=ignore_labels, expected_type=type_hints["ignore_labels"])
            check_type(argname="argument insecure", value=insecure, expected_type=type_hints["insecure"])
            check_type(argname="argument password", value=password, expected_type=type_hints["password"])
            check_type(argname="argument proxy_url", value=proxy_url, expected_type=type_hints["proxy_url"])
            check_type(argname="argument tls_server_name", value=tls_server_name, expected_type=type_hints["tls_server_name"])
            check_type(argname="argument token", value=token, expected_type=type_hints["token"])
            check_type(argname="argument username", value=username, expected_type=type_hints["username"])
            check_type(argname="argument cdk8s_app", value=cdk8s_app, expected_type=type_hints["cdk8s_app"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "cdk8s_app": cdk8s_app,
        }
        if alias is not None:
            self._values["alias"] = alias
        if client_certificate is not None:
            self._values["client_certificate"] = client_certificate
        if client_key is not None:
            self._values["client_key"] = client_key
        if cluster_ca_certificate is not None:
            self._values["cluster_ca_certificate"] = cluster_ca_certificate
        if config_context is not None:
            self._values["config_context"] = config_context
        if config_context_auth_info is not None:
            self._values["config_context_auth_info"] = config_context_auth_info
        if config_context_cluster is not None:
            self._values["config_context_cluster"] = config_context_cluster
        if config_path is not None:
            self._values["config_path"] = config_path
        if config_paths is not None:
            self._values["config_paths"] = config_paths
        if exec is not None:
            self._values["exec"] = exec
        if experiments is not None:
            self._values["experiments"] = experiments
        if host is not None:
            self._values["host"] = host
        if ignore_annotations is not None:
            self._values["ignore_annotations"] = ignore_annotations
        if ignore_labels is not None:
            self._values["ignore_labels"] = ignore_labels
        if insecure is not None:
            self._values["insecure"] = insecure
        if password is not None:
            self._values["password"] = password
        if proxy_url is not None:
            self._values["proxy_url"] = proxy_url
        if tls_server_name is not None:
            self._values["tls_server_name"] = tls_server_name
        if token is not None:
            self._values["token"] = token
        if username is not None:
            self._values["username"] = username

    @builtins.property
    def alias(self) -> typing.Optional[builtins.str]:
        '''Alias name.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/kubernetes/2.37.1/docs#alias KubernetesProvider#alias}
        '''
        result = self._values.get("alias")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def client_certificate(self) -> typing.Optional[builtins.str]:
        '''PEM-encoded client certificate for TLS authentication.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/kubernetes/2.37.1/docs#client_certificate KubernetesProvider#client_certificate}
        '''
        result = self._values.get("client_certificate")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def client_key(self) -> typing.Optional[builtins.str]:
        '''PEM-encoded client certificate key for TLS authentication.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/kubernetes/2.37.1/docs#client_key KubernetesProvider#client_key}
        '''
        result = self._values.get("client_key")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def cluster_ca_certificate(self) -> typing.Optional[builtins.str]:
        '''PEM-encoded root certificates bundle for TLS authentication.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/kubernetes/2.37.1/docs#cluster_ca_certificate KubernetesProvider#cluster_ca_certificate}
        '''
        result = self._values.get("cluster_ca_certificate")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def config_context(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/kubernetes/2.37.1/docs#config_context KubernetesProvider#config_context}.'''
        result = self._values.get("config_context")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def config_context_auth_info(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/kubernetes/2.37.1/docs#config_context_auth_info KubernetesProvider#config_context_auth_info}.'''
        result = self._values.get("config_context_auth_info")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def config_context_cluster(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/kubernetes/2.37.1/docs#config_context_cluster KubernetesProvider#config_context_cluster}.'''
        result = self._values.get("config_context_cluster")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def config_path(self) -> typing.Optional[builtins.str]:
        '''Path to the kube config file. Can be set with KUBE_CONFIG_PATH.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/kubernetes/2.37.1/docs#config_path KubernetesProvider#config_path}
        '''
        result = self._values.get("config_path")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def config_paths(self) -> typing.Optional[typing.List[builtins.str]]:
        '''A list of paths to kube config files. Can be set with KUBE_CONFIG_PATHS environment variable.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/kubernetes/2.37.1/docs#config_paths KubernetesProvider#config_paths}
        '''
        result = self._values.get("config_paths")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def exec(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[_cdktf_cdktf_provider_kubernetes_provider_b14d7399.KubernetesProviderExec]]]:
        '''exec block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/kubernetes/2.37.1/docs#exec KubernetesProvider#exec}
        '''
        result = self._values.get("exec")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[_cdktf_cdktf_provider_kubernetes_provider_b14d7399.KubernetesProviderExec]]], result)

    @builtins.property
    def experiments(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[_cdktf_cdktf_provider_kubernetes_provider_b14d7399.KubernetesProviderExperiments]]]:
        '''experiments block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/kubernetes/2.37.1/docs#experiments KubernetesProvider#experiments}
        '''
        result = self._values.get("experiments")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[_cdktf_cdktf_provider_kubernetes_provider_b14d7399.KubernetesProviderExperiments]]], result)

    @builtins.property
    def host(self) -> typing.Optional[builtins.str]:
        '''The hostname (in form of URI) of Kubernetes master.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/kubernetes/2.37.1/docs#host KubernetesProvider#host}
        '''
        result = self._values.get("host")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def ignore_annotations(self) -> typing.Optional[typing.List[builtins.str]]:
        '''List of Kubernetes metadata annotations to ignore across all resources handled by this provider for situations where external systems are managing certain resource annotations.

        Each item is a regular expression.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/kubernetes/2.37.1/docs#ignore_annotations KubernetesProvider#ignore_annotations}
        '''
        result = self._values.get("ignore_annotations")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def ignore_labels(self) -> typing.Optional[typing.List[builtins.str]]:
        '''List of Kubernetes metadata labels to ignore across all resources handled by this provider for situations where external systems are managing certain resource labels.

        Each item is a regular expression.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/kubernetes/2.37.1/docs#ignore_labels KubernetesProvider#ignore_labels}
        '''
        result = self._values.get("ignore_labels")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def insecure(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Whether server should be accessed without verifying the TLS certificate.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/kubernetes/2.37.1/docs#insecure KubernetesProvider#insecure}
        '''
        result = self._values.get("insecure")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def password(self) -> typing.Optional[builtins.str]:
        '''The password to use for HTTP basic authentication when accessing the Kubernetes master endpoint.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/kubernetes/2.37.1/docs#password KubernetesProvider#password}
        '''
        result = self._values.get("password")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def proxy_url(self) -> typing.Optional[builtins.str]:
        '''URL to the proxy to be used for all API requests.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/kubernetes/2.37.1/docs#proxy_url KubernetesProvider#proxy_url}
        '''
        result = self._values.get("proxy_url")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def tls_server_name(self) -> typing.Optional[builtins.str]:
        '''Server name passed to the server for SNI and is used in the client to check server certificates against.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/kubernetes/2.37.1/docs#tls_server_name KubernetesProvider#tls_server_name}
        '''
        result = self._values.get("tls_server_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def token(self) -> typing.Optional[builtins.str]:
        '''Token to authenticate an service account.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/kubernetes/2.37.1/docs#token KubernetesProvider#token}
        '''
        result = self._values.get("token")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def username(self) -> typing.Optional[builtins.str]:
        '''The username to use for HTTP basic authentication when accessing the Kubernetes master endpoint.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/kubernetes/2.37.1/docs#username KubernetesProvider#username}
        '''
        result = self._values.get("username")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def cdk8s_app(self) -> _cdk8s_d3d9af27.App:
        '''
        :stability: experimental
        '''
        result = self._values.get("cdk8s_app")
        assert result is not None, "Required property 'cdk8s_app' is missing"
        return typing.cast(_cdk8s_d3d9af27.App, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CDK8sProviderConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "CDK8sProvider",
    "CDK8sProviderConfig",
]

publication.publish()

def _typecheckingstub__c1318c333a56de3bcab994349ad716a730c79b7743c7f471bcd586a5025ca0ab(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    cdk8s_app: _cdk8s_d3d9af27.App,
    alias: typing.Optional[builtins.str] = None,
    client_certificate: typing.Optional[builtins.str] = None,
    client_key: typing.Optional[builtins.str] = None,
    cluster_ca_certificate: typing.Optional[builtins.str] = None,
    config_context: typing.Optional[builtins.str] = None,
    config_context_auth_info: typing.Optional[builtins.str] = None,
    config_context_cluster: typing.Optional[builtins.str] = None,
    config_path: typing.Optional[builtins.str] = None,
    config_paths: typing.Optional[typing.Sequence[builtins.str]] = None,
    exec: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[_cdktf_cdktf_provider_kubernetes_provider_b14d7399.KubernetesProviderExec, typing.Dict[builtins.str, typing.Any]]]]] = None,
    experiments: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[_cdktf_cdktf_provider_kubernetes_provider_b14d7399.KubernetesProviderExperiments, typing.Dict[builtins.str, typing.Any]]]]] = None,
    host: typing.Optional[builtins.str] = None,
    ignore_annotations: typing.Optional[typing.Sequence[builtins.str]] = None,
    ignore_labels: typing.Optional[typing.Sequence[builtins.str]] = None,
    insecure: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    password: typing.Optional[builtins.str] = None,
    proxy_url: typing.Optional[builtins.str] = None,
    tls_server_name: typing.Optional[builtins.str] = None,
    token: typing.Optional[builtins.str] = None,
    username: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__eca8720f2b770ba7124f7697d37cde3f0db7c9415eb821ddccf066e9fa5cec5c(
    *,
    alias: typing.Optional[builtins.str] = None,
    client_certificate: typing.Optional[builtins.str] = None,
    client_key: typing.Optional[builtins.str] = None,
    cluster_ca_certificate: typing.Optional[builtins.str] = None,
    config_context: typing.Optional[builtins.str] = None,
    config_context_auth_info: typing.Optional[builtins.str] = None,
    config_context_cluster: typing.Optional[builtins.str] = None,
    config_path: typing.Optional[builtins.str] = None,
    config_paths: typing.Optional[typing.Sequence[builtins.str]] = None,
    exec: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[_cdktf_cdktf_provider_kubernetes_provider_b14d7399.KubernetesProviderExec, typing.Dict[builtins.str, typing.Any]]]]] = None,
    experiments: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[_cdktf_cdktf_provider_kubernetes_provider_b14d7399.KubernetesProviderExperiments, typing.Dict[builtins.str, typing.Any]]]]] = None,
    host: typing.Optional[builtins.str] = None,
    ignore_annotations: typing.Optional[typing.Sequence[builtins.str]] = None,
    ignore_labels: typing.Optional[typing.Sequence[builtins.str]] = None,
    insecure: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    password: typing.Optional[builtins.str] = None,
    proxy_url: typing.Optional[builtins.str] = None,
    tls_server_name: typing.Optional[builtins.str] = None,
    token: typing.Optional[builtins.str] = None,
    username: typing.Optional[builtins.str] = None,
    cdk8s_app: _cdk8s_d3d9af27.App,
) -> None:
    """Type checking stubs"""
    pass
