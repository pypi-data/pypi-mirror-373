# AWS Frontend Web App Deploy Stack

[![GitHub](https://img.shields.io/github/license/gammarers/aws-frontend-web-app-deploy-stack?style=flat-square)](https://github.com/gammarers/aws-frontend-web-app-deploy-stack/blob/main/LICENSE)
[![npm (scoped)](https://img.shields.io/npm/v/@gammarers/aws-frontend-web-app-deploy-stack?style=flat-square)](https://www.npmjs.com/package/@gammarers/aws-frontend-web-app-deploy-stack)
[![PyPI](https://img.shields.io/pypi/v/gammarers.aws-frontend-web-app-deploy-stack?style=flat-square)](https://pypi.org/project/gammarers.aws-frontend-web-app-deploy-stack/)
[![Nuget](https://img.shields.io/nuget/v/Gammarers.CDK.AWS.FrontendWebAppDeployStack?style=flat-square)](https://www.nuget.org/packages/Gammarers.CDK.AWS.FrontendWebAppDeployStack/)
[![GitHub Workflow Status (branch)](https://img.shields.io/github/actions/workflow/status/gammarers/aws-frontend-web-app-deploy-stack/release.yml?branch=main&label=release&style=flat-square)](https://github.com/gammarers/aws-frontend-web-app-deploy-stack/actions/workflows/release.yml)
[![GitHub release (latest SemVer)](https://img.shields.io/github/v/release/gammarers/aws-frontend-web-app-deploy-stack?sort=semver&style=flat-square)](https://github.com/gammarers/aws-frontend-web-app-deploy-stack/releases)

[![View on Construct Hub](https://constructs.dev/badge?package=@gammarers/aws-frontend-web-app-deploy-stack)](https://constructs.dev/packages/@gammarers/aws-frontend-web-app-deploy-stack)

This is an AWS CDK Construct to make deploying a Frontend Web App (SPA) deploy to S3 behind CloudFront.

## Install

### TypeScript

#### install by npm

```shell
npm install @gammarers/aws-frontend-web-app-deploy-stack
```

#### install by yarn

```shell
yarn add @gammarers/aws-frontend-web-app-deploy-stack
```

#### install by pnpm

```shell
pnpm add @gammarers/aws-frontend-web-app-deploy-stack
```

#### install by bun

```shell
bun add @gammarers/aws-frontend-web-app-deploy-stack
```

### Python

```shell
pip install gammarers.aws-frontend-web-app-deploy-stack
```

### C# / .NET

```shell
dotnet add package Gammarers.CDK.AWS.FrontendWebAppDeployStack
```

## Example

```python
import { FrontendWebAppDeployStack } from '@gammarers/aws-frontend-web-app-deploy-stack';

new FrontendWebAppDeployStack(app, 'FrontendWebAppDeployStack', {
  env: { account: '012345678901', region: 'us-east-1' },
  domainName: 'example.com',
  hostedZoneId: 'Z0000000000000000000Q',
  originBucketName: 'frontend-web-app-example-origin-bucket', // new create in this stack
  deploySourceAssetPath: 'website/',
  logBucketArn: 'arn:aws:s3:::frontend-web-app-example-access-log-bucket', // already created
});
```

## License

This project is licensed under the Apache-2.0 License.
