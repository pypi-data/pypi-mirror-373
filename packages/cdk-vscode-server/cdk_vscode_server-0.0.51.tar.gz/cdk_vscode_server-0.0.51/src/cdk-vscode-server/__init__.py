r'''
![Source](https://img.shields.io/github/stars/MV-Consulting/cdk-vscode-server?logo=github&label=GitHub%20Stars)
[![Build Status](https://github.com/MV-Consulting/cdk-vscode-server/actions/workflows/build.yml/badge.svg)](https://github.com/MV-Consulting/cdk-vscode-server/actions/workflows/build.yml)
[![ESLint Code Formatting](https://img.shields.io/badge/code_style-eslint-brightgreen.svg)](https://eslint.org)
[![Latest release](https://img.shields.io/github/release/MV-Consulting/cdk-vscode-server.svg)](https://github.com/MV-Consulting/cdk-vscode-server/releases)
![GitHub](https://img.shields.io/github/license/MV-Consulting/cdk-vscode-server)
[![npm](https://img.shields.io/npm/dt/@mavogel/cdk-vscode-server?label=npm&color=orange)](https://www.npmjs.com/package/@mavogel/cdk-vscode-server)
[![typescript](https://img.shields.io/badge/jsii-typescript-blueviolet.svg)](https://www.npmjs.com/package/@mavogel/cdk-vscode-server)

# cdk-vscode-server

Running your dev IDE vscode on AWS for development and workshop purposes.

> [!Note]
> This construct is designed for workshop purposes and does not fulfill all security and authentication best practices.

![EXPERIMENTAL](https://img.shields.io/badge/stability-experimantal-orange?style=for-the-badge)**<br>This is an early version of the package. The API will change while I
we implement new features. Therefore make sure you use an exact version in your `package.json` before it reaches 1.0.0.**

## Table of Contents

* [Features](#features)
* [Usage](#usage)
* [Solution Design](#solution-design)
* [Inspiration](#inspiration)

## Features

* ⚡ **Quick Setup**: Spin up and configure your [vscode](https://code.visualstudio.com/) server in under 10 minutes in your AWS account
* 📏 **Best Practice Setup**: Set up with [projen](https://projen.io/) and a [single configuration file](./.projenrc.ts) to keep your changes centralized.
* 🤹‍♂️ **Pre-installed packages**: Besides the [vscode](https://code.visualstudio.com/) server, other tools and software packages such as `git`, `docker`, `awscli` `nodejs` and `python` are pre-installed on the EC2 instance.
* 🏗️ **Extensibility**: Pass in properties to the construct, which start with `additional*`. They allow you to extend the configuration to your needs. There are more to come...

## Usage

The following steps get you started:

1. Create a new `awscdk-app` via

```bash
npx projen new awscdk-app-ts --package-manager=npm
```

1. Add `@mavogel/cdk-vscode-server` as a dependency to your project in the `.projenrc.ts` file
2. Run `npx projen` to install it
3. Add the following to the `src/main.ts` file:

```python
import { App, Stack, StackProps } from 'aws-cdk-lib';
import * as ec2 from 'aws-cdk-lib/aws-ec2';
import * as iam from 'aws-cdk-lib/aws-iam';
import { Construct } from 'constructs';
import {
  LinuxArchitectureType,
  LinuxFlavorType,
  VSCodeServer
} from '@mavogel/cdk-vscode-server';

export class MyStack extends Stack {
  constructor(scope: Construct, id: string, props: StackProps = {}) {
    super(scope, id, props);

    new VSCodeServer(this, 'vscode', {
      // for example (or simply use the defaults by not setting the properties)
      instanceVolumeSize: 8,
      instanceClass: ec2.InstanceClass.M7G,
      instanceSize: ec2.InstanceSize.LARGE,
      instanceOperatingSystem: LinuxFlavorType.UBUNTU_22,
      instanceCpuArchitecture: LinuxArchitectureType.ARM,

      // 👇🏽 or if you want to give the InstanceRole more permissions
      additionalInstanceRolePolicies: [
        new iam.PolicyStatement({
          effect: iam.Effect.ALLOW,
          actions: [
            'codebuild:*',
          ],
          resources: [
            `arn:aws:codebuild:*:${Stack.of(this).account}:*/*`,
          ],
        }),
      ]

      // and more... 💡
    });
  }
}

const env = {
  account: '123456789912',
  region: 'eu-central-1',
};

const app = new App();
new MyStack(app, 'vscode-server', { env });
app.synth();
```

and deploy it

```bash
npx projen build
npx projen deploy
```

with the output

```console
✨  Deployment time: 509.87s

Outputs:
dev.vscodedomainName6729AA39 = https://d1foo65bar4baz.cloudfront.net/?folder=/Workshop
dev.vscodepassword64FBCA12 = foobarbaz
```

See the [examples](./examples) folder for more inspiration.

1. Then open the domain name in your favorite browser and you'd see the following login screen:
   ![vscode-server-ui-login](docs/img/vscode-server-ui-login-min.png)
2. After entering the password, you are logged into VSCode and can start coding :tada:

![vscode-server-ui](docs/img/vscode-server-ui-min.png)

> [!Important]
> There are issues with copy pasting into the VSCode terminal within the Firefox browser (2025-01-12)

## Solution Design

<details>
  <summary>... if you're curious about click here for the details</summary>

![vscode-server-solution-design](docs/img/vscode-server.drawio-min.png)

</details>

## Inspiration

This project was created based on the following inspiration

* [vscode-on-ec2-for-prototyping](https://github.com/aws-samples/vscode-on-ec2-for-prototyping): as baseline, which unfortunately was outdated
* [aws-terraform-dev-container](https://github.com/awslabs/aws-terraform-dev-container): as baseline for terraform, but unfortunately also outdated
* [java-on-aws-workshop-ide-only.yaml](https://github.com/aws-samples/java-on-aws/blob/main/labs/unicorn-store/infrastructure/cfn/java-on-aws-workshop-ide-only.yaml): an already synthesized cloudformation stack, which used mostly python as the custom resources
* [fleet-workshop-team-stack-self.json](https://static.us-east-1.prod.workshops.aws/public/cc4aa67e-5b7a-4df1-abf7-c42502899a25/assets/fleet-workshop-team-stack-self.json): also an already synthesized cloudformation stack, which did much more as I currently implemented here.
* [eks-workshop-vscode-cfn.yaml](https://github.com/aws-samples/eks-workshop-v2/blob/main/lab/cfn/eks-workshop-vscode-cfn.yaml): another great baseline

## 🚀 Unlock the Full Potential of Your AWS Cloud Infrastructure

Hi, I’m Manuel, an AWS expert passionate about empowering businesses with **scalable, resilient, and cost-optimized cloud solutions**. With **MV Consulting**, I specialize in crafting **tailored AWS architectures** and **DevOps-driven workflows** that not only meet your current needs but grow with you.

---


### 🌟 Why Work With Me?

✔️ **Tailored AWS Solutions:** Every business is unique, so I design custom solutions that fit your goals and challenges.
✔️ **Well-Architected Designs:** From scalability to security, my solutions align with AWS Well-Architected Framework.
✔️ **Cloud-Native Focus:** I specialize in modern, cloud-native systems that embrace the full potential of AWS.
✔️ **Business-Driven Tech:** Technology should serve your business, not the other way around.

---


### 🛠 What I Bring to the Table

🔑 **12x AWS Certifications**
I’m **AWS Certified Solutions Architect and DevOps – Professional** and hold numerous additional certifications, so you can trust I’ll bring industry best practices to your projects. Feel free to explose by [badges](https://www.credly.com/users/manuel-vogel)

⚙️ **Infrastructure as Code (IaC)**
With deep expertise in **AWS CDK** and **Terraform**, I ensure your infrastructure is automated, maintainable, and scalable.

📦 **DevOps Expertise**
From CI/CD pipelines with **GitHub Actions** and **GitLab CI** to container orchestration **Kubernetes** and others, I deliver workflows that are smooth and efficient.

🌐 **Hands-On Experience**
With over **7 years of AWS experience** and a decade in the tech world, I’ve delivered solutions for companies large and small. My open-source contributions showcase my commitment to transparency and innovation. Feel free to explore my [GitHub profile](https://github.com/mavogel)

---


### 💼 Let’s Build Something Great Together

I know that choosing the right partner is critical to your success. When you work with me, you’re not just contracting an engineer – you’re gaining a trusted advisor and hands-on expert who cares about your business as much as you do.

✔️ **Direct Collaboration**: No middlemen or red tape – you work with me directly.
✔️ **Transparent Process**: Expect open communication, clear timelines, and visible results.
✔️ **Real Value**: My solutions focus on delivering measurable impact for your business.

<a href="https://tinyurl.com/mvc-15min"><img alt="Schedule your call" src="https://img.shields.io/badge/schedule%20your%20call-success.svg?style=for-the-badge"/></a>

---


## 🙌 Acknowledgements

Big shoutout to the amazing team behind [Projen](https://github.com/projen/projen)!
Their groundbreaking work simplifies cloud infrastructure projects and inspires us every day. 💡

## Author

[Manuel Vogel](https://manuel-vogel.de/about/)

[![](https://img.shields.io/badge/LinkedIn-0077B5?style=for-the-badge&logo=linkedin&logoColor=white)](https://www.linkedin.com/in/manuel-vogel)
[![](https://img.shields.io/badge/GitHub-2b3137?style=for-the-badge&logo=github&logoColor=white)](https://github.com/mavogel)
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

import aws_cdk.aws_ec2 as _aws_cdk_aws_ec2_ceddda9d
import aws_cdk.aws_iam as _aws_cdk_aws_iam_ceddda9d
import constructs as _constructs_77d1e7e8


@jsii.enum(jsii_type="@mavogel/cdk-vscode-server.LinuxArchitectureType")
class LinuxArchitectureType(enum.Enum):
    '''(experimental) The architecture of the cpu you want to run vscode server on.

    :stability: experimental
    '''

    ARM = "ARM"
    '''(experimental) ARM architecture.

    :stability: experimental
    '''
    AMD64 = "AMD64"
    '''(experimental) AMD64 architecture.

    :stability: experimental
    '''


@jsii.enum(jsii_type="@mavogel/cdk-vscode-server.LinuxFlavorType")
class LinuxFlavorType(enum.Enum):
    '''(experimental) The flavor of linux you want to run vscode server on.

    :stability: experimental
    '''

    UBUNTU_22 = "UBUNTU_22"
    '''(experimental) Ubuntu 22.

    :stability: experimental
    '''
    UBUNTU_24 = "UBUNTU_24"
    '''(experimental) Ubuntu 24.

    :stability: experimental
    '''
    AMAZON_LINUX_2023 = "AMAZON_LINUX_2023"
    '''(experimental) Amazon Linux 2023.

    :stability: experimental
    '''


class VSCodeServer(
    _constructs_77d1e7e8.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="@mavogel/cdk-vscode-server.VSCodeServer",
):
    '''(experimental) VSCodeServer - spin it up in under 10 minutes.

    :stability: experimental
    '''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        additional_instance_role_policies: typing.Optional[typing.Sequence[_aws_cdk_aws_iam_ceddda9d.PolicyStatement]] = None,
        additional_tags: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        dev_server_base_path: typing.Optional[builtins.str] = None,
        dev_server_port: typing.Optional[jsii.Number] = None,
        home_folder: typing.Optional[builtins.str] = None,
        instance_class: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.InstanceClass] = None,
        instance_cpu_architecture: typing.Optional[LinuxArchitectureType] = None,
        instance_name: typing.Optional[builtins.str] = None,
        instance_operating_system: typing.Optional[LinuxFlavorType] = None,
        instance_size: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.InstanceSize] = None,
        instance_volume_size: typing.Optional[jsii.Number] = None,
        vscode_password: typing.Optional[builtins.str] = None,
        vscode_user: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param additional_instance_role_policies: (experimental) Additional instance role policies. Default: - []
        :param additional_tags: (experimental) Additional tags to add to the instance. Default: - {}
        :param dev_server_base_path: (experimental) Base path for the application to be added to Nginx sites-available list. Default: - app
        :param dev_server_port: (experimental) Port for the DevServer. Default: - 8081
        :param home_folder: (experimental) Folder to open in VS Code server. Default: - /Workshop
        :param instance_class: (experimental) VSCode Server EC2 instance class. Default: - m7g
        :param instance_cpu_architecture: (experimental) VSCode Server EC2 cpu architecture for the operating system. Default: - arm
        :param instance_name: (experimental) VSCode Server EC2 instance name. Default: - VSCodeServer
        :param instance_operating_system: (experimental) VSCode Server EC2 operating system. Default: - Ubuntu-22
        :param instance_size: (experimental) VSCode Server EC2 instance size. Default: - xlarge
        :param instance_volume_size: (experimental) VSCode Server EC2 instance volume size in GB. Default: - 40
        :param vscode_password: (experimental) Password for VSCode Server. Default: - empty and will then be generated
        :param vscode_user: (experimental) UserName for VSCode Server. Default: - participant

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__13d98894e731d8d5e45fa4088dfd79af04a4cb66cead591188c4ba44d922873c)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = VSCodeServerProps(
            additional_instance_role_policies=additional_instance_role_policies,
            additional_tags=additional_tags,
            dev_server_base_path=dev_server_base_path,
            dev_server_port=dev_server_port,
            home_folder=home_folder,
            instance_class=instance_class,
            instance_cpu_architecture=instance_cpu_architecture,
            instance_name=instance_name,
            instance_operating_system=instance_operating_system,
            instance_size=instance_size,
            instance_volume_size=instance_volume_size,
            vscode_password=vscode_password,
            vscode_user=vscode_user,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @builtins.property
    @jsii.member(jsii_name="domainName")
    def domain_name(self) -> builtins.str:
        '''(experimental) The name of the domain the server is reachable.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "domainName"))

    @builtins.property
    @jsii.member(jsii_name="password")
    def password(self) -> builtins.str:
        '''(experimental) The password to login to the server.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "password"))


@jsii.data_type(
    jsii_type="@mavogel/cdk-vscode-server.VSCodeServerProps",
    jsii_struct_bases=[],
    name_mapping={
        "additional_instance_role_policies": "additionalInstanceRolePolicies",
        "additional_tags": "additionalTags",
        "dev_server_base_path": "devServerBasePath",
        "dev_server_port": "devServerPort",
        "home_folder": "homeFolder",
        "instance_class": "instanceClass",
        "instance_cpu_architecture": "instanceCpuArchitecture",
        "instance_name": "instanceName",
        "instance_operating_system": "instanceOperatingSystem",
        "instance_size": "instanceSize",
        "instance_volume_size": "instanceVolumeSize",
        "vscode_password": "vscodePassword",
        "vscode_user": "vscodeUser",
    },
)
class VSCodeServerProps:
    def __init__(
        self,
        *,
        additional_instance_role_policies: typing.Optional[typing.Sequence[_aws_cdk_aws_iam_ceddda9d.PolicyStatement]] = None,
        additional_tags: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        dev_server_base_path: typing.Optional[builtins.str] = None,
        dev_server_port: typing.Optional[jsii.Number] = None,
        home_folder: typing.Optional[builtins.str] = None,
        instance_class: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.InstanceClass] = None,
        instance_cpu_architecture: typing.Optional[LinuxArchitectureType] = None,
        instance_name: typing.Optional[builtins.str] = None,
        instance_operating_system: typing.Optional[LinuxFlavorType] = None,
        instance_size: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.InstanceSize] = None,
        instance_volume_size: typing.Optional[jsii.Number] = None,
        vscode_password: typing.Optional[builtins.str] = None,
        vscode_user: typing.Optional[builtins.str] = None,
    ) -> None:
        '''(experimental) Properties for the VSCodeServer construct.

        :param additional_instance_role_policies: (experimental) Additional instance role policies. Default: - []
        :param additional_tags: (experimental) Additional tags to add to the instance. Default: - {}
        :param dev_server_base_path: (experimental) Base path for the application to be added to Nginx sites-available list. Default: - app
        :param dev_server_port: (experimental) Port for the DevServer. Default: - 8081
        :param home_folder: (experimental) Folder to open in VS Code server. Default: - /Workshop
        :param instance_class: (experimental) VSCode Server EC2 instance class. Default: - m7g
        :param instance_cpu_architecture: (experimental) VSCode Server EC2 cpu architecture for the operating system. Default: - arm
        :param instance_name: (experimental) VSCode Server EC2 instance name. Default: - VSCodeServer
        :param instance_operating_system: (experimental) VSCode Server EC2 operating system. Default: - Ubuntu-22
        :param instance_size: (experimental) VSCode Server EC2 instance size. Default: - xlarge
        :param instance_volume_size: (experimental) VSCode Server EC2 instance volume size in GB. Default: - 40
        :param vscode_password: (experimental) Password for VSCode Server. Default: - empty and will then be generated
        :param vscode_user: (experimental) UserName for VSCode Server. Default: - participant

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2e462747a4e6316ff07a1ca12065fecb7b143031e2052b9b3ed692a4d9a458c7)
            check_type(argname="argument additional_instance_role_policies", value=additional_instance_role_policies, expected_type=type_hints["additional_instance_role_policies"])
            check_type(argname="argument additional_tags", value=additional_tags, expected_type=type_hints["additional_tags"])
            check_type(argname="argument dev_server_base_path", value=dev_server_base_path, expected_type=type_hints["dev_server_base_path"])
            check_type(argname="argument dev_server_port", value=dev_server_port, expected_type=type_hints["dev_server_port"])
            check_type(argname="argument home_folder", value=home_folder, expected_type=type_hints["home_folder"])
            check_type(argname="argument instance_class", value=instance_class, expected_type=type_hints["instance_class"])
            check_type(argname="argument instance_cpu_architecture", value=instance_cpu_architecture, expected_type=type_hints["instance_cpu_architecture"])
            check_type(argname="argument instance_name", value=instance_name, expected_type=type_hints["instance_name"])
            check_type(argname="argument instance_operating_system", value=instance_operating_system, expected_type=type_hints["instance_operating_system"])
            check_type(argname="argument instance_size", value=instance_size, expected_type=type_hints["instance_size"])
            check_type(argname="argument instance_volume_size", value=instance_volume_size, expected_type=type_hints["instance_volume_size"])
            check_type(argname="argument vscode_password", value=vscode_password, expected_type=type_hints["vscode_password"])
            check_type(argname="argument vscode_user", value=vscode_user, expected_type=type_hints["vscode_user"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if additional_instance_role_policies is not None:
            self._values["additional_instance_role_policies"] = additional_instance_role_policies
        if additional_tags is not None:
            self._values["additional_tags"] = additional_tags
        if dev_server_base_path is not None:
            self._values["dev_server_base_path"] = dev_server_base_path
        if dev_server_port is not None:
            self._values["dev_server_port"] = dev_server_port
        if home_folder is not None:
            self._values["home_folder"] = home_folder
        if instance_class is not None:
            self._values["instance_class"] = instance_class
        if instance_cpu_architecture is not None:
            self._values["instance_cpu_architecture"] = instance_cpu_architecture
        if instance_name is not None:
            self._values["instance_name"] = instance_name
        if instance_operating_system is not None:
            self._values["instance_operating_system"] = instance_operating_system
        if instance_size is not None:
            self._values["instance_size"] = instance_size
        if instance_volume_size is not None:
            self._values["instance_volume_size"] = instance_volume_size
        if vscode_password is not None:
            self._values["vscode_password"] = vscode_password
        if vscode_user is not None:
            self._values["vscode_user"] = vscode_user

    @builtins.property
    def additional_instance_role_policies(
        self,
    ) -> typing.Optional[typing.List[_aws_cdk_aws_iam_ceddda9d.PolicyStatement]]:
        '''(experimental) Additional instance role policies.

        :default: - []

        :stability: experimental
        '''
        result = self._values.get("additional_instance_role_policies")
        return typing.cast(typing.Optional[typing.List[_aws_cdk_aws_iam_ceddda9d.PolicyStatement]], result)

    @builtins.property
    def additional_tags(
        self,
    ) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        '''(experimental) Additional tags to add to the instance.

        :default: - {}

        :stability: experimental
        '''
        result = self._values.get("additional_tags")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], result)

    @builtins.property
    def dev_server_base_path(self) -> typing.Optional[builtins.str]:
        '''(experimental) Base path for the application to be added to Nginx sites-available list.

        :default: - app

        :stability: experimental
        '''
        result = self._values.get("dev_server_base_path")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def dev_server_port(self) -> typing.Optional[jsii.Number]:
        '''(experimental) Port for the DevServer.

        :default: - 8081

        :stability: experimental
        '''
        result = self._values.get("dev_server_port")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def home_folder(self) -> typing.Optional[builtins.str]:
        '''(experimental) Folder to open in VS Code server.

        :default: - /Workshop

        :stability: experimental
        '''
        result = self._values.get("home_folder")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def instance_class(
        self,
    ) -> typing.Optional[_aws_cdk_aws_ec2_ceddda9d.InstanceClass]:
        '''(experimental) VSCode Server EC2 instance class.

        :default: - m7g

        :stability: experimental
        '''
        result = self._values.get("instance_class")
        return typing.cast(typing.Optional[_aws_cdk_aws_ec2_ceddda9d.InstanceClass], result)

    @builtins.property
    def instance_cpu_architecture(self) -> typing.Optional[LinuxArchitectureType]:
        '''(experimental) VSCode Server EC2 cpu architecture for the operating system.

        :default: - arm

        :stability: experimental
        '''
        result = self._values.get("instance_cpu_architecture")
        return typing.cast(typing.Optional[LinuxArchitectureType], result)

    @builtins.property
    def instance_name(self) -> typing.Optional[builtins.str]:
        '''(experimental) VSCode Server EC2 instance name.

        :default: - VSCodeServer

        :stability: experimental
        '''
        result = self._values.get("instance_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def instance_operating_system(self) -> typing.Optional[LinuxFlavorType]:
        '''(experimental) VSCode Server EC2 operating system.

        :default: - Ubuntu-22

        :stability: experimental
        '''
        result = self._values.get("instance_operating_system")
        return typing.cast(typing.Optional[LinuxFlavorType], result)

    @builtins.property
    def instance_size(self) -> typing.Optional[_aws_cdk_aws_ec2_ceddda9d.InstanceSize]:
        '''(experimental) VSCode Server EC2 instance size.

        :default: - xlarge

        :stability: experimental
        '''
        result = self._values.get("instance_size")
        return typing.cast(typing.Optional[_aws_cdk_aws_ec2_ceddda9d.InstanceSize], result)

    @builtins.property
    def instance_volume_size(self) -> typing.Optional[jsii.Number]:
        '''(experimental) VSCode Server EC2 instance volume size in GB.

        :default: - 40

        :stability: experimental
        '''
        result = self._values.get("instance_volume_size")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def vscode_password(self) -> typing.Optional[builtins.str]:
        '''(experimental) Password for VSCode Server.

        :default: - empty and will then be generated

        :stability: experimental
        '''
        result = self._values.get("vscode_password")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def vscode_user(self) -> typing.Optional[builtins.str]:
        '''(experimental) UserName for VSCode Server.

        :default: - participant

        :stability: experimental
        '''
        result = self._values.get("vscode_user")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "VSCodeServerProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "LinuxArchitectureType",
    "LinuxFlavorType",
    "VSCodeServer",
    "VSCodeServerProps",
]

