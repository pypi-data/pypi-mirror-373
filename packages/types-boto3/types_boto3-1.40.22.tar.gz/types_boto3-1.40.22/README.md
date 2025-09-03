<a id="types-boto3"></a>

# types-boto3

[![PyPI - types-boto3](https://img.shields.io/pypi/v/types-boto3.svg?color=blue)](https://pypi.org/project/types-boto3/)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/types-boto3.svg?color=blue)](https://pypi.org/project/types-boto3/)
[![Docs](https://img.shields.io/readthedocs/boto3-stubs.svg?color=blue)](https://youtype.github.io/types_boto3_docs/)
[![PyPI - Downloads](https://static.pepy.tech/badge/types-boto3)](https://pypistats.org/packages/types-boto3)

![boto3.typed](https://github.com/youtype/mypy_boto3_builder/raw/main/logo.png)

Type annotations for [boto3 1.40.22](https://pypi.org/project/boto3/)
compatible with [VSCode](https://code.visualstudio.com/),
[PyCharm](https://www.jetbrains.com/pycharm/),
[Emacs](https://www.gnu.org/software/emacs/),
[Sublime Text](https://www.sublimetext.com/),
[mypy](https://github.com/python/mypy),
[pyright](https://github.com/microsoft/pyright) and other tools.

Generated with
[mypy-boto3-builder 8.11.0](https://github.com/youtype/mypy_boto3_builder).

More information can be found in
[types-boto3 docs](https://youtype.github.io/types_boto3_docs/).

See how it helps you find and fix potential bugs:

![types-boto3 demo](https://github.com/youtype/mypy_boto3_builder/raw/main/demo.gif)

- [types-boto3](#types-boto3)
  - [How to install](#how-to-install)
    - [Generate locally (recommended)](<#generate-locally-(recommended)>)
    - [VSCode extension](#vscode-extension)
    - [From PyPI with pip](#from-pypi-with-pip)
  - [How to uninstall](#how-to-uninstall)
  - [Usage](#usage)
    - [VSCode](#vscode)
    - [PyCharm](#pycharm)
    - [Emacs](#emacs)
    - [Sublime Text](#sublime-text)
    - [Other IDEs](#other-ides)
    - [mypy](#mypy)
    - [pyright](#pyright)
    - [Pylint compatibility](#pylint-compatibility)
    - [Explicit type annotations](#explicit-type-annotations)
  - [How it works](#how-it-works)
  - [What's new](#what's-new)
    - [Implemented features](#implemented-features)
    - [Latest changes](#latest-changes)
  - [Versioning](#versioning)
  - [Thank you](#thank-you)
  - [Documentation](#documentation)
  - [Support and contributing](#support-and-contributing)
  - [Submodules](#submodules)

<a id="how-to-install"></a>

## How to install

<a id="generate-locally-(recommended)"></a>

### Generate locally (recommended)

You can generate type annotations for `boto3` package locally with
`mypy-boto3-builder`. Use
[uv](https://docs.astral.sh/uv/getting-started/installation/) for build
isolation.

1. Run mypy-boto3-builder in your package root directory:
   `uvx --with 'boto3==1.40.22' mypy-boto3-builder`
2. Select `boto3` AWS SDK.
3. Select services you use in the current project.
4. Use provided commands to install generated packages.

<a id="vscode-extension"></a>

### VSCode extension

Add
[AWS Boto3](https://marketplace.visualstudio.com/items?itemName=Boto3typed.boto3-ide)
extension to your VSCode and run `AWS boto3: Quick Start` command.

Click `Auto-discover services` and select services you use in the current
project.

<a id="from-pypi-with-pip"></a>

### From PyPI with pip

Install `types-boto3` to add type checking for `boto3` package.

```bash
# install type annotations only for boto3
python -m pip install types-boto3

# install boto3 type annotations
# for cloudformation, dynamodb, ec2, lambda, rds, s3, sqs
python -m pip install 'types-boto3[essential]'

# or install annotations for services you use
python -m pip install 'types-boto3[acm,apigateway]'

# or install annotations in sync with boto3 version
python -m pip install 'types-boto3[boto3]'

# or install all-in-one annotations for all services
python -m pip install 'types-boto3[full]'

# Lite version does not provide session.client/resource overloads
# it is more RAM-friendly, but requires explicit type annotations
python -m pip install 'types-boto3-lite[essential]'
```

<a id="how-to-uninstall"></a>

## How to uninstall

```bash
# uninstall types-boto3
python -m pip uninstall -y types-boto3
```

<a id="usage"></a>

## Usage

<a id="vscode"></a>

### VSCode

- Install
  [Python extension](https://marketplace.visualstudio.com/items?itemName=ms-python.python)
- Install
  [Pylance extension](https://marketplace.visualstudio.com/items?itemName=ms-python.vscode-pylance)
- Set `Pylance` as your Python Language Server
- Install `types-boto3[essential]` in your environment:

```bash
python -m pip install 'types-boto3[essential]'
```

Both type checking and code completion should now work. No explicit type
annotations required, write your `boto3` code as usual.

<a id="pycharm"></a>

### PyCharm

> ⚠️ Due to slow PyCharm performance on `Literal` overloads (issue
> [PY-40997](https://youtrack.jetbrains.com/issue/PY-40997)), it is recommended
> to use [types-boto3-lite](https://pypi.org/project/types-boto3-lite/) until
> the issue is resolved.

> ⚠️ If you experience slow performance and high CPU usage, try to disable
> `PyCharm` type checker and use [mypy](https://github.com/python/mypy) or
> [pyright](https://github.com/microsoft/pyright) instead.

> ⚠️ To continue using `PyCharm` type checker, you can try to replace
> `types-boto3` with
> [types-boto3-lite](https://pypi.org/project/types-boto3-lite/):

```bash
pip uninstall types-boto3
pip install types-boto3-lite
```

Install `types-boto3[essential]` in your environment:

```bash
python -m pip install 'types-boto3[essential]'
```

Both type checking and code completion should now work.

<a id="emacs"></a>

### Emacs

- Install `types-boto3` with services you use in your environment:

```bash
python -m pip install 'types-boto3[essential]'
```

- Install [use-package](https://github.com/jwiegley/use-package),
  [lsp](https://github.com/emacs-lsp/lsp-mode/),
  [company](https://github.com/company-mode/company-mode) and
  [flycheck](https://github.com/flycheck/flycheck) packages
- Install [lsp-pyright](https://github.com/emacs-lsp/lsp-pyright) package

```elisp
(use-package lsp-pyright
  :ensure t
  :hook (python-mode . (lambda ()
                          (require 'lsp-pyright)
                          (lsp)))  ; or lsp-deferred
  :init (when (executable-find "python3")
          (setq lsp-pyright-python-executable-cmd "python3"))
  )
```

- Make sure emacs uses the environment where you have installed `types-boto3`

Type checking should now work. No explicit type annotations required, write
your `boto3` code as usual.

<a id="sublime-text"></a>

### Sublime Text

- Install `types-boto3[essential]` with services you use in your environment:

```bash
python -m pip install 'types-boto3[essential]'
```

- Install [LSP-pyright](https://github.com/sublimelsp/LSP-pyright) package

Type checking should now work. No explicit type annotations required, write
your `boto3` code as usual.

<a id="other-ides"></a>

### Other IDEs

Not tested, but as long as your IDE supports `mypy` or `pyright`, everything
should work.

<a id="mypy"></a>

### mypy

- Install `mypy`: `python -m pip install mypy`
- Install `types-boto3[essential]` in your environment:

```bash
python -m pip install 'types-boto3[essential]'
```

Type checking should now work. No explicit type annotations required, write
your `boto3` code as usual.

<a id="pyright"></a>

### pyright

- Install `pyright`: `npm i -g pyright`
- Install `types-boto3[essential]` in your environment:

```bash
python -m pip install 'types-boto3[essential]'
```

Optionally, you can install `types-boto3` to `typings` directory.

Type checking should now work. No explicit type annotations required, write
your `boto3` code as usual.

<a id="pylint-compatibility"></a>

### Pylint compatibility

It is totally safe to use `TYPE_CHECKING` flag in order to avoid `types-boto3`
dependency in production. However, there is an issue in `pylint` that it
complains about undefined variables. To fix it, set all types to `object` in
non-`TYPE_CHECKING` mode.

```python
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from types_boto3_ec2 import EC2Client, EC2ServiceResource
    from types_boto3_ec2.waiters import BundleTaskCompleteWaiter
    from types_boto3_ec2.paginators import DescribeVolumesPaginator
else:
    EC2Client = object
    EC2ServiceResource = object
    BundleTaskCompleteWaiter = object
    DescribeVolumesPaginator = object

...
```

<a id="explicit-type-annotations"></a>

### Explicit type annotations

To speed up type checking and code completion, you can set types explicitly.

```python
import boto3
from boto3.session import Session

from types_boto3_ec2.client import EC2Client
from types_boto3_ec2.service_resource import EC2ServiceResource
from types_boto3_ec2.waiter import BundleTaskCompleteWaiter
from types_boto3_ec2.paginator import DescribeVolumesPaginator

session = Session(region_name="us-west-1")

ec2_client: EC2Client = boto3.client("ec2", region_name="us-west-1")
ec2_resource: EC2ServiceResource = session.resource("ec2")

bundle_task_complete_waiter: BundleTaskCompleteWaiter = ec2_client.get_waiter(
    "bundle_task_complete"
)
describe_volumes_paginator: DescribeVolumesPaginator = ec2_client.get_paginator("describe_volumes")
```

<a id="how-it-works"></a>

## How it works

Fully automated
[mypy-boto3-builder](https://github.com/youtype/mypy_boto3_builder) carefully
generates type annotations for each service, patiently waiting for `boto3`
updates. It delivers drop-in type annotations for you and makes sure that:

- All available `boto3` services are covered.
- Each public class and method of every `boto3` service gets valid type
  annotations extracted from `botocore` schemas.
- Type annotations include up-to-date documentation.
- Link to documentation is provided for every method.
- Code is processed by [ruff](https://docs.astral.sh/ruff/) for readability.

<a id="what's-new"></a>

## What's new

<a id="implemented-features"></a>

### Implemented features

- Fully type annotated `boto3`, `botocore`, `aiobotocore` and `aioboto3`
  libraries
- `mypy`, `pyright`, `VSCode`, `PyCharm`, `Sublime Text` and `Emacs`
  compatibility
- `Client`, `ServiceResource`, `Resource`, `Waiter` `Paginator` type
  annotations for each service
- Generated `TypeDefs` for each service
- Generated `Literals` for each service
- Auto discovery of types for `boto3.client` and `boto3.resource` calls
- Auto discovery of types for `session.client` and `session.resource` calls
- Auto discovery of types for `client.get_waiter` and `client.get_paginator`
  calls
- Auto discovery of types for `ServiceResource` and `Resource` collections
- Auto discovery of types for `aiobotocore.Session.create_client` calls

<a id="latest-changes"></a>

### Latest changes

Builder changelog can be found in
[Releases](https://github.com/youtype/mypy_boto3_builder/releases).

<a id="versioning"></a>

## Versioning

`types-boto3` version is the same as related `boto3` version and follows
[Python Packaging version specifiers](https://packaging.python.org/en/latest/specifications/version-specifiers/).

<a id="thank-you"></a>

## Thank you

- [Allie Fitter](https://github.com/alliefitter) for
  [boto3-type-annotations](https://pypi.org/project/boto3-type-annotations/),
  this package is based on top of his work
- [black](https://github.com/psf/black) developers for an awesome formatting
  tool
- [Timothy Edmund Crosley](https://github.com/timothycrosley) for
  [isort](https://github.com/PyCQA/isort) and how flexible it is
- [mypy](https://github.com/python/mypy) developers for doing all dirty work
  for us
- [pyright](https://github.com/microsoft/pyright) team for the new era of typed
  Python

<a id="documentation"></a>

## Documentation

All services type annotations can be found in
[boto3 docs](https://youtype.github.io/types_boto3_docs/)

<a id="support-and-contributing"></a>

## Support and contributing

This package is auto-generated. Please reports any bugs or request new features
in [mypy-boto3-builder](https://github.com/youtype/mypy_boto3_builder/issues/)
repository.

<a id="submodules"></a>

## Submodules

- `types-boto3[full]` - Type annotations for all 413 services in one package
  (recommended).
- `types-boto3[all]` - Type annotations for all 413 services in separate
  packages.
- `types-boto3[essential]` - Type annotations for
  [CloudFormation](https://youtype.github.io/types_boto3_docs/types_boto3_cloudformation/),
  [DynamoDB](https://youtype.github.io/types_boto3_docs/types_boto3_dynamodb/),
  [EC2](https://youtype.github.io/types_boto3_docs/types_boto3_ec2/),
  [Lambda](https://youtype.github.io/types_boto3_docs/types_boto3_lambda/),
  [RDS](https://youtype.github.io/types_boto3_docs/types_boto3_rds/),
  [S3](https://youtype.github.io/types_boto3_docs/types_boto3_s3/) and
  [SQS](https://youtype.github.io/types_boto3_docs/types_boto3_sqs/) services.
- `types-boto3[boto3]` - Install annotations in sync with `boto3` version.
- `types-boto3[accessanalyzer]` - Type annotations for
  [AccessAnalyzer](https://youtype.github.io/types_boto3_docs/types_boto3_accessanalyzer/)
  service.
- `types-boto3[account]` - Type annotations for
  [Account](https://youtype.github.io/types_boto3_docs/types_boto3_account/)
  service.
- `types-boto3[acm]` - Type annotations for
  [ACM](https://youtype.github.io/types_boto3_docs/types_boto3_acm/) service.
- `types-boto3[acm-pca]` - Type annotations for
  [ACMPCA](https://youtype.github.io/types_boto3_docs/types_boto3_acm_pca/)
  service.
- `types-boto3[aiops]` - Type annotations for
  [AIOps](https://youtype.github.io/types_boto3_docs/types_boto3_aiops/)
  service.
- `types-boto3[amp]` - Type annotations for
  [PrometheusService](https://youtype.github.io/types_boto3_docs/types_boto3_amp/)
  service.
- `types-boto3[amplify]` - Type annotations for
  [Amplify](https://youtype.github.io/types_boto3_docs/types_boto3_amplify/)
  service.
- `types-boto3[amplifybackend]` - Type annotations for
  [AmplifyBackend](https://youtype.github.io/types_boto3_docs/types_boto3_amplifybackend/)
  service.
- `types-boto3[amplifyuibuilder]` - Type annotations for
  [AmplifyUIBuilder](https://youtype.github.io/types_boto3_docs/types_boto3_amplifyuibuilder/)
  service.
- `types-boto3[apigateway]` - Type annotations for
  [APIGateway](https://youtype.github.io/types_boto3_docs/types_boto3_apigateway/)
  service.
- `types-boto3[apigatewaymanagementapi]` - Type annotations for
  [ApiGatewayManagementApi](https://youtype.github.io/types_boto3_docs/types_boto3_apigatewaymanagementapi/)
  service.
- `types-boto3[apigatewayv2]` - Type annotations for
  [ApiGatewayV2](https://youtype.github.io/types_boto3_docs/types_boto3_apigatewayv2/)
  service.
- `types-boto3[appconfig]` - Type annotations for
  [AppConfig](https://youtype.github.io/types_boto3_docs/types_boto3_appconfig/)
  service.
- `types-boto3[appconfigdata]` - Type annotations for
  [AppConfigData](https://youtype.github.io/types_boto3_docs/types_boto3_appconfigdata/)
  service.
- `types-boto3[appfabric]` - Type annotations for
  [AppFabric](https://youtype.github.io/types_boto3_docs/types_boto3_appfabric/)
  service.
- `types-boto3[appflow]` - Type annotations for
  [Appflow](https://youtype.github.io/types_boto3_docs/types_boto3_appflow/)
  service.
- `types-boto3[appintegrations]` - Type annotations for
  [AppIntegrationsService](https://youtype.github.io/types_boto3_docs/types_boto3_appintegrations/)
  service.
- `types-boto3[application-autoscaling]` - Type annotations for
  [ApplicationAutoScaling](https://youtype.github.io/types_boto3_docs/types_boto3_application_autoscaling/)
  service.
- `types-boto3[application-insights]` - Type annotations for
  [ApplicationInsights](https://youtype.github.io/types_boto3_docs/types_boto3_application_insights/)
  service.
- `types-boto3[application-signals]` - Type annotations for
  [CloudWatchApplicationSignals](https://youtype.github.io/types_boto3_docs/types_boto3_application_signals/)
  service.
- `types-boto3[applicationcostprofiler]` - Type annotations for
  [ApplicationCostProfiler](https://youtype.github.io/types_boto3_docs/types_boto3_applicationcostprofiler/)
  service.
- `types-boto3[appmesh]` - Type annotations for
  [AppMesh](https://youtype.github.io/types_boto3_docs/types_boto3_appmesh/)
  service.
- `types-boto3[apprunner]` - Type annotations for
  [AppRunner](https://youtype.github.io/types_boto3_docs/types_boto3_apprunner/)
  service.
- `types-boto3[appstream]` - Type annotations for
  [AppStream](https://youtype.github.io/types_boto3_docs/types_boto3_appstream/)
  service.
- `types-boto3[appsync]` - Type annotations for
  [AppSync](https://youtype.github.io/types_boto3_docs/types_boto3_appsync/)
  service.
- `types-boto3[apptest]` - Type annotations for
  [MainframeModernizationApplicationTesting](https://youtype.github.io/types_boto3_docs/types_boto3_apptest/)
  service.
- `types-boto3[arc-region-switch]` - Type annotations for
  [ARCRegionswitch](https://youtype.github.io/types_boto3_docs/types_boto3_arc_region_switch/)
  service.
- `types-boto3[arc-zonal-shift]` - Type annotations for
  [ARCZonalShift](https://youtype.github.io/types_boto3_docs/types_boto3_arc_zonal_shift/)
  service.
- `types-boto3[artifact]` - Type annotations for
  [Artifact](https://youtype.github.io/types_boto3_docs/types_boto3_artifact/)
  service.
- `types-boto3[athena]` - Type annotations for
  [Athena](https://youtype.github.io/types_boto3_docs/types_boto3_athena/)
  service.
- `types-boto3[auditmanager]` - Type annotations for
  [AuditManager](https://youtype.github.io/types_boto3_docs/types_boto3_auditmanager/)
  service.
- `types-boto3[autoscaling]` - Type annotations for
  [AutoScaling](https://youtype.github.io/types_boto3_docs/types_boto3_autoscaling/)
  service.
- `types-boto3[autoscaling-plans]` - Type annotations for
  [AutoScalingPlans](https://youtype.github.io/types_boto3_docs/types_boto3_autoscaling_plans/)
  service.
- `types-boto3[b2bi]` - Type annotations for
  [B2BI](https://youtype.github.io/types_boto3_docs/types_boto3_b2bi/) service.
- `types-boto3[backup]` - Type annotations for
  [Backup](https://youtype.github.io/types_boto3_docs/types_boto3_backup/)
  service.
- `types-boto3[backup-gateway]` - Type annotations for
  [BackupGateway](https://youtype.github.io/types_boto3_docs/types_boto3_backup_gateway/)
  service.
- `types-boto3[backupsearch]` - Type annotations for
  [BackupSearch](https://youtype.github.io/types_boto3_docs/types_boto3_backupsearch/)
  service.
- `types-boto3[batch]` - Type annotations for
  [Batch](https://youtype.github.io/types_boto3_docs/types_boto3_batch/)
  service.
- `types-boto3[bcm-dashboards]` - Type annotations for
  [BillingandCostManagementDashboards](https://youtype.github.io/types_boto3_docs/types_boto3_bcm_dashboards/)
  service.
- `types-boto3[bcm-data-exports]` - Type annotations for
  [BillingandCostManagementDataExports](https://youtype.github.io/types_boto3_docs/types_boto3_bcm_data_exports/)
  service.
- `types-boto3[bcm-pricing-calculator]` - Type annotations for
  [BillingandCostManagementPricingCalculator](https://youtype.github.io/types_boto3_docs/types_boto3_bcm_pricing_calculator/)
  service.
- `types-boto3[bcm-recommended-actions]` - Type annotations for
  [BillingandCostManagementRecommendedActions](https://youtype.github.io/types_boto3_docs/types_boto3_bcm_recommended_actions/)
  service.
- `types-boto3[bedrock]` - Type annotations for
  [Bedrock](https://youtype.github.io/types_boto3_docs/types_boto3_bedrock/)
  service.
- `types-boto3[bedrock-agent]` - Type annotations for
  [AgentsforBedrock](https://youtype.github.io/types_boto3_docs/types_boto3_bedrock_agent/)
  service.
- `types-boto3[bedrock-agent-runtime]` - Type annotations for
  [AgentsforBedrockRuntime](https://youtype.github.io/types_boto3_docs/types_boto3_bedrock_agent_runtime/)
  service.
- `types-boto3[bedrock-agentcore]` - Type annotations for
  [BedrockAgentCoreDataPlaneFrontingLayer](https://youtype.github.io/types_boto3_docs/types_boto3_bedrock_agentcore/)
  service.
- `types-boto3[bedrock-agentcore-control]` - Type annotations for
  [BedrockAgentCoreControlPlaneFrontingLayer](https://youtype.github.io/types_boto3_docs/types_boto3_bedrock_agentcore_control/)
  service.
- `types-boto3[bedrock-data-automation]` - Type annotations for
  [DataAutomationforBedrock](https://youtype.github.io/types_boto3_docs/types_boto3_bedrock_data_automation/)
  service.
- `types-boto3[bedrock-data-automation-runtime]` - Type annotations for
  [RuntimeforBedrockDataAutomation](https://youtype.github.io/types_boto3_docs/types_boto3_bedrock_data_automation_runtime/)
  service.
- `types-boto3[bedrock-runtime]` - Type annotations for
  [BedrockRuntime](https://youtype.github.io/types_boto3_docs/types_boto3_bedrock_runtime/)
  service.
- `types-boto3[billing]` - Type annotations for
  [Billing](https://youtype.github.io/types_boto3_docs/types_boto3_billing/)
  service.
- `types-boto3[billingconductor]` - Type annotations for
  [BillingConductor](https://youtype.github.io/types_boto3_docs/types_boto3_billingconductor/)
  service.
- `types-boto3[braket]` - Type annotations for
  [Braket](https://youtype.github.io/types_boto3_docs/types_boto3_braket/)
  service.
- `types-boto3[budgets]` - Type annotations for
  [Budgets](https://youtype.github.io/types_boto3_docs/types_boto3_budgets/)
  service.
- `types-boto3[ce]` - Type annotations for
  [CostExplorer](https://youtype.github.io/types_boto3_docs/types_boto3_ce/)
  service.
- `types-boto3[chatbot]` - Type annotations for
  [Chatbot](https://youtype.github.io/types_boto3_docs/types_boto3_chatbot/)
  service.
- `types-boto3[chime]` - Type annotations for
  [Chime](https://youtype.github.io/types_boto3_docs/types_boto3_chime/)
  service.
- `types-boto3[chime-sdk-identity]` - Type annotations for
  [ChimeSDKIdentity](https://youtype.github.io/types_boto3_docs/types_boto3_chime_sdk_identity/)
  service.
- `types-boto3[chime-sdk-media-pipelines]` - Type annotations for
  [ChimeSDKMediaPipelines](https://youtype.github.io/types_boto3_docs/types_boto3_chime_sdk_media_pipelines/)
  service.
- `types-boto3[chime-sdk-meetings]` - Type annotations for
  [ChimeSDKMeetings](https://youtype.github.io/types_boto3_docs/types_boto3_chime_sdk_meetings/)
  service.
- `types-boto3[chime-sdk-messaging]` - Type annotations for
  [ChimeSDKMessaging](https://youtype.github.io/types_boto3_docs/types_boto3_chime_sdk_messaging/)
  service.
- `types-boto3[chime-sdk-voice]` - Type annotations for
  [ChimeSDKVoice](https://youtype.github.io/types_boto3_docs/types_boto3_chime_sdk_voice/)
  service.
- `types-boto3[cleanrooms]` - Type annotations for
  [CleanRoomsService](https://youtype.github.io/types_boto3_docs/types_boto3_cleanrooms/)
  service.
- `types-boto3[cleanroomsml]` - Type annotations for
  [CleanRoomsML](https://youtype.github.io/types_boto3_docs/types_boto3_cleanroomsml/)
  service.
- `types-boto3[cloud9]` - Type annotations for
  [Cloud9](https://youtype.github.io/types_boto3_docs/types_boto3_cloud9/)
  service.
- `types-boto3[cloudcontrol]` - Type annotations for
  [CloudControlApi](https://youtype.github.io/types_boto3_docs/types_boto3_cloudcontrol/)
  service.
- `types-boto3[clouddirectory]` - Type annotations for
  [CloudDirectory](https://youtype.github.io/types_boto3_docs/types_boto3_clouddirectory/)
  service.
- `types-boto3[cloudformation]` - Type annotations for
  [CloudFormation](https://youtype.github.io/types_boto3_docs/types_boto3_cloudformation/)
  service.
- `types-boto3[cloudfront]` - Type annotations for
  [CloudFront](https://youtype.github.io/types_boto3_docs/types_boto3_cloudfront/)
  service.
- `types-boto3[cloudfront-keyvaluestore]` - Type annotations for
  [CloudFrontKeyValueStore](https://youtype.github.io/types_boto3_docs/types_boto3_cloudfront_keyvaluestore/)
  service.
- `types-boto3[cloudhsm]` - Type annotations for
  [CloudHSM](https://youtype.github.io/types_boto3_docs/types_boto3_cloudhsm/)
  service.
- `types-boto3[cloudhsmv2]` - Type annotations for
  [CloudHSMV2](https://youtype.github.io/types_boto3_docs/types_boto3_cloudhsmv2/)
  service.
- `types-boto3[cloudsearch]` - Type annotations for
  [CloudSearch](https://youtype.github.io/types_boto3_docs/types_boto3_cloudsearch/)
  service.
- `types-boto3[cloudsearchdomain]` - Type annotations for
  [CloudSearchDomain](https://youtype.github.io/types_boto3_docs/types_boto3_cloudsearchdomain/)
  service.
- `types-boto3[cloudtrail]` - Type annotations for
  [CloudTrail](https://youtype.github.io/types_boto3_docs/types_boto3_cloudtrail/)
  service.
- `types-boto3[cloudtrail-data]` - Type annotations for
  [CloudTrailDataService](https://youtype.github.io/types_boto3_docs/types_boto3_cloudtrail_data/)
  service.
- `types-boto3[cloudwatch]` - Type annotations for
  [CloudWatch](https://youtype.github.io/types_boto3_docs/types_boto3_cloudwatch/)
  service.
- `types-boto3[codeartifact]` - Type annotations for
  [CodeArtifact](https://youtype.github.io/types_boto3_docs/types_boto3_codeartifact/)
  service.
- `types-boto3[codebuild]` - Type annotations for
  [CodeBuild](https://youtype.github.io/types_boto3_docs/types_boto3_codebuild/)
  service.
- `types-boto3[codecatalyst]` - Type annotations for
  [CodeCatalyst](https://youtype.github.io/types_boto3_docs/types_boto3_codecatalyst/)
  service.
- `types-boto3[codecommit]` - Type annotations for
  [CodeCommit](https://youtype.github.io/types_boto3_docs/types_boto3_codecommit/)
  service.
- `types-boto3[codeconnections]` - Type annotations for
  [CodeConnections](https://youtype.github.io/types_boto3_docs/types_boto3_codeconnections/)
  service.
- `types-boto3[codedeploy]` - Type annotations for
  [CodeDeploy](https://youtype.github.io/types_boto3_docs/types_boto3_codedeploy/)
  service.
- `types-boto3[codeguru-reviewer]` - Type annotations for
  [CodeGuruReviewer](https://youtype.github.io/types_boto3_docs/types_boto3_codeguru_reviewer/)
  service.
- `types-boto3[codeguru-security]` - Type annotations for
  [CodeGuruSecurity](https://youtype.github.io/types_boto3_docs/types_boto3_codeguru_security/)
  service.
- `types-boto3[codeguruprofiler]` - Type annotations for
  [CodeGuruProfiler](https://youtype.github.io/types_boto3_docs/types_boto3_codeguruprofiler/)
  service.
- `types-boto3[codepipeline]` - Type annotations for
  [CodePipeline](https://youtype.github.io/types_boto3_docs/types_boto3_codepipeline/)
  service.
- `types-boto3[codestar-connections]` - Type annotations for
  [CodeStarconnections](https://youtype.github.io/types_boto3_docs/types_boto3_codestar_connections/)
  service.
- `types-boto3[codestar-notifications]` - Type annotations for
  [CodeStarNotifications](https://youtype.github.io/types_boto3_docs/types_boto3_codestar_notifications/)
  service.
- `types-boto3[cognito-identity]` - Type annotations for
  [CognitoIdentity](https://youtype.github.io/types_boto3_docs/types_boto3_cognito_identity/)
  service.
- `types-boto3[cognito-idp]` - Type annotations for
  [CognitoIdentityProvider](https://youtype.github.io/types_boto3_docs/types_boto3_cognito_idp/)
  service.
- `types-boto3[cognito-sync]` - Type annotations for
  [CognitoSync](https://youtype.github.io/types_boto3_docs/types_boto3_cognito_sync/)
  service.
- `types-boto3[comprehend]` - Type annotations for
  [Comprehend](https://youtype.github.io/types_boto3_docs/types_boto3_comprehend/)
  service.
- `types-boto3[comprehendmedical]` - Type annotations for
  [ComprehendMedical](https://youtype.github.io/types_boto3_docs/types_boto3_comprehendmedical/)
  service.
- `types-boto3[compute-optimizer]` - Type annotations for
  [ComputeOptimizer](https://youtype.github.io/types_boto3_docs/types_boto3_compute_optimizer/)
  service.
- `types-boto3[config]` - Type annotations for
  [ConfigService](https://youtype.github.io/types_boto3_docs/types_boto3_config/)
  service.
- `types-boto3[connect]` - Type annotations for
  [Connect](https://youtype.github.io/types_boto3_docs/types_boto3_connect/)
  service.
- `types-boto3[connect-contact-lens]` - Type annotations for
  [ConnectContactLens](https://youtype.github.io/types_boto3_docs/types_boto3_connect_contact_lens/)
  service.
- `types-boto3[connectcampaigns]` - Type annotations for
  [ConnectCampaignService](https://youtype.github.io/types_boto3_docs/types_boto3_connectcampaigns/)
  service.
- `types-boto3[connectcampaignsv2]` - Type annotations for
  [ConnectCampaignServiceV2](https://youtype.github.io/types_boto3_docs/types_boto3_connectcampaignsv2/)
  service.
- `types-boto3[connectcases]` - Type annotations for
  [ConnectCases](https://youtype.github.io/types_boto3_docs/types_boto3_connectcases/)
  service.
- `types-boto3[connectparticipant]` - Type annotations for
  [ConnectParticipant](https://youtype.github.io/types_boto3_docs/types_boto3_connectparticipant/)
  service.
- `types-boto3[controlcatalog]` - Type annotations for
  [ControlCatalog](https://youtype.github.io/types_boto3_docs/types_boto3_controlcatalog/)
  service.
- `types-boto3[controltower]` - Type annotations for
  [ControlTower](https://youtype.github.io/types_boto3_docs/types_boto3_controltower/)
  service.
- `types-boto3[cost-optimization-hub]` - Type annotations for
  [CostOptimizationHub](https://youtype.github.io/types_boto3_docs/types_boto3_cost_optimization_hub/)
  service.
- `types-boto3[cur]` - Type annotations for
  [CostandUsageReportService](https://youtype.github.io/types_boto3_docs/types_boto3_cur/)
  service.
- `types-boto3[customer-profiles]` - Type annotations for
  [CustomerProfiles](https://youtype.github.io/types_boto3_docs/types_boto3_customer_profiles/)
  service.
- `types-boto3[databrew]` - Type annotations for
  [GlueDataBrew](https://youtype.github.io/types_boto3_docs/types_boto3_databrew/)
  service.
- `types-boto3[dataexchange]` - Type annotations for
  [DataExchange](https://youtype.github.io/types_boto3_docs/types_boto3_dataexchange/)
  service.
- `types-boto3[datapipeline]` - Type annotations for
  [DataPipeline](https://youtype.github.io/types_boto3_docs/types_boto3_datapipeline/)
  service.
- `types-boto3[datasync]` - Type annotations for
  [DataSync](https://youtype.github.io/types_boto3_docs/types_boto3_datasync/)
  service.
- `types-boto3[datazone]` - Type annotations for
  [DataZone](https://youtype.github.io/types_boto3_docs/types_boto3_datazone/)
  service.
- `types-boto3[dax]` - Type annotations for
  [DAX](https://youtype.github.io/types_boto3_docs/types_boto3_dax/) service.
- `types-boto3[deadline]` - Type annotations for
  [DeadlineCloud](https://youtype.github.io/types_boto3_docs/types_boto3_deadline/)
  service.
- `types-boto3[detective]` - Type annotations for
  [Detective](https://youtype.github.io/types_boto3_docs/types_boto3_detective/)
  service.
- `types-boto3[devicefarm]` - Type annotations for
  [DeviceFarm](https://youtype.github.io/types_boto3_docs/types_boto3_devicefarm/)
  service.
- `types-boto3[devops-guru]` - Type annotations for
  [DevOpsGuru](https://youtype.github.io/types_boto3_docs/types_boto3_devops_guru/)
  service.
- `types-boto3[directconnect]` - Type annotations for
  [DirectConnect](https://youtype.github.io/types_boto3_docs/types_boto3_directconnect/)
  service.
- `types-boto3[discovery]` - Type annotations for
  [ApplicationDiscoveryService](https://youtype.github.io/types_boto3_docs/types_boto3_discovery/)
  service.
- `types-boto3[dlm]` - Type annotations for
  [DLM](https://youtype.github.io/types_boto3_docs/types_boto3_dlm/) service.
- `types-boto3[dms]` - Type annotations for
  [DatabaseMigrationService](https://youtype.github.io/types_boto3_docs/types_boto3_dms/)
  service.
- `types-boto3[docdb]` - Type annotations for
  [DocDB](https://youtype.github.io/types_boto3_docs/types_boto3_docdb/)
  service.
- `types-boto3[docdb-elastic]` - Type annotations for
  [DocDBElastic](https://youtype.github.io/types_boto3_docs/types_boto3_docdb_elastic/)
  service.
- `types-boto3[drs]` - Type annotations for
  [Drs](https://youtype.github.io/types_boto3_docs/types_boto3_drs/) service.
- `types-boto3[ds]` - Type annotations for
  [DirectoryService](https://youtype.github.io/types_boto3_docs/types_boto3_ds/)
  service.
- `types-boto3[ds-data]` - Type annotations for
  [DirectoryServiceData](https://youtype.github.io/types_boto3_docs/types_boto3_ds_data/)
  service.
- `types-boto3[dsql]` - Type annotations for
  [AuroraDSQL](https://youtype.github.io/types_boto3_docs/types_boto3_dsql/)
  service.
- `types-boto3[dynamodb]` - Type annotations for
  [DynamoDB](https://youtype.github.io/types_boto3_docs/types_boto3_dynamodb/)
  service.
- `types-boto3[dynamodbstreams]` - Type annotations for
  [DynamoDBStreams](https://youtype.github.io/types_boto3_docs/types_boto3_dynamodbstreams/)
  service.
- `types-boto3[ebs]` - Type annotations for
  [EBS](https://youtype.github.io/types_boto3_docs/types_boto3_ebs/) service.
- `types-boto3[ec2]` - Type annotations for
  [EC2](https://youtype.github.io/types_boto3_docs/types_boto3_ec2/) service.
- `types-boto3[ec2-instance-connect]` - Type annotations for
  [EC2InstanceConnect](https://youtype.github.io/types_boto3_docs/types_boto3_ec2_instance_connect/)
  service.
- `types-boto3[ecr]` - Type annotations for
  [ECR](https://youtype.github.io/types_boto3_docs/types_boto3_ecr/) service.
- `types-boto3[ecr-public]` - Type annotations for
  [ECRPublic](https://youtype.github.io/types_boto3_docs/types_boto3_ecr_public/)
  service.
- `types-boto3[ecs]` - Type annotations for
  [ECS](https://youtype.github.io/types_boto3_docs/types_boto3_ecs/) service.
- `types-boto3[efs]` - Type annotations for
  [EFS](https://youtype.github.io/types_boto3_docs/types_boto3_efs/) service.
- `types-boto3[eks]` - Type annotations for
  [EKS](https://youtype.github.io/types_boto3_docs/types_boto3_eks/) service.
- `types-boto3[eks-auth]` - Type annotations for
  [EKSAuth](https://youtype.github.io/types_boto3_docs/types_boto3_eks_auth/)
  service.
- `types-boto3[elasticache]` - Type annotations for
  [ElastiCache](https://youtype.github.io/types_boto3_docs/types_boto3_elasticache/)
  service.
- `types-boto3[elasticbeanstalk]` - Type annotations for
  [ElasticBeanstalk](https://youtype.github.io/types_boto3_docs/types_boto3_elasticbeanstalk/)
  service.
- `types-boto3[elastictranscoder]` - Type annotations for
  [ElasticTranscoder](https://youtype.github.io/types_boto3_docs/types_boto3_elastictranscoder/)
  service.
- `types-boto3[elb]` - Type annotations for
  [ElasticLoadBalancing](https://youtype.github.io/types_boto3_docs/types_boto3_elb/)
  service.
- `types-boto3[elbv2]` - Type annotations for
  [ElasticLoadBalancingv2](https://youtype.github.io/types_boto3_docs/types_boto3_elbv2/)
  service.
- `types-boto3[emr]` - Type annotations for
  [EMR](https://youtype.github.io/types_boto3_docs/types_boto3_emr/) service.
- `types-boto3[emr-containers]` - Type annotations for
  [EMRContainers](https://youtype.github.io/types_boto3_docs/types_boto3_emr_containers/)
  service.
- `types-boto3[emr-serverless]` - Type annotations for
  [EMRServerless](https://youtype.github.io/types_boto3_docs/types_boto3_emr_serverless/)
  service.
- `types-boto3[entityresolution]` - Type annotations for
  [EntityResolution](https://youtype.github.io/types_boto3_docs/types_boto3_entityresolution/)
  service.
- `types-boto3[es]` - Type annotations for
  [ElasticsearchService](https://youtype.github.io/types_boto3_docs/types_boto3_es/)
  service.
- `types-boto3[events]` - Type annotations for
  [EventBridge](https://youtype.github.io/types_boto3_docs/types_boto3_events/)
  service.
- `types-boto3[evidently]` - Type annotations for
  [CloudWatchEvidently](https://youtype.github.io/types_boto3_docs/types_boto3_evidently/)
  service.
- `types-boto3[evs]` - Type annotations for
  [EVS](https://youtype.github.io/types_boto3_docs/types_boto3_evs/) service.
- `types-boto3[finspace]` - Type annotations for
  [Finspace](https://youtype.github.io/types_boto3_docs/types_boto3_finspace/)
  service.
- `types-boto3[finspace-data]` - Type annotations for
  [FinSpaceData](https://youtype.github.io/types_boto3_docs/types_boto3_finspace_data/)
  service.
- `types-boto3[firehose]` - Type annotations for
  [Firehose](https://youtype.github.io/types_boto3_docs/types_boto3_firehose/)
  service.
- `types-boto3[fis]` - Type annotations for
  [FIS](https://youtype.github.io/types_boto3_docs/types_boto3_fis/) service.
- `types-boto3[fms]` - Type annotations for
  [FMS](https://youtype.github.io/types_boto3_docs/types_boto3_fms/) service.
- `types-boto3[forecast]` - Type annotations for
  [ForecastService](https://youtype.github.io/types_boto3_docs/types_boto3_forecast/)
  service.
- `types-boto3[forecastquery]` - Type annotations for
  [ForecastQueryService](https://youtype.github.io/types_boto3_docs/types_boto3_forecastquery/)
  service.
- `types-boto3[frauddetector]` - Type annotations for
  [FraudDetector](https://youtype.github.io/types_boto3_docs/types_boto3_frauddetector/)
  service.
- `types-boto3[freetier]` - Type annotations for
  [FreeTier](https://youtype.github.io/types_boto3_docs/types_boto3_freetier/)
  service.
- `types-boto3[fsx]` - Type annotations for
  [FSx](https://youtype.github.io/types_boto3_docs/types_boto3_fsx/) service.
- `types-boto3[gamelift]` - Type annotations for
  [GameLift](https://youtype.github.io/types_boto3_docs/types_boto3_gamelift/)
  service.
- `types-boto3[gameliftstreams]` - Type annotations for
  [GameLiftStreams](https://youtype.github.io/types_boto3_docs/types_boto3_gameliftstreams/)
  service.
- `types-boto3[geo-maps]` - Type annotations for
  [LocationServiceMapsV2](https://youtype.github.io/types_boto3_docs/types_boto3_geo_maps/)
  service.
- `types-boto3[geo-places]` - Type annotations for
  [LocationServicePlacesV2](https://youtype.github.io/types_boto3_docs/types_boto3_geo_places/)
  service.
- `types-boto3[geo-routes]` - Type annotations for
  [LocationServiceRoutesV2](https://youtype.github.io/types_boto3_docs/types_boto3_geo_routes/)
  service.
- `types-boto3[glacier]` - Type annotations for
  [Glacier](https://youtype.github.io/types_boto3_docs/types_boto3_glacier/)
  service.
- `types-boto3[globalaccelerator]` - Type annotations for
  [GlobalAccelerator](https://youtype.github.io/types_boto3_docs/types_boto3_globalaccelerator/)
  service.
- `types-boto3[glue]` - Type annotations for
  [Glue](https://youtype.github.io/types_boto3_docs/types_boto3_glue/) service.
- `types-boto3[grafana]` - Type annotations for
  [ManagedGrafana](https://youtype.github.io/types_boto3_docs/types_boto3_grafana/)
  service.
- `types-boto3[greengrass]` - Type annotations for
  [Greengrass](https://youtype.github.io/types_boto3_docs/types_boto3_greengrass/)
  service.
- `types-boto3[greengrassv2]` - Type annotations for
  [GreengrassV2](https://youtype.github.io/types_boto3_docs/types_boto3_greengrassv2/)
  service.
- `types-boto3[groundstation]` - Type annotations for
  [GroundStation](https://youtype.github.io/types_boto3_docs/types_boto3_groundstation/)
  service.
- `types-boto3[guardduty]` - Type annotations for
  [GuardDuty](https://youtype.github.io/types_boto3_docs/types_boto3_guardduty/)
  service.
- `types-boto3[health]` - Type annotations for
  [Health](https://youtype.github.io/types_boto3_docs/types_boto3_health/)
  service.
- `types-boto3[healthlake]` - Type annotations for
  [HealthLake](https://youtype.github.io/types_boto3_docs/types_boto3_healthlake/)
  service.
- `types-boto3[iam]` - Type annotations for
  [IAM](https://youtype.github.io/types_boto3_docs/types_boto3_iam/) service.
- `types-boto3[identitystore]` - Type annotations for
  [IdentityStore](https://youtype.github.io/types_boto3_docs/types_boto3_identitystore/)
  service.
- `types-boto3[imagebuilder]` - Type annotations for
  [Imagebuilder](https://youtype.github.io/types_boto3_docs/types_boto3_imagebuilder/)
  service.
- `types-boto3[importexport]` - Type annotations for
  [ImportExport](https://youtype.github.io/types_boto3_docs/types_boto3_importexport/)
  service.
- `types-boto3[inspector]` - Type annotations for
  [Inspector](https://youtype.github.io/types_boto3_docs/types_boto3_inspector/)
  service.
- `types-boto3[inspector-scan]` - Type annotations for
  [Inspectorscan](https://youtype.github.io/types_boto3_docs/types_boto3_inspector_scan/)
  service.
- `types-boto3[inspector2]` - Type annotations for
  [Inspector2](https://youtype.github.io/types_boto3_docs/types_boto3_inspector2/)
  service.
- `types-boto3[internetmonitor]` - Type annotations for
  [CloudWatchInternetMonitor](https://youtype.github.io/types_boto3_docs/types_boto3_internetmonitor/)
  service.
- `types-boto3[invoicing]` - Type annotations for
  [Invoicing](https://youtype.github.io/types_boto3_docs/types_boto3_invoicing/)
  service.
- `types-boto3[iot]` - Type annotations for
  [IoT](https://youtype.github.io/types_boto3_docs/types_boto3_iot/) service.
- `types-boto3[iot-data]` - Type annotations for
  [IoTDataPlane](https://youtype.github.io/types_boto3_docs/types_boto3_iot_data/)
  service.
- `types-boto3[iot-jobs-data]` - Type annotations for
  [IoTJobsDataPlane](https://youtype.github.io/types_boto3_docs/types_boto3_iot_jobs_data/)
  service.
- `types-boto3[iot-managed-integrations]` - Type annotations for
  [ManagedintegrationsforIoTDeviceManagement](https://youtype.github.io/types_boto3_docs/types_boto3_iot_managed_integrations/)
  service.
- `types-boto3[iotanalytics]` - Type annotations for
  [IoTAnalytics](https://youtype.github.io/types_boto3_docs/types_boto3_iotanalytics/)
  service.
- `types-boto3[iotdeviceadvisor]` - Type annotations for
  [IoTDeviceAdvisor](https://youtype.github.io/types_boto3_docs/types_boto3_iotdeviceadvisor/)
  service.
- `types-boto3[iotevents]` - Type annotations for
  [IoTEvents](https://youtype.github.io/types_boto3_docs/types_boto3_iotevents/)
  service.
- `types-boto3[iotevents-data]` - Type annotations for
  [IoTEventsData](https://youtype.github.io/types_boto3_docs/types_boto3_iotevents_data/)
  service.
- `types-boto3[iotfleethub]` - Type annotations for
  [IoTFleetHub](https://youtype.github.io/types_boto3_docs/types_boto3_iotfleethub/)
  service.
- `types-boto3[iotfleetwise]` - Type annotations for
  [IoTFleetWise](https://youtype.github.io/types_boto3_docs/types_boto3_iotfleetwise/)
  service.
- `types-boto3[iotsecuretunneling]` - Type annotations for
  [IoTSecureTunneling](https://youtype.github.io/types_boto3_docs/types_boto3_iotsecuretunneling/)
  service.
- `types-boto3[iotsitewise]` - Type annotations for
  [IoTSiteWise](https://youtype.github.io/types_boto3_docs/types_boto3_iotsitewise/)
  service.
- `types-boto3[iotthingsgraph]` - Type annotations for
  [IoTThingsGraph](https://youtype.github.io/types_boto3_docs/types_boto3_iotthingsgraph/)
  service.
- `types-boto3[iottwinmaker]` - Type annotations for
  [IoTTwinMaker](https://youtype.github.io/types_boto3_docs/types_boto3_iottwinmaker/)
  service.
- `types-boto3[iotwireless]` - Type annotations for
  [IoTWireless](https://youtype.github.io/types_boto3_docs/types_boto3_iotwireless/)
  service.
- `types-boto3[ivs]` - Type annotations for
  [IVS](https://youtype.github.io/types_boto3_docs/types_boto3_ivs/) service.
- `types-boto3[ivs-realtime]` - Type annotations for
  [Ivsrealtime](https://youtype.github.io/types_boto3_docs/types_boto3_ivs_realtime/)
  service.
- `types-boto3[ivschat]` - Type annotations for
  [Ivschat](https://youtype.github.io/types_boto3_docs/types_boto3_ivschat/)
  service.
- `types-boto3[kafka]` - Type annotations for
  [Kafka](https://youtype.github.io/types_boto3_docs/types_boto3_kafka/)
  service.
- `types-boto3[kafkaconnect]` - Type annotations for
  [KafkaConnect](https://youtype.github.io/types_boto3_docs/types_boto3_kafkaconnect/)
  service.
- `types-boto3[kendra]` - Type annotations for
  [Kendra](https://youtype.github.io/types_boto3_docs/types_boto3_kendra/)
  service.
- `types-boto3[kendra-ranking]` - Type annotations for
  [KendraRanking](https://youtype.github.io/types_boto3_docs/types_boto3_kendra_ranking/)
  service.
- `types-boto3[keyspaces]` - Type annotations for
  [Keyspaces](https://youtype.github.io/types_boto3_docs/types_boto3_keyspaces/)
  service.
- `types-boto3[keyspacesstreams]` - Type annotations for
  [KeyspacesStreams](https://youtype.github.io/types_boto3_docs/types_boto3_keyspacesstreams/)
  service.
- `types-boto3[kinesis]` - Type annotations for
  [Kinesis](https://youtype.github.io/types_boto3_docs/types_boto3_kinesis/)
  service.
- `types-boto3[kinesis-video-archived-media]` - Type annotations for
  [KinesisVideoArchivedMedia](https://youtype.github.io/types_boto3_docs/types_boto3_kinesis_video_archived_media/)
  service.
- `types-boto3[kinesis-video-media]` - Type annotations for
  [KinesisVideoMedia](https://youtype.github.io/types_boto3_docs/types_boto3_kinesis_video_media/)
  service.
- `types-boto3[kinesis-video-signaling]` - Type annotations for
  [KinesisVideoSignalingChannels](https://youtype.github.io/types_boto3_docs/types_boto3_kinesis_video_signaling/)
  service.
- `types-boto3[kinesis-video-webrtc-storage]` - Type annotations for
  [KinesisVideoWebRTCStorage](https://youtype.github.io/types_boto3_docs/types_boto3_kinesis_video_webrtc_storage/)
  service.
- `types-boto3[kinesisanalytics]` - Type annotations for
  [KinesisAnalytics](https://youtype.github.io/types_boto3_docs/types_boto3_kinesisanalytics/)
  service.
- `types-boto3[kinesisanalyticsv2]` - Type annotations for
  [KinesisAnalyticsV2](https://youtype.github.io/types_boto3_docs/types_boto3_kinesisanalyticsv2/)
  service.
- `types-boto3[kinesisvideo]` - Type annotations for
  [KinesisVideo](https://youtype.github.io/types_boto3_docs/types_boto3_kinesisvideo/)
  service.
- `types-boto3[kms]` - Type annotations for
  [KMS](https://youtype.github.io/types_boto3_docs/types_boto3_kms/) service.
- `types-boto3[lakeformation]` - Type annotations for
  [LakeFormation](https://youtype.github.io/types_boto3_docs/types_boto3_lakeformation/)
  service.
- `types-boto3[lambda]` - Type annotations for
  [Lambda](https://youtype.github.io/types_boto3_docs/types_boto3_lambda/)
  service.
- `types-boto3[launch-wizard]` - Type annotations for
  [LaunchWizard](https://youtype.github.io/types_boto3_docs/types_boto3_launch_wizard/)
  service.
- `types-boto3[lex-models]` - Type annotations for
  [LexModelBuildingService](https://youtype.github.io/types_boto3_docs/types_boto3_lex_models/)
  service.
- `types-boto3[lex-runtime]` - Type annotations for
  [LexRuntimeService](https://youtype.github.io/types_boto3_docs/types_boto3_lex_runtime/)
  service.
- `types-boto3[lexv2-models]` - Type annotations for
  [LexModelsV2](https://youtype.github.io/types_boto3_docs/types_boto3_lexv2_models/)
  service.
- `types-boto3[lexv2-runtime]` - Type annotations for
  [LexRuntimeV2](https://youtype.github.io/types_boto3_docs/types_boto3_lexv2_runtime/)
  service.
- `types-boto3[license-manager]` - Type annotations for
  [LicenseManager](https://youtype.github.io/types_boto3_docs/types_boto3_license_manager/)
  service.
- `types-boto3[license-manager-linux-subscriptions]` - Type annotations for
  [LicenseManagerLinuxSubscriptions](https://youtype.github.io/types_boto3_docs/types_boto3_license_manager_linux_subscriptions/)
  service.
- `types-boto3[license-manager-user-subscriptions]` - Type annotations for
  [LicenseManagerUserSubscriptions](https://youtype.github.io/types_boto3_docs/types_boto3_license_manager_user_subscriptions/)
  service.
- `types-boto3[lightsail]` - Type annotations for
  [Lightsail](https://youtype.github.io/types_boto3_docs/types_boto3_lightsail/)
  service.
- `types-boto3[location]` - Type annotations for
  [LocationService](https://youtype.github.io/types_boto3_docs/types_boto3_location/)
  service.
- `types-boto3[logs]` - Type annotations for
  [CloudWatchLogs](https://youtype.github.io/types_boto3_docs/types_boto3_logs/)
  service.
- `types-boto3[lookoutequipment]` - Type annotations for
  [LookoutEquipment](https://youtype.github.io/types_boto3_docs/types_boto3_lookoutequipment/)
  service.
- `types-boto3[lookoutmetrics]` - Type annotations for
  [LookoutMetrics](https://youtype.github.io/types_boto3_docs/types_boto3_lookoutmetrics/)
  service.
- `types-boto3[lookoutvision]` - Type annotations for
  [LookoutforVision](https://youtype.github.io/types_boto3_docs/types_boto3_lookoutvision/)
  service.
- `types-boto3[m2]` - Type annotations for
  [MainframeModernization](https://youtype.github.io/types_boto3_docs/types_boto3_m2/)
  service.
- `types-boto3[machinelearning]` - Type annotations for
  [MachineLearning](https://youtype.github.io/types_boto3_docs/types_boto3_machinelearning/)
  service.
- `types-boto3[macie2]` - Type annotations for
  [Macie2](https://youtype.github.io/types_boto3_docs/types_boto3_macie2/)
  service.
- `types-boto3[mailmanager]` - Type annotations for
  [MailManager](https://youtype.github.io/types_boto3_docs/types_boto3_mailmanager/)
  service.
- `types-boto3[managedblockchain]` - Type annotations for
  [ManagedBlockchain](https://youtype.github.io/types_boto3_docs/types_boto3_managedblockchain/)
  service.
- `types-boto3[managedblockchain-query]` - Type annotations for
  [ManagedBlockchainQuery](https://youtype.github.io/types_boto3_docs/types_boto3_managedblockchain_query/)
  service.
- `types-boto3[marketplace-agreement]` - Type annotations for
  [AgreementService](https://youtype.github.io/types_boto3_docs/types_boto3_marketplace_agreement/)
  service.
- `types-boto3[marketplace-catalog]` - Type annotations for
  [MarketplaceCatalog](https://youtype.github.io/types_boto3_docs/types_boto3_marketplace_catalog/)
  service.
- `types-boto3[marketplace-deployment]` - Type annotations for
  [MarketplaceDeploymentService](https://youtype.github.io/types_boto3_docs/types_boto3_marketplace_deployment/)
  service.
- `types-boto3[marketplace-entitlement]` - Type annotations for
  [MarketplaceEntitlementService](https://youtype.github.io/types_boto3_docs/types_boto3_marketplace_entitlement/)
  service.
- `types-boto3[marketplace-reporting]` - Type annotations for
  [MarketplaceReportingService](https://youtype.github.io/types_boto3_docs/types_boto3_marketplace_reporting/)
  service.
- `types-boto3[marketplacecommerceanalytics]` - Type annotations for
  [MarketplaceCommerceAnalytics](https://youtype.github.io/types_boto3_docs/types_boto3_marketplacecommerceanalytics/)
  service.
- `types-boto3[mediaconnect]` - Type annotations for
  [MediaConnect](https://youtype.github.io/types_boto3_docs/types_boto3_mediaconnect/)
  service.
- `types-boto3[mediaconvert]` - Type annotations for
  [MediaConvert](https://youtype.github.io/types_boto3_docs/types_boto3_mediaconvert/)
  service.
- `types-boto3[medialive]` - Type annotations for
  [MediaLive](https://youtype.github.io/types_boto3_docs/types_boto3_medialive/)
  service.
- `types-boto3[mediapackage]` - Type annotations for
  [MediaPackage](https://youtype.github.io/types_boto3_docs/types_boto3_mediapackage/)
  service.
- `types-boto3[mediapackage-vod]` - Type annotations for
  [MediaPackageVod](https://youtype.github.io/types_boto3_docs/types_boto3_mediapackage_vod/)
  service.
- `types-boto3[mediapackagev2]` - Type annotations for
  [Mediapackagev2](https://youtype.github.io/types_boto3_docs/types_boto3_mediapackagev2/)
  service.
- `types-boto3[mediastore]` - Type annotations for
  [MediaStore](https://youtype.github.io/types_boto3_docs/types_boto3_mediastore/)
  service.
- `types-boto3[mediastore-data]` - Type annotations for
  [MediaStoreData](https://youtype.github.io/types_boto3_docs/types_boto3_mediastore_data/)
  service.
- `types-boto3[mediatailor]` - Type annotations for
  [MediaTailor](https://youtype.github.io/types_boto3_docs/types_boto3_mediatailor/)
  service.
- `types-boto3[medical-imaging]` - Type annotations for
  [HealthImaging](https://youtype.github.io/types_boto3_docs/types_boto3_medical_imaging/)
  service.
- `types-boto3[memorydb]` - Type annotations for
  [MemoryDB](https://youtype.github.io/types_boto3_docs/types_boto3_memorydb/)
  service.
- `types-boto3[meteringmarketplace]` - Type annotations for
  [MarketplaceMetering](https://youtype.github.io/types_boto3_docs/types_boto3_meteringmarketplace/)
  service.
- `types-boto3[mgh]` - Type annotations for
  [MigrationHub](https://youtype.github.io/types_boto3_docs/types_boto3_mgh/)
  service.
- `types-boto3[mgn]` - Type annotations for
  [Mgn](https://youtype.github.io/types_boto3_docs/types_boto3_mgn/) service.
- `types-boto3[migration-hub-refactor-spaces]` - Type annotations for
  [MigrationHubRefactorSpaces](https://youtype.github.io/types_boto3_docs/types_boto3_migration_hub_refactor_spaces/)
  service.
- `types-boto3[migrationhub-config]` - Type annotations for
  [MigrationHubConfig](https://youtype.github.io/types_boto3_docs/types_boto3_migrationhub_config/)
  service.
- `types-boto3[migrationhuborchestrator]` - Type annotations for
  [MigrationHubOrchestrator](https://youtype.github.io/types_boto3_docs/types_boto3_migrationhuborchestrator/)
  service.
- `types-boto3[migrationhubstrategy]` - Type annotations for
  [MigrationHubStrategyRecommendations](https://youtype.github.io/types_boto3_docs/types_boto3_migrationhubstrategy/)
  service.
- `types-boto3[mpa]` - Type annotations for
  [MultipartyApproval](https://youtype.github.io/types_boto3_docs/types_boto3_mpa/)
  service.
- `types-boto3[mq]` - Type annotations for
  [MQ](https://youtype.github.io/types_boto3_docs/types_boto3_mq/) service.
- `types-boto3[mturk]` - Type annotations for
  [MTurk](https://youtype.github.io/types_boto3_docs/types_boto3_mturk/)
  service.
- `types-boto3[mwaa]` - Type annotations for
  [MWAA](https://youtype.github.io/types_boto3_docs/types_boto3_mwaa/) service.
- `types-boto3[neptune]` - Type annotations for
  [Neptune](https://youtype.github.io/types_boto3_docs/types_boto3_neptune/)
  service.
- `types-boto3[neptune-graph]` - Type annotations for
  [NeptuneGraph](https://youtype.github.io/types_boto3_docs/types_boto3_neptune_graph/)
  service.
- `types-boto3[neptunedata]` - Type annotations for
  [NeptuneData](https://youtype.github.io/types_boto3_docs/types_boto3_neptunedata/)
  service.
- `types-boto3[network-firewall]` - Type annotations for
  [NetworkFirewall](https://youtype.github.io/types_boto3_docs/types_boto3_network_firewall/)
  service.
- `types-boto3[networkflowmonitor]` - Type annotations for
  [NetworkFlowMonitor](https://youtype.github.io/types_boto3_docs/types_boto3_networkflowmonitor/)
  service.
- `types-boto3[networkmanager]` - Type annotations for
  [NetworkManager](https://youtype.github.io/types_boto3_docs/types_boto3_networkmanager/)
  service.
- `types-boto3[networkmonitor]` - Type annotations for
  [CloudWatchNetworkMonitor](https://youtype.github.io/types_boto3_docs/types_boto3_networkmonitor/)
  service.
- `types-boto3[notifications]` - Type annotations for
  [UserNotifications](https://youtype.github.io/types_boto3_docs/types_boto3_notifications/)
  service.
- `types-boto3[notificationscontacts]` - Type annotations for
  [UserNotificationsContacts](https://youtype.github.io/types_boto3_docs/types_boto3_notificationscontacts/)
  service.
- `types-boto3[oam]` - Type annotations for
  [CloudWatchObservabilityAccessManager](https://youtype.github.io/types_boto3_docs/types_boto3_oam/)
  service.
- `types-boto3[observabilityadmin]` - Type annotations for
  [CloudWatchObservabilityAdminService](https://youtype.github.io/types_boto3_docs/types_boto3_observabilityadmin/)
  service.
- `types-boto3[odb]` - Type annotations for
  [Odb](https://youtype.github.io/types_boto3_docs/types_boto3_odb/) service.
- `types-boto3[omics]` - Type annotations for
  [Omics](https://youtype.github.io/types_boto3_docs/types_boto3_omics/)
  service.
- `types-boto3[opensearch]` - Type annotations for
  [OpenSearchService](https://youtype.github.io/types_boto3_docs/types_boto3_opensearch/)
  service.
- `types-boto3[opensearchserverless]` - Type annotations for
  [OpenSearchServiceServerless](https://youtype.github.io/types_boto3_docs/types_boto3_opensearchserverless/)
  service.
- `types-boto3[organizations]` - Type annotations for
  [Organizations](https://youtype.github.io/types_boto3_docs/types_boto3_organizations/)
  service.
- `types-boto3[osis]` - Type annotations for
  [OpenSearchIngestion](https://youtype.github.io/types_boto3_docs/types_boto3_osis/)
  service.
- `types-boto3[outposts]` - Type annotations for
  [Outposts](https://youtype.github.io/types_boto3_docs/types_boto3_outposts/)
  service.
- `types-boto3[panorama]` - Type annotations for
  [Panorama](https://youtype.github.io/types_boto3_docs/types_boto3_panorama/)
  service.
- `types-boto3[partnercentral-selling]` - Type annotations for
  [PartnerCentralSellingAPI](https://youtype.github.io/types_boto3_docs/types_boto3_partnercentral_selling/)
  service.
- `types-boto3[payment-cryptography]` - Type annotations for
  [PaymentCryptographyControlPlane](https://youtype.github.io/types_boto3_docs/types_boto3_payment_cryptography/)
  service.
- `types-boto3[payment-cryptography-data]` - Type annotations for
  [PaymentCryptographyDataPlane](https://youtype.github.io/types_boto3_docs/types_boto3_payment_cryptography_data/)
  service.
- `types-boto3[pca-connector-ad]` - Type annotations for
  [PcaConnectorAd](https://youtype.github.io/types_boto3_docs/types_boto3_pca_connector_ad/)
  service.
- `types-boto3[pca-connector-scep]` - Type annotations for
  [PrivateCAConnectorforSCEP](https://youtype.github.io/types_boto3_docs/types_boto3_pca_connector_scep/)
  service.
- `types-boto3[pcs]` - Type annotations for
  [ParallelComputingService](https://youtype.github.io/types_boto3_docs/types_boto3_pcs/)
  service.
- `types-boto3[personalize]` - Type annotations for
  [Personalize](https://youtype.github.io/types_boto3_docs/types_boto3_personalize/)
  service.
- `types-boto3[personalize-events]` - Type annotations for
  [PersonalizeEvents](https://youtype.github.io/types_boto3_docs/types_boto3_personalize_events/)
  service.
- `types-boto3[personalize-runtime]` - Type annotations for
  [PersonalizeRuntime](https://youtype.github.io/types_boto3_docs/types_boto3_personalize_runtime/)
  service.
- `types-boto3[pi]` - Type annotations for
  [PI](https://youtype.github.io/types_boto3_docs/types_boto3_pi/) service.
- `types-boto3[pinpoint]` - Type annotations for
  [Pinpoint](https://youtype.github.io/types_boto3_docs/types_boto3_pinpoint/)
  service.
- `types-boto3[pinpoint-email]` - Type annotations for
  [PinpointEmail](https://youtype.github.io/types_boto3_docs/types_boto3_pinpoint_email/)
  service.
- `types-boto3[pinpoint-sms-voice]` - Type annotations for
  [PinpointSMSVoice](https://youtype.github.io/types_boto3_docs/types_boto3_pinpoint_sms_voice/)
  service.
- `types-boto3[pinpoint-sms-voice-v2]` - Type annotations for
  [PinpointSMSVoiceV2](https://youtype.github.io/types_boto3_docs/types_boto3_pinpoint_sms_voice_v2/)
  service.
- `types-boto3[pipes]` - Type annotations for
  [EventBridgePipes](https://youtype.github.io/types_boto3_docs/types_boto3_pipes/)
  service.
- `types-boto3[polly]` - Type annotations for
  [Polly](https://youtype.github.io/types_boto3_docs/types_boto3_polly/)
  service.
- `types-boto3[pricing]` - Type annotations for
  [Pricing](https://youtype.github.io/types_boto3_docs/types_boto3_pricing/)
  service.
- `types-boto3[proton]` - Type annotations for
  [Proton](https://youtype.github.io/types_boto3_docs/types_boto3_proton/)
  service.
- `types-boto3[qapps]` - Type annotations for
  [QApps](https://youtype.github.io/types_boto3_docs/types_boto3_qapps/)
  service.
- `types-boto3[qbusiness]` - Type annotations for
  [QBusiness](https://youtype.github.io/types_boto3_docs/types_boto3_qbusiness/)
  service.
- `types-boto3[qconnect]` - Type annotations for
  [QConnect](https://youtype.github.io/types_boto3_docs/types_boto3_qconnect/)
  service.
- `types-boto3[qldb]` - Type annotations for
  [QLDB](https://youtype.github.io/types_boto3_docs/types_boto3_qldb/) service.
- `types-boto3[qldb-session]` - Type annotations for
  [QLDBSession](https://youtype.github.io/types_boto3_docs/types_boto3_qldb_session/)
  service.
- `types-boto3[quicksight]` - Type annotations for
  [QuickSight](https://youtype.github.io/types_boto3_docs/types_boto3_quicksight/)
  service.
- `types-boto3[ram]` - Type annotations for
  [RAM](https://youtype.github.io/types_boto3_docs/types_boto3_ram/) service.
- `types-boto3[rbin]` - Type annotations for
  [RecycleBin](https://youtype.github.io/types_boto3_docs/types_boto3_rbin/)
  service.
- `types-boto3[rds]` - Type annotations for
  [RDS](https://youtype.github.io/types_boto3_docs/types_boto3_rds/) service.
- `types-boto3[rds-data]` - Type annotations for
  [RDSDataService](https://youtype.github.io/types_boto3_docs/types_boto3_rds_data/)
  service.
- `types-boto3[redshift]` - Type annotations for
  [Redshift](https://youtype.github.io/types_boto3_docs/types_boto3_redshift/)
  service.
- `types-boto3[redshift-data]` - Type annotations for
  [RedshiftDataAPIService](https://youtype.github.io/types_boto3_docs/types_boto3_redshift_data/)
  service.
- `types-boto3[redshift-serverless]` - Type annotations for
  [RedshiftServerless](https://youtype.github.io/types_boto3_docs/types_boto3_redshift_serverless/)
  service.
- `types-boto3[rekognition]` - Type annotations for
  [Rekognition](https://youtype.github.io/types_boto3_docs/types_boto3_rekognition/)
  service.
- `types-boto3[repostspace]` - Type annotations for
  [RePostPrivate](https://youtype.github.io/types_boto3_docs/types_boto3_repostspace/)
  service.
- `types-boto3[resiliencehub]` - Type annotations for
  [ResilienceHub](https://youtype.github.io/types_boto3_docs/types_boto3_resiliencehub/)
  service.
- `types-boto3[resource-explorer-2]` - Type annotations for
  [ResourceExplorer](https://youtype.github.io/types_boto3_docs/types_boto3_resource_explorer_2/)
  service.
- `types-boto3[resource-groups]` - Type annotations for
  [ResourceGroups](https://youtype.github.io/types_boto3_docs/types_boto3_resource_groups/)
  service.
- `types-boto3[resourcegroupstaggingapi]` - Type annotations for
  [ResourceGroupsTaggingAPI](https://youtype.github.io/types_boto3_docs/types_boto3_resourcegroupstaggingapi/)
  service.
- `types-boto3[robomaker]` - Type annotations for
  [RoboMaker](https://youtype.github.io/types_boto3_docs/types_boto3_robomaker/)
  service.
- `types-boto3[rolesanywhere]` - Type annotations for
  [IAMRolesAnywhere](https://youtype.github.io/types_boto3_docs/types_boto3_rolesanywhere/)
  service.
- `types-boto3[route53]` - Type annotations for
  [Route53](https://youtype.github.io/types_boto3_docs/types_boto3_route53/)
  service.
- `types-boto3[route53-recovery-cluster]` - Type annotations for
  [Route53RecoveryCluster](https://youtype.github.io/types_boto3_docs/types_boto3_route53_recovery_cluster/)
  service.
- `types-boto3[route53-recovery-control-config]` - Type annotations for
  [Route53RecoveryControlConfig](https://youtype.github.io/types_boto3_docs/types_boto3_route53_recovery_control_config/)
  service.
- `types-boto3[route53-recovery-readiness]` - Type annotations for
  [Route53RecoveryReadiness](https://youtype.github.io/types_boto3_docs/types_boto3_route53_recovery_readiness/)
  service.
- `types-boto3[route53domains]` - Type annotations for
  [Route53Domains](https://youtype.github.io/types_boto3_docs/types_boto3_route53domains/)
  service.
- `types-boto3[route53profiles]` - Type annotations for
  [Route53Profiles](https://youtype.github.io/types_boto3_docs/types_boto3_route53profiles/)
  service.
- `types-boto3[route53resolver]` - Type annotations for
  [Route53Resolver](https://youtype.github.io/types_boto3_docs/types_boto3_route53resolver/)
  service.
- `types-boto3[rum]` - Type annotations for
  [CloudWatchRUM](https://youtype.github.io/types_boto3_docs/types_boto3_rum/)
  service.
- `types-boto3[s3]` - Type annotations for
  [S3](https://youtype.github.io/types_boto3_docs/types_boto3_s3/) service.
- `types-boto3[s3control]` - Type annotations for
  [S3Control](https://youtype.github.io/types_boto3_docs/types_boto3_s3control/)
  service.
- `types-boto3[s3outposts]` - Type annotations for
  [S3Outposts](https://youtype.github.io/types_boto3_docs/types_boto3_s3outposts/)
  service.
- `types-boto3[s3tables]` - Type annotations for
  [S3Tables](https://youtype.github.io/types_boto3_docs/types_boto3_s3tables/)
  service.
- `types-boto3[s3vectors]` - Type annotations for
  [S3Vectors](https://youtype.github.io/types_boto3_docs/types_boto3_s3vectors/)
  service.
- `types-boto3[sagemaker]` - Type annotations for
  [SageMaker](https://youtype.github.io/types_boto3_docs/types_boto3_sagemaker/)
  service.
- `types-boto3[sagemaker-a2i-runtime]` - Type annotations for
  [AugmentedAIRuntime](https://youtype.github.io/types_boto3_docs/types_boto3_sagemaker_a2i_runtime/)
  service.
- `types-boto3[sagemaker-edge]` - Type annotations for
  [SagemakerEdgeManager](https://youtype.github.io/types_boto3_docs/types_boto3_sagemaker_edge/)
  service.
- `types-boto3[sagemaker-featurestore-runtime]` - Type annotations for
  [SageMakerFeatureStoreRuntime](https://youtype.github.io/types_boto3_docs/types_boto3_sagemaker_featurestore_runtime/)
  service.
- `types-boto3[sagemaker-geospatial]` - Type annotations for
  [SageMakergeospatialcapabilities](https://youtype.github.io/types_boto3_docs/types_boto3_sagemaker_geospatial/)
  service.
- `types-boto3[sagemaker-metrics]` - Type annotations for
  [SageMakerMetrics](https://youtype.github.io/types_boto3_docs/types_boto3_sagemaker_metrics/)
  service.
- `types-boto3[sagemaker-runtime]` - Type annotations for
  [SageMakerRuntime](https://youtype.github.io/types_boto3_docs/types_boto3_sagemaker_runtime/)
  service.
- `types-boto3[savingsplans]` - Type annotations for
  [SavingsPlans](https://youtype.github.io/types_boto3_docs/types_boto3_savingsplans/)
  service.
- `types-boto3[scheduler]` - Type annotations for
  [EventBridgeScheduler](https://youtype.github.io/types_boto3_docs/types_boto3_scheduler/)
  service.
- `types-boto3[schemas]` - Type annotations for
  [Schemas](https://youtype.github.io/types_boto3_docs/types_boto3_schemas/)
  service.
- `types-boto3[sdb]` - Type annotations for
  [SimpleDB](https://youtype.github.io/types_boto3_docs/types_boto3_sdb/)
  service.
- `types-boto3[secretsmanager]` - Type annotations for
  [SecretsManager](https://youtype.github.io/types_boto3_docs/types_boto3_secretsmanager/)
  service.
- `types-boto3[security-ir]` - Type annotations for
  [SecurityIncidentResponse](https://youtype.github.io/types_boto3_docs/types_boto3_security_ir/)
  service.
- `types-boto3[securityhub]` - Type annotations for
  [SecurityHub](https://youtype.github.io/types_boto3_docs/types_boto3_securityhub/)
  service.
- `types-boto3[securitylake]` - Type annotations for
  [SecurityLake](https://youtype.github.io/types_boto3_docs/types_boto3_securitylake/)
  service.
- `types-boto3[serverlessrepo]` - Type annotations for
  [ServerlessApplicationRepository](https://youtype.github.io/types_boto3_docs/types_boto3_serverlessrepo/)
  service.
- `types-boto3[service-quotas]` - Type annotations for
  [ServiceQuotas](https://youtype.github.io/types_boto3_docs/types_boto3_service_quotas/)
  service.
- `types-boto3[servicecatalog]` - Type annotations for
  [ServiceCatalog](https://youtype.github.io/types_boto3_docs/types_boto3_servicecatalog/)
  service.
- `types-boto3[servicecatalog-appregistry]` - Type annotations for
  [AppRegistry](https://youtype.github.io/types_boto3_docs/types_boto3_servicecatalog_appregistry/)
  service.
- `types-boto3[servicediscovery]` - Type annotations for
  [ServiceDiscovery](https://youtype.github.io/types_boto3_docs/types_boto3_servicediscovery/)
  service.
- `types-boto3[ses]` - Type annotations for
  [SES](https://youtype.github.io/types_boto3_docs/types_boto3_ses/) service.
- `types-boto3[sesv2]` - Type annotations for
  [SESV2](https://youtype.github.io/types_boto3_docs/types_boto3_sesv2/)
  service.
- `types-boto3[shield]` - Type annotations for
  [Shield](https://youtype.github.io/types_boto3_docs/types_boto3_shield/)
  service.
- `types-boto3[signer]` - Type annotations for
  [Signer](https://youtype.github.io/types_boto3_docs/types_boto3_signer/)
  service.
- `types-boto3[simspaceweaver]` - Type annotations for
  [SimSpaceWeaver](https://youtype.github.io/types_boto3_docs/types_boto3_simspaceweaver/)
  service.
- `types-boto3[sms]` - Type annotations for
  [SMS](https://youtype.github.io/types_boto3_docs/types_boto3_sms/) service.
- `types-boto3[snow-device-management]` - Type annotations for
  [SnowDeviceManagement](https://youtype.github.io/types_boto3_docs/types_boto3_snow_device_management/)
  service.
- `types-boto3[snowball]` - Type annotations for
  [Snowball](https://youtype.github.io/types_boto3_docs/types_boto3_snowball/)
  service.
- `types-boto3[sns]` - Type annotations for
  [SNS](https://youtype.github.io/types_boto3_docs/types_boto3_sns/) service.
- `types-boto3[socialmessaging]` - Type annotations for
  [EndUserMessagingSocial](https://youtype.github.io/types_boto3_docs/types_boto3_socialmessaging/)
  service.
- `types-boto3[sqs]` - Type annotations for
  [SQS](https://youtype.github.io/types_boto3_docs/types_boto3_sqs/) service.
- `types-boto3[ssm]` - Type annotations for
  [SSM](https://youtype.github.io/types_boto3_docs/types_boto3_ssm/) service.
- `types-boto3[ssm-contacts]` - Type annotations for
  [SSMContacts](https://youtype.github.io/types_boto3_docs/types_boto3_ssm_contacts/)
  service.
- `types-boto3[ssm-guiconnect]` - Type annotations for
  [SSMGUIConnect](https://youtype.github.io/types_boto3_docs/types_boto3_ssm_guiconnect/)
  service.
- `types-boto3[ssm-incidents]` - Type annotations for
  [SSMIncidents](https://youtype.github.io/types_boto3_docs/types_boto3_ssm_incidents/)
  service.
- `types-boto3[ssm-quicksetup]` - Type annotations for
  [SystemsManagerQuickSetup](https://youtype.github.io/types_boto3_docs/types_boto3_ssm_quicksetup/)
  service.
- `types-boto3[ssm-sap]` - Type annotations for
  [SsmSap](https://youtype.github.io/types_boto3_docs/types_boto3_ssm_sap/)
  service.
- `types-boto3[sso]` - Type annotations for
  [SSO](https://youtype.github.io/types_boto3_docs/types_boto3_sso/) service.
- `types-boto3[sso-admin]` - Type annotations for
  [SSOAdmin](https://youtype.github.io/types_boto3_docs/types_boto3_sso_admin/)
  service.
- `types-boto3[sso-oidc]` - Type annotations for
  [SSOOIDC](https://youtype.github.io/types_boto3_docs/types_boto3_sso_oidc/)
  service.
- `types-boto3[stepfunctions]` - Type annotations for
  [SFN](https://youtype.github.io/types_boto3_docs/types_boto3_stepfunctions/)
  service.
- `types-boto3[storagegateway]` - Type annotations for
  [StorageGateway](https://youtype.github.io/types_boto3_docs/types_boto3_storagegateway/)
  service.
- `types-boto3[sts]` - Type annotations for
  [STS](https://youtype.github.io/types_boto3_docs/types_boto3_sts/) service.
- `types-boto3[supplychain]` - Type annotations for
  [SupplyChain](https://youtype.github.io/types_boto3_docs/types_boto3_supplychain/)
  service.
- `types-boto3[support]` - Type annotations for
  [Support](https://youtype.github.io/types_boto3_docs/types_boto3_support/)
  service.
- `types-boto3[support-app]` - Type annotations for
  [SupportApp](https://youtype.github.io/types_boto3_docs/types_boto3_support_app/)
  service.
- `types-boto3[swf]` - Type annotations for
  [SWF](https://youtype.github.io/types_boto3_docs/types_boto3_swf/) service.
- `types-boto3[synthetics]` - Type annotations for
  [Synthetics](https://youtype.github.io/types_boto3_docs/types_boto3_synthetics/)
  service.
- `types-boto3[taxsettings]` - Type annotations for
  [TaxSettings](https://youtype.github.io/types_boto3_docs/types_boto3_taxsettings/)
  service.
- `types-boto3[textract]` - Type annotations for
  [Textract](https://youtype.github.io/types_boto3_docs/types_boto3_textract/)
  service.
- `types-boto3[timestream-influxdb]` - Type annotations for
  [TimestreamInfluxDB](https://youtype.github.io/types_boto3_docs/types_boto3_timestream_influxdb/)
  service.
- `types-boto3[timestream-query]` - Type annotations for
  [TimestreamQuery](https://youtype.github.io/types_boto3_docs/types_boto3_timestream_query/)
  service.
- `types-boto3[timestream-write]` - Type annotations for
  [TimestreamWrite](https://youtype.github.io/types_boto3_docs/types_boto3_timestream_write/)
  service.
- `types-boto3[tnb]` - Type annotations for
  [TelcoNetworkBuilder](https://youtype.github.io/types_boto3_docs/types_boto3_tnb/)
  service.
- `types-boto3[transcribe]` - Type annotations for
  [TranscribeService](https://youtype.github.io/types_boto3_docs/types_boto3_transcribe/)
  service.
- `types-boto3[transfer]` - Type annotations for
  [Transfer](https://youtype.github.io/types_boto3_docs/types_boto3_transfer/)
  service.
- `types-boto3[translate]` - Type annotations for
  [Translate](https://youtype.github.io/types_boto3_docs/types_boto3_translate/)
  service.
- `types-boto3[trustedadvisor]` - Type annotations for
  [TrustedAdvisorPublicAPI](https://youtype.github.io/types_boto3_docs/types_boto3_trustedadvisor/)
  service.
- `types-boto3[verifiedpermissions]` - Type annotations for
  [VerifiedPermissions](https://youtype.github.io/types_boto3_docs/types_boto3_verifiedpermissions/)
  service.
- `types-boto3[voice-id]` - Type annotations for
  [VoiceID](https://youtype.github.io/types_boto3_docs/types_boto3_voice_id/)
  service.
- `types-boto3[vpc-lattice]` - Type annotations for
  [VPCLattice](https://youtype.github.io/types_boto3_docs/types_boto3_vpc_lattice/)
  service.
- `types-boto3[waf]` - Type annotations for
  [WAF](https://youtype.github.io/types_boto3_docs/types_boto3_waf/) service.
- `types-boto3[waf-regional]` - Type annotations for
  [WAFRegional](https://youtype.github.io/types_boto3_docs/types_boto3_waf_regional/)
  service.
- `types-boto3[wafv2]` - Type annotations for
  [WAFV2](https://youtype.github.io/types_boto3_docs/types_boto3_wafv2/)
  service.
- `types-boto3[wellarchitected]` - Type annotations for
  [WellArchitected](https://youtype.github.io/types_boto3_docs/types_boto3_wellarchitected/)
  service.
- `types-boto3[wisdom]` - Type annotations for
  [ConnectWisdomService](https://youtype.github.io/types_boto3_docs/types_boto3_wisdom/)
  service.
- `types-boto3[workdocs]` - Type annotations for
  [WorkDocs](https://youtype.github.io/types_boto3_docs/types_boto3_workdocs/)
  service.
- `types-boto3[workmail]` - Type annotations for
  [WorkMail](https://youtype.github.io/types_boto3_docs/types_boto3_workmail/)
  service.
- `types-boto3[workmailmessageflow]` - Type annotations for
  [WorkMailMessageFlow](https://youtype.github.io/types_boto3_docs/types_boto3_workmailmessageflow/)
  service.
- `types-boto3[workspaces]` - Type annotations for
  [WorkSpaces](https://youtype.github.io/types_boto3_docs/types_boto3_workspaces/)
  service.
- `types-boto3[workspaces-instances]` - Type annotations for
  [WorkspacesInstances](https://youtype.github.io/types_boto3_docs/types_boto3_workspaces_instances/)
  service.
- `types-boto3[workspaces-thin-client]` - Type annotations for
  [WorkSpacesThinClient](https://youtype.github.io/types_boto3_docs/types_boto3_workspaces_thin_client/)
  service.
- `types-boto3[workspaces-web]` - Type annotations for
  [WorkSpacesWeb](https://youtype.github.io/types_boto3_docs/types_boto3_workspaces_web/)
  service.
- `types-boto3[xray]` - Type annotations for
  [XRay](https://youtype.github.io/types_boto3_docs/types_boto3_xray/) service.