publication.publish()

def _typecheckingstub__13d98894e731d8d5e45fa4088dfd79af04a4cb66cead591188c4ba44d922873c(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    additional_instance_role_policies: typing.Optional[typing.Sequence[_aws_cdk_aws_iam_ceddda9d.PolicyStatement]] = None,
    additional_tags: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    dev_server_base_path: typing.Optional[builtins.str] = None,
    dev_server_port: typing.Optional[jsii.Number] = None,
    home_folder: typing.Optional[builtins.str] = None,
    instance_class: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.InstanceClass] = None,
    instance_cpu_architecture: typing.Optional[LinuxArchitectureType] = None,
    instance_name: typing.Optional[builtins.str] = None,
    instance_operating_system: typing.Optional[LinuxFlavorType] = None,
    instance_size: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.InstanceSize] = None,
    instance_volume_size: typing.Optional[jsii.Number] = None,
    vscode_password: typing.Optional[builtins.str] = None,
    vscode_user: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2e462747a4e6316ff07a1ca12065fecb7b143031e2052b9b3ed692a4d9a458c7(
    *,
    additional_instance_role_policies: typing.Optional[typing.Sequence[_aws_cdk_aws_iam_ceddda9d.PolicyStatement]] = None,
    additional_tags: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    dev_server_base_path: typing.Optional[builtins.str] = None,
    dev_server_port: typing.Optional[jsii.Number] = None,
    home_folder: typing.Optional[builtins.str] = None,
    instance_class: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.InstanceClass] = None,
    instance_cpu_architecture: typing.Optional[LinuxArchitectureType] = None,
    instance_name: typing.Optional[builtins.str] = None,
    instance_operating_system: typing.Optional[LinuxFlavorType] = None,
    instance_size: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.InstanceSize] = None,
    instance_volume_size: typing.Optional[jsii.Number] = None,
    vscode_password: typing.Optional[builtins.str] = None,
    vscode_user: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass
