r'''
# Amazon EKS V2 Construct Library

<!--BEGIN STABILITY BANNER-->---


![cdk-constructs: Experimental](https://img.shields.io/badge/cdk--constructs-experimental-important.svg?style=for-the-badge)

> The APIs of higher level constructs in this module are experimental and under active development.
> They are subject to non-backward compatible changes or removal in any future version. These are
> not subject to the [Semantic Versioning](https://semver.org/) model and breaking changes will be
> announced in the release notes. This means that while you may use them, you may need to update
> your source code when upgrading to a newer version of this package.

---
<!--END STABILITY BANNER-->

The eks-v2-alpha module is a rewrite of the existing aws-eks module (https://docs.aws.amazon.com/cdk/api/v2/docs/aws-cdk-lib.aws_eks-readme.html). This new iteration leverages native L1 CFN resources, replacing the previous custom resource approach for creating EKS clusters and Fargate Profiles.

Compared to the original EKS module, it has the following major changes:

* Use native L1 AWS::EKS::Cluster resource to replace custom resource Custom::AWSCDK-EKS-Cluster
* Use native L1 AWS::EKS::FargateProfile resource to replace custom resource Custom::AWSCDK-EKS-FargateProfile
* Kubectl Handler will not be created by default. It will only be created if users specify it.
* Remove AwsAuth construct. Permissions to the cluster will be managed by Access Entry.
* Remove the limit of 1 cluster per stack
* Remove nested stacks
* API changes to make them more ergonomic.

## Quick start

Here is the minimal example of defining an AWS EKS cluster

```python
cluster = eks.Cluster(self, "hello-eks",
    version=eks.KubernetesVersion.V1_33
)
```

## Architecture

```text
 +-----------------------------------------------+
 | EKS Cluster      | kubectl |  |
 | -----------------|<--------+| Kubectl Handler |
 | AWS::EKS::Cluster             (Optional)      |
 | +--------------------+    +-----------------+ |
 | |                    |    |                 | |
 | | Managed Node Group |    | Fargate Profile | |
 | |                    |    |                 | |
 | +--------------------+    +-----------------+ |
 +-----------------------------------------------+
    ^
    | connect self managed capacity
    +
 +--------------------+
 | Auto Scaling Group |
 +--------------------+
```

In a nutshell:

* EKS Cluster - The cluster endpoint created by EKS.
* Managed Node Group - EC2 worker nodes managed by EKS.
* Fargate Profile - Fargate worker nodes managed by EKS.
* Auto Scaling Group - EC2 worker nodes managed by the user.
* Kubectl Handler (Optional) - Custom resource (i.e Lambda Function) for invoking kubectl commands on the
  cluster - created by CDK

## Provisioning cluster

Creating a new cluster is done using the `Cluster` constructs. The only required property is the kubernetes version.

```python
eks.Cluster(self, "HelloEKS",
    version=eks.KubernetesVersion.V1_33
)
```

You can also use `FargateCluster` to provision a cluster that uses only fargate workers.

```python
eks.FargateCluster(self, "HelloEKS",
    version=eks.KubernetesVersion.V1_33
)
```

**Note: Unlike the previous EKS cluster, `Kubectl Handler` will not
be created by default. It will only be deployed when `kubectlProviderOptions`
property is used.**

```python
from aws_cdk.lambda_layer_kubectl_v33 import KubectlV33Layer


eks.Cluster(self, "hello-eks",
    version=eks.KubernetesVersion.V1_33,
    kubectl_provider_options=eks.KubectlProviderOptions(
        kubectl_layer=KubectlV33Layer(self, "kubectl")
    )
)
```

### EKS Auto Mode

[Amazon EKS Auto Mode](https://aws.amazon.com/eks/auto-mode/) extends AWS management of Kubernetes clusters beyond the cluster itself, allowing AWS to set up and manage the infrastructure that enables the smooth operation of your workloads.

#### Using Auto Mode

While `aws-eks` uses `DefaultCapacityType.NODEGROUP` by default, `aws-eks-v2` uses `DefaultCapacityType.AUTOMODE` as the default capacity type.

Auto Mode is enabled by default when creating a new cluster without specifying any capacity-related properties:

```python
# Create EKS cluster with Auto Mode implicitly enabled
cluster = eks.Cluster(self, "EksAutoCluster",
    version=eks.KubernetesVersion.V1_33
)
```

You can also explicitly enable Auto Mode using `defaultCapacityType`:

```python
# Create EKS cluster with Auto Mode explicitly enabled
cluster = eks.Cluster(self, "EksAutoCluster",
    version=eks.KubernetesVersion.V1_33,
    default_capacity_type=eks.DefaultCapacityType.AUTOMODE
)
```

#### Node Pools

When Auto Mode is enabled, the cluster comes with two default node pools:

* `system`: For running system components and add-ons
* `general-purpose`: For running your application workloads

These node pools are managed automatically by EKS. You can configure which node pools to enable through the `compute` property:

```python
cluster = eks.Cluster(self, "EksAutoCluster",
    version=eks.KubernetesVersion.V1_33,
    default_capacity_type=eks.DefaultCapacityType.AUTOMODE,
    compute=eks.ComputeConfig(
        node_pools=["system", "general-purpose"]
    )
)
```

For more information, see [Create a Node Pool for EKS Auto Mode](https://docs.aws.amazon.com/eks/latest/userguide/create-node-pool.html).

#### Disabling Default Node Pools

You can disable the default node pools entirely by setting an empty array for `nodePools`. This is useful when you want to use Auto Mode features but manage your compute resources separately:

```python
cluster = eks.Cluster(self, "EksAutoCluster",
    version=eks.KubernetesVersion.V1_33,
    default_capacity_type=eks.DefaultCapacityType.AUTOMODE,
    compute=eks.ComputeConfig(
        node_pools=[]
    )
)
```

When node pools are disabled this way, no IAM role will be created for the node pools, preventing deployment failures that would otherwise occur when a role is created without any node pools.

### Node Groups as the default capacity type

If you prefer to manage your own node groups instead of using Auto Mode, you can use the traditional node group approach by specifying `defaultCapacityType` as `NODEGROUP`:

```python
# Create EKS cluster with traditional managed node group
cluster = eks.Cluster(self, "EksCluster",
    version=eks.KubernetesVersion.V1_33,
    default_capacity_type=eks.DefaultCapacityType.NODEGROUP,
    default_capacity=3,  # Number of instances
    default_capacity_instance=ec2.InstanceType.of(ec2.InstanceClass.T3, ec2.InstanceSize.LARGE)
)
```

You can also create a cluster with no initial capacity and add node groups later:

```python
cluster = eks.Cluster(self, "EksCluster",
    version=eks.KubernetesVersion.V1_33,
    default_capacity_type=eks.DefaultCapacityType.NODEGROUP,
    default_capacity=0
)

# Add node groups as needed
cluster.add_nodegroup_capacity("custom-node-group",
    min_size=1,
    max_size=3,
    instance_types=[ec2.InstanceType.of(ec2.InstanceClass.T3, ec2.InstanceSize.LARGE)]
)
```

Read [Managed node groups](#managed-node-groups) for more information on how to add node groups to the cluster.

### Mixed with Auto Mode and Node Groups

You can combine Auto Mode with traditional node groups for specific workload requirements:

```python
cluster = eks.Cluster(self, "Cluster",
    version=eks.KubernetesVersion.V1_33,
    default_capacity_type=eks.DefaultCapacityType.AUTOMODE,
    compute=eks.ComputeConfig(
        node_pools=["system", "general-purpose"]
    )
)

# Add specialized node group for specific workloads
cluster.add_nodegroup_capacity("specialized-workload",
    min_size=1,
    max_size=3,
    instance_types=[ec2.InstanceType.of(ec2.InstanceClass.C5, ec2.InstanceSize.XLARGE)],
    labels={
        "workload": "specialized"
    }
)
```

### Important Notes

1. Auto Mode and traditional capacity management are mutually exclusive at the default capacity level. You cannot opt in to Auto Mode and specify `defaultCapacity` or `defaultCapacityInstance`.
2. When Auto Mode is enabled:

   * The cluster will automatically manage compute resources
   * Node pools cannot be modified, only enabled or disabled
   * EKS will handle scaling and management of the node pools
3. Auto Mode requires specific IAM permissions. The construct will automatically attach the required managed policies.

### Managed node groups

Amazon EKS managed node groups automate the provisioning and lifecycle management of nodes (Amazon EC2 instances) for Amazon EKS Kubernetes clusters.
With Amazon EKS managed node groups, you don't need to separately provision or register the Amazon EC2 instances that provide compute capacity to run your Kubernetes applications. You can create, update, or terminate nodes for your cluster with a single operation. Nodes run using the latest Amazon EKS optimized AMIs in your AWS account while node updates and terminations gracefully drain nodes to ensure that your applications stay available.

> For more details visit [Amazon EKS Managed Node Groups](https://docs.aws.amazon.com/eks/latest/userguide/managed-node-groups.html).

By default, when using `DefaultCapacityType.NODEGROUP`, this library will allocate a managed node group with 2 *m5.large* instances (this instance type suits most common use-cases, and is good value for money).

```python
eks.Cluster(self, "HelloEKS",
    version=eks.KubernetesVersion.V1_33,
    default_capacity_type=eks.DefaultCapacityType.NODEGROUP
)
```

At cluster instantiation time, you can customize the number of instances and their type:

```python
eks.Cluster(self, "HelloEKS",
    version=eks.KubernetesVersion.V1_33,
    default_capacity_type=eks.DefaultCapacityType.NODEGROUP,
    default_capacity=5,
    default_capacity_instance=ec2.InstanceType.of(ec2.InstanceClass.M5, ec2.InstanceSize.SMALL)
)
```

To access the node group that was created on your behalf, you can use `cluster.defaultNodegroup`.

Additional customizations are available post instantiation. To apply them, set the default capacity to 0, and use the `cluster.addNodegroupCapacity` method:

```python
cluster = eks.Cluster(self, "HelloEKS",
    version=eks.KubernetesVersion.V1_33,
    default_capacity_type=eks.DefaultCapacityType.NODEGROUP,
    default_capacity=0
)

cluster.add_nodegroup_capacity("custom-node-group",
    instance_types=[ec2.InstanceType("m5.large")],
    min_size=4,
    disk_size=100
)
```

### Fargate profiles

AWS Fargate is a technology that provides on-demand, right-sized compute
capacity for containers. With AWS Fargate, you no longer have to provision,
configure, or scale groups of virtual machines to run containers. This removes
the need to choose server types, decide when to scale your node groups, or
optimize cluster packing.

You can control which pods start on Fargate and how they run with Fargate
Profiles, which are defined as part of your Amazon EKS cluster.

See [Fargate Considerations](https://docs.aws.amazon.com/eks/latest/userguide/fargate.html#fargate-considerations) in the AWS EKS User Guide.

You can add Fargate Profiles to any EKS cluster defined in your CDK app
through the `addFargateProfile()` method. The following example adds a profile
that will match all pods from the "default" namespace:

```python
# cluster: eks.Cluster

cluster.add_fargate_profile("MyProfile",
    selectors=[eks.Selector(namespace="default")]
)
```

You can also directly use the `FargateProfile` construct to create profiles under different scopes:

```python
# cluster: eks.Cluster

eks.FargateProfile(self, "MyProfile",
    cluster=cluster,
    selectors=[eks.Selector(namespace="default")]
)
```

To create an EKS cluster that **only** uses Fargate capacity, you can use `FargateCluster`.
The following code defines an Amazon EKS cluster with a default Fargate Profile that matches all pods from the "kube-system" and "default" namespaces. It is also configured to [run CoreDNS on Fargate](https://docs.aws.amazon.com/eks/latest/userguide/fargate-getting-started.html#fargate-gs-coredns).

```python
cluster = eks.FargateCluster(self, "MyCluster",
    version=eks.KubernetesVersion.V1_33
)
```

`FargateCluster` will create a default `FargateProfile` which can be accessed via the cluster's `defaultProfile` property. The created profile can also be customized by passing options as with `addFargateProfile`.

**NOTE**: Classic Load Balancers and Network Load Balancers are not supported on
pods running on Fargate. For ingress, we recommend that you use the [ALB Ingress
Controller](https://docs.aws.amazon.com/eks/latest/userguide/alb-ingress.html)
on Amazon EKS (minimum version v1.1.4).

### Endpoint Access

When you create a new cluster, Amazon EKS creates an endpoint for the managed Kubernetes API server that you use to communicate with your cluster (using Kubernetes management tools such as `kubectl`)

You can configure the [cluster endpoint access](https://docs.aws.amazon.com/eks/latest/userguide/cluster-endpoint.html) by using the `endpointAccess` property:

```python
cluster = eks.Cluster(self, "hello-eks",
    version=eks.KubernetesVersion.V1_33,
    endpoint_access=eks.EndpointAccess.PRIVATE
)
```

The default value is `eks.EndpointAccess.PUBLIC_AND_PRIVATE`. Which means the cluster endpoint is accessible from outside of your VPC, but worker node traffic and `kubectl` commands issued by this library stay within your VPC.

### Alb Controller

Some Kubernetes resources are commonly implemented on AWS with the help of the [ALB Controller](https://kubernetes-sigs.github.io/aws-load-balancer-controller/latest/).

From the docs:

> AWS Load Balancer Controller is a controller to help manage Elastic Load Balancers for a Kubernetes cluster.
>
> * It satisfies Kubernetes Ingress resources by provisioning Application Load Balancers.
> * It satisfies Kubernetes Service resources by provisioning Network Load Balancers.

To deploy the controller on your EKS cluster, configure the `albController` property:

```python
eks.Cluster(self, "HelloEKS",
    version=eks.KubernetesVersion.V1_33,
    alb_controller=eks.AlbControllerOptions(
        version=eks.AlbControllerVersion.V2_8_2
    )
)
```

The `albController` requires `defaultCapacity` or at least one nodegroup. If there's no `defaultCapacity` or available
nodegroup for the cluster, the `albController` deployment would fail.

Querying the controller pods should look something like this:

```console
❯ kubectl get pods -n kube-system
NAME                                            READY   STATUS    RESTARTS   AGE
aws-load-balancer-controller-76bd6c7586-d929p   1/1     Running   0          109m
aws-load-balancer-controller-76bd6c7586-fqxph   1/1     Running   0          109m
...
...
```

Every Kubernetes manifest that utilizes the ALB Controller is effectively dependant on the controller.
If the controller is deleted before the manifest, it might result in dangling ELB/ALB resources.
Currently, the EKS construct library does not detect such dependencies, and they should be done explicitly.

For example:

```python
# cluster: eks.Cluster

manifest = cluster.add_manifest("manifest", {})
if cluster.alb_controller:
    manifest.node.add_dependency(cluster.alb_controller)
```

You can specify the VPC of the cluster using the `vpc` and `vpcSubnets` properties:

```python
# vpc: ec2.Vpc


eks.Cluster(self, "HelloEKS",
    version=eks.KubernetesVersion.V1_33,
    vpc=vpc,
    vpc_subnets=[ec2.SubnetSelection(subnet_type=ec2.SubnetType.PRIVATE_WITH_EGRESS)]
)
```

If you do not specify a VPC, one will be created on your behalf, which you can then access via `cluster.vpc`. The cluster VPC will be associated to any EKS managed capacity (i.e Managed Node Groups and Fargate Profiles).

Please note that the `vpcSubnets` property defines the subnets where EKS will place the *control plane* ENIs. To choose
the subnets where EKS will place the worker nodes, please refer to the **Provisioning clusters** section above.

If you allocate self managed capacity, you can specify which subnets should the auto-scaling group use:

```python
# vpc: ec2.Vpc
# cluster: eks.Cluster

cluster.add_auto_scaling_group_capacity("nodes",
    vpc_subnets=ec2.SubnetSelection(subnets=vpc.private_subnets),
    instance_type=ec2.InstanceType("t2.medium")
)
```

There is an additional components you might want to provision within the VPC.

The `KubectlHandler` is a Lambda function responsible to issuing `kubectl` and `helm` commands against the cluster when you add resource manifests to the cluster.

The handler association to the VPC is derived from the `endpointAccess` configuration. The rule of thumb is: *If the cluster VPC can be associated, it will be*.

Breaking this down, it means that if the endpoint exposes private access (via `EndpointAccess.PRIVATE` or `EndpointAccess.PUBLIC_AND_PRIVATE`), and the VPC contains **private** subnets, the Lambda function will be provisioned inside the VPC and use the private subnets to interact with the cluster. This is the common use-case.

If the endpoint does not expose private access (via `EndpointAccess.PUBLIC`) **or** the VPC does not contain private subnets, the function will not be provisioned within the VPC.

If your use-case requires control over the IAM role that the KubeCtl Handler assumes, a custom role can be passed through the ClusterProps (as `kubectlLambdaRole`) of the EKS Cluster construct.

### Kubectl Support

You can choose to have CDK create a `Kubectl Handler` - a Python Lambda Function to
apply k8s manifests using `kubectl apply`. This handler will not be created by default.

To create a `Kubectl Handler`, use `kubectlProviderOptions` when creating the cluster.
`kubectlLayer` is the only required property in `kubectlProviderOptions`.

```python
from aws_cdk.lambda_layer_kubectl_v33 import KubectlV33Layer


eks.Cluster(self, "hello-eks",
    version=eks.KubernetesVersion.V1_33,
    kubectl_provider_options=eks.KubectlProviderOptions(
        kubectl_layer=KubectlV33Layer(self, "kubectl")
    )
)
```

`Kubectl Handler` created along with the cluster will be granted admin permissions to the cluster.

If you want to use an existing kubectl provider function, for example with tight trusted entities on your IAM Roles - you can import the existing provider and then use the imported provider when importing the cluster:

```python
handler_role = iam.Role.from_role_arn(self, "HandlerRole", "arn:aws:iam::123456789012:role/lambda-role")
# get the serivceToken from the custom resource provider
function_arn = lambda_.Function.from_function_name(self, "ProviderOnEventFunc", "ProviderframeworkonEvent-XXX").function_arn
kubectl_provider = eks.KubectlProvider.from_kubectl_provider_attributes(self, "KubectlProvider",
    service_token=function_arn,
    role=handler_role
)

cluster = eks.Cluster.from_cluster_attributes(self, "Cluster",
    cluster_name="cluster",
    kubectl_provider=kubectl_provider
)
```

#### Environment

You can configure the environment of this function by specifying it at cluster instantiation. For example, this can be useful in order to configure an http proxy:

```python
from aws_cdk.lambda_layer_kubectl_v33 import KubectlV33Layer


cluster = eks.Cluster(self, "hello-eks",
    version=eks.KubernetesVersion.V1_33,
    kubectl_provider_options=eks.KubectlProviderOptions(
        kubectl_layer=KubectlV33Layer(self, "kubectl"),
        environment={
            "http_proxy": "http://proxy.myproxy.com"
        }
    )
)
```

#### Runtime

The kubectl handler uses `kubectl`, `helm` and the `aws` CLI in order to
interact with the cluster. These are bundled into AWS Lambda layers included in
the `@aws-cdk/lambda-layer-awscli` and `@aws-cdk/lambda-layer-kubectl` modules.

The version of kubectl used must be compatible with the Kubernetes version of the
cluster. kubectl is supported within one minor version (older or newer) of Kubernetes
(see [Kubernetes version skew policy](https://kubernetes.io/releases/version-skew-policy/#kubectl)).
Depending on which version of kubernetes you're targeting, you will need to use one of
the `@aws-cdk/lambda-layer-kubectl-vXY` packages.

```python
from aws_cdk.lambda_layer_kubectl_v33 import KubectlV33Layer


cluster = eks.Cluster(self, "hello-eks",
    version=eks.KubernetesVersion.V1_33,
    kubectl_provider_options=eks.KubectlProviderOptions(
        kubectl_layer=KubectlV33Layer(self, "kubectl")
    )
)
```

#### Memory

By default, the kubectl provider is configured with 1024MiB of memory. You can use the `memory` option to specify the memory size for the AWS Lambda function:

```python
from aws_cdk.lambda_layer_kubectl_v33 import KubectlV33Layer


eks.Cluster(self, "MyCluster",
    kubectl_provider_options=eks.KubectlProviderOptions(
        kubectl_layer=KubectlV33Layer(self, "kubectl"),
        memory=Size.gibibytes(4)
    ),
    version=eks.KubernetesVersion.V1_33
)
```

### ARM64 Support

Instance types with `ARM64` architecture are supported in both managed nodegroup and self-managed capacity. Simply specify an ARM64 `instanceType` (such as `m6g.medium`), and the latest
Amazon Linux 2 AMI for ARM64 will be automatically selected.

```python
# cluster: eks.Cluster

# add a managed ARM64 nodegroup
cluster.add_nodegroup_capacity("extra-ng-arm",
    instance_types=[ec2.InstanceType("m6g.medium")],
    min_size=2
)

# add a self-managed ARM64 nodegroup
cluster.add_auto_scaling_group_capacity("self-ng-arm",
    instance_type=ec2.InstanceType("m6g.medium"),
    min_capacity=2
)
```

### Masters Role

When you create a cluster, you can specify a `mastersRole`. The `Cluster` construct will associate this role with `AmazonEKSClusterAdminPolicy` through [Access Entry](https://docs.aws.amazon.com/eks/latest/userguide/access-policy-permissions.html).

```python
# role: iam.Role

eks.Cluster(self, "HelloEKS",
    version=eks.KubernetesVersion.V1_33,
    masters_role=role
)
```

If you do not specify it, you won't have access to the cluster from outside of the CDK application.

### Encryption

When you create an Amazon EKS cluster, envelope encryption of Kubernetes secrets using the AWS Key Management Service (AWS KMS) can be enabled.
The documentation on [creating a cluster](https://docs.aws.amazon.com/eks/latest/userguide/create-cluster.html)
can provide more details about the customer master key (CMK) that can be used for the encryption.

You can use the `secretsEncryptionKey` to configure which key the cluster will use to encrypt Kubernetes secrets. By default, an AWS Managed key will be used.

> This setting can only be specified when the cluster is created and cannot be updated.

```python
secrets_key = kms.Key(self, "SecretsKey")
cluster = eks.Cluster(self, "MyCluster",
    secrets_encryption_key=secrets_key,
    version=eks.KubernetesVersion.V1_33
)
```

You can also use a similar configuration for running a cluster built using the FargateCluster construct.

```python
secrets_key = kms.Key(self, "SecretsKey")
cluster = eks.FargateCluster(self, "MyFargateCluster",
    secrets_encryption_key=secrets_key,
    version=eks.KubernetesVersion.V1_33
)
```

The Amazon Resource Name (ARN) for that CMK can be retrieved.

```python
# cluster: eks.Cluster

cluster_encryption_config_key_arn = cluster.cluster_encryption_config_key_arn
```

## Permissions and Security

In the new EKS module, `ConfigMap` is deprecated. Clusters created by the new module will use `API` as authentication mode. Access Entry will be the only way for granting permissions to specific IAM users and roles.

### Access Entry

An access entry is a cluster identity—directly linked to an AWS IAM principal user or role that is used to authenticate to
an Amazon EKS cluster. An Amazon EKS access policy authorizes an access entry to perform specific cluster actions.

Access policies are Amazon EKS-specific policies that assign Kubernetes permissions to access entries. Amazon EKS supports
only predefined and AWS managed policies. Access policies are not AWS IAM entities and are defined and managed by Amazon EKS.
Amazon EKS access policies include permission sets that support common use cases of administration, editing, or read-only access
to Kubernetes resources. See [Access Policy Permissions](https://docs.aws.amazon.com/eks/latest/userguide/access-policies.html#access-policy-permissions) for more details.

Use `AccessPolicy` to include predefined AWS managed policies:

```python
# AmazonEKSClusterAdminPolicy with `cluster` scope
eks.AccessPolicy.from_access_policy_name("AmazonEKSClusterAdminPolicy",
    access_scope_type=eks.AccessScopeType.CLUSTER
)
# AmazonEKSAdminPolicy with `namespace` scope
eks.AccessPolicy.from_access_policy_name("AmazonEKSAdminPolicy",
    access_scope_type=eks.AccessScopeType.NAMESPACE,
    namespaces=["foo", "bar"]
)
```

Use `grantAccess()` to grant the AccessPolicy to an IAM principal:

```python
from aws_cdk.lambda_layer_kubectl_v33 import KubectlV33Layer
# vpc: ec2.Vpc


cluster_admin_role = iam.Role(self, "ClusterAdminRole",
    assumed_by=iam.ArnPrincipal("arn_for_trusted_principal")
)

eks_admin_role = iam.Role(self, "EKSAdminRole",
    assumed_by=iam.ArnPrincipal("arn_for_trusted_principal")
)

cluster = eks.Cluster(self, "Cluster",
    vpc=vpc,
    masters_role=cluster_admin_role,
    version=eks.KubernetesVersion.V1_33,
    kubectl_provider_options=eks.KubectlProviderOptions(
        kubectl_layer=KubectlV33Layer(self, "kubectl"),
        memory=Size.gibibytes(4)
    )
)

# Cluster Admin role for this cluster
cluster.grant_access("clusterAdminAccess", cluster_admin_role.role_arn, [
    eks.AccessPolicy.from_access_policy_name("AmazonEKSClusterAdminPolicy",
        access_scope_type=eks.AccessScopeType.CLUSTER
    )
])

# EKS Admin role for specified namespaces of this cluster
cluster.grant_access("eksAdminRoleAccess", eks_admin_role.role_arn, [
    eks.AccessPolicy.from_access_policy_name("AmazonEKSAdminPolicy",
        access_scope_type=eks.AccessScopeType.NAMESPACE,
        namespaces=["foo", "bar"]
    )
])
```

By default, the cluster creator role will be granted the cluster admin permissions. You can disable it by setting
`bootstrapClusterCreatorAdminPermissions` to false.

> **Note** - Switching `bootstrapClusterCreatorAdminPermissions` on an existing cluster would cause cluster replacement and should be avoided in production.

### Cluster Security Group

When you create an Amazon EKS cluster, a [cluster security group](https://docs.aws.amazon.com/eks/latest/userguide/sec-group-reqs.html)
is automatically created as well. This security group is designed to allow all traffic from the control plane and managed node groups to flow freely
between each other.

The ID for that security group can be retrieved after creating the cluster.

```python
# cluster: eks.Cluster

cluster_security_group_id = cluster.cluster_security_group_id
```

## Applying Kubernetes Resources

To apply kubernetes resource, kubectl provider needs to be created for the cluster. You can use `kubectlProviderOptions` to create the kubectl Provider.

The library supports several popular resource deployment mechanisms, among which are:

### Kubernetes Manifests

The `KubernetesManifest` construct or `cluster.addManifest` method can be used
to apply Kubernetes resource manifests to this cluster.

> When using `cluster.addManifest`, the manifest construct is defined within the cluster's stack scope. If the manifest contains
> attributes from a different stack which depend on the cluster stack, a circular dependency will be created and you will get a synth time error.
> To avoid this, directly use `new KubernetesManifest` to create the manifest in the scope of the other stack.

The following examples will deploy the [paulbouwer/hello-kubernetes](https://github.com/paulbouwer/hello-kubernetes)
service on the cluster:

```python
# cluster: eks.Cluster

app_label = {"app": "hello-kubernetes"}

deployment = {
    "api_version": "apps/v1",
    "kind": "Deployment",
    "metadata": {"name": "hello-kubernetes"},
    "spec": {
        "replicas": 3,
        "selector": {"match_labels": app_label},
        "template": {
            "metadata": {"labels": app_label},
            "spec": {
                "containers": [{
                    "name": "hello-kubernetes",
                    "image": "paulbouwer/hello-kubernetes:1.5",
                    "ports": [{"container_port": 8080}]
                }
                ]
            }
        }
    }
}

service = {
    "api_version": "v1",
    "kind": "Service",
    "metadata": {"name": "hello-kubernetes"},
    "spec": {
        "type": "LoadBalancer",
        "ports": [{"port": 80, "target_port": 8080}],
        "selector": app_label
    }
}

# option 1: use a construct
eks.KubernetesManifest(self, "hello-kub",
    cluster=cluster,
    manifest=[deployment, service]
)

# or, option2: use `addManifest`
cluster.add_manifest("hello-kub", service, deployment)
```

#### ALB Controller Integration

The `KubernetesManifest` construct can detect ingress resources inside your manifest and automatically add the necessary annotations
so they are picked up by the ALB Controller.

> See [Alb Controller](#alb-controller)

To that end, it offers the following properties:

* `ingressAlb` - Signal that the ingress detection should be done.
* `ingressAlbScheme` - Which ALB scheme should be applied. Defaults to `internal`.

#### Adding resources from a URL

The following example will deploy the resource manifest hosting on remote server:

```text
// This example is only available in TypeScript

import * as yaml from 'js-yaml';
import * as request from 'sync-request';

declare const cluster: eks.Cluster;
const manifestUrl = 'https://url/of/manifest.yaml';
const manifest = yaml.safeLoadAll(request('GET', manifestUrl).getBody());
cluster.addManifest('my-resource', manifest);
```

#### Dependencies

There are cases where Kubernetes resources must be deployed in a specific order.
For example, you cannot define a resource in a Kubernetes namespace before the
namespace was created.

You can represent dependencies between `KubernetesManifest`s using
`resource.node.addDependency()`:

```python
# cluster: eks.Cluster

namespace = cluster.add_manifest("my-namespace", {
    "api_version": "v1",
    "kind": "Namespace",
    "metadata": {"name": "my-app"}
})

service = cluster.add_manifest("my-service", {
    "metadata": {
        "name": "myservice",
        "namespace": "my-app"
    },
    "spec": {}
})

service.node.add_dependency(namespace)
```

**NOTE:** when a `KubernetesManifest` includes multiple resources (either directly
or through `cluster.addManifest()`) (e.g. `cluster.addManifest('foo', r1, r2, r3,...)`), these resources will be applied as a single manifest via `kubectl`
and will be applied sequentially (the standard behavior in `kubectl`).

---


Since Kubernetes manifests are implemented as CloudFormation resources in the
CDK. This means that if the manifest is deleted from your code (or the stack is
deleted), the next `cdk deploy` will issue a `kubectl delete` command and the
Kubernetes resources in that manifest will be deleted.

#### Resource Pruning

When a resource is deleted from a Kubernetes manifest, the EKS module will
automatically delete these resources by injecting a *prune label* to all
manifest resources. This label is then passed to [`kubectl apply --prune`](https://kubernetes.io/docs/tasks/manage-kubernetes-objects/declarative-config/#alternative-kubectl-apply-f-directory-prune-l-your-label).

Pruning is enabled by default but can be disabled through the `prune` option
when a cluster is defined:

```python
eks.Cluster(self, "MyCluster",
    version=eks.KubernetesVersion.V1_33,
    prune=False
)
```

#### Manifests Validation

The `kubectl` CLI supports applying a manifest by skipping the validation.
This can be accomplished by setting the `skipValidation` flag to `true` in the `KubernetesManifest` props.

```python
# cluster: eks.Cluster

eks.KubernetesManifest(self, "HelloAppWithoutValidation",
    cluster=cluster,
    manifest=[{"foo": "bar"}],
    skip_validation=True
)
```

### Helm Charts

The `HelmChart` construct or `cluster.addHelmChart` method can be used
to add Kubernetes resources to this cluster using Helm.

> When using `cluster.addHelmChart`, the manifest construct is defined within the cluster's stack scope. If the manifest contains
> attributes from a different stack which depend on the cluster stack, a circular dependency will be created and you will get a synth time error.
> To avoid this, directly use `new HelmChart` to create the chart in the scope of the other stack.

The following example will install the [NGINX Ingress Controller](https://kubernetes.github.io/ingress-nginx/) to your cluster using Helm.

```python
# cluster: eks.Cluster

# option 1: use a construct
eks.HelmChart(self, "NginxIngress",
    cluster=cluster,
    chart="nginx-ingress",
    repository="https://helm.nginx.com/stable",
    namespace="kube-system"
)

# or, option2: use `addHelmChart`
cluster.add_helm_chart("NginxIngress",
    chart="nginx-ingress",
    repository="https://helm.nginx.com/stable",
    namespace="kube-system"
)
```

Helm charts will be installed and updated using `helm upgrade --install`, where a few parameters
are being passed down (such as `repo`, `values`, `version`, `namespace`, `wait`, `timeout`, etc).
This means that if the chart is added to CDK with the same release name, it will try to update
the chart in the cluster.

Additionally, the `chartAsset` property can be an `aws-s3-assets.Asset`. This allows the use of local, private helm charts.

```python
import aws_cdk.aws_s3_assets as s3_assets

# cluster: eks.Cluster

chart_asset = s3_assets.Asset(self, "ChartAsset",
    path="/path/to/asset"
)

cluster.add_helm_chart("test-chart",
    chart_asset=chart_asset
)
```

Nested values passed to the `values` parameter should be provided as a nested dictionary:

```python
# cluster: eks.Cluster


cluster.add_helm_chart("ExternalSecretsOperator",
    chart="external-secrets",
    release="external-secrets",
    repository="https://charts.external-secrets.io",
    namespace="external-secrets",
    values={
        "install_cRDs": True,
        "webhook": {
            "port": 9443
        }
    }
)
```

Helm chart can come with Custom Resource Definitions (CRDs) defined that by default will be installed by helm as well. However in special cases it might be needed to skip the installation of CRDs, for that the property `skipCrds` can be used.

```python
# cluster: eks.Cluster

# option 1: use a construct
eks.HelmChart(self, "NginxIngress",
    cluster=cluster,
    chart="nginx-ingress",
    repository="https://helm.nginx.com/stable",
    namespace="kube-system",
    skip_crds=True
)
```

### OCI Charts

OCI charts are also supported.
Also replace the `${VARS}` with appropriate values.

```python
# cluster: eks.Cluster

# option 1: use a construct
eks.HelmChart(self, "MyOCIChart",
    cluster=cluster,
    chart="some-chart",
    repository="oci://${ACCOUNT_ID}.dkr.ecr.${ACCOUNT_REGION}.amazonaws.com/${REPO_NAME}",
    namespace="oci",
    version="0.0.1"
)
```

Helm charts are implemented as CloudFormation resources in CDK.
This means that if the chart is deleted from your code (or the stack is
deleted), the next `cdk deploy` will issue a `helm uninstall` command and the
Helm chart will be deleted.

When there is no `release` defined, a unique ID will be allocated for the release based
on the construct path.

By default, all Helm charts will be installed concurrently. In some cases, this
could cause race conditions where two Helm charts attempt to deploy the same
resource or if Helm charts depend on each other. You can use
`chart.node.addDependency()` in order to declare a dependency order between
charts:

```python
# cluster: eks.Cluster

chart1 = cluster.add_helm_chart("MyChart",
    chart="foo"
)
chart2 = cluster.add_helm_chart("MyChart",
    chart="bar"
)

chart2.node.add_dependency(chart1)
```

#### Custom CDK8s Constructs

You can also compose a few stock `cdk8s+` constructs into your own custom construct. However, since mixing scopes between `aws-cdk` and `cdk8s` is currently not supported, the `Construct` class
you'll need to use is the one from the [`constructs`](https://github.com/aws/constructs) module, and not from `aws-cdk-lib` like you normally would.
This is why we used `new cdk8s.App()` as the scope of the chart above.

```python
import constructs as constructs
import cdk8s as cdk8s
import cdk8s_plus_25 as kplus


app = cdk8s.App()
chart = cdk8s.Chart(app, "my-chart")

class LoadBalancedWebService(constructs.Construct):
    def __init__(self, scope, id, props):
        super().__init__(scope, id)

        deployment = kplus.Deployment(chart, "Deployment",
            replicas=props.replicas,
            containers=[kplus.Container(image=props.image)]
        )

        deployment.expose_via_service(
            ports=[kplus.ServicePort(port=props.port)
            ],
            service_type=kplus.ServiceType.LOAD_BALANCER
        )
```

#### Manually importing k8s specs and CRD's

If you find yourself unable to use `cdk8s+`, or just like to directly use the `k8s` native objects or CRD's, you can do so by manually importing them using the `cdk8s-cli`.

See [Importing kubernetes objects](https://cdk8s.io/docs/latest/cli/import/) for detailed instructions.

## Patching Kubernetes Resources

The `KubernetesPatch` construct can be used to update existing kubernetes
resources. The following example can be used to patch the `hello-kubernetes`
deployment from the example above with 5 replicas.

```python
# cluster: eks.Cluster

eks.KubernetesPatch(self, "hello-kub-deployment-label",
    cluster=cluster,
    resource_name="deployment/hello-kubernetes",
    apply_patch={"spec": {"replicas": 5}},
    restore_patch={"spec": {"replicas": 3}}
)
```

## Querying Kubernetes Resources

The `KubernetesObjectValue` construct can be used to query for information about kubernetes objects,
and use that as part of your CDK application.

For example, you can fetch the address of a [`LoadBalancer`](https://kubernetes.io/docs/concepts/services-networking/service/#loadbalancer) type service:

```python
# cluster: eks.Cluster

# query the load balancer address
my_service_address = eks.KubernetesObjectValue(self, "LoadBalancerAttribute",
    cluster=cluster,
    object_type="service",
    object_name="my-service",
    json_path=".status.loadBalancer.ingress[0].hostname"
)

# pass the address to a lambda function
proxy_function = lambda_.Function(self, "ProxyFunction",
    handler="index.handler",
    code=lambda_.Code.from_inline("my-code"),
    runtime=lambda_.Runtime.NODEJS_LATEST,
    environment={
        "my_service_address": my_service_address.value
    }
)
```

Specifically, since the above use-case is quite common, there is an easier way to access that information:

```python
# cluster: eks.Cluster

load_balancer_address = cluster.get_service_load_balancer_address("my-service")
```

## Add-ons

[Add-ons](https://docs.aws.amazon.com/eks/latest/userguide/eks-add-ons.html) is a software that provides supporting operational capabilities to Kubernetes applications. The EKS module supports adding add-ons to your cluster using the `eks.Addon` class.

```python
# cluster: eks.Cluster


eks.Addon(self, "Addon",
    cluster=cluster,
    addon_name="coredns",
    addon_version="v1.11.4-eksbuild.2",
    # whether to preserve the add-on software on your cluster but Amazon EKS stops managing any settings for the add-on.
    preserve_on_delete=False,
    configuration_values={
        "replica_count": 2
    }
)
```

## Using existing clusters

The EKS library allows defining Kubernetes resources such as [Kubernetes
manifests](#kubernetes-resources) and [Helm charts](#helm-charts) on clusters
that are not defined as part of your CDK app.

First you will need to import the kubectl provider and cluster created in another stack

```python
handler_role = iam.Role.from_role_arn(self, "HandlerRole", "arn:aws:iam::123456789012:role/lambda-role")

kubectl_provider = eks.KubectlProvider.from_kubectl_provider_attributes(self, "KubectlProvider",
    service_token="arn:aws:lambda:us-east-2:123456789012:function:my-function:1",
    role=handler_role
)

cluster = eks.Cluster.from_cluster_attributes(self, "Cluster",
    cluster_name="cluster",
    kubectl_provider=kubectl_provider
)
```

Then, you can use `addManifest` or `addHelmChart` to define resources inside
your Kubernetes cluster.

```python
# cluster: eks.Cluster

cluster.add_manifest("Test", {
    "api_version": "v1",
    "kind": "ConfigMap",
    "metadata": {
        "name": "myconfigmap"
    },
    "data": {
        "Key": "value",
        "Another": "123454"
    }
})
```

## Logging

EKS supports cluster logging for 5 different types of events:

* API requests to the cluster.
* Cluster access via the Kubernetes API.
* Authentication requests into the cluster.
* State of cluster controllers.
* Scheduling decisions.

You can enable logging for each one separately using the `clusterLogging`
property. For example:

```python
cluster = eks.Cluster(self, "Cluster",
    # ...
    version=eks.KubernetesVersion.V1_33,
    cluster_logging=[eks.ClusterLoggingTypes.API, eks.ClusterLoggingTypes.AUTHENTICATOR, eks.ClusterLoggingTypes.SCHEDULER
    ]
)
```

## NodeGroup Repair Config

You can enable Managed Node Group [auto-repair config](https://docs.aws.amazon.com/eks/latest/userguide/node-health.html#node-auto-repair) using `enableNodeAutoRepair`
property. For example:

```python
# cluster: eks.Cluster


cluster.add_nodegroup_capacity("NodeGroup",
    enable_node_auto_repair=True
)
```
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
import aws_cdk.aws_autoscaling as _aws_cdk_aws_autoscaling_ceddda9d
import aws_cdk.aws_ec2 as _aws_cdk_aws_ec2_ceddda9d
import aws_cdk.aws_iam as _aws_cdk_aws_iam_ceddda9d
import aws_cdk.aws_kms as _aws_cdk_aws_kms_ceddda9d
import aws_cdk.aws_lambda as _aws_cdk_aws_lambda_ceddda9d
import aws_cdk.aws_s3_assets as _aws_cdk_aws_s3_assets_ceddda9d
import constructs as _constructs_77d1e7e8


@jsii.data_type(
    jsii_type="@aws-cdk/aws-eks-v2-alpha.AccessEntryAttributes",
    jsii_struct_bases=[],
    name_mapping={
        "access_entry_arn": "accessEntryArn",
        "access_entry_name": "accessEntryName",
    },
)
class AccessEntryAttributes:
    def __init__(
        self,
        *,
        access_entry_arn: builtins.str,
        access_entry_name: builtins.str,
    ) -> None:
        '''(experimental) Represents the attributes of an access entry.

        :param access_entry_arn: (experimental) The Amazon Resource Name (ARN) of the access entry.
        :param access_entry_name: (experimental) The name of the access entry.

        :stability: experimental
        :exampleMetadata: fixture=_generated

        Example::

            # The code below shows an example of how to instantiate this type.
            # The values are placeholders you should change.
            import aws_cdk.aws_eks_v2_alpha as eks_v2_alpha
            
            access_entry_attributes = eks_v2_alpha.AccessEntryAttributes(
                access_entry_arn="accessEntryArn",
                access_entry_name="accessEntryName"
            )
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a1c42761d8ad618e710840d7ce74bb7a2f8a514feedccc8036a6981b147024bc)
            check_type(argname="argument access_entry_arn", value=access_entry_arn, expected_type=type_hints["access_entry_arn"])
            check_type(argname="argument access_entry_name", value=access_entry_name, expected_type=type_hints["access_entry_name"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "access_entry_arn": access_entry_arn,
            "access_entry_name": access_entry_name,
        }

    @builtins.property
    def access_entry_arn(self) -> builtins.str:
        '''(experimental) The Amazon Resource Name (ARN) of the access entry.

        :stability: experimental
        '''
        result = self._values.get("access_entry_arn")
        assert result is not None, "Required property 'access_entry_arn' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def access_entry_name(self) -> builtins.str:
        '''(experimental) The name of the access entry.

        :stability: experimental
        '''
        result = self._values.get("access_entry_name")
        assert result is not None, "Required property 'access_entry_name' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "AccessEntryAttributes(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@aws-cdk/aws-eks-v2-alpha.AccessEntryProps",
    jsii_struct_bases=[],
    name_mapping={
        "access_policies": "accessPolicies",
        "cluster": "cluster",
        "principal": "principal",
        "access_entry_name": "accessEntryName",
        "access_entry_type": "accessEntryType",
    },
)
class AccessEntryProps:
    def __init__(
        self,
        *,
        access_policies: typing.Sequence["IAccessPolicy"],
        cluster: "ICluster",
        principal: builtins.str,
        access_entry_name: typing.Optional[builtins.str] = None,
        access_entry_type: typing.Optional["AccessEntryType"] = None,
    ) -> None:
        '''(experimental) Represents the properties required to create an Amazon EKS access entry.

        :param access_policies: (experimental) The access policies that define the permissions and scope for the access entry.
        :param cluster: (experimental) The Amazon EKS cluster to which the access entry applies.
        :param principal: (experimental) The Amazon Resource Name (ARN) of the principal (user or role) to associate the access entry with.
        :param access_entry_name: (experimental) The name of the AccessEntry. Default: - No access entry name is provided
        :param access_entry_type: (experimental) The type of the AccessEntry. Default: STANDARD

        :stability: experimental
        :exampleMetadata: fixture=_generated

        Example::

            # The code below shows an example of how to instantiate this type.
            # The values are placeholders you should change.
            import aws_cdk.aws_eks_v2_alpha as eks_v2_alpha
            
            # access_policy: eks_v2_alpha.AccessPolicy
            # cluster: eks_v2_alpha.Cluster
            
            access_entry_props = eks_v2_alpha.AccessEntryProps(
                access_policies=[access_policy],
                cluster=cluster,
                principal="principal",
            
                # the properties below are optional
                access_entry_name="accessEntryName",
                access_entry_type=eks_v2_alpha.AccessEntryType.STANDARD
            )
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__28312253bcbfe1c95acff9f4dd1b5759694a940428c1c62932fe961a5a9ba258)
            check_type(argname="argument access_policies", value=access_policies, expected_type=type_hints["access_policies"])
            check_type(argname="argument cluster", value=cluster, expected_type=type_hints["cluster"])
            check_type(argname="argument principal", value=principal, expected_type=type_hints["principal"])
            check_type(argname="argument access_entry_name", value=access_entry_name, expected_type=type_hints["access_entry_name"])
            check_type(argname="argument access_entry_type", value=access_entry_type, expected_type=type_hints["access_entry_type"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "access_policies": access_policies,
            "cluster": cluster,
            "principal": principal,
        }
        if access_entry_name is not None:
            self._values["access_entry_name"] = access_entry_name
        if access_entry_type is not None:
            self._values["access_entry_type"] = access_entry_type

    @builtins.property
    def access_policies(self) -> typing.List["IAccessPolicy"]:
        '''(experimental) The access policies that define the permissions and scope for the access entry.

        :stability: experimental
        '''
        result = self._values.get("access_policies")
        assert result is not None, "Required property 'access_policies' is missing"
        return typing.cast(typing.List["IAccessPolicy"], result)

    @builtins.property
    def cluster(self) -> "ICluster":
        '''(experimental) The Amazon EKS cluster to which the access entry applies.

        :stability: experimental
        '''
        result = self._values.get("cluster")
        assert result is not None, "Required property 'cluster' is missing"
        return typing.cast("ICluster", result)

    @builtins.property
    def principal(self) -> builtins.str:
        '''(experimental) The Amazon Resource Name (ARN) of the principal (user or role) to associate the access entry with.

        :stability: experimental
        '''
        result = self._values.get("principal")
        assert result is not None, "Required property 'principal' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def access_entry_name(self) -> typing.Optional[builtins.str]:
        '''(experimental) The name of the AccessEntry.

        :default: - No access entry name is provided

        :stability: experimental
        '''
        result = self._values.get("access_entry_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def access_entry_type(self) -> typing.Optional["AccessEntryType"]:
        '''(experimental) The type of the AccessEntry.

        :default: STANDARD

        :stability: experimental
        '''
        result = self._values.get("access_entry_type")
        return typing.cast(typing.Optional["AccessEntryType"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "AccessEntryProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.enum(jsii_type="@aws-cdk/aws-eks-v2-alpha.AccessEntryType")
class AccessEntryType(enum.Enum):
    '''(experimental) Represents the different types of access entries that can be used in an Amazon EKS cluster.

    :stability: experimental
    :enum: true
    '''

    STANDARD = "STANDARD"
    '''(experimental) Represents a standard access entry.

    :stability: experimental
    '''
    FARGATE_LINUX = "FARGATE_LINUX"
    '''(experimental) Represents a Fargate Linux access entry.

    :stability: experimental
    '''
    EC2_LINUX = "EC2_LINUX"
    '''(experimental) Represents an EC2 Linux access entry.

    :stability: experimental
    '''
    EC2_WINDOWS = "EC2_WINDOWS"
    '''(experimental) Represents an EC2 Windows access entry.

    :stability: experimental
    '''


class AccessPolicyArn(
    metaclass=jsii.JSIIMeta,
    jsii_type="@aws-cdk/aws-eks-v2-alpha.AccessPolicyArn",
):
    '''(experimental) Represents an Amazon EKS Access Policy ARN.

    Amazon EKS Access Policies are used to control access to Amazon EKS clusters.

    :see: https://docs.aws.amazon.com/eks/latest/userguide/access-policies.html
    :stability: experimental
    :exampleMetadata: fixture=_generated

    Example::

        # The code below shows an example of how to instantiate this type.
        # The values are placeholders you should change.
        import aws_cdk.aws_eks_v2_alpha as eks_v2_alpha
        
        access_policy_arn = eks_v2_alpha.AccessPolicyArn.AMAZON_EKS_ADMIN_POLICY
    '''

    def __init__(self, policy_name: builtins.str) -> None:
        '''(experimental) Constructs a new instance of the ``AccessEntry`` class.

        :param policy_name: - The name of the Amazon EKS access policy. This is used to construct the policy ARN.

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b6bcee6a7fdd4d7280e30d78ff502c787d282b5a96f4540c76eac9d188ec3da3)
            check_type(argname="argument policy_name", value=policy_name, expected_type=type_hints["policy_name"])
        jsii.create(self.__class__, self, [policy_name])

    @jsii.member(jsii_name="of")
    @builtins.classmethod
    def of(cls, policy_name: builtins.str) -> "AccessPolicyArn":
        '''(experimental) Creates a new instance of the AccessPolicy class with the specified policy name.

        :param policy_name: The name of the access policy.

        :return: A new instance of the AccessPolicy class.

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__155fac0a7fd65467d537ff4154d30c6ff4695350828b6ec7f85303a397092bd7)
            check_type(argname="argument policy_name", value=policy_name, expected_type=type_hints["policy_name"])
        return typing.cast("AccessPolicyArn", jsii.sinvoke(cls, "of", [policy_name]))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AMAZON_EKS_ADMIN_POLICY")
    def AMAZON_EKS_ADMIN_POLICY(cls) -> "AccessPolicyArn":
        '''(experimental) The Amazon EKS Admin Policy.

        This access policy includes permissions that grant an IAM principal
        most permissions to resources. When associated to an access entry, its access scope is typically
        one or more Kubernetes namespaces.

        :stability: experimental
        '''
        return typing.cast("AccessPolicyArn", jsii.sget(cls, "AMAZON_EKS_ADMIN_POLICY"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AMAZON_EKS_ADMIN_VIEW_POLICY")
    def AMAZON_EKS_ADMIN_VIEW_POLICY(cls) -> "AccessPolicyArn":
        '''(experimental) The Amazon EKS Admin View Policy.

        This access policy includes permissions that grant an IAM principal
        access to list/view all resources in a cluster.

        :stability: experimental
        '''
        return typing.cast("AccessPolicyArn", jsii.sget(cls, "AMAZON_EKS_ADMIN_VIEW_POLICY"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AMAZON_EKS_CLUSTER_ADMIN_POLICY")
    def AMAZON_EKS_CLUSTER_ADMIN_POLICY(cls) -> "AccessPolicyArn":
        '''(experimental) The Amazon EKS Cluster Admin Policy.

        This access policy includes permissions that grant an IAM
        principal administrator access to a cluster. When associated to an access entry, its access scope
        is typically the cluster, rather than a Kubernetes namespace.

        :stability: experimental
        '''
        return typing.cast("AccessPolicyArn", jsii.sget(cls, "AMAZON_EKS_CLUSTER_ADMIN_POLICY"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AMAZON_EKS_EDIT_POLICY")
    def AMAZON_EKS_EDIT_POLICY(cls) -> "AccessPolicyArn":
        '''(experimental) The Amazon EKS Edit Policy.

        This access policy includes permissions that allow an IAM principal
        to edit most Kubernetes resources.

        :stability: experimental
        '''
        return typing.cast("AccessPolicyArn", jsii.sget(cls, "AMAZON_EKS_EDIT_POLICY"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AMAZON_EKS_VIEW_POLICY")
    def AMAZON_EKS_VIEW_POLICY(cls) -> "AccessPolicyArn":
        '''(experimental) The Amazon EKS View Policy.

        This access policy includes permissions that grant an IAM principal
        access to list/view all resources in a cluster.

        :stability: experimental
        '''
        return typing.cast("AccessPolicyArn", jsii.sget(cls, "AMAZON_EKS_VIEW_POLICY"))

    @builtins.property
    @jsii.member(jsii_name="policyArn")
    def policy_arn(self) -> builtins.str:
        '''(experimental) The Amazon Resource Name (ARN) of the access policy.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "policyArn"))

    @builtins.property
    @jsii.member(jsii_name="policyName")
    def policy_name(self) -> builtins.str:
        '''(experimental) - The name of the Amazon EKS access policy.

        This is used to construct the policy ARN.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "policyName"))


@jsii.data_type(
    jsii_type="@aws-cdk/aws-eks-v2-alpha.AccessPolicyNameOptions",
    jsii_struct_bases=[],
    name_mapping={"access_scope_type": "accessScopeType", "namespaces": "namespaces"},
)
class AccessPolicyNameOptions:
    def __init__(
        self,
        *,
        access_scope_type: "AccessScopeType",
        namespaces: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''(experimental) Represents the options required to create an Amazon EKS Access Policy using the ``fromAccessPolicyName()`` method.

        :param access_scope_type: (experimental) The scope of the access policy. This determines the level of access granted by the policy.
        :param namespaces: (experimental) An optional array of Kubernetes namespaces to which the access policy applies. Default: - no specific namespaces for this scope

        :stability: experimental
        :exampleMetadata: infused

        Example::

            # AmazonEKSClusterAdminPolicy with `cluster` scope
            eks.AccessPolicy.from_access_policy_name("AmazonEKSClusterAdminPolicy",
                access_scope_type=eks.AccessScopeType.CLUSTER
            )
            # AmazonEKSAdminPolicy with `namespace` scope
            eks.AccessPolicy.from_access_policy_name("AmazonEKSAdminPolicy",
                access_scope_type=eks.AccessScopeType.NAMESPACE,
                namespaces=["foo", "bar"]
            )
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__18c9055694d7edcbddf83f561177ec54d0045caca2dff5354a29ccaf0421b493)
            check_type(argname="argument access_scope_type", value=access_scope_type, expected_type=type_hints["access_scope_type"])
            check_type(argname="argument namespaces", value=namespaces, expected_type=type_hints["namespaces"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "access_scope_type": access_scope_type,
        }
        if namespaces is not None:
            self._values["namespaces"] = namespaces

    @builtins.property
    def access_scope_type(self) -> "AccessScopeType":
        '''(experimental) The scope of the access policy.

        This determines the level of access granted by the policy.

        :stability: experimental
        '''
        result = self._values.get("access_scope_type")
        assert result is not None, "Required property 'access_scope_type' is missing"
        return typing.cast("AccessScopeType", result)

    @builtins.property
    def namespaces(self) -> typing.Optional[typing.List[builtins.str]]:
        '''(experimental) An optional array of Kubernetes namespaces to which the access policy applies.

        :default: - no specific namespaces for this scope

        :stability: experimental
        '''
        result = self._values.get("namespaces")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "AccessPolicyNameOptions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@aws-cdk/aws-eks-v2-alpha.AccessPolicyProps",
    jsii_struct_bases=[],
    name_mapping={"access_scope": "accessScope", "policy": "policy"},
)
class AccessPolicyProps:
    def __init__(
        self,
        *,
        access_scope: typing.Union["AccessScope", typing.Dict[builtins.str, typing.Any]],
        policy: AccessPolicyArn,
    ) -> None:
        '''(experimental) Properties for configuring an Amazon EKS Access Policy.

        :param access_scope: (experimental) The scope of the access policy, which determines the level of access granted.
        :param policy: (experimental) The access policy itself, which defines the specific permissions.

        :stability: experimental
        :exampleMetadata: fixture=_generated

        Example::

            # The code below shows an example of how to instantiate this type.
            # The values are placeholders you should change.
            import aws_cdk.aws_eks_v2_alpha as eks_v2_alpha
            
            # access_policy_arn: eks_v2_alpha.AccessPolicyArn
            
            access_policy_props = eks_v2_alpha.AccessPolicyProps(
                access_scope=eks_v2_alpha.AccessScope(
                    type=eks_v2_alpha.AccessScopeType.NAMESPACE,
            
                    # the properties below are optional
                    namespaces=["namespaces"]
                ),
                policy=access_policy_arn
            )
        '''
        if isinstance(access_scope, dict):
            access_scope = AccessScope(**access_scope)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__67dd0dd6c6160b9fa70474d028bdae828b4c8b27179b498fbd95c4ed4b19c3d8)
            check_type(argname="argument access_scope", value=access_scope, expected_type=type_hints["access_scope"])
            check_type(argname="argument policy", value=policy, expected_type=type_hints["policy"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "access_scope": access_scope,
            "policy": policy,
        }

    @builtins.property
    def access_scope(self) -> "AccessScope":
        '''(experimental) The scope of the access policy, which determines the level of access granted.

        :stability: experimental
        '''
        result = self._values.get("access_scope")
        assert result is not None, "Required property 'access_scope' is missing"
        return typing.cast("AccessScope", result)

    @builtins.property
    def policy(self) -> AccessPolicyArn:
        '''(experimental) The access policy itself, which defines the specific permissions.

        :stability: experimental
        '''
        result = self._values.get("policy")
        assert result is not None, "Required property 'policy' is missing"
        return typing.cast(AccessPolicyArn, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "AccessPolicyProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@aws-cdk/aws-eks-v2-alpha.AccessScope",
    jsii_struct_bases=[],
    name_mapping={"type": "type", "namespaces": "namespaces"},
)
class AccessScope:
    def __init__(
        self,
        *,
        type: "AccessScopeType",
        namespaces: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''(experimental) Represents the scope of an access policy.

        The scope defines the namespaces or cluster-level access granted by the policy.

        :param type: (experimental) The scope type of the policy, either 'namespace' or 'cluster'.
        :param namespaces: (experimental) A Kubernetes namespace that an access policy is scoped to. A value is required if you specified namespace for Type. Default: - no specific namespaces for this scope.

        :stability: experimental
        :interface: AccessScope
        :property: {AccessScopeType} type - The scope type of the policy, either 'namespace' or 'cluster'.
        :exampleMetadata: fixture=_generated

        Example::

            # The code below shows an example of how to instantiate this type.
            # The values are placeholders you should change.
            import aws_cdk.aws_eks_v2_alpha as eks_v2_alpha
            
            access_scope = eks_v2_alpha.AccessScope(
                type=eks_v2_alpha.AccessScopeType.NAMESPACE,
            
                # the properties below are optional
                namespaces=["namespaces"]
            )
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2b5165802a21d1fa47a765766414c1a219e1b28c0ea0666a761a47a6014d6d15)
            check_type(argname="argument type", value=type, expected_type=type_hints["type"])
            check_type(argname="argument namespaces", value=namespaces, expected_type=type_hints["namespaces"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "type": type,
        }
        if namespaces is not None:
            self._values["namespaces"] = namespaces

    @builtins.property
    def type(self) -> "AccessScopeType":
        '''(experimental) The scope type of the policy, either 'namespace' or 'cluster'.

        :stability: experimental
        '''
        result = self._values.get("type")
        assert result is not None, "Required property 'type' is missing"
        return typing.cast("AccessScopeType", result)

    @builtins.property
    def namespaces(self) -> typing.Optional[typing.List[builtins.str]]:
        '''(experimental) A Kubernetes namespace that an access policy is scoped to.

        A value is required if you specified
        namespace for Type.

        :default: - no specific namespaces for this scope.

        :stability: experimental
        '''
        result = self._values.get("namespaces")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "AccessScope(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.enum(jsii_type="@aws-cdk/aws-eks-v2-alpha.AccessScopeType")
class AccessScopeType(enum.Enum):
    '''(experimental) Represents the scope type of an access policy.

    The scope type determines the level of access granted by the policy.

    :stability: experimental
    :enum: true
    :export: true
    :exampleMetadata: infused

    Example::

        # AmazonEKSClusterAdminPolicy with `cluster` scope
        eks.AccessPolicy.from_access_policy_name("AmazonEKSClusterAdminPolicy",
            access_scope_type=eks.AccessScopeType.CLUSTER
        )
        # AmazonEKSAdminPolicy with `namespace` scope
        eks.AccessPolicy.from_access_policy_name("AmazonEKSAdminPolicy",
            access_scope_type=eks.AccessScopeType.NAMESPACE,
            namespaces=["foo", "bar"]
        )
    '''

    NAMESPACE = "NAMESPACE"
    '''(experimental) The policy applies to a specific namespace within the cluster.

    :stability: experimental
    '''
    CLUSTER = "CLUSTER"
    '''(experimental) The policy applies to the entire cluster.

    :stability: experimental
    '''


@jsii.data_type(
    jsii_type="@aws-cdk/aws-eks-v2-alpha.AddonAttributes",
    jsii_struct_bases=[],
    name_mapping={"addon_name": "addonName", "cluster_name": "clusterName"},
)
class AddonAttributes:
    def __init__(self, *, addon_name: builtins.str, cluster_name: builtins.str) -> None:
        '''(experimental) Represents the attributes of an addon for an Amazon EKS cluster.

        :param addon_name: (experimental) The name of the addon.
        :param cluster_name: (experimental) The name of the Amazon EKS cluster the addon is associated with.

        :stability: experimental
        :exampleMetadata: fixture=_generated

        Example::

            # The code below shows an example of how to instantiate this type.
            # The values are placeholders you should change.
            import aws_cdk.aws_eks_v2_alpha as eks_v2_alpha
            
            addon_attributes = eks_v2_alpha.AddonAttributes(
                addon_name="addonName",
                cluster_name="clusterName"
            )
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c45f5324dae53f08d3805a9ed526230051bfa314a37fce62f6c6559495f0a9ef)
            check_type(argname="argument addon_name", value=addon_name, expected_type=type_hints["addon_name"])
            check_type(argname="argument cluster_name", value=cluster_name, expected_type=type_hints["cluster_name"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "addon_name": addon_name,
            "cluster_name": cluster_name,
        }

    @builtins.property
    def addon_name(self) -> builtins.str:
        '''(experimental) The name of the addon.

        :stability: experimental
        '''
        result = self._values.get("addon_name")
        assert result is not None, "Required property 'addon_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def cluster_name(self) -> builtins.str:
        '''(experimental) The name of the Amazon EKS cluster the addon is associated with.

        :stability: experimental
        '''
        result = self._values.get("cluster_name")
        assert result is not None, "Required property 'cluster_name' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "AddonAttributes(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@aws-cdk/aws-eks-v2-alpha.AddonProps",
    jsii_struct_bases=[],
    name_mapping={
        "addon_name": "addonName",
        "cluster": "cluster",
        "addon_version": "addonVersion",
        "configuration_values": "configurationValues",
        "preserve_on_delete": "preserveOnDelete",
    },
)
class AddonProps:
    def __init__(
        self,
        *,
        addon_name: builtins.str,
        cluster: "ICluster",
        addon_version: typing.Optional[builtins.str] = None,
        configuration_values: typing.Optional[typing.Mapping[builtins.str, typing.Any]] = None,
        preserve_on_delete: typing.Optional[builtins.bool] = None,
    ) -> None:
        '''(experimental) Properties for creating an Amazon EKS Add-On.

        :param addon_name: (experimental) Name of the Add-On.
        :param cluster: (experimental) The EKS cluster the Add-On is associated with.
        :param addon_version: (experimental) Version of the Add-On. You can check all available versions with describe-addon-versions. For example, this lists all available versions for the ``eks-pod-identity-agent`` addon: $ aws eks describe-addon-versions --addon-name eks-pod-identity-agent --query 'addons[*].addonVersions[*].addonVersion' Default: the latest version.
        :param configuration_values: (experimental) The configuration values for the Add-on. Default: - Use default configuration.
        :param preserve_on_delete: (experimental) Specifying this option preserves the add-on software on your cluster but Amazon EKS stops managing any settings for the add-on. If an IAM account is associated with the add-on, it isn't removed. Default: true

        :stability: experimental
        :exampleMetadata: infused

        Example::

            # cluster: eks.Cluster
            
            
            eks.Addon(self, "Addon",
                cluster=cluster,
                addon_name="coredns",
                addon_version="v1.11.4-eksbuild.2",
                # whether to preserve the add-on software on your cluster but Amazon EKS stops managing any settings for the add-on.
                preserve_on_delete=False,
                configuration_values={
                    "replica_count": 2
                }
            )
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ce116d5a90e7137ae9a49817a403d4e436125d6de14d8cc0d64941c9bbf10338)
            check_type(argname="argument addon_name", value=addon_name, expected_type=type_hints["addon_name"])
            check_type(argname="argument cluster", value=cluster, expected_type=type_hints["cluster"])
            check_type(argname="argument addon_version", value=addon_version, expected_type=type_hints["addon_version"])
            check_type(argname="argument configuration_values", value=configuration_values, expected_type=type_hints["configuration_values"])
            check_type(argname="argument preserve_on_delete", value=preserve_on_delete, expected_type=type_hints["preserve_on_delete"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "addon_name": addon_name,
            "cluster": cluster,
        }
        if addon_version is not None:
            self._values["addon_version"] = addon_version
        if configuration_values is not None:
            self._values["configuration_values"] = configuration_values
        if preserve_on_delete is not None:
            self._values["preserve_on_delete"] = preserve_on_delete

    @builtins.property
    def addon_name(self) -> builtins.str:
        '''(experimental) Name of the Add-On.

        :stability: experimental
        '''
        result = self._values.get("addon_name")
        assert result is not None, "Required property 'addon_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def cluster(self) -> "ICluster":
        '''(experimental) The EKS cluster the Add-On is associated with.

        :stability: experimental
        '''
        result = self._values.get("cluster")
        assert result is not None, "Required property 'cluster' is missing"
        return typing.cast("ICluster", result)

    @builtins.property
    def addon_version(self) -> typing.Optional[builtins.str]:
        '''(experimental) Version of the Add-On.

        You can check all available versions with describe-addon-versions.
        For example, this lists all available versions for the ``eks-pod-identity-agent`` addon:
        $ aws eks describe-addon-versions --addon-name eks-pod-identity-agent
        --query 'addons[*].addonVersions[*].addonVersion'

        :default: the latest version.

        :stability: experimental
        '''
        result = self._values.get("addon_version")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def configuration_values(
        self,
    ) -> typing.Optional[typing.Mapping[builtins.str, typing.Any]]:
        '''(experimental) The configuration values for the Add-on.

        :default: - Use default configuration.

        :stability: experimental
        '''
        result = self._values.get("configuration_values")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, typing.Any]], result)

    @builtins.property
    def preserve_on_delete(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Specifying this option preserves the add-on software on your cluster but Amazon EKS stops managing any settings for the add-on.

        If an IAM account is associated with the add-on, it isn't removed.

        :default: true

        :stability: experimental
        '''
        result = self._values.get("preserve_on_delete")
        return typing.cast(typing.Optional[builtins.bool], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "AddonProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class AlbController(
    _constructs_77d1e7e8.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="@aws-cdk/aws-eks-v2-alpha.AlbController",
):
    '''(experimental) Construct for installing the AWS ALB Contoller on EKS clusters.

    Use the factory functions ``get`` and ``getOrCreate`` to obtain/create instances of this controller.

    :see: https://kubernetes-sigs.github.io/aws-load-balancer-controller
    :stability: experimental
    :exampleMetadata: fixture=_generated

    Example::

        # The code below shows an example of how to instantiate this type.
        # The values are placeholders you should change.
        import aws_cdk.aws_eks_v2_alpha as eks_v2_alpha
        
        # alb_controller_version: eks_v2_alpha.AlbControllerVersion
        # cluster: eks_v2_alpha.Cluster
        # policy: Any
        
        alb_controller = eks_v2_alpha.AlbController(self, "MyAlbController",
            cluster=cluster,
            version=alb_controller_version,
        
            # the properties below are optional
            policy=policy,
            repository="repository"
        )
    '''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        cluster: "Cluster",
        version: "AlbControllerVersion",
        policy: typing.Any = None,
        repository: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param cluster: (experimental) [disable-awslint:ref-via-interface] Cluster to install the controller onto.
        :param version: (experimental) Version of the controller.
        :param policy: (experimental) The IAM policy to apply to the service account. If you're using one of the built-in versions, this is not required since CDK ships with the appropriate policies for those versions. However, if you are using a custom version, this is required (and validated). Default: - Corresponds to the predefined version.
        :param repository: (experimental) The repository to pull the controller image from. Note that the default repository works for most regions, but not all. If the repository is not applicable to your region, use a custom repository according to the information here: https://github.com/kubernetes-sigs/aws-load-balancer-controller/releases. Default: '602401143452.dkr.ecr.us-west-2.amazonaws.com/amazon/aws-load-balancer-controller'

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6c1fc18874adc65eddee4779680e882efdd136a784f11a6821fbb017354e4821)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = AlbControllerProps(
            cluster=cluster, version=version, policy=policy, repository=repository
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @jsii.member(jsii_name="create")
    @builtins.classmethod
    def create(
        cls,
        scope: _constructs_77d1e7e8.Construct,
        *,
        cluster: "Cluster",
        version: "AlbControllerVersion",
        policy: typing.Any = None,
        repository: typing.Optional[builtins.str] = None,
    ) -> "AlbController":
        '''(experimental) Create the controller construct associated with this cluster and scope.

        Singleton per stack/cluster.

        :param scope: -
        :param cluster: (experimental) [disable-awslint:ref-via-interface] Cluster to install the controller onto.
        :param version: (experimental) Version of the controller.
        :param policy: (experimental) The IAM policy to apply to the service account. If you're using one of the built-in versions, this is not required since CDK ships with the appropriate policies for those versions. However, if you are using a custom version, this is required (and validated). Default: - Corresponds to the predefined version.
        :param repository: (experimental) The repository to pull the controller image from. Note that the default repository works for most regions, but not all. If the repository is not applicable to your region, use a custom repository according to the information here: https://github.com/kubernetes-sigs/aws-load-balancer-controller/releases. Default: '602401143452.dkr.ecr.us-west-2.amazonaws.com/amazon/aws-load-balancer-controller'

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b7d42172ce30796b336d53a283aaf2d1861ef8f3513b5174f100f1d0ca21f07e)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
        props = AlbControllerProps(
            cluster=cluster, version=version, policy=policy, repository=repository
        )

        return typing.cast("AlbController", jsii.sinvoke(cls, "create", [scope, props]))


@jsii.data_type(
    jsii_type="@aws-cdk/aws-eks-v2-alpha.AlbControllerOptions",
    jsii_struct_bases=[],
    name_mapping={
        "version": "version",
        "policy": "policy",
        "repository": "repository",
    },
)
class AlbControllerOptions:
    def __init__(
        self,
        *,
        version: "AlbControllerVersion",
        policy: typing.Any = None,
        repository: typing.Optional[builtins.str] = None,
    ) -> None:
        '''(experimental) Options for ``AlbController``.

        :param version: (experimental) Version of the controller.
        :param policy: (experimental) The IAM policy to apply to the service account. If you're using one of the built-in versions, this is not required since CDK ships with the appropriate policies for those versions. However, if you are using a custom version, this is required (and validated). Default: - Corresponds to the predefined version.
        :param repository: (experimental) The repository to pull the controller image from. Note that the default repository works for most regions, but not all. If the repository is not applicable to your region, use a custom repository according to the information here: https://github.com/kubernetes-sigs/aws-load-balancer-controller/releases. Default: '602401143452.dkr.ecr.us-west-2.amazonaws.com/amazon/aws-load-balancer-controller'

        :stability: experimental
        :exampleMetadata: infused

        Example::

            eks.Cluster(self, "HelloEKS",
                version=eks.KubernetesVersion.V1_33,
                alb_controller=eks.AlbControllerOptions(
                    version=eks.AlbControllerVersion.V2_8_2
                )
            )
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a1139b37be2b46399f7ef96eec4f70ca36576851005d609b6f8a06ff3509e8ad)
            check_type(argname="argument version", value=version, expected_type=type_hints["version"])
            check_type(argname="argument policy", value=policy, expected_type=type_hints["policy"])
            check_type(argname="argument repository", value=repository, expected_type=type_hints["repository"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "version": version,
        }
        if policy is not None:
            self._values["policy"] = policy
        if repository is not None:
            self._values["repository"] = repository

    @builtins.property
    def version(self) -> "AlbControllerVersion":
        '''(experimental) Version of the controller.

        :stability: experimental
        '''
        result = self._values.get("version")
        assert result is not None, "Required property 'version' is missing"
        return typing.cast("AlbControllerVersion", result)

    @builtins.property
    def policy(self) -> typing.Any:
        '''(experimental) The IAM policy to apply to the service account.

        If you're using one of the built-in versions, this is not required since
        CDK ships with the appropriate policies for those versions.

        However, if you are using a custom version, this is required (and validated).

        :default: - Corresponds to the predefined version.

        :stability: experimental
        '''
        result = self._values.get("policy")
        return typing.cast(typing.Any, result)

    @builtins.property
    def repository(self) -> typing.Optional[builtins.str]:
        '''(experimental) The repository to pull the controller image from.

        Note that the default repository works for most regions, but not all.
        If the repository is not applicable to your region, use a custom repository
        according to the information here: https://github.com/kubernetes-sigs/aws-load-balancer-controller/releases.

        :default: '602401143452.dkr.ecr.us-west-2.amazonaws.com/amazon/aws-load-balancer-controller'

        :stability: experimental
        '''
        result = self._values.get("repository")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "AlbControllerOptions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@aws-cdk/aws-eks-v2-alpha.AlbControllerProps",
    jsii_struct_bases=[AlbControllerOptions],
    name_mapping={
        "version": "version",
        "policy": "policy",
        "repository": "repository",
        "cluster": "cluster",
    },
)
class AlbControllerProps(AlbControllerOptions):
    def __init__(
        self,
        *,
        version: "AlbControllerVersion",
        policy: typing.Any = None,
        repository: typing.Optional[builtins.str] = None,
        cluster: "Cluster",
    ) -> None:
        '''(experimental) Properties for ``AlbController``.

        :param version: (experimental) Version of the controller.
        :param policy: (experimental) The IAM policy to apply to the service account. If you're using one of the built-in versions, this is not required since CDK ships with the appropriate policies for those versions. However, if you are using a custom version, this is required (and validated). Default: - Corresponds to the predefined version.
        :param repository: (experimental) The repository to pull the controller image from. Note that the default repository works for most regions, but not all. If the repository is not applicable to your region, use a custom repository according to the information here: https://github.com/kubernetes-sigs/aws-load-balancer-controller/releases. Default: '602401143452.dkr.ecr.us-west-2.amazonaws.com/amazon/aws-load-balancer-controller'
        :param cluster: (experimental) [disable-awslint:ref-via-interface] Cluster to install the controller onto.

        :stability: experimental
        :exampleMetadata: fixture=_generated

        Example::

            # The code below shows an example of how to instantiate this type.
            # The values are placeholders you should change.
            import aws_cdk.aws_eks_v2_alpha as eks_v2_alpha
            
            # alb_controller_version: eks_v2_alpha.AlbControllerVersion
            # cluster: eks_v2_alpha.Cluster
            # policy: Any
            
            alb_controller_props = eks_v2_alpha.AlbControllerProps(
                cluster=cluster,
                version=alb_controller_version,
            
                # the properties below are optional
                policy=policy,
                repository="repository"
            )
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8534a14f2dfaef545def42149b259d669b343d67a1d2e725421704e573f3ee13)
            check_type(argname="argument version", value=version, expected_type=type_hints["version"])
            check_type(argname="argument policy", value=policy, expected_type=type_hints["policy"])
            check_type(argname="argument repository", value=repository, expected_type=type_hints["repository"])
            check_type(argname="argument cluster", value=cluster, expected_type=type_hints["cluster"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "version": version,
            "cluster": cluster,
        }
        if policy is not None:
            self._values["policy"] = policy
        if repository is not None:
            self._values["repository"] = repository

    @builtins.property
    def version(self) -> "AlbControllerVersion":
        '''(experimental) Version of the controller.

        :stability: experimental
        '''
        result = self._values.get("version")
        assert result is not None, "Required property 'version' is missing"
        return typing.cast("AlbControllerVersion", result)

    @builtins.property
    def policy(self) -> typing.Any:
        '''(experimental) The IAM policy to apply to the service account.

        If you're using one of the built-in versions, this is not required since
        CDK ships with the appropriate policies for those versions.

        However, if you are using a custom version, this is required (and validated).

        :default: - Corresponds to the predefined version.

        :stability: experimental
        '''
        result = self._values.get("policy")
        return typing.cast(typing.Any, result)

    @builtins.property
    def repository(self) -> typing.Optional[builtins.str]:
        '''(experimental) The repository to pull the controller image from.

        Note that the default repository works for most regions, but not all.
        If the repository is not applicable to your region, use a custom repository
        according to the information here: https://github.com/kubernetes-sigs/aws-load-balancer-controller/releases.

        :default: '602401143452.dkr.ecr.us-west-2.amazonaws.com/amazon/aws-load-balancer-controller'

        :stability: experimental
        '''
        result = self._values.get("repository")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def cluster(self) -> "Cluster":
        '''(experimental) [disable-awslint:ref-via-interface] Cluster to install the controller onto.

        :stability: experimental
        '''
        result = self._values.get("cluster")
        assert result is not None, "Required property 'cluster' is missing"
        return typing.cast("Cluster", result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "AlbControllerProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class AlbControllerVersion(
    metaclass=jsii.JSIIMeta,
    jsii_type="@aws-cdk/aws-eks-v2-alpha.AlbControllerVersion",
):
    '''(experimental) Controller version.

    Corresponds to the image tag of 'amazon/aws-load-balancer-controller' image.

    :stability: experimental
    :exampleMetadata: infused

    Example::

        eks.Cluster(self, "HelloEKS",
            version=eks.KubernetesVersion.V1_33,
            alb_controller=eks.AlbControllerOptions(
                version=eks.AlbControllerVersion.V2_8_2
            )
        )
    '''

    @jsii.member(jsii_name="of")
    @builtins.classmethod
    def of(
        cls,
        version: builtins.str,
        helm_chart_version: typing.Optional[builtins.str] = None,
    ) -> "AlbControllerVersion":
        '''(experimental) Specify a custom version and an associated helm chart version.

        Use this if the version you need is not available in one of the predefined versions.
        Note that in this case, you will also need to provide an IAM policy in the controller options.

        ALB controller version and helm chart version compatibility information can be found
        here: https://github.com/aws/eks-charts/blob/v0.0.133/stable/aws-load-balancer-controller/Chart.yaml

        :param version: The version number.
        :param helm_chart_version: The version of the helm chart. Version 1.4.1 is the default version to support legacy users.

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1167bdec41553341107a601373e40e2bbf5ffeb8e179efc1ad19421c7989edf6)
            check_type(argname="argument version", value=version, expected_type=type_hints["version"])
            check_type(argname="argument helm_chart_version", value=helm_chart_version, expected_type=type_hints["helm_chart_version"])
        return typing.cast("AlbControllerVersion", jsii.sinvoke(cls, "of", [version, helm_chart_version]))

    @jsii.python.classproperty
    @jsii.member(jsii_name="V2_0_0")
    def V2_0_0(cls) -> "AlbControllerVersion":
        '''(experimental) v2.0.0.

        :stability: experimental
        '''
        return typing.cast("AlbControllerVersion", jsii.sget(cls, "V2_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="V2_0_1")
    def V2_0_1(cls) -> "AlbControllerVersion":
        '''(experimental) v2.0.1.

        :stability: experimental
        '''
        return typing.cast("AlbControllerVersion", jsii.sget(cls, "V2_0_1"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="V2_1_0")
    def V2_1_0(cls) -> "AlbControllerVersion":
        '''(experimental) v2.1.0.

        :stability: experimental
        '''
        return typing.cast("AlbControllerVersion", jsii.sget(cls, "V2_1_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="V2_1_1")
    def V2_1_1(cls) -> "AlbControllerVersion":
        '''(experimental) v2.1.1.

        :stability: experimental
        '''
        return typing.cast("AlbControllerVersion", jsii.sget(cls, "V2_1_1"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="V2_1_2")
    def V2_1_2(cls) -> "AlbControllerVersion":
        '''(experimental) v2.1.2.

        :stability: experimental
        '''
        return typing.cast("AlbControllerVersion", jsii.sget(cls, "V2_1_2"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="V2_1_3")
    def V2_1_3(cls) -> "AlbControllerVersion":
        '''(experimental) v2.1.3.

        :stability: experimental
        '''
        return typing.cast("AlbControllerVersion", jsii.sget(cls, "V2_1_3"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="V2_2_0")
    def V2_2_0(cls) -> "AlbControllerVersion":
        '''(experimental) v2.0.0.

        :stability: experimental
        '''
        return typing.cast("AlbControllerVersion", jsii.sget(cls, "V2_2_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="V2_2_1")
    def V2_2_1(cls) -> "AlbControllerVersion":
        '''(experimental) v2.2.1.

        :stability: experimental
        '''
        return typing.cast("AlbControllerVersion", jsii.sget(cls, "V2_2_1"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="V2_2_2")
    def V2_2_2(cls) -> "AlbControllerVersion":
        '''(experimental) v2.2.2.

        :stability: experimental
        '''
        return typing.cast("AlbControllerVersion", jsii.sget(cls, "V2_2_2"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="V2_2_3")
    def V2_2_3(cls) -> "AlbControllerVersion":
        '''(experimental) v2.2.3.

        :stability: experimental
        '''
        return typing.cast("AlbControllerVersion", jsii.sget(cls, "V2_2_3"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="V2_2_4")
    def V2_2_4(cls) -> "AlbControllerVersion":
        '''(experimental) v2.2.4.

        :stability: experimental
        '''
        return typing.cast("AlbControllerVersion", jsii.sget(cls, "V2_2_4"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="V2_3_0")
    def V2_3_0(cls) -> "AlbControllerVersion":
        '''(experimental) v2.3.0.

        :stability: experimental
        '''
        return typing.cast("AlbControllerVersion", jsii.sget(cls, "V2_3_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="V2_3_1")
    def V2_3_1(cls) -> "AlbControllerVersion":
        '''(experimental) v2.3.1.

        :stability: experimental
        '''
        return typing.cast("AlbControllerVersion", jsii.sget(cls, "V2_3_1"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="V2_4_1")
    def V2_4_1(cls) -> "AlbControllerVersion":
        '''(experimental) v2.4.1.

        :stability: experimental
        '''
        return typing.cast("AlbControllerVersion", jsii.sget(cls, "V2_4_1"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="V2_4_2")
    def V2_4_2(cls) -> "AlbControllerVersion":
        '''(experimental) v2.4.2.

        :stability: experimental
        '''
        return typing.cast("AlbControllerVersion", jsii.sget(cls, "V2_4_2"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="V2_4_3")
    def V2_4_3(cls) -> "AlbControllerVersion":
        '''(experimental) v2.4.3.

        :stability: experimental
        '''
        return typing.cast("AlbControllerVersion", jsii.sget(cls, "V2_4_3"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="V2_4_4")
    def V2_4_4(cls) -> "AlbControllerVersion":
        '''(experimental) v2.4.4.

        :stability: experimental
        '''
        return typing.cast("AlbControllerVersion", jsii.sget(cls, "V2_4_4"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="V2_4_5")
    def V2_4_5(cls) -> "AlbControllerVersion":
        '''(experimental) v2.4.5.

        :stability: experimental
        '''
        return typing.cast("AlbControllerVersion", jsii.sget(cls, "V2_4_5"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="V2_4_6")
    def V2_4_6(cls) -> "AlbControllerVersion":
        '''(experimental) v2.4.6.

        :stability: experimental
        '''
        return typing.cast("AlbControllerVersion", jsii.sget(cls, "V2_4_6"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="V2_4_7")
    def V2_4_7(cls) -> "AlbControllerVersion":
        '''(experimental) v2.4.7.

        :stability: experimental
        '''
        return typing.cast("AlbControllerVersion", jsii.sget(cls, "V2_4_7"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="V2_5_0")
    def V2_5_0(cls) -> "AlbControllerVersion":
        '''(experimental) v2.5.0.

        :stability: experimental
        '''
        return typing.cast("AlbControllerVersion", jsii.sget(cls, "V2_5_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="V2_5_1")
    def V2_5_1(cls) -> "AlbControllerVersion":
        '''(experimental) v2.5.1.

        :stability: experimental
        '''
        return typing.cast("AlbControllerVersion", jsii.sget(cls, "V2_5_1"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="V2_5_2")
    def V2_5_2(cls) -> "AlbControllerVersion":
        '''(experimental) v2.5.2.

        :stability: experimental
        '''
        return typing.cast("AlbControllerVersion", jsii.sget(cls, "V2_5_2"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="V2_5_3")
    def V2_5_3(cls) -> "AlbControllerVersion":
        '''(experimental) v2.5.3.

        :stability: experimental
        '''
        return typing.cast("AlbControllerVersion", jsii.sget(cls, "V2_5_3"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="V2_5_4")
    def V2_5_4(cls) -> "AlbControllerVersion":
        '''(experimental) v2.5.4.

        :stability: experimental
        '''
        return typing.cast("AlbControllerVersion", jsii.sget(cls, "V2_5_4"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="V2_6_0")
    def V2_6_0(cls) -> "AlbControllerVersion":
        '''(experimental) v2.6.0.

        :stability: experimental
        '''
        return typing.cast("AlbControllerVersion", jsii.sget(cls, "V2_6_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="V2_6_1")
    def V2_6_1(cls) -> "AlbControllerVersion":
        '''(experimental) v2.6.1.

        :stability: experimental
        '''
        return typing.cast("AlbControllerVersion", jsii.sget(cls, "V2_6_1"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="V2_6_2")
    def V2_6_2(cls) -> "AlbControllerVersion":
        '''(experimental) v2.6.2.

        :stability: experimental
        '''
        return typing.cast("AlbControllerVersion", jsii.sget(cls, "V2_6_2"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="V2_7_0")
    def V2_7_0(cls) -> "AlbControllerVersion":
        '''(experimental) v2.7.0.

        :stability: experimental
        '''
        return typing.cast("AlbControllerVersion", jsii.sget(cls, "V2_7_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="V2_7_1")
    def V2_7_1(cls) -> "AlbControllerVersion":
        '''(experimental) v2.7.1.

        :stability: experimental
        '''
        return typing.cast("AlbControllerVersion", jsii.sget(cls, "V2_7_1"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="V2_7_2")
    def V2_7_2(cls) -> "AlbControllerVersion":
        '''(experimental) v2.7.2.

        :stability: experimental
        '''
        return typing.cast("AlbControllerVersion", jsii.sget(cls, "V2_7_2"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="V2_8_0")
    def V2_8_0(cls) -> "AlbControllerVersion":
        '''(experimental) v2.8.0.

        :stability: experimental
        '''
        return typing.cast("AlbControllerVersion", jsii.sget(cls, "V2_8_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="V2_8_1")
    def V2_8_1(cls) -> "AlbControllerVersion":
        '''(experimental) v2.8.1.

        :stability: experimental
        '''
        return typing.cast("AlbControllerVersion", jsii.sget(cls, "V2_8_1"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="V2_8_2")
    def V2_8_2(cls) -> "AlbControllerVersion":
        '''(experimental) v2.8.2.

        :stability: experimental
        '''
        return typing.cast("AlbControllerVersion", jsii.sget(cls, "V2_8_2"))

    @builtins.property
    @jsii.member(jsii_name="custom")
    def custom(self) -> builtins.bool:
        '''(experimental) Whether or not its a custom version.

        :stability: experimental
        '''
        return typing.cast(builtins.bool, jsii.get(self, "custom"))

    @builtins.property
    @jsii.member(jsii_name="helmChartVersion")
    def helm_chart_version(self) -> builtins.str:
        '''(experimental) The version of the helm chart to use.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "helmChartVersion"))

    @builtins.property
    @jsii.member(jsii_name="version")
    def version(self) -> builtins.str:
        '''(experimental) The version string.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "version"))


@jsii.enum(jsii_type="@aws-cdk/aws-eks-v2-alpha.AlbScheme")
class AlbScheme(enum.Enum):
    '''(experimental) ALB Scheme.

    :see: https://kubernetes-sigs.github.io/aws-load-balancer-controller/v2.3/guide/ingress/annotations/#scheme
    :stability: experimental
    '''

    INTERNAL = "INTERNAL"
    '''(experimental) The nodes of an internal load balancer have only private IP addresses.

    The DNS name of an internal load balancer is publicly resolvable to the private IP addresses of the nodes.
    Therefore, internal load balancers can only route requests from clients with access to the VPC for the load balancer.

    :stability: experimental
    '''
    INTERNET_FACING = "INTERNET_FACING"
    '''(experimental) An internet-facing load balancer has a publicly resolvable DNS name, so it can route requests from clients over the internet to the EC2 instances that are registered with the load balancer.

    :stability: experimental
    '''


@jsii.data_type(
    jsii_type="@aws-cdk/aws-eks-v2-alpha.AutoScalingGroupCapacityOptions",
    jsii_struct_bases=[_aws_cdk_aws_autoscaling_ceddda9d.CommonAutoScalingGroupProps],
    name_mapping={
        "allow_all_outbound": "allowAllOutbound",
        "associate_public_ip_address": "associatePublicIpAddress",
        "auto_scaling_group_name": "autoScalingGroupName",
        "az_capacity_distribution_strategy": "azCapacityDistributionStrategy",
        "block_devices": "blockDevices",
        "capacity_rebalance": "capacityRebalance",
        "cooldown": "cooldown",
        "default_instance_warmup": "defaultInstanceWarmup",
        "desired_capacity": "desiredCapacity",
        "group_metrics": "groupMetrics",
        "health_check": "healthCheck",
        "health_checks": "healthChecks",
        "ignore_unmodified_size_properties": "ignoreUnmodifiedSizeProperties",
        "instance_monitoring": "instanceMonitoring",
        "key_name": "keyName",
        "key_pair": "keyPair",
        "max_capacity": "maxCapacity",
        "max_instance_lifetime": "maxInstanceLifetime",
        "min_capacity": "minCapacity",
        "new_instances_protected_from_scale_in": "newInstancesProtectedFromScaleIn",
        "notifications": "notifications",
        "signals": "signals",
        "spot_price": "spotPrice",
        "ssm_session_permissions": "ssmSessionPermissions",
        "termination_policies": "terminationPolicies",
        "termination_policy_custom_lambda_function_arn": "terminationPolicyCustomLambdaFunctionArn",
        "update_policy": "updatePolicy",
        "vpc_subnets": "vpcSubnets",
        "instance_type": "instanceType",
        "bootstrap_enabled": "bootstrapEnabled",
        "bootstrap_options": "bootstrapOptions",
        "machine_image_type": "machineImageType",
    },
)
class AutoScalingGroupCapacityOptions(
    _aws_cdk_aws_autoscaling_ceddda9d.CommonAutoScalingGroupProps,
):
    def __init__(
        self,
        *,
        allow_all_outbound: typing.Optional[builtins.bool] = None,
        associate_public_ip_address: typing.Optional[builtins.bool] = None,
        auto_scaling_group_name: typing.Optional[builtins.str] = None,
        az_capacity_distribution_strategy: typing.Optional[_aws_cdk_aws_autoscaling_ceddda9d.CapacityDistributionStrategy] = None,
        block_devices: typing.Optional[typing.Sequence[typing.Union[_aws_cdk_aws_autoscaling_ceddda9d.BlockDevice, typing.Dict[builtins.str, typing.Any]]]] = None,
        capacity_rebalance: typing.Optional[builtins.bool] = None,
        cooldown: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        default_instance_warmup: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        desired_capacity: typing.Optional[jsii.Number] = None,
        group_metrics: typing.Optional[typing.Sequence[_aws_cdk_aws_autoscaling_ceddda9d.GroupMetrics]] = None,
        health_check: typing.Optional[_aws_cdk_aws_autoscaling_ceddda9d.HealthCheck] = None,
        health_checks: typing.Optional[_aws_cdk_aws_autoscaling_ceddda9d.HealthChecks] = None,
        ignore_unmodified_size_properties: typing.Optional[builtins.bool] = None,
        instance_monitoring: typing.Optional[_aws_cdk_aws_autoscaling_ceddda9d.Monitoring] = None,
        key_name: typing.Optional[builtins.str] = None,
        key_pair: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IKeyPair] = None,
        max_capacity: typing.Optional[jsii.Number] = None,
        max_instance_lifetime: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        min_capacity: typing.Optional[jsii.Number] = None,
        new_instances_protected_from_scale_in: typing.Optional[builtins.bool] = None,
        notifications: typing.Optional[typing.Sequence[typing.Union[_aws_cdk_aws_autoscaling_ceddda9d.NotificationConfiguration, typing.Dict[builtins.str, typing.Any]]]] = None,
        signals: typing.Optional[_aws_cdk_aws_autoscaling_ceddda9d.Signals] = None,
        spot_price: typing.Optional[builtins.str] = None,
        ssm_session_permissions: typing.Optional[builtins.bool] = None,
        termination_policies: typing.Optional[typing.Sequence[_aws_cdk_aws_autoscaling_ceddda9d.TerminationPolicy]] = None,
        termination_policy_custom_lambda_function_arn: typing.Optional[builtins.str] = None,
        update_policy: typing.Optional[_aws_cdk_aws_autoscaling_ceddda9d.UpdatePolicy] = None,
        vpc_subnets: typing.Optional[typing.Union[_aws_cdk_aws_ec2_ceddda9d.SubnetSelection, typing.Dict[builtins.str, typing.Any]]] = None,
        instance_type: _aws_cdk_aws_ec2_ceddda9d.InstanceType,
        bootstrap_enabled: typing.Optional[builtins.bool] = None,
        bootstrap_options: typing.Optional[typing.Union["BootstrapOptions", typing.Dict[builtins.str, typing.Any]]] = None,
        machine_image_type: typing.Optional["MachineImageType"] = None,
    ) -> None:
        '''(experimental) Options for adding worker nodes.

        :param allow_all_outbound: Whether the instances can initiate connections to anywhere by default. Default: true
        :param associate_public_ip_address: Whether instances in the Auto Scaling Group should have public IP addresses associated with them. ``launchTemplate`` and ``mixedInstancesPolicy`` must not be specified when this property is specified Default: - Use subnet setting.
        :param auto_scaling_group_name: The name of the Auto Scaling group. This name must be unique per Region per account. Default: - Auto generated by CloudFormation
        :param az_capacity_distribution_strategy: The strategy for distributing instances across Availability Zones. Default: None
        :param block_devices: Specifies how block devices are exposed to the instance. You can specify virtual devices and EBS volumes. Each instance that is launched has an associated root device volume, either an Amazon EBS volume or an instance store volume. You can use block device mappings to specify additional EBS volumes or instance store volumes to attach to an instance when it is launched. ``launchTemplate`` and ``mixedInstancesPolicy`` must not be specified when this property is specified Default: - Uses the block device mapping of the AMI
        :param capacity_rebalance: Indicates whether Capacity Rebalancing is enabled. When you turn on Capacity Rebalancing, Amazon EC2 Auto Scaling attempts to launch a Spot Instance whenever Amazon EC2 notifies that a Spot Instance is at an elevated risk of interruption. After launching a new instance, it then terminates an old instance. Default: false
        :param cooldown: Default scaling cooldown for this AutoScalingGroup. Default: Duration.minutes(5)
        :param default_instance_warmup: The amount of time, in seconds, until a newly launched instance can contribute to the Amazon CloudWatch metrics. This delay lets an instance finish initializing before Amazon EC2 Auto Scaling aggregates instance metrics, resulting in more reliable usage data. Set this value equal to the amount of time that it takes for resource consumption to become stable after an instance reaches the InService state. To optimize the performance of scaling policies that scale continuously, such as target tracking and step scaling policies, we strongly recommend that you enable the default instance warmup, even if its value is set to 0 seconds Default instance warmup will not be added if no value is specified Default: None
        :param desired_capacity: Initial amount of instances in the fleet. If this is set to a number, every deployment will reset the amount of instances to this number. It is recommended to leave this value blank. Default: minCapacity, and leave unchanged during deployment
        :param group_metrics: Enable monitoring for group metrics, these metrics describe the group rather than any of its instances. To report all group metrics use ``GroupMetrics.all()`` Group metrics are reported in a granularity of 1 minute at no additional charge. Default: - no group metrics will be reported
        :param health_check: (deprecated) Configuration for health checks. Default: - HealthCheck.ec2 with no grace period
        :param health_checks: Configuration for EC2 or additional health checks. Even when using ``HealthChecks.withAdditionalChecks()``, the EC2 type is implicitly included. Default: - EC2 type with no grace period
        :param ignore_unmodified_size_properties: If the ASG has scheduled actions, don't reset unchanged group sizes. Only used if the ASG has scheduled actions (which may scale your ASG up or down regardless of cdk deployments). If true, the size of the group will only be reset if it has been changed in the CDK app. If false, the sizes will always be changed back to what they were in the CDK app on deployment. Default: true
        :param instance_monitoring: Controls whether instances in this group are launched with detailed or basic monitoring. When detailed monitoring is enabled, Amazon CloudWatch generates metrics every minute and your account is charged a fee. When you disable detailed monitoring, CloudWatch generates metrics every 5 minutes. ``launchTemplate`` and ``mixedInstancesPolicy`` must not be specified when this property is specified Default: - Monitoring.DETAILED
        :param key_name: (deprecated) Name of SSH keypair to grant access to instances. ``launchTemplate`` and ``mixedInstancesPolicy`` must not be specified when this property is specified You can either specify ``keyPair`` or ``keyName``, not both. Default: - No SSH access will be possible.
        :param key_pair: The SSH keypair to grant access to the instance. Feature flag ``AUTOSCALING_GENERATE_LAUNCH_TEMPLATE`` must be enabled to use this property. ``launchTemplate`` and ``mixedInstancesPolicy`` must not be specified when this property is specified. You can either specify ``keyPair`` or ``keyName``, not both. Default: - No SSH access will be possible.
        :param max_capacity: Maximum number of instances in the fleet. Default: desiredCapacity
        :param max_instance_lifetime: The maximum amount of time that an instance can be in service. The maximum duration applies to all current and future instances in the group. As an instance approaches its maximum duration, it is terminated and replaced, and cannot be used again. You must specify a value of at least 86,400 seconds (one day). To clear a previously set value, leave this property undefined. Default: none
        :param min_capacity: Minimum number of instances in the fleet. Default: 1
        :param new_instances_protected_from_scale_in: Whether newly-launched instances are protected from termination by Amazon EC2 Auto Scaling when scaling in. By default, Auto Scaling can terminate an instance at any time after launch when scaling in an Auto Scaling Group, subject to the group's termination policy. However, you may wish to protect newly-launched instances from being scaled in if they are going to run critical applications that should not be prematurely terminated. This flag must be enabled if the Auto Scaling Group will be associated with an ECS Capacity Provider with managed termination protection. Default: false
        :param notifications: Configure autoscaling group to send notifications about fleet changes to an SNS topic(s). Default: - No fleet change notifications will be sent.
        :param signals: Configure waiting for signals during deployment. Use this to pause the CloudFormation deployment to wait for the instances in the AutoScalingGroup to report successful startup during creation and updates. The UserData script needs to invoke ``cfn-signal`` with a success or failure code after it is done setting up the instance. Without waiting for signals, the CloudFormation deployment will proceed as soon as the AutoScalingGroup has been created or updated but before the instances in the group have been started. For example, to have instances wait for an Elastic Load Balancing health check before they signal success, add a health-check verification by using the cfn-init helper script. For an example, see the verify_instance_health command in the Auto Scaling rolling updates sample template: https://github.com/awslabs/aws-cloudformation-templates/blob/master/aws/services/AutoScaling/AutoScalingRollingUpdates.yaml Default: - Do not wait for signals
        :param spot_price: The maximum hourly price (in USD) to be paid for any Spot Instance launched to fulfill the request. Spot Instances are launched when the price you specify exceeds the current Spot market price. ``launchTemplate`` and ``mixedInstancesPolicy`` must not be specified when this property is specified Default: none
        :param ssm_session_permissions: Add SSM session permissions to the instance role. Setting this to ``true`` adds the necessary permissions to connect to the instance using SSM Session Manager. You can do this from the AWS Console. NOTE: Setting this flag to ``true`` may not be enough by itself. You must also use an AMI that comes with the SSM Agent, or install the SSM Agent yourself. See `Working with SSM Agent <https://docs.aws.amazon.com/systems-manager/latest/userguide/ssm-agent.html>`_ in the SSM Developer Guide. Default: false
        :param termination_policies: A policy or a list of policies that are used to select the instances to terminate. The policies are executed in the order that you list them. Default: - ``TerminationPolicy.DEFAULT``
        :param termination_policy_custom_lambda_function_arn: A lambda function Arn that can be used as a custom termination policy to select the instances to terminate. This property must be specified if the TerminationPolicy.CUSTOM_LAMBDA_FUNCTION is used. Default: - No lambda function Arn will be supplied
        :param update_policy: What to do when an AutoScalingGroup's instance configuration is changed. This is applied when any of the settings on the ASG are changed that affect how the instances should be created (VPC, instance type, startup scripts, etc.). It indicates how the existing instances should be replaced with new instances matching the new config. By default, nothing is done and only new instances are launched with the new config. Default: - ``UpdatePolicy.rollingUpdate()`` if using ``init``, ``UpdatePolicy.none()`` otherwise
        :param vpc_subnets: Where to place instances within the VPC. Default: - All Private subnets.
        :param instance_type: (experimental) Instance type of the instances to start.
        :param bootstrap_enabled: (experimental) Configures the EC2 user-data script for instances in this autoscaling group to bootstrap the node (invoke ``/etc/eks/bootstrap.sh``) and associate it with the EKS cluster. If you wish to provide a custom user data script, set this to ``false`` and manually invoke ``autoscalingGroup.addUserData()``. Default: true
        :param bootstrap_options: (experimental) EKS node bootstrapping options. Default: - none
        :param machine_image_type: (experimental) Machine image type. Default: MachineImageType.AMAZON_LINUX_2

        :stability: experimental
        :exampleMetadata: infused

        Example::

            # vpc: ec2.Vpc
            # cluster: eks.Cluster
            
            cluster.add_auto_scaling_group_capacity("nodes",
                vpc_subnets=ec2.SubnetSelection(subnets=vpc.private_subnets),
                instance_type=ec2.InstanceType("t2.medium")
            )
        '''
        if isinstance(vpc_subnets, dict):
            vpc_subnets = _aws_cdk_aws_ec2_ceddda9d.SubnetSelection(**vpc_subnets)
        if isinstance(bootstrap_options, dict):
            bootstrap_options = BootstrapOptions(**bootstrap_options)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__eb99c268be8192566d7bfb495648a3dadbee5b1ea942e5f4d69e1a57935ac540)
            check_type(argname="argument allow_all_outbound", value=allow_all_outbound, expected_type=type_hints["allow_all_outbound"])
            check_type(argname="argument associate_public_ip_address", value=associate_public_ip_address, expected_type=type_hints["associate_public_ip_address"])
            check_type(argname="argument auto_scaling_group_name", value=auto_scaling_group_name, expected_type=type_hints["auto_scaling_group_name"])
            check_type(argname="argument az_capacity_distribution_strategy", value=az_capacity_distribution_strategy, expected_type=type_hints["az_capacity_distribution_strategy"])
            check_type(argname="argument block_devices", value=block_devices, expected_type=type_hints["block_devices"])
            check_type(argname="argument capacity_rebalance", value=capacity_rebalance, expected_type=type_hints["capacity_rebalance"])
            check_type(argname="argument cooldown", value=cooldown, expected_type=type_hints["cooldown"])
            check_type(argname="argument default_instance_warmup", value=default_instance_warmup, expected_type=type_hints["default_instance_warmup"])
            check_type(argname="argument desired_capacity", value=desired_capacity, expected_type=type_hints["desired_capacity"])
            check_type(argname="argument group_metrics", value=group_metrics, expected_type=type_hints["group_metrics"])
            check_type(argname="argument health_check", value=health_check, expected_type=type_hints["health_check"])
            check_type(argname="argument health_checks", value=health_checks, expected_type=type_hints["health_checks"])
            check_type(argname="argument ignore_unmodified_size_properties", value=ignore_unmodified_size_properties, expected_type=type_hints["ignore_unmodified_size_properties"])
            check_type(argname="argument instance_monitoring", value=instance_monitoring, expected_type=type_hints["instance_monitoring"])
            check_type(argname="argument key_name", value=key_name, expected_type=type_hints["key_name"])
            check_type(argname="argument key_pair", value=key_pair, expected_type=type_hints["key_pair"])
            check_type(argname="argument max_capacity", value=max_capacity, expected_type=type_hints["max_capacity"])
            check_type(argname="argument max_instance_lifetime", value=max_instance_lifetime, expected_type=type_hints["max_instance_lifetime"])
            check_type(argname="argument min_capacity", value=min_capacity, expected_type=type_hints["min_capacity"])
            check_type(argname="argument new_instances_protected_from_scale_in", value=new_instances_protected_from_scale_in, expected_type=type_hints["new_instances_protected_from_scale_in"])
            check_type(argname="argument notifications", value=notifications, expected_type=type_hints["notifications"])
            check_type(argname="argument signals", value=signals, expected_type=type_hints["signals"])
            check_type(argname="argument spot_price", value=spot_price, expected_type=type_hints["spot_price"])
            check_type(argname="argument ssm_session_permissions", value=ssm_session_permissions, expected_type=type_hints["ssm_session_permissions"])
            check_type(argname="argument termination_policies", value=termination_policies, expected_type=type_hints["termination_policies"])
            check_type(argname="argument termination_policy_custom_lambda_function_arn", value=termination_policy_custom_lambda_function_arn, expected_type=type_hints["termination_policy_custom_lambda_function_arn"])
            check_type(argname="argument update_policy", value=update_policy, expected_type=type_hints["update_policy"])
            check_type(argname="argument vpc_subnets", value=vpc_subnets, expected_type=type_hints["vpc_subnets"])
            check_type(argname="argument instance_type", value=instance_type, expected_type=type_hints["instance_type"])
            check_type(argname="argument bootstrap_enabled", value=bootstrap_enabled, expected_type=type_hints["bootstrap_enabled"])
            check_type(argname="argument bootstrap_options", value=bootstrap_options, expected_type=type_hints["bootstrap_options"])
            check_type(argname="argument machine_image_type", value=machine_image_type, expected_type=type_hints["machine_image_type"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "instance_type": instance_type,
        }
        if allow_all_outbound is not None:
            self._values["allow_all_outbound"] = allow_all_outbound
        if associate_public_ip_address is not None:
            self._values["associate_public_ip_address"] = associate_public_ip_address
        if auto_scaling_group_name is not None:
            self._values["auto_scaling_group_name"] = auto_scaling_group_name
        if az_capacity_distribution_strategy is not None:
            self._values["az_capacity_distribution_strategy"] = az_capacity_distribution_strategy
        if block_devices is not None:
            self._values["block_devices"] = block_devices
        if capacity_rebalance is not None:
            self._values["capacity_rebalance"] = capacity_rebalance
        if cooldown is not None:
            self._values["cooldown"] = cooldown
        if default_instance_warmup is not None:
            self._values["default_instance_warmup"] = default_instance_warmup
        if desired_capacity is not None:
            self._values["desired_capacity"] = desired_capacity
        if group_metrics is not None:
            self._values["group_metrics"] = group_metrics
        if health_check is not None:
            self._values["health_check"] = health_check
        if health_checks is not None:
            self._values["health_checks"] = health_checks
        if ignore_unmodified_size_properties is not None:
            self._values["ignore_unmodified_size_properties"] = ignore_unmodified_size_properties
        if instance_monitoring is not None:
            self._values["instance_monitoring"] = instance_monitoring
        if key_name is not None:
            self._values["key_name"] = key_name
        if key_pair is not None:
            self._values["key_pair"] = key_pair
        if max_capacity is not None:
            self._values["max_capacity"] = max_capacity
        if max_instance_lifetime is not None:
            self._values["max_instance_lifetime"] = max_instance_lifetime
        if min_capacity is not None:
            self._values["min_capacity"] = min_capacity
        if new_instances_protected_from_scale_in is not None:
            self._values["new_instances_protected_from_scale_in"] = new_instances_protected_from_scale_in
        if notifications is not None:
            self._values["notifications"] = notifications
        if signals is not None:
            self._values["signals"] = signals
        if spot_price is not None:
            self._values["spot_price"] = spot_price
        if ssm_session_permissions is not None:
            self._values["ssm_session_permissions"] = ssm_session_permissions
        if termination_policies is not None:
            self._values["termination_policies"] = termination_policies
        if termination_policy_custom_lambda_function_arn is not None:
            self._values["termination_policy_custom_lambda_function_arn"] = termination_policy_custom_lambda_function_arn
        if update_policy is not None:
            self._values["update_policy"] = update_policy
        if vpc_subnets is not None:
            self._values["vpc_subnets"] = vpc_subnets
        if bootstrap_enabled is not None:
            self._values["bootstrap_enabled"] = bootstrap_enabled
        if bootstrap_options is not None:
            self._values["bootstrap_options"] = bootstrap_options
        if machine_image_type is not None:
            self._values["machine_image_type"] = machine_image_type

    @builtins.property
    def allow_all_outbound(self) -> typing.Optional[builtins.bool]:
        '''Whether the instances can initiate connections to anywhere by default.

        :default: true
        '''
        result = self._values.get("allow_all_outbound")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def associate_public_ip_address(self) -> typing.Optional[builtins.bool]:
        '''Whether instances in the Auto Scaling Group should have public IP addresses associated with them.

        ``launchTemplate`` and ``mixedInstancesPolicy`` must not be specified when this property is specified

        :default: - Use subnet setting.
        '''
        result = self._values.get("associate_public_ip_address")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def auto_scaling_group_name(self) -> typing.Optional[builtins.str]:
        '''The name of the Auto Scaling group.

        This name must be unique per Region per account.

        :default: - Auto generated by CloudFormation
        '''
        result = self._values.get("auto_scaling_group_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def az_capacity_distribution_strategy(
        self,
    ) -> typing.Optional[_aws_cdk_aws_autoscaling_ceddda9d.CapacityDistributionStrategy]:
        '''The strategy for distributing instances across Availability Zones.

        :default: None
        '''
        result = self._values.get("az_capacity_distribution_strategy")
        return typing.cast(typing.Optional[_aws_cdk_aws_autoscaling_ceddda9d.CapacityDistributionStrategy], result)

    @builtins.property
    def block_devices(
        self,
    ) -> typing.Optional[typing.List[_aws_cdk_aws_autoscaling_ceddda9d.BlockDevice]]:
        '''Specifies how block devices are exposed to the instance. You can specify virtual devices and EBS volumes.

        Each instance that is launched has an associated root device volume,
        either an Amazon EBS volume or an instance store volume.
        You can use block device mappings to specify additional EBS volumes or
        instance store volumes to attach to an instance when it is launched.

        ``launchTemplate`` and ``mixedInstancesPolicy`` must not be specified when this property is specified

        :default: - Uses the block device mapping of the AMI

        :see: https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/block-device-mapping-concepts.html
        '''
        result = self._values.get("block_devices")
        return typing.cast(typing.Optional[typing.List[_aws_cdk_aws_autoscaling_ceddda9d.BlockDevice]], result)

    @builtins.property
    def capacity_rebalance(self) -> typing.Optional[builtins.bool]:
        '''Indicates whether Capacity Rebalancing is enabled.

        When you turn on Capacity Rebalancing, Amazon EC2 Auto Scaling
        attempts to launch a Spot Instance whenever Amazon EC2 notifies that a Spot Instance is at an elevated risk of
        interruption. After launching a new instance, it then terminates an old instance.

        :default: false

        :see: https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-as-group.html#cfn-as-group-capacityrebalance
        '''
        result = self._values.get("capacity_rebalance")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def cooldown(self) -> typing.Optional[_aws_cdk_ceddda9d.Duration]:
        '''Default scaling cooldown for this AutoScalingGroup.

        :default: Duration.minutes(5)
        '''
        result = self._values.get("cooldown")
        return typing.cast(typing.Optional[_aws_cdk_ceddda9d.Duration], result)

    @builtins.property
    def default_instance_warmup(self) -> typing.Optional[_aws_cdk_ceddda9d.Duration]:
        '''The amount of time, in seconds, until a newly launched instance can contribute to the Amazon CloudWatch metrics.

        This delay lets an instance finish initializing before Amazon EC2 Auto Scaling aggregates instance metrics,
        resulting in more reliable usage data. Set this value equal to the amount of time that it takes for resource
        consumption to become stable after an instance reaches the InService state.

        To optimize the performance of scaling policies that scale continuously, such as target tracking and
        step scaling policies, we strongly recommend that you enable the default instance warmup, even if its value is set to 0 seconds

        Default instance warmup will not be added if no value is specified

        :default: None

        :see: https://docs.aws.amazon.com/autoscaling/ec2/userguide/ec2-auto-scaling-default-instance-warmup.html
        '''
        result = self._values.get("default_instance_warmup")
        return typing.cast(typing.Optional[_aws_cdk_ceddda9d.Duration], result)

    @builtins.property
    def desired_capacity(self) -> typing.Optional[jsii.Number]:
        '''Initial amount of instances in the fleet.

        If this is set to a number, every deployment will reset the amount of
        instances to this number. It is recommended to leave this value blank.

        :default: minCapacity, and leave unchanged during deployment

        :see: https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-as-group.html#cfn-as-group-desiredcapacity
        '''
        result = self._values.get("desired_capacity")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def group_metrics(
        self,
    ) -> typing.Optional[typing.List[_aws_cdk_aws_autoscaling_ceddda9d.GroupMetrics]]:
        '''Enable monitoring for group metrics, these metrics describe the group rather than any of its instances.

        To report all group metrics use ``GroupMetrics.all()``
        Group metrics are reported in a granularity of 1 minute at no additional charge.

        :default: - no group metrics will be reported
        '''
        result = self._values.get("group_metrics")
        return typing.cast(typing.Optional[typing.List[_aws_cdk_aws_autoscaling_ceddda9d.GroupMetrics]], result)

    @builtins.property
    def health_check(
        self,
    ) -> typing.Optional[_aws_cdk_aws_autoscaling_ceddda9d.HealthCheck]:
        '''(deprecated) Configuration for health checks.

        :default: - HealthCheck.ec2 with no grace period

        :deprecated: Use ``healthChecks`` instead

        :stability: deprecated
        '''
        result = self._values.get("health_check")
        return typing.cast(typing.Optional[_aws_cdk_aws_autoscaling_ceddda9d.HealthCheck], result)

    @builtins.property
    def health_checks(
        self,
    ) -> typing.Optional[_aws_cdk_aws_autoscaling_ceddda9d.HealthChecks]:
        '''Configuration for EC2 or additional health checks.

        Even when using ``HealthChecks.withAdditionalChecks()``, the EC2 type is implicitly included.

        :default: - EC2 type with no grace period

        :see: https://docs.aws.amazon.com/autoscaling/ec2/userguide/ec2-auto-scaling-health-checks.html
        '''
        result = self._values.get("health_checks")
        return typing.cast(typing.Optional[_aws_cdk_aws_autoscaling_ceddda9d.HealthChecks], result)

    @builtins.property
    def ignore_unmodified_size_properties(self) -> typing.Optional[builtins.bool]:
        '''If the ASG has scheduled actions, don't reset unchanged group sizes.

        Only used if the ASG has scheduled actions (which may scale your ASG up
        or down regardless of cdk deployments). If true, the size of the group
        will only be reset if it has been changed in the CDK app. If false, the
        sizes will always be changed back to what they were in the CDK app
        on deployment.

        :default: true
        '''
        result = self._values.get("ignore_unmodified_size_properties")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def instance_monitoring(
        self,
    ) -> typing.Optional[_aws_cdk_aws_autoscaling_ceddda9d.Monitoring]:
        '''Controls whether instances in this group are launched with detailed or basic monitoring.

        When detailed monitoring is enabled, Amazon CloudWatch generates metrics every minute and your account
        is charged a fee. When you disable detailed monitoring, CloudWatch generates metrics every 5 minutes.

        ``launchTemplate`` and ``mixedInstancesPolicy`` must not be specified when this property is specified

        :default: - Monitoring.DETAILED

        :see: https://docs.aws.amazon.com/autoscaling/latest/userguide/as-instance-monitoring.html#enable-as-instance-metrics
        '''
        result = self._values.get("instance_monitoring")
        return typing.cast(typing.Optional[_aws_cdk_aws_autoscaling_ceddda9d.Monitoring], result)

    @builtins.property
    def key_name(self) -> typing.Optional[builtins.str]:
        '''(deprecated) Name of SSH keypair to grant access to instances.

        ``launchTemplate`` and ``mixedInstancesPolicy`` must not be specified when this property is specified

        You can either specify ``keyPair`` or ``keyName``, not both.

        :default: - No SSH access will be possible.

        :deprecated: - Use ``keyPair`` instead - https://docs.aws.amazon.com/cdk/api/v2/docs/aws-cdk-lib.aws_ec2-readme.html#using-an-existing-ec2-key-pair

        :stability: deprecated
        '''
        result = self._values.get("key_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def key_pair(self) -> typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IKeyPair]:
        '''The SSH keypair to grant access to the instance.

        Feature flag ``AUTOSCALING_GENERATE_LAUNCH_TEMPLATE`` must be enabled to use this property.

        ``launchTemplate`` and ``mixedInstancesPolicy`` must not be specified when this property is specified.

        You can either specify ``keyPair`` or ``keyName``, not both.

        :default: - No SSH access will be possible.
        '''
        result = self._values.get("key_pair")
        return typing.cast(typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IKeyPair], result)

    @builtins.property
    def max_capacity(self) -> typing.Optional[jsii.Number]:
        '''Maximum number of instances in the fleet.

        :default: desiredCapacity
        '''
        result = self._values.get("max_capacity")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def max_instance_lifetime(self) -> typing.Optional[_aws_cdk_ceddda9d.Duration]:
        '''The maximum amount of time that an instance can be in service.

        The maximum duration applies
        to all current and future instances in the group. As an instance approaches its maximum duration,
        it is terminated and replaced, and cannot be used again.

        You must specify a value of at least 86,400 seconds (one day). To clear a previously set value,
        leave this property undefined.

        :default: none

        :see: https://docs.aws.amazon.com/autoscaling/ec2/userguide/asg-max-instance-lifetime.html
        '''
        result = self._values.get("max_instance_lifetime")
        return typing.cast(typing.Optional[_aws_cdk_ceddda9d.Duration], result)

    @builtins.property
    def min_capacity(self) -> typing.Optional[jsii.Number]:
        '''Minimum number of instances in the fleet.

        :default: 1
        '''
        result = self._values.get("min_capacity")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def new_instances_protected_from_scale_in(self) -> typing.Optional[builtins.bool]:
        '''Whether newly-launched instances are protected from termination by Amazon EC2 Auto Scaling when scaling in.

        By default, Auto Scaling can terminate an instance at any time after launch
        when scaling in an Auto Scaling Group, subject to the group's termination
        policy. However, you may wish to protect newly-launched instances from
        being scaled in if they are going to run critical applications that should
        not be prematurely terminated.

        This flag must be enabled if the Auto Scaling Group will be associated with
        an ECS Capacity Provider with managed termination protection.

        :default: false
        '''
        result = self._values.get("new_instances_protected_from_scale_in")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def notifications(
        self,
    ) -> typing.Optional[typing.List[_aws_cdk_aws_autoscaling_ceddda9d.NotificationConfiguration]]:
        '''Configure autoscaling group to send notifications about fleet changes to an SNS topic(s).

        :default: - No fleet change notifications will be sent.

        :see: https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-as-group.html#cfn-as-group-notificationconfigurations
        '''
        result = self._values.get("notifications")
        return typing.cast(typing.Optional[typing.List[_aws_cdk_aws_autoscaling_ceddda9d.NotificationConfiguration]], result)

    @builtins.property
    def signals(self) -> typing.Optional[_aws_cdk_aws_autoscaling_ceddda9d.Signals]:
        '''Configure waiting for signals during deployment.

        Use this to pause the CloudFormation deployment to wait for the instances
        in the AutoScalingGroup to report successful startup during
        creation and updates. The UserData script needs to invoke ``cfn-signal``
        with a success or failure code after it is done setting up the instance.

        Without waiting for signals, the CloudFormation deployment will proceed as
        soon as the AutoScalingGroup has been created or updated but before the
        instances in the group have been started.

        For example, to have instances wait for an Elastic Load Balancing health check before
        they signal success, add a health-check verification by using the
        cfn-init helper script. For an example, see the verify_instance_health
        command in the Auto Scaling rolling updates sample template:

        https://github.com/awslabs/aws-cloudformation-templates/blob/master/aws/services/AutoScaling/AutoScalingRollingUpdates.yaml

        :default: - Do not wait for signals
        '''
        result = self._values.get("signals")
        return typing.cast(typing.Optional[_aws_cdk_aws_autoscaling_ceddda9d.Signals], result)

    @builtins.property
    def spot_price(self) -> typing.Optional[builtins.str]:
        '''The maximum hourly price (in USD) to be paid for any Spot Instance launched to fulfill the request.

        Spot Instances are
        launched when the price you specify exceeds the current Spot market price.

        ``launchTemplate`` and ``mixedInstancesPolicy`` must not be specified when this property is specified

        :default: none
        '''
        result = self._values.get("spot_price")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def ssm_session_permissions(self) -> typing.Optional[builtins.bool]:
        '''Add SSM session permissions to the instance role.

        Setting this to ``true`` adds the necessary permissions to connect
        to the instance using SSM Session Manager. You can do this
        from the AWS Console.

        NOTE: Setting this flag to ``true`` may not be enough by itself.
        You must also use an AMI that comes with the SSM Agent, or install
        the SSM Agent yourself. See
        `Working with SSM Agent <https://docs.aws.amazon.com/systems-manager/latest/userguide/ssm-agent.html>`_
        in the SSM Developer Guide.

        :default: false
        '''
        result = self._values.get("ssm_session_permissions")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def termination_policies(
        self,
    ) -> typing.Optional[typing.List[_aws_cdk_aws_autoscaling_ceddda9d.TerminationPolicy]]:
        '''A policy or a list of policies that are used to select the instances to terminate.

        The policies are executed in the order that you list them.

        :default: - ``TerminationPolicy.DEFAULT``

        :see: https://docs.aws.amazon.com/autoscaling/ec2/userguide/as-instance-termination.html
        '''
        result = self._values.get("termination_policies")
        return typing.cast(typing.Optional[typing.List[_aws_cdk_aws_autoscaling_ceddda9d.TerminationPolicy]], result)

    @builtins.property
    def termination_policy_custom_lambda_function_arn(
        self,
    ) -> typing.Optional[builtins.str]:
        '''A lambda function Arn that can be used as a custom termination policy to select the instances to terminate.

        This property must be specified if the TerminationPolicy.CUSTOM_LAMBDA_FUNCTION
        is used.

        :default: - No lambda function Arn will be supplied

        :see: https://docs.aws.amazon.com/autoscaling/ec2/userguide/lambda-custom-termination-policy.html
        '''
        result = self._values.get("termination_policy_custom_lambda_function_arn")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def update_policy(
        self,
    ) -> typing.Optional[_aws_cdk_aws_autoscaling_ceddda9d.UpdatePolicy]:
        '''What to do when an AutoScalingGroup's instance configuration is changed.

        This is applied when any of the settings on the ASG are changed that
        affect how the instances should be created (VPC, instance type, startup
        scripts, etc.). It indicates how the existing instances should be
        replaced with new instances matching the new config. By default, nothing
        is done and only new instances are launched with the new config.

        :default: - ``UpdatePolicy.rollingUpdate()`` if using ``init``, ``UpdatePolicy.none()`` otherwise
        '''
        result = self._values.get("update_policy")
        return typing.cast(typing.Optional[_aws_cdk_aws_autoscaling_ceddda9d.UpdatePolicy], result)

    @builtins.property
    def vpc_subnets(self) -> typing.Optional[_aws_cdk_aws_ec2_ceddda9d.SubnetSelection]:
        '''Where to place instances within the VPC.

        :default: - All Private subnets.
        '''
        result = self._values.get("vpc_subnets")
        return typing.cast(typing.Optional[_aws_cdk_aws_ec2_ceddda9d.SubnetSelection], result)

    @builtins.property
    def instance_type(self) -> _aws_cdk_aws_ec2_ceddda9d.InstanceType:
        '''(experimental) Instance type of the instances to start.

        :stability: experimental
        '''
        result = self._values.get("instance_type")
        assert result is not None, "Required property 'instance_type' is missing"
        return typing.cast(_aws_cdk_aws_ec2_ceddda9d.InstanceType, result)

    @builtins.property
    def bootstrap_enabled(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Configures the EC2 user-data script for instances in this autoscaling group to bootstrap the node (invoke ``/etc/eks/bootstrap.sh``) and associate it with the EKS cluster.

        If you wish to provide a custom user data script, set this to ``false`` and
        manually invoke ``autoscalingGroup.addUserData()``.

        :default: true

        :stability: experimental
        '''
        result = self._values.get("bootstrap_enabled")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def bootstrap_options(self) -> typing.Optional["BootstrapOptions"]:
        '''(experimental) EKS node bootstrapping options.

        :default: - none

        :stability: experimental
        '''
        result = self._values.get("bootstrap_options")
        return typing.cast(typing.Optional["BootstrapOptions"], result)

    @builtins.property
    def machine_image_type(self) -> typing.Optional["MachineImageType"]:
        '''(experimental) Machine image type.

        :default: MachineImageType.AMAZON_LINUX_2

        :stability: experimental
        '''
        result = self._values.get("machine_image_type")
        return typing.cast(typing.Optional["MachineImageType"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "AutoScalingGroupCapacityOptions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@aws-cdk/aws-eks-v2-alpha.AutoScalingGroupOptions",
    jsii_struct_bases=[],
    name_mapping={
        "bootstrap_enabled": "bootstrapEnabled",
        "bootstrap_options": "bootstrapOptions",
        "machine_image_type": "machineImageType",
    },
)
class AutoScalingGroupOptions:
    def __init__(
        self,
        *,
        bootstrap_enabled: typing.Optional[builtins.bool] = None,
        bootstrap_options: typing.Optional[typing.Union["BootstrapOptions", typing.Dict[builtins.str, typing.Any]]] = None,
        machine_image_type: typing.Optional["MachineImageType"] = None,
    ) -> None:
        '''(experimental) Options for adding an AutoScalingGroup as capacity.

        :param bootstrap_enabled: (experimental) Configures the EC2 user-data script for instances in this autoscaling group to bootstrap the node (invoke ``/etc/eks/bootstrap.sh``) and associate it with the EKS cluster. If you wish to provide a custom user data script, set this to ``false`` and manually invoke ``autoscalingGroup.addUserData()``. Default: true
        :param bootstrap_options: (experimental) Allows options for node bootstrapping through EC2 user data. Default: - default options
        :param machine_image_type: (experimental) Allow options to specify different machine image type. Default: MachineImageType.AMAZON_LINUX_2

        :stability: experimental
        :exampleMetadata: fixture=_generated

        Example::

            # The code below shows an example of how to instantiate this type.
            # The values are placeholders you should change.
            import aws_cdk.aws_eks_v2_alpha as eks_v2_alpha
            
            auto_scaling_group_options = eks_v2_alpha.AutoScalingGroupOptions(
                bootstrap_enabled=False,
                bootstrap_options=eks_v2_alpha.BootstrapOptions(
                    additional_args="additionalArgs",
                    aws_api_retry_attempts=123,
                    dns_cluster_ip="dnsClusterIp",
                    docker_config_json="dockerConfigJson",
                    enable_docker_bridge=False,
                    kubelet_extra_args="kubeletExtraArgs",
                    use_max_pods=False
                ),
                machine_image_type=eks_v2_alpha.MachineImageType.AMAZON_LINUX_2
            )
        '''
        if isinstance(bootstrap_options, dict):
            bootstrap_options = BootstrapOptions(**bootstrap_options)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__80c4d5f46701b7f97c3792dbf2230ae20b5bfabf12a3d73e5e01c6c755b4b3d9)
            check_type(argname="argument bootstrap_enabled", value=bootstrap_enabled, expected_type=type_hints["bootstrap_enabled"])
            check_type(argname="argument bootstrap_options", value=bootstrap_options, expected_type=type_hints["bootstrap_options"])
            check_type(argname="argument machine_image_type", value=machine_image_type, expected_type=type_hints["machine_image_type"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if bootstrap_enabled is not None:
            self._values["bootstrap_enabled"] = bootstrap_enabled
        if bootstrap_options is not None:
            self._values["bootstrap_options"] = bootstrap_options
        if machine_image_type is not None:
            self._values["machine_image_type"] = machine_image_type

    @builtins.property
    def bootstrap_enabled(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Configures the EC2 user-data script for instances in this autoscaling group to bootstrap the node (invoke ``/etc/eks/bootstrap.sh``) and associate it with the EKS cluster.

        If you wish to provide a custom user data script, set this to ``false`` and
        manually invoke ``autoscalingGroup.addUserData()``.

        :default: true

        :stability: experimental
        '''
        result = self._values.get("bootstrap_enabled")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def bootstrap_options(self) -> typing.Optional["BootstrapOptions"]:
        '''(experimental) Allows options for node bootstrapping through EC2 user data.

        :default: - default options

        :stability: experimental
        '''
        result = self._values.get("bootstrap_options")
        return typing.cast(typing.Optional["BootstrapOptions"], result)

    @builtins.property
    def machine_image_type(self) -> typing.Optional["MachineImageType"]:
        '''(experimental) Allow options to specify different machine image type.

        :default: MachineImageType.AMAZON_LINUX_2

        :stability: experimental
        '''
        result = self._values.get("machine_image_type")
        return typing.cast(typing.Optional["MachineImageType"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "AutoScalingGroupOptions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@aws-cdk/aws-eks-v2-alpha.BootstrapOptions",
    jsii_struct_bases=[],
    name_mapping={
        "additional_args": "additionalArgs",
        "aws_api_retry_attempts": "awsApiRetryAttempts",
        "dns_cluster_ip": "dnsClusterIp",
        "docker_config_json": "dockerConfigJson",
        "enable_docker_bridge": "enableDockerBridge",
        "kubelet_extra_args": "kubeletExtraArgs",
        "use_max_pods": "useMaxPods",
    },
)
class BootstrapOptions:
    def __init__(
        self,
        *,
        additional_args: typing.Optional[builtins.str] = None,
        aws_api_retry_attempts: typing.Optional[jsii.Number] = None,
        dns_cluster_ip: typing.Optional[builtins.str] = None,
        docker_config_json: typing.Optional[builtins.str] = None,
        enable_docker_bridge: typing.Optional[builtins.bool] = None,
        kubelet_extra_args: typing.Optional[builtins.str] = None,
        use_max_pods: typing.Optional[builtins.bool] = None,
    ) -> None:
        '''(experimental) EKS node bootstrapping options.

        :param additional_args: (experimental) Additional command line arguments to pass to the ``/etc/eks/bootstrap.sh`` command. Default: - none
        :param aws_api_retry_attempts: (experimental) Number of retry attempts for AWS API call (DescribeCluster). Default: 3
        :param dns_cluster_ip: (experimental) Overrides the IP address to use for DNS queries within the cluster. Default: - 10.100.0.10 or 172.20.0.10 based on the IP address of the primary interface.
        :param docker_config_json: (experimental) The contents of the ``/etc/docker/daemon.json`` file. Useful if you want a custom config differing from the default one in the EKS AMI. Default: - none
        :param enable_docker_bridge: (experimental) Restores the docker default bridge network. Default: false
        :param kubelet_extra_args: (experimental) Extra arguments to add to the kubelet. Useful for adding labels or taints. For example, ``--node-labels foo=bar,goo=far``. Default: - none
        :param use_max_pods: (experimental) Sets ``--max-pods`` for the kubelet based on the capacity of the EC2 instance. Default: true

        :stability: experimental
        :exampleMetadata: fixture=_generated

        Example::

            # The code below shows an example of how to instantiate this type.
            # The values are placeholders you should change.
            import aws_cdk.aws_eks_v2_alpha as eks_v2_alpha
            
            bootstrap_options = eks_v2_alpha.BootstrapOptions(
                additional_args="additionalArgs",
                aws_api_retry_attempts=123,
                dns_cluster_ip="dnsClusterIp",
                docker_config_json="dockerConfigJson",
                enable_docker_bridge=False,
                kubelet_extra_args="kubeletExtraArgs",
                use_max_pods=False
            )
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__93623b95a0480231b16717efee254b138fdefc282e67783dd4ac43cd0f30e33c)
            check_type(argname="argument additional_args", value=additional_args, expected_type=type_hints["additional_args"])
            check_type(argname="argument aws_api_retry_attempts", value=aws_api_retry_attempts, expected_type=type_hints["aws_api_retry_attempts"])
            check_type(argname="argument dns_cluster_ip", value=dns_cluster_ip, expected_type=type_hints["dns_cluster_ip"])
            check_type(argname="argument docker_config_json", value=docker_config_json, expected_type=type_hints["docker_config_json"])
            check_type(argname="argument enable_docker_bridge", value=enable_docker_bridge, expected_type=type_hints["enable_docker_bridge"])
            check_type(argname="argument kubelet_extra_args", value=kubelet_extra_args, expected_type=type_hints["kubelet_extra_args"])
            check_type(argname="argument use_max_pods", value=use_max_pods, expected_type=type_hints["use_max_pods"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if additional_args is not None:
            self._values["additional_args"] = additional_args
        if aws_api_retry_attempts is not None:
            self._values["aws_api_retry_attempts"] = aws_api_retry_attempts
        if dns_cluster_ip is not None:
            self._values["dns_cluster_ip"] = dns_cluster_ip
        if docker_config_json is not None:
            self._values["docker_config_json"] = docker_config_json
        if enable_docker_bridge is not None:
            self._values["enable_docker_bridge"] = enable_docker_bridge
        if kubelet_extra_args is not None:
            self._values["kubelet_extra_args"] = kubelet_extra_args
        if use_max_pods is not None:
            self._values["use_max_pods"] = use_max_pods

    @builtins.property
    def additional_args(self) -> typing.Optional[builtins.str]:
        '''(experimental) Additional command line arguments to pass to the ``/etc/eks/bootstrap.sh`` command.

        :default: - none

        :see: https://github.com/awslabs/amazon-eks-ami/blob/master/files/bootstrap.sh
        :stability: experimental
        '''
        result = self._values.get("additional_args")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def aws_api_retry_attempts(self) -> typing.Optional[jsii.Number]:
        '''(experimental) Number of retry attempts for AWS API call (DescribeCluster).

        :default: 3

        :stability: experimental
        '''
        result = self._values.get("aws_api_retry_attempts")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def dns_cluster_ip(self) -> typing.Optional[builtins.str]:
        '''(experimental) Overrides the IP address to use for DNS queries within the cluster.

        :default:

        - 10.100.0.10 or 172.20.0.10 based on the IP
        address of the primary interface.

        :stability: experimental
        '''
        result = self._values.get("dns_cluster_ip")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def docker_config_json(self) -> typing.Optional[builtins.str]:
        '''(experimental) The contents of the ``/etc/docker/daemon.json`` file. Useful if you want a custom config differing from the default one in the EKS AMI.

        :default: - none

        :stability: experimental
        '''
        result = self._values.get("docker_config_json")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def enable_docker_bridge(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Restores the docker default bridge network.

        :default: false

        :stability: experimental
        '''
        result = self._values.get("enable_docker_bridge")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def kubelet_extra_args(self) -> typing.Optional[builtins.str]:
        '''(experimental) Extra arguments to add to the kubelet. Useful for adding labels or taints.

        For example, ``--node-labels foo=bar,goo=far``.

        :default: - none

        :stability: experimental
        '''
        result = self._values.get("kubelet_extra_args")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def use_max_pods(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Sets ``--max-pods`` for the kubelet based on the capacity of the EC2 instance.

        :default: true

        :stability: experimental
        '''
        result = self._values.get("use_max_pods")
        return typing.cast(typing.Optional[builtins.bool], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "BootstrapOptions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.enum(jsii_type="@aws-cdk/aws-eks-v2-alpha.CapacityType")
class CapacityType(enum.Enum):
    '''(experimental) Capacity type of the managed node group.

    :stability: experimental
    '''

    SPOT = "SPOT"
    '''(experimental) spot instances.

    :stability: experimental
    '''
    ON_DEMAND = "ON_DEMAND"
    '''(experimental) on-demand instances.

    :stability: experimental
    '''
    CAPACITY_BLOCK = "CAPACITY_BLOCK"
    '''(experimental) capacity block instances.

    :stability: experimental
    '''


@jsii.data_type(
    jsii_type="@aws-cdk/aws-eks-v2-alpha.ClusterAttributes",
    jsii_struct_bases=[],
    name_mapping={
        "cluster_name": "clusterName",
        "cluster_certificate_authority_data": "clusterCertificateAuthorityData",
        "cluster_encryption_config_key_arn": "clusterEncryptionConfigKeyArn",
        "cluster_endpoint": "clusterEndpoint",
        "cluster_security_group_id": "clusterSecurityGroupId",
        "ip_family": "ipFamily",
        "kubectl_provider": "kubectlProvider",
        "kubectl_provider_options": "kubectlProviderOptions",
        "open_id_connect_provider": "openIdConnectProvider",
        "prune": "prune",
        "security_group_ids": "securityGroupIds",
        "vpc": "vpc",
    },
)
class ClusterAttributes:
    def __init__(
        self,
        *,
        cluster_name: builtins.str,
        cluster_certificate_authority_data: typing.Optional[builtins.str] = None,
        cluster_encryption_config_key_arn: typing.Optional[builtins.str] = None,
        cluster_endpoint: typing.Optional[builtins.str] = None,
        cluster_security_group_id: typing.Optional[builtins.str] = None,
        ip_family: typing.Optional["IpFamily"] = None,
        kubectl_provider: typing.Optional["IKubectlProvider"] = None,
        kubectl_provider_options: typing.Optional[typing.Union["KubectlProviderOptions", typing.Dict[builtins.str, typing.Any]]] = None,
        open_id_connect_provider: typing.Optional[_aws_cdk_aws_iam_ceddda9d.IOpenIdConnectProvider] = None,
        prune: typing.Optional[builtins.bool] = None,
        security_group_ids: typing.Optional[typing.Sequence[builtins.str]] = None,
        vpc: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IVpc] = None,
    ) -> None:
        '''(experimental) Attributes for EKS clusters.

        :param cluster_name: (experimental) The physical name of the Cluster.
        :param cluster_certificate_authority_data: (experimental) The certificate-authority-data for your cluster. Default: - if not specified ``cluster.clusterCertificateAuthorityData`` will throw an error
        :param cluster_encryption_config_key_arn: (experimental) Amazon Resource Name (ARN) or alias of the customer master key (CMK). Default: - if not specified ``cluster.clusterEncryptionConfigKeyArn`` will throw an error
        :param cluster_endpoint: (experimental) The API Server endpoint URL. Default: - if not specified ``cluster.clusterEndpoint`` will throw an error.
        :param cluster_security_group_id: (experimental) The cluster security group that was created by Amazon EKS for the cluster. Default: - if not specified ``cluster.clusterSecurityGroupId`` will throw an error
        :param ip_family: (experimental) Specify which IP family is used to assign Kubernetes pod and service IP addresses. Default: - IpFamily.IP_V4
        :param kubectl_provider: (experimental) KubectlProvider for issuing kubectl commands. Default: - Default CDK provider
        :param kubectl_provider_options: (experimental) Options for creating the kubectl provider - a lambda function that executes ``kubectl`` and ``helm`` against the cluster. If defined, ``kubectlLayer`` is a required property. If not defined, kubectl provider will not be created by default.
        :param open_id_connect_provider: (experimental) An Open ID Connect provider for this cluster that can be used to configure service accounts. You can either import an existing provider using ``iam.OpenIdConnectProvider.fromProviderArn``, or create a new provider using ``new eks.OpenIdConnectProvider`` Default: - if not specified ``cluster.openIdConnectProvider`` and ``cluster.addServiceAccount`` will throw an error.
        :param prune: (experimental) Indicates whether Kubernetes resources added through ``addManifest()`` can be automatically pruned. When this is enabled (default), prune labels will be allocated and injected to each resource. These labels will then be used when issuing the ``kubectl apply`` operation with the ``--prune`` switch. Default: true
        :param security_group_ids: (experimental) Additional security groups associated with this cluster. Default: - if not specified, no additional security groups will be considered in ``cluster.connections``.
        :param vpc: (experimental) The VPC in which this Cluster was created. Default: - if not specified ``cluster.vpc`` will throw an error

        :stability: experimental
        :exampleMetadata: infused

        Example::

            handler_role = iam.Role.from_role_arn(self, "HandlerRole", "arn:aws:iam::123456789012:role/lambda-role")
            # get the serivceToken from the custom resource provider
            function_arn = lambda_.Function.from_function_name(self, "ProviderOnEventFunc", "ProviderframeworkonEvent-XXX").function_arn
            kubectl_provider = eks.KubectlProvider.from_kubectl_provider_attributes(self, "KubectlProvider",
                service_token=function_arn,
                role=handler_role
            )
            
            cluster = eks.Cluster.from_cluster_attributes(self, "Cluster",
                cluster_name="cluster",
                kubectl_provider=kubectl_provider
            )
        '''
        if isinstance(kubectl_provider_options, dict):
            kubectl_provider_options = KubectlProviderOptions(**kubectl_provider_options)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__000c78cc58b69c9c1f9d75052e6a7ba89be1dd825fcc3b2701bdc2609e77c79a)
            check_type(argname="argument cluster_name", value=cluster_name, expected_type=type_hints["cluster_name"])
            check_type(argname="argument cluster_certificate_authority_data", value=cluster_certificate_authority_data, expected_type=type_hints["cluster_certificate_authority_data"])
            check_type(argname="argument cluster_encryption_config_key_arn", value=cluster_encryption_config_key_arn, expected_type=type_hints["cluster_encryption_config_key_arn"])
            check_type(argname="argument cluster_endpoint", value=cluster_endpoint, expected_type=type_hints["cluster_endpoint"])
            check_type(argname="argument cluster_security_group_id", value=cluster_security_group_id, expected_type=type_hints["cluster_security_group_id"])
            check_type(argname="argument ip_family", value=ip_family, expected_type=type_hints["ip_family"])
            check_type(argname="argument kubectl_provider", value=kubectl_provider, expected_type=type_hints["kubectl_provider"])
            check_type(argname="argument kubectl_provider_options", value=kubectl_provider_options, expected_type=type_hints["kubectl_provider_options"])
            check_type(argname="argument open_id_connect_provider", value=open_id_connect_provider, expected_type=type_hints["open_id_connect_provider"])
            check_type(argname="argument prune", value=prune, expected_type=type_hints["prune"])
            check_type(argname="argument security_group_ids", value=security_group_ids, expected_type=type_hints["security_group_ids"])
            check_type(argname="argument vpc", value=vpc, expected_type=type_hints["vpc"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "cluster_name": cluster_name,
        }
        if cluster_certificate_authority_data is not None:
            self._values["cluster_certificate_authority_data"] = cluster_certificate_authority_data
        if cluster_encryption_config_key_arn is not None:
            self._values["cluster_encryption_config_key_arn"] = cluster_encryption_config_key_arn
        if cluster_endpoint is not None:
            self._values["cluster_endpoint"] = cluster_endpoint
        if cluster_security_group_id is not None:
            self._values["cluster_security_group_id"] = cluster_security_group_id
        if ip_family is not None:
            self._values["ip_family"] = ip_family
        if kubectl_provider is not None:
            self._values["kubectl_provider"] = kubectl_provider
        if kubectl_provider_options is not None:
            self._values["kubectl_provider_options"] = kubectl_provider_options
        if open_id_connect_provider is not None:
            self._values["open_id_connect_provider"] = open_id_connect_provider
        if prune is not None:
            self._values["prune"] = prune
        if security_group_ids is not None:
            self._values["security_group_ids"] = security_group_ids
        if vpc is not None:
            self._values["vpc"] = vpc

    @builtins.property
    def cluster_name(self) -> builtins.str:
        '''(experimental) The physical name of the Cluster.

        :stability: experimental
        '''
        result = self._values.get("cluster_name")
        assert result is not None, "Required property 'cluster_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def cluster_certificate_authority_data(self) -> typing.Optional[builtins.str]:
        '''(experimental) The certificate-authority-data for your cluster.

        :default:

        - if not specified ``cluster.clusterCertificateAuthorityData`` will
        throw an error

        :stability: experimental
        '''
        result = self._values.get("cluster_certificate_authority_data")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def cluster_encryption_config_key_arn(self) -> typing.Optional[builtins.str]:
        '''(experimental) Amazon Resource Name (ARN) or alias of the customer master key (CMK).

        :default:

        - if not specified ``cluster.clusterEncryptionConfigKeyArn`` will
        throw an error

        :stability: experimental
        '''
        result = self._values.get("cluster_encryption_config_key_arn")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def cluster_endpoint(self) -> typing.Optional[builtins.str]:
        '''(experimental) The API Server endpoint URL.

        :default: - if not specified ``cluster.clusterEndpoint`` will throw an error.

        :stability: experimental
        '''
        result = self._values.get("cluster_endpoint")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def cluster_security_group_id(self) -> typing.Optional[builtins.str]:
        '''(experimental) The cluster security group that was created by Amazon EKS for the cluster.

        :default:

        - if not specified ``cluster.clusterSecurityGroupId`` will throw an
        error

        :stability: experimental
        '''
        result = self._values.get("cluster_security_group_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def ip_family(self) -> typing.Optional["IpFamily"]:
        '''(experimental) Specify which IP family is used to assign Kubernetes pod and service IP addresses.

        :default: - IpFamily.IP_V4

        :see: https://docs.aws.amazon.com/eks/latest/APIReference/API_KubernetesNetworkConfigRequest.html#AmazonEKS-Type-KubernetesNetworkConfigRequest-ipFamily
        :stability: experimental
        '''
        result = self._values.get("ip_family")
        return typing.cast(typing.Optional["IpFamily"], result)

    @builtins.property
    def kubectl_provider(self) -> typing.Optional["IKubectlProvider"]:
        '''(experimental) KubectlProvider for issuing kubectl commands.

        :default: - Default CDK provider

        :stability: experimental
        '''
        result = self._values.get("kubectl_provider")
        return typing.cast(typing.Optional["IKubectlProvider"], result)

    @builtins.property
    def kubectl_provider_options(self) -> typing.Optional["KubectlProviderOptions"]:
        '''(experimental) Options for creating the kubectl provider - a lambda function that executes ``kubectl`` and ``helm`` against the cluster.

        If defined, ``kubectlLayer`` is a required property.

        If not defined, kubectl provider will not be created by default.

        :stability: experimental
        '''
        result = self._values.get("kubectl_provider_options")
        return typing.cast(typing.Optional["KubectlProviderOptions"], result)

    @builtins.property
    def open_id_connect_provider(
        self,
    ) -> typing.Optional[_aws_cdk_aws_iam_ceddda9d.IOpenIdConnectProvider]:
        '''(experimental) An Open ID Connect provider for this cluster that can be used to configure service accounts.

        You can either import an existing provider using ``iam.OpenIdConnectProvider.fromProviderArn``,
        or create a new provider using ``new eks.OpenIdConnectProvider``

        :default: - if not specified ``cluster.openIdConnectProvider`` and ``cluster.addServiceAccount`` will throw an error.

        :stability: experimental
        '''
        result = self._values.get("open_id_connect_provider")
        return typing.cast(typing.Optional[_aws_cdk_aws_iam_ceddda9d.IOpenIdConnectProvider], result)

    @builtins.property
    def prune(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Indicates whether Kubernetes resources added through ``addManifest()`` can be automatically pruned.

        When this is enabled (default), prune labels will be
        allocated and injected to each resource. These labels will then be used
        when issuing the ``kubectl apply`` operation with the ``--prune`` switch.

        :default: true

        :stability: experimental
        '''
        result = self._values.get("prune")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def security_group_ids(self) -> typing.Optional[typing.List[builtins.str]]:
        '''(experimental) Additional security groups associated with this cluster.

        :default:

        - if not specified, no additional security groups will be
        considered in ``cluster.connections``.

        :stability: experimental
        '''
        result = self._values.get("security_group_ids")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def vpc(self) -> typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IVpc]:
        '''(experimental) The VPC in which this Cluster was created.

        :default: - if not specified ``cluster.vpc`` will throw an error

        :stability: experimental
        '''
        result = self._values.get("vpc")
        return typing.cast(typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IVpc], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ClusterAttributes(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@aws-cdk/aws-eks-v2-alpha.ClusterCommonOptions",
    jsii_struct_bases=[],
    name_mapping={
        "version": "version",
        "alb_controller": "albController",
        "cluster_logging": "clusterLogging",
        "cluster_name": "clusterName",
        "core_dns_compute_type": "coreDnsComputeType",
        "endpoint_access": "endpointAccess",
        "ip_family": "ipFamily",
        "kubectl_provider_options": "kubectlProviderOptions",
        "masters_role": "mastersRole",
        "prune": "prune",
        "role": "role",
        "secrets_encryption_key": "secretsEncryptionKey",
        "security_group": "securityGroup",
        "service_ipv4_cidr": "serviceIpv4Cidr",
        "tags": "tags",
        "vpc": "vpc",
        "vpc_subnets": "vpcSubnets",
    },
)
class ClusterCommonOptions:
    def __init__(
        self,
        *,
        version: "KubernetesVersion",
        alb_controller: typing.Optional[typing.Union[AlbControllerOptions, typing.Dict[builtins.str, typing.Any]]] = None,
        cluster_logging: typing.Optional[typing.Sequence["ClusterLoggingTypes"]] = None,
        cluster_name: typing.Optional[builtins.str] = None,
        core_dns_compute_type: typing.Optional["CoreDnsComputeType"] = None,
        endpoint_access: typing.Optional["EndpointAccess"] = None,
        ip_family: typing.Optional["IpFamily"] = None,
        kubectl_provider_options: typing.Optional[typing.Union["KubectlProviderOptions", typing.Dict[builtins.str, typing.Any]]] = None,
        masters_role: typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole] = None,
        prune: typing.Optional[builtins.bool] = None,
        role: typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole] = None,
        secrets_encryption_key: typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey] = None,
        security_group: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup] = None,
        service_ipv4_cidr: typing.Optional[builtins.str] = None,
        tags: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        vpc: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IVpc] = None,
        vpc_subnets: typing.Optional[typing.Sequence[typing.Union[_aws_cdk_aws_ec2_ceddda9d.SubnetSelection, typing.Dict[builtins.str, typing.Any]]]] = None,
    ) -> None:
        '''(experimental) Options for configuring an EKS cluster.

        :param version: (experimental) The Kubernetes version to run in the cluster.
        :param alb_controller: (experimental) Install the AWS Load Balancer Controller onto the cluster. Default: - The controller is not installed.
        :param cluster_logging: (experimental) The cluster log types which you want to enable. Default: - none
        :param cluster_name: (experimental) Name for the cluster. Default: - Automatically generated name
        :param core_dns_compute_type: (experimental) Controls the "eks.amazonaws.com/compute-type" annotation in the CoreDNS configuration on your cluster to determine which compute type to use for CoreDNS. Default: CoreDnsComputeType.EC2 (for ``FargateCluster`` the default is FARGATE)
        :param endpoint_access: (experimental) Configure access to the Kubernetes API server endpoint.. Default: EndpointAccess.PUBLIC_AND_PRIVATE
        :param ip_family: (experimental) Specify which IP family is used to assign Kubernetes pod and service IP addresses. Default: - IpFamily.IP_V4
        :param kubectl_provider_options: (experimental) Options for creating the kubectl provider - a lambda function that executes ``kubectl`` and ``helm`` against the cluster. If defined, ``kubectlLayer`` is a required property. If not defined, kubectl provider will not be created by default.
        :param masters_role: (experimental) An IAM role that will be added to the ``system:masters`` Kubernetes RBAC group. Default: - no masters role.
        :param prune: (experimental) Indicates whether Kubernetes resources added through ``addManifest()`` can be automatically pruned. When this is enabled (default), prune labels will be allocated and injected to each resource. These labels will then be used when issuing the ``kubectl apply`` operation with the ``--prune`` switch. Default: true
        :param role: (experimental) Role that provides permissions for the Kubernetes control plane to make calls to AWS API operations on your behalf. Default: - A role is automatically created for you
        :param secrets_encryption_key: (experimental) KMS secret for envelope encryption for Kubernetes secrets. Default: - By default, Kubernetes stores all secret object data within etcd and all etcd volumes used by Amazon EKS are encrypted at the disk-level using AWS-Managed encryption keys.
        :param security_group: (experimental) Security Group to use for Control Plane ENIs. Default: - A security group is automatically created
        :param service_ipv4_cidr: (experimental) The CIDR block to assign Kubernetes service IP addresses from. Default: - Kubernetes assigns addresses from either the 10.100.0.0/16 or 172.20.0.0/16 CIDR blocks
        :param tags: (experimental) The tags assigned to the EKS cluster. Default: - none
        :param vpc: (experimental) The VPC in which to create the Cluster. Default: - a VPC with default configuration will be created and can be accessed through ``cluster.vpc``.
        :param vpc_subnets: (experimental) Where to place EKS Control Plane ENIs. For example, to only select private subnets, supply the following: ``vpcSubnets: [{ subnetType: ec2.SubnetType.PRIVATE_WITH_EGRESS }]`` Default: - All public and private subnets

        :stability: experimental
        :exampleMetadata: fixture=_generated

        Example::

            # The code below shows an example of how to instantiate this type.
            # The values are placeholders you should change.
            import aws_cdk.aws_eks_v2_alpha as eks_v2_alpha
            import aws_cdk as cdk
            from aws_cdk import aws_ec2 as ec2
            from aws_cdk import aws_iam as iam
            from aws_cdk import aws_kms as kms
            from aws_cdk import aws_lambda as lambda_
            
            # alb_controller_version: eks_v2_alpha.AlbControllerVersion
            # endpoint_access: eks_v2_alpha.EndpointAccess
            # key: kms.Key
            # kubernetes_version: eks_v2_alpha.KubernetesVersion
            # layer_version: lambda.LayerVersion
            # policy: Any
            # role: iam.Role
            # security_group: ec2.SecurityGroup
            # size: cdk.Size
            # subnet: ec2.Subnet
            # subnet_filter: ec2.SubnetFilter
            # vpc: ec2.Vpc
            
            cluster_common_options = eks_v2_alpha.ClusterCommonOptions(
                version=kubernetes_version,
            
                # the properties below are optional
                alb_controller=eks_v2_alpha.AlbControllerOptions(
                    version=alb_controller_version,
            
                    # the properties below are optional
                    policy=policy,
                    repository="repository"
                ),
                cluster_logging=[eks_v2_alpha.ClusterLoggingTypes.API],
                cluster_name="clusterName",
                core_dns_compute_type=eks_v2_alpha.CoreDnsComputeType.EC2,
                endpoint_access=endpoint_access,
                ip_family=eks_v2_alpha.IpFamily.IP_V4,
                kubectl_provider_options=eks_v2_alpha.KubectlProviderOptions(
                    kubectl_layer=layer_version,
            
                    # the properties below are optional
                    awscli_layer=layer_version,
                    environment={
                        "environment_key": "environment"
                    },
                    memory=size,
                    private_subnets=[subnet],
                    role=role,
                    security_group=security_group
                ),
                masters_role=role,
                prune=False,
                role=role,
                secrets_encryption_key=key,
                security_group=security_group,
                service_ipv4_cidr="serviceIpv4Cidr",
                tags={
                    "tags_key": "tags"
                },
                vpc=vpc,
                vpc_subnets=[ec2.SubnetSelection(
                    availability_zones=["availabilityZones"],
                    one_per_az=False,
                    subnet_filters=[subnet_filter],
                    subnet_group_name="subnetGroupName",
                    subnets=[subnet],
                    subnet_type=ec2.SubnetType.PRIVATE_ISOLATED
                )]
            )
        '''
        if isinstance(alb_controller, dict):
            alb_controller = AlbControllerOptions(**alb_controller)
        if isinstance(kubectl_provider_options, dict):
            kubectl_provider_options = KubectlProviderOptions(**kubectl_provider_options)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__522396bf3ea38086bd92ddd50181dc1757140cccc27f7d0415c200a262a260a5)
            check_type(argname="argument version", value=version, expected_type=type_hints["version"])
            check_type(argname="argument alb_controller", value=alb_controller, expected_type=type_hints["alb_controller"])
            check_type(argname="argument cluster_logging", value=cluster_logging, expected_type=type_hints["cluster_logging"])
            check_type(argname="argument cluster_name", value=cluster_name, expected_type=type_hints["cluster_name"])
            check_type(argname="argument core_dns_compute_type", value=core_dns_compute_type, expected_type=type_hints["core_dns_compute_type"])
            check_type(argname="argument endpoint_access", value=endpoint_access, expected_type=type_hints["endpoint_access"])
            check_type(argname="argument ip_family", value=ip_family, expected_type=type_hints["ip_family"])
            check_type(argname="argument kubectl_provider_options", value=kubectl_provider_options, expected_type=type_hints["kubectl_provider_options"])
            check_type(argname="argument masters_role", value=masters_role, expected_type=type_hints["masters_role"])
            check_type(argname="argument prune", value=prune, expected_type=type_hints["prune"])
            check_type(argname="argument role", value=role, expected_type=type_hints["role"])
            check_type(argname="argument secrets_encryption_key", value=secrets_encryption_key, expected_type=type_hints["secrets_encryption_key"])
            check_type(argname="argument security_group", value=security_group, expected_type=type_hints["security_group"])
            check_type(argname="argument service_ipv4_cidr", value=service_ipv4_cidr, expected_type=type_hints["service_ipv4_cidr"])
            check_type(argname="argument tags", value=tags, expected_type=type_hints["tags"])
            check_type(argname="argument vpc", value=vpc, expected_type=type_hints["vpc"])
            check_type(argname="argument vpc_subnets", value=vpc_subnets, expected_type=type_hints["vpc_subnets"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "version": version,
        }
        if alb_controller is not None:
            self._values["alb_controller"] = alb_controller
        if cluster_logging is not None:
            self._values["cluster_logging"] = cluster_logging
        if cluster_name is not None:
            self._values["cluster_name"] = cluster_name
        if core_dns_compute_type is not None:
            self._values["core_dns_compute_type"] = core_dns_compute_type
        if endpoint_access is not None:
            self._values["endpoint_access"] = endpoint_access
        if ip_family is not None:
            self._values["ip_family"] = ip_family
        if kubectl_provider_options is not None:
            self._values["kubectl_provider_options"] = kubectl_provider_options
        if masters_role is not None:
            self._values["masters_role"] = masters_role
        if prune is not None:
            self._values["prune"] = prune
        if role is not None:
            self._values["role"] = role
        if secrets_encryption_key is not None:
            self._values["secrets_encryption_key"] = secrets_encryption_key
        if security_group is not None:
            self._values["security_group"] = security_group
        if service_ipv4_cidr is not None:
            self._values["service_ipv4_cidr"] = service_ipv4_cidr
        if tags is not None:
            self._values["tags"] = tags
        if vpc is not None:
            self._values["vpc"] = vpc
        if vpc_subnets is not None:
            self._values["vpc_subnets"] = vpc_subnets

    @builtins.property
    def version(self) -> "KubernetesVersion":
        '''(experimental) The Kubernetes version to run in the cluster.

        :stability: experimental
        '''
        result = self._values.get("version")
        assert result is not None, "Required property 'version' is missing"
        return typing.cast("KubernetesVersion", result)

    @builtins.property
    def alb_controller(self) -> typing.Optional[AlbControllerOptions]:
        '''(experimental) Install the AWS Load Balancer Controller onto the cluster.

        :default: - The controller is not installed.

        :see: https://kubernetes-sigs.github.io/aws-load-balancer-controller
        :stability: experimental
        '''
        result = self._values.get("alb_controller")
        return typing.cast(typing.Optional[AlbControllerOptions], result)

    @builtins.property
    def cluster_logging(self) -> typing.Optional[typing.List["ClusterLoggingTypes"]]:
        '''(experimental) The cluster log types which you want to enable.

        :default: - none

        :stability: experimental
        '''
        result = self._values.get("cluster_logging")
        return typing.cast(typing.Optional[typing.List["ClusterLoggingTypes"]], result)

    @builtins.property
    def cluster_name(self) -> typing.Optional[builtins.str]:
        '''(experimental) Name for the cluster.

        :default: - Automatically generated name

        :stability: experimental
        '''
        result = self._values.get("cluster_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def core_dns_compute_type(self) -> typing.Optional["CoreDnsComputeType"]:
        '''(experimental) Controls the "eks.amazonaws.com/compute-type" annotation in the CoreDNS configuration on your cluster to determine which compute type to use for CoreDNS.

        :default: CoreDnsComputeType.EC2 (for ``FargateCluster`` the default is FARGATE)

        :stability: experimental
        '''
        result = self._values.get("core_dns_compute_type")
        return typing.cast(typing.Optional["CoreDnsComputeType"], result)

    @builtins.property
    def endpoint_access(self) -> typing.Optional["EndpointAccess"]:
        '''(experimental) Configure access to the Kubernetes API server endpoint..

        :default: EndpointAccess.PUBLIC_AND_PRIVATE

        :see: https://docs.aws.amazon.com/eks/latest/userguide/cluster-endpoint.html
        :stability: experimental
        '''
        result = self._values.get("endpoint_access")
        return typing.cast(typing.Optional["EndpointAccess"], result)

    @builtins.property
    def ip_family(self) -> typing.Optional["IpFamily"]:
        '''(experimental) Specify which IP family is used to assign Kubernetes pod and service IP addresses.

        :default: - IpFamily.IP_V4

        :see: https://docs.aws.amazon.com/eks/latest/APIReference/API_KubernetesNetworkConfigRequest.html#AmazonEKS-Type-KubernetesNetworkConfigRequest-ipFamily
        :stability: experimental
        '''
        result = self._values.get("ip_family")
        return typing.cast(typing.Optional["IpFamily"], result)

    @builtins.property
    def kubectl_provider_options(self) -> typing.Optional["KubectlProviderOptions"]:
        '''(experimental) Options for creating the kubectl provider - a lambda function that executes ``kubectl`` and ``helm`` against the cluster.

        If defined, ``kubectlLayer`` is a required property.

        If not defined, kubectl provider will not be created by default.

        :stability: experimental
        '''
        result = self._values.get("kubectl_provider_options")
        return typing.cast(typing.Optional["KubectlProviderOptions"], result)

    @builtins.property
    def masters_role(self) -> typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole]:
        '''(experimental) An IAM role that will be added to the ``system:masters`` Kubernetes RBAC group.

        :default: - no masters role.

        :see: https://kubernetes.io/docs/reference/access-authn-authz/rbac/#default-roles-and-role-bindings
        :stability: experimental
        '''
        result = self._values.get("masters_role")
        return typing.cast(typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole], result)

    @builtins.property
    def prune(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Indicates whether Kubernetes resources added through ``addManifest()`` can be automatically pruned.

        When this is enabled (default), prune labels will be
        allocated and injected to each resource. These labels will then be used
        when issuing the ``kubectl apply`` operation with the ``--prune`` switch.

        :default: true

        :stability: experimental
        '''
        result = self._values.get("prune")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def role(self) -> typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole]:
        '''(experimental) Role that provides permissions for the Kubernetes control plane to make calls to AWS API operations on your behalf.

        :default: - A role is automatically created for you

        :stability: experimental
        '''
        result = self._values.get("role")
        return typing.cast(typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole], result)

    @builtins.property
    def secrets_encryption_key(self) -> typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey]:
        '''(experimental) KMS secret for envelope encryption for Kubernetes secrets.

        :default:

        - By default, Kubernetes stores all secret object data within etcd and
        all etcd volumes used by Amazon EKS are encrypted at the disk-level
        using AWS-Managed encryption keys.

        :stability: experimental
        '''
        result = self._values.get("secrets_encryption_key")
        return typing.cast(typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey], result)

    @builtins.property
    def security_group(
        self,
    ) -> typing.Optional[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup]:
        '''(experimental) Security Group to use for Control Plane ENIs.

        :default: - A security group is automatically created

        :stability: experimental
        '''
        result = self._values.get("security_group")
        return typing.cast(typing.Optional[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup], result)

    @builtins.property
    def service_ipv4_cidr(self) -> typing.Optional[builtins.str]:
        '''(experimental) The CIDR block to assign Kubernetes service IP addresses from.

        :default:

        - Kubernetes assigns addresses from either the
        10.100.0.0/16 or 172.20.0.0/16 CIDR blocks

        :see: https://docs.aws.amazon.com/eks/latest/APIReference/API_KubernetesNetworkConfigRequest.html#AmazonEKS-Type-KubernetesNetworkConfigRequest-serviceIpv4Cidr
        :stability: experimental
        '''
        result = self._values.get("service_ipv4_cidr")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def tags(self) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        '''(experimental) The tags assigned to the EKS cluster.

        :default: - none

        :stability: experimental
        '''
        result = self._values.get("tags")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], result)

    @builtins.property
    def vpc(self) -> typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IVpc]:
        '''(experimental) The VPC in which to create the Cluster.

        :default: - a VPC with default configuration will be created and can be accessed through ``cluster.vpc``.

        :stability: experimental
        '''
        result = self._values.get("vpc")
        return typing.cast(typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IVpc], result)

    @builtins.property
    def vpc_subnets(
        self,
    ) -> typing.Optional[typing.List[_aws_cdk_aws_ec2_ceddda9d.SubnetSelection]]:
        '''(experimental) Where to place EKS Control Plane ENIs.

        For example, to only select private subnets, supply the following:

        ``vpcSubnets: [{ subnetType: ec2.SubnetType.PRIVATE_WITH_EGRESS }]``

        :default: - All public and private subnets

        :stability: experimental
        '''
        result = self._values.get("vpc_subnets")
        return typing.cast(typing.Optional[typing.List[_aws_cdk_aws_ec2_ceddda9d.SubnetSelection]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ClusterCommonOptions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.enum(jsii_type="@aws-cdk/aws-eks-v2-alpha.ClusterLoggingTypes")
class ClusterLoggingTypes(enum.Enum):
    '''(experimental) EKS cluster logging types.

    :stability: experimental
    :exampleMetadata: infused

    Example::

        cluster = eks.Cluster(self, "Cluster",
            # ...
            version=eks.KubernetesVersion.V1_33,
            cluster_logging=[eks.ClusterLoggingTypes.API, eks.ClusterLoggingTypes.AUTHENTICATOR, eks.ClusterLoggingTypes.SCHEDULER
            ]
        )
    '''

    API = "API"
    '''(experimental) Logs pertaining to API requests to the cluster.

    :stability: experimental
    '''
    AUDIT = "AUDIT"
    '''(experimental) Logs pertaining to cluster access via the Kubernetes API.

    :stability: experimental
    '''
    AUTHENTICATOR = "AUTHENTICATOR"
    '''(experimental) Logs pertaining to authentication requests into the cluster.

    :stability: experimental
    '''
    CONTROLLER_MANAGER = "CONTROLLER_MANAGER"
    '''(experimental) Logs pertaining to state of cluster controllers.

    :stability: experimental
    '''
    SCHEDULER = "SCHEDULER"
    '''(experimental) Logs pertaining to scheduling decisions.

    :stability: experimental
    '''


@jsii.data_type(
    jsii_type="@aws-cdk/aws-eks-v2-alpha.ClusterProps",
    jsii_struct_bases=[ClusterCommonOptions],
    name_mapping={
        "version": "version",
        "alb_controller": "albController",
        "cluster_logging": "clusterLogging",
        "cluster_name": "clusterName",
        "core_dns_compute_type": "coreDnsComputeType",
        "endpoint_access": "endpointAccess",
        "ip_family": "ipFamily",
        "kubectl_provider_options": "kubectlProviderOptions",
        "masters_role": "mastersRole",
        "prune": "prune",
        "role": "role",
        "secrets_encryption_key": "secretsEncryptionKey",
        "security_group": "securityGroup",
        "service_ipv4_cidr": "serviceIpv4Cidr",
        "tags": "tags",
        "vpc": "vpc",
        "vpc_subnets": "vpcSubnets",
        "bootstrap_cluster_creator_admin_permissions": "bootstrapClusterCreatorAdminPermissions",
        "compute": "compute",
        "default_capacity": "defaultCapacity",
        "default_capacity_instance": "defaultCapacityInstance",
        "default_capacity_type": "defaultCapacityType",
        "output_config_command": "outputConfigCommand",
    },
)
class ClusterProps(ClusterCommonOptions):
    def __init__(
        self,
        *,
        version: "KubernetesVersion",
        alb_controller: typing.Optional[typing.Union[AlbControllerOptions, typing.Dict[builtins.str, typing.Any]]] = None,
        cluster_logging: typing.Optional[typing.Sequence[ClusterLoggingTypes]] = None,
        cluster_name: typing.Optional[builtins.str] = None,
        core_dns_compute_type: typing.Optional["CoreDnsComputeType"] = None,
        endpoint_access: typing.Optional["EndpointAccess"] = None,
        ip_family: typing.Optional["IpFamily"] = None,
        kubectl_provider_options: typing.Optional[typing.Union["KubectlProviderOptions", typing.Dict[builtins.str, typing.Any]]] = None,
        masters_role: typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole] = None,
        prune: typing.Optional[builtins.bool] = None,
        role: typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole] = None,
        secrets_encryption_key: typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey] = None,
        security_group: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup] = None,
        service_ipv4_cidr: typing.Optional[builtins.str] = None,
        tags: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        vpc: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IVpc] = None,
        vpc_subnets: typing.Optional[typing.Sequence[typing.Union[_aws_cdk_aws_ec2_ceddda9d.SubnetSelection, typing.Dict[builtins.str, typing.Any]]]] = None,
        bootstrap_cluster_creator_admin_permissions: typing.Optional[builtins.bool] = None,
        compute: typing.Optional[typing.Union["ComputeConfig", typing.Dict[builtins.str, typing.Any]]] = None,
        default_capacity: typing.Optional[jsii.Number] = None,
        default_capacity_instance: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.InstanceType] = None,
        default_capacity_type: typing.Optional["DefaultCapacityType"] = None,
        output_config_command: typing.Optional[builtins.bool] = None,
    ) -> None:
        '''(experimental) Properties for configuring a standard EKS cluster (non-Fargate).

        :param version: (experimental) The Kubernetes version to run in the cluster.
        :param alb_controller: (experimental) Install the AWS Load Balancer Controller onto the cluster. Default: - The controller is not installed.
        :param cluster_logging: (experimental) The cluster log types which you want to enable. Default: - none
        :param cluster_name: (experimental) Name for the cluster. Default: - Automatically generated name
        :param core_dns_compute_type: (experimental) Controls the "eks.amazonaws.com/compute-type" annotation in the CoreDNS configuration on your cluster to determine which compute type to use for CoreDNS. Default: CoreDnsComputeType.EC2 (for ``FargateCluster`` the default is FARGATE)
        :param endpoint_access: (experimental) Configure access to the Kubernetes API server endpoint.. Default: EndpointAccess.PUBLIC_AND_PRIVATE
        :param ip_family: (experimental) Specify which IP family is used to assign Kubernetes pod and service IP addresses. Default: - IpFamily.IP_V4
        :param kubectl_provider_options: (experimental) Options for creating the kubectl provider - a lambda function that executes ``kubectl`` and ``helm`` against the cluster. If defined, ``kubectlLayer`` is a required property. If not defined, kubectl provider will not be created by default.
        :param masters_role: (experimental) An IAM role that will be added to the ``system:masters`` Kubernetes RBAC group. Default: - no masters role.
        :param prune: (experimental) Indicates whether Kubernetes resources added through ``addManifest()`` can be automatically pruned. When this is enabled (default), prune labels will be allocated and injected to each resource. These labels will then be used when issuing the ``kubectl apply`` operation with the ``--prune`` switch. Default: true
        :param role: (experimental) Role that provides permissions for the Kubernetes control plane to make calls to AWS API operations on your behalf. Default: - A role is automatically created for you
        :param secrets_encryption_key: (experimental) KMS secret for envelope encryption for Kubernetes secrets. Default: - By default, Kubernetes stores all secret object data within etcd and all etcd volumes used by Amazon EKS are encrypted at the disk-level using AWS-Managed encryption keys.
        :param security_group: (experimental) Security Group to use for Control Plane ENIs. Default: - A security group is automatically created
        :param service_ipv4_cidr: (experimental) The CIDR block to assign Kubernetes service IP addresses from. Default: - Kubernetes assigns addresses from either the 10.100.0.0/16 or 172.20.0.0/16 CIDR blocks
        :param tags: (experimental) The tags assigned to the EKS cluster. Default: - none
        :param vpc: (experimental) The VPC in which to create the Cluster. Default: - a VPC with default configuration will be created and can be accessed through ``cluster.vpc``.
        :param vpc_subnets: (experimental) Where to place EKS Control Plane ENIs. For example, to only select private subnets, supply the following: ``vpcSubnets: [{ subnetType: ec2.SubnetType.PRIVATE_WITH_EGRESS }]`` Default: - All public and private subnets
        :param bootstrap_cluster_creator_admin_permissions: (experimental) Whether or not IAM principal of the cluster creator was set as a cluster admin access entry during cluster creation time. Changing this value after the cluster has been created will result in the cluster being replaced. Default: true
        :param compute: (experimental) Configuration for compute settings in Auto Mode. When enabled, EKS will automatically manage compute resources. Default: - Auto Mode compute disabled
        :param default_capacity: (experimental) Number of instances to allocate as an initial capacity for this cluster. Instance type can be configured through ``defaultCapacityInstanceType``, which defaults to ``m5.large``. Use ``cluster.addAutoScalingGroupCapacity`` to add additional customized capacity. Set this to ``0`` is you wish to avoid the initial capacity allocation. Default: 2
        :param default_capacity_instance: (experimental) The instance type to use for the default capacity. This will only be taken into account if ``defaultCapacity`` is > 0. Default: m5.large
        :param default_capacity_type: (experimental) The default capacity type for the cluster. Default: AUTOMODE
        :param output_config_command: (experimental) Determines whether a CloudFormation output with the ``aws eks update-kubeconfig`` command will be synthesized. This command will include the cluster name and, if applicable, the ARN of the masters IAM role. Default: true

        :stability: experimental
        :exampleMetadata: infused

        Example::

            cluster = eks.Cluster(self, "EksAutoCluster",
                version=eks.KubernetesVersion.V1_33,
                default_capacity_type=eks.DefaultCapacityType.AUTOMODE,
                compute=eks.ComputeConfig(
                    node_pools=["system", "general-purpose"]
                )
            )
        '''
        if isinstance(alb_controller, dict):
            alb_controller = AlbControllerOptions(**alb_controller)
        if isinstance(kubectl_provider_options, dict):
            kubectl_provider_options = KubectlProviderOptions(**kubectl_provider_options)
        if isinstance(compute, dict):
            compute = ComputeConfig(**compute)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__cdebba88d00ede95b7f48fc97c266609fdb0fc0ef3bb709493d319c84ab460db)
            check_type(argname="argument version", value=version, expected_type=type_hints["version"])
            check_type(argname="argument alb_controller", value=alb_controller, expected_type=type_hints["alb_controller"])
            check_type(argname="argument cluster_logging", value=cluster_logging, expected_type=type_hints["cluster_logging"])
            check_type(argname="argument cluster_name", value=cluster_name, expected_type=type_hints["cluster_name"])
            check_type(argname="argument core_dns_compute_type", value=core_dns_compute_type, expected_type=type_hints["core_dns_compute_type"])
            check_type(argname="argument endpoint_access", value=endpoint_access, expected_type=type_hints["endpoint_access"])
            check_type(argname="argument ip_family", value=ip_family, expected_type=type_hints["ip_family"])
            check_type(argname="argument kubectl_provider_options", value=kubectl_provider_options, expected_type=type_hints["kubectl_provider_options"])
            check_type(argname="argument masters_role", value=masters_role, expected_type=type_hints["masters_role"])
            check_type(argname="argument prune", value=prune, expected_type=type_hints["prune"])
            check_type(argname="argument role", value=role, expected_type=type_hints["role"])
            check_type(argname="argument secrets_encryption_key", value=secrets_encryption_key, expected_type=type_hints["secrets_encryption_key"])
            check_type(argname="argument security_group", value=security_group, expected_type=type_hints["security_group"])
            check_type(argname="argument service_ipv4_cidr", value=service_ipv4_cidr, expected_type=type_hints["service_ipv4_cidr"])
            check_type(argname="argument tags", value=tags, expected_type=type_hints["tags"])
            check_type(argname="argument vpc", value=vpc, expected_type=type_hints["vpc"])
            check_type(argname="argument vpc_subnets", value=vpc_subnets, expected_type=type_hints["vpc_subnets"])
            check_type(argname="argument bootstrap_cluster_creator_admin_permissions", value=bootstrap_cluster_creator_admin_permissions, expected_type=type_hints["bootstrap_cluster_creator_admin_permissions"])
            check_type(argname="argument compute", value=compute, expected_type=type_hints["compute"])
            check_type(argname="argument default_capacity", value=default_capacity, expected_type=type_hints["default_capacity"])
            check_type(argname="argument default_capacity_instance", value=default_capacity_instance, expected_type=type_hints["default_capacity_instance"])
            check_type(argname="argument default_capacity_type", value=default_capacity_type, expected_type=type_hints["default_capacity_type"])
            check_type(argname="argument output_config_command", value=output_config_command, expected_type=type_hints["output_config_command"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "version": version,
        }
        if alb_controller is not None:
            self._values["alb_controller"] = alb_controller
        if cluster_logging is not None:
            self._values["cluster_logging"] = cluster_logging
        if cluster_name is not None:
            self._values["cluster_name"] = cluster_name
        if core_dns_compute_type is not None:
            self._values["core_dns_compute_type"] = core_dns_compute_type
        if endpoint_access is not None:
            self._values["endpoint_access"] = endpoint_access
        if ip_family is not None:
            self._values["ip_family"] = ip_family
        if kubectl_provider_options is not None:
            self._values["kubectl_provider_options"] = kubectl_provider_options
        if masters_role is not None:
            self._values["masters_role"] = masters_role
        if prune is not None:
            self._values["prune"] = prune
        if role is not None:
            self._values["role"] = role
        if secrets_encryption_key is not None:
            self._values["secrets_encryption_key"] = secrets_encryption_key
        if security_group is not None:
            self._values["security_group"] = security_group
        if service_ipv4_cidr is not None:
            self._values["service_ipv4_cidr"] = service_ipv4_cidr
        if tags is not None:
            self._values["tags"] = tags
        if vpc is not None:
            self._values["vpc"] = vpc
        if vpc_subnets is not None:
            self._values["vpc_subnets"] = vpc_subnets
        if bootstrap_cluster_creator_admin_permissions is not None:
            self._values["bootstrap_cluster_creator_admin_permissions"] = bootstrap_cluster_creator_admin_permissions
        if compute is not None:
            self._values["compute"] = compute
        if default_capacity is not None:
            self._values["default_capacity"] = default_capacity
        if default_capacity_instance is not None:
            self._values["default_capacity_instance"] = default_capacity_instance
        if default_capacity_type is not None:
            self._values["default_capacity_type"] = default_capacity_type
        if output_config_command is not None:
            self._values["output_config_command"] = output_config_command

    @builtins.property
    def version(self) -> "KubernetesVersion":
        '''(experimental) The Kubernetes version to run in the cluster.

        :stability: experimental
        '''
        result = self._values.get("version")
        assert result is not None, "Required property 'version' is missing"
        return typing.cast("KubernetesVersion", result)

    @builtins.property
    def alb_controller(self) -> typing.Optional[AlbControllerOptions]:
        '''(experimental) Install the AWS Load Balancer Controller onto the cluster.

        :default: - The controller is not installed.

        :see: https://kubernetes-sigs.github.io/aws-load-balancer-controller
        :stability: experimental
        '''
        result = self._values.get("alb_controller")
        return typing.cast(typing.Optional[AlbControllerOptions], result)

    @builtins.property
    def cluster_logging(self) -> typing.Optional[typing.List[ClusterLoggingTypes]]:
        '''(experimental) The cluster log types which you want to enable.

        :default: - none

        :stability: experimental
        '''
        result = self._values.get("cluster_logging")
        return typing.cast(typing.Optional[typing.List[ClusterLoggingTypes]], result)

    @builtins.property
    def cluster_name(self) -> typing.Optional[builtins.str]:
        '''(experimental) Name for the cluster.

        :default: - Automatically generated name

        :stability: experimental
        '''
        result = self._values.get("cluster_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def core_dns_compute_type(self) -> typing.Optional["CoreDnsComputeType"]:
        '''(experimental) Controls the "eks.amazonaws.com/compute-type" annotation in the CoreDNS configuration on your cluster to determine which compute type to use for CoreDNS.

        :default: CoreDnsComputeType.EC2 (for ``FargateCluster`` the default is FARGATE)

        :stability: experimental
        '''
        result = self._values.get("core_dns_compute_type")
        return typing.cast(typing.Optional["CoreDnsComputeType"], result)

    @builtins.property
    def endpoint_access(self) -> typing.Optional["EndpointAccess"]:
        '''(experimental) Configure access to the Kubernetes API server endpoint..

        :default: EndpointAccess.PUBLIC_AND_PRIVATE

        :see: https://docs.aws.amazon.com/eks/latest/userguide/cluster-endpoint.html
        :stability: experimental
        '''
        result = self._values.get("endpoint_access")
        return typing.cast(typing.Optional["EndpointAccess"], result)

    @builtins.property
    def ip_family(self) -> typing.Optional["IpFamily"]:
        '''(experimental) Specify which IP family is used to assign Kubernetes pod and service IP addresses.

        :default: - IpFamily.IP_V4

        :see: https://docs.aws.amazon.com/eks/latest/APIReference/API_KubernetesNetworkConfigRequest.html#AmazonEKS-Type-KubernetesNetworkConfigRequest-ipFamily
        :stability: experimental
        '''
        result = self._values.get("ip_family")
        return typing.cast(typing.Optional["IpFamily"], result)

    @builtins.property
    def kubectl_provider_options(self) -> typing.Optional["KubectlProviderOptions"]:
        '''(experimental) Options for creating the kubectl provider - a lambda function that executes ``kubectl`` and ``helm`` against the cluster.

        If defined, ``kubectlLayer`` is a required property.

        If not defined, kubectl provider will not be created by default.

        :stability: experimental
        '''
        result = self._values.get("kubectl_provider_options")
        return typing.cast(typing.Optional["KubectlProviderOptions"], result)

    @builtins.property
    def masters_role(self) -> typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole]:
        '''(experimental) An IAM role that will be added to the ``system:masters`` Kubernetes RBAC group.

        :default: - no masters role.

        :see: https://kubernetes.io/docs/reference/access-authn-authz/rbac/#default-roles-and-role-bindings
        :stability: experimental
        '''
        result = self._values.get("masters_role")
        return typing.cast(typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole], result)

    @builtins.property
    def prune(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Indicates whether Kubernetes resources added through ``addManifest()`` can be automatically pruned.

        When this is enabled (default), prune labels will be
        allocated and injected to each resource. These labels will then be used
        when issuing the ``kubectl apply`` operation with the ``--prune`` switch.

        :default: true

        :stability: experimental
        '''
        result = self._values.get("prune")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def role(self) -> typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole]:
        '''(experimental) Role that provides permissions for the Kubernetes control plane to make calls to AWS API operations on your behalf.

        :default: - A role is automatically created for you

        :stability: experimental
        '''
        result = self._values.get("role")
        return typing.cast(typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole], result)

    @builtins.property
    def secrets_encryption_key(self) -> typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey]:
        '''(experimental) KMS secret for envelope encryption for Kubernetes secrets.

        :default:

        - By default, Kubernetes stores all secret object data within etcd and
        all etcd volumes used by Amazon EKS are encrypted at the disk-level
        using AWS-Managed encryption keys.

        :stability: experimental
        '''
        result = self._values.get("secrets_encryption_key")
        return typing.cast(typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey], result)

    @builtins.property
    def security_group(
        self,
    ) -> typing.Optional[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup]:
        '''(experimental) Security Group to use for Control Plane ENIs.

        :default: - A security group is automatically created

        :stability: experimental
        '''
        result = self._values.get("security_group")
        return typing.cast(typing.Optional[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup], result)

    @builtins.property
    def service_ipv4_cidr(self) -> typing.Optional[builtins.str]:
        '''(experimental) The CIDR block to assign Kubernetes service IP addresses from.

        :default:

        - Kubernetes assigns addresses from either the
        10.100.0.0/16 or 172.20.0.0/16 CIDR blocks

        :see: https://docs.aws.amazon.com/eks/latest/APIReference/API_KubernetesNetworkConfigRequest.html#AmazonEKS-Type-KubernetesNetworkConfigRequest-serviceIpv4Cidr
        :stability: experimental
        '''
        result = self._values.get("service_ipv4_cidr")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def tags(self) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        '''(experimental) The tags assigned to the EKS cluster.

        :default: - none

        :stability: experimental
        '''
        result = self._values.get("tags")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], result)

    @builtins.property
    def vpc(self) -> typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IVpc]:
        '''(experimental) The VPC in which to create the Cluster.

        :default: - a VPC with default configuration will be created and can be accessed through ``cluster.vpc``.

        :stability: experimental
        '''
        result = self._values.get("vpc")
        return typing.cast(typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IVpc], result)

    @builtins.property
    def vpc_subnets(
        self,
    ) -> typing.Optional[typing.List[_aws_cdk_aws_ec2_ceddda9d.SubnetSelection]]:
        '''(experimental) Where to place EKS Control Plane ENIs.

        For example, to only select private subnets, supply the following:

        ``vpcSubnets: [{ subnetType: ec2.SubnetType.PRIVATE_WITH_EGRESS }]``

        :default: - All public and private subnets

        :stability: experimental
        '''
        result = self._values.get("vpc_subnets")
        return typing.cast(typing.Optional[typing.List[_aws_cdk_aws_ec2_ceddda9d.SubnetSelection]], result)

    @builtins.property
    def bootstrap_cluster_creator_admin_permissions(
        self,
    ) -> typing.Optional[builtins.bool]:
        '''(experimental) Whether or not IAM principal of the cluster creator was set as a cluster admin access entry during cluster creation time.

        Changing this value after the cluster has been created will result in the cluster being replaced.

        :default: true

        :stability: experimental
        '''
        result = self._values.get("bootstrap_cluster_creator_admin_permissions")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def compute(self) -> typing.Optional["ComputeConfig"]:
        '''(experimental) Configuration for compute settings in Auto Mode.

        When enabled, EKS will automatically manage compute resources.

        :default: - Auto Mode compute disabled

        :stability: experimental
        '''
        result = self._values.get("compute")
        return typing.cast(typing.Optional["ComputeConfig"], result)

    @builtins.property
    def default_capacity(self) -> typing.Optional[jsii.Number]:
        '''(experimental) Number of instances to allocate as an initial capacity for this cluster.

        Instance type can be configured through ``defaultCapacityInstanceType``,
        which defaults to ``m5.large``.

        Use ``cluster.addAutoScalingGroupCapacity`` to add additional customized capacity. Set this
        to ``0`` is you wish to avoid the initial capacity allocation.

        :default: 2

        :stability: experimental
        '''
        result = self._values.get("default_capacity")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def default_capacity_instance(
        self,
    ) -> typing.Optional[_aws_cdk_aws_ec2_ceddda9d.InstanceType]:
        '''(experimental) The instance type to use for the default capacity.

        This will only be taken
        into account if ``defaultCapacity`` is > 0.

        :default: m5.large

        :stability: experimental
        '''
        result = self._values.get("default_capacity_instance")
        return typing.cast(typing.Optional[_aws_cdk_aws_ec2_ceddda9d.InstanceType], result)

    @builtins.property
    def default_capacity_type(self) -> typing.Optional["DefaultCapacityType"]:
        '''(experimental) The default capacity type for the cluster.

        :default: AUTOMODE

        :stability: experimental
        '''
        result = self._values.get("default_capacity_type")
        return typing.cast(typing.Optional["DefaultCapacityType"], result)

    @builtins.property
    def output_config_command(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Determines whether a CloudFormation output with the ``aws eks update-kubeconfig`` command will be synthesized.

        This command will include
        the cluster name and, if applicable, the ARN of the masters IAM role.

        :default: true

        :stability: experimental
        '''
        result = self._values.get("output_config_command")
        return typing.cast(typing.Optional[builtins.bool], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ClusterProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@aws-cdk/aws-eks-v2-alpha.ComputeConfig",
    jsii_struct_bases=[],
    name_mapping={"node_pools": "nodePools", "node_role": "nodeRole"},
)
class ComputeConfig:
    def __init__(
        self,
        *,
        node_pools: typing.Optional[typing.Sequence[builtins.str]] = None,
        node_role: typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole] = None,
    ) -> None:
        '''(experimental) Options for configuring EKS Auto Mode compute settings.

        When enabled, EKS will automatically manage compute resources like node groups and Fargate profiles.

        :param node_pools: (experimental) Names of nodePools to include in Auto Mode. You cannot modify the built in system and general-purpose node pools. You can only enable or disable them. Node pool values are case-sensitive and must be ``general-purpose`` and/or ``system``. Default: - ['system', 'general-purpose']
        :param node_role: (experimental) IAM role for the nodePools. Default: - generated by the CDK

        :stability: experimental
        :exampleMetadata: infused

        Example::

            cluster = eks.Cluster(self, "EksAutoCluster",
                version=eks.KubernetesVersion.V1_33,
                default_capacity_type=eks.DefaultCapacityType.AUTOMODE,
                compute=eks.ComputeConfig(
                    node_pools=["system", "general-purpose"]
                )
            )
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ecd4e0b2b1c23fafd1f01982b69fda08d5f3b0615f7bf8fe543ae2d8e6784f6e)
            check_type(argname="argument node_pools", value=node_pools, expected_type=type_hints["node_pools"])
            check_type(argname="argument node_role", value=node_role, expected_type=type_hints["node_role"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if node_pools is not None:
            self._values["node_pools"] = node_pools
        if node_role is not None:
            self._values["node_role"] = node_role

    @builtins.property
    def node_pools(self) -> typing.Optional[typing.List[builtins.str]]:
        '''(experimental) Names of nodePools to include in Auto Mode.

        You cannot modify the built in system and general-purpose node pools. You can only enable or disable them.
        Node pool values are case-sensitive and must be ``general-purpose`` and/or ``system``.

        :default: - ['system', 'general-purpose']

        :see: - https://docs.aws.amazon.com/eks/latest/userguide/create-node-pool.html
        :stability: experimental
        '''
        result = self._values.get("node_pools")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def node_role(self) -> typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole]:
        '''(experimental) IAM role for the nodePools.

        :default: - generated by the CDK

        :see: - https://docs.aws.amazon.com/eks/latest/userguide/create-node-role.html
        :stability: experimental
        '''
        result = self._values.get("node_role")
        return typing.cast(typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ComputeConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.enum(jsii_type="@aws-cdk/aws-eks-v2-alpha.CoreDnsComputeType")
class CoreDnsComputeType(enum.Enum):
    '''(experimental) The type of compute resources to use for CoreDNS.

    :stability: experimental
    '''

    EC2 = "EC2"
    '''(experimental) Deploy CoreDNS on EC2 instances.

    :stability: experimental
    '''
    FARGATE = "FARGATE"
    '''(experimental) Deploy CoreDNS on Fargate-managed instances.

    :stability: experimental
    '''


@jsii.enum(jsii_type="@aws-cdk/aws-eks-v2-alpha.CpuArch")
class CpuArch(enum.Enum):
    '''(experimental) CPU architecture.

    :stability: experimental
    '''

    ARM_64 = "ARM_64"
    '''(experimental) arm64 CPU type.

    :stability: experimental
    '''
    X86_64 = "X86_64"
    '''(experimental) x86_64 CPU type.

    :stability: experimental
    '''


@jsii.enum(jsii_type="@aws-cdk/aws-eks-v2-alpha.DefaultCapacityType")
class DefaultCapacityType(enum.Enum):
    '''(experimental) The default capacity type for the cluster.

    :stability: experimental
    :exampleMetadata: infused

    Example::

        cluster = eks.Cluster(self, "HelloEKS",
            version=eks.KubernetesVersion.V1_33,
            default_capacity_type=eks.DefaultCapacityType.NODEGROUP,
            default_capacity=0
        )
        
        cluster.add_nodegroup_capacity("custom-node-group",
            instance_types=[ec2.InstanceType("m5.large")],
            min_size=4,
            disk_size=100
        )
    '''

    NODEGROUP = "NODEGROUP"
    '''(experimental) managed node group.

    :stability: experimental
    '''
    EC2 = "EC2"
    '''(experimental) EC2 autoscaling group.

    :stability: experimental
    '''
    AUTOMODE = "AUTOMODE"
    '''(experimental) Auto Mode.

    :stability: experimental
    '''


@jsii.implements(_aws_cdk_aws_ec2_ceddda9d.IMachineImage)
class EksOptimizedImage(
    metaclass=jsii.JSIIMeta,
    jsii_type="@aws-cdk/aws-eks-v2-alpha.EksOptimizedImage",
):
    '''(experimental) Construct an Amazon Linux 2 image from the latest EKS Optimized AMI published in SSM.

    :stability: experimental
    :exampleMetadata: fixture=_generated

    Example::

        # The code below shows an example of how to instantiate this type.
        # The values are placeholders you should change.
        import aws_cdk.aws_eks_v2_alpha as eks_v2_alpha
        
        eks_optimized_image = eks_v2_alpha.EksOptimizedImage(
            cpu_arch=eks_v2_alpha.CpuArch.ARM_64,
            kubernetes_version="kubernetesVersion",
            node_type=eks_v2_alpha.NodeType.STANDARD
        )
    '''

    def __init__(
        self,
        *,
        cpu_arch: typing.Optional[CpuArch] = None,
        kubernetes_version: typing.Optional[builtins.str] = None,
        node_type: typing.Optional["NodeType"] = None,
    ) -> None:
        '''(experimental) Constructs a new instance of the EcsOptimizedAmi class.

        :param cpu_arch: (experimental) What cpu architecture to retrieve the image for (arm64 or x86_64). Default: CpuArch.X86_64
        :param kubernetes_version: (experimental) The Kubernetes version to use. Default: - The latest version
        :param node_type: (experimental) What instance type to retrieve the image for (standard or GPU-optimized). Default: NodeType.STANDARD

        :stability: experimental
        '''
        props = EksOptimizedImageProps(
            cpu_arch=cpu_arch,
            kubernetes_version=kubernetes_version,
            node_type=node_type,
        )

        jsii.create(self.__class__, self, [props])

    @jsii.member(jsii_name="getImage")
    def get_image(
        self,
        scope: _constructs_77d1e7e8.Construct,
    ) -> _aws_cdk_aws_ec2_ceddda9d.MachineImageConfig:
        '''(experimental) Return the correct image.

        :param scope: -

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5d60c600375f3cd4d2de211326df14f63e8e0248643232223ecaa3a7b785bd59)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
        return typing.cast(_aws_cdk_aws_ec2_ceddda9d.MachineImageConfig, jsii.invoke(self, "getImage", [scope]))


@jsii.data_type(
    jsii_type="@aws-cdk/aws-eks-v2-alpha.EksOptimizedImageProps",
    jsii_struct_bases=[],
    name_mapping={
        "cpu_arch": "cpuArch",
        "kubernetes_version": "kubernetesVersion",
        "node_type": "nodeType",
    },
)
class EksOptimizedImageProps:
    def __init__(
        self,
        *,
        cpu_arch: typing.Optional[CpuArch] = None,
        kubernetes_version: typing.Optional[builtins.str] = None,
        node_type: typing.Optional["NodeType"] = None,
    ) -> None:
        '''(experimental) Properties for EksOptimizedImage.

        :param cpu_arch: (experimental) What cpu architecture to retrieve the image for (arm64 or x86_64). Default: CpuArch.X86_64
        :param kubernetes_version: (experimental) The Kubernetes version to use. Default: - The latest version
        :param node_type: (experimental) What instance type to retrieve the image for (standard or GPU-optimized). Default: NodeType.STANDARD

        :stability: experimental
        :exampleMetadata: fixture=_generated

        Example::

            # The code below shows an example of how to instantiate this type.
            # The values are placeholders you should change.
            import aws_cdk.aws_eks_v2_alpha as eks_v2_alpha
            
            eks_optimized_image_props = eks_v2_alpha.EksOptimizedImageProps(
                cpu_arch=eks_v2_alpha.CpuArch.ARM_64,
                kubernetes_version="kubernetesVersion",
                node_type=eks_v2_alpha.NodeType.STANDARD
            )
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__eb5af32c1a878ac8b2da202202fb401d5b46e60face624044d2514c385431f61)
            check_type(argname="argument cpu_arch", value=cpu_arch, expected_type=type_hints["cpu_arch"])
            check_type(argname="argument kubernetes_version", value=kubernetes_version, expected_type=type_hints["kubernetes_version"])
            check_type(argname="argument node_type", value=node_type, expected_type=type_hints["node_type"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if cpu_arch is not None:
            self._values["cpu_arch"] = cpu_arch
        if kubernetes_version is not None:
            self._values["kubernetes_version"] = kubernetes_version
        if node_type is not None:
            self._values["node_type"] = node_type

    @builtins.property
    def cpu_arch(self) -> typing.Optional[CpuArch]:
        '''(experimental) What cpu architecture to retrieve the image for (arm64 or x86_64).

        :default: CpuArch.X86_64

        :stability: experimental
        '''
        result = self._values.get("cpu_arch")
        return typing.cast(typing.Optional[CpuArch], result)

    @builtins.property
    def kubernetes_version(self) -> typing.Optional[builtins.str]:
        '''(experimental) The Kubernetes version to use.

        :default: - The latest version

        :stability: experimental
        '''
        result = self._values.get("kubernetes_version")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def node_type(self) -> typing.Optional["NodeType"]:
        '''(experimental) What instance type to retrieve the image for (standard or GPU-optimized).

        :default: NodeType.STANDARD

        :stability: experimental
        '''
        result = self._values.get("node_type")
        return typing.cast(typing.Optional["NodeType"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "EksOptimizedImageProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class EndpointAccess(
    metaclass=jsii.JSIIMeta,
    jsii_type="@aws-cdk/aws-eks-v2-alpha.EndpointAccess",
):
    '''(experimental) Endpoint access characteristics.

    :stability: experimental
    :exampleMetadata: infused

    Example::

        cluster = eks.Cluster(self, "hello-eks",
            version=eks.KubernetesVersion.V1_33,
            endpoint_access=eks.EndpointAccess.PRIVATE
        )
    '''

    @jsii.member(jsii_name="onlyFrom")
    def only_from(self, *cidr: builtins.str) -> "EndpointAccess":
        '''(experimental) Restrict public access to specific CIDR blocks.

        If public access is disabled, this method will result in an error.

        :param cidr: CIDR blocks.

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a2ac5f9f350e9a81225b8d655b582f3953844cf3cd196d2153d2ac97f3457e25)
            check_type(argname="argument cidr", value=cidr, expected_type=typing.Tuple[type_hints["cidr"], ...]) # pyright: ignore [reportGeneralTypeIssues]
        return typing.cast("EndpointAccess", jsii.invoke(self, "onlyFrom", [*cidr]))

    @jsii.python.classproperty
    @jsii.member(jsii_name="PRIVATE")
    def PRIVATE(cls) -> "EndpointAccess":
        '''(experimental) The cluster endpoint is only accessible through your VPC.

        Worker node traffic to the endpoint will stay within your VPC.

        :stability: experimental
        '''
        return typing.cast("EndpointAccess", jsii.sget(cls, "PRIVATE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="PUBLIC")
    def PUBLIC(cls) -> "EndpointAccess":
        '''(experimental) The cluster endpoint is accessible from outside of your VPC.

        Worker node traffic will leave your VPC to connect to the endpoint.

        By default, the endpoint is exposed to all adresses. You can optionally limit the CIDR blocks that can access the public endpoint using the ``PUBLIC.onlyFrom`` method.
        If you limit access to specific CIDR blocks, you must ensure that the CIDR blocks that you
        specify include the addresses that worker nodes and Fargate pods (if you use them)
        access the public endpoint from.

        :stability: experimental
        '''
        return typing.cast("EndpointAccess", jsii.sget(cls, "PUBLIC"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="PUBLIC_AND_PRIVATE")
    def PUBLIC_AND_PRIVATE(cls) -> "EndpointAccess":
        '''(experimental) The cluster endpoint is accessible from outside of your VPC.

        Worker node traffic to the endpoint will stay within your VPC.

        By default, the endpoint is exposed to all adresses. You can optionally limit the CIDR blocks that can access the public endpoint using the ``PUBLIC_AND_PRIVATE.onlyFrom`` method.
        If you limit access to specific CIDR blocks, you must ensure that the CIDR blocks that you
        specify include the addresses that worker nodes and Fargate pods (if you use them)
        access the public endpoint from.

        :stability: experimental
        '''
        return typing.cast("EndpointAccess", jsii.sget(cls, "PUBLIC_AND_PRIVATE"))


@jsii.data_type(
    jsii_type="@aws-cdk/aws-eks-v2-alpha.FargateClusterProps",
    jsii_struct_bases=[ClusterCommonOptions],
    name_mapping={
        "version": "version",
        "alb_controller": "albController",
        "cluster_logging": "clusterLogging",
        "cluster_name": "clusterName",
        "core_dns_compute_type": "coreDnsComputeType",
        "endpoint_access": "endpointAccess",
        "ip_family": "ipFamily",
        "kubectl_provider_options": "kubectlProviderOptions",
        "masters_role": "mastersRole",
        "prune": "prune",
        "role": "role",
        "secrets_encryption_key": "secretsEncryptionKey",
        "security_group": "securityGroup",
        "service_ipv4_cidr": "serviceIpv4Cidr",
        "tags": "tags",
        "vpc": "vpc",
        "vpc_subnets": "vpcSubnets",
        "default_profile": "defaultProfile",
    },
)
class FargateClusterProps(ClusterCommonOptions):
    def __init__(
        self,
        *,
        version: "KubernetesVersion",
        alb_controller: typing.Optional[typing.Union[AlbControllerOptions, typing.Dict[builtins.str, typing.Any]]] = None,
        cluster_logging: typing.Optional[typing.Sequence[ClusterLoggingTypes]] = None,
        cluster_name: typing.Optional[builtins.str] = None,
        core_dns_compute_type: typing.Optional[CoreDnsComputeType] = None,
        endpoint_access: typing.Optional[EndpointAccess] = None,
        ip_family: typing.Optional["IpFamily"] = None,
        kubectl_provider_options: typing.Optional[typing.Union["KubectlProviderOptions", typing.Dict[builtins.str, typing.Any]]] = None,
        masters_role: typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole] = None,
        prune: typing.Optional[builtins.bool] = None,
        role: typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole] = None,
        secrets_encryption_key: typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey] = None,
        security_group: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup] = None,
        service_ipv4_cidr: typing.Optional[builtins.str] = None,
        tags: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        vpc: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IVpc] = None,
        vpc_subnets: typing.Optional[typing.Sequence[typing.Union[_aws_cdk_aws_ec2_ceddda9d.SubnetSelection, typing.Dict[builtins.str, typing.Any]]]] = None,
        default_profile: typing.Optional[typing.Union["FargateProfileOptions", typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''(experimental) Configuration props for EKS Fargate.

        :param version: (experimental) The Kubernetes version to run in the cluster.
        :param alb_controller: (experimental) Install the AWS Load Balancer Controller onto the cluster. Default: - The controller is not installed.
        :param cluster_logging: (experimental) The cluster log types which you want to enable. Default: - none
        :param cluster_name: (experimental) Name for the cluster. Default: - Automatically generated name
        :param core_dns_compute_type: (experimental) Controls the "eks.amazonaws.com/compute-type" annotation in the CoreDNS configuration on your cluster to determine which compute type to use for CoreDNS. Default: CoreDnsComputeType.EC2 (for ``FargateCluster`` the default is FARGATE)
        :param endpoint_access: (experimental) Configure access to the Kubernetes API server endpoint.. Default: EndpointAccess.PUBLIC_AND_PRIVATE
        :param ip_family: (experimental) Specify which IP family is used to assign Kubernetes pod and service IP addresses. Default: - IpFamily.IP_V4
        :param kubectl_provider_options: (experimental) Options for creating the kubectl provider - a lambda function that executes ``kubectl`` and ``helm`` against the cluster. If defined, ``kubectlLayer`` is a required property. If not defined, kubectl provider will not be created by default.
        :param masters_role: (experimental) An IAM role that will be added to the ``system:masters`` Kubernetes RBAC group. Default: - no masters role.
        :param prune: (experimental) Indicates whether Kubernetes resources added through ``addManifest()`` can be automatically pruned. When this is enabled (default), prune labels will be allocated and injected to each resource. These labels will then be used when issuing the ``kubectl apply`` operation with the ``--prune`` switch. Default: true
        :param role: (experimental) Role that provides permissions for the Kubernetes control plane to make calls to AWS API operations on your behalf. Default: - A role is automatically created for you
        :param secrets_encryption_key: (experimental) KMS secret for envelope encryption for Kubernetes secrets. Default: - By default, Kubernetes stores all secret object data within etcd and all etcd volumes used by Amazon EKS are encrypted at the disk-level using AWS-Managed encryption keys.
        :param security_group: (experimental) Security Group to use for Control Plane ENIs. Default: - A security group is automatically created
        :param service_ipv4_cidr: (experimental) The CIDR block to assign Kubernetes service IP addresses from. Default: - Kubernetes assigns addresses from either the 10.100.0.0/16 or 172.20.0.0/16 CIDR blocks
        :param tags: (experimental) The tags assigned to the EKS cluster. Default: - none
        :param vpc: (experimental) The VPC in which to create the Cluster. Default: - a VPC with default configuration will be created and can be accessed through ``cluster.vpc``.
        :param vpc_subnets: (experimental) Where to place EKS Control Plane ENIs. For example, to only select private subnets, supply the following: ``vpcSubnets: [{ subnetType: ec2.SubnetType.PRIVATE_WITH_EGRESS }]`` Default: - All public and private subnets
        :param default_profile: (experimental) Fargate Profile to create along with the cluster. Default: - A profile called "default" with 'default' and 'kube-system' selectors will be created if this is left undefined.

        :stability: experimental
        :exampleMetadata: infused

        Example::

            cluster = eks.FargateCluster(self, "MyCluster",
                version=eks.KubernetesVersion.V1_33
            )
        '''
        if isinstance(alb_controller, dict):
            alb_controller = AlbControllerOptions(**alb_controller)
        if isinstance(kubectl_provider_options, dict):
            kubectl_provider_options = KubectlProviderOptions(**kubectl_provider_options)
        if isinstance(default_profile, dict):
            default_profile = FargateProfileOptions(**default_profile)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__89419afd037884b6a69d80af0bf5c1fe35164b8d31e7e5746501350e5dce60d0)
            check_type(argname="argument version", value=version, expected_type=type_hints["version"])
            check_type(argname="argument alb_controller", value=alb_controller, expected_type=type_hints["alb_controller"])
            check_type(argname="argument cluster_logging", value=cluster_logging, expected_type=type_hints["cluster_logging"])
            check_type(argname="argument cluster_name", value=cluster_name, expected_type=type_hints["cluster_name"])
            check_type(argname="argument core_dns_compute_type", value=core_dns_compute_type, expected_type=type_hints["core_dns_compute_type"])
            check_type(argname="argument endpoint_access", value=endpoint_access, expected_type=type_hints["endpoint_access"])
            check_type(argname="argument ip_family", value=ip_family, expected_type=type_hints["ip_family"])
            check_type(argname="argument kubectl_provider_options", value=kubectl_provider_options, expected_type=type_hints["kubectl_provider_options"])
            check_type(argname="argument masters_role", value=masters_role, expected_type=type_hints["masters_role"])
            check_type(argname="argument prune", value=prune, expected_type=type_hints["prune"])
            check_type(argname="argument role", value=role, expected_type=type_hints["role"])
            check_type(argname="argument secrets_encryption_key", value=secrets_encryption_key, expected_type=type_hints["secrets_encryption_key"])
            check_type(argname="argument security_group", value=security_group, expected_type=type_hints["security_group"])
            check_type(argname="argument service_ipv4_cidr", value=service_ipv4_cidr, expected_type=type_hints["service_ipv4_cidr"])
            check_type(argname="argument tags", value=tags, expected_type=type_hints["tags"])
            check_type(argname="argument vpc", value=vpc, expected_type=type_hints["vpc"])
            check_type(argname="argument vpc_subnets", value=vpc_subnets, expected_type=type_hints["vpc_subnets"])
            check_type(argname="argument default_profile", value=default_profile, expected_type=type_hints["default_profile"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "version": version,
        }
        if alb_controller is not None:
            self._values["alb_controller"] = alb_controller
        if cluster_logging is not None:
            self._values["cluster_logging"] = cluster_logging
        if cluster_name is not None:
            self._values["cluster_name"] = cluster_name
        if core_dns_compute_type is not None:
            self._values["core_dns_compute_type"] = core_dns_compute_type
        if endpoint_access is not None:
            self._values["endpoint_access"] = endpoint_access
        if ip_family is not None:
            self._values["ip_family"] = ip_family
        if kubectl_provider_options is not None:
            self._values["kubectl_provider_options"] = kubectl_provider_options
        if masters_role is not None:
            self._values["masters_role"] = masters_role
        if prune is not None:
            self._values["prune"] = prune
        if role is not None:
            self._values["role"] = role
        if secrets_encryption_key is not None:
            self._values["secrets_encryption_key"] = secrets_encryption_key
        if security_group is not None:
            self._values["security_group"] = security_group
        if service_ipv4_cidr is not None:
            self._values["service_ipv4_cidr"] = service_ipv4_cidr
        if tags is not None:
            self._values["tags"] = tags
        if vpc is not None:
            self._values["vpc"] = vpc
        if vpc_subnets is not None:
            self._values["vpc_subnets"] = vpc_subnets
        if default_profile is not None:
            self._values["default_profile"] = default_profile

    @builtins.property
    def version(self) -> "KubernetesVersion":
        '''(experimental) The Kubernetes version to run in the cluster.

        :stability: experimental
        '''
        result = self._values.get("version")
        assert result is not None, "Required property 'version' is missing"
        return typing.cast("KubernetesVersion", result)

    @builtins.property
    def alb_controller(self) -> typing.Optional[AlbControllerOptions]:
        '''(experimental) Install the AWS Load Balancer Controller onto the cluster.

        :default: - The controller is not installed.

        :see: https://kubernetes-sigs.github.io/aws-load-balancer-controller
        :stability: experimental
        '''
        result = self._values.get("alb_controller")
        return typing.cast(typing.Optional[AlbControllerOptions], result)

    @builtins.property
    def cluster_logging(self) -> typing.Optional[typing.List[ClusterLoggingTypes]]:
        '''(experimental) The cluster log types which you want to enable.

        :default: - none

        :stability: experimental
        '''
        result = self._values.get("cluster_logging")
        return typing.cast(typing.Optional[typing.List[ClusterLoggingTypes]], result)

    @builtins.property
    def cluster_name(self) -> typing.Optional[builtins.str]:
        '''(experimental) Name for the cluster.

        :default: - Automatically generated name

        :stability: experimental
        '''
        result = self._values.get("cluster_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def core_dns_compute_type(self) -> typing.Optional[CoreDnsComputeType]:
        '''(experimental) Controls the "eks.amazonaws.com/compute-type" annotation in the CoreDNS configuration on your cluster to determine which compute type to use for CoreDNS.

        :default: CoreDnsComputeType.EC2 (for ``FargateCluster`` the default is FARGATE)

        :stability: experimental
        '''
        result = self._values.get("core_dns_compute_type")
        return typing.cast(typing.Optional[CoreDnsComputeType], result)

    @builtins.property
    def endpoint_access(self) -> typing.Optional[EndpointAccess]:
        '''(experimental) Configure access to the Kubernetes API server endpoint..

        :default: EndpointAccess.PUBLIC_AND_PRIVATE

        :see: https://docs.aws.amazon.com/eks/latest/userguide/cluster-endpoint.html
        :stability: experimental
        '''
        result = self._values.get("endpoint_access")
        return typing.cast(typing.Optional[EndpointAccess], result)

    @builtins.property
    def ip_family(self) -> typing.Optional["IpFamily"]:
        '''(experimental) Specify which IP family is used to assign Kubernetes pod and service IP addresses.

        :default: - IpFamily.IP_V4

        :see: https://docs.aws.amazon.com/eks/latest/APIReference/API_KubernetesNetworkConfigRequest.html#AmazonEKS-Type-KubernetesNetworkConfigRequest-ipFamily
        :stability: experimental
        '''
        result = self._values.get("ip_family")
        return typing.cast(typing.Optional["IpFamily"], result)

    @builtins.property
    def kubectl_provider_options(self) -> typing.Optional["KubectlProviderOptions"]:
        '''(experimental) Options for creating the kubectl provider - a lambda function that executes ``kubectl`` and ``helm`` against the cluster.

        If defined, ``kubectlLayer`` is a required property.

        If not defined, kubectl provider will not be created by default.

        :stability: experimental
        '''
        result = self._values.get("kubectl_provider_options")
        return typing.cast(typing.Optional["KubectlProviderOptions"], result)

    @builtins.property
    def masters_role(self) -> typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole]:
        '''(experimental) An IAM role that will be added to the ``system:masters`` Kubernetes RBAC group.

        :default: - no masters role.

        :see: https://kubernetes.io/docs/reference/access-authn-authz/rbac/#default-roles-and-role-bindings
        :stability: experimental
        '''
        result = self._values.get("masters_role")
        return typing.cast(typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole], result)

    @builtins.property
    def prune(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Indicates whether Kubernetes resources added through ``addManifest()`` can be automatically pruned.

        When this is enabled (default), prune labels will be
        allocated and injected to each resource. These labels will then be used
        when issuing the ``kubectl apply`` operation with the ``--prune`` switch.

        :default: true

        :stability: experimental
        '''
        result = self._values.get("prune")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def role(self) -> typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole]:
        '''(experimental) Role that provides permissions for the Kubernetes control plane to make calls to AWS API operations on your behalf.

        :default: - A role is automatically created for you

        :stability: experimental
        '''
        result = self._values.get("role")
        return typing.cast(typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole], result)

    @builtins.property
    def secrets_encryption_key(self) -> typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey]:
        '''(experimental) KMS secret for envelope encryption for Kubernetes secrets.

        :default:

        - By default, Kubernetes stores all secret object data within etcd and
        all etcd volumes used by Amazon EKS are encrypted at the disk-level
        using AWS-Managed encryption keys.

        :stability: experimental
        '''
        result = self._values.get("secrets_encryption_key")
        return typing.cast(typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey], result)

    @builtins.property
    def security_group(
        self,
    ) -> typing.Optional[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup]:
        '''(experimental) Security Group to use for Control Plane ENIs.

        :default: - A security group is automatically created

        :stability: experimental
        '''
        result = self._values.get("security_group")
        return typing.cast(typing.Optional[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup], result)

    @builtins.property
    def service_ipv4_cidr(self) -> typing.Optional[builtins.str]:
        '''(experimental) The CIDR block to assign Kubernetes service IP addresses from.

        :default:

        - Kubernetes assigns addresses from either the
        10.100.0.0/16 or 172.20.0.0/16 CIDR blocks

        :see: https://docs.aws.amazon.com/eks/latest/APIReference/API_KubernetesNetworkConfigRequest.html#AmazonEKS-Type-KubernetesNetworkConfigRequest-serviceIpv4Cidr
        :stability: experimental
        '''
        result = self._values.get("service_ipv4_cidr")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def tags(self) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        '''(experimental) The tags assigned to the EKS cluster.

        :default: - none

        :stability: experimental
        '''
        result = self._values.get("tags")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], result)

    @builtins.property
    def vpc(self) -> typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IVpc]:
        '''(experimental) The VPC in which to create the Cluster.

        :default: - a VPC with default configuration will be created and can be accessed through ``cluster.vpc``.

        :stability: experimental
        '''
        result = self._values.get("vpc")
        return typing.cast(typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IVpc], result)

    @builtins.property
    def vpc_subnets(
        self,
    ) -> typing.Optional[typing.List[_aws_cdk_aws_ec2_ceddda9d.SubnetSelection]]:
        '''(experimental) Where to place EKS Control Plane ENIs.

        For example, to only select private subnets, supply the following:

        ``vpcSubnets: [{ subnetType: ec2.SubnetType.PRIVATE_WITH_EGRESS }]``

        :default: - All public and private subnets

        :stability: experimental
        '''
        result = self._values.get("vpc_subnets")
        return typing.cast(typing.Optional[typing.List[_aws_cdk_aws_ec2_ceddda9d.SubnetSelection]], result)

    @builtins.property
    def default_profile(self) -> typing.Optional["FargateProfileOptions"]:
        '''(experimental) Fargate Profile to create along with the cluster.

        :default:

        - A profile called "default" with 'default' and 'kube-system'
        selectors will be created if this is left undefined.

        :stability: experimental
        '''
        result = self._values.get("default_profile")
        return typing.cast(typing.Optional["FargateProfileOptions"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "FargateClusterProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.implements(_aws_cdk_ceddda9d.ITaggable)
class FargateProfile(
    _constructs_77d1e7e8.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="@aws-cdk/aws-eks-v2-alpha.FargateProfile",
):
    '''(experimental) Fargate profiles allows an administrator to declare which pods run on Fargate.

    This declaration is done through the profile’s selectors. Each
    profile can have up to five selectors that contain a namespace and optional
    labels. You must define a namespace for every selector. The label field
    consists of multiple optional key-value pairs. Pods that match a selector (by
    matching a namespace for the selector and all of the labels specified in the
    selector) are scheduled on Fargate. If a namespace selector is defined
    without any labels, Amazon EKS will attempt to schedule all pods that run in
    that namespace onto Fargate using the profile. If a to-be-scheduled pod
    matches any of the selectors in the Fargate profile, then that pod is
    scheduled on Fargate.

    If a pod matches multiple Fargate profiles, Amazon EKS picks one of the
    matches at random. In this case, you can specify which profile a pod should
    use by adding the following Kubernetes label to the pod specification:
    eks.amazonaws.com/fargate-profile: profile_name. However, the pod must still
    match a selector in that profile in order to be scheduled onto Fargate.

    :stability: experimental
    :exampleMetadata: infused

    Example::

        # cluster: eks.Cluster
        
        eks.FargateProfile(self, "MyProfile",
            cluster=cluster,
            selectors=[eks.Selector(namespace="default")]
        )
    '''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        cluster: "Cluster",
        selectors: typing.Sequence[typing.Union["Selector", typing.Dict[builtins.str, typing.Any]]],
        fargate_profile_name: typing.Optional[builtins.str] = None,
        pod_execution_role: typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole] = None,
        subnet_selection: typing.Optional[typing.Union[_aws_cdk_aws_ec2_ceddda9d.SubnetSelection, typing.Dict[builtins.str, typing.Any]]] = None,
        vpc: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IVpc] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param cluster: (experimental) The EKS cluster to apply the Fargate profile to. [disable-awslint:ref-via-interface]
        :param selectors: (experimental) The selectors to match for pods to use this Fargate profile. Each selector must have an associated namespace. Optionally, you can also specify labels for a namespace. At least one selector is required and you may specify up to five selectors.
        :param fargate_profile_name: (experimental) The name of the Fargate profile. Default: - generated
        :param pod_execution_role: (experimental) The pod execution role to use for pods that match the selectors in the Fargate profile. The pod execution role allows Fargate infrastructure to register with your cluster as a node, and it provides read access to Amazon ECR image repositories. Default: - a role will be automatically created
        :param subnet_selection: (experimental) Select which subnets to launch your pods into. At this time, pods running on Fargate are not assigned public IP addresses, so only private subnets (with no direct route to an Internet Gateway) are allowed. You must specify the VPC to customize the subnet selection Default: - all private subnets of the VPC are selected.
        :param vpc: (experimental) The VPC from which to select subnets to launch your pods into. By default, all private subnets are selected. You can customize this using ``subnetSelection``. Default: - all private subnets used by the EKS cluster

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8fda2e7322d0839708496820fcb933c83a2eca4719746d8d6c30b513e2d6ae21)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = FargateProfileProps(
            cluster=cluster,
            selectors=selectors,
            fargate_profile_name=fargate_profile_name,
            pod_execution_role=pod_execution_role,
            subnet_selection=subnet_selection,
            vpc=vpc,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @builtins.property
    @jsii.member(jsii_name="fargateProfileArn")
    def fargate_profile_arn(self) -> builtins.str:
        '''(experimental) The full Amazon Resource Name (ARN) of the Fargate profile.

        :stability: experimental
        :attribute: true
        '''
        return typing.cast(builtins.str, jsii.get(self, "fargateProfileArn"))

    @builtins.property
    @jsii.member(jsii_name="fargateProfileName")
    def fargate_profile_name(self) -> builtins.str:
        '''(experimental) The name of the Fargate profile.

        :stability: experimental
        :attribute: true
        '''
        return typing.cast(builtins.str, jsii.get(self, "fargateProfileName"))

    @builtins.property
    @jsii.member(jsii_name="podExecutionRole")
    def pod_execution_role(self) -> _aws_cdk_aws_iam_ceddda9d.IRole:
        '''(experimental) The pod execution role to use for pods that match the selectors in the Fargate profile.

        The pod execution role allows Fargate infrastructure to
        register with your cluster as a node, and it provides read access to Amazon
        ECR image repositories.

        :stability: experimental
        '''
        return typing.cast(_aws_cdk_aws_iam_ceddda9d.IRole, jsii.get(self, "podExecutionRole"))

    @builtins.property
    @jsii.member(jsii_name="tags")
    def tags(self) -> _aws_cdk_ceddda9d.TagManager:
        '''(experimental) Resource tags.

        :stability: experimental
        '''
        return typing.cast(_aws_cdk_ceddda9d.TagManager, jsii.get(self, "tags"))


@jsii.data_type(
    jsii_type="@aws-cdk/aws-eks-v2-alpha.FargateProfileOptions",
    jsii_struct_bases=[],
    name_mapping={
        "selectors": "selectors",
        "fargate_profile_name": "fargateProfileName",
        "pod_execution_role": "podExecutionRole",
        "subnet_selection": "subnetSelection",
        "vpc": "vpc",
    },
)
class FargateProfileOptions:
    def __init__(
        self,
        *,
        selectors: typing.Sequence[typing.Union["Selector", typing.Dict[builtins.str, typing.Any]]],
        fargate_profile_name: typing.Optional[builtins.str] = None,
        pod_execution_role: typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole] = None,
        subnet_selection: typing.Optional[typing.Union[_aws_cdk_aws_ec2_ceddda9d.SubnetSelection, typing.Dict[builtins.str, typing.Any]]] = None,
        vpc: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IVpc] = None,
    ) -> None:
        '''(experimental) Options for defining EKS Fargate Profiles.

        :param selectors: (experimental) The selectors to match for pods to use this Fargate profile. Each selector must have an associated namespace. Optionally, you can also specify labels for a namespace. At least one selector is required and you may specify up to five selectors.
        :param fargate_profile_name: (experimental) The name of the Fargate profile. Default: - generated
        :param pod_execution_role: (experimental) The pod execution role to use for pods that match the selectors in the Fargate profile. The pod execution role allows Fargate infrastructure to register with your cluster as a node, and it provides read access to Amazon ECR image repositories. Default: - a role will be automatically created
        :param subnet_selection: (experimental) Select which subnets to launch your pods into. At this time, pods running on Fargate are not assigned public IP addresses, so only private subnets (with no direct route to an Internet Gateway) are allowed. You must specify the VPC to customize the subnet selection Default: - all private subnets of the VPC are selected.
        :param vpc: (experimental) The VPC from which to select subnets to launch your pods into. By default, all private subnets are selected. You can customize this using ``subnetSelection``. Default: - all private subnets used by the EKS cluster

        :stability: experimental
        :exampleMetadata: infused

        Example::

            # cluster: eks.Cluster
            
            cluster.add_fargate_profile("MyProfile",
                selectors=[eks.Selector(namespace="default")]
            )
        '''
        if isinstance(subnet_selection, dict):
            subnet_selection = _aws_cdk_aws_ec2_ceddda9d.SubnetSelection(**subnet_selection)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__13ac7e4d5e707c67c365ab240566b231d61479b53823a8c1813c0ca790a3fa4b)
            check_type(argname="argument selectors", value=selectors, expected_type=type_hints["selectors"])
            check_type(argname="argument fargate_profile_name", value=fargate_profile_name, expected_type=type_hints["fargate_profile_name"])
            check_type(argname="argument pod_execution_role", value=pod_execution_role, expected_type=type_hints["pod_execution_role"])
            check_type(argname="argument subnet_selection", value=subnet_selection, expected_type=type_hints["subnet_selection"])
            check_type(argname="argument vpc", value=vpc, expected_type=type_hints["vpc"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "selectors": selectors,
        }
        if fargate_profile_name is not None:
            self._values["fargate_profile_name"] = fargate_profile_name
        if pod_execution_role is not None:
            self._values["pod_execution_role"] = pod_execution_role
        if subnet_selection is not None:
            self._values["subnet_selection"] = subnet_selection
        if vpc is not None:
            self._values["vpc"] = vpc

    @builtins.property
    def selectors(self) -> typing.List["Selector"]:
        '''(experimental) The selectors to match for pods to use this Fargate profile.

        Each selector
        must have an associated namespace. Optionally, you can also specify labels
        for a namespace.

        At least one selector is required and you may specify up to five selectors.

        :stability: experimental
        '''
        result = self._values.get("selectors")
        assert result is not None, "Required property 'selectors' is missing"
        return typing.cast(typing.List["Selector"], result)

    @builtins.property
    def fargate_profile_name(self) -> typing.Optional[builtins.str]:
        '''(experimental) The name of the Fargate profile.

        :default: - generated

        :stability: experimental
        '''
        result = self._values.get("fargate_profile_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def pod_execution_role(self) -> typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole]:
        '''(experimental) The pod execution role to use for pods that match the selectors in the Fargate profile.

        The pod execution role allows Fargate infrastructure to
        register with your cluster as a node, and it provides read access to Amazon
        ECR image repositories.

        :default: - a role will be automatically created

        :see: https://docs.aws.amazon.com/eks/latest/userguide/pod-execution-role.html
        :stability: experimental
        '''
        result = self._values.get("pod_execution_role")
        return typing.cast(typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole], result)

    @builtins.property
    def subnet_selection(
        self,
    ) -> typing.Optional[_aws_cdk_aws_ec2_ceddda9d.SubnetSelection]:
        '''(experimental) Select which subnets to launch your pods into.

        At this time, pods running
        on Fargate are not assigned public IP addresses, so only private subnets
        (with no direct route to an Internet Gateway) are allowed.

        You must specify the VPC to customize the subnet selection

        :default: - all private subnets of the VPC are selected.

        :stability: experimental
        '''
        result = self._values.get("subnet_selection")
        return typing.cast(typing.Optional[_aws_cdk_aws_ec2_ceddda9d.SubnetSelection], result)

    @builtins.property
    def vpc(self) -> typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IVpc]:
        '''(experimental) The VPC from which to select subnets to launch your pods into.

        By default, all private subnets are selected. You can customize this using
        ``subnetSelection``.

        :default: - all private subnets used by the EKS cluster

        :stability: experimental
        '''
        result = self._values.get("vpc")
        return typing.cast(typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IVpc], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "FargateProfileOptions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@aws-cdk/aws-eks-v2-alpha.FargateProfileProps",
    jsii_struct_bases=[FargateProfileOptions],
    name_mapping={
        "selectors": "selectors",
        "fargate_profile_name": "fargateProfileName",
        "pod_execution_role": "podExecutionRole",
        "subnet_selection": "subnetSelection",
        "vpc": "vpc",
        "cluster": "cluster",
    },
)
class FargateProfileProps(FargateProfileOptions):
    def __init__(
        self,
        *,
        selectors: typing.Sequence[typing.Union["Selector", typing.Dict[builtins.str, typing.Any]]],
        fargate_profile_name: typing.Optional[builtins.str] = None,
        pod_execution_role: typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole] = None,
        subnet_selection: typing.Optional[typing.Union[_aws_cdk_aws_ec2_ceddda9d.SubnetSelection, typing.Dict[builtins.str, typing.Any]]] = None,
        vpc: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IVpc] = None,
        cluster: "Cluster",
    ) -> None:
        '''(experimental) Configuration props for EKS Fargate Profiles.

        :param selectors: (experimental) The selectors to match for pods to use this Fargate profile. Each selector must have an associated namespace. Optionally, you can also specify labels for a namespace. At least one selector is required and you may specify up to five selectors.
        :param fargate_profile_name: (experimental) The name of the Fargate profile. Default: - generated
        :param pod_execution_role: (experimental) The pod execution role to use for pods that match the selectors in the Fargate profile. The pod execution role allows Fargate infrastructure to register with your cluster as a node, and it provides read access to Amazon ECR image repositories. Default: - a role will be automatically created
        :param subnet_selection: (experimental) Select which subnets to launch your pods into. At this time, pods running on Fargate are not assigned public IP addresses, so only private subnets (with no direct route to an Internet Gateway) are allowed. You must specify the VPC to customize the subnet selection Default: - all private subnets of the VPC are selected.
        :param vpc: (experimental) The VPC from which to select subnets to launch your pods into. By default, all private subnets are selected. You can customize this using ``subnetSelection``. Default: - all private subnets used by the EKS cluster
        :param cluster: (experimental) The EKS cluster to apply the Fargate profile to. [disable-awslint:ref-via-interface]

        :stability: experimental
        :exampleMetadata: infused

        Example::

            # cluster: eks.Cluster
            
            eks.FargateProfile(self, "MyProfile",
                cluster=cluster,
                selectors=[eks.Selector(namespace="default")]
            )
        '''
        if isinstance(subnet_selection, dict):
            subnet_selection = _aws_cdk_aws_ec2_ceddda9d.SubnetSelection(**subnet_selection)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__fe54fadef84522ce1ddcbcb9cb688cea9c28ea444936beae0d6ab3cc18f646f5)
            check_type(argname="argument selectors", value=selectors, expected_type=type_hints["selectors"])
            check_type(argname="argument fargate_profile_name", value=fargate_profile_name, expected_type=type_hints["fargate_profile_name"])
            check_type(argname="argument pod_execution_role", value=pod_execution_role, expected_type=type_hints["pod_execution_role"])
            check_type(argname="argument subnet_selection", value=subnet_selection, expected_type=type_hints["subnet_selection"])
            check_type(argname="argument vpc", value=vpc, expected_type=type_hints["vpc"])
            check_type(argname="argument cluster", value=cluster, expected_type=type_hints["cluster"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "selectors": selectors,
            "cluster": cluster,
        }
        if fargate_profile_name is not None:
            self._values["fargate_profile_name"] = fargate_profile_name
        if pod_execution_role is not None:
            self._values["pod_execution_role"] = pod_execution_role
        if subnet_selection is not None:
            self._values["subnet_selection"] = subnet_selection
        if vpc is not None:
            self._values["vpc"] = vpc

    @builtins.property
    def selectors(self) -> typing.List["Selector"]:
        '''(experimental) The selectors to match for pods to use this Fargate profile.

        Each selector
        must have an associated namespace. Optionally, you can also specify labels
        for a namespace.

        At least one selector is required and you may specify up to five selectors.

        :stability: experimental
        '''
        result = self._values.get("selectors")
        assert result is not None, "Required property 'selectors' is missing"
        return typing.cast(typing.List["Selector"], result)

    @builtins.property
    def fargate_profile_name(self) -> typing.Optional[builtins.str]:
        '''(experimental) The name of the Fargate profile.

        :default: - generated

        :stability: experimental
        '''
        result = self._values.get("fargate_profile_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def pod_execution_role(self) -> typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole]:
        '''(experimental) The pod execution role to use for pods that match the selectors in the Fargate profile.

        The pod execution role allows Fargate infrastructure to
        register with your cluster as a node, and it provides read access to Amazon
        ECR image repositories.

        :default: - a role will be automatically created

        :see: https://docs.aws.amazon.com/eks/latest/userguide/pod-execution-role.html
        :stability: experimental
        '''
        result = self._values.get("pod_execution_role")
        return typing.cast(typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole], result)

    @builtins.property
    def subnet_selection(
        self,
    ) -> typing.Optional[_aws_cdk_aws_ec2_ceddda9d.SubnetSelection]:
        '''(experimental) Select which subnets to launch your pods into.

        At this time, pods running
        on Fargate are not assigned public IP addresses, so only private subnets
        (with no direct route to an Internet Gateway) are allowed.

        You must specify the VPC to customize the subnet selection

        :default: - all private subnets of the VPC are selected.

        :stability: experimental
        '''
        result = self._values.get("subnet_selection")
        return typing.cast(typing.Optional[_aws_cdk_aws_ec2_ceddda9d.SubnetSelection], result)

    @builtins.property
    def vpc(self) -> typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IVpc]:
        '''(experimental) The VPC from which to select subnets to launch your pods into.

        By default, all private subnets are selected. You can customize this using
        ``subnetSelection``.

        :default: - all private subnets used by the EKS cluster

        :stability: experimental
        '''
        result = self._values.get("vpc")
        return typing.cast(typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IVpc], result)

    @builtins.property
    def cluster(self) -> "Cluster":
        '''(experimental) The EKS cluster to apply the Fargate profile to.

        [disable-awslint:ref-via-interface]

        :stability: experimental
        '''
        result = self._values.get("cluster")
        assert result is not None, "Required property 'cluster' is missing"
        return typing.cast("Cluster", result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "FargateProfileProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class HelmChart(
    _constructs_77d1e7e8.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="@aws-cdk/aws-eks-v2-alpha.HelmChart",
):
    '''(experimental) Represents a helm chart within the Kubernetes system.

    Applies/deletes the resources using ``kubectl`` in sync with the resource.

    :stability: experimental
    :exampleMetadata: infused

    Example::

        # cluster: eks.Cluster
        
        # option 1: use a construct
        eks.HelmChart(self, "MyOCIChart",
            cluster=cluster,
            chart="some-chart",
            repository="oci://${ACCOUNT_ID}.dkr.ecr.${ACCOUNT_REGION}.amazonaws.com/${REPO_NAME}",
            namespace="oci",
            version="0.0.1"
        )
    '''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        cluster: "ICluster",
        atomic: typing.Optional[builtins.bool] = None,
        chart: typing.Optional[builtins.str] = None,
        chart_asset: typing.Optional[_aws_cdk_aws_s3_assets_ceddda9d.Asset] = None,
        create_namespace: typing.Optional[builtins.bool] = None,
        namespace: typing.Optional[builtins.str] = None,
        release: typing.Optional[builtins.str] = None,
        repository: typing.Optional[builtins.str] = None,
        skip_crds: typing.Optional[builtins.bool] = None,
        timeout: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        values: typing.Optional[typing.Mapping[builtins.str, typing.Any]] = None,
        version: typing.Optional[builtins.str] = None,
        wait: typing.Optional[builtins.bool] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param cluster: (experimental) The EKS cluster to apply this configuration to. [disable-awslint:ref-via-interface]
        :param atomic: (experimental) Whether or not Helm should treat this operation as atomic; if set, upgrade process rolls back changes made in case of failed upgrade. The --wait flag will be set automatically if --atomic is used. Default: false
        :param chart: (experimental) The name of the chart. Either this or ``chartAsset`` must be specified. Default: - No chart name. Implies ``chartAsset`` is used.
        :param chart_asset: (experimental) The chart in the form of an asset. Either this or ``chart`` must be specified. Default: - No chart asset. Implies ``chart`` is used.
        :param create_namespace: (experimental) create namespace if not exist. Default: true
        :param namespace: (experimental) The Kubernetes namespace scope of the requests. Default: default
        :param release: (experimental) The name of the release. Default: - If no release name is given, it will use the last 53 characters of the node's unique id.
        :param repository: (experimental) The repository which contains the chart. For example: https://charts.helm.sh/stable/ Default: - No repository will be used, which means that the chart needs to be an absolute URL.
        :param skip_crds: (experimental) if set, no CRDs will be installed. Default: - CRDs are installed if not already present
        :param timeout: (experimental) Amount of time to wait for any individual Kubernetes operation. Maximum 15 minutes. Default: Duration.minutes(5)
        :param values: (experimental) The values to be used by the chart. For nested values use a nested dictionary. For example: values: { installationCRDs: true, webhook: { port: 9443 } } Default: - No values are provided to the chart.
        :param version: (experimental) The chart version to install. Default: - If this is not specified, the latest version is installed
        :param wait: (experimental) Whether or not Helm should wait until all Pods, PVCs, Services, and minimum number of Pods of a Deployment, StatefulSet, or ReplicaSet are in a ready state before marking the release as successful. Default: - Helm will not wait before marking release as successful

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e2ded6c2419a82e0debe530842e0b88f5af59ae5ecfe5fa58ccf3c9665442b61)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = HelmChartProps(
            cluster=cluster,
            atomic=atomic,
            chart=chart,
            chart_asset=chart_asset,
            create_namespace=create_namespace,
            namespace=namespace,
            release=release,
            repository=repository,
            skip_crds=skip_crds,
            timeout=timeout,
            values=values,
            version=version,
            wait=wait,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @jsii.python.classproperty
    @jsii.member(jsii_name="RESOURCE_TYPE")
    def RESOURCE_TYPE(cls) -> builtins.str:
        '''(experimental) The CloudFormation resource type.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "RESOURCE_TYPE"))

    @builtins.property
    @jsii.member(jsii_name="atomic")
    def atomic(self) -> typing.Optional[builtins.bool]:
        '''
        :stability: experimental
        '''
        return typing.cast(typing.Optional[builtins.bool], jsii.get(self, "atomic"))

    @builtins.property
    @jsii.member(jsii_name="chart")
    def chart(self) -> typing.Optional[builtins.str]:
        '''
        :stability: experimental
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "chart"))

    @builtins.property
    @jsii.member(jsii_name="chartAsset")
    def chart_asset(self) -> typing.Optional[_aws_cdk_aws_s3_assets_ceddda9d.Asset]:
        '''
        :stability: experimental
        '''
        return typing.cast(typing.Optional[_aws_cdk_aws_s3_assets_ceddda9d.Asset], jsii.get(self, "chartAsset"))

    @builtins.property
    @jsii.member(jsii_name="repository")
    def repository(self) -> typing.Optional[builtins.str]:
        '''
        :stability: experimental
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "repository"))

    @builtins.property
    @jsii.member(jsii_name="version")
    def version(self) -> typing.Optional[builtins.str]:
        '''
        :stability: experimental
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "version"))


@jsii.data_type(
    jsii_type="@aws-cdk/aws-eks-v2-alpha.HelmChartOptions",
    jsii_struct_bases=[],
    name_mapping={
        "atomic": "atomic",
        "chart": "chart",
        "chart_asset": "chartAsset",
        "create_namespace": "createNamespace",
        "namespace": "namespace",
        "release": "release",
        "repository": "repository",
        "skip_crds": "skipCrds",
        "timeout": "timeout",
        "values": "values",
        "version": "version",
        "wait": "wait",
    },
)
class HelmChartOptions:
    def __init__(
        self,
        *,
        atomic: typing.Optional[builtins.bool] = None,
        chart: typing.Optional[builtins.str] = None,
        chart_asset: typing.Optional[_aws_cdk_aws_s3_assets_ceddda9d.Asset] = None,
        create_namespace: typing.Optional[builtins.bool] = None,
        namespace: typing.Optional[builtins.str] = None,
        release: typing.Optional[builtins.str] = None,
        repository: typing.Optional[builtins.str] = None,
        skip_crds: typing.Optional[builtins.bool] = None,
        timeout: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        values: typing.Optional[typing.Mapping[builtins.str, typing.Any]] = None,
        version: typing.Optional[builtins.str] = None,
        wait: typing.Optional[builtins.bool] = None,
    ) -> None:
        '''(experimental) Helm Chart options.

        :param atomic: (experimental) Whether or not Helm should treat this operation as atomic; if set, upgrade process rolls back changes made in case of failed upgrade. The --wait flag will be set automatically if --atomic is used. Default: false
        :param chart: (experimental) The name of the chart. Either this or ``chartAsset`` must be specified. Default: - No chart name. Implies ``chartAsset`` is used.
        :param chart_asset: (experimental) The chart in the form of an asset. Either this or ``chart`` must be specified. Default: - No chart asset. Implies ``chart`` is used.
        :param create_namespace: (experimental) create namespace if not exist. Default: true
        :param namespace: (experimental) The Kubernetes namespace scope of the requests. Default: default
        :param release: (experimental) The name of the release. Default: - If no release name is given, it will use the last 53 characters of the node's unique id.
        :param repository: (experimental) The repository which contains the chart. For example: https://charts.helm.sh/stable/ Default: - No repository will be used, which means that the chart needs to be an absolute URL.
        :param skip_crds: (experimental) if set, no CRDs will be installed. Default: - CRDs are installed if not already present
        :param timeout: (experimental) Amount of time to wait for any individual Kubernetes operation. Maximum 15 minutes. Default: Duration.minutes(5)
        :param values: (experimental) The values to be used by the chart. For nested values use a nested dictionary. For example: values: { installationCRDs: true, webhook: { port: 9443 } } Default: - No values are provided to the chart.
        :param version: (experimental) The chart version to install. Default: - If this is not specified, the latest version is installed
        :param wait: (experimental) Whether or not Helm should wait until all Pods, PVCs, Services, and minimum number of Pods of a Deployment, StatefulSet, or ReplicaSet are in a ready state before marking the release as successful. Default: - Helm will not wait before marking release as successful

        :stability: experimental
        :exampleMetadata: infused

        Example::

            import aws_cdk.aws_s3_assets as s3_assets
            
            # cluster: eks.Cluster
            
            chart_asset = s3_assets.Asset(self, "ChartAsset",
                path="/path/to/asset"
            )
            
            cluster.add_helm_chart("test-chart",
                chart_asset=chart_asset
            )
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__10ed29c454f002893e5586eb49b74f48903e50b690a353a03efcf7da45eb8f19)
            check_type(argname="argument atomic", value=atomic, expected_type=type_hints["atomic"])
            check_type(argname="argument chart", value=chart, expected_type=type_hints["chart"])
            check_type(argname="argument chart_asset", value=chart_asset, expected_type=type_hints["chart_asset"])
            check_type(argname="argument create_namespace", value=create_namespace, expected_type=type_hints["create_namespace"])
            check_type(argname="argument namespace", value=namespace, expected_type=type_hints["namespace"])
            check_type(argname="argument release", value=release, expected_type=type_hints["release"])
            check_type(argname="argument repository", value=repository, expected_type=type_hints["repository"])
            check_type(argname="argument skip_crds", value=skip_crds, expected_type=type_hints["skip_crds"])
            check_type(argname="argument timeout", value=timeout, expected_type=type_hints["timeout"])
            check_type(argname="argument values", value=values, expected_type=type_hints["values"])
            check_type(argname="argument version", value=version, expected_type=type_hints["version"])
            check_type(argname="argument wait", value=wait, expected_type=type_hints["wait"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if atomic is not None:
            self._values["atomic"] = atomic
        if chart is not None:
            self._values["chart"] = chart
        if chart_asset is not None:
            self._values["chart_asset"] = chart_asset
        if create_namespace is not None:
            self._values["create_namespace"] = create_namespace
        if namespace is not None:
            self._values["namespace"] = namespace
        if release is not None:
            self._values["release"] = release
        if repository is not None:
            self._values["repository"] = repository
        if skip_crds is not None:
            self._values["skip_crds"] = skip_crds
        if timeout is not None:
            self._values["timeout"] = timeout
        if values is not None:
            self._values["values"] = values
        if version is not None:
            self._values["version"] = version
        if wait is not None:
            self._values["wait"] = wait

    @builtins.property
    def atomic(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Whether or not Helm should treat this operation as atomic;

        if set, upgrade process rolls back changes
        made in case of failed upgrade. The --wait flag will be set automatically if --atomic is used.

        :default: false

        :stability: experimental
        '''
        result = self._values.get("atomic")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def chart(self) -> typing.Optional[builtins.str]:
        '''(experimental) The name of the chart.

        Either this or ``chartAsset`` must be specified.

        :default: - No chart name. Implies ``chartAsset`` is used.

        :stability: experimental
        '''
        result = self._values.get("chart")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def chart_asset(self) -> typing.Optional[_aws_cdk_aws_s3_assets_ceddda9d.Asset]:
        '''(experimental) The chart in the form of an asset.

        Either this or ``chart`` must be specified.

        :default: - No chart asset. Implies ``chart`` is used.

        :stability: experimental
        '''
        result = self._values.get("chart_asset")
        return typing.cast(typing.Optional[_aws_cdk_aws_s3_assets_ceddda9d.Asset], result)

    @builtins.property
    def create_namespace(self) -> typing.Optional[builtins.bool]:
        '''(experimental) create namespace if not exist.

        :default: true

        :stability: experimental
        '''
        result = self._values.get("create_namespace")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def namespace(self) -> typing.Optional[builtins.str]:
        '''(experimental) The Kubernetes namespace scope of the requests.

        :default: default

        :stability: experimental
        '''
        result = self._values.get("namespace")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def release(self) -> typing.Optional[builtins.str]:
        '''(experimental) The name of the release.

        :default: - If no release name is given, it will use the last 53 characters of the node's unique id.

        :stability: experimental
        '''
        result = self._values.get("release")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def repository(self) -> typing.Optional[builtins.str]:
        '''(experimental) The repository which contains the chart.

        For example: https://charts.helm.sh/stable/

        :default: - No repository will be used, which means that the chart needs to be an absolute URL.

        :stability: experimental
        '''
        result = self._values.get("repository")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def skip_crds(self) -> typing.Optional[builtins.bool]:
        '''(experimental) if set, no CRDs will be installed.

        :default: - CRDs are installed if not already present

        :stability: experimental
        '''
        result = self._values.get("skip_crds")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def timeout(self) -> typing.Optional[_aws_cdk_ceddda9d.Duration]:
        '''(experimental) Amount of time to wait for any individual Kubernetes operation.

        Maximum 15 minutes.

        :default: Duration.minutes(5)

        :stability: experimental
        '''
        result = self._values.get("timeout")
        return typing.cast(typing.Optional[_aws_cdk_ceddda9d.Duration], result)

    @builtins.property
    def values(self) -> typing.Optional[typing.Mapping[builtins.str, typing.Any]]:
        '''(experimental) The values to be used by the chart.

        For nested values use a nested dictionary. For example:
        values: {
        installationCRDs: true,
        webhook: { port: 9443 }
        }

        :default: - No values are provided to the chart.

        :stability: experimental
        '''
        result = self._values.get("values")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, typing.Any]], result)

    @builtins.property
    def version(self) -> typing.Optional[builtins.str]:
        '''(experimental) The chart version to install.

        :default: - If this is not specified, the latest version is installed

        :stability: experimental
        '''
        result = self._values.get("version")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def wait(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Whether or not Helm should wait until all Pods, PVCs, Services, and minimum number of Pods of a Deployment, StatefulSet, or ReplicaSet are in a ready state before marking the release as successful.

        :default: - Helm will not wait before marking release as successful

        :stability: experimental
        '''
        result = self._values.get("wait")
        return typing.cast(typing.Optional[builtins.bool], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "HelmChartOptions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@aws-cdk/aws-eks-v2-alpha.HelmChartProps",
    jsii_struct_bases=[HelmChartOptions],
    name_mapping={
        "atomic": "atomic",
        "chart": "chart",
        "chart_asset": "chartAsset",
        "create_namespace": "createNamespace",
        "namespace": "namespace",
        "release": "release",
        "repository": "repository",
        "skip_crds": "skipCrds",
        "timeout": "timeout",
        "values": "values",
        "version": "version",
        "wait": "wait",
        "cluster": "cluster",
    },
)
class HelmChartProps(HelmChartOptions):
    def __init__(
        self,
        *,
        atomic: typing.Optional[builtins.bool] = None,
        chart: typing.Optional[builtins.str] = None,
        chart_asset: typing.Optional[_aws_cdk_aws_s3_assets_ceddda9d.Asset] = None,
        create_namespace: typing.Optional[builtins.bool] = None,
        namespace: typing.Optional[builtins.str] = None,
        release: typing.Optional[builtins.str] = None,
        repository: typing.Optional[builtins.str] = None,
        skip_crds: typing.Optional[builtins.bool] = None,
        timeout: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        values: typing.Optional[typing.Mapping[builtins.str, typing.Any]] = None,
        version: typing.Optional[builtins.str] = None,
        wait: typing.Optional[builtins.bool] = None,
        cluster: "ICluster",
    ) -> None:
        '''(experimental) Helm Chart properties.

        :param atomic: (experimental) Whether or not Helm should treat this operation as atomic; if set, upgrade process rolls back changes made in case of failed upgrade. The --wait flag will be set automatically if --atomic is used. Default: false
        :param chart: (experimental) The name of the chart. Either this or ``chartAsset`` must be specified. Default: - No chart name. Implies ``chartAsset`` is used.
        :param chart_asset: (experimental) The chart in the form of an asset. Either this or ``chart`` must be specified. Default: - No chart asset. Implies ``chart`` is used.
        :param create_namespace: (experimental) create namespace if not exist. Default: true
        :param namespace: (experimental) The Kubernetes namespace scope of the requests. Default: default
        :param release: (experimental) The name of the release. Default: - If no release name is given, it will use the last 53 characters of the node's unique id.
        :param repository: (experimental) The repository which contains the chart. For example: https://charts.helm.sh/stable/ Default: - No repository will be used, which means that the chart needs to be an absolute URL.
        :param skip_crds: (experimental) if set, no CRDs will be installed. Default: - CRDs are installed if not already present
        :param timeout: (experimental) Amount of time to wait for any individual Kubernetes operation. Maximum 15 minutes. Default: Duration.minutes(5)
        :param values: (experimental) The values to be used by the chart. For nested values use a nested dictionary. For example: values: { installationCRDs: true, webhook: { port: 9443 } } Default: - No values are provided to the chart.
        :param version: (experimental) The chart version to install. Default: - If this is not specified, the latest version is installed
        :param wait: (experimental) Whether or not Helm should wait until all Pods, PVCs, Services, and minimum number of Pods of a Deployment, StatefulSet, or ReplicaSet are in a ready state before marking the release as successful. Default: - Helm will not wait before marking release as successful
        :param cluster: (experimental) The EKS cluster to apply this configuration to. [disable-awslint:ref-via-interface]

        :stability: experimental
        :exampleMetadata: infused

        Example::

            # cluster: eks.Cluster
            
            # option 1: use a construct
            eks.HelmChart(self, "MyOCIChart",
                cluster=cluster,
                chart="some-chart",
                repository="oci://${ACCOUNT_ID}.dkr.ecr.${ACCOUNT_REGION}.amazonaws.com/${REPO_NAME}",
                namespace="oci",
                version="0.0.1"
            )
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b8d67c7be3f3c54dd9f759c893537dddbe6975848be6b4893d2c359372a076f9)
            check_type(argname="argument atomic", value=atomic, expected_type=type_hints["atomic"])
            check_type(argname="argument chart", value=chart, expected_type=type_hints["chart"])
            check_type(argname="argument chart_asset", value=chart_asset, expected_type=type_hints["chart_asset"])
            check_type(argname="argument create_namespace", value=create_namespace, expected_type=type_hints["create_namespace"])
            check_type(argname="argument namespace", value=namespace, expected_type=type_hints["namespace"])
            check_type(argname="argument release", value=release, expected_type=type_hints["release"])
            check_type(argname="argument repository", value=repository, expected_type=type_hints["repository"])
            check_type(argname="argument skip_crds", value=skip_crds, expected_type=type_hints["skip_crds"])
            check_type(argname="argument timeout", value=timeout, expected_type=type_hints["timeout"])
            check_type(argname="argument values", value=values, expected_type=type_hints["values"])
            check_type(argname="argument version", value=version, expected_type=type_hints["version"])
            check_type(argname="argument wait", value=wait, expected_type=type_hints["wait"])
            check_type(argname="argument cluster", value=cluster, expected_type=type_hints["cluster"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "cluster": cluster,
        }
        if atomic is not None:
            self._values["atomic"] = atomic
        if chart is not None:
            self._values["chart"] = chart
        if chart_asset is not None:
            self._values["chart_asset"] = chart_asset
        if create_namespace is not None:
            self._values["create_namespace"] = create_namespace
        if namespace is not None:
            self._values["namespace"] = namespace
        if release is not None:
            self._values["release"] = release
        if repository is not None:
            self._values["repository"] = repository
        if skip_crds is not None:
            self._values["skip_crds"] = skip_crds
        if timeout is not None:
            self._values["timeout"] = timeout
        if values is not None:
            self._values["values"] = values
        if version is not None:
            self._values["version"] = version
        if wait is not None:
            self._values["wait"] = wait

    @builtins.property
    def atomic(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Whether or not Helm should treat this operation as atomic;

        if set, upgrade process rolls back changes
        made in case of failed upgrade. The --wait flag will be set automatically if --atomic is used.

        :default: false

        :stability: experimental
        '''
        result = self._values.get("atomic")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def chart(self) -> typing.Optional[builtins.str]:
        '''(experimental) The name of the chart.

        Either this or ``chartAsset`` must be specified.

        :default: - No chart name. Implies ``chartAsset`` is used.

        :stability: experimental
        '''
        result = self._values.get("chart")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def chart_asset(self) -> typing.Optional[_aws_cdk_aws_s3_assets_ceddda9d.Asset]:
        '''(experimental) The chart in the form of an asset.

        Either this or ``chart`` must be specified.

        :default: - No chart asset. Implies ``chart`` is used.

        :stability: experimental
        '''
        result = self._values.get("chart_asset")
        return typing.cast(typing.Optional[_aws_cdk_aws_s3_assets_ceddda9d.Asset], result)

    @builtins.property
    def create_namespace(self) -> typing.Optional[builtins.bool]:
        '''(experimental) create namespace if not exist.

        :default: true

        :stability: experimental
        '''
        result = self._values.get("create_namespace")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def namespace(self) -> typing.Optional[builtins.str]:
        '''(experimental) The Kubernetes namespace scope of the requests.

        :default: default

        :stability: experimental
        '''
        result = self._values.get("namespace")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def release(self) -> typing.Optional[builtins.str]:
        '''(experimental) The name of the release.

        :default: - If no release name is given, it will use the last 53 characters of the node's unique id.

        :stability: experimental
        '''
        result = self._values.get("release")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def repository(self) -> typing.Optional[builtins.str]:
        '''(experimental) The repository which contains the chart.

        For example: https://charts.helm.sh/stable/

        :default: - No repository will be used, which means that the chart needs to be an absolute URL.

        :stability: experimental
        '''
        result = self._values.get("repository")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def skip_crds(self) -> typing.Optional[builtins.bool]:
        '''(experimental) if set, no CRDs will be installed.

        :default: - CRDs are installed if not already present

        :stability: experimental
        '''
        result = self._values.get("skip_crds")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def timeout(self) -> typing.Optional[_aws_cdk_ceddda9d.Duration]:
        '''(experimental) Amount of time to wait for any individual Kubernetes operation.

        Maximum 15 minutes.

        :default: Duration.minutes(5)

        :stability: experimental
        '''
        result = self._values.get("timeout")
        return typing.cast(typing.Optional[_aws_cdk_ceddda9d.Duration], result)

    @builtins.property
    def values(self) -> typing.Optional[typing.Mapping[builtins.str, typing.Any]]:
        '''(experimental) The values to be used by the chart.

        For nested values use a nested dictionary. For example:
        values: {
        installationCRDs: true,
        webhook: { port: 9443 }
        }

        :default: - No values are provided to the chart.

        :stability: experimental
        '''
        result = self._values.get("values")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, typing.Any]], result)

    @builtins.property
    def version(self) -> typing.Optional[builtins.str]:
        '''(experimental) The chart version to install.

        :default: - If this is not specified, the latest version is installed

        :stability: experimental
        '''
        result = self._values.get("version")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def wait(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Whether or not Helm should wait until all Pods, PVCs, Services, and minimum number of Pods of a Deployment, StatefulSet, or ReplicaSet are in a ready state before marking the release as successful.

        :default: - Helm will not wait before marking release as successful

        :stability: experimental
        '''
        result = self._values.get("wait")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def cluster(self) -> "ICluster":
        '''(experimental) The EKS cluster to apply this configuration to.

        [disable-awslint:ref-via-interface]

        :stability: experimental
        '''
        result = self._values.get("cluster")
        assert result is not None, "Required property 'cluster' is missing"
        return typing.cast("ICluster", result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "HelmChartProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.interface(jsii_type="@aws-cdk/aws-eks-v2-alpha.IAccessEntry")
class IAccessEntry(_aws_cdk_ceddda9d.IResource, typing_extensions.Protocol):
    '''(experimental) Represents an access entry in an Amazon EKS cluster.

    An access entry defines the permissions and scope for a user or role to access an Amazon EKS cluster.

    :stability: experimental
    :extends: IResource *
    :interface: IAccessEntry
    :property: {string} accessEntryArn - The Amazon Resource Name (ARN) of the access entry.
    '''

    @builtins.property
    @jsii.member(jsii_name="accessEntryArn")
    def access_entry_arn(self) -> builtins.str:
        '''(experimental) The Amazon Resource Name (ARN) of the access entry.

        :stability: experimental
        :attribute: true
        '''
        ...

    @builtins.property
    @jsii.member(jsii_name="accessEntryName")
    def access_entry_name(self) -> builtins.str:
        '''(experimental) The name of the access entry.

        :stability: experimental
        :attribute: true
        '''
        ...


class _IAccessEntryProxy(
    jsii.proxy_for(_aws_cdk_ceddda9d.IResource), # type: ignore[misc]
):
    '''(experimental) Represents an access entry in an Amazon EKS cluster.

    An access entry defines the permissions and scope for a user or role to access an Amazon EKS cluster.

    :stability: experimental
    :extends: IResource *
    :interface: IAccessEntry
    :property: {string} accessEntryArn - The Amazon Resource Name (ARN) of the access entry.
    '''

    __jsii_type__: typing.ClassVar[str] = "@aws-cdk/aws-eks-v2-alpha.IAccessEntry"

    @builtins.property
    @jsii.member(jsii_name="accessEntryArn")
    def access_entry_arn(self) -> builtins.str:
        '''(experimental) The Amazon Resource Name (ARN) of the access entry.

        :stability: experimental
        :attribute: true
        '''
        return typing.cast(builtins.str, jsii.get(self, "accessEntryArn"))

    @builtins.property
    @jsii.member(jsii_name="accessEntryName")
    def access_entry_name(self) -> builtins.str:
        '''(experimental) The name of the access entry.

        :stability: experimental
        :attribute: true
        '''
        return typing.cast(builtins.str, jsii.get(self, "accessEntryName"))

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, IAccessEntry).__jsii_proxy_class__ = lambda : _IAccessEntryProxy


@jsii.interface(jsii_type="@aws-cdk/aws-eks-v2-alpha.IAccessPolicy")
class IAccessPolicy(typing_extensions.Protocol):
    '''(experimental) Represents an access policy that defines the permissions and scope for a user or role to access an Amazon EKS cluster.

    :stability: experimental
    :interface: IAccessPolicy
    '''

    @builtins.property
    @jsii.member(jsii_name="accessScope")
    def access_scope(self) -> AccessScope:
        '''(experimental) The scope of the access policy, which determines the level of access granted.

        :stability: experimental
        '''
        ...

    @builtins.property
    @jsii.member(jsii_name="policy")
    def policy(self) -> builtins.str:
        '''(experimental) The access policy itself, which defines the specific permissions.

        :stability: experimental
        '''
        ...


class _IAccessPolicyProxy:
    '''(experimental) Represents an access policy that defines the permissions and scope for a user or role to access an Amazon EKS cluster.

    :stability: experimental
    :interface: IAccessPolicy
    '''

    __jsii_type__: typing.ClassVar[str] = "@aws-cdk/aws-eks-v2-alpha.IAccessPolicy"

    @builtins.property
    @jsii.member(jsii_name="accessScope")
    def access_scope(self) -> AccessScope:
        '''(experimental) The scope of the access policy, which determines the level of access granted.

        :stability: experimental
        '''
        return typing.cast(AccessScope, jsii.get(self, "accessScope"))

    @builtins.property
    @jsii.member(jsii_name="policy")
    def policy(self) -> builtins.str:
        '''(experimental) The access policy itself, which defines the specific permissions.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "policy"))

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, IAccessPolicy).__jsii_proxy_class__ = lambda : _IAccessPolicyProxy


@jsii.interface(jsii_type="@aws-cdk/aws-eks-v2-alpha.IAddon")
class IAddon(_aws_cdk_ceddda9d.IResource, typing_extensions.Protocol):
    '''(experimental) Represents an Amazon EKS Add-On.

    :stability: experimental
    '''

    @builtins.property
    @jsii.member(jsii_name="addonArn")
    def addon_arn(self) -> builtins.str:
        '''(experimental) ARN of the Add-On.

        :stability: experimental
        :attribute: true
        '''
        ...

    @builtins.property
    @jsii.member(jsii_name="addonName")
    def addon_name(self) -> builtins.str:
        '''(experimental) Name of the Add-On.

        :stability: experimental
        :attribute: true
        '''
        ...


class _IAddonProxy(
    jsii.proxy_for(_aws_cdk_ceddda9d.IResource), # type: ignore[misc]
):
    '''(experimental) Represents an Amazon EKS Add-On.

    :stability: experimental
    '''

    __jsii_type__: typing.ClassVar[str] = "@aws-cdk/aws-eks-v2-alpha.IAddon"

    @builtins.property
    @jsii.member(jsii_name="addonArn")
    def addon_arn(self) -> builtins.str:
        '''(experimental) ARN of the Add-On.

        :stability: experimental
        :attribute: true
        '''
        return typing.cast(builtins.str, jsii.get(self, "addonArn"))

    @builtins.property
    @jsii.member(jsii_name="addonName")
    def addon_name(self) -> builtins.str:
        '''(experimental) Name of the Add-On.

        :stability: experimental
        :attribute: true
        '''
        return typing.cast(builtins.str, jsii.get(self, "addonName"))

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, IAddon).__jsii_proxy_class__ = lambda : _IAddonProxy


@jsii.interface(jsii_type="@aws-cdk/aws-eks-v2-alpha.ICluster")
class ICluster(
    _aws_cdk_ceddda9d.IResource,
    _aws_cdk_aws_ec2_ceddda9d.IConnectable,
    typing_extensions.Protocol,
):
    '''(experimental) An EKS cluster.

    :stability: experimental
    '''

    @builtins.property
    @jsii.member(jsii_name="clusterArn")
    def cluster_arn(self) -> builtins.str:
        '''(experimental) The unique ARN assigned to the service by AWS in the form of arn:aws:eks:.

        :stability: experimental
        :attribute: true
        '''
        ...

    @builtins.property
    @jsii.member(jsii_name="clusterCertificateAuthorityData")
    def cluster_certificate_authority_data(self) -> builtins.str:
        '''(experimental) The certificate-authority-data for your cluster.

        :stability: experimental
        :attribute: true
        '''
        ...

    @builtins.property
    @jsii.member(jsii_name="clusterEncryptionConfigKeyArn")
    def cluster_encryption_config_key_arn(self) -> builtins.str:
        '''(experimental) Amazon Resource Name (ARN) or alias of the customer master key (CMK).

        :stability: experimental
        :attribute: true
        '''
        ...

    @builtins.property
    @jsii.member(jsii_name="clusterEndpoint")
    def cluster_endpoint(self) -> builtins.str:
        '''(experimental) The API Server endpoint URL.

        :stability: experimental
        :attribute: true
        '''
        ...

    @builtins.property
    @jsii.member(jsii_name="clusterName")
    def cluster_name(self) -> builtins.str:
        '''(experimental) The physical name of the Cluster.

        :stability: experimental
        :attribute: true
        '''
        ...

    @builtins.property
    @jsii.member(jsii_name="clusterSecurityGroup")
    def cluster_security_group(self) -> _aws_cdk_aws_ec2_ceddda9d.ISecurityGroup:
        '''(experimental) The cluster security group that was created by Amazon EKS for the cluster.

        :stability: experimental
        :attribute: true
        '''
        ...

    @builtins.property
    @jsii.member(jsii_name="clusterSecurityGroupId")
    def cluster_security_group_id(self) -> builtins.str:
        '''(experimental) The id of the cluster security group that was created by Amazon EKS for the cluster.

        :stability: experimental
        :attribute: true
        '''
        ...

    @builtins.property
    @jsii.member(jsii_name="openIdConnectProvider")
    def open_id_connect_provider(
        self,
    ) -> _aws_cdk_aws_iam_ceddda9d.IOpenIdConnectProvider:
        '''(experimental) The Open ID Connect Provider of the cluster used to configure Service Accounts.

        :stability: experimental
        '''
        ...

    @builtins.property
    @jsii.member(jsii_name="prune")
    def prune(self) -> builtins.bool:
        '''(experimental) Indicates whether Kubernetes resources can be automatically pruned.

        When
        this is enabled (default), prune labels will be allocated and injected to
        each resource. These labels will then be used when issuing the ``kubectl apply`` operation with the ``--prune`` switch.

        :stability: experimental
        '''
        ...

    @builtins.property
    @jsii.member(jsii_name="vpc")
    def vpc(self) -> _aws_cdk_aws_ec2_ceddda9d.IVpc:
        '''(experimental) The VPC in which this Cluster was created.

        :stability: experimental
        '''
        ...

    @builtins.property
    @jsii.member(jsii_name="eksPodIdentityAgent")
    def eks_pod_identity_agent(self) -> typing.Optional[IAddon]:
        '''(experimental) The EKS Pod Identity Agent addon for the EKS cluster.

        The EKS Pod Identity Agent is responsible for managing the temporary credentials
        used by pods in the cluster to access AWS resources. It runs as a DaemonSet on
        each node and provides the necessary credentials to the pods based on their
        associated service account.

        This property returns the ``CfnAddon`` resource representing the EKS Pod Identity
        Agent addon. If the addon has not been created yet, it will be created and
        returned.

        :stability: experimental
        '''
        ...

    @builtins.property
    @jsii.member(jsii_name="ipFamily")
    def ip_family(self) -> typing.Optional["IpFamily"]:
        '''(experimental) Specify which IP family is used to assign Kubernetes pod and service IP addresses.

        :default: - IpFamily.IP_V4

        :see: https://docs.aws.amazon.com/eks/latest/APIReference/API_KubernetesNetworkConfigRequest.html#AmazonEKS-Type-KubernetesNetworkConfigRequest-ipFamily
        :stability: experimental
        '''
        ...

    @builtins.property
    @jsii.member(jsii_name="kubectlProvider")
    def kubectl_provider(self) -> typing.Optional["IKubectlProvider"]:
        '''(experimental) Kubectl Provider for issuing kubectl commands against it.

        If not defined, a default provider will be used

        :stability: experimental
        '''
        ...

    @builtins.property
    @jsii.member(jsii_name="kubectlProviderOptions")
    def kubectl_provider_options(self) -> typing.Optional["KubectlProviderOptions"]:
        '''(experimental) Options for creating the kubectl provider - a lambda function that executes ``kubectl`` and ``helm`` against the cluster.

        If defined, ``kubectlLayer`` is a required property.

        If not defined, kubectl provider will not be created by default.

        :stability: experimental
        '''
        ...

    @jsii.member(jsii_name="addCdk8sChart")
    def add_cdk8s_chart(
        self,
        id: builtins.str,
        chart: _constructs_77d1e7e8.Construct,
        *,
        ingress_alb: typing.Optional[builtins.bool] = None,
        ingress_alb_scheme: typing.Optional[AlbScheme] = None,
        prune: typing.Optional[builtins.bool] = None,
        skip_validation: typing.Optional[builtins.bool] = None,
    ) -> "KubernetesManifest":
        '''(experimental) Defines a CDK8s chart in this cluster.

        :param id: logical id of this chart.
        :param chart: the cdk8s chart.
        :param ingress_alb: (experimental) Automatically detect ``Ingress`` resources in the manifest and annotate them so they are picked up by an ALB Ingress Controller. Default: false
        :param ingress_alb_scheme: (experimental) Specify the ALB scheme that should be applied to ``Ingress`` resources. Only applicable if ``ingressAlb`` is set to ``true``. Default: AlbScheme.INTERNAL
        :param prune: (experimental) When a resource is removed from a Kubernetes manifest, it no longer appears in the manifest, and there is no way to know that this resource needs to be deleted. To address this, ``kubectl apply`` has a ``--prune`` option which will query the cluster for all resources with a specific label and will remove all the labeld resources that are not part of the applied manifest. If this option is disabled and a resource is removed, it will become "orphaned" and will not be deleted from the cluster. When this option is enabled (default), the construct will inject a label to all Kubernetes resources included in this manifest which will be used to prune resources when the manifest changes via ``kubectl apply --prune``. The label name will be ``aws.cdk.eks/prune-<ADDR>`` where ``<ADDR>`` is the 42-char unique address of this construct in the construct tree. Value is empty. Default: - based on the prune option of the cluster, which is ``true`` unless otherwise specified.
        :param skip_validation: (experimental) A flag to signify if the manifest validation should be skipped. Default: false

        :return: a ``KubernetesManifest`` construct representing the chart.

        :stability: experimental
        '''
        ...

    @jsii.member(jsii_name="addHelmChart")
    def add_helm_chart(
        self,
        id: builtins.str,
        *,
        atomic: typing.Optional[builtins.bool] = None,
        chart: typing.Optional[builtins.str] = None,
        chart_asset: typing.Optional[_aws_cdk_aws_s3_assets_ceddda9d.Asset] = None,
        create_namespace: typing.Optional[builtins.bool] = None,
        namespace: typing.Optional[builtins.str] = None,
        release: typing.Optional[builtins.str] = None,
        repository: typing.Optional[builtins.str] = None,
        skip_crds: typing.Optional[builtins.bool] = None,
        timeout: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        values: typing.Optional[typing.Mapping[builtins.str, typing.Any]] = None,
        version: typing.Optional[builtins.str] = None,
        wait: typing.Optional[builtins.bool] = None,
    ) -> HelmChart:
        '''(experimental) Defines a Helm chart in this cluster.

        :param id: logical id of this chart.
        :param atomic: (experimental) Whether or not Helm should treat this operation as atomic; if set, upgrade process rolls back changes made in case of failed upgrade. The --wait flag will be set automatically if --atomic is used. Default: false
        :param chart: (experimental) The name of the chart. Either this or ``chartAsset`` must be specified. Default: - No chart name. Implies ``chartAsset`` is used.
        :param chart_asset: (experimental) The chart in the form of an asset. Either this or ``chart`` must be specified. Default: - No chart asset. Implies ``chart`` is used.
        :param create_namespace: (experimental) create namespace if not exist. Default: true
        :param namespace: (experimental) The Kubernetes namespace scope of the requests. Default: default
        :param release: (experimental) The name of the release. Default: - If no release name is given, it will use the last 53 characters of the node's unique id.
        :param repository: (experimental) The repository which contains the chart. For example: https://charts.helm.sh/stable/ Default: - No repository will be used, which means that the chart needs to be an absolute URL.
        :param skip_crds: (experimental) if set, no CRDs will be installed. Default: - CRDs are installed if not already present
        :param timeout: (experimental) Amount of time to wait for any individual Kubernetes operation. Maximum 15 minutes. Default: Duration.minutes(5)
        :param values: (experimental) The values to be used by the chart. For nested values use a nested dictionary. For example: values: { installationCRDs: true, webhook: { port: 9443 } } Default: - No values are provided to the chart.
        :param version: (experimental) The chart version to install. Default: - If this is not specified, the latest version is installed
        :param wait: (experimental) Whether or not Helm should wait until all Pods, PVCs, Services, and minimum number of Pods of a Deployment, StatefulSet, or ReplicaSet are in a ready state before marking the release as successful. Default: - Helm will not wait before marking release as successful

        :return: a ``HelmChart`` construct

        :stability: experimental
        '''
        ...

    @jsii.member(jsii_name="addManifest")
    def add_manifest(
        self,
        id: builtins.str,
        *manifest: typing.Mapping[builtins.str, typing.Any],
    ) -> "KubernetesManifest":
        '''(experimental) Defines a Kubernetes resource in this cluster.

        The manifest will be applied/deleted using kubectl as needed.

        :param id: logical id of this manifest.
        :param manifest: a list of Kubernetes resource specifications.

        :return: a ``KubernetesManifest`` object.

        :stability: experimental
        '''
        ...

    @jsii.member(jsii_name="addServiceAccount")
    def add_service_account(
        self,
        id: builtins.str,
        *,
        annotations: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        identity_type: typing.Optional["IdentityType"] = None,
        labels: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        name: typing.Optional[builtins.str] = None,
        namespace: typing.Optional[builtins.str] = None,
    ) -> "ServiceAccount":
        '''(experimental) Creates a new service account with corresponding IAM Role (IRSA).

        :param id: logical id of service account.
        :param annotations: (experimental) Additional annotations of the service account. Default: - no additional annotations
        :param identity_type: (experimental) The identity type to use for the service account. Default: IdentityType.IRSA
        :param labels: (experimental) Additional labels of the service account. Default: - no additional labels
        :param name: (experimental) The name of the service account. The name of a ServiceAccount object must be a valid DNS subdomain name. https://kubernetes.io/docs/tasks/configure-pod-container/configure-service-account/ Default: - If no name is given, it will use the id of the resource.
        :param namespace: (experimental) The namespace of the service account. All namespace names must be valid RFC 1123 DNS labels. https://kubernetes.io/docs/concepts/overview/working-with-objects/namespaces/#namespaces-and-dns Default: "default"

        :stability: experimental
        '''
        ...

    @jsii.member(jsii_name="connectAutoScalingGroupCapacity")
    def connect_auto_scaling_group_capacity(
        self,
        auto_scaling_group: _aws_cdk_aws_autoscaling_ceddda9d.AutoScalingGroup,
        *,
        bootstrap_enabled: typing.Optional[builtins.bool] = None,
        bootstrap_options: typing.Optional[typing.Union[BootstrapOptions, typing.Dict[builtins.str, typing.Any]]] = None,
        machine_image_type: typing.Optional["MachineImageType"] = None,
    ) -> None:
        '''(experimental) Connect capacity in the form of an existing AutoScalingGroup to the EKS cluster.

        The AutoScalingGroup must be running an EKS-optimized AMI containing the
        /etc/eks/bootstrap.sh script. This method will configure Security Groups,
        add the right policies to the instance role, apply the right tags, and add
        the required user data to the instance's launch configuration.

        Prefer to use ``addAutoScalingGroupCapacity`` if possible.

        :param auto_scaling_group: [disable-awslint:ref-via-interface].
        :param bootstrap_enabled: (experimental) Configures the EC2 user-data script for instances in this autoscaling group to bootstrap the node (invoke ``/etc/eks/bootstrap.sh``) and associate it with the EKS cluster. If you wish to provide a custom user data script, set this to ``false`` and manually invoke ``autoscalingGroup.addUserData()``. Default: true
        :param bootstrap_options: (experimental) Allows options for node bootstrapping through EC2 user data. Default: - default options
        :param machine_image_type: (experimental) Allow options to specify different machine image type. Default: MachineImageType.AMAZON_LINUX_2

        :see: https://docs.aws.amazon.com/eks/latest/userguide/launch-workers.html
        :stability: experimental
        '''
        ...


class _IClusterProxy(
    jsii.proxy_for(_aws_cdk_ceddda9d.IResource), # type: ignore[misc]
    jsii.proxy_for(_aws_cdk_aws_ec2_ceddda9d.IConnectable), # type: ignore[misc]
):
    '''(experimental) An EKS cluster.

    :stability: experimental
    '''

    __jsii_type__: typing.ClassVar[str] = "@aws-cdk/aws-eks-v2-alpha.ICluster"

    @builtins.property
    @jsii.member(jsii_name="clusterArn")
    def cluster_arn(self) -> builtins.str:
        '''(experimental) The unique ARN assigned to the service by AWS in the form of arn:aws:eks:.

        :stability: experimental
        :attribute: true
        '''
        return typing.cast(builtins.str, jsii.get(self, "clusterArn"))

    @builtins.property
    @jsii.member(jsii_name="clusterCertificateAuthorityData")
    def cluster_certificate_authority_data(self) -> builtins.str:
        '''(experimental) The certificate-authority-data for your cluster.

        :stability: experimental
        :attribute: true
        '''
        return typing.cast(builtins.str, jsii.get(self, "clusterCertificateAuthorityData"))

    @builtins.property
    @jsii.member(jsii_name="clusterEncryptionConfigKeyArn")
    def cluster_encryption_config_key_arn(self) -> builtins.str:
        '''(experimental) Amazon Resource Name (ARN) or alias of the customer master key (CMK).

        :stability: experimental
        :attribute: true
        '''
        return typing.cast(builtins.str, jsii.get(self, "clusterEncryptionConfigKeyArn"))

    @builtins.property
    @jsii.member(jsii_name="clusterEndpoint")
    def cluster_endpoint(self) -> builtins.str:
        '''(experimental) The API Server endpoint URL.

        :stability: experimental
        :attribute: true
        '''
        return typing.cast(builtins.str, jsii.get(self, "clusterEndpoint"))

    @builtins.property
    @jsii.member(jsii_name="clusterName")
    def cluster_name(self) -> builtins.str:
        '''(experimental) The physical name of the Cluster.

        :stability: experimental
        :attribute: true
        '''
        return typing.cast(builtins.str, jsii.get(self, "clusterName"))

    @builtins.property
    @jsii.member(jsii_name="clusterSecurityGroup")
    def cluster_security_group(self) -> _aws_cdk_aws_ec2_ceddda9d.ISecurityGroup:
        '''(experimental) The cluster security group that was created by Amazon EKS for the cluster.

        :stability: experimental
        :attribute: true
        '''
        return typing.cast(_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup, jsii.get(self, "clusterSecurityGroup"))

    @builtins.property
    @jsii.member(jsii_name="clusterSecurityGroupId")
    def cluster_security_group_id(self) -> builtins.str:
        '''(experimental) The id of the cluster security group that was created by Amazon EKS for the cluster.

        :stability: experimental
        :attribute: true
        '''
        return typing.cast(builtins.str, jsii.get(self, "clusterSecurityGroupId"))

    @builtins.property
    @jsii.member(jsii_name="openIdConnectProvider")
    def open_id_connect_provider(
        self,
    ) -> _aws_cdk_aws_iam_ceddda9d.IOpenIdConnectProvider:
        '''(experimental) The Open ID Connect Provider of the cluster used to configure Service Accounts.

        :stability: experimental
        '''
        return typing.cast(_aws_cdk_aws_iam_ceddda9d.IOpenIdConnectProvider, jsii.get(self, "openIdConnectProvider"))

    @builtins.property
    @jsii.member(jsii_name="prune")
    def prune(self) -> builtins.bool:
        '''(experimental) Indicates whether Kubernetes resources can be automatically pruned.

        When
        this is enabled (default), prune labels will be allocated and injected to
        each resource. These labels will then be used when issuing the ``kubectl apply`` operation with the ``--prune`` switch.

        :stability: experimental
        '''
        return typing.cast(builtins.bool, jsii.get(self, "prune"))

    @builtins.property
    @jsii.member(jsii_name="vpc")
    def vpc(self) -> _aws_cdk_aws_ec2_ceddda9d.IVpc:
        '''(experimental) The VPC in which this Cluster was created.

        :stability: experimental
        '''
        return typing.cast(_aws_cdk_aws_ec2_ceddda9d.IVpc, jsii.get(self, "vpc"))

    @builtins.property
    @jsii.member(jsii_name="eksPodIdentityAgent")
    def eks_pod_identity_agent(self) -> typing.Optional[IAddon]:
        '''(experimental) The EKS Pod Identity Agent addon for the EKS cluster.

        The EKS Pod Identity Agent is responsible for managing the temporary credentials
        used by pods in the cluster to access AWS resources. It runs as a DaemonSet on
        each node and provides the necessary credentials to the pods based on their
        associated service account.

        This property returns the ``CfnAddon`` resource representing the EKS Pod Identity
        Agent addon. If the addon has not been created yet, it will be created and
        returned.

        :stability: experimental
        '''
        return typing.cast(typing.Optional[IAddon], jsii.get(self, "eksPodIdentityAgent"))

    @builtins.property
    @jsii.member(jsii_name="ipFamily")
    def ip_family(self) -> typing.Optional["IpFamily"]:
        '''(experimental) Specify which IP family is used to assign Kubernetes pod and service IP addresses.

        :default: - IpFamily.IP_V4

        :see: https://docs.aws.amazon.com/eks/latest/APIReference/API_KubernetesNetworkConfigRequest.html#AmazonEKS-Type-KubernetesNetworkConfigRequest-ipFamily
        :stability: experimental
        '''
        return typing.cast(typing.Optional["IpFamily"], jsii.get(self, "ipFamily"))

    @builtins.property
    @jsii.member(jsii_name="kubectlProvider")
    def kubectl_provider(self) -> typing.Optional["IKubectlProvider"]:
        '''(experimental) Kubectl Provider for issuing kubectl commands against it.

        If not defined, a default provider will be used

        :stability: experimental
        '''
        return typing.cast(typing.Optional["IKubectlProvider"], jsii.get(self, "kubectlProvider"))

    @builtins.property
    @jsii.member(jsii_name="kubectlProviderOptions")
    def kubectl_provider_options(self) -> typing.Optional["KubectlProviderOptions"]:
        '''(experimental) Options for creating the kubectl provider - a lambda function that executes ``kubectl`` and ``helm`` against the cluster.

        If defined, ``kubectlLayer`` is a required property.

        If not defined, kubectl provider will not be created by default.

        :stability: experimental
        '''
        return typing.cast(typing.Optional["KubectlProviderOptions"], jsii.get(self, "kubectlProviderOptions"))

    @jsii.member(jsii_name="addCdk8sChart")
    def add_cdk8s_chart(
        self,
        id: builtins.str,
        chart: _constructs_77d1e7e8.Construct,
        *,
        ingress_alb: typing.Optional[builtins.bool] = None,
        ingress_alb_scheme: typing.Optional[AlbScheme] = None,
        prune: typing.Optional[builtins.bool] = None,
        skip_validation: typing.Optional[builtins.bool] = None,
    ) -> "KubernetesManifest":
        '''(experimental) Defines a CDK8s chart in this cluster.

        :param id: logical id of this chart.
        :param chart: the cdk8s chart.
        :param ingress_alb: (experimental) Automatically detect ``Ingress`` resources in the manifest and annotate them so they are picked up by an ALB Ingress Controller. Default: false
        :param ingress_alb_scheme: (experimental) Specify the ALB scheme that should be applied to ``Ingress`` resources. Only applicable if ``ingressAlb`` is set to ``true``. Default: AlbScheme.INTERNAL
        :param prune: (experimental) When a resource is removed from a Kubernetes manifest, it no longer appears in the manifest, and there is no way to know that this resource needs to be deleted. To address this, ``kubectl apply`` has a ``--prune`` option which will query the cluster for all resources with a specific label and will remove all the labeld resources that are not part of the applied manifest. If this option is disabled and a resource is removed, it will become "orphaned" and will not be deleted from the cluster. When this option is enabled (default), the construct will inject a label to all Kubernetes resources included in this manifest which will be used to prune resources when the manifest changes via ``kubectl apply --prune``. The label name will be ``aws.cdk.eks/prune-<ADDR>`` where ``<ADDR>`` is the 42-char unique address of this construct in the construct tree. Value is empty. Default: - based on the prune option of the cluster, which is ``true`` unless otherwise specified.
        :param skip_validation: (experimental) A flag to signify if the manifest validation should be skipped. Default: false

        :return: a ``KubernetesManifest`` construct representing the chart.

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f459ac98d924ed6307c30338ff2aa989532034bca8648f0d213388ac6fa624ea)
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument chart", value=chart, expected_type=type_hints["chart"])
        options = KubernetesManifestOptions(
            ingress_alb=ingress_alb,
            ingress_alb_scheme=ingress_alb_scheme,
            prune=prune,
            skip_validation=skip_validation,
        )

        return typing.cast("KubernetesManifest", jsii.invoke(self, "addCdk8sChart", [id, chart, options]))

    @jsii.member(jsii_name="addHelmChart")
    def add_helm_chart(
        self,
        id: builtins.str,
        *,
        atomic: typing.Optional[builtins.bool] = None,
        chart: typing.Optional[builtins.str] = None,
        chart_asset: typing.Optional[_aws_cdk_aws_s3_assets_ceddda9d.Asset] = None,
        create_namespace: typing.Optional[builtins.bool] = None,
        namespace: typing.Optional[builtins.str] = None,
        release: typing.Optional[builtins.str] = None,
        repository: typing.Optional[builtins.str] = None,
        skip_crds: typing.Optional[builtins.bool] = None,
        timeout: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        values: typing.Optional[typing.Mapping[builtins.str, typing.Any]] = None,
        version: typing.Optional[builtins.str] = None,
        wait: typing.Optional[builtins.bool] = None,
    ) -> HelmChart:
        '''(experimental) Defines a Helm chart in this cluster.

        :param id: logical id of this chart.
        :param atomic: (experimental) Whether or not Helm should treat this operation as atomic; if set, upgrade process rolls back changes made in case of failed upgrade. The --wait flag will be set automatically if --atomic is used. Default: false
        :param chart: (experimental) The name of the chart. Either this or ``chartAsset`` must be specified. Default: - No chart name. Implies ``chartAsset`` is used.
        :param chart_asset: (experimental) The chart in the form of an asset. Either this or ``chart`` must be specified. Default: - No chart asset. Implies ``chart`` is used.
        :param create_namespace: (experimental) create namespace if not exist. Default: true
        :param namespace: (experimental) The Kubernetes namespace scope of the requests. Default: default
        :param release: (experimental) The name of the release. Default: - If no release name is given, it will use the last 53 characters of the node's unique id.
        :param repository: (experimental) The repository which contains the chart. For example: https://charts.helm.sh/stable/ Default: - No repository will be used, which means that the chart needs to be an absolute URL.
        :param skip_crds: (experimental) if set, no CRDs will be installed. Default: - CRDs are installed if not already present
        :param timeout: (experimental) Amount of time to wait for any individual Kubernetes operation. Maximum 15 minutes. Default: Duration.minutes(5)
        :param values: (experimental) The values to be used by the chart. For nested values use a nested dictionary. For example: values: { installationCRDs: true, webhook: { port: 9443 } } Default: - No values are provided to the chart.
        :param version: (experimental) The chart version to install. Default: - If this is not specified, the latest version is installed
        :param wait: (experimental) Whether or not Helm should wait until all Pods, PVCs, Services, and minimum number of Pods of a Deployment, StatefulSet, or ReplicaSet are in a ready state before marking the release as successful. Default: - Helm will not wait before marking release as successful

        :return: a ``HelmChart`` construct

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__52256e6c30e726782e2fe2c664d6fe326d73b190eff84afda390022980e9565a)
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        options = HelmChartOptions(
            atomic=atomic,
            chart=chart,
            chart_asset=chart_asset,
            create_namespace=create_namespace,
            namespace=namespace,
            release=release,
            repository=repository,
            skip_crds=skip_crds,
            timeout=timeout,
            values=values,
            version=version,
            wait=wait,
        )

        return typing.cast(HelmChart, jsii.invoke(self, "addHelmChart", [id, options]))

    @jsii.member(jsii_name="addManifest")
    def add_manifest(
        self,
        id: builtins.str,
        *manifest: typing.Mapping[builtins.str, typing.Any],
    ) -> "KubernetesManifest":
        '''(experimental) Defines a Kubernetes resource in this cluster.

        The manifest will be applied/deleted using kubectl as needed.

        :param id: logical id of this manifest.
        :param manifest: a list of Kubernetes resource specifications.

        :return: a ``KubernetesManifest`` object.

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__60918ce77747e9408d3a9d728c009990501845848cdfc39f8b7a0bcd4166d8f7)
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument manifest", value=manifest, expected_type=typing.Tuple[type_hints["manifest"], ...]) # pyright: ignore [reportGeneralTypeIssues]
        return typing.cast("KubernetesManifest", jsii.invoke(self, "addManifest", [id, *manifest]))

    @jsii.member(jsii_name="addServiceAccount")
    def add_service_account(
        self,
        id: builtins.str,
        *,
        annotations: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        identity_type: typing.Optional["IdentityType"] = None,
        labels: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        name: typing.Optional[builtins.str] = None,
        namespace: typing.Optional[builtins.str] = None,
    ) -> "ServiceAccount":
        '''(experimental) Creates a new service account with corresponding IAM Role (IRSA).

        :param id: logical id of service account.
        :param annotations: (experimental) Additional annotations of the service account. Default: - no additional annotations
        :param identity_type: (experimental) The identity type to use for the service account. Default: IdentityType.IRSA
        :param labels: (experimental) Additional labels of the service account. Default: - no additional labels
        :param name: (experimental) The name of the service account. The name of a ServiceAccount object must be a valid DNS subdomain name. https://kubernetes.io/docs/tasks/configure-pod-container/configure-service-account/ Default: - If no name is given, it will use the id of the resource.
        :param namespace: (experimental) The namespace of the service account. All namespace names must be valid RFC 1123 DNS labels. https://kubernetes.io/docs/concepts/overview/working-with-objects/namespaces/#namespaces-and-dns Default: "default"

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__54c7d27762cad0e201d56f32d63c9ea04e919c371197f80bb76628ae8827fca4)
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        options = ServiceAccountOptions(
            annotations=annotations,
            identity_type=identity_type,
            labels=labels,
            name=name,
            namespace=namespace,
        )

        return typing.cast("ServiceAccount", jsii.invoke(self, "addServiceAccount", [id, options]))

    @jsii.member(jsii_name="connectAutoScalingGroupCapacity")
    def connect_auto_scaling_group_capacity(
        self,
        auto_scaling_group: _aws_cdk_aws_autoscaling_ceddda9d.AutoScalingGroup,
        *,
        bootstrap_enabled: typing.Optional[builtins.bool] = None,
        bootstrap_options: typing.Optional[typing.Union[BootstrapOptions, typing.Dict[builtins.str, typing.Any]]] = None,
        machine_image_type: typing.Optional["MachineImageType"] = None,
    ) -> None:
        '''(experimental) Connect capacity in the form of an existing AutoScalingGroup to the EKS cluster.

        The AutoScalingGroup must be running an EKS-optimized AMI containing the
        /etc/eks/bootstrap.sh script. This method will configure Security Groups,
        add the right policies to the instance role, apply the right tags, and add
        the required user data to the instance's launch configuration.

        Prefer to use ``addAutoScalingGroupCapacity`` if possible.

        :param auto_scaling_group: [disable-awslint:ref-via-interface].
        :param bootstrap_enabled: (experimental) Configures the EC2 user-data script for instances in this autoscaling group to bootstrap the node (invoke ``/etc/eks/bootstrap.sh``) and associate it with the EKS cluster. If you wish to provide a custom user data script, set this to ``false`` and manually invoke ``autoscalingGroup.addUserData()``. Default: true
        :param bootstrap_options: (experimental) Allows options for node bootstrapping through EC2 user data. Default: - default options
        :param machine_image_type: (experimental) Allow options to specify different machine image type. Default: MachineImageType.AMAZON_LINUX_2

        :see: https://docs.aws.amazon.com/eks/latest/userguide/launch-workers.html
        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ae7e85ee5fe1351899045b2f6a355bd8e6513d98bf420901c3f7e9e06d7b60ae)
            check_type(argname="argument auto_scaling_group", value=auto_scaling_group, expected_type=type_hints["auto_scaling_group"])
        options = AutoScalingGroupOptions(
            bootstrap_enabled=bootstrap_enabled,
            bootstrap_options=bootstrap_options,
            machine_image_type=machine_image_type,
        )

        return typing.cast(None, jsii.invoke(self, "connectAutoScalingGroupCapacity", [auto_scaling_group, options]))

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, ICluster).__jsii_proxy_class__ = lambda : _IClusterProxy


@jsii.interface(jsii_type="@aws-cdk/aws-eks-v2-alpha.IKubectlProvider")
class IKubectlProvider(_constructs_77d1e7e8.IConstruct, typing_extensions.Protocol):
    '''(experimental) Imported KubectlProvider that can be used in place of the default one created by CDK.

    :stability: experimental
    '''

    @builtins.property
    @jsii.member(jsii_name="serviceToken")
    def service_token(self) -> builtins.str:
        '''(experimental) The custom resource provider's service token.

        :stability: experimental
        '''
        ...

    @builtins.property
    @jsii.member(jsii_name="role")
    def role(self) -> typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole]:
        '''(experimental) The role of the provider lambda function.

        If undefined,
        you cannot use this provider to deploy helm charts.

        :stability: experimental
        '''
        ...


class _IKubectlProviderProxy(
    jsii.proxy_for(_constructs_77d1e7e8.IConstruct), # type: ignore[misc]
):
    '''(experimental) Imported KubectlProvider that can be used in place of the default one created by CDK.

    :stability: experimental
    '''

    __jsii_type__: typing.ClassVar[str] = "@aws-cdk/aws-eks-v2-alpha.IKubectlProvider"

    @builtins.property
    @jsii.member(jsii_name="serviceToken")
    def service_token(self) -> builtins.str:
        '''(experimental) The custom resource provider's service token.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "serviceToken"))

    @builtins.property
    @jsii.member(jsii_name="role")
    def role(self) -> typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole]:
        '''(experimental) The role of the provider lambda function.

        If undefined,
        you cannot use this provider to deploy helm charts.

        :stability: experimental
        '''
        return typing.cast(typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole], jsii.get(self, "role"))

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, IKubectlProvider).__jsii_proxy_class__ = lambda : _IKubectlProviderProxy


@jsii.interface(jsii_type="@aws-cdk/aws-eks-v2-alpha.INodegroup")
class INodegroup(_aws_cdk_ceddda9d.IResource, typing_extensions.Protocol):
    '''(experimental) NodeGroup interface.

    :stability: experimental
    '''

    @builtins.property
    @jsii.member(jsii_name="nodegroupName")
    def nodegroup_name(self) -> builtins.str:
        '''(experimental) Name of the nodegroup.

        :stability: experimental
        :attribute: true
        '''
        ...


class _INodegroupProxy(
    jsii.proxy_for(_aws_cdk_ceddda9d.IResource), # type: ignore[misc]
):
    '''(experimental) NodeGroup interface.

    :stability: experimental
    '''

    __jsii_type__: typing.ClassVar[str] = "@aws-cdk/aws-eks-v2-alpha.INodegroup"

    @builtins.property
    @jsii.member(jsii_name="nodegroupName")
    def nodegroup_name(self) -> builtins.str:
        '''(experimental) Name of the nodegroup.

        :stability: experimental
        :attribute: true
        '''
        return typing.cast(builtins.str, jsii.get(self, "nodegroupName"))

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, INodegroup).__jsii_proxy_class__ = lambda : _INodegroupProxy


@jsii.enum(jsii_type="@aws-cdk/aws-eks-v2-alpha.IdentityType")
class IdentityType(enum.Enum):
    '''(experimental) Enum representing the different identity types that can be used for a Kubernetes service account.

    :stability: experimental
    '''

    IRSA = "IRSA"
    '''(experimental) Use the IAM Roles for Service Accounts (IRSA) identity type.

    IRSA allows you to associate an IAM role with a Kubernetes service account.
    This provides a way to grant permissions to Kubernetes pods by associating an IAM role with a Kubernetes service account.
    The IAM role can then be used to provide AWS credentials to the pods, allowing them to access other AWS resources.

    When enabled, the openIdConnectProvider of the cluster would be created when you create the ServiceAccount.

    :see: https://docs.aws.amazon.com/eks/latest/userguide/iam-roles-for-service-accounts.html
    :stability: experimental
    '''
    POD_IDENTITY = "POD_IDENTITY"
    '''(experimental) Use the EKS Pod Identities identity type.

    EKS Pod Identities provide the ability to manage credentials for your applications, similar to the way that Amazon EC2 instance profiles
    provide credentials to Amazon EC2 instances. Instead of creating and distributing your AWS credentials to the containers or using the
    Amazon EC2 instance's role, you associate an IAM role with a Kubernetes service account and configure your Pods to use the service account.

    When enabled, the Pod Identity Agent AddOn of the cluster would be created when you create the ServiceAccount.

    :see: https://docs.aws.amazon.com/eks/latest/userguide/pod-identities.html
    :stability: experimental
    '''


@jsii.enum(jsii_type="@aws-cdk/aws-eks-v2-alpha.IpFamily")
class IpFamily(enum.Enum):
    '''(experimental) EKS cluster IP family.

    :stability: experimental
    '''

    IP_V4 = "IP_V4"
    '''(experimental) Use IPv4 for pods and services in your cluster.

    :stability: experimental
    '''
    IP_V6 = "IP_V6"
    '''(experimental) Use IPv6 for pods and services in your cluster.

    :stability: experimental
    '''


@jsii.implements(IKubectlProvider)
class KubectlProvider(
    _constructs_77d1e7e8.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="@aws-cdk/aws-eks-v2-alpha.KubectlProvider",
):
    '''(experimental) Implementation of Kubectl Lambda.

    :stability: experimental
    :exampleMetadata: infused

    Example::

        handler_role = iam.Role.from_role_arn(self, "HandlerRole", "arn:aws:iam::123456789012:role/lambda-role")
        # get the serivceToken from the custom resource provider
        function_arn = lambda_.Function.from_function_name(self, "ProviderOnEventFunc", "ProviderframeworkonEvent-XXX").function_arn
        kubectl_provider = eks.KubectlProvider.from_kubectl_provider_attributes(self, "KubectlProvider",
            service_token=function_arn,
            role=handler_role
        )
        
        cluster = eks.Cluster.from_cluster_attributes(self, "Cluster",
            cluster_name="cluster",
            kubectl_provider=kubectl_provider
        )
    '''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        cluster: ICluster,
        kubectl_layer: _aws_cdk_aws_lambda_ceddda9d.ILayerVersion,
        awscli_layer: typing.Optional[_aws_cdk_aws_lambda_ceddda9d.ILayerVersion] = None,
        environment: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        memory: typing.Optional[_aws_cdk_ceddda9d.Size] = None,
        private_subnets: typing.Optional[typing.Sequence[_aws_cdk_aws_ec2_ceddda9d.ISubnet]] = None,
        role: typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole] = None,
        security_group: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param cluster: (experimental) The cluster to control.
        :param kubectl_layer: (experimental) An AWS Lambda layer that includes ``kubectl`` and ``helm``.
        :param awscli_layer: (experimental) An AWS Lambda layer that contains the ``aws`` CLI. If not defined, a default layer will be used containing the AWS CLI 2.x.
        :param environment: (experimental) Custom environment variables when running ``kubectl`` against this cluster.
        :param memory: (experimental) The amount of memory allocated to the kubectl provider's lambda function.
        :param private_subnets: (experimental) Subnets to host the ``kubectl`` compute resources. If not specified, the k8s endpoint is expected to be accessible publicly.
        :param role: (experimental) An IAM role that can perform kubectl operations against this cluster. The role should be mapped to the ``system:masters`` Kubernetes RBAC role. This role is directly passed to the lambda handler that sends Kube Ctl commands to the cluster. Default: - if not specified, the default role created by a lambda function will be used.
        :param security_group: (experimental) A security group to use for ``kubectl`` execution. Default: - If not specified, the k8s endpoint is expected to be accessible publicly.

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2727744972a89db9aea3f964a70a4c06bff58e13dbaf1fadf0d01bd8c4807569)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = KubectlProviderProps(
            cluster=cluster,
            kubectl_layer=kubectl_layer,
            awscli_layer=awscli_layer,
            environment=environment,
            memory=memory,
            private_subnets=private_subnets,
            role=role,
            security_group=security_group,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @jsii.member(jsii_name="fromKubectlProviderAttributes")
    @builtins.classmethod
    def from_kubectl_provider_attributes(
        cls,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        service_token: builtins.str,
        role: typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole] = None,
    ) -> IKubectlProvider:
        '''(experimental) Import an existing provider.

        :param scope: Construct.
        :param id: an id of resource.
        :param service_token: (experimental) The kubectl provider lambda arn.
        :param role: (experimental) The role of the provider lambda function. Only required if you deploy helm charts using this imported provider. Default: - no role.

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d01c897b7d6625a93468ddad4e123eb600739f04d7e53af0cccd0459dccff9ee)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        attrs = KubectlProviderAttributes(service_token=service_token, role=role)

        return typing.cast(IKubectlProvider, jsii.sinvoke(cls, "fromKubectlProviderAttributes", [scope, id, attrs]))

    @jsii.member(jsii_name="getKubectlProvider")
    @builtins.classmethod
    def get_kubectl_provider(
        cls,
        scope: _constructs_77d1e7e8.Construct,
        cluster: ICluster,
    ) -> typing.Optional[IKubectlProvider]:
        '''(experimental) Take existing provider on cluster.

        :param scope: Construct.
        :param cluster: k8s cluster.

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5f0476065e77a8fff5af95995870110c067c55720127c4719f2ef78397a74418)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument cluster", value=cluster, expected_type=type_hints["cluster"])
        return typing.cast(typing.Optional[IKubectlProvider], jsii.sinvoke(cls, "getKubectlProvider", [scope, cluster]))

    @builtins.property
    @jsii.member(jsii_name="serviceToken")
    def service_token(self) -> builtins.str:
        '''(experimental) The custom resource provider's service token.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "serviceToken"))

    @builtins.property
    @jsii.member(jsii_name="role")
    def role(self) -> typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole]:
        '''(experimental) The IAM execution role of the handler.

        :stability: experimental
        '''
        return typing.cast(typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole], jsii.get(self, "role"))


@jsii.data_type(
    jsii_type="@aws-cdk/aws-eks-v2-alpha.KubectlProviderAttributes",
    jsii_struct_bases=[],
    name_mapping={"service_token": "serviceToken", "role": "role"},
)
class KubectlProviderAttributes:
    def __init__(
        self,
        *,
        service_token: builtins.str,
        role: typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole] = None,
    ) -> None:
        '''(experimental) Kubectl Provider Attributes.

        :param service_token: (experimental) The kubectl provider lambda arn.
        :param role: (experimental) The role of the provider lambda function. Only required if you deploy helm charts using this imported provider. Default: - no role.

        :stability: experimental
        :exampleMetadata: infused

        Example::

            handler_role = iam.Role.from_role_arn(self, "HandlerRole", "arn:aws:iam::123456789012:role/lambda-role")
            # get the serivceToken from the custom resource provider
            function_arn = lambda_.Function.from_function_name(self, "ProviderOnEventFunc", "ProviderframeworkonEvent-XXX").function_arn
            kubectl_provider = eks.KubectlProvider.from_kubectl_provider_attributes(self, "KubectlProvider",
                service_token=function_arn,
                role=handler_role
            )
            
            cluster = eks.Cluster.from_cluster_attributes(self, "Cluster",
                cluster_name="cluster",
                kubectl_provider=kubectl_provider
            )
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__43b2bf79b275491320586dc0b1c56ce24a179ad7f0a6e5dec512ed8b26df6e6f)
            check_type(argname="argument service_token", value=service_token, expected_type=type_hints["service_token"])
            check_type(argname="argument role", value=role, expected_type=type_hints["role"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "service_token": service_token,
        }
        if role is not None:
            self._values["role"] = role

    @builtins.property
    def service_token(self) -> builtins.str:
        '''(experimental) The kubectl provider lambda arn.

        :stability: experimental
        '''
        result = self._values.get("service_token")
        assert result is not None, "Required property 'service_token' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def role(self) -> typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole]:
        '''(experimental) The role of the provider lambda function.

        Only required if you deploy helm charts using this imported provider.

        :default: - no role.

        :stability: experimental
        '''
        result = self._values.get("role")
        return typing.cast(typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "KubectlProviderAttributes(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@aws-cdk/aws-eks-v2-alpha.KubectlProviderOptions",
    jsii_struct_bases=[],
    name_mapping={
        "kubectl_layer": "kubectlLayer",
        "awscli_layer": "awscliLayer",
        "environment": "environment",
        "memory": "memory",
        "private_subnets": "privateSubnets",
        "role": "role",
        "security_group": "securityGroup",
    },
)
class KubectlProviderOptions:
    def __init__(
        self,
        *,
        kubectl_layer: _aws_cdk_aws_lambda_ceddda9d.ILayerVersion,
        awscli_layer: typing.Optional[_aws_cdk_aws_lambda_ceddda9d.ILayerVersion] = None,
        environment: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        memory: typing.Optional[_aws_cdk_ceddda9d.Size] = None,
        private_subnets: typing.Optional[typing.Sequence[_aws_cdk_aws_ec2_ceddda9d.ISubnet]] = None,
        role: typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole] = None,
        security_group: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup] = None,
    ) -> None:
        '''
        :param kubectl_layer: (experimental) An AWS Lambda layer that includes ``kubectl`` and ``helm``.
        :param awscli_layer: (experimental) An AWS Lambda layer that contains the ``aws`` CLI. If not defined, a default layer will be used containing the AWS CLI 2.x.
        :param environment: (experimental) Custom environment variables when running ``kubectl`` against this cluster.
        :param memory: (experimental) The amount of memory allocated to the kubectl provider's lambda function.
        :param private_subnets: (experimental) Subnets to host the ``kubectl`` compute resources. If not specified, the k8s endpoint is expected to be accessible publicly.
        :param role: (experimental) An IAM role that can perform kubectl operations against this cluster. The role should be mapped to the ``system:masters`` Kubernetes RBAC role. This role is directly passed to the lambda handler that sends Kube Ctl commands to the cluster. Default: - if not specified, the default role created by a lambda function will be used.
        :param security_group: (experimental) A security group to use for ``kubectl`` execution. Default: - If not specified, the k8s endpoint is expected to be accessible publicly.

        :stability: experimental
        :exampleMetadata: infused

        Example::

            from aws_cdk.lambda_layer_kubectl_v33 import KubectlV33Layer
            
            
            cluster = eks.Cluster(self, "hello-eks",
                version=eks.KubernetesVersion.V1_33,
                kubectl_provider_options=eks.KubectlProviderOptions(
                    kubectl_layer=KubectlV33Layer(self, "kubectl"),
                    environment={
                        "http_proxy": "http://proxy.myproxy.com"
                    }
                )
            )
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9277e03d81f2504be1f4bfdbebaa07d5981427081ee7df98e56f401e95b72da2)
            check_type(argname="argument kubectl_layer", value=kubectl_layer, expected_type=type_hints["kubectl_layer"])
            check_type(argname="argument awscli_layer", value=awscli_layer, expected_type=type_hints["awscli_layer"])
            check_type(argname="argument environment", value=environment, expected_type=type_hints["environment"])
            check_type(argname="argument memory", value=memory, expected_type=type_hints["memory"])
            check_type(argname="argument private_subnets", value=private_subnets, expected_type=type_hints["private_subnets"])
            check_type(argname="argument role", value=role, expected_type=type_hints["role"])
            check_type(argname="argument security_group", value=security_group, expected_type=type_hints["security_group"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "kubectl_layer": kubectl_layer,
        }
        if awscli_layer is not None:
            self._values["awscli_layer"] = awscli_layer
        if environment is not None:
            self._values["environment"] = environment
        if memory is not None:
            self._values["memory"] = memory
        if private_subnets is not None:
            self._values["private_subnets"] = private_subnets
        if role is not None:
            self._values["role"] = role
        if security_group is not None:
            self._values["security_group"] = security_group

    @builtins.property
    def kubectl_layer(self) -> _aws_cdk_aws_lambda_ceddda9d.ILayerVersion:
        '''(experimental) An AWS Lambda layer that includes ``kubectl`` and ``helm``.

        :stability: experimental
        '''
        result = self._values.get("kubectl_layer")
        assert result is not None, "Required property 'kubectl_layer' is missing"
        return typing.cast(_aws_cdk_aws_lambda_ceddda9d.ILayerVersion, result)

    @builtins.property
    def awscli_layer(
        self,
    ) -> typing.Optional[_aws_cdk_aws_lambda_ceddda9d.ILayerVersion]:
        '''(experimental) An AWS Lambda layer that contains the ``aws`` CLI.

        If not defined, a default layer will be used containing the AWS CLI 2.x.

        :stability: experimental
        '''
        result = self._values.get("awscli_layer")
        return typing.cast(typing.Optional[_aws_cdk_aws_lambda_ceddda9d.ILayerVersion], result)

    @builtins.property
    def environment(
        self,
    ) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        '''(experimental) Custom environment variables when running ``kubectl`` against this cluster.

        :stability: experimental
        '''
        result = self._values.get("environment")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], result)

    @builtins.property
    def memory(self) -> typing.Optional[_aws_cdk_ceddda9d.Size]:
        '''(experimental) The amount of memory allocated to the kubectl provider's lambda function.

        :stability: experimental
        '''
        result = self._values.get("memory")
        return typing.cast(typing.Optional[_aws_cdk_ceddda9d.Size], result)

    @builtins.property
    def private_subnets(
        self,
    ) -> typing.Optional[typing.List[_aws_cdk_aws_ec2_ceddda9d.ISubnet]]:
        '''(experimental) Subnets to host the ``kubectl`` compute resources.

        If not specified, the k8s
        endpoint is expected to be accessible publicly.

        :stability: experimental
        '''
        result = self._values.get("private_subnets")
        return typing.cast(typing.Optional[typing.List[_aws_cdk_aws_ec2_ceddda9d.ISubnet]], result)

    @builtins.property
    def role(self) -> typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole]:
        '''(experimental) An IAM role that can perform kubectl operations against this cluster.

        The role should be mapped to the ``system:masters`` Kubernetes RBAC role.

        This role is directly passed to the lambda handler that sends Kube Ctl commands to the cluster.

        :default:

        - if not specified, the default role created by a lambda function will
        be used.

        :stability: experimental
        '''
        result = self._values.get("role")
        return typing.cast(typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole], result)

    @builtins.property
    def security_group(
        self,
    ) -> typing.Optional[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup]:
        '''(experimental) A security group to use for ``kubectl`` execution.

        :default:

        - If not specified, the k8s endpoint is expected to be accessible
        publicly.

        :stability: experimental
        '''
        result = self._values.get("security_group")
        return typing.cast(typing.Optional[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "KubectlProviderOptions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@aws-cdk/aws-eks-v2-alpha.KubectlProviderProps",
    jsii_struct_bases=[KubectlProviderOptions],
    name_mapping={
        "kubectl_layer": "kubectlLayer",
        "awscli_layer": "awscliLayer",
        "environment": "environment",
        "memory": "memory",
        "private_subnets": "privateSubnets",
        "role": "role",
        "security_group": "securityGroup",
        "cluster": "cluster",
    },
)
class KubectlProviderProps(KubectlProviderOptions):
    def __init__(
        self,
        *,
        kubectl_layer: _aws_cdk_aws_lambda_ceddda9d.ILayerVersion,
        awscli_layer: typing.Optional[_aws_cdk_aws_lambda_ceddda9d.ILayerVersion] = None,
        environment: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        memory: typing.Optional[_aws_cdk_ceddda9d.Size] = None,
        private_subnets: typing.Optional[typing.Sequence[_aws_cdk_aws_ec2_ceddda9d.ISubnet]] = None,
        role: typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole] = None,
        security_group: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup] = None,
        cluster: ICluster,
    ) -> None:
        '''(experimental) Properties for a KubectlProvider.

        :param kubectl_layer: (experimental) An AWS Lambda layer that includes ``kubectl`` and ``helm``.
        :param awscli_layer: (experimental) An AWS Lambda layer that contains the ``aws`` CLI. If not defined, a default layer will be used containing the AWS CLI 2.x.
        :param environment: (experimental) Custom environment variables when running ``kubectl`` against this cluster.
        :param memory: (experimental) The amount of memory allocated to the kubectl provider's lambda function.
        :param private_subnets: (experimental) Subnets to host the ``kubectl`` compute resources. If not specified, the k8s endpoint is expected to be accessible publicly.
        :param role: (experimental) An IAM role that can perform kubectl operations against this cluster. The role should be mapped to the ``system:masters`` Kubernetes RBAC role. This role is directly passed to the lambda handler that sends Kube Ctl commands to the cluster. Default: - if not specified, the default role created by a lambda function will be used.
        :param security_group: (experimental) A security group to use for ``kubectl`` execution. Default: - If not specified, the k8s endpoint is expected to be accessible publicly.
        :param cluster: (experimental) The cluster to control.

        :stability: experimental
        :exampleMetadata: fixture=_generated

        Example::

            # The code below shows an example of how to instantiate this type.
            # The values are placeholders you should change.
            import aws_cdk.aws_eks_v2_alpha as eks_v2_alpha
            import aws_cdk as cdk
            from aws_cdk import aws_ec2 as ec2
            from aws_cdk import aws_iam as iam
            from aws_cdk import aws_lambda as lambda_
            
            # cluster: eks_v2_alpha.Cluster
            # layer_version: lambda.LayerVersion
            # role: iam.Role
            # security_group: ec2.SecurityGroup
            # size: cdk.Size
            # subnet: ec2.Subnet
            
            kubectl_provider_props = eks_v2_alpha.KubectlProviderProps(
                cluster=cluster,
                kubectl_layer=layer_version,
            
                # the properties below are optional
                awscli_layer=layer_version,
                environment={
                    "environment_key": "environment"
                },
                memory=size,
                private_subnets=[subnet],
                role=role,
                security_group=security_group
            )
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5a43e0389ce84d427182514777711bd5e0d20341c50e14d2bba6a20b786e2989)
            check_type(argname="argument kubectl_layer", value=kubectl_layer, expected_type=type_hints["kubectl_layer"])
            check_type(argname="argument awscli_layer", value=awscli_layer, expected_type=type_hints["awscli_layer"])
            check_type(argname="argument environment", value=environment, expected_type=type_hints["environment"])
            check_type(argname="argument memory", value=memory, expected_type=type_hints["memory"])
            check_type(argname="argument private_subnets", value=private_subnets, expected_type=type_hints["private_subnets"])
            check_type(argname="argument role", value=role, expected_type=type_hints["role"])
            check_type(argname="argument security_group", value=security_group, expected_type=type_hints["security_group"])
            check_type(argname="argument cluster", value=cluster, expected_type=type_hints["cluster"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "kubectl_layer": kubectl_layer,
            "cluster": cluster,
        }
        if awscli_layer is not None:
            self._values["awscli_layer"] = awscli_layer
        if environment is not None:
            self._values["environment"] = environment
        if memory is not None:
            self._values["memory"] = memory
        if private_subnets is not None:
            self._values["private_subnets"] = private_subnets
        if role is not None:
            self._values["role"] = role
        if security_group is not None:
            self._values["security_group"] = security_group

    @builtins.property
    def kubectl_layer(self) -> _aws_cdk_aws_lambda_ceddda9d.ILayerVersion:
        '''(experimental) An AWS Lambda layer that includes ``kubectl`` and ``helm``.

        :stability: experimental
        '''
        result = self._values.get("kubectl_layer")
        assert result is not None, "Required property 'kubectl_layer' is missing"
        return typing.cast(_aws_cdk_aws_lambda_ceddda9d.ILayerVersion, result)

    @builtins.property
    def awscli_layer(
        self,
    ) -> typing.Optional[_aws_cdk_aws_lambda_ceddda9d.ILayerVersion]:
        '''(experimental) An AWS Lambda layer that contains the ``aws`` CLI.

        If not defined, a default layer will be used containing the AWS CLI 2.x.

        :stability: experimental
        '''
        result = self._values.get("awscli_layer")
        return typing.cast(typing.Optional[_aws_cdk_aws_lambda_ceddda9d.ILayerVersion], result)

    @builtins.property
    def environment(
        self,
    ) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        '''(experimental) Custom environment variables when running ``kubectl`` against this cluster.

        :stability: experimental
        '''
        result = self._values.get("environment")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], result)

    @builtins.property
    def memory(self) -> typing.Optional[_aws_cdk_ceddda9d.Size]:
        '''(experimental) The amount of memory allocated to the kubectl provider's lambda function.

        :stability: experimental
        '''
        result = self._values.get("memory")
        return typing.cast(typing.Optional[_aws_cdk_ceddda9d.Size], result)

    @builtins.property
    def private_subnets(
        self,
    ) -> typing.Optional[typing.List[_aws_cdk_aws_ec2_ceddda9d.ISubnet]]:
        '''(experimental) Subnets to host the ``kubectl`` compute resources.

        If not specified, the k8s
        endpoint is expected to be accessible publicly.

        :stability: experimental
        '''
        result = self._values.get("private_subnets")
        return typing.cast(typing.Optional[typing.List[_aws_cdk_aws_ec2_ceddda9d.ISubnet]], result)

    @builtins.property
    def role(self) -> typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole]:
        '''(experimental) An IAM role that can perform kubectl operations against this cluster.

        The role should be mapped to the ``system:masters`` Kubernetes RBAC role.

        This role is directly passed to the lambda handler that sends Kube Ctl commands to the cluster.

        :default:

        - if not specified, the default role created by a lambda function will
        be used.

        :stability: experimental
        '''
        result = self._values.get("role")
        return typing.cast(typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole], result)

    @builtins.property
    def security_group(
        self,
    ) -> typing.Optional[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup]:
        '''(experimental) A security group to use for ``kubectl`` execution.

        :default:

        - If not specified, the k8s endpoint is expected to be accessible
        publicly.

        :stability: experimental
        '''
        result = self._values.get("security_group")
        return typing.cast(typing.Optional[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup], result)

    @builtins.property
    def cluster(self) -> ICluster:
        '''(experimental) The cluster to control.

        :stability: experimental
        '''
        result = self._values.get("cluster")
        assert result is not None, "Required property 'cluster' is missing"
        return typing.cast(ICluster, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "KubectlProviderProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class KubernetesManifest(
    _constructs_77d1e7e8.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="@aws-cdk/aws-eks-v2-alpha.KubernetesManifest",
):
    '''(experimental) Represents a manifest within the Kubernetes system.

    Alternatively, you can use ``cluster.addManifest(resource[, resource, ...])``
    to define resources on this cluster.

    Applies/deletes the manifest using ``kubectl``.

    :stability: experimental
    :exampleMetadata: infused

    Example::

        # cluster: eks.Cluster
        
        namespace = cluster.add_manifest("my-namespace", {
            "api_version": "v1",
            "kind": "Namespace",
            "metadata": {"name": "my-app"}
        })
        
        service = cluster.add_manifest("my-service", {
            "metadata": {
                "name": "myservice",
                "namespace": "my-app"
            },
            "spec": {}
        })
        
        service.node.add_dependency(namespace)
    '''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        cluster: ICluster,
        manifest: typing.Sequence[typing.Mapping[builtins.str, typing.Any]],
        overwrite: typing.Optional[builtins.bool] = None,
        ingress_alb: typing.Optional[builtins.bool] = None,
        ingress_alb_scheme: typing.Optional[AlbScheme] = None,
        prune: typing.Optional[builtins.bool] = None,
        skip_validation: typing.Optional[builtins.bool] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param cluster: (experimental) The EKS cluster to apply this manifest to. [disable-awslint:ref-via-interface]
        :param manifest: (experimental) The manifest to apply. Consists of any number of child resources. When the resources are created/updated, this manifest will be applied to the cluster through ``kubectl apply`` and when the resources or the stack is deleted, the resources in the manifest will be deleted through ``kubectl delete``.
        :param overwrite: (experimental) Overwrite any existing resources. If this is set, we will use ``kubectl apply`` instead of ``kubectl create`` when the resource is created. Otherwise, if there is already a resource in the cluster with the same name, the operation will fail. Default: false
        :param ingress_alb: (experimental) Automatically detect ``Ingress`` resources in the manifest and annotate them so they are picked up by an ALB Ingress Controller. Default: false
        :param ingress_alb_scheme: (experimental) Specify the ALB scheme that should be applied to ``Ingress`` resources. Only applicable if ``ingressAlb`` is set to ``true``. Default: AlbScheme.INTERNAL
        :param prune: (experimental) When a resource is removed from a Kubernetes manifest, it no longer appears in the manifest, and there is no way to know that this resource needs to be deleted. To address this, ``kubectl apply`` has a ``--prune`` option which will query the cluster for all resources with a specific label and will remove all the labeld resources that are not part of the applied manifest. If this option is disabled and a resource is removed, it will become "orphaned" and will not be deleted from the cluster. When this option is enabled (default), the construct will inject a label to all Kubernetes resources included in this manifest which will be used to prune resources when the manifest changes via ``kubectl apply --prune``. The label name will be ``aws.cdk.eks/prune-<ADDR>`` where ``<ADDR>`` is the 42-char unique address of this construct in the construct tree. Value is empty. Default: - based on the prune option of the cluster, which is ``true`` unless otherwise specified.
        :param skip_validation: (experimental) A flag to signify if the manifest validation should be skipped. Default: false

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a98f85227580b8191bcd0e8f3f6195758157c48b7d98ccefd42d9d059b17ec94)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = KubernetesManifestProps(
            cluster=cluster,
            manifest=manifest,
            overwrite=overwrite,
            ingress_alb=ingress_alb,
            ingress_alb_scheme=ingress_alb_scheme,
            prune=prune,
            skip_validation=skip_validation,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @jsii.python.classproperty
    @jsii.member(jsii_name="RESOURCE_TYPE")
    def RESOURCE_TYPE(cls) -> builtins.str:
        '''(experimental) The CloudFormation resource type.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "RESOURCE_TYPE"))


@jsii.data_type(
    jsii_type="@aws-cdk/aws-eks-v2-alpha.KubernetesManifestOptions",
    jsii_struct_bases=[],
    name_mapping={
        "ingress_alb": "ingressAlb",
        "ingress_alb_scheme": "ingressAlbScheme",
        "prune": "prune",
        "skip_validation": "skipValidation",
    },
)
class KubernetesManifestOptions:
    def __init__(
        self,
        *,
        ingress_alb: typing.Optional[builtins.bool] = None,
        ingress_alb_scheme: typing.Optional[AlbScheme] = None,
        prune: typing.Optional[builtins.bool] = None,
        skip_validation: typing.Optional[builtins.bool] = None,
    ) -> None:
        '''(experimental) Options for ``KubernetesManifest``.

        :param ingress_alb: (experimental) Automatically detect ``Ingress`` resources in the manifest and annotate them so they are picked up by an ALB Ingress Controller. Default: false
        :param ingress_alb_scheme: (experimental) Specify the ALB scheme that should be applied to ``Ingress`` resources. Only applicable if ``ingressAlb`` is set to ``true``. Default: AlbScheme.INTERNAL
        :param prune: (experimental) When a resource is removed from a Kubernetes manifest, it no longer appears in the manifest, and there is no way to know that this resource needs to be deleted. To address this, ``kubectl apply`` has a ``--prune`` option which will query the cluster for all resources with a specific label and will remove all the labeld resources that are not part of the applied manifest. If this option is disabled and a resource is removed, it will become "orphaned" and will not be deleted from the cluster. When this option is enabled (default), the construct will inject a label to all Kubernetes resources included in this manifest which will be used to prune resources when the manifest changes via ``kubectl apply --prune``. The label name will be ``aws.cdk.eks/prune-<ADDR>`` where ``<ADDR>`` is the 42-char unique address of this construct in the construct tree. Value is empty. Default: - based on the prune option of the cluster, which is ``true`` unless otherwise specified.
        :param skip_validation: (experimental) A flag to signify if the manifest validation should be skipped. Default: false

        :stability: experimental
        :exampleMetadata: fixture=_generated

        Example::

            # The code below shows an example of how to instantiate this type.
            # The values are placeholders you should change.
            import aws_cdk.aws_eks_v2_alpha as eks_v2_alpha
            
            kubernetes_manifest_options = eks_v2_alpha.KubernetesManifestOptions(
                ingress_alb=False,
                ingress_alb_scheme=eks_v2_alpha.AlbScheme.INTERNAL,
                prune=False,
                skip_validation=False
            )
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9213887feeb82fa12f23b39945263ce6d3b80422fa394db44cae4209a6d123b7)
            check_type(argname="argument ingress_alb", value=ingress_alb, expected_type=type_hints["ingress_alb"])
            check_type(argname="argument ingress_alb_scheme", value=ingress_alb_scheme, expected_type=type_hints["ingress_alb_scheme"])
            check_type(argname="argument prune", value=prune, expected_type=type_hints["prune"])
            check_type(argname="argument skip_validation", value=skip_validation, expected_type=type_hints["skip_validation"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if ingress_alb is not None:
            self._values["ingress_alb"] = ingress_alb
        if ingress_alb_scheme is not None:
            self._values["ingress_alb_scheme"] = ingress_alb_scheme
        if prune is not None:
            self._values["prune"] = prune
        if skip_validation is not None:
            self._values["skip_validation"] = skip_validation

    @builtins.property
    def ingress_alb(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Automatically detect ``Ingress`` resources in the manifest and annotate them so they are picked up by an ALB Ingress Controller.

        :default: false

        :stability: experimental
        '''
        result = self._values.get("ingress_alb")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def ingress_alb_scheme(self) -> typing.Optional[AlbScheme]:
        '''(experimental) Specify the ALB scheme that should be applied to ``Ingress`` resources.

        Only applicable if ``ingressAlb`` is set to ``true``.

        :default: AlbScheme.INTERNAL

        :stability: experimental
        '''
        result = self._values.get("ingress_alb_scheme")
        return typing.cast(typing.Optional[AlbScheme], result)

    @builtins.property
    def prune(self) -> typing.Optional[builtins.bool]:
        '''(experimental) When a resource is removed from a Kubernetes manifest, it no longer appears in the manifest, and there is no way to know that this resource needs to be deleted.

        To address this, ``kubectl apply`` has a ``--prune`` option which will
        query the cluster for all resources with a specific label and will remove
        all the labeld resources that are not part of the applied manifest. If this
        option is disabled and a resource is removed, it will become "orphaned" and
        will not be deleted from the cluster.

        When this option is enabled (default), the construct will inject a label to
        all Kubernetes resources included in this manifest which will be used to
        prune resources when the manifest changes via ``kubectl apply --prune``.

        The label name will be ``aws.cdk.eks/prune-<ADDR>`` where ``<ADDR>`` is the
        42-char unique address of this construct in the construct tree. Value is
        empty.

        :default:

        - based on the prune option of the cluster, which is ``true`` unless
        otherwise specified.

        :see: https://kubernetes.io/docs/tasks/manage-kubernetes-objects/declarative-config/#alternative-kubectl-apply-f-directory-prune-l-your-label
        :stability: experimental
        '''
        result = self._values.get("prune")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def skip_validation(self) -> typing.Optional[builtins.bool]:
        '''(experimental) A flag to signify if the manifest validation should be skipped.

        :default: false

        :stability: experimental
        '''
        result = self._values.get("skip_validation")
        return typing.cast(typing.Optional[builtins.bool], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "KubernetesManifestOptions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@aws-cdk/aws-eks-v2-alpha.KubernetesManifestProps",
    jsii_struct_bases=[KubernetesManifestOptions],
    name_mapping={
        "ingress_alb": "ingressAlb",
        "ingress_alb_scheme": "ingressAlbScheme",
        "prune": "prune",
        "skip_validation": "skipValidation",
        "cluster": "cluster",
        "manifest": "manifest",
        "overwrite": "overwrite",
    },
)
class KubernetesManifestProps(KubernetesManifestOptions):
    def __init__(
        self,
        *,
        ingress_alb: typing.Optional[builtins.bool] = None,
        ingress_alb_scheme: typing.Optional[AlbScheme] = None,
        prune: typing.Optional[builtins.bool] = None,
        skip_validation: typing.Optional[builtins.bool] = None,
        cluster: ICluster,
        manifest: typing.Sequence[typing.Mapping[builtins.str, typing.Any]],
        overwrite: typing.Optional[builtins.bool] = None,
    ) -> None:
        '''(experimental) Properties for KubernetesManifest.

        :param ingress_alb: (experimental) Automatically detect ``Ingress`` resources in the manifest and annotate them so they are picked up by an ALB Ingress Controller. Default: false
        :param ingress_alb_scheme: (experimental) Specify the ALB scheme that should be applied to ``Ingress`` resources. Only applicable if ``ingressAlb`` is set to ``true``. Default: AlbScheme.INTERNAL
        :param prune: (experimental) When a resource is removed from a Kubernetes manifest, it no longer appears in the manifest, and there is no way to know that this resource needs to be deleted. To address this, ``kubectl apply`` has a ``--prune`` option which will query the cluster for all resources with a specific label and will remove all the labeld resources that are not part of the applied manifest. If this option is disabled and a resource is removed, it will become "orphaned" and will not be deleted from the cluster. When this option is enabled (default), the construct will inject a label to all Kubernetes resources included in this manifest which will be used to prune resources when the manifest changes via ``kubectl apply --prune``. The label name will be ``aws.cdk.eks/prune-<ADDR>`` where ``<ADDR>`` is the 42-char unique address of this construct in the construct tree. Value is empty. Default: - based on the prune option of the cluster, which is ``true`` unless otherwise specified.
        :param skip_validation: (experimental) A flag to signify if the manifest validation should be skipped. Default: false
        :param cluster: (experimental) The EKS cluster to apply this manifest to. [disable-awslint:ref-via-interface]
        :param manifest: (experimental) The manifest to apply. Consists of any number of child resources. When the resources are created/updated, this manifest will be applied to the cluster through ``kubectl apply`` and when the resources or the stack is deleted, the resources in the manifest will be deleted through ``kubectl delete``.
        :param overwrite: (experimental) Overwrite any existing resources. If this is set, we will use ``kubectl apply`` instead of ``kubectl create`` when the resource is created. Otherwise, if there is already a resource in the cluster with the same name, the operation will fail. Default: false

        :stability: experimental
        :exampleMetadata: infused

        Example::

            # cluster: eks.Cluster
            
            app_label = {"app": "hello-kubernetes"}
            
            deployment = {
                "api_version": "apps/v1",
                "kind": "Deployment",
                "metadata": {"name": "hello-kubernetes"},
                "spec": {
                    "replicas": 3,
                    "selector": {"match_labels": app_label},
                    "template": {
                        "metadata": {"labels": app_label},
                        "spec": {
                            "containers": [{
                                "name": "hello-kubernetes",
                                "image": "paulbouwer/hello-kubernetes:1.5",
                                "ports": [{"container_port": 8080}]
                            }
                            ]
                        }
                    }
                }
            }
            
            service = {
                "api_version": "v1",
                "kind": "Service",
                "metadata": {"name": "hello-kubernetes"},
                "spec": {
                    "type": "LoadBalancer",
                    "ports": [{"port": 80, "target_port": 8080}],
                    "selector": app_label
                }
            }
            
            # option 1: use a construct
            eks.KubernetesManifest(self, "hello-kub",
                cluster=cluster,
                manifest=[deployment, service]
            )
            
            # or, option2: use `addManifest`
            cluster.add_manifest("hello-kub", service, deployment)
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1d422d0928845d93f04b27e21267a606598597ae4ac81109f31e2bdb34966aaa)
            check_type(argname="argument ingress_alb", value=ingress_alb, expected_type=type_hints["ingress_alb"])
            check_type(argname="argument ingress_alb_scheme", value=ingress_alb_scheme, expected_type=type_hints["ingress_alb_scheme"])
            check_type(argname="argument prune", value=prune, expected_type=type_hints["prune"])
            check_type(argname="argument skip_validation", value=skip_validation, expected_type=type_hints["skip_validation"])
            check_type(argname="argument cluster", value=cluster, expected_type=type_hints["cluster"])
            check_type(argname="argument manifest", value=manifest, expected_type=type_hints["manifest"])
            check_type(argname="argument overwrite", value=overwrite, expected_type=type_hints["overwrite"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "cluster": cluster,
            "manifest": manifest,
        }
        if ingress_alb is not None:
            self._values["ingress_alb"] = ingress_alb
        if ingress_alb_scheme is not None:
            self._values["ingress_alb_scheme"] = ingress_alb_scheme
        if prune is not None:
            self._values["prune"] = prune
        if skip_validation is not None:
            self._values["skip_validation"] = skip_validation
        if overwrite is not None:
            self._values["overwrite"] = overwrite

    @builtins.property
    def ingress_alb(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Automatically detect ``Ingress`` resources in the manifest and annotate them so they are picked up by an ALB Ingress Controller.

        :default: false

        :stability: experimental
        '''
        result = self._values.get("ingress_alb")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def ingress_alb_scheme(self) -> typing.Optional[AlbScheme]:
        '''(experimental) Specify the ALB scheme that should be applied to ``Ingress`` resources.

        Only applicable if ``ingressAlb`` is set to ``true``.

        :default: AlbScheme.INTERNAL

        :stability: experimental
        '''
        result = self._values.get("ingress_alb_scheme")
        return typing.cast(typing.Optional[AlbScheme], result)

    @builtins.property
    def prune(self) -> typing.Optional[builtins.bool]:
        '''(experimental) When a resource is removed from a Kubernetes manifest, it no longer appears in the manifest, and there is no way to know that this resource needs to be deleted.

        To address this, ``kubectl apply`` has a ``--prune`` option which will
        query the cluster for all resources with a specific label and will remove
        all the labeld resources that are not part of the applied manifest. If this
        option is disabled and a resource is removed, it will become "orphaned" and
        will not be deleted from the cluster.

        When this option is enabled (default), the construct will inject a label to
        all Kubernetes resources included in this manifest which will be used to
        prune resources when the manifest changes via ``kubectl apply --prune``.

        The label name will be ``aws.cdk.eks/prune-<ADDR>`` where ``<ADDR>`` is the
        42-char unique address of this construct in the construct tree. Value is
        empty.

        :default:

        - based on the prune option of the cluster, which is ``true`` unless
        otherwise specified.

        :see: https://kubernetes.io/docs/tasks/manage-kubernetes-objects/declarative-config/#alternative-kubectl-apply-f-directory-prune-l-your-label
        :stability: experimental
        '''
        result = self._values.get("prune")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def skip_validation(self) -> typing.Optional[builtins.bool]:
        '''(experimental) A flag to signify if the manifest validation should be skipped.

        :default: false

        :stability: experimental
        '''
        result = self._values.get("skip_validation")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def cluster(self) -> ICluster:
        '''(experimental) The EKS cluster to apply this manifest to.

        [disable-awslint:ref-via-interface]

        :stability: experimental
        '''
        result = self._values.get("cluster")
        assert result is not None, "Required property 'cluster' is missing"
        return typing.cast(ICluster, result)

    @builtins.property
    def manifest(self) -> typing.List[typing.Mapping[builtins.str, typing.Any]]:
        '''(experimental) The manifest to apply.

        Consists of any number of child resources.

        When the resources are created/updated, this manifest will be applied to the
        cluster through ``kubectl apply`` and when the resources or the stack is
        deleted, the resources in the manifest will be deleted through ``kubectl delete``.

        :stability: experimental

        Example::

            [{
                "api_version": "v1",
                "kind": "Pod",
                "metadata": {"name": "mypod"},
                "spec": {
                    "containers": [{"name": "hello", "image": "paulbouwer/hello-kubernetes:1.5", "ports": [{"container_port": 8080}]}]
                }
            }]
        '''
        result = self._values.get("manifest")
        assert result is not None, "Required property 'manifest' is missing"
        return typing.cast(typing.List[typing.Mapping[builtins.str, typing.Any]], result)

    @builtins.property
    def overwrite(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Overwrite any existing resources.

        If this is set, we will use ``kubectl apply`` instead of ``kubectl create``
        when the resource is created. Otherwise, if there is already a resource
        in the cluster with the same name, the operation will fail.

        :default: false

        :stability: experimental
        '''
        result = self._values.get("overwrite")
        return typing.cast(typing.Optional[builtins.bool], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "KubernetesManifestProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class KubernetesObjectValue(
    _constructs_77d1e7e8.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="@aws-cdk/aws-eks-v2-alpha.KubernetesObjectValue",
):
    '''(experimental) Represents a value of a specific object deployed in the cluster.

    Use this to fetch any information available by the ``kubectl get`` command.

    :stability: experimental
    :exampleMetadata: infused

    Example::

        # cluster: eks.Cluster
        
        # query the load balancer address
        my_service_address = eks.KubernetesObjectValue(self, "LoadBalancerAttribute",
            cluster=cluster,
            object_type="service",
            object_name="my-service",
            json_path=".status.loadBalancer.ingress[0].hostname"
        )
        
        # pass the address to a lambda function
        proxy_function = lambda_.Function(self, "ProxyFunction",
            handler="index.handler",
            code=lambda_.Code.from_inline("my-code"),
            runtime=lambda_.Runtime.NODEJS_LATEST,
            environment={
                "my_service_address": my_service_address.value
            }
        )
    '''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        cluster: ICluster,
        json_path: builtins.str,
        object_name: builtins.str,
        object_type: builtins.str,
        object_namespace: typing.Optional[builtins.str] = None,
        timeout: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param cluster: (experimental) The EKS cluster to fetch attributes from. [disable-awslint:ref-via-interface]
        :param json_path: (experimental) JSONPath to the specific value.
        :param object_name: (experimental) The name of the object to query.
        :param object_type: (experimental) The object type to query. (e.g 'service', 'pod'...)
        :param object_namespace: (experimental) The namespace the object belongs to. Default: 'default'
        :param timeout: (experimental) Timeout for waiting on a value. Default: Duration.minutes(5)

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b33d1e78eda8d7f720836ea00e003335099872a491e2a4ff85cdef6f95c7cf05)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = KubernetesObjectValueProps(
            cluster=cluster,
            json_path=json_path,
            object_name=object_name,
            object_type=object_type,
            object_namespace=object_namespace,
            timeout=timeout,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @jsii.python.classproperty
    @jsii.member(jsii_name="RESOURCE_TYPE")
    def RESOURCE_TYPE(cls) -> builtins.str:
        '''(experimental) The CloudFormation resource type.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "RESOURCE_TYPE"))

    @builtins.property
    @jsii.member(jsii_name="value")
    def value(self) -> builtins.str:
        '''(experimental) The value as a string token.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "value"))


@jsii.data_type(
    jsii_type="@aws-cdk/aws-eks-v2-alpha.KubernetesObjectValueProps",
    jsii_struct_bases=[],
    name_mapping={
        "cluster": "cluster",
        "json_path": "jsonPath",
        "object_name": "objectName",
        "object_type": "objectType",
        "object_namespace": "objectNamespace",
        "timeout": "timeout",
    },
)
class KubernetesObjectValueProps:
    def __init__(
        self,
        *,
        cluster: ICluster,
        json_path: builtins.str,
        object_name: builtins.str,
        object_type: builtins.str,
        object_namespace: typing.Optional[builtins.str] = None,
        timeout: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
    ) -> None:
        '''(experimental) Properties for KubernetesObjectValue.

        :param cluster: (experimental) The EKS cluster to fetch attributes from. [disable-awslint:ref-via-interface]
        :param json_path: (experimental) JSONPath to the specific value.
        :param object_name: (experimental) The name of the object to query.
        :param object_type: (experimental) The object type to query. (e.g 'service', 'pod'...)
        :param object_namespace: (experimental) The namespace the object belongs to. Default: 'default'
        :param timeout: (experimental) Timeout for waiting on a value. Default: Duration.minutes(5)

        :stability: experimental
        :exampleMetadata: infused

        Example::

            # cluster: eks.Cluster
            
            # query the load balancer address
            my_service_address = eks.KubernetesObjectValue(self, "LoadBalancerAttribute",
                cluster=cluster,
                object_type="service",
                object_name="my-service",
                json_path=".status.loadBalancer.ingress[0].hostname"
            )
            
            # pass the address to a lambda function
            proxy_function = lambda_.Function(self, "ProxyFunction",
                handler="index.handler",
                code=lambda_.Code.from_inline("my-code"),
                runtime=lambda_.Runtime.NODEJS_LATEST,
                environment={
                    "my_service_address": my_service_address.value
                }
            )
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3176fefda15b476ceac8b1c85f1ea17547b109979e2d9bc914fbddf92b82f9d1)
            check_type(argname="argument cluster", value=cluster, expected_type=type_hints["cluster"])
            check_type(argname="argument json_path", value=json_path, expected_type=type_hints["json_path"])
            check_type(argname="argument object_name", value=object_name, expected_type=type_hints["object_name"])
            check_type(argname="argument object_type", value=object_type, expected_type=type_hints["object_type"])
            check_type(argname="argument object_namespace", value=object_namespace, expected_type=type_hints["object_namespace"])
            check_type(argname="argument timeout", value=timeout, expected_type=type_hints["timeout"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "cluster": cluster,
            "json_path": json_path,
            "object_name": object_name,
            "object_type": object_type,
        }
        if object_namespace is not None:
            self._values["object_namespace"] = object_namespace
        if timeout is not None:
            self._values["timeout"] = timeout

    @builtins.property
    def cluster(self) -> ICluster:
        '''(experimental) The EKS cluster to fetch attributes from.

        [disable-awslint:ref-via-interface]

        :stability: experimental
        '''
        result = self._values.get("cluster")
        assert result is not None, "Required property 'cluster' is missing"
        return typing.cast(ICluster, result)

    @builtins.property
    def json_path(self) -> builtins.str:
        '''(experimental) JSONPath to the specific value.

        :see: https://kubernetes.io/docs/reference/kubectl/jsonpath/
        :stability: experimental
        '''
        result = self._values.get("json_path")
        assert result is not None, "Required property 'json_path' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def object_name(self) -> builtins.str:
        '''(experimental) The name of the object to query.

        :stability: experimental
        '''
        result = self._values.get("object_name")
        assert result is not None, "Required property 'object_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def object_type(self) -> builtins.str:
        '''(experimental) The object type to query.

        (e.g 'service', 'pod'...)

        :stability: experimental
        '''
        result = self._values.get("object_type")
        assert result is not None, "Required property 'object_type' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def object_namespace(self) -> typing.Optional[builtins.str]:
        '''(experimental) The namespace the object belongs to.

        :default: 'default'

        :stability: experimental
        '''
        result = self._values.get("object_namespace")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def timeout(self) -> typing.Optional[_aws_cdk_ceddda9d.Duration]:
        '''(experimental) Timeout for waiting on a value.

        :default: Duration.minutes(5)

        :stability: experimental
        '''
        result = self._values.get("timeout")
        return typing.cast(typing.Optional[_aws_cdk_ceddda9d.Duration], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "KubernetesObjectValueProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class KubernetesPatch(
    _constructs_77d1e7e8.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="@aws-cdk/aws-eks-v2-alpha.KubernetesPatch",
):
    '''(experimental) A CloudFormation resource which applies/restores a JSON patch into a Kubernetes resource.

    :see: https://kubernetes.io/docs/tasks/run-application/update-api-object-kubectl-patch/
    :stability: experimental
    :exampleMetadata: infused

    Example::

        # cluster: eks.Cluster
        
        eks.KubernetesPatch(self, "hello-kub-deployment-label",
            cluster=cluster,
            resource_name="deployment/hello-kubernetes",
            apply_patch={"spec": {"replicas": 5}},
            restore_patch={"spec": {"replicas": 3}}
        )
    '''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        apply_patch: typing.Mapping[builtins.str, typing.Any],
        cluster: ICluster,
        resource_name: builtins.str,
        restore_patch: typing.Mapping[builtins.str, typing.Any],
        patch_type: typing.Optional["PatchType"] = None,
        resource_namespace: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param apply_patch: (experimental) The JSON object to pass to ``kubectl patch`` when the resource is created/updated.
        :param cluster: (experimental) The cluster to apply the patch to. [disable-awslint:ref-via-interface]
        :param resource_name: (experimental) The full name of the resource to patch (e.g. ``deployment/coredns``).
        :param restore_patch: (experimental) The JSON object to pass to ``kubectl patch`` when the resource is removed.
        :param patch_type: (experimental) The patch type to pass to ``kubectl patch``. The default type used by ``kubectl patch`` is "strategic". Default: PatchType.STRATEGIC
        :param resource_namespace: (experimental) The kubernetes API namespace. Default: "default"

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b8e7dfe37990c2f03d7477c4bedbe6018b058a419a1ffc65a19a4914b9c0cd09)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = KubernetesPatchProps(
            apply_patch=apply_patch,
            cluster=cluster,
            resource_name=resource_name,
            restore_patch=restore_patch,
            patch_type=patch_type,
            resource_namespace=resource_namespace,
        )

        jsii.create(self.__class__, self, [scope, id, props])


@jsii.data_type(
    jsii_type="@aws-cdk/aws-eks-v2-alpha.KubernetesPatchProps",
    jsii_struct_bases=[],
    name_mapping={
        "apply_patch": "applyPatch",
        "cluster": "cluster",
        "resource_name": "resourceName",
        "restore_patch": "restorePatch",
        "patch_type": "patchType",
        "resource_namespace": "resourceNamespace",
    },
)
class KubernetesPatchProps:
    def __init__(
        self,
        *,
        apply_patch: typing.Mapping[builtins.str, typing.Any],
        cluster: ICluster,
        resource_name: builtins.str,
        restore_patch: typing.Mapping[builtins.str, typing.Any],
        patch_type: typing.Optional["PatchType"] = None,
        resource_namespace: typing.Optional[builtins.str] = None,
    ) -> None:
        '''(experimental) Properties for KubernetesPatch.

        :param apply_patch: (experimental) The JSON object to pass to ``kubectl patch`` when the resource is created/updated.
        :param cluster: (experimental) The cluster to apply the patch to. [disable-awslint:ref-via-interface]
        :param resource_name: (experimental) The full name of the resource to patch (e.g. ``deployment/coredns``).
        :param restore_patch: (experimental) The JSON object to pass to ``kubectl patch`` when the resource is removed.
        :param patch_type: (experimental) The patch type to pass to ``kubectl patch``. The default type used by ``kubectl patch`` is "strategic". Default: PatchType.STRATEGIC
        :param resource_namespace: (experimental) The kubernetes API namespace. Default: "default"

        :stability: experimental
        :exampleMetadata: infused

        Example::

            # cluster: eks.Cluster
            
            eks.KubernetesPatch(self, "hello-kub-deployment-label",
                cluster=cluster,
                resource_name="deployment/hello-kubernetes",
                apply_patch={"spec": {"replicas": 5}},
                restore_patch={"spec": {"replicas": 3}}
            )
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6a2a8250f9a8e2560086c3b4a14c105177bdade8b60ad3fff1746c21a40baf74)
            check_type(argname="argument apply_patch", value=apply_patch, expected_type=type_hints["apply_patch"])
            check_type(argname="argument cluster", value=cluster, expected_type=type_hints["cluster"])
            check_type(argname="argument resource_name", value=resource_name, expected_type=type_hints["resource_name"])
            check_type(argname="argument restore_patch", value=restore_patch, expected_type=type_hints["restore_patch"])
            check_type(argname="argument patch_type", value=patch_type, expected_type=type_hints["patch_type"])
            check_type(argname="argument resource_namespace", value=resource_namespace, expected_type=type_hints["resource_namespace"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "apply_patch": apply_patch,
            "cluster": cluster,
            "resource_name": resource_name,
            "restore_patch": restore_patch,
        }
        if patch_type is not None:
            self._values["patch_type"] = patch_type
        if resource_namespace is not None:
            self._values["resource_namespace"] = resource_namespace

    @builtins.property
    def apply_patch(self) -> typing.Mapping[builtins.str, typing.Any]:
        '''(experimental) The JSON object to pass to ``kubectl patch`` when the resource is created/updated.

        :stability: experimental
        '''
        result = self._values.get("apply_patch")
        assert result is not None, "Required property 'apply_patch' is missing"
        return typing.cast(typing.Mapping[builtins.str, typing.Any], result)

    @builtins.property
    def cluster(self) -> ICluster:
        '''(experimental) The cluster to apply the patch to.

        [disable-awslint:ref-via-interface]

        :stability: experimental
        '''
        result = self._values.get("cluster")
        assert result is not None, "Required property 'cluster' is missing"
        return typing.cast(ICluster, result)

    @builtins.property
    def resource_name(self) -> builtins.str:
        '''(experimental) The full name of the resource to patch (e.g. ``deployment/coredns``).

        :stability: experimental
        '''
        result = self._values.get("resource_name")
        assert result is not None, "Required property 'resource_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def restore_patch(self) -> typing.Mapping[builtins.str, typing.Any]:
        '''(experimental) The JSON object to pass to ``kubectl patch`` when the resource is removed.

        :stability: experimental
        '''
        result = self._values.get("restore_patch")
        assert result is not None, "Required property 'restore_patch' is missing"
        return typing.cast(typing.Mapping[builtins.str, typing.Any], result)

    @builtins.property
    def patch_type(self) -> typing.Optional["PatchType"]:
        '''(experimental) The patch type to pass to ``kubectl patch``.

        The default type used by ``kubectl patch`` is "strategic".

        :default: PatchType.STRATEGIC

        :stability: experimental
        '''
        result = self._values.get("patch_type")
        return typing.cast(typing.Optional["PatchType"], result)

    @builtins.property
    def resource_namespace(self) -> typing.Optional[builtins.str]:
        '''(experimental) The kubernetes API namespace.

        :default: "default"

        :stability: experimental
        '''
        result = self._values.get("resource_namespace")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "KubernetesPatchProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class KubernetesVersion(
    metaclass=jsii.JSIIMeta,
    jsii_type="@aws-cdk/aws-eks-v2-alpha.KubernetesVersion",
):
    '''(experimental) Kubernetes cluster version.

    :see: https://docs.aws.amazon.com/eks/latest/userguide/kubernetes-versions.html#kubernetes-release-calendar
    :stability: experimental
    :exampleMetadata: infused

    Example::

        cluster = eks.Cluster(self, "EksAutoCluster",
            version=eks.KubernetesVersion.V1_33,
            default_capacity_type=eks.DefaultCapacityType.AUTOMODE,
            compute=eks.ComputeConfig(
                node_pools=["system", "general-purpose"]
            )
        )
    '''

    @jsii.member(jsii_name="of")
    @builtins.classmethod
    def of(cls, version: builtins.str) -> "KubernetesVersion":
        '''(experimental) Custom cluster version.

        :param version: custom version number.

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d63266ad2e560fe6dfe332fdec56b7db18121e33667f27bf25a1a952eae8a7fa)
            check_type(argname="argument version", value=version, expected_type=type_hints["version"])
        return typing.cast("KubernetesVersion", jsii.sinvoke(cls, "of", [version]))

    @jsii.python.classproperty
    @jsii.member(jsii_name="V1_25")
    def V1_25(cls) -> "KubernetesVersion":
        '''(experimental) Kubernetes version 1.25.

        When creating a ``Cluster`` with this version, you need to also specify the
        ``kubectlLayer`` property with a ``KubectlV25Layer`` from
        ``@aws-cdk/lambda-layer-kubectl-v25``.

        :stability: experimental
        '''
        return typing.cast("KubernetesVersion", jsii.sget(cls, "V1_25"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="V1_26")
    def V1_26(cls) -> "KubernetesVersion":
        '''(experimental) Kubernetes version 1.26.

        When creating a ``Cluster`` with this version, you need to also specify the
        ``kubectlLayer`` property with a ``KubectlV26Layer`` from
        ``@aws-cdk/lambda-layer-kubectl-v26``.

        :stability: experimental
        '''
        return typing.cast("KubernetesVersion", jsii.sget(cls, "V1_26"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="V1_27")
    def V1_27(cls) -> "KubernetesVersion":
        '''(experimental) Kubernetes version 1.27.

        When creating a ``Cluster`` with this version, you need to also specify the
        ``kubectlLayer`` property with a ``KubectlV27Layer`` from
        ``@aws-cdk/lambda-layer-kubectl-v27``.

        :stability: experimental
        '''
        return typing.cast("KubernetesVersion", jsii.sget(cls, "V1_27"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="V1_28")
    def V1_28(cls) -> "KubernetesVersion":
        '''(experimental) Kubernetes version 1.28.

        When creating a ``Cluster`` with this version, you need to also specify the
        ``kubectlLayer`` property with a ``KubectlV28Layer`` from
        ``@aws-cdk/lambda-layer-kubectl-v28``.

        :stability: experimental
        '''
        return typing.cast("KubernetesVersion", jsii.sget(cls, "V1_28"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="V1_29")
    def V1_29(cls) -> "KubernetesVersion":
        '''(experimental) Kubernetes version 1.29.

        When creating a ``Cluster`` with this version, you need to also specify the
        ``kubectlLayer`` property with a ``KubectlV29Layer`` from
        ``@aws-cdk/lambda-layer-kubectl-v29``.

        :stability: experimental
        '''
        return typing.cast("KubernetesVersion", jsii.sget(cls, "V1_29"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="V1_30")
    def V1_30(cls) -> "KubernetesVersion":
        '''(experimental) Kubernetes version 1.30.

        When creating a ``Cluster`` with this version, you need to also specify the
        ``kubectlLayer`` property with a ``KubectlV30Layer`` from
        ``@aws-cdk/lambda-layer-kubectl-v30``.

        :stability: experimental
        '''
        return typing.cast("KubernetesVersion", jsii.sget(cls, "V1_30"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="V1_31")
    def V1_31(cls) -> "KubernetesVersion":
        '''(experimental) Kubernetes version 1.31.

        When creating a ``Cluster`` with this version, you need to also specify the
        ``kubectlLayer`` property with a ``KubectlV31Layer`` from
        ``@aws-cdk/lambda-layer-kubectl-v31``.

        :stability: experimental
        '''
        return typing.cast("KubernetesVersion", jsii.sget(cls, "V1_31"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="V1_32")
    def V1_32(cls) -> "KubernetesVersion":
        '''(experimental) Kubernetes version 1.32.

        When creating a ``Cluster`` with this version, you need to also specify the
        ``kubectlLayer`` property with a ``KubectlV32Layer`` from
        ``@aws-cdk/lambda-layer-kubectl-v32``.

        :stability: experimental
        '''
        return typing.cast("KubernetesVersion", jsii.sget(cls, "V1_32"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="V1_33")
    def V1_33(cls) -> "KubernetesVersion":
        '''(experimental) Kubernetes version 1.33.

        When creating a ``Cluster`` with this version, you need to also specify the
        ``kubectlLayer`` property with a ``KubectlV33Layer`` from
        ``@aws-cdk/lambda-layer-kubectl-v33``.

        :stability: experimental
        '''
        return typing.cast("KubernetesVersion", jsii.sget(cls, "V1_33"))

    @builtins.property
    @jsii.member(jsii_name="version")
    def version(self) -> builtins.str:
        '''(experimental) cluster version number.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "version"))


@jsii.data_type(
    jsii_type="@aws-cdk/aws-eks-v2-alpha.LaunchTemplateSpec",
    jsii_struct_bases=[],
    name_mapping={"id": "id", "version": "version"},
)
class LaunchTemplateSpec:
    def __init__(
        self,
        *,
        id: builtins.str,
        version: typing.Optional[builtins.str] = None,
    ) -> None:
        '''(experimental) Launch template property specification.

        :param id: (experimental) The Launch template ID.
        :param version: (experimental) The launch template version to be used (optional). Default: - the default version of the launch template

        :stability: experimental
        :exampleMetadata: fixture=_generated

        Example::

            # The code below shows an example of how to instantiate this type.
            # The values are placeholders you should change.
            import aws_cdk.aws_eks_v2_alpha as eks_v2_alpha
            
            launch_template_spec = eks_v2_alpha.LaunchTemplateSpec(
                id="id",
            
                # the properties below are optional
                version="version"
            )
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__fa14fa5ca62ae0433f472a1652360ff8e5957789e80aa8f86fdaa0feef3f8416)
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument version", value=version, expected_type=type_hints["version"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "id": id,
        }
        if version is not None:
            self._values["version"] = version

    @builtins.property
    def id(self) -> builtins.str:
        '''(experimental) The Launch template ID.

        :stability: experimental
        '''
        result = self._values.get("id")
        assert result is not None, "Required property 'id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def version(self) -> typing.Optional[builtins.str]:
        '''(experimental) The launch template version to be used (optional).

        :default: - the default version of the launch template

        :stability: experimental
        '''
        result = self._values.get("version")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "LaunchTemplateSpec(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.enum(jsii_type="@aws-cdk/aws-eks-v2-alpha.MachineImageType")
class MachineImageType(enum.Enum):
    '''(experimental) The machine image type.

    :stability: experimental
    '''

    AMAZON_LINUX_2 = "AMAZON_LINUX_2"
    '''(experimental) Amazon EKS-optimized Linux AMI.

    :stability: experimental
    '''
    BOTTLEROCKET = "BOTTLEROCKET"
    '''(experimental) Bottlerocket AMI.

    :stability: experimental
    '''


@jsii.enum(jsii_type="@aws-cdk/aws-eks-v2-alpha.NodeType")
class NodeType(enum.Enum):
    '''(experimental) Whether the worker nodes should support GPU or just standard instances.

    :stability: experimental
    '''

    STANDARD = "STANDARD"
    '''(experimental) Standard instances.

    :stability: experimental
    '''
    GPU = "GPU"
    '''(experimental) GPU instances.

    :stability: experimental
    '''
    INFERENTIA = "INFERENTIA"
    '''(experimental) Inferentia instances.

    :stability: experimental
    '''
    TRAINIUM = "TRAINIUM"
    '''(experimental) Trainium instances.

    :stability: experimental
    '''


@jsii.implements(INodegroup)
class Nodegroup(
    _aws_cdk_ceddda9d.Resource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@aws-cdk/aws-eks-v2-alpha.Nodegroup",
):
    '''(experimental) The Nodegroup resource class.

    :stability: experimental
    :resource: AWS::EKS::Nodegroup
    :exampleMetadata: fixture=_generated

    Example::

        # The code below shows an example of how to instantiate this type.
        # The values are placeholders you should change.
        import aws_cdk.aws_eks_v2_alpha as eks_v2_alpha
        from aws_cdk import aws_ec2 as ec2
        from aws_cdk import aws_iam as iam
        
        # cluster: eks_v2_alpha.Cluster
        # instance_type: ec2.InstanceType
        # role: iam.Role
        # security_group: ec2.SecurityGroup
        # subnet: ec2.Subnet
        # subnet_filter: ec2.SubnetFilter
        
        nodegroup = eks_v2_alpha.Nodegroup(self, "MyNodegroup",
            cluster=cluster,
        
            # the properties below are optional
            ami_type=eks_v2_alpha.NodegroupAmiType.AL2_X86_64,
            capacity_type=eks_v2_alpha.CapacityType.SPOT,
            desired_size=123,
            disk_size=123,
            enable_node_auto_repair=False,
            force_update=False,
            instance_type=instance_type,
            instance_types=[instance_type],
            labels={
                "labels_key": "labels"
            },
            launch_template_spec=eks_v2_alpha.LaunchTemplateSpec(
                id="id",
        
                # the properties below are optional
                version="version"
            ),
            max_size=123,
            max_unavailable=123,
            max_unavailable_percentage=123,
            min_size=123,
            nodegroup_name="nodegroupName",
            node_role=role,
            release_version="releaseVersion",
            remote_access=eks_v2_alpha.NodegroupRemoteAccess(
                ssh_key_name="sshKeyName",
        
                # the properties below are optional
                source_security_groups=[security_group]
            ),
            subnets=ec2.SubnetSelection(
                availability_zones=["availabilityZones"],
                one_per_az=False,
                subnet_filters=[subnet_filter],
                subnet_group_name="subnetGroupName",
                subnets=[subnet],
                subnet_type=ec2.SubnetType.PRIVATE_ISOLATED
            ),
            tags={
                "tags_key": "tags"
            },
            taints=[eks_v2_alpha.TaintSpec(
                effect=eks_v2_alpha.TaintEffect.NO_SCHEDULE,
                key="key",
                value="value"
            )]
        )
    '''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        cluster: ICluster,
        ami_type: typing.Optional["NodegroupAmiType"] = None,
        capacity_type: typing.Optional[CapacityType] = None,
        desired_size: typing.Optional[jsii.Number] = None,
        disk_size: typing.Optional[jsii.Number] = None,
        enable_node_auto_repair: typing.Optional[builtins.bool] = None,
        force_update: typing.Optional[builtins.bool] = None,
        instance_type: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.InstanceType] = None,
        instance_types: typing.Optional[typing.Sequence[_aws_cdk_aws_ec2_ceddda9d.InstanceType]] = None,
        labels: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        launch_template_spec: typing.Optional[typing.Union[LaunchTemplateSpec, typing.Dict[builtins.str, typing.Any]]] = None,
        max_size: typing.Optional[jsii.Number] = None,
        max_unavailable: typing.Optional[jsii.Number] = None,
        max_unavailable_percentage: typing.Optional[jsii.Number] = None,
        min_size: typing.Optional[jsii.Number] = None,
        nodegroup_name: typing.Optional[builtins.str] = None,
        node_role: typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole] = None,
        release_version: typing.Optional[builtins.str] = None,
        remote_access: typing.Optional[typing.Union["NodegroupRemoteAccess", typing.Dict[builtins.str, typing.Any]]] = None,
        subnets: typing.Optional[typing.Union[_aws_cdk_aws_ec2_ceddda9d.SubnetSelection, typing.Dict[builtins.str, typing.Any]]] = None,
        tags: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        taints: typing.Optional[typing.Sequence[typing.Union["TaintSpec", typing.Dict[builtins.str, typing.Any]]]] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param cluster: (experimental) Cluster resource.
        :param ami_type: (experimental) The AMI type for your node group. If you explicitly specify the launchTemplate with custom AMI, do not specify this property, or the node group deployment will fail. In other cases, you will need to specify correct amiType for the nodegroup. Default: - auto-determined from the instanceTypes property when launchTemplateSpec property is not specified
        :param capacity_type: (experimental) The capacity type of the nodegroup. Default: - ON_DEMAND
        :param desired_size: (experimental) The current number of worker nodes that the managed node group should maintain. If not specified, the nodewgroup will initially create ``minSize`` instances. Default: 2
        :param disk_size: (experimental) The root device disk size (in GiB) for your node group instances. Default: 20
        :param enable_node_auto_repair: (experimental) Specifies whether to enable node auto repair for the node group. Node auto repair is disabled by default. Default: - disabled
        :param force_update: (experimental) Force the update if the existing node group's pods are unable to be drained due to a pod disruption budget issue. If an update fails because pods could not be drained, you can force the update after it fails to terminate the old node whether or not any pods are running on the node. Default: true
        :param instance_type: (deprecated) The instance type to use for your node group. Currently, you can specify a single instance type for a node group. The default value for this parameter is ``t3.medium``. If you choose a GPU instance type, be sure to specify the ``AL2_x86_64_GPU``, ``BOTTLEROCKET_ARM_64_NVIDIA``, or ``BOTTLEROCKET_x86_64_NVIDIA`` with the amiType parameter. Default: t3.medium
        :param instance_types: (experimental) The instance types to use for your node group. Default: t3.medium will be used according to the cloudformation document.
        :param labels: (experimental) The Kubernetes labels to be applied to the nodes in the node group when they are created. Default: - None
        :param launch_template_spec: (experimental) Launch template specification used for the nodegroup. Default: - no launch template
        :param max_size: (experimental) The maximum number of worker nodes that the managed node group can scale out to. Managed node groups can support up to 100 nodes by default. Default: - desiredSize
        :param max_unavailable: (experimental) The maximum number of nodes unavailable at once during a version update. Nodes will be updated in parallel. The maximum number is 100. This value or ``maxUnavailablePercentage`` is required to have a value for custom update configurations to be applied. Default: 1
        :param max_unavailable_percentage: (experimental) The maximum percentage of nodes unavailable during a version update. This percentage of nodes will be updated in parallel, up to 100 nodes at once. This value or ``maxUnavailable`` is required to have a value for custom update configurations to be applied. Default: undefined - node groups will update instances one at a time
        :param min_size: (experimental) The minimum number of worker nodes that the managed node group can scale in to. This number must be greater than or equal to zero. Default: 1
        :param nodegroup_name: (experimental) Name of the Nodegroup. Default: - resource ID
        :param node_role: (experimental) The IAM role to associate with your node group. The Amazon EKS worker node kubelet daemon makes calls to AWS APIs on your behalf. Worker nodes receive permissions for these API calls through an IAM instance profile and associated policies. Before you can launch worker nodes and register them into a cluster, you must create an IAM role for those worker nodes to use when they are launched. Default: - None. Auto-generated if not specified.
        :param release_version: (experimental) The AMI version of the Amazon EKS-optimized AMI to use with your node group (for example, ``1.14.7-YYYYMMDD``). Default: - The latest available AMI version for the node group's current Kubernetes version is used.
        :param remote_access: (experimental) The remote access (SSH) configuration to use with your node group. Disabled by default, however, if you specify an Amazon EC2 SSH key but do not specify a source security group when you create a managed node group, then port 22 on the worker nodes is opened to the internet (0.0.0.0/0) Default: - disabled
        :param subnets: (experimental) The subnets to use for the Auto Scaling group that is created for your node group. By specifying the SubnetSelection, the selected subnets will automatically apply required tags i.e. ``kubernetes.io/cluster/CLUSTER_NAME`` with a value of ``shared``, where ``CLUSTER_NAME`` is replaced with the name of your cluster. Default: - private subnets
        :param tags: (experimental) The metadata to apply to the node group to assist with categorization and organization. Each tag consists of a key and an optional value, both of which you define. Node group tags do not propagate to any other resources associated with the node group, such as the Amazon EC2 instances or subnets. Default: - None
        :param taints: (experimental) The Kubernetes taints to be applied to the nodes in the node group when they are created. Default: - None

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__fc8b0755389df345d97a19957b1626674e36777445f00245597a6b40ca83a096)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = NodegroupProps(
            cluster=cluster,
            ami_type=ami_type,
            capacity_type=capacity_type,
            desired_size=desired_size,
            disk_size=disk_size,
            enable_node_auto_repair=enable_node_auto_repair,
            force_update=force_update,
            instance_type=instance_type,
            instance_types=instance_types,
            labels=labels,
            launch_template_spec=launch_template_spec,
            max_size=max_size,
            max_unavailable=max_unavailable,
            max_unavailable_percentage=max_unavailable_percentage,
            min_size=min_size,
            nodegroup_name=nodegroup_name,
            node_role=node_role,
            release_version=release_version,
            remote_access=remote_access,
            subnets=subnets,
            tags=tags,
            taints=taints,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @jsii.member(jsii_name="fromNodegroupName")
    @builtins.classmethod
    def from_nodegroup_name(
        cls,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        nodegroup_name: builtins.str,
    ) -> INodegroup:
        '''(experimental) Import the Nodegroup from attributes.

        :param scope: -
        :param id: -
        :param nodegroup_name: -

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ba37b072ec60d2b3168ea14dba461b6b0b311846e547be16bde6effd1a73a6d5)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument nodegroup_name", value=nodegroup_name, expected_type=type_hints["nodegroup_name"])
        return typing.cast(INodegroup, jsii.sinvoke(cls, "fromNodegroupName", [scope, id, nodegroup_name]))

    @jsii.python.classproperty
    @jsii.member(jsii_name="PROPERTY_INJECTION_ID")
    def PROPERTY_INJECTION_ID(cls) -> builtins.str:
        '''(experimental) Uniquely identifies this class.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "PROPERTY_INJECTION_ID"))

    @builtins.property
    @jsii.member(jsii_name="cluster")
    def cluster(self) -> ICluster:
        '''(experimental) the Amazon EKS cluster resource.

        :stability: experimental
        :attribute: ClusterName
        '''
        return typing.cast(ICluster, jsii.get(self, "cluster"))

    @builtins.property
    @jsii.member(jsii_name="nodegroupArn")
    def nodegroup_arn(self) -> builtins.str:
        '''(experimental) ARN of the nodegroup.

        :stability: experimental
        :attribute: true
        '''
        return typing.cast(builtins.str, jsii.get(self, "nodegroupArn"))

    @builtins.property
    @jsii.member(jsii_name="nodegroupName")
    def nodegroup_name(self) -> builtins.str:
        '''(experimental) Nodegroup name.

        :stability: experimental
        :attribute: true
        '''
        return typing.cast(builtins.str, jsii.get(self, "nodegroupName"))

    @builtins.property
    @jsii.member(jsii_name="role")
    def role(self) -> _aws_cdk_aws_iam_ceddda9d.IRole:
        '''(experimental) IAM role of the instance profile for the nodegroup.

        :stability: experimental
        '''
        return typing.cast(_aws_cdk_aws_iam_ceddda9d.IRole, jsii.get(self, "role"))


@jsii.enum(jsii_type="@aws-cdk/aws-eks-v2-alpha.NodegroupAmiType")
class NodegroupAmiType(enum.Enum):
    '''(experimental) The AMI type for your node group.

    GPU instance types should use the ``AL2_x86_64_GPU`` AMI type, which uses the
    Amazon EKS-optimized Linux AMI with GPU support or the ``BOTTLEROCKET_ARM_64_NVIDIA`` or ``BOTTLEROCKET_X86_64_NVIDIA``
    AMI types, which uses the Amazon EKS-optimized Linux AMI with Nvidia-GPU support.

    Non-GPU instances should use the ``AL2_x86_64`` AMI type, which uses the Amazon EKS-optimized Linux AMI.

    :stability: experimental
    '''

    AL2_X86_64 = "AL2_X86_64"
    '''(experimental) Amazon Linux 2 (x86-64).

    :stability: experimental
    '''
    AL2_X86_64_GPU = "AL2_X86_64_GPU"
    '''(experimental) Amazon Linux 2 with GPU support.

    :stability: experimental
    '''
    AL2_ARM_64 = "AL2_ARM_64"
    '''(experimental) Amazon Linux 2 (ARM-64).

    :stability: experimental
    '''
    BOTTLEROCKET_ARM_64 = "BOTTLEROCKET_ARM_64"
    '''(experimental) Bottlerocket Linux (ARM-64).

    :stability: experimental
    '''
    BOTTLEROCKET_X86_64 = "BOTTLEROCKET_X86_64"
    '''(experimental) Bottlerocket (x86-64).

    :stability: experimental
    '''
    BOTTLEROCKET_ARM_64_NVIDIA = "BOTTLEROCKET_ARM_64_NVIDIA"
    '''(experimental) Bottlerocket Linux with Nvidia-GPU support (ARM-64).

    :stability: experimental
    '''
    BOTTLEROCKET_X86_64_NVIDIA = "BOTTLEROCKET_X86_64_NVIDIA"
    '''(experimental) Bottlerocket with Nvidia-GPU support (x86-64).

    :stability: experimental
    '''
    BOTTLEROCKET_ARM_64_FIPS = "BOTTLEROCKET_ARM_64_FIPS"
    '''(experimental) Bottlerocket Linux (ARM-64) with FIPS enabled.

    :stability: experimental
    '''
    BOTTLEROCKET_X86_64_FIPS = "BOTTLEROCKET_X86_64_FIPS"
    '''(experimental) Bottlerocket (x86-64) with FIPS enabled.

    :stability: experimental
    '''
    WINDOWS_CORE_2019_X86_64 = "WINDOWS_CORE_2019_X86_64"
    '''(experimental) Windows Core 2019 (x86-64).

    :stability: experimental
    '''
    WINDOWS_CORE_2022_X86_64 = "WINDOWS_CORE_2022_X86_64"
    '''(experimental) Windows Core 2022 (x86-64).

    :stability: experimental
    '''
    WINDOWS_FULL_2019_X86_64 = "WINDOWS_FULL_2019_X86_64"
    '''(experimental) Windows Full 2019 (x86-64).

    :stability: experimental
    '''
    WINDOWS_FULL_2022_X86_64 = "WINDOWS_FULL_2022_X86_64"
    '''(experimental) Windows Full 2022 (x86-64).

    :stability: experimental
    '''
    AL2023_X86_64_STANDARD = "AL2023_X86_64_STANDARD"
    '''(experimental) Amazon Linux 2023 (x86-64).

    :stability: experimental
    '''
    AL2023_X86_64_NEURON = "AL2023_X86_64_NEURON"
    '''(experimental) Amazon Linux 2023 with AWS Neuron drivers (x86-64).

    :stability: experimental
    '''
    AL2023_X86_64_NVIDIA = "AL2023_X86_64_NVIDIA"
    '''(experimental) Amazon Linux 2023 with NVIDIA drivers (x86-64).

    :stability: experimental
    '''
    AL2023_ARM_64_STANDARD = "AL2023_ARM_64_STANDARD"
    '''(experimental) Amazon Linux 2023 (ARM-64).

    :stability: experimental
    '''


@jsii.data_type(
    jsii_type="@aws-cdk/aws-eks-v2-alpha.NodegroupOptions",
    jsii_struct_bases=[],
    name_mapping={
        "ami_type": "amiType",
        "capacity_type": "capacityType",
        "desired_size": "desiredSize",
        "disk_size": "diskSize",
        "enable_node_auto_repair": "enableNodeAutoRepair",
        "force_update": "forceUpdate",
        "instance_type": "instanceType",
        "instance_types": "instanceTypes",
        "labels": "labels",
        "launch_template_spec": "launchTemplateSpec",
        "max_size": "maxSize",
        "max_unavailable": "maxUnavailable",
        "max_unavailable_percentage": "maxUnavailablePercentage",
        "min_size": "minSize",
        "nodegroup_name": "nodegroupName",
        "node_role": "nodeRole",
        "release_version": "releaseVersion",
        "remote_access": "remoteAccess",
        "subnets": "subnets",
        "tags": "tags",
        "taints": "taints",
    },
)
class NodegroupOptions:
    def __init__(
        self,
        *,
        ami_type: typing.Optional[NodegroupAmiType] = None,
        capacity_type: typing.Optional[CapacityType] = None,
        desired_size: typing.Optional[jsii.Number] = None,
        disk_size: typing.Optional[jsii.Number] = None,
        enable_node_auto_repair: typing.Optional[builtins.bool] = None,
        force_update: typing.Optional[builtins.bool] = None,
        instance_type: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.InstanceType] = None,
        instance_types: typing.Optional[typing.Sequence[_aws_cdk_aws_ec2_ceddda9d.InstanceType]] = None,
        labels: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        launch_template_spec: typing.Optional[typing.Union[LaunchTemplateSpec, typing.Dict[builtins.str, typing.Any]]] = None,
        max_size: typing.Optional[jsii.Number] = None,
        max_unavailable: typing.Optional[jsii.Number] = None,
        max_unavailable_percentage: typing.Optional[jsii.Number] = None,
        min_size: typing.Optional[jsii.Number] = None,
        nodegroup_name: typing.Optional[builtins.str] = None,
        node_role: typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole] = None,
        release_version: typing.Optional[builtins.str] = None,
        remote_access: typing.Optional[typing.Union["NodegroupRemoteAccess", typing.Dict[builtins.str, typing.Any]]] = None,
        subnets: typing.Optional[typing.Union[_aws_cdk_aws_ec2_ceddda9d.SubnetSelection, typing.Dict[builtins.str, typing.Any]]] = None,
        tags: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        taints: typing.Optional[typing.Sequence[typing.Union["TaintSpec", typing.Dict[builtins.str, typing.Any]]]] = None,
    ) -> None:
        '''(experimental) The Nodegroup Options for addNodeGroup() method.

        :param ami_type: (experimental) The AMI type for your node group. If you explicitly specify the launchTemplate with custom AMI, do not specify this property, or the node group deployment will fail. In other cases, you will need to specify correct amiType for the nodegroup. Default: - auto-determined from the instanceTypes property when launchTemplateSpec property is not specified
        :param capacity_type: (experimental) The capacity type of the nodegroup. Default: - ON_DEMAND
        :param desired_size: (experimental) The current number of worker nodes that the managed node group should maintain. If not specified, the nodewgroup will initially create ``minSize`` instances. Default: 2
        :param disk_size: (experimental) The root device disk size (in GiB) for your node group instances. Default: 20
        :param enable_node_auto_repair: (experimental) Specifies whether to enable node auto repair for the node group. Node auto repair is disabled by default. Default: - disabled
        :param force_update: (experimental) Force the update if the existing node group's pods are unable to be drained due to a pod disruption budget issue. If an update fails because pods could not be drained, you can force the update after it fails to terminate the old node whether or not any pods are running on the node. Default: true
        :param instance_type: (deprecated) The instance type to use for your node group. Currently, you can specify a single instance type for a node group. The default value for this parameter is ``t3.medium``. If you choose a GPU instance type, be sure to specify the ``AL2_x86_64_GPU``, ``BOTTLEROCKET_ARM_64_NVIDIA``, or ``BOTTLEROCKET_x86_64_NVIDIA`` with the amiType parameter. Default: t3.medium
        :param instance_types: (experimental) The instance types to use for your node group. Default: t3.medium will be used according to the cloudformation document.
        :param labels: (experimental) The Kubernetes labels to be applied to the nodes in the node group when they are created. Default: - None
        :param launch_template_spec: (experimental) Launch template specification used for the nodegroup. Default: - no launch template
        :param max_size: (experimental) The maximum number of worker nodes that the managed node group can scale out to. Managed node groups can support up to 100 nodes by default. Default: - desiredSize
        :param max_unavailable: (experimental) The maximum number of nodes unavailable at once during a version update. Nodes will be updated in parallel. The maximum number is 100. This value or ``maxUnavailablePercentage`` is required to have a value for custom update configurations to be applied. Default: 1
        :param max_unavailable_percentage: (experimental) The maximum percentage of nodes unavailable during a version update. This percentage of nodes will be updated in parallel, up to 100 nodes at once. This value or ``maxUnavailable`` is required to have a value for custom update configurations to be applied. Default: undefined - node groups will update instances one at a time
        :param min_size: (experimental) The minimum number of worker nodes that the managed node group can scale in to. This number must be greater than or equal to zero. Default: 1
        :param nodegroup_name: (experimental) Name of the Nodegroup. Default: - resource ID
        :param node_role: (experimental) The IAM role to associate with your node group. The Amazon EKS worker node kubelet daemon makes calls to AWS APIs on your behalf. Worker nodes receive permissions for these API calls through an IAM instance profile and associated policies. Before you can launch worker nodes and register them into a cluster, you must create an IAM role for those worker nodes to use when they are launched. Default: - None. Auto-generated if not specified.
        :param release_version: (experimental) The AMI version of the Amazon EKS-optimized AMI to use with your node group (for example, ``1.14.7-YYYYMMDD``). Default: - The latest available AMI version for the node group's current Kubernetes version is used.
        :param remote_access: (experimental) The remote access (SSH) configuration to use with your node group. Disabled by default, however, if you specify an Amazon EC2 SSH key but do not specify a source security group when you create a managed node group, then port 22 on the worker nodes is opened to the internet (0.0.0.0/0) Default: - disabled
        :param subnets: (experimental) The subnets to use for the Auto Scaling group that is created for your node group. By specifying the SubnetSelection, the selected subnets will automatically apply required tags i.e. ``kubernetes.io/cluster/CLUSTER_NAME`` with a value of ``shared``, where ``CLUSTER_NAME`` is replaced with the name of your cluster. Default: - private subnets
        :param tags: (experimental) The metadata to apply to the node group to assist with categorization and organization. Each tag consists of a key and an optional value, both of which you define. Node group tags do not propagate to any other resources associated with the node group, such as the Amazon EC2 instances or subnets. Default: - None
        :param taints: (experimental) The Kubernetes taints to be applied to the nodes in the node group when they are created. Default: - None

        :stability: experimental
        :exampleMetadata: infused

        Example::

            cluster = eks.Cluster(self, "HelloEKS",
                version=eks.KubernetesVersion.V1_33,
                default_capacity_type=eks.DefaultCapacityType.NODEGROUP,
                default_capacity=0
            )
            
            cluster.add_nodegroup_capacity("custom-node-group",
                instance_types=[ec2.InstanceType("m5.large")],
                min_size=4,
                disk_size=100
            )
        '''
        if isinstance(launch_template_spec, dict):
            launch_template_spec = LaunchTemplateSpec(**launch_template_spec)
        if isinstance(remote_access, dict):
            remote_access = NodegroupRemoteAccess(**remote_access)
        if isinstance(subnets, dict):
            subnets = _aws_cdk_aws_ec2_ceddda9d.SubnetSelection(**subnets)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9f3bb52aa005520d24284a00deee84fca7e8c4afe54a8bdd40771517f0d53904)
            check_type(argname="argument ami_type", value=ami_type, expected_type=type_hints["ami_type"])
            check_type(argname="argument capacity_type", value=capacity_type, expected_type=type_hints["capacity_type"])
            check_type(argname="argument desired_size", value=desired_size, expected_type=type_hints["desired_size"])
            check_type(argname="argument disk_size", value=disk_size, expected_type=type_hints["disk_size"])
            check_type(argname="argument enable_node_auto_repair", value=enable_node_auto_repair, expected_type=type_hints["enable_node_auto_repair"])
            check_type(argname="argument force_update", value=force_update, expected_type=type_hints["force_update"])
            check_type(argname="argument instance_type", value=instance_type, expected_type=type_hints["instance_type"])
            check_type(argname="argument instance_types", value=instance_types, expected_type=type_hints["instance_types"])
            check_type(argname="argument labels", value=labels, expected_type=type_hints["labels"])
            check_type(argname="argument launch_template_spec", value=launch_template_spec, expected_type=type_hints["launch_template_spec"])
            check_type(argname="argument max_size", value=max_size, expected_type=type_hints["max_size"])
            check_type(argname="argument max_unavailable", value=max_unavailable, expected_type=type_hints["max_unavailable"])
            check_type(argname="argument max_unavailable_percentage", value=max_unavailable_percentage, expected_type=type_hints["max_unavailable_percentage"])
            check_type(argname="argument min_size", value=min_size, expected_type=type_hints["min_size"])
            check_type(argname="argument nodegroup_name", value=nodegroup_name, expected_type=type_hints["nodegroup_name"])
            check_type(argname="argument node_role", value=node_role, expected_type=type_hints["node_role"])
            check_type(argname="argument release_version", value=release_version, expected_type=type_hints["release_version"])
            check_type(argname="argument remote_access", value=remote_access, expected_type=type_hints["remote_access"])
            check_type(argname="argument subnets", value=subnets, expected_type=type_hints["subnets"])
            check_type(argname="argument tags", value=tags, expected_type=type_hints["tags"])
            check_type(argname="argument taints", value=taints, expected_type=type_hints["taints"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if ami_type is not None:
            self._values["ami_type"] = ami_type
        if capacity_type is not None:
            self._values["capacity_type"] = capacity_type
        if desired_size is not None:
            self._values["desired_size"] = desired_size
        if disk_size is not None:
            self._values["disk_size"] = disk_size
        if enable_node_auto_repair is not None:
            self._values["enable_node_auto_repair"] = enable_node_auto_repair
        if force_update is not None:
            self._values["force_update"] = force_update
        if instance_type is not None:
            self._values["instance_type"] = instance_type
        if instance_types is not None:
            self._values["instance_types"] = instance_types
        if labels is not None:
            self._values["labels"] = labels
        if launch_template_spec is not None:
            self._values["launch_template_spec"] = launch_template_spec
        if max_size is not None:
            self._values["max_size"] = max_size
        if max_unavailable is not None:
            self._values["max_unavailable"] = max_unavailable
        if max_unavailable_percentage is not None:
            self._values["max_unavailable_percentage"] = max_unavailable_percentage
        if min_size is not None:
            self._values["min_size"] = min_size
        if nodegroup_name is not None:
            self._values["nodegroup_name"] = nodegroup_name
        if node_role is not None:
            self._values["node_role"] = node_role
        if release_version is not None:
            self._values["release_version"] = release_version
        if remote_access is not None:
            self._values["remote_access"] = remote_access
        if subnets is not None:
            self._values["subnets"] = subnets
        if tags is not None:
            self._values["tags"] = tags
        if taints is not None:
            self._values["taints"] = taints

    @builtins.property
    def ami_type(self) -> typing.Optional[NodegroupAmiType]:
        '''(experimental) The AMI type for your node group.

        If you explicitly specify the launchTemplate with custom AMI, do not specify this property, or
        the node group deployment will fail. In other cases, you will need to specify correct amiType for the nodegroup.

        :default: - auto-determined from the instanceTypes property when launchTemplateSpec property is not specified

        :stability: experimental
        '''
        result = self._values.get("ami_type")
        return typing.cast(typing.Optional[NodegroupAmiType], result)

    @builtins.property
    def capacity_type(self) -> typing.Optional[CapacityType]:
        '''(experimental) The capacity type of the nodegroup.

        :default: - ON_DEMAND

        :stability: experimental
        '''
        result = self._values.get("capacity_type")
        return typing.cast(typing.Optional[CapacityType], result)

    @builtins.property
    def desired_size(self) -> typing.Optional[jsii.Number]:
        '''(experimental) The current number of worker nodes that the managed node group should maintain.

        If not specified,
        the nodewgroup will initially create ``minSize`` instances.

        :default: 2

        :stability: experimental
        '''
        result = self._values.get("desired_size")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def disk_size(self) -> typing.Optional[jsii.Number]:
        '''(experimental) The root device disk size (in GiB) for your node group instances.

        :default: 20

        :stability: experimental
        '''
        result = self._values.get("disk_size")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def enable_node_auto_repair(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Specifies whether to enable node auto repair for the node group.

        Node auto repair is disabled by default.

        :default: - disabled

        :see: https://docs.aws.amazon.com/eks/latest/userguide/node-health.html#node-auto-repair
        :stability: experimental
        '''
        result = self._values.get("enable_node_auto_repair")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def force_update(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Force the update if the existing node group's pods are unable to be drained due to a pod disruption budget issue.

        If an update fails because pods could not be drained, you can force the update after it fails to terminate the old
        node whether or not any pods are
        running on the node.

        :default: true

        :stability: experimental
        '''
        result = self._values.get("force_update")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def instance_type(self) -> typing.Optional[_aws_cdk_aws_ec2_ceddda9d.InstanceType]:
        '''(deprecated) The instance type to use for your node group.

        Currently, you can specify a single instance type for a node group.
        The default value for this parameter is ``t3.medium``. If you choose a GPU instance type, be sure to specify the
        ``AL2_x86_64_GPU``, ``BOTTLEROCKET_ARM_64_NVIDIA``, or ``BOTTLEROCKET_x86_64_NVIDIA`` with the amiType parameter.

        :default: t3.medium

        :deprecated: Use ``instanceTypes`` instead.

        :stability: deprecated
        '''
        result = self._values.get("instance_type")
        return typing.cast(typing.Optional[_aws_cdk_aws_ec2_ceddda9d.InstanceType], result)

    @builtins.property
    def instance_types(
        self,
    ) -> typing.Optional[typing.List[_aws_cdk_aws_ec2_ceddda9d.InstanceType]]:
        '''(experimental) The instance types to use for your node group.

        :default: t3.medium will be used according to the cloudformation document.

        :see: https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-eks-nodegroup.html#cfn-eks-nodegroup-instancetypes
        :stability: experimental
        '''
        result = self._values.get("instance_types")
        return typing.cast(typing.Optional[typing.List[_aws_cdk_aws_ec2_ceddda9d.InstanceType]], result)

    @builtins.property
    def labels(self) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        '''(experimental) The Kubernetes labels to be applied to the nodes in the node group when they are created.

        :default: - None

        :stability: experimental
        '''
        result = self._values.get("labels")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], result)

    @builtins.property
    def launch_template_spec(self) -> typing.Optional[LaunchTemplateSpec]:
        '''(experimental) Launch template specification used for the nodegroup.

        :default: - no launch template

        :see: https://docs.aws.amazon.com/eks/latest/userguide/launch-templates.html
        :stability: experimental
        '''
        result = self._values.get("launch_template_spec")
        return typing.cast(typing.Optional[LaunchTemplateSpec], result)

    @builtins.property
    def max_size(self) -> typing.Optional[jsii.Number]:
        '''(experimental) The maximum number of worker nodes that the managed node group can scale out to.

        Managed node groups can support up to 100 nodes by default.

        :default: - desiredSize

        :stability: experimental
        '''
        result = self._values.get("max_size")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def max_unavailable(self) -> typing.Optional[jsii.Number]:
        '''(experimental) The maximum number of nodes unavailable at once during a version update.

        Nodes will be updated in parallel. The maximum number is 100.

        This value or ``maxUnavailablePercentage`` is required to have a value for custom update configurations to be applied.

        :default: 1

        :see: https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-eks-nodegroup-updateconfig.html#cfn-eks-nodegroup-updateconfig-maxunavailable
        :stability: experimental
        '''
        result = self._values.get("max_unavailable")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def max_unavailable_percentage(self) -> typing.Optional[jsii.Number]:
        '''(experimental) The maximum percentage of nodes unavailable during a version update.

        This percentage of nodes will be updated in parallel, up to 100 nodes at once.

        This value or ``maxUnavailable`` is required to have a value for custom update configurations to be applied.

        :default: undefined - node groups will update instances one at a time

        :see: https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-eks-nodegroup-updateconfig.html#cfn-eks-nodegroup-updateconfig-maxunavailablepercentage
        :stability: experimental
        '''
        result = self._values.get("max_unavailable_percentage")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def min_size(self) -> typing.Optional[jsii.Number]:
        '''(experimental) The minimum number of worker nodes that the managed node group can scale in to.

        This number must be greater than or equal to zero.

        :default: 1

        :stability: experimental
        '''
        result = self._values.get("min_size")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def nodegroup_name(self) -> typing.Optional[builtins.str]:
        '''(experimental) Name of the Nodegroup.

        :default: - resource ID

        :stability: experimental
        '''
        result = self._values.get("nodegroup_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def node_role(self) -> typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole]:
        '''(experimental) The IAM role to associate with your node group.

        The Amazon EKS worker node kubelet daemon
        makes calls to AWS APIs on your behalf. Worker nodes receive permissions for these API calls through
        an IAM instance profile and associated policies. Before you can launch worker nodes and register them
        into a cluster, you must create an IAM role for those worker nodes to use when they are launched.

        :default: - None. Auto-generated if not specified.

        :stability: experimental
        '''
        result = self._values.get("node_role")
        return typing.cast(typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole], result)

    @builtins.property
    def release_version(self) -> typing.Optional[builtins.str]:
        '''(experimental) The AMI version of the Amazon EKS-optimized AMI to use with your node group (for example, ``1.14.7-YYYYMMDD``).

        :default: - The latest available AMI version for the node group's current Kubernetes version is used.

        :stability: experimental
        '''
        result = self._values.get("release_version")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def remote_access(self) -> typing.Optional["NodegroupRemoteAccess"]:
        '''(experimental) The remote access (SSH) configuration to use with your node group.

        Disabled by default, however, if you
        specify an Amazon EC2 SSH key but do not specify a source security group when you create a managed node group,
        then port 22 on the worker nodes is opened to the internet (0.0.0.0/0)

        :default: - disabled

        :stability: experimental
        '''
        result = self._values.get("remote_access")
        return typing.cast(typing.Optional["NodegroupRemoteAccess"], result)

    @builtins.property
    def subnets(self) -> typing.Optional[_aws_cdk_aws_ec2_ceddda9d.SubnetSelection]:
        '''(experimental) The subnets to use for the Auto Scaling group that is created for your node group.

        By specifying the
        SubnetSelection, the selected subnets will automatically apply required tags i.e.
        ``kubernetes.io/cluster/CLUSTER_NAME`` with a value of ``shared``, where ``CLUSTER_NAME`` is replaced with
        the name of your cluster.

        :default: - private subnets

        :stability: experimental
        '''
        result = self._values.get("subnets")
        return typing.cast(typing.Optional[_aws_cdk_aws_ec2_ceddda9d.SubnetSelection], result)

    @builtins.property
    def tags(self) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        '''(experimental) The metadata to apply to the node group to assist with categorization and organization.

        Each tag consists of
        a key and an optional value, both of which you define. Node group tags do not propagate to any other resources
        associated with the node group, such as the Amazon EC2 instances or subnets.

        :default: - None

        :stability: experimental
        '''
        result = self._values.get("tags")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], result)

    @builtins.property
    def taints(self) -> typing.Optional[typing.List["TaintSpec"]]:
        '''(experimental) The Kubernetes taints to be applied to the nodes in the node group when they are created.

        :default: - None

        :stability: experimental
        '''
        result = self._values.get("taints")
        return typing.cast(typing.Optional[typing.List["TaintSpec"]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "NodegroupOptions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@aws-cdk/aws-eks-v2-alpha.NodegroupProps",
    jsii_struct_bases=[NodegroupOptions],
    name_mapping={
        "ami_type": "amiType",
        "capacity_type": "capacityType",
        "desired_size": "desiredSize",
        "disk_size": "diskSize",
        "enable_node_auto_repair": "enableNodeAutoRepair",
        "force_update": "forceUpdate",
        "instance_type": "instanceType",
        "instance_types": "instanceTypes",
        "labels": "labels",
        "launch_template_spec": "launchTemplateSpec",
        "max_size": "maxSize",
        "max_unavailable": "maxUnavailable",
        "max_unavailable_percentage": "maxUnavailablePercentage",
        "min_size": "minSize",
        "nodegroup_name": "nodegroupName",
        "node_role": "nodeRole",
        "release_version": "releaseVersion",
        "remote_access": "remoteAccess",
        "subnets": "subnets",
        "tags": "tags",
        "taints": "taints",
        "cluster": "cluster",
    },
)
class NodegroupProps(NodegroupOptions):
    def __init__(
        self,
        *,
        ami_type: typing.Optional[NodegroupAmiType] = None,
        capacity_type: typing.Optional[CapacityType] = None,
        desired_size: typing.Optional[jsii.Number] = None,
        disk_size: typing.Optional[jsii.Number] = None,
        enable_node_auto_repair: typing.Optional[builtins.bool] = None,
        force_update: typing.Optional[builtins.bool] = None,
        instance_type: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.InstanceType] = None,
        instance_types: typing.Optional[typing.Sequence[_aws_cdk_aws_ec2_ceddda9d.InstanceType]] = None,
        labels: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        launch_template_spec: typing.Optional[typing.Union[LaunchTemplateSpec, typing.Dict[builtins.str, typing.Any]]] = None,
        max_size: typing.Optional[jsii.Number] = None,
        max_unavailable: typing.Optional[jsii.Number] = None,
        max_unavailable_percentage: typing.Optional[jsii.Number] = None,
        min_size: typing.Optional[jsii.Number] = None,
        nodegroup_name: typing.Optional[builtins.str] = None,
        node_role: typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole] = None,
        release_version: typing.Optional[builtins.str] = None,
        remote_access: typing.Optional[typing.Union["NodegroupRemoteAccess", typing.Dict[builtins.str, typing.Any]]] = None,
        subnets: typing.Optional[typing.Union[_aws_cdk_aws_ec2_ceddda9d.SubnetSelection, typing.Dict[builtins.str, typing.Any]]] = None,
        tags: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        taints: typing.Optional[typing.Sequence[typing.Union["TaintSpec", typing.Dict[builtins.str, typing.Any]]]] = None,
        cluster: ICluster,
    ) -> None:
        '''(experimental) NodeGroup properties interface.

        :param ami_type: (experimental) The AMI type for your node group. If you explicitly specify the launchTemplate with custom AMI, do not specify this property, or the node group deployment will fail. In other cases, you will need to specify correct amiType for the nodegroup. Default: - auto-determined from the instanceTypes property when launchTemplateSpec property is not specified
        :param capacity_type: (experimental) The capacity type of the nodegroup. Default: - ON_DEMAND
        :param desired_size: (experimental) The current number of worker nodes that the managed node group should maintain. If not specified, the nodewgroup will initially create ``minSize`` instances. Default: 2
        :param disk_size: (experimental) The root device disk size (in GiB) for your node group instances. Default: 20
        :param enable_node_auto_repair: (experimental) Specifies whether to enable node auto repair for the node group. Node auto repair is disabled by default. Default: - disabled
        :param force_update: (experimental) Force the update if the existing node group's pods are unable to be drained due to a pod disruption budget issue. If an update fails because pods could not be drained, you can force the update after it fails to terminate the old node whether or not any pods are running on the node. Default: true
        :param instance_type: (deprecated) The instance type to use for your node group. Currently, you can specify a single instance type for a node group. The default value for this parameter is ``t3.medium``. If you choose a GPU instance type, be sure to specify the ``AL2_x86_64_GPU``, ``BOTTLEROCKET_ARM_64_NVIDIA``, or ``BOTTLEROCKET_x86_64_NVIDIA`` with the amiType parameter. Default: t3.medium
        :param instance_types: (experimental) The instance types to use for your node group. Default: t3.medium will be used according to the cloudformation document.
        :param labels: (experimental) The Kubernetes labels to be applied to the nodes in the node group when they are created. Default: - None
        :param launch_template_spec: (experimental) Launch template specification used for the nodegroup. Default: - no launch template
        :param max_size: (experimental) The maximum number of worker nodes that the managed node group can scale out to. Managed node groups can support up to 100 nodes by default. Default: - desiredSize
        :param max_unavailable: (experimental) The maximum number of nodes unavailable at once during a version update. Nodes will be updated in parallel. The maximum number is 100. This value or ``maxUnavailablePercentage`` is required to have a value for custom update configurations to be applied. Default: 1
        :param max_unavailable_percentage: (experimental) The maximum percentage of nodes unavailable during a version update. This percentage of nodes will be updated in parallel, up to 100 nodes at once. This value or ``maxUnavailable`` is required to have a value for custom update configurations to be applied. Default: undefined - node groups will update instances one at a time
        :param min_size: (experimental) The minimum number of worker nodes that the managed node group can scale in to. This number must be greater than or equal to zero. Default: 1
        :param nodegroup_name: (experimental) Name of the Nodegroup. Default: - resource ID
        :param node_role: (experimental) The IAM role to associate with your node group. The Amazon EKS worker node kubelet daemon makes calls to AWS APIs on your behalf. Worker nodes receive permissions for these API calls through an IAM instance profile and associated policies. Before you can launch worker nodes and register them into a cluster, you must create an IAM role for those worker nodes to use when they are launched. Default: - None. Auto-generated if not specified.
        :param release_version: (experimental) The AMI version of the Amazon EKS-optimized AMI to use with your node group (for example, ``1.14.7-YYYYMMDD``). Default: - The latest available AMI version for the node group's current Kubernetes version is used.
        :param remote_access: (experimental) The remote access (SSH) configuration to use with your node group. Disabled by default, however, if you specify an Amazon EC2 SSH key but do not specify a source security group when you create a managed node group, then port 22 on the worker nodes is opened to the internet (0.0.0.0/0) Default: - disabled
        :param subnets: (experimental) The subnets to use for the Auto Scaling group that is created for your node group. By specifying the SubnetSelection, the selected subnets will automatically apply required tags i.e. ``kubernetes.io/cluster/CLUSTER_NAME`` with a value of ``shared``, where ``CLUSTER_NAME`` is replaced with the name of your cluster. Default: - private subnets
        :param tags: (experimental) The metadata to apply to the node group to assist with categorization and organization. Each tag consists of a key and an optional value, both of which you define. Node group tags do not propagate to any other resources associated with the node group, such as the Amazon EC2 instances or subnets. Default: - None
        :param taints: (experimental) The Kubernetes taints to be applied to the nodes in the node group when they are created. Default: - None
        :param cluster: (experimental) Cluster resource.

        :stability: experimental
        :exampleMetadata: fixture=_generated

        Example::

            # The code below shows an example of how to instantiate this type.
            # The values are placeholders you should change.
            import aws_cdk.aws_eks_v2_alpha as eks_v2_alpha
            from aws_cdk import aws_ec2 as ec2
            from aws_cdk import aws_iam as iam
            
            # cluster: eks_v2_alpha.Cluster
            # instance_type: ec2.InstanceType
            # role: iam.Role
            # security_group: ec2.SecurityGroup
            # subnet: ec2.Subnet
            # subnet_filter: ec2.SubnetFilter
            
            nodegroup_props = eks_v2_alpha.NodegroupProps(
                cluster=cluster,
            
                # the properties below are optional
                ami_type=eks_v2_alpha.NodegroupAmiType.AL2_X86_64,
                capacity_type=eks_v2_alpha.CapacityType.SPOT,
                desired_size=123,
                disk_size=123,
                enable_node_auto_repair=False,
                force_update=False,
                instance_type=instance_type,
                instance_types=[instance_type],
                labels={
                    "labels_key": "labels"
                },
                launch_template_spec=eks_v2_alpha.LaunchTemplateSpec(
                    id="id",
            
                    # the properties below are optional
                    version="version"
                ),
                max_size=123,
                max_unavailable=123,
                max_unavailable_percentage=123,
                min_size=123,
                nodegroup_name="nodegroupName",
                node_role=role,
                release_version="releaseVersion",
                remote_access=eks_v2_alpha.NodegroupRemoteAccess(
                    ssh_key_name="sshKeyName",
            
                    # the properties below are optional
                    source_security_groups=[security_group]
                ),
                subnets=ec2.SubnetSelection(
                    availability_zones=["availabilityZones"],
                    one_per_az=False,
                    subnet_filters=[subnet_filter],
                    subnet_group_name="subnetGroupName",
                    subnets=[subnet],
                    subnet_type=ec2.SubnetType.PRIVATE_ISOLATED
                ),
                tags={
                    "tags_key": "tags"
                },
                taints=[eks_v2_alpha.TaintSpec(
                    effect=eks_v2_alpha.TaintEffect.NO_SCHEDULE,
                    key="key",
                    value="value"
                )]
            )
        '''
        if isinstance(launch_template_spec, dict):
            launch_template_spec = LaunchTemplateSpec(**launch_template_spec)
        if isinstance(remote_access, dict):
            remote_access = NodegroupRemoteAccess(**remote_access)
        if isinstance(subnets, dict):
            subnets = _aws_cdk_aws_ec2_ceddda9d.SubnetSelection(**subnets)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1eebacdf94f3e813ed7347b7e8a9a3d1a5527b9a5a2d8f9ef83d77bc6fd8b442)
            check_type(argname="argument ami_type", value=ami_type, expected_type=type_hints["ami_type"])
            check_type(argname="argument capacity_type", value=capacity_type, expected_type=type_hints["capacity_type"])
            check_type(argname="argument desired_size", value=desired_size, expected_type=type_hints["desired_size"])
            check_type(argname="argument disk_size", value=disk_size, expected_type=type_hints["disk_size"])
            check_type(argname="argument enable_node_auto_repair", value=enable_node_auto_repair, expected_type=type_hints["enable_node_auto_repair"])
            check_type(argname="argument force_update", value=force_update, expected_type=type_hints["force_update"])
            check_type(argname="argument instance_type", value=instance_type, expected_type=type_hints["instance_type"])
            check_type(argname="argument instance_types", value=instance_types, expected_type=type_hints["instance_types"])
            check_type(argname="argument labels", value=labels, expected_type=type_hints["labels"])
            check_type(argname="argument launch_template_spec", value=launch_template_spec, expected_type=type_hints["launch_template_spec"])
            check_type(argname="argument max_size", value=max_size, expected_type=type_hints["max_size"])
            check_type(argname="argument max_unavailable", value=max_unavailable, expected_type=type_hints["max_unavailable"])
            check_type(argname="argument max_unavailable_percentage", value=max_unavailable_percentage, expected_type=type_hints["max_unavailable_percentage"])
            check_type(argname="argument min_size", value=min_size, expected_type=type_hints["min_size"])
            check_type(argname="argument nodegroup_name", value=nodegroup_name, expected_type=type_hints["nodegroup_name"])
            check_type(argname="argument node_role", value=node_role, expected_type=type_hints["node_role"])
            check_type(argname="argument release_version", value=release_version, expected_type=type_hints["release_version"])
            check_type(argname="argument remote_access", value=remote_access, expected_type=type_hints["remote_access"])
            check_type(argname="argument subnets", value=subnets, expected_type=type_hints["subnets"])
            check_type(argname="argument tags", value=tags, expected_type=type_hints["tags"])
            check_type(argname="argument taints", value=taints, expected_type=type_hints["taints"])
            check_type(argname="argument cluster", value=cluster, expected_type=type_hints["cluster"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "cluster": cluster,
        }
        if ami_type is not None:
            self._values["ami_type"] = ami_type
        if capacity_type is not None:
            self._values["capacity_type"] = capacity_type
        if desired_size is not None:
            self._values["desired_size"] = desired_size
        if disk_size is not None:
            self._values["disk_size"] = disk_size
        if enable_node_auto_repair is not None:
            self._values["enable_node_auto_repair"] = enable_node_auto_repair
        if force_update is not None:
            self._values["force_update"] = force_update
        if instance_type is not None:
            self._values["instance_type"] = instance_type
        if instance_types is not None:
            self._values["instance_types"] = instance_types
        if labels is not None:
            self._values["labels"] = labels
        if launch_template_spec is not None:
            self._values["launch_template_spec"] = launch_template_spec
        if max_size is not None:
            self._values["max_size"] = max_size
        if max_unavailable is not None:
            self._values["max_unavailable"] = max_unavailable
        if max_unavailable_percentage is not None:
            self._values["max_unavailable_percentage"] = max_unavailable_percentage
        if min_size is not None:
            self._values["min_size"] = min_size
        if nodegroup_name is not None:
            self._values["nodegroup_name"] = nodegroup_name
        if node_role is not None:
            self._values["node_role"] = node_role
        if release_version is not None:
            self._values["release_version"] = release_version
        if remote_access is not None:
            self._values["remote_access"] = remote_access
        if subnets is not None:
            self._values["subnets"] = subnets
        if tags is not None:
            self._values["tags"] = tags
        if taints is not None:
            self._values["taints"] = taints

    @builtins.property
    def ami_type(self) -> typing.Optional[NodegroupAmiType]:
        '''(experimental) The AMI type for your node group.

        If you explicitly specify the launchTemplate with custom AMI, do not specify this property, or
        the node group deployment will fail. In other cases, you will need to specify correct amiType for the nodegroup.

        :default: - auto-determined from the instanceTypes property when launchTemplateSpec property is not specified

        :stability: experimental
        '''
        result = self._values.get("ami_type")
        return typing.cast(typing.Optional[NodegroupAmiType], result)

    @builtins.property
    def capacity_type(self) -> typing.Optional[CapacityType]:
        '''(experimental) The capacity type of the nodegroup.

        :default: - ON_DEMAND

        :stability: experimental
        '''
        result = self._values.get("capacity_type")
        return typing.cast(typing.Optional[CapacityType], result)

    @builtins.property
    def desired_size(self) -> typing.Optional[jsii.Number]:
        '''(experimental) The current number of worker nodes that the managed node group should maintain.

        If not specified,
        the nodewgroup will initially create ``minSize`` instances.

        :default: 2

        :stability: experimental
        '''
        result = self._values.get("desired_size")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def disk_size(self) -> typing.Optional[jsii.Number]:
        '''(experimental) The root device disk size (in GiB) for your node group instances.

        :default: 20

        :stability: experimental
        '''
        result = self._values.get("disk_size")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def enable_node_auto_repair(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Specifies whether to enable node auto repair for the node group.

        Node auto repair is disabled by default.

        :default: - disabled

        :see: https://docs.aws.amazon.com/eks/latest/userguide/node-health.html#node-auto-repair
        :stability: experimental
        '''
        result = self._values.get("enable_node_auto_repair")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def force_update(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Force the update if the existing node group's pods are unable to be drained due to a pod disruption budget issue.

        If an update fails because pods could not be drained, you can force the update after it fails to terminate the old
        node whether or not any pods are
        running on the node.

        :default: true

        :stability: experimental
        '''
        result = self._values.get("force_update")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def instance_type(self) -> typing.Optional[_aws_cdk_aws_ec2_ceddda9d.InstanceType]:
        '''(deprecated) The instance type to use for your node group.

        Currently, you can specify a single instance type for a node group.
        The default value for this parameter is ``t3.medium``. If you choose a GPU instance type, be sure to specify the
        ``AL2_x86_64_GPU``, ``BOTTLEROCKET_ARM_64_NVIDIA``, or ``BOTTLEROCKET_x86_64_NVIDIA`` with the amiType parameter.

        :default: t3.medium

        :deprecated: Use ``instanceTypes`` instead.

        :stability: deprecated
        '''
        result = self._values.get("instance_type")
        return typing.cast(typing.Optional[_aws_cdk_aws_ec2_ceddda9d.InstanceType], result)

    @builtins.property
    def instance_types(
        self,
    ) -> typing.Optional[typing.List[_aws_cdk_aws_ec2_ceddda9d.InstanceType]]:
        '''(experimental) The instance types to use for your node group.

        :default: t3.medium will be used according to the cloudformation document.

        :see: https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-eks-nodegroup.html#cfn-eks-nodegroup-instancetypes
        :stability: experimental
        '''
        result = self._values.get("instance_types")
        return typing.cast(typing.Optional[typing.List[_aws_cdk_aws_ec2_ceddda9d.InstanceType]], result)

    @builtins.property
    def labels(self) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        '''(experimental) The Kubernetes labels to be applied to the nodes in the node group when they are created.

        :default: - None

        :stability: experimental
        '''
        result = self._values.get("labels")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], result)

    @builtins.property
    def launch_template_spec(self) -> typing.Optional[LaunchTemplateSpec]:
        '''(experimental) Launch template specification used for the nodegroup.

        :default: - no launch template

        :see: https://docs.aws.amazon.com/eks/latest/userguide/launch-templates.html
        :stability: experimental
        '''
        result = self._values.get("launch_template_spec")
        return typing.cast(typing.Optional[LaunchTemplateSpec], result)

    @builtins.property
    def max_size(self) -> typing.Optional[jsii.Number]:
        '''(experimental) The maximum number of worker nodes that the managed node group can scale out to.

        Managed node groups can support up to 100 nodes by default.

        :default: - desiredSize

        :stability: experimental
        '''
        result = self._values.get("max_size")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def max_unavailable(self) -> typing.Optional[jsii.Number]:
        '''(experimental) The maximum number of nodes unavailable at once during a version update.

        Nodes will be updated in parallel. The maximum number is 100.

        This value or ``maxUnavailablePercentage`` is required to have a value for custom update configurations to be applied.

        :default: 1

        :see: https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-eks-nodegroup-updateconfig.html#cfn-eks-nodegroup-updateconfig-maxunavailable
        :stability: experimental
        '''
        result = self._values.get("max_unavailable")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def max_unavailable_percentage(self) -> typing.Optional[jsii.Number]:
        '''(experimental) The maximum percentage of nodes unavailable during a version update.

        This percentage of nodes will be updated in parallel, up to 100 nodes at once.

        This value or ``maxUnavailable`` is required to have a value for custom update configurations to be applied.

        :default: undefined - node groups will update instances one at a time

        :see: https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-eks-nodegroup-updateconfig.html#cfn-eks-nodegroup-updateconfig-maxunavailablepercentage
        :stability: experimental
        '''
        result = self._values.get("max_unavailable_percentage")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def min_size(self) -> typing.Optional[jsii.Number]:
        '''(experimental) The minimum number of worker nodes that the managed node group can scale in to.

        This number must be greater than or equal to zero.

        :default: 1

        :stability: experimental
        '''
        result = self._values.get("min_size")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def nodegroup_name(self) -> typing.Optional[builtins.str]:
        '''(experimental) Name of the Nodegroup.

        :default: - resource ID

        :stability: experimental
        '''
        result = self._values.get("nodegroup_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def node_role(self) -> typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole]:
        '''(experimental) The IAM role to associate with your node group.

        The Amazon EKS worker node kubelet daemon
        makes calls to AWS APIs on your behalf. Worker nodes receive permissions for these API calls through
        an IAM instance profile and associated policies. Before you can launch worker nodes and register them
        into a cluster, you must create an IAM role for those worker nodes to use when they are launched.

        :default: - None. Auto-generated if not specified.

        :stability: experimental
        '''
        result = self._values.get("node_role")
        return typing.cast(typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole], result)

    @builtins.property
    def release_version(self) -> typing.Optional[builtins.str]:
        '''(experimental) The AMI version of the Amazon EKS-optimized AMI to use with your node group (for example, ``1.14.7-YYYYMMDD``).

        :default: - The latest available AMI version for the node group's current Kubernetes version is used.

        :stability: experimental
        '''
        result = self._values.get("release_version")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def remote_access(self) -> typing.Optional["NodegroupRemoteAccess"]:
        '''(experimental) The remote access (SSH) configuration to use with your node group.

        Disabled by default, however, if you
        specify an Amazon EC2 SSH key but do not specify a source security group when you create a managed node group,
        then port 22 on the worker nodes is opened to the internet (0.0.0.0/0)

        :default: - disabled

        :stability: experimental
        '''
        result = self._values.get("remote_access")
        return typing.cast(typing.Optional["NodegroupRemoteAccess"], result)

    @builtins.property
    def subnets(self) -> typing.Optional[_aws_cdk_aws_ec2_ceddda9d.SubnetSelection]:
        '''(experimental) The subnets to use for the Auto Scaling group that is created for your node group.

        By specifying the
        SubnetSelection, the selected subnets will automatically apply required tags i.e.
        ``kubernetes.io/cluster/CLUSTER_NAME`` with a value of ``shared``, where ``CLUSTER_NAME`` is replaced with
        the name of your cluster.

        :default: - private subnets

        :stability: experimental
        '''
        result = self._values.get("subnets")
        return typing.cast(typing.Optional[_aws_cdk_aws_ec2_ceddda9d.SubnetSelection], result)

    @builtins.property
    def tags(self) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        '''(experimental) The metadata to apply to the node group to assist with categorization and organization.

        Each tag consists of
        a key and an optional value, both of which you define. Node group tags do not propagate to any other resources
        associated with the node group, such as the Amazon EC2 instances or subnets.

        :default: - None

        :stability: experimental
        '''
        result = self._values.get("tags")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], result)

    @builtins.property
    def taints(self) -> typing.Optional[typing.List["TaintSpec"]]:
        '''(experimental) The Kubernetes taints to be applied to the nodes in the node group when they are created.

        :default: - None

        :stability: experimental
        '''
        result = self._values.get("taints")
        return typing.cast(typing.Optional[typing.List["TaintSpec"]], result)

    @builtins.property
    def cluster(self) -> ICluster:
        '''(experimental) Cluster resource.

        :stability: experimental
        '''
        result = self._values.get("cluster")
        assert result is not None, "Required property 'cluster' is missing"
        return typing.cast(ICluster, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "NodegroupProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@aws-cdk/aws-eks-v2-alpha.NodegroupRemoteAccess",
    jsii_struct_bases=[],
    name_mapping={
        "ssh_key_name": "sshKeyName",
        "source_security_groups": "sourceSecurityGroups",
    },
)
class NodegroupRemoteAccess:
    def __init__(
        self,
        *,
        ssh_key_name: builtins.str,
        source_security_groups: typing.Optional[typing.Sequence[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup]] = None,
    ) -> None:
        '''(experimental) The remote access (SSH) configuration to use with your node group.

        :param ssh_key_name: (experimental) The Amazon EC2 SSH key that provides access for SSH communication with the worker nodes in the managed node group.
        :param source_security_groups: (experimental) The security groups that are allowed SSH access (port 22) to the worker nodes. If you specify an Amazon EC2 SSH key but do not specify a source security group when you create a managed node group, then port 22 on the worker nodes is opened to the internet (0.0.0.0/0). Default: - port 22 on the worker nodes is opened to the internet (0.0.0.0/0)

        :see: https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-eks-nodegroup-remoteaccess.html
        :stability: experimental
        :exampleMetadata: fixture=_generated

        Example::

            # The code below shows an example of how to instantiate this type.
            # The values are placeholders you should change.
            import aws_cdk.aws_eks_v2_alpha as eks_v2_alpha
            from aws_cdk import aws_ec2 as ec2
            
            # security_group: ec2.SecurityGroup
            
            nodegroup_remote_access = eks_v2_alpha.NodegroupRemoteAccess(
                ssh_key_name="sshKeyName",
            
                # the properties below are optional
                source_security_groups=[security_group]
            )
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7e2d48859c362dd7583430ca612f6286dff54e738afd7db71bb5614a75b195c8)
            check_type(argname="argument ssh_key_name", value=ssh_key_name, expected_type=type_hints["ssh_key_name"])
            check_type(argname="argument source_security_groups", value=source_security_groups, expected_type=type_hints["source_security_groups"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "ssh_key_name": ssh_key_name,
        }
        if source_security_groups is not None:
            self._values["source_security_groups"] = source_security_groups

    @builtins.property
    def ssh_key_name(self) -> builtins.str:
        '''(experimental) The Amazon EC2 SSH key that provides access for SSH communication with the worker nodes in the managed node group.

        :stability: experimental
        '''
        result = self._values.get("ssh_key_name")
        assert result is not None, "Required property 'ssh_key_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def source_security_groups(
        self,
    ) -> typing.Optional[typing.List[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup]]:
        '''(experimental) The security groups that are allowed SSH access (port 22) to the worker nodes.

        If you specify an Amazon EC2 SSH
        key but do not specify a source security group when you create a managed node group, then port 22 on the worker
        nodes is opened to the internet (0.0.0.0/0).

        :default: - port 22 on the worker nodes is opened to the internet (0.0.0.0/0)

        :stability: experimental
        '''
        result = self._values.get("source_security_groups")
        return typing.cast(typing.Optional[typing.List[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "NodegroupRemoteAccess(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class OpenIdConnectProvider(
    _aws_cdk_aws_iam_ceddda9d.OpenIdConnectProvider,
    metaclass=jsii.JSIIMeta,
    jsii_type="@aws-cdk/aws-eks-v2-alpha.OpenIdConnectProvider",
):
    '''(experimental) IAM OIDC identity providers are entities in IAM that describe an external identity provider (IdP) service that supports the OpenID Connect (OIDC) standard, such as Google or Salesforce.

    You use an IAM OIDC identity provider
    when you want to establish trust between an OIDC-compatible IdP and your AWS
    account.

    This implementation has default values for thumbprints and clientIds props
    that will be compatible with the eks cluster

    :see: https://docs.aws.amazon.com/IAM/latest/UserGuide/id_roles_providers_oidc.html
    :stability: experimental
    :resource: AWS::CloudFormation::CustomResource
    :exampleMetadata: fixture=_generated

    Example::

        # The code below shows an example of how to instantiate this type.
        # The values are placeholders you should change.
        import aws_cdk.aws_eks_v2_alpha as eks_v2_alpha
        
        open_id_connect_provider = eks_v2_alpha.OpenIdConnectProvider(self, "MyOpenIdConnectProvider",
            url="url"
        )
    '''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        url: builtins.str,
    ) -> None:
        '''(experimental) Defines an OpenID Connect provider.

        :param scope: The definition scope.
        :param id: Construct ID.
        :param url: (experimental) The URL of the identity provider. The URL must begin with https:// and should correspond to the iss claim in the provider's OpenID Connect ID tokens. Per the OIDC standard, path components are allowed but query parameters are not. Typically the URL consists of only a hostname, like https://server.example.org or https://example.com. You can find your OIDC Issuer URL by: aws eks describe-cluster --name %cluster_name% --query "cluster.identity.oidc.issuer" --output text

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ff947c100a9f93eae1804845d85376aa51e32fdc8dfbb887925e502cb46615fa)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = OpenIdConnectProviderProps(url=url)

        jsii.create(self.__class__, self, [scope, id, props])

    @jsii.python.classproperty
    @jsii.member(jsii_name="PROPERTY_INJECTION_ID")
    def PROPERTY_INJECTION_ID(cls) -> builtins.str:
        '''(experimental) Uniquely identifies this class.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "PROPERTY_INJECTION_ID"))


@jsii.data_type(
    jsii_type="@aws-cdk/aws-eks-v2-alpha.OpenIdConnectProviderProps",
    jsii_struct_bases=[],
    name_mapping={"url": "url"},
)
class OpenIdConnectProviderProps:
    def __init__(self, *, url: builtins.str) -> None:
        '''(experimental) Initialization properties for ``OpenIdConnectProvider``.

        :param url: (experimental) The URL of the identity provider. The URL must begin with https:// and should correspond to the iss claim in the provider's OpenID Connect ID tokens. Per the OIDC standard, path components are allowed but query parameters are not. Typically the URL consists of only a hostname, like https://server.example.org or https://example.com. You can find your OIDC Issuer URL by: aws eks describe-cluster --name %cluster_name% --query "cluster.identity.oidc.issuer" --output text

        :stability: experimental
        :exampleMetadata: fixture=_generated

        Example::

            # The code below shows an example of how to instantiate this type.
            # The values are placeholders you should change.
            import aws_cdk.aws_eks_v2_alpha as eks_v2_alpha
            
            open_id_connect_provider_props = eks_v2_alpha.OpenIdConnectProviderProps(
                url="url"
            )
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e51c0e0b152fc05e514c652e218aa91a83ae3d3ffd37ce3c81cc7ef7aa158ea6)
            check_type(argname="argument url", value=url, expected_type=type_hints["url"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "url": url,
        }

    @builtins.property
    def url(self) -> builtins.str:
        '''(experimental) The URL of the identity provider.

        The URL must begin with https:// and
        should correspond to the iss claim in the provider's OpenID Connect ID
        tokens. Per the OIDC standard, path components are allowed but query
        parameters are not. Typically the URL consists of only a hostname, like
        https://server.example.org or https://example.com.

        You can find your OIDC Issuer URL by:
        aws eks describe-cluster --name %cluster_name% --query "cluster.identity.oidc.issuer" --output text

        :stability: experimental
        '''
        result = self._values.get("url")
        assert result is not None, "Required property 'url' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "OpenIdConnectProviderProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.enum(jsii_type="@aws-cdk/aws-eks-v2-alpha.PatchType")
class PatchType(enum.Enum):
    '''(experimental) Values for ``kubectl patch`` --type argument.

    :stability: experimental
    '''

    JSON = "JSON"
    '''(experimental) JSON Patch, RFC 6902.

    :stability: experimental
    '''
    MERGE = "MERGE"
    '''(experimental) JSON Merge patch.

    :stability: experimental
    '''
    STRATEGIC = "STRATEGIC"
    '''(experimental) Strategic merge patch.

    :stability: experimental
    '''


@jsii.data_type(
    jsii_type="@aws-cdk/aws-eks-v2-alpha.Selector",
    jsii_struct_bases=[],
    name_mapping={"namespace": "namespace", "labels": "labels"},
)
class Selector:
    def __init__(
        self,
        *,
        namespace: builtins.str,
        labels: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    ) -> None:
        '''(experimental) Fargate profile selector.

        :param namespace: (experimental) The Kubernetes namespace that the selector should match. You must specify a namespace for a selector. The selector only matches pods that are created in this namespace, but you can create multiple selectors to target multiple namespaces.
        :param labels: (experimental) The Kubernetes labels that the selector should match. A pod must contain all of the labels that are specified in the selector for it to be considered a match. Default: - all pods within the namespace will be selected.

        :stability: experimental
        :exampleMetadata: fixture=_generated

        Example::

            # The code below shows an example of how to instantiate this type.
            # The values are placeholders you should change.
            import aws_cdk.aws_eks_v2_alpha as eks_v2_alpha
            
            selector = eks_v2_alpha.Selector(
                namespace="namespace",
            
                # the properties below are optional
                labels={
                    "labels_key": "labels"
                }
            )
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9911766762b7aab73e519cbbd248d7c596d3fc57d9bb6c5111982ceac3893b38)
            check_type(argname="argument namespace", value=namespace, expected_type=type_hints["namespace"])
            check_type(argname="argument labels", value=labels, expected_type=type_hints["labels"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "namespace": namespace,
        }
        if labels is not None:
            self._values["labels"] = labels

    @builtins.property
    def namespace(self) -> builtins.str:
        '''(experimental) The Kubernetes namespace that the selector should match.

        You must specify a namespace for a selector. The selector only matches pods
        that are created in this namespace, but you can create multiple selectors
        to target multiple namespaces.

        :stability: experimental
        '''
        result = self._values.get("namespace")
        assert result is not None, "Required property 'namespace' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def labels(self) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        '''(experimental) The Kubernetes labels that the selector should match.

        A pod must contain
        all of the labels that are specified in the selector for it to be
        considered a match.

        :default: - all pods within the namespace will be selected.

        :stability: experimental
        '''
        result = self._values.get("labels")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "Selector(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.implements(_aws_cdk_aws_iam_ceddda9d.IPrincipal)
class ServiceAccount(
    _constructs_77d1e7e8.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="@aws-cdk/aws-eks-v2-alpha.ServiceAccount",
):
    '''(experimental) Service Account.

    :stability: experimental
    :exampleMetadata: fixture=_generated

    Example::

        # The code below shows an example of how to instantiate this type.
        # The values are placeholders you should change.
        import aws_cdk.aws_eks_v2_alpha as eks_v2_alpha
        
        # cluster: eks_v2_alpha.Cluster
        
        service_account = eks_v2_alpha.ServiceAccount(self, "MyServiceAccount",
            cluster=cluster,
        
            # the properties below are optional
            annotations={
                "annotations_key": "annotations"
            },
            identity_type=eks_v2_alpha.IdentityType.IRSA,
            labels={
                "labels_key": "labels"
            },
            name="name",
            namespace="namespace"
        )
    '''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        cluster: ICluster,
        annotations: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        identity_type: typing.Optional[IdentityType] = None,
        labels: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        name: typing.Optional[builtins.str] = None,
        namespace: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param cluster: (experimental) The cluster to apply the patch to.
        :param annotations: (experimental) Additional annotations of the service account. Default: - no additional annotations
        :param identity_type: (experimental) The identity type to use for the service account. Default: IdentityType.IRSA
        :param labels: (experimental) Additional labels of the service account. Default: - no additional labels
        :param name: (experimental) The name of the service account. The name of a ServiceAccount object must be a valid DNS subdomain name. https://kubernetes.io/docs/tasks/configure-pod-container/configure-service-account/ Default: - If no name is given, it will use the id of the resource.
        :param namespace: (experimental) The namespace of the service account. All namespace names must be valid RFC 1123 DNS labels. https://kubernetes.io/docs/concepts/overview/working-with-objects/namespaces/#namespaces-and-dns Default: "default"

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__59d2cd5450f84e9b32d879613fee8749090a043d987b87cb3f41235259318083)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = ServiceAccountProps(
            cluster=cluster,
            annotations=annotations,
            identity_type=identity_type,
            labels=labels,
            name=name,
            namespace=namespace,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @jsii.member(jsii_name="addToPolicy")
    def add_to_policy(
        self,
        statement: _aws_cdk_aws_iam_ceddda9d.PolicyStatement,
    ) -> builtins.bool:
        '''
        :param statement: -

        :deprecated: use ``addToPrincipalPolicy()``

        :stability: deprecated
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9354abb1e4d2f8a5301e08be5aee342f6dba512efb916f84bf95a8ac5bc0edd9)
            check_type(argname="argument statement", value=statement, expected_type=type_hints["statement"])
        return typing.cast(builtins.bool, jsii.invoke(self, "addToPolicy", [statement]))

    @jsii.member(jsii_name="addToPrincipalPolicy")
    def add_to_principal_policy(
        self,
        statement: _aws_cdk_aws_iam_ceddda9d.PolicyStatement,
    ) -> _aws_cdk_aws_iam_ceddda9d.AddToPrincipalPolicyResult:
        '''(experimental) Add to the policy of this principal.

        :param statement: -

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__100d788900bbaab34be52e0189b4ff18d53d1a8f3f871d71d199b39f885f7053)
            check_type(argname="argument statement", value=statement, expected_type=type_hints["statement"])
        return typing.cast(_aws_cdk_aws_iam_ceddda9d.AddToPrincipalPolicyResult, jsii.invoke(self, "addToPrincipalPolicy", [statement]))

    @builtins.property
    @jsii.member(jsii_name="assumeRoleAction")
    def assume_role_action(self) -> builtins.str:
        '''(experimental) When this Principal is used in an AssumeRole policy, the action to use.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "assumeRoleAction"))

    @builtins.property
    @jsii.member(jsii_name="grantPrincipal")
    def grant_principal(self) -> _aws_cdk_aws_iam_ceddda9d.IPrincipal:
        '''(experimental) The principal to grant permissions to.

        :stability: experimental
        '''
        return typing.cast(_aws_cdk_aws_iam_ceddda9d.IPrincipal, jsii.get(self, "grantPrincipal"))

    @builtins.property
    @jsii.member(jsii_name="policyFragment")
    def policy_fragment(self) -> _aws_cdk_aws_iam_ceddda9d.PrincipalPolicyFragment:
        '''(experimental) Return the policy fragment that identifies this principal in a Policy.

        :stability: experimental
        '''
        return typing.cast(_aws_cdk_aws_iam_ceddda9d.PrincipalPolicyFragment, jsii.get(self, "policyFragment"))

    @builtins.property
    @jsii.member(jsii_name="role")
    def role(self) -> _aws_cdk_aws_iam_ceddda9d.IRole:
        '''(experimental) The role which is linked to the service account.

        :stability: experimental
        '''
        return typing.cast(_aws_cdk_aws_iam_ceddda9d.IRole, jsii.get(self, "role"))

    @builtins.property
    @jsii.member(jsii_name="serviceAccountName")
    def service_account_name(self) -> builtins.str:
        '''(experimental) The name of the service account.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "serviceAccountName"))

    @builtins.property
    @jsii.member(jsii_name="serviceAccountNamespace")
    def service_account_namespace(self) -> builtins.str:
        '''(experimental) The namespace where the service account is located in.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "serviceAccountNamespace"))


@jsii.data_type(
    jsii_type="@aws-cdk/aws-eks-v2-alpha.ServiceAccountOptions",
    jsii_struct_bases=[],
    name_mapping={
        "annotations": "annotations",
        "identity_type": "identityType",
        "labels": "labels",
        "name": "name",
        "namespace": "namespace",
    },
)
class ServiceAccountOptions:
    def __init__(
        self,
        *,
        annotations: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        identity_type: typing.Optional[IdentityType] = None,
        labels: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        name: typing.Optional[builtins.str] = None,
        namespace: typing.Optional[builtins.str] = None,
    ) -> None:
        '''(experimental) Options for ``ServiceAccount``.

        :param annotations: (experimental) Additional annotations of the service account. Default: - no additional annotations
        :param identity_type: (experimental) The identity type to use for the service account. Default: IdentityType.IRSA
        :param labels: (experimental) Additional labels of the service account. Default: - no additional labels
        :param name: (experimental) The name of the service account. The name of a ServiceAccount object must be a valid DNS subdomain name. https://kubernetes.io/docs/tasks/configure-pod-container/configure-service-account/ Default: - If no name is given, it will use the id of the resource.
        :param namespace: (experimental) The namespace of the service account. All namespace names must be valid RFC 1123 DNS labels. https://kubernetes.io/docs/concepts/overview/working-with-objects/namespaces/#namespaces-and-dns Default: "default"

        :stability: experimental
        :exampleMetadata: fixture=_generated

        Example::

            # The code below shows an example of how to instantiate this type.
            # The values are placeholders you should change.
            import aws_cdk.aws_eks_v2_alpha as eks_v2_alpha
            
            service_account_options = eks_v2_alpha.ServiceAccountOptions(
                annotations={
                    "annotations_key": "annotations"
                },
                identity_type=eks_v2_alpha.IdentityType.IRSA,
                labels={
                    "labels_key": "labels"
                },
                name="name",
                namespace="namespace"
            )
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b8aeba614d1b7fb1055e46177bab0671bb8b977ba1fb52885245e6ee59b7d8af)
            check_type(argname="argument annotations", value=annotations, expected_type=type_hints["annotations"])
            check_type(argname="argument identity_type", value=identity_type, expected_type=type_hints["identity_type"])
            check_type(argname="argument labels", value=labels, expected_type=type_hints["labels"])
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument namespace", value=namespace, expected_type=type_hints["namespace"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if annotations is not None:
            self._values["annotations"] = annotations
        if identity_type is not None:
            self._values["identity_type"] = identity_type
        if labels is not None:
            self._values["labels"] = labels
        if name is not None:
            self._values["name"] = name
        if namespace is not None:
            self._values["namespace"] = namespace

    @builtins.property
    def annotations(
        self,
    ) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        '''(experimental) Additional annotations of the service account.

        :default: - no additional annotations

        :stability: experimental
        '''
        result = self._values.get("annotations")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], result)

    @builtins.property
    def identity_type(self) -> typing.Optional[IdentityType]:
        '''(experimental) The identity type to use for the service account.

        :default: IdentityType.IRSA

        :stability: experimental
        '''
        result = self._values.get("identity_type")
        return typing.cast(typing.Optional[IdentityType], result)

    @builtins.property
    def labels(self) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        '''(experimental) Additional labels of the service account.

        :default: - no additional labels

        :stability: experimental
        '''
        result = self._values.get("labels")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], result)

    @builtins.property
    def name(self) -> typing.Optional[builtins.str]:
        '''(experimental) The name of the service account.

        The name of a ServiceAccount object must be a valid DNS subdomain name.
        https://kubernetes.io/docs/tasks/configure-pod-container/configure-service-account/

        :default: - If no name is given, it will use the id of the resource.

        :stability: experimental
        '''
        result = self._values.get("name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def namespace(self) -> typing.Optional[builtins.str]:
        '''(experimental) The namespace of the service account.

        All namespace names must be valid RFC 1123 DNS labels.
        https://kubernetes.io/docs/concepts/overview/working-with-objects/namespaces/#namespaces-and-dns

        :default: "default"

        :stability: experimental
        '''
        result = self._values.get("namespace")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ServiceAccountOptions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@aws-cdk/aws-eks-v2-alpha.ServiceAccountProps",
    jsii_struct_bases=[ServiceAccountOptions],
    name_mapping={
        "annotations": "annotations",
        "identity_type": "identityType",
        "labels": "labels",
        "name": "name",
        "namespace": "namespace",
        "cluster": "cluster",
    },
)
class ServiceAccountProps(ServiceAccountOptions):
    def __init__(
        self,
        *,
        annotations: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        identity_type: typing.Optional[IdentityType] = None,
        labels: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        name: typing.Optional[builtins.str] = None,
        namespace: typing.Optional[builtins.str] = None,
        cluster: ICluster,
    ) -> None:
        '''(experimental) Properties for defining service accounts.

        :param annotations: (experimental) Additional annotations of the service account. Default: - no additional annotations
        :param identity_type: (experimental) The identity type to use for the service account. Default: IdentityType.IRSA
        :param labels: (experimental) Additional labels of the service account. Default: - no additional labels
        :param name: (experimental) The name of the service account. The name of a ServiceAccount object must be a valid DNS subdomain name. https://kubernetes.io/docs/tasks/configure-pod-container/configure-service-account/ Default: - If no name is given, it will use the id of the resource.
        :param namespace: (experimental) The namespace of the service account. All namespace names must be valid RFC 1123 DNS labels. https://kubernetes.io/docs/concepts/overview/working-with-objects/namespaces/#namespaces-and-dns Default: "default"
        :param cluster: (experimental) The cluster to apply the patch to.

        :stability: experimental
        :exampleMetadata: fixture=_generated

        Example::

            # The code below shows an example of how to instantiate this type.
            # The values are placeholders you should change.
            import aws_cdk.aws_eks_v2_alpha as eks_v2_alpha
            
            # cluster: eks_v2_alpha.Cluster
            
            service_account_props = eks_v2_alpha.ServiceAccountProps(
                cluster=cluster,
            
                # the properties below are optional
                annotations={
                    "annotations_key": "annotations"
                },
                identity_type=eks_v2_alpha.IdentityType.IRSA,
                labels={
                    "labels_key": "labels"
                },
                name="name",
                namespace="namespace"
            )
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__072f92804a73eaaceb4eaa101eddd03353373a90b6e44c6b0370811577a1994b)
            check_type(argname="argument annotations", value=annotations, expected_type=type_hints["annotations"])
            check_type(argname="argument identity_type", value=identity_type, expected_type=type_hints["identity_type"])
            check_type(argname="argument labels", value=labels, expected_type=type_hints["labels"])
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument namespace", value=namespace, expected_type=type_hints["namespace"])
            check_type(argname="argument cluster", value=cluster, expected_type=type_hints["cluster"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "cluster": cluster,
        }
        if annotations is not None:
            self._values["annotations"] = annotations
        if identity_type is not None:
            self._values["identity_type"] = identity_type
        if labels is not None:
            self._values["labels"] = labels
        if name is not None:
            self._values["name"] = name
        if namespace is not None:
            self._values["namespace"] = namespace

    @builtins.property
    def annotations(
        self,
    ) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        '''(experimental) Additional annotations of the service account.

        :default: - no additional annotations

        :stability: experimental
        '''
        result = self._values.get("annotations")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], result)

    @builtins.property
    def identity_type(self) -> typing.Optional[IdentityType]:
        '''(experimental) The identity type to use for the service account.

        :default: IdentityType.IRSA

        :stability: experimental
        '''
        result = self._values.get("identity_type")
        return typing.cast(typing.Optional[IdentityType], result)

    @builtins.property
    def labels(self) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        '''(experimental) Additional labels of the service account.

        :default: - no additional labels

        :stability: experimental
        '''
        result = self._values.get("labels")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], result)

    @builtins.property
    def name(self) -> typing.Optional[builtins.str]:
        '''(experimental) The name of the service account.

        The name of a ServiceAccount object must be a valid DNS subdomain name.
        https://kubernetes.io/docs/tasks/configure-pod-container/configure-service-account/

        :default: - If no name is given, it will use the id of the resource.

        :stability: experimental
        '''
        result = self._values.get("name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def namespace(self) -> typing.Optional[builtins.str]:
        '''(experimental) The namespace of the service account.

        All namespace names must be valid RFC 1123 DNS labels.
        https://kubernetes.io/docs/concepts/overview/working-with-objects/namespaces/#namespaces-and-dns

        :default: "default"

        :stability: experimental
        '''
        result = self._values.get("namespace")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def cluster(self) -> ICluster:
        '''(experimental) The cluster to apply the patch to.

        :stability: experimental
        '''
        result = self._values.get("cluster")
        assert result is not None, "Required property 'cluster' is missing"
        return typing.cast(ICluster, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ServiceAccountProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@aws-cdk/aws-eks-v2-alpha.ServiceLoadBalancerAddressOptions",
    jsii_struct_bases=[],
    name_mapping={"namespace": "namespace", "timeout": "timeout"},
)
class ServiceLoadBalancerAddressOptions:
    def __init__(
        self,
        *,
        namespace: typing.Optional[builtins.str] = None,
        timeout: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
    ) -> None:
        '''(experimental) Options for fetching a ServiceLoadBalancerAddress.

        :param namespace: (experimental) The namespace the service belongs to. Default: 'default'
        :param timeout: (experimental) Timeout for waiting on the load balancer address. Default: Duration.minutes(5)

        :stability: experimental
        :exampleMetadata: fixture=_generated

        Example::

            # The code below shows an example of how to instantiate this type.
            # The values are placeholders you should change.
            import aws_cdk.aws_eks_v2_alpha as eks_v2_alpha
            import aws_cdk as cdk
            
            service_load_balancer_address_options = eks_v2_alpha.ServiceLoadBalancerAddressOptions(
                namespace="namespace",
                timeout=cdk.Duration.minutes(30)
            )
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__375437ae14574762dafcddb85a25a9451aa14c4728ce35f797cdeb227139785a)
            check_type(argname="argument namespace", value=namespace, expected_type=type_hints["namespace"])
            check_type(argname="argument timeout", value=timeout, expected_type=type_hints["timeout"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if namespace is not None:
            self._values["namespace"] = namespace
        if timeout is not None:
            self._values["timeout"] = timeout

    @builtins.property
    def namespace(self) -> typing.Optional[builtins.str]:
        '''(experimental) The namespace the service belongs to.

        :default: 'default'

        :stability: experimental
        '''
        result = self._values.get("namespace")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def timeout(self) -> typing.Optional[_aws_cdk_ceddda9d.Duration]:
        '''(experimental) Timeout for waiting on the load balancer address.

        :default: Duration.minutes(5)

        :stability: experimental
        '''
        result = self._values.get("timeout")
        return typing.cast(typing.Optional[_aws_cdk_ceddda9d.Duration], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ServiceLoadBalancerAddressOptions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.enum(jsii_type="@aws-cdk/aws-eks-v2-alpha.TaintEffect")
class TaintEffect(enum.Enum):
    '''(experimental) Effect types of kubernetes node taint.

    Note: These values are specifically for AWS EKS NodeGroups and use the AWS API format.
    When using AWS CLI or API, taint effects must be NO_SCHEDULE, PREFER_NO_SCHEDULE, or NO_EXECUTE.
    When using Kubernetes directly or kubectl, taint effects must be NoSchedule, PreferNoSchedule, or NoExecute.

    For Kubernetes manifests (like Karpenter NodePools), use string literals with PascalCase format:

    - 'NoSchedule' instead of TaintEffect.NO_SCHEDULE
    - 'PreferNoSchedule' instead of TaintEffect.PREFER_NO_SCHEDULE
    - 'NoExecute' instead of TaintEffect.NO_EXECUTE

    :see: https://docs.aws.amazon.com/eks/latest/userguide/node-taints-managed-node-groups.html
    :stability: experimental
    '''

    NO_SCHEDULE = "NO_SCHEDULE"
    '''(experimental) NoSchedule.

    :stability: experimental
    '''
    PREFER_NO_SCHEDULE = "PREFER_NO_SCHEDULE"
    '''(experimental) PreferNoSchedule.

    :stability: experimental
    '''
    NO_EXECUTE = "NO_EXECUTE"
    '''(experimental) NoExecute.

    :stability: experimental
    '''


@jsii.data_type(
    jsii_type="@aws-cdk/aws-eks-v2-alpha.TaintSpec",
    jsii_struct_bases=[],
    name_mapping={"effect": "effect", "key": "key", "value": "value"},
)
class TaintSpec:
    def __init__(
        self,
        *,
        effect: typing.Optional[TaintEffect] = None,
        key: typing.Optional[builtins.str] = None,
        value: typing.Optional[builtins.str] = None,
    ) -> None:
        '''(experimental) Taint interface.

        :param effect: (experimental) Effect type. Default: - None
        :param key: (experimental) Taint key. Default: - None
        :param value: (experimental) Taint value. Default: - None

        :stability: experimental
        :exampleMetadata: fixture=_generated

        Example::

            # The code below shows an example of how to instantiate this type.
            # The values are placeholders you should change.
            import aws_cdk.aws_eks_v2_alpha as eks_v2_alpha
            
            taint_spec = eks_v2_alpha.TaintSpec(
                effect=eks_v2_alpha.TaintEffect.NO_SCHEDULE,
                key="key",
                value="value"
            )
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9637a1b82876a86812c888482a6f065b486e8650308c6323b8b663373188e7d6)
            check_type(argname="argument effect", value=effect, expected_type=type_hints["effect"])
            check_type(argname="argument key", value=key, expected_type=type_hints["key"])
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if effect is not None:
            self._values["effect"] = effect
        if key is not None:
            self._values["key"] = key
        if value is not None:
            self._values["value"] = value

    @builtins.property
    def effect(self) -> typing.Optional[TaintEffect]:
        '''(experimental) Effect type.

        :default: - None

        :stability: experimental
        '''
        result = self._values.get("effect")
        return typing.cast(typing.Optional[TaintEffect], result)

    @builtins.property
    def key(self) -> typing.Optional[builtins.str]:
        '''(experimental) Taint key.

        :default: - None

        :stability: experimental
        '''
        result = self._values.get("key")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def value(self) -> typing.Optional[builtins.str]:
        '''(experimental) Taint value.

        :default: - None

        :stability: experimental
        '''
        result = self._values.get("value")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "TaintSpec(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.implements(IAccessEntry)
class AccessEntry(
    _aws_cdk_ceddda9d.Resource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@aws-cdk/aws-eks-v2-alpha.AccessEntry",
):
    '''(experimental) Represents an access entry in an Amazon EKS cluster.

    An access entry defines the permissions and scope for a user or role to access an Amazon EKS cluster.

    :stability: experimental
    :implements: IAccessEntry *
    :resource: AWS::EKS::AccessEntry
    :exampleMetadata: fixture=_generated

    Example::

        # The code below shows an example of how to instantiate this type.
        # The values are placeholders you should change.
        import aws_cdk.aws_eks_v2_alpha as eks_v2_alpha
        
        # access_policy: eks_v2_alpha.AccessPolicy
        # cluster: eks_v2_alpha.Cluster
        
        access_entry = eks_v2_alpha.AccessEntry(self, "MyAccessEntry",
            access_policies=[access_policy],
            cluster=cluster,
            principal="principal",
        
            # the properties below are optional
            access_entry_name="accessEntryName",
            access_entry_type=eks_v2_alpha.AccessEntryType.STANDARD
        )
    '''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        access_policies: typing.Sequence[IAccessPolicy],
        cluster: ICluster,
        principal: builtins.str,
        access_entry_name: typing.Optional[builtins.str] = None,
        access_entry_type: typing.Optional[AccessEntryType] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param access_policies: (experimental) The access policies that define the permissions and scope for the access entry.
        :param cluster: (experimental) The Amazon EKS cluster to which the access entry applies.
        :param principal: (experimental) The Amazon Resource Name (ARN) of the principal (user or role) to associate the access entry with.
        :param access_entry_name: (experimental) The name of the AccessEntry. Default: - No access entry name is provided
        :param access_entry_type: (experimental) The type of the AccessEntry. Default: STANDARD

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c50b24f7efb06e6404385f9fd709494fbb499d37a9547274f526781a807c0b75)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = AccessEntryProps(
            access_policies=access_policies,
            cluster=cluster,
            principal=principal,
            access_entry_name=access_entry_name,
            access_entry_type=access_entry_type,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @jsii.member(jsii_name="fromAccessEntryAttributes")
    @builtins.classmethod
    def from_access_entry_attributes(
        cls,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        access_entry_arn: builtins.str,
        access_entry_name: builtins.str,
    ) -> IAccessEntry:
        '''(experimental) Imports an ``AccessEntry`` from its attributes.

        :param scope: - The parent construct.
        :param id: - The ID of the imported construct.
        :param access_entry_arn: (experimental) The Amazon Resource Name (ARN) of the access entry.
        :param access_entry_name: (experimental) The name of the access entry.

        :return: The imported access entry.

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c2abef686b152cdabe07352f560805c65fcae0787d860d12d8ca21861a8e3488)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        attrs = AccessEntryAttributes(
            access_entry_arn=access_entry_arn, access_entry_name=access_entry_name
        )

        return typing.cast(IAccessEntry, jsii.sinvoke(cls, "fromAccessEntryAttributes", [scope, id, attrs]))

    @jsii.member(jsii_name="addAccessPolicies")
    def add_access_policies(
        self,
        new_access_policies: typing.Sequence[IAccessPolicy],
    ) -> None:
        '''(experimental) Add the access policies for this entry.

        :param new_access_policies: - The new access policies to add.

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__edc2c9e628394d869cfeb6eb8ca2671134840ebfe051a9c9166ea8f353aa81f8)
            check_type(argname="argument new_access_policies", value=new_access_policies, expected_type=type_hints["new_access_policies"])
        return typing.cast(None, jsii.invoke(self, "addAccessPolicies", [new_access_policies]))

    @jsii.python.classproperty
    @jsii.member(jsii_name="PROPERTY_INJECTION_ID")
    def PROPERTY_INJECTION_ID(cls) -> builtins.str:
        '''(experimental) Uniquely identifies this class.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "PROPERTY_INJECTION_ID"))

    @builtins.property
    @jsii.member(jsii_name="accessEntryArn")
    def access_entry_arn(self) -> builtins.str:
        '''(experimental) The Amazon Resource Name (ARN) of the access entry.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "accessEntryArn"))

    @builtins.property
    @jsii.member(jsii_name="accessEntryName")
    def access_entry_name(self) -> builtins.str:
        '''(experimental) The name of the access entry.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "accessEntryName"))


@jsii.implements(IAccessPolicy)
class AccessPolicy(
    metaclass=jsii.JSIIMeta,
    jsii_type="@aws-cdk/aws-eks-v2-alpha.AccessPolicy",
):
    '''(experimental) Represents an Amazon EKS Access Policy that implements the IAccessPolicy interface.

    :stability: experimental
    :implements: IAccessPolicy
    :exampleMetadata: infused

    Example::

        # AmazonEKSClusterAdminPolicy with `cluster` scope
        eks.AccessPolicy.from_access_policy_name("AmazonEKSClusterAdminPolicy",
            access_scope_type=eks.AccessScopeType.CLUSTER
        )
        # AmazonEKSAdminPolicy with `namespace` scope
        eks.AccessPolicy.from_access_policy_name("AmazonEKSAdminPolicy",
            access_scope_type=eks.AccessScopeType.NAMESPACE,
            namespaces=["foo", "bar"]
        )
    '''

    def __init__(
        self,
        *,
        access_scope: typing.Union[AccessScope, typing.Dict[builtins.str, typing.Any]],
        policy: AccessPolicyArn,
    ) -> None:
        '''(experimental) Constructs a new instance of the AccessPolicy class.

        :param access_scope: (experimental) The scope of the access policy, which determines the level of access granted.
        :param policy: (experimental) The access policy itself, which defines the specific permissions.

        :stability: experimental
        '''
        props = AccessPolicyProps(access_scope=access_scope, policy=policy)

        jsii.create(self.__class__, self, [props])

    @jsii.member(jsii_name="fromAccessPolicyName")
    @builtins.classmethod
    def from_access_policy_name(
        cls,
        policy_name: builtins.str,
        *,
        access_scope_type: AccessScopeType,
        namespaces: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> IAccessPolicy:
        '''(experimental) Import AccessPolicy by name.

        :param policy_name: -
        :param access_scope_type: (experimental) The scope of the access policy. This determines the level of access granted by the policy.
        :param namespaces: (experimental) An optional array of Kubernetes namespaces to which the access policy applies. Default: - no specific namespaces for this scope

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8cf50f783b482d05db39cc523377d9b9a874a916a6213b18b9a007c2f1c00b0e)
            check_type(argname="argument policy_name", value=policy_name, expected_type=type_hints["policy_name"])
        options = AccessPolicyNameOptions(
            access_scope_type=access_scope_type, namespaces=namespaces
        )

        return typing.cast(IAccessPolicy, jsii.sinvoke(cls, "fromAccessPolicyName", [policy_name, options]))

    @builtins.property
    @jsii.member(jsii_name="accessScope")
    def access_scope(self) -> AccessScope:
        '''(experimental) The scope of the access policy, which determines the level of access granted.

        :stability: experimental
        '''
        return typing.cast(AccessScope, jsii.get(self, "accessScope"))

    @builtins.property
    @jsii.member(jsii_name="policy")
    def policy(self) -> builtins.str:
        '''(experimental) The access policy itself, which defines the specific permissions.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "policy"))


@jsii.implements(IAddon)
class Addon(
    _aws_cdk_ceddda9d.Resource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@aws-cdk/aws-eks-v2-alpha.Addon",
):
    '''(experimental) Represents an Amazon EKS Add-On.

    :stability: experimental
    :resource: AWS::EKS::Addon
    :exampleMetadata: infused

    Example::

        # cluster: eks.Cluster
        
        
        eks.Addon(self, "Addon",
            cluster=cluster,
            addon_name="coredns",
            addon_version="v1.11.4-eksbuild.2",
            # whether to preserve the add-on software on your cluster but Amazon EKS stops managing any settings for the add-on.
            preserve_on_delete=False,
            configuration_values={
                "replica_count": 2
            }
        )
    '''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        addon_name: builtins.str,
        cluster: ICluster,
        addon_version: typing.Optional[builtins.str] = None,
        configuration_values: typing.Optional[typing.Mapping[builtins.str, typing.Any]] = None,
        preserve_on_delete: typing.Optional[builtins.bool] = None,
    ) -> None:
        '''(experimental) Creates a new Amazon EKS Add-On.

        :param scope: The parent construct.
        :param id: The construct ID.
        :param addon_name: (experimental) Name of the Add-On.
        :param cluster: (experimental) The EKS cluster the Add-On is associated with.
        :param addon_version: (experimental) Version of the Add-On. You can check all available versions with describe-addon-versions. For example, this lists all available versions for the ``eks-pod-identity-agent`` addon: $ aws eks describe-addon-versions --addon-name eks-pod-identity-agent --query 'addons[*].addonVersions[*].addonVersion' Default: the latest version.
        :param configuration_values: (experimental) The configuration values for the Add-on. Default: - Use default configuration.
        :param preserve_on_delete: (experimental) Specifying this option preserves the add-on software on your cluster but Amazon EKS stops managing any settings for the add-on. If an IAM account is associated with the add-on, it isn't removed. Default: true

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__49ab56d851f25a3b483cf3839b4b364bfa85f97144cd71c949220f7361a05c63)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = AddonProps(
            addon_name=addon_name,
            cluster=cluster,
            addon_version=addon_version,
            configuration_values=configuration_values,
            preserve_on_delete=preserve_on_delete,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @jsii.member(jsii_name="fromAddonArn")
    @builtins.classmethod
    def from_addon_arn(
        cls,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        addon_arn: builtins.str,
    ) -> IAddon:
        '''(experimental) Creates an ``IAddon`` from an existing addon ARN.

        :param scope: - The parent construct.
        :param id: - The ID of the construct.
        :param addon_arn: - The ARN of the addon.

        :return: An ``IAddon`` implementation.

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f8bf18bbe5d4f8271614a12a9fcab91c0eaff06abd225596e97aaff6845d2c23)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument addon_arn", value=addon_arn, expected_type=type_hints["addon_arn"])
        return typing.cast(IAddon, jsii.sinvoke(cls, "fromAddonArn", [scope, id, addon_arn]))

    @jsii.member(jsii_name="fromAddonAttributes")
    @builtins.classmethod
    def from_addon_attributes(
        cls,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        addon_name: builtins.str,
        cluster_name: builtins.str,
    ) -> IAddon:
        '''(experimental) Creates an ``IAddon`` instance from the given addon attributes.

        :param scope: - The parent construct.
        :param id: - The construct ID.
        :param addon_name: (experimental) The name of the addon.
        :param cluster_name: (experimental) The name of the Amazon EKS cluster the addon is associated with.

        :return: An ``IAddon`` instance.

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5aec0251268136a09ee648fead3099643ab09a7ead60028d0e0218a81d386aa0)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        attrs = AddonAttributes(addon_name=addon_name, cluster_name=cluster_name)

        return typing.cast(IAddon, jsii.sinvoke(cls, "fromAddonAttributes", [scope, id, attrs]))

    @jsii.python.classproperty
    @jsii.member(jsii_name="PROPERTY_INJECTION_ID")
    def PROPERTY_INJECTION_ID(cls) -> builtins.str:
        '''(experimental) Uniquely identifies this class.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "PROPERTY_INJECTION_ID"))

    @builtins.property
    @jsii.member(jsii_name="addonArn")
    def addon_arn(self) -> builtins.str:
        '''(experimental) Arn of the addon.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "addonArn"))

    @builtins.property
    @jsii.member(jsii_name="addonName")
    def addon_name(self) -> builtins.str:
        '''(experimental) Name of the addon.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "addonName"))


@jsii.implements(ICluster)
class Cluster(
    _aws_cdk_ceddda9d.Resource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@aws-cdk/aws-eks-v2-alpha.Cluster",
):
    '''(experimental) A Cluster represents a managed Kubernetes Service (EKS).

    This is a fully managed cluster of API Servers (control-plane)
    The user is still required to create the worker nodes.

    :stability: experimental
    :resource: AWS::EKS::Cluster
    :exampleMetadata: infused

    Example::

        cluster = eks.Cluster(self, "EksAutoCluster",
            version=eks.KubernetesVersion.V1_33,
            default_capacity_type=eks.DefaultCapacityType.AUTOMODE,
            compute=eks.ComputeConfig(
                node_pools=["system", "general-purpose"]
            )
        )
    '''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        bootstrap_cluster_creator_admin_permissions: typing.Optional[builtins.bool] = None,
        compute: typing.Optional[typing.Union[ComputeConfig, typing.Dict[builtins.str, typing.Any]]] = None,
        default_capacity: typing.Optional[jsii.Number] = None,
        default_capacity_instance: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.InstanceType] = None,
        default_capacity_type: typing.Optional[DefaultCapacityType] = None,
        output_config_command: typing.Optional[builtins.bool] = None,
        version: KubernetesVersion,
        alb_controller: typing.Optional[typing.Union[AlbControllerOptions, typing.Dict[builtins.str, typing.Any]]] = None,
        cluster_logging: typing.Optional[typing.Sequence[ClusterLoggingTypes]] = None,
        cluster_name: typing.Optional[builtins.str] = None,
        core_dns_compute_type: typing.Optional[CoreDnsComputeType] = None,
        endpoint_access: typing.Optional[EndpointAccess] = None,
        ip_family: typing.Optional[IpFamily] = None,
        kubectl_provider_options: typing.Optional[typing.Union[KubectlProviderOptions, typing.Dict[builtins.str, typing.Any]]] = None,
        masters_role: typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole] = None,
        prune: typing.Optional[builtins.bool] = None,
        role: typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole] = None,
        secrets_encryption_key: typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey] = None,
        security_group: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup] = None,
        service_ipv4_cidr: typing.Optional[builtins.str] = None,
        tags: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        vpc: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IVpc] = None,
        vpc_subnets: typing.Optional[typing.Sequence[typing.Union[_aws_cdk_aws_ec2_ceddda9d.SubnetSelection, typing.Dict[builtins.str, typing.Any]]]] = None,
    ) -> None:
        '''(experimental) Initiates an EKS Cluster with the supplied arguments.

        :param scope: a Construct, most likely a cdk.Stack created.
        :param id: the id of the Construct to create.
        :param bootstrap_cluster_creator_admin_permissions: (experimental) Whether or not IAM principal of the cluster creator was set as a cluster admin access entry during cluster creation time. Changing this value after the cluster has been created will result in the cluster being replaced. Default: true
        :param compute: (experimental) Configuration for compute settings in Auto Mode. When enabled, EKS will automatically manage compute resources. Default: - Auto Mode compute disabled
        :param default_capacity: (experimental) Number of instances to allocate as an initial capacity for this cluster. Instance type can be configured through ``defaultCapacityInstanceType``, which defaults to ``m5.large``. Use ``cluster.addAutoScalingGroupCapacity`` to add additional customized capacity. Set this to ``0`` is you wish to avoid the initial capacity allocation. Default: 2
        :param default_capacity_instance: (experimental) The instance type to use for the default capacity. This will only be taken into account if ``defaultCapacity`` is > 0. Default: m5.large
        :param default_capacity_type: (experimental) The default capacity type for the cluster. Default: AUTOMODE
        :param output_config_command: (experimental) Determines whether a CloudFormation output with the ``aws eks update-kubeconfig`` command will be synthesized. This command will include the cluster name and, if applicable, the ARN of the masters IAM role. Default: true
        :param version: (experimental) The Kubernetes version to run in the cluster.
        :param alb_controller: (experimental) Install the AWS Load Balancer Controller onto the cluster. Default: - The controller is not installed.
        :param cluster_logging: (experimental) The cluster log types which you want to enable. Default: - none
        :param cluster_name: (experimental) Name for the cluster. Default: - Automatically generated name
        :param core_dns_compute_type: (experimental) Controls the "eks.amazonaws.com/compute-type" annotation in the CoreDNS configuration on your cluster to determine which compute type to use for CoreDNS. Default: CoreDnsComputeType.EC2 (for ``FargateCluster`` the default is FARGATE)
        :param endpoint_access: (experimental) Configure access to the Kubernetes API server endpoint.. Default: EndpointAccess.PUBLIC_AND_PRIVATE
        :param ip_family: (experimental) Specify which IP family is used to assign Kubernetes pod and service IP addresses. Default: - IpFamily.IP_V4
        :param kubectl_provider_options: (experimental) Options for creating the kubectl provider - a lambda function that executes ``kubectl`` and ``helm`` against the cluster. If defined, ``kubectlLayer`` is a required property. If not defined, kubectl provider will not be created by default.
        :param masters_role: (experimental) An IAM role that will be added to the ``system:masters`` Kubernetes RBAC group. Default: - no masters role.
        :param prune: (experimental) Indicates whether Kubernetes resources added through ``addManifest()`` can be automatically pruned. When this is enabled (default), prune labels will be allocated and injected to each resource. These labels will then be used when issuing the ``kubectl apply`` operation with the ``--prune`` switch. Default: true
        :param role: (experimental) Role that provides permissions for the Kubernetes control plane to make calls to AWS API operations on your behalf. Default: - A role is automatically created for you
        :param secrets_encryption_key: (experimental) KMS secret for envelope encryption for Kubernetes secrets. Default: - By default, Kubernetes stores all secret object data within etcd and all etcd volumes used by Amazon EKS are encrypted at the disk-level using AWS-Managed encryption keys.
        :param security_group: (experimental) Security Group to use for Control Plane ENIs. Default: - A security group is automatically created
        :param service_ipv4_cidr: (experimental) The CIDR block to assign Kubernetes service IP addresses from. Default: - Kubernetes assigns addresses from either the 10.100.0.0/16 or 172.20.0.0/16 CIDR blocks
        :param tags: (experimental) The tags assigned to the EKS cluster. Default: - none
        :param vpc: (experimental) The VPC in which to create the Cluster. Default: - a VPC with default configuration will be created and can be accessed through ``cluster.vpc``.
        :param vpc_subnets: (experimental) Where to place EKS Control Plane ENIs. For example, to only select private subnets, supply the following: ``vpcSubnets: [{ subnetType: ec2.SubnetType.PRIVATE_WITH_EGRESS }]`` Default: - All public and private subnets

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f953a3ebdf317cd4c17c2caf66c079973022b58e6c5cf124f9d5f0089f9171fd)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = ClusterProps(
            bootstrap_cluster_creator_admin_permissions=bootstrap_cluster_creator_admin_permissions,
            compute=compute,
            default_capacity=default_capacity,
            default_capacity_instance=default_capacity_instance,
            default_capacity_type=default_capacity_type,
            output_config_command=output_config_command,
            version=version,
            alb_controller=alb_controller,
            cluster_logging=cluster_logging,
            cluster_name=cluster_name,
            core_dns_compute_type=core_dns_compute_type,
            endpoint_access=endpoint_access,
            ip_family=ip_family,
            kubectl_provider_options=kubectl_provider_options,
            masters_role=masters_role,
            prune=prune,
            role=role,
            secrets_encryption_key=secrets_encryption_key,
            security_group=security_group,
            service_ipv4_cidr=service_ipv4_cidr,
            tags=tags,
            vpc=vpc,
            vpc_subnets=vpc_subnets,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @jsii.member(jsii_name="fromClusterAttributes")
    @builtins.classmethod
    def from_cluster_attributes(
        cls,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        cluster_name: builtins.str,
        cluster_certificate_authority_data: typing.Optional[builtins.str] = None,
        cluster_encryption_config_key_arn: typing.Optional[builtins.str] = None,
        cluster_endpoint: typing.Optional[builtins.str] = None,
        cluster_security_group_id: typing.Optional[builtins.str] = None,
        ip_family: typing.Optional[IpFamily] = None,
        kubectl_provider: typing.Optional[IKubectlProvider] = None,
        kubectl_provider_options: typing.Optional[typing.Union[KubectlProviderOptions, typing.Dict[builtins.str, typing.Any]]] = None,
        open_id_connect_provider: typing.Optional[_aws_cdk_aws_iam_ceddda9d.IOpenIdConnectProvider] = None,
        prune: typing.Optional[builtins.bool] = None,
        security_group_ids: typing.Optional[typing.Sequence[builtins.str]] = None,
        vpc: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IVpc] = None,
    ) -> ICluster:
        '''(experimental) Import an existing cluster.

        :param scope: the construct scope, in most cases 'this'.
        :param id: the id or name to import as.
        :param cluster_name: (experimental) The physical name of the Cluster.
        :param cluster_certificate_authority_data: (experimental) The certificate-authority-data for your cluster. Default: - if not specified ``cluster.clusterCertificateAuthorityData`` will throw an error
        :param cluster_encryption_config_key_arn: (experimental) Amazon Resource Name (ARN) or alias of the customer master key (CMK). Default: - if not specified ``cluster.clusterEncryptionConfigKeyArn`` will throw an error
        :param cluster_endpoint: (experimental) The API Server endpoint URL. Default: - if not specified ``cluster.clusterEndpoint`` will throw an error.
        :param cluster_security_group_id: (experimental) The cluster security group that was created by Amazon EKS for the cluster. Default: - if not specified ``cluster.clusterSecurityGroupId`` will throw an error
        :param ip_family: (experimental) Specify which IP family is used to assign Kubernetes pod and service IP addresses. Default: - IpFamily.IP_V4
        :param kubectl_provider: (experimental) KubectlProvider for issuing kubectl commands. Default: - Default CDK provider
        :param kubectl_provider_options: (experimental) Options for creating the kubectl provider - a lambda function that executes ``kubectl`` and ``helm`` against the cluster. If defined, ``kubectlLayer`` is a required property. If not defined, kubectl provider will not be created by default.
        :param open_id_connect_provider: (experimental) An Open ID Connect provider for this cluster that can be used to configure service accounts. You can either import an existing provider using ``iam.OpenIdConnectProvider.fromProviderArn``, or create a new provider using ``new eks.OpenIdConnectProvider`` Default: - if not specified ``cluster.openIdConnectProvider`` and ``cluster.addServiceAccount`` will throw an error.
        :param prune: (experimental) Indicates whether Kubernetes resources added through ``addManifest()`` can be automatically pruned. When this is enabled (default), prune labels will be allocated and injected to each resource. These labels will then be used when issuing the ``kubectl apply`` operation with the ``--prune`` switch. Default: true
        :param security_group_ids: (experimental) Additional security groups associated with this cluster. Default: - if not specified, no additional security groups will be considered in ``cluster.connections``.
        :param vpc: (experimental) The VPC in which this Cluster was created. Default: - if not specified ``cluster.vpc`` will throw an error

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__92b8acf77f490c0c9dcfc8e22cfd896c75a58145ffa99499186d2e970f3b81ad)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        attrs = ClusterAttributes(
            cluster_name=cluster_name,
            cluster_certificate_authority_data=cluster_certificate_authority_data,
            cluster_encryption_config_key_arn=cluster_encryption_config_key_arn,
            cluster_endpoint=cluster_endpoint,
            cluster_security_group_id=cluster_security_group_id,
            ip_family=ip_family,
            kubectl_provider=kubectl_provider,
            kubectl_provider_options=kubectl_provider_options,
            open_id_connect_provider=open_id_connect_provider,
            prune=prune,
            security_group_ids=security_group_ids,
            vpc=vpc,
        )

        return typing.cast(ICluster, jsii.sinvoke(cls, "fromClusterAttributes", [scope, id, attrs]))

    @jsii.member(jsii_name="addAutoScalingGroupCapacity")
    def add_auto_scaling_group_capacity(
        self,
        id: builtins.str,
        *,
        instance_type: _aws_cdk_aws_ec2_ceddda9d.InstanceType,
        bootstrap_enabled: typing.Optional[builtins.bool] = None,
        bootstrap_options: typing.Optional[typing.Union[BootstrapOptions, typing.Dict[builtins.str, typing.Any]]] = None,
        machine_image_type: typing.Optional[MachineImageType] = None,
        allow_all_outbound: typing.Optional[builtins.bool] = None,
        associate_public_ip_address: typing.Optional[builtins.bool] = None,
        auto_scaling_group_name: typing.Optional[builtins.str] = None,
        az_capacity_distribution_strategy: typing.Optional[_aws_cdk_aws_autoscaling_ceddda9d.CapacityDistributionStrategy] = None,
        block_devices: typing.Optional[typing.Sequence[typing.Union[_aws_cdk_aws_autoscaling_ceddda9d.BlockDevice, typing.Dict[builtins.str, typing.Any]]]] = None,
        capacity_rebalance: typing.Optional[builtins.bool] = None,
        cooldown: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        default_instance_warmup: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        desired_capacity: typing.Optional[jsii.Number] = None,
        group_metrics: typing.Optional[typing.Sequence[_aws_cdk_aws_autoscaling_ceddda9d.GroupMetrics]] = None,
        health_check: typing.Optional[_aws_cdk_aws_autoscaling_ceddda9d.HealthCheck] = None,
        health_checks: typing.Optional[_aws_cdk_aws_autoscaling_ceddda9d.HealthChecks] = None,
        ignore_unmodified_size_properties: typing.Optional[builtins.bool] = None,
        instance_monitoring: typing.Optional[_aws_cdk_aws_autoscaling_ceddda9d.Monitoring] = None,
        key_name: typing.Optional[builtins.str] = None,
        key_pair: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IKeyPair] = None,
        max_capacity: typing.Optional[jsii.Number] = None,
        max_instance_lifetime: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        min_capacity: typing.Optional[jsii.Number] = None,
        new_instances_protected_from_scale_in: typing.Optional[builtins.bool] = None,
        notifications: typing.Optional[typing.Sequence[typing.Union[_aws_cdk_aws_autoscaling_ceddda9d.NotificationConfiguration, typing.Dict[builtins.str, typing.Any]]]] = None,
        signals: typing.Optional[_aws_cdk_aws_autoscaling_ceddda9d.Signals] = None,
        spot_price: typing.Optional[builtins.str] = None,
        ssm_session_permissions: typing.Optional[builtins.bool] = None,
        termination_policies: typing.Optional[typing.Sequence[_aws_cdk_aws_autoscaling_ceddda9d.TerminationPolicy]] = None,
        termination_policy_custom_lambda_function_arn: typing.Optional[builtins.str] = None,
        update_policy: typing.Optional[_aws_cdk_aws_autoscaling_ceddda9d.UpdatePolicy] = None,
        vpc_subnets: typing.Optional[typing.Union[_aws_cdk_aws_ec2_ceddda9d.SubnetSelection, typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> _aws_cdk_aws_autoscaling_ceddda9d.AutoScalingGroup:
        '''(experimental) Add nodes to this EKS cluster.

        The nodes will automatically be configured with the right VPC and AMI
        for the instance type and Kubernetes version.

        Note that if you specify ``updateType: RollingUpdate`` or ``updateType: ReplacingUpdate``, your nodes might be replaced at deploy
        time without notice in case the recommended AMI for your machine image type has been updated by AWS.
        The default behavior for ``updateType`` is ``None``, which means only new instances will be launched using the new AMI.

        :param id: -
        :param instance_type: (experimental) Instance type of the instances to start.
        :param bootstrap_enabled: (experimental) Configures the EC2 user-data script for instances in this autoscaling group to bootstrap the node (invoke ``/etc/eks/bootstrap.sh``) and associate it with the EKS cluster. If you wish to provide a custom user data script, set this to ``false`` and manually invoke ``autoscalingGroup.addUserData()``. Default: true
        :param bootstrap_options: (experimental) EKS node bootstrapping options. Default: - none
        :param machine_image_type: (experimental) Machine image type. Default: MachineImageType.AMAZON_LINUX_2
        :param allow_all_outbound: Whether the instances can initiate connections to anywhere by default. Default: true
        :param associate_public_ip_address: Whether instances in the Auto Scaling Group should have public IP addresses associated with them. ``launchTemplate`` and ``mixedInstancesPolicy`` must not be specified when this property is specified Default: - Use subnet setting.
        :param auto_scaling_group_name: The name of the Auto Scaling group. This name must be unique per Region per account. Default: - Auto generated by CloudFormation
        :param az_capacity_distribution_strategy: The strategy for distributing instances across Availability Zones. Default: None
        :param block_devices: Specifies how block devices are exposed to the instance. You can specify virtual devices and EBS volumes. Each instance that is launched has an associated root device volume, either an Amazon EBS volume or an instance store volume. You can use block device mappings to specify additional EBS volumes or instance store volumes to attach to an instance when it is launched. ``launchTemplate`` and ``mixedInstancesPolicy`` must not be specified when this property is specified Default: - Uses the block device mapping of the AMI
        :param capacity_rebalance: Indicates whether Capacity Rebalancing is enabled. When you turn on Capacity Rebalancing, Amazon EC2 Auto Scaling attempts to launch a Spot Instance whenever Amazon EC2 notifies that a Spot Instance is at an elevated risk of interruption. After launching a new instance, it then terminates an old instance. Default: false
        :param cooldown: Default scaling cooldown for this AutoScalingGroup. Default: Duration.minutes(5)
        :param default_instance_warmup: The amount of time, in seconds, until a newly launched instance can contribute to the Amazon CloudWatch metrics. This delay lets an instance finish initializing before Amazon EC2 Auto Scaling aggregates instance metrics, resulting in more reliable usage data. Set this value equal to the amount of time that it takes for resource consumption to become stable after an instance reaches the InService state. To optimize the performance of scaling policies that scale continuously, such as target tracking and step scaling policies, we strongly recommend that you enable the default instance warmup, even if its value is set to 0 seconds Default instance warmup will not be added if no value is specified Default: None
        :param desired_capacity: Initial amount of instances in the fleet. If this is set to a number, every deployment will reset the amount of instances to this number. It is recommended to leave this value blank. Default: minCapacity, and leave unchanged during deployment
        :param group_metrics: Enable monitoring for group metrics, these metrics describe the group rather than any of its instances. To report all group metrics use ``GroupMetrics.all()`` Group metrics are reported in a granularity of 1 minute at no additional charge. Default: - no group metrics will be reported
        :param health_check: (deprecated) Configuration for health checks. Default: - HealthCheck.ec2 with no grace period
        :param health_checks: Configuration for EC2 or additional health checks. Even when using ``HealthChecks.withAdditionalChecks()``, the EC2 type is implicitly included. Default: - EC2 type with no grace period
        :param ignore_unmodified_size_properties: If the ASG has scheduled actions, don't reset unchanged group sizes. Only used if the ASG has scheduled actions (which may scale your ASG up or down regardless of cdk deployments). If true, the size of the group will only be reset if it has been changed in the CDK app. If false, the sizes will always be changed back to what they were in the CDK app on deployment. Default: true
        :param instance_monitoring: Controls whether instances in this group are launched with detailed or basic monitoring. When detailed monitoring is enabled, Amazon CloudWatch generates metrics every minute and your account is charged a fee. When you disable detailed monitoring, CloudWatch generates metrics every 5 minutes. ``launchTemplate`` and ``mixedInstancesPolicy`` must not be specified when this property is specified Default: - Monitoring.DETAILED
        :param key_name: (deprecated) Name of SSH keypair to grant access to instances. ``launchTemplate`` and ``mixedInstancesPolicy`` must not be specified when this property is specified You can either specify ``keyPair`` or ``keyName``, not both. Default: - No SSH access will be possible.
        :param key_pair: The SSH keypair to grant access to the instance. Feature flag ``AUTOSCALING_GENERATE_LAUNCH_TEMPLATE`` must be enabled to use this property. ``launchTemplate`` and ``mixedInstancesPolicy`` must not be specified when this property is specified. You can either specify ``keyPair`` or ``keyName``, not both. Default: - No SSH access will be possible.
        :param max_capacity: Maximum number of instances in the fleet. Default: desiredCapacity
        :param max_instance_lifetime: The maximum amount of time that an instance can be in service. The maximum duration applies to all current and future instances in the group. As an instance approaches its maximum duration, it is terminated and replaced, and cannot be used again. You must specify a value of at least 86,400 seconds (one day). To clear a previously set value, leave this property undefined. Default: none
        :param min_capacity: Minimum number of instances in the fleet. Default: 1
        :param new_instances_protected_from_scale_in: Whether newly-launched instances are protected from termination by Amazon EC2 Auto Scaling when scaling in. By default, Auto Scaling can terminate an instance at any time after launch when scaling in an Auto Scaling Group, subject to the group's termination policy. However, you may wish to protect newly-launched instances from being scaled in if they are going to run critical applications that should not be prematurely terminated. This flag must be enabled if the Auto Scaling Group will be associated with an ECS Capacity Provider with managed termination protection. Default: false
        :param notifications: Configure autoscaling group to send notifications about fleet changes to an SNS topic(s). Default: - No fleet change notifications will be sent.
        :param signals: Configure waiting for signals during deployment. Use this to pause the CloudFormation deployment to wait for the instances in the AutoScalingGroup to report successful startup during creation and updates. The UserData script needs to invoke ``cfn-signal`` with a success or failure code after it is done setting up the instance. Without waiting for signals, the CloudFormation deployment will proceed as soon as the AutoScalingGroup has been created or updated but before the instances in the group have been started. For example, to have instances wait for an Elastic Load Balancing health check before they signal success, add a health-check verification by using the cfn-init helper script. For an example, see the verify_instance_health command in the Auto Scaling rolling updates sample template: https://github.com/awslabs/aws-cloudformation-templates/blob/master/aws/services/AutoScaling/AutoScalingRollingUpdates.yaml Default: - Do not wait for signals
        :param spot_price: The maximum hourly price (in USD) to be paid for any Spot Instance launched to fulfill the request. Spot Instances are launched when the price you specify exceeds the current Spot market price. ``launchTemplate`` and ``mixedInstancesPolicy`` must not be specified when this property is specified Default: none
        :param ssm_session_permissions: Add SSM session permissions to the instance role. Setting this to ``true`` adds the necessary permissions to connect to the instance using SSM Session Manager. You can do this from the AWS Console. NOTE: Setting this flag to ``true`` may not be enough by itself. You must also use an AMI that comes with the SSM Agent, or install the SSM Agent yourself. See `Working with SSM Agent <https://docs.aws.amazon.com/systems-manager/latest/userguide/ssm-agent.html>`_ in the SSM Developer Guide. Default: false
        :param termination_policies: A policy or a list of policies that are used to select the instances to terminate. The policies are executed in the order that you list them. Default: - ``TerminationPolicy.DEFAULT``
        :param termination_policy_custom_lambda_function_arn: A lambda function Arn that can be used as a custom termination policy to select the instances to terminate. This property must be specified if the TerminationPolicy.CUSTOM_LAMBDA_FUNCTION is used. Default: - No lambda function Arn will be supplied
        :param update_policy: What to do when an AutoScalingGroup's instance configuration is changed. This is applied when any of the settings on the ASG are changed that affect how the instances should be created (VPC, instance type, startup scripts, etc.). It indicates how the existing instances should be replaced with new instances matching the new config. By default, nothing is done and only new instances are launched with the new config. Default: - ``UpdatePolicy.rollingUpdate()`` if using ``init``, ``UpdatePolicy.none()`` otherwise
        :param vpc_subnets: Where to place instances within the VPC. Default: - All Private subnets.

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9693df090efed8f99d9380bbafdd596bd520fbaf6c8708b00b81560ee70628bb)
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        options = AutoScalingGroupCapacityOptions(
            instance_type=instance_type,
            bootstrap_enabled=bootstrap_enabled,
            bootstrap_options=bootstrap_options,
            machine_image_type=machine_image_type,
            allow_all_outbound=allow_all_outbound,
            associate_public_ip_address=associate_public_ip_address,
            auto_scaling_group_name=auto_scaling_group_name,
            az_capacity_distribution_strategy=az_capacity_distribution_strategy,
            block_devices=block_devices,
            capacity_rebalance=capacity_rebalance,
            cooldown=cooldown,
            default_instance_warmup=default_instance_warmup,
            desired_capacity=desired_capacity,
            group_metrics=group_metrics,
            health_check=health_check,
            health_checks=health_checks,
            ignore_unmodified_size_properties=ignore_unmodified_size_properties,
            instance_monitoring=instance_monitoring,
            key_name=key_name,
            key_pair=key_pair,
            max_capacity=max_capacity,
            max_instance_lifetime=max_instance_lifetime,
            min_capacity=min_capacity,
            new_instances_protected_from_scale_in=new_instances_protected_from_scale_in,
            notifications=notifications,
            signals=signals,
            spot_price=spot_price,
            ssm_session_permissions=ssm_session_permissions,
            termination_policies=termination_policies,
            termination_policy_custom_lambda_function_arn=termination_policy_custom_lambda_function_arn,
            update_policy=update_policy,
            vpc_subnets=vpc_subnets,
        )

        return typing.cast(_aws_cdk_aws_autoscaling_ceddda9d.AutoScalingGroup, jsii.invoke(self, "addAutoScalingGroupCapacity", [id, options]))

    @jsii.member(jsii_name="addCdk8sChart")
    def add_cdk8s_chart(
        self,
        id: builtins.str,
        chart: _constructs_77d1e7e8.Construct,
        *,
        ingress_alb: typing.Optional[builtins.bool] = None,
        ingress_alb_scheme: typing.Optional[AlbScheme] = None,
        prune: typing.Optional[builtins.bool] = None,
        skip_validation: typing.Optional[builtins.bool] = None,
    ) -> KubernetesManifest:
        '''(experimental) Defines a CDK8s chart in this cluster.

        :param id: logical id of this chart.
        :param chart: the cdk8s chart.
        :param ingress_alb: (experimental) Automatically detect ``Ingress`` resources in the manifest and annotate them so they are picked up by an ALB Ingress Controller. Default: false
        :param ingress_alb_scheme: (experimental) Specify the ALB scheme that should be applied to ``Ingress`` resources. Only applicable if ``ingressAlb`` is set to ``true``. Default: AlbScheme.INTERNAL
        :param prune: (experimental) When a resource is removed from a Kubernetes manifest, it no longer appears in the manifest, and there is no way to know that this resource needs to be deleted. To address this, ``kubectl apply`` has a ``--prune`` option which will query the cluster for all resources with a specific label and will remove all the labeld resources that are not part of the applied manifest. If this option is disabled and a resource is removed, it will become "orphaned" and will not be deleted from the cluster. When this option is enabled (default), the construct will inject a label to all Kubernetes resources included in this manifest which will be used to prune resources when the manifest changes via ``kubectl apply --prune``. The label name will be ``aws.cdk.eks/prune-<ADDR>`` where ``<ADDR>`` is the 42-char unique address of this construct in the construct tree. Value is empty. Default: - based on the prune option of the cluster, which is ``true`` unless otherwise specified.
        :param skip_validation: (experimental) A flag to signify if the manifest validation should be skipped. Default: false

        :return: a ``KubernetesManifest`` construct representing the chart.

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__fd88626e858659904edafa02fcbf622da5c2eba9e7e88a2512e50d8bf55d51eb)
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument chart", value=chart, expected_type=type_hints["chart"])
        options = KubernetesManifestOptions(
            ingress_alb=ingress_alb,
            ingress_alb_scheme=ingress_alb_scheme,
            prune=prune,
            skip_validation=skip_validation,
        )

        return typing.cast(KubernetesManifest, jsii.invoke(self, "addCdk8sChart", [id, chart, options]))

    @jsii.member(jsii_name="addFargateProfile")
    def add_fargate_profile(
        self,
        id: builtins.str,
        *,
        selectors: typing.Sequence[typing.Union[Selector, typing.Dict[builtins.str, typing.Any]]],
        fargate_profile_name: typing.Optional[builtins.str] = None,
        pod_execution_role: typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole] = None,
        subnet_selection: typing.Optional[typing.Union[_aws_cdk_aws_ec2_ceddda9d.SubnetSelection, typing.Dict[builtins.str, typing.Any]]] = None,
        vpc: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IVpc] = None,
    ) -> FargateProfile:
        '''(experimental) Adds a Fargate profile to this cluster.

        :param id: the id of this profile.
        :param selectors: (experimental) The selectors to match for pods to use this Fargate profile. Each selector must have an associated namespace. Optionally, you can also specify labels for a namespace. At least one selector is required and you may specify up to five selectors.
        :param fargate_profile_name: (experimental) The name of the Fargate profile. Default: - generated
        :param pod_execution_role: (experimental) The pod execution role to use for pods that match the selectors in the Fargate profile. The pod execution role allows Fargate infrastructure to register with your cluster as a node, and it provides read access to Amazon ECR image repositories. Default: - a role will be automatically created
        :param subnet_selection: (experimental) Select which subnets to launch your pods into. At this time, pods running on Fargate are not assigned public IP addresses, so only private subnets (with no direct route to an Internet Gateway) are allowed. You must specify the VPC to customize the subnet selection Default: - all private subnets of the VPC are selected.
        :param vpc: (experimental) The VPC from which to select subnets to launch your pods into. By default, all private subnets are selected. You can customize this using ``subnetSelection``. Default: - all private subnets used by the EKS cluster

        :see: https://docs.aws.amazon.com/eks/latest/userguide/fargate-profile.html
        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__270d94658e88e002a679c76d9279cdccae0092dfe69e76cb95c6369f63472767)
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        options = FargateProfileOptions(
            selectors=selectors,
            fargate_profile_name=fargate_profile_name,
            pod_execution_role=pod_execution_role,
            subnet_selection=subnet_selection,
            vpc=vpc,
        )

        return typing.cast(FargateProfile, jsii.invoke(self, "addFargateProfile", [id, options]))

    @jsii.member(jsii_name="addHelmChart")
    def add_helm_chart(
        self,
        id: builtins.str,
        *,
        atomic: typing.Optional[builtins.bool] = None,
        chart: typing.Optional[builtins.str] = None,
        chart_asset: typing.Optional[_aws_cdk_aws_s3_assets_ceddda9d.Asset] = None,
        create_namespace: typing.Optional[builtins.bool] = None,
        namespace: typing.Optional[builtins.str] = None,
        release: typing.Optional[builtins.str] = None,
        repository: typing.Optional[builtins.str] = None,
        skip_crds: typing.Optional[builtins.bool] = None,
        timeout: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        values: typing.Optional[typing.Mapping[builtins.str, typing.Any]] = None,
        version: typing.Optional[builtins.str] = None,
        wait: typing.Optional[builtins.bool] = None,
    ) -> HelmChart:
        '''(experimental) Defines a Helm chart in this cluster.

        :param id: logical id of this chart.
        :param atomic: (experimental) Whether or not Helm should treat this operation as atomic; if set, upgrade process rolls back changes made in case of failed upgrade. The --wait flag will be set automatically if --atomic is used. Default: false
        :param chart: (experimental) The name of the chart. Either this or ``chartAsset`` must be specified. Default: - No chart name. Implies ``chartAsset`` is used.
        :param chart_asset: (experimental) The chart in the form of an asset. Either this or ``chart`` must be specified. Default: - No chart asset. Implies ``chart`` is used.
        :param create_namespace: (experimental) create namespace if not exist. Default: true
        :param namespace: (experimental) The Kubernetes namespace scope of the requests. Default: default
        :param release: (experimental) The name of the release. Default: - If no release name is given, it will use the last 53 characters of the node's unique id.
        :param repository: (experimental) The repository which contains the chart. For example: https://charts.helm.sh/stable/ Default: - No repository will be used, which means that the chart needs to be an absolute URL.
        :param skip_crds: (experimental) if set, no CRDs will be installed. Default: - CRDs are installed if not already present
        :param timeout: (experimental) Amount of time to wait for any individual Kubernetes operation. Maximum 15 minutes. Default: Duration.minutes(5)
        :param values: (experimental) The values to be used by the chart. For nested values use a nested dictionary. For example: values: { installationCRDs: true, webhook: { port: 9443 } } Default: - No values are provided to the chart.
        :param version: (experimental) The chart version to install. Default: - If this is not specified, the latest version is installed
        :param wait: (experimental) Whether or not Helm should wait until all Pods, PVCs, Services, and minimum number of Pods of a Deployment, StatefulSet, or ReplicaSet are in a ready state before marking the release as successful. Default: - Helm will not wait before marking release as successful

        :return: a ``HelmChart`` construct

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__331a0171c170acae0c4098b1da2d9d25e1be7a7ab7af71e57bda308b57563a5e)
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        options = HelmChartOptions(
            atomic=atomic,
            chart=chart,
            chart_asset=chart_asset,
            create_namespace=create_namespace,
            namespace=namespace,
            release=release,
            repository=repository,
            skip_crds=skip_crds,
            timeout=timeout,
            values=values,
            version=version,
            wait=wait,
        )

        return typing.cast(HelmChart, jsii.invoke(self, "addHelmChart", [id, options]))

    @jsii.member(jsii_name="addManifest")
    def add_manifest(
        self,
        id: builtins.str,
        *manifest: typing.Mapping[builtins.str, typing.Any],
    ) -> KubernetesManifest:
        '''(experimental) Defines a Kubernetes resource in this cluster.

        The manifest will be applied/deleted using kubectl as needed.

        :param id: logical id of this manifest.
        :param manifest: a list of Kubernetes resource specifications.

        :return: a ``KubernetesResource`` object.

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__da5cdafdeba9df51e152027ddb1b45b77bb781a77f295eb73b5927f04d5e7b9d)
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument manifest", value=manifest, expected_type=typing.Tuple[type_hints["manifest"], ...]) # pyright: ignore [reportGeneralTypeIssues]
        return typing.cast(KubernetesManifest, jsii.invoke(self, "addManifest", [id, *manifest]))

    @jsii.member(jsii_name="addNodegroupCapacity")
    def add_nodegroup_capacity(
        self,
        id: builtins.str,
        *,
        ami_type: typing.Optional[NodegroupAmiType] = None,
        capacity_type: typing.Optional[CapacityType] = None,
        desired_size: typing.Optional[jsii.Number] = None,
        disk_size: typing.Optional[jsii.Number] = None,
        enable_node_auto_repair: typing.Optional[builtins.bool] = None,
        force_update: typing.Optional[builtins.bool] = None,
        instance_type: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.InstanceType] = None,
        instance_types: typing.Optional[typing.Sequence[_aws_cdk_aws_ec2_ceddda9d.InstanceType]] = None,
        labels: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        launch_template_spec: typing.Optional[typing.Union[LaunchTemplateSpec, typing.Dict[builtins.str, typing.Any]]] = None,
        max_size: typing.Optional[jsii.Number] = None,
        max_unavailable: typing.Optional[jsii.Number] = None,
        max_unavailable_percentage: typing.Optional[jsii.Number] = None,
        min_size: typing.Optional[jsii.Number] = None,
        nodegroup_name: typing.Optional[builtins.str] = None,
        node_role: typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole] = None,
        release_version: typing.Optional[builtins.str] = None,
        remote_access: typing.Optional[typing.Union[NodegroupRemoteAccess, typing.Dict[builtins.str, typing.Any]]] = None,
        subnets: typing.Optional[typing.Union[_aws_cdk_aws_ec2_ceddda9d.SubnetSelection, typing.Dict[builtins.str, typing.Any]]] = None,
        tags: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        taints: typing.Optional[typing.Sequence[typing.Union[TaintSpec, typing.Dict[builtins.str, typing.Any]]]] = None,
    ) -> Nodegroup:
        '''(experimental) Add managed nodegroup to this Amazon EKS cluster.

        This method will create a new managed nodegroup and add into the capacity.

        :param id: The ID of the nodegroup.
        :param ami_type: (experimental) The AMI type for your node group. If you explicitly specify the launchTemplate with custom AMI, do not specify this property, or the node group deployment will fail. In other cases, you will need to specify correct amiType for the nodegroup. Default: - auto-determined from the instanceTypes property when launchTemplateSpec property is not specified
        :param capacity_type: (experimental) The capacity type of the nodegroup. Default: - ON_DEMAND
        :param desired_size: (experimental) The current number of worker nodes that the managed node group should maintain. If not specified, the nodewgroup will initially create ``minSize`` instances. Default: 2
        :param disk_size: (experimental) The root device disk size (in GiB) for your node group instances. Default: 20
        :param enable_node_auto_repair: (experimental) Specifies whether to enable node auto repair for the node group. Node auto repair is disabled by default. Default: - disabled
        :param force_update: (experimental) Force the update if the existing node group's pods are unable to be drained due to a pod disruption budget issue. If an update fails because pods could not be drained, you can force the update after it fails to terminate the old node whether or not any pods are running on the node. Default: true
        :param instance_type: (deprecated) The instance type to use for your node group. Currently, you can specify a single instance type for a node group. The default value for this parameter is ``t3.medium``. If you choose a GPU instance type, be sure to specify the ``AL2_x86_64_GPU``, ``BOTTLEROCKET_ARM_64_NVIDIA``, or ``BOTTLEROCKET_x86_64_NVIDIA`` with the amiType parameter. Default: t3.medium
        :param instance_types: (experimental) The instance types to use for your node group. Default: t3.medium will be used according to the cloudformation document.
        :param labels: (experimental) The Kubernetes labels to be applied to the nodes in the node group when they are created. Default: - None
        :param launch_template_spec: (experimental) Launch template specification used for the nodegroup. Default: - no launch template
        :param max_size: (experimental) The maximum number of worker nodes that the managed node group can scale out to. Managed node groups can support up to 100 nodes by default. Default: - desiredSize
        :param max_unavailable: (experimental) The maximum number of nodes unavailable at once during a version update. Nodes will be updated in parallel. The maximum number is 100. This value or ``maxUnavailablePercentage`` is required to have a value for custom update configurations to be applied. Default: 1
        :param max_unavailable_percentage: (experimental) The maximum percentage of nodes unavailable during a version update. This percentage of nodes will be updated in parallel, up to 100 nodes at once. This value or ``maxUnavailable`` is required to have a value for custom update configurations to be applied. Default: undefined - node groups will update instances one at a time
        :param min_size: (experimental) The minimum number of worker nodes that the managed node group can scale in to. This number must be greater than or equal to zero. Default: 1
        :param nodegroup_name: (experimental) Name of the Nodegroup. Default: - resource ID
        :param node_role: (experimental) The IAM role to associate with your node group. The Amazon EKS worker node kubelet daemon makes calls to AWS APIs on your behalf. Worker nodes receive permissions for these API calls through an IAM instance profile and associated policies. Before you can launch worker nodes and register them into a cluster, you must create an IAM role for those worker nodes to use when they are launched. Default: - None. Auto-generated if not specified.
        :param release_version: (experimental) The AMI version of the Amazon EKS-optimized AMI to use with your node group (for example, ``1.14.7-YYYYMMDD``). Default: - The latest available AMI version for the node group's current Kubernetes version is used.
        :param remote_access: (experimental) The remote access (SSH) configuration to use with your node group. Disabled by default, however, if you specify an Amazon EC2 SSH key but do not specify a source security group when you create a managed node group, then port 22 on the worker nodes is opened to the internet (0.0.0.0/0) Default: - disabled
        :param subnets: (experimental) The subnets to use for the Auto Scaling group that is created for your node group. By specifying the SubnetSelection, the selected subnets will automatically apply required tags i.e. ``kubernetes.io/cluster/CLUSTER_NAME`` with a value of ``shared``, where ``CLUSTER_NAME`` is replaced with the name of your cluster. Default: - private subnets
        :param tags: (experimental) The metadata to apply to the node group to assist with categorization and organization. Each tag consists of a key and an optional value, both of which you define. Node group tags do not propagate to any other resources associated with the node group, such as the Amazon EC2 instances or subnets. Default: - None
        :param taints: (experimental) The Kubernetes taints to be applied to the nodes in the node group when they are created. Default: - None

        :see: https://docs.aws.amazon.com/eks/latest/userguide/managed-node-groups.html
        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__53ffb8b8a0e8d695d7a8d656e57c375a99ce7420e23269e0c1ffb12ebd16fcda)
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        options = NodegroupOptions(
            ami_type=ami_type,
            capacity_type=capacity_type,
            desired_size=desired_size,
            disk_size=disk_size,
            enable_node_auto_repair=enable_node_auto_repair,
            force_update=force_update,
            instance_type=instance_type,
            instance_types=instance_types,
            labels=labels,
            launch_template_spec=launch_template_spec,
            max_size=max_size,
            max_unavailable=max_unavailable,
            max_unavailable_percentage=max_unavailable_percentage,
            min_size=min_size,
            nodegroup_name=nodegroup_name,
            node_role=node_role,
            release_version=release_version,
            remote_access=remote_access,
            subnets=subnets,
            tags=tags,
            taints=taints,
        )

        return typing.cast(Nodegroup, jsii.invoke(self, "addNodegroupCapacity", [id, options]))

    @jsii.member(jsii_name="addServiceAccount")
    def add_service_account(
        self,
        id: builtins.str,
        *,
        annotations: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        identity_type: typing.Optional[IdentityType] = None,
        labels: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        name: typing.Optional[builtins.str] = None,
        namespace: typing.Optional[builtins.str] = None,
    ) -> ServiceAccount:
        '''(experimental) Creates a new service account with corresponding IAM Role (IRSA).

        :param id: -
        :param annotations: (experimental) Additional annotations of the service account. Default: - no additional annotations
        :param identity_type: (experimental) The identity type to use for the service account. Default: IdentityType.IRSA
        :param labels: (experimental) Additional labels of the service account. Default: - no additional labels
        :param name: (experimental) The name of the service account. The name of a ServiceAccount object must be a valid DNS subdomain name. https://kubernetes.io/docs/tasks/configure-pod-container/configure-service-account/ Default: - If no name is given, it will use the id of the resource.
        :param namespace: (experimental) The namespace of the service account. All namespace names must be valid RFC 1123 DNS labels. https://kubernetes.io/docs/concepts/overview/working-with-objects/namespaces/#namespaces-and-dns Default: "default"

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__36a54546780efd88d87f4fa87074bbbd7bbe7dae77512314baf0271c80334b19)
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        options = ServiceAccountOptions(
            annotations=annotations,
            identity_type=identity_type,
            labels=labels,
            name=name,
            namespace=namespace,
        )

        return typing.cast(ServiceAccount, jsii.invoke(self, "addServiceAccount", [id, options]))

    @jsii.member(jsii_name="connectAutoScalingGroupCapacity")
    def connect_auto_scaling_group_capacity(
        self,
        auto_scaling_group: _aws_cdk_aws_autoscaling_ceddda9d.AutoScalingGroup,
        *,
        bootstrap_enabled: typing.Optional[builtins.bool] = None,
        bootstrap_options: typing.Optional[typing.Union[BootstrapOptions, typing.Dict[builtins.str, typing.Any]]] = None,
        machine_image_type: typing.Optional[MachineImageType] = None,
    ) -> None:
        '''(experimental) Connect capacity in the form of an existing AutoScalingGroup to the EKS cluster.

        The AutoScalingGroup must be running an EKS-optimized AMI containing the
        /etc/eks/bootstrap.sh script. This method will configure Security Groups,
        add the right policies to the instance role, apply the right tags, and add
        the required user data to the instance's launch configuration.

        Prefer to use ``addAutoScalingGroupCapacity`` if possible.

        :param auto_scaling_group: [disable-awslint:ref-via-interface].
        :param bootstrap_enabled: (experimental) Configures the EC2 user-data script for instances in this autoscaling group to bootstrap the node (invoke ``/etc/eks/bootstrap.sh``) and associate it with the EKS cluster. If you wish to provide a custom user data script, set this to ``false`` and manually invoke ``autoscalingGroup.addUserData()``. Default: true
        :param bootstrap_options: (experimental) Allows options for node bootstrapping through EC2 user data. Default: - default options
        :param machine_image_type: (experimental) Allow options to specify different machine image type. Default: MachineImageType.AMAZON_LINUX_2

        :see: https://docs.aws.amazon.com/eks/latest/userguide/launch-workers.html
        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2c30a42f1e6c85140faa9a09d0e623dfa0cbf0f349bc35215f806313ad22faa4)
            check_type(argname="argument auto_scaling_group", value=auto_scaling_group, expected_type=type_hints["auto_scaling_group"])
        options = AutoScalingGroupOptions(
            bootstrap_enabled=bootstrap_enabled,
            bootstrap_options=bootstrap_options,
            machine_image_type=machine_image_type,
        )

        return typing.cast(None, jsii.invoke(self, "connectAutoScalingGroupCapacity", [auto_scaling_group, options]))

    @jsii.member(jsii_name="getIngressLoadBalancerAddress")
    def get_ingress_load_balancer_address(
        self,
        ingress_name: builtins.str,
        *,
        namespace: typing.Optional[builtins.str] = None,
        timeout: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
    ) -> builtins.str:
        '''(experimental) Fetch the load balancer address of an ingress backed by a load balancer.

        :param ingress_name: The name of the ingress.
        :param namespace: (experimental) The namespace the service belongs to. Default: 'default'
        :param timeout: (experimental) Timeout for waiting on the load balancer address. Default: Duration.minutes(5)

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4fb18943d5a03fdc5b5261720fbcac024d7eadc01b68d2188ca3863fb0079137)
            check_type(argname="argument ingress_name", value=ingress_name, expected_type=type_hints["ingress_name"])
        options = IngressLoadBalancerAddressOptions(
            namespace=namespace, timeout=timeout
        )

        return typing.cast(builtins.str, jsii.invoke(self, "getIngressLoadBalancerAddress", [ingress_name, options]))

    @jsii.member(jsii_name="getServiceLoadBalancerAddress")
    def get_service_load_balancer_address(
        self,
        service_name: builtins.str,
        *,
        namespace: typing.Optional[builtins.str] = None,
        timeout: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
    ) -> builtins.str:
        '''(experimental) Fetch the load balancer address of a service of type 'LoadBalancer'.

        :param service_name: The name of the service.
        :param namespace: (experimental) The namespace the service belongs to. Default: 'default'
        :param timeout: (experimental) Timeout for waiting on the load balancer address. Default: Duration.minutes(5)

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1af0e770bf9ab42af4d91256c3401240b72d64175dbc01d02cd356e1b0abe7c4)
            check_type(argname="argument service_name", value=service_name, expected_type=type_hints["service_name"])
        options = ServiceLoadBalancerAddressOptions(
            namespace=namespace, timeout=timeout
        )

        return typing.cast(builtins.str, jsii.invoke(self, "getServiceLoadBalancerAddress", [service_name, options]))

    @jsii.member(jsii_name="grantAccess")
    def grant_access(
        self,
        id: builtins.str,
        principal: builtins.str,
        access_policies: typing.Sequence[IAccessPolicy],
    ) -> None:
        '''(experimental) Grants the specified IAM principal access to the EKS cluster based on the provided access policies.

        This method creates an ``AccessEntry`` construct that grants the specified IAM principal the access permissions
        defined by the provided ``IAccessPolicy`` array. This allows the IAM principal to perform the actions permitted
        by the access policies within the EKS cluster.

        :param id: - The ID of the ``AccessEntry`` construct to be created.
        :param principal: - The IAM principal (role or user) to be granted access to the EKS cluster.
        :param access_policies: - An array of ``IAccessPolicy`` objects that define the access permissions to be granted to the IAM principal.

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__90b4483311d0a7d87252ed390a8138277fb3ae083bf9d3d36921f72d3de1fd5a)
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument principal", value=principal, expected_type=type_hints["principal"])
            check_type(argname="argument access_policies", value=access_policies, expected_type=type_hints["access_policies"])
        return typing.cast(None, jsii.invoke(self, "grantAccess", [id, principal, access_policies]))

    @jsii.member(jsii_name="grantClusterAdmin")
    def grant_cluster_admin(
        self,
        id: builtins.str,
        principal: builtins.str,
    ) -> AccessEntry:
        '''(experimental) Grants the specified IAM principal cluster admin access to the EKS cluster.

        This method creates an ``AccessEntry`` construct that grants the specified IAM principal the cluster admin
        access permissions. This allows the IAM principal to perform the actions permitted
        by the cluster admin acces.

        :param id: - The ID of the ``AccessEntry`` construct to be created.
        :param principal: - The IAM principal (role or user) to be granted access to the EKS cluster.

        :return: the access entry construct

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e1d4f786977ba522de732fe537d5732729fd14835a49d9c2277539b21b2eddc1)
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument principal", value=principal, expected_type=type_hints["principal"])
        return typing.cast(AccessEntry, jsii.invoke(self, "grantClusterAdmin", [id, principal]))

    @jsii.python.classproperty
    @jsii.member(jsii_name="PROPERTY_INJECTION_ID")
    def PROPERTY_INJECTION_ID(cls) -> builtins.str:
        '''(experimental) Uniquely identifies this class.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "PROPERTY_INJECTION_ID"))

    @builtins.property
    @jsii.member(jsii_name="clusterArn")
    def cluster_arn(self) -> builtins.str:
        '''(experimental) The AWS generated ARN for the Cluster resource.

        For example, ``arn:aws:eks:us-west-2:666666666666:cluster/prod``

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "clusterArn"))

    @builtins.property
    @jsii.member(jsii_name="clusterCertificateAuthorityData")
    def cluster_certificate_authority_data(self) -> builtins.str:
        '''(experimental) The certificate-authority-data for your cluster.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "clusterCertificateAuthorityData"))

    @builtins.property
    @jsii.member(jsii_name="clusterEncryptionConfigKeyArn")
    def cluster_encryption_config_key_arn(self) -> builtins.str:
        '''(experimental) Amazon Resource Name (ARN) or alias of the customer master key (CMK).

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "clusterEncryptionConfigKeyArn"))

    @builtins.property
    @jsii.member(jsii_name="clusterEndpoint")
    def cluster_endpoint(self) -> builtins.str:
        '''(experimental) The endpoint URL for the Cluster.

        This is the URL inside the kubeconfig file to use with kubectl

        For example, ``https://5E1D0CEXAMPLEA591B746AFC5AB30262.yl4.us-west-2.eks.amazonaws.com``

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "clusterEndpoint"))

    @builtins.property
    @jsii.member(jsii_name="clusterName")
    def cluster_name(self) -> builtins.str:
        '''(experimental) The Name of the created EKS Cluster.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "clusterName"))

    @builtins.property
    @jsii.member(jsii_name="clusterOpenIdConnectIssuerUrl")
    def cluster_open_id_connect_issuer_url(self) -> builtins.str:
        '''(experimental) If this cluster is kubectl-enabled, returns the OpenID Connect issuer url.

        If this cluster is not kubectl-enabled (i.e. uses the
        stock ``CfnCluster``), this is ``undefined``.

        :stability: experimental
        :attribute: true
        '''
        return typing.cast(builtins.str, jsii.get(self, "clusterOpenIdConnectIssuerUrl"))

    @builtins.property
    @jsii.member(jsii_name="clusterSecurityGroup")
    def cluster_security_group(self) -> _aws_cdk_aws_ec2_ceddda9d.ISecurityGroup:
        '''(experimental) The cluster security group that was created by Amazon EKS for the cluster.

        :stability: experimental
        '''
        return typing.cast(_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup, jsii.get(self, "clusterSecurityGroup"))

    @builtins.property
    @jsii.member(jsii_name="clusterSecurityGroupId")
    def cluster_security_group_id(self) -> builtins.str:
        '''(experimental) The id of the cluster security group that was created by Amazon EKS for the cluster.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "clusterSecurityGroupId"))

    @builtins.property
    @jsii.member(jsii_name="connections")
    def connections(self) -> _aws_cdk_aws_ec2_ceddda9d.Connections:
        '''(experimental) Manages connection rules (Security Group Rules) for the cluster.

        :stability: experimental
        :memberof: Cluster
        :type: {ec2.Connections}
        '''
        return typing.cast(_aws_cdk_aws_ec2_ceddda9d.Connections, jsii.get(self, "connections"))

    @builtins.property
    @jsii.member(jsii_name="openIdConnectProvider")
    def open_id_connect_provider(
        self,
    ) -> _aws_cdk_aws_iam_ceddda9d.IOpenIdConnectProvider:
        '''(experimental) An ``OpenIdConnectProvider`` resource associated with this cluster, and which can be used to link this cluster to AWS IAM.

        A provider will only be defined if this property is accessed (lazy initialization).

        :stability: experimental
        '''
        return typing.cast(_aws_cdk_aws_iam_ceddda9d.IOpenIdConnectProvider, jsii.get(self, "openIdConnectProvider"))

    @builtins.property
    @jsii.member(jsii_name="prune")
    def prune(self) -> builtins.bool:
        '''(experimental) Determines if Kubernetes resources can be pruned automatically.

        :stability: experimental
        '''
        return typing.cast(builtins.bool, jsii.get(self, "prune"))

    @builtins.property
    @jsii.member(jsii_name="role")
    def role(self) -> _aws_cdk_aws_iam_ceddda9d.IRole:
        '''(experimental) IAM role assumed by the EKS Control Plane.

        :stability: experimental
        '''
        return typing.cast(_aws_cdk_aws_iam_ceddda9d.IRole, jsii.get(self, "role"))

    @builtins.property
    @jsii.member(jsii_name="vpc")
    def vpc(self) -> _aws_cdk_aws_ec2_ceddda9d.IVpc:
        '''(experimental) The VPC in which this Cluster was created.

        :stability: experimental
        '''
        return typing.cast(_aws_cdk_aws_ec2_ceddda9d.IVpc, jsii.get(self, "vpc"))

    @builtins.property
    @jsii.member(jsii_name="albController")
    def alb_controller(self) -> typing.Optional[AlbController]:
        '''(experimental) The ALB Controller construct defined for this cluster.

        Will be undefined if ``albController`` wasn't configured.

        :stability: experimental
        '''
        return typing.cast(typing.Optional[AlbController], jsii.get(self, "albController"))

    @builtins.property
    @jsii.member(jsii_name="defaultCapacity")
    def default_capacity(
        self,
    ) -> typing.Optional[_aws_cdk_aws_autoscaling_ceddda9d.AutoScalingGroup]:
        '''(experimental) The auto scaling group that hosts the default capacity for this cluster.

        This will be ``undefined`` if the ``defaultCapacityType`` is not ``EC2`` or
        ``defaultCapacityType`` is ``EC2`` but default capacity is set to 0.

        :stability: experimental
        '''
        return typing.cast(typing.Optional[_aws_cdk_aws_autoscaling_ceddda9d.AutoScalingGroup], jsii.get(self, "defaultCapacity"))

    @builtins.property
    @jsii.member(jsii_name="defaultNodegroup")
    def default_nodegroup(self) -> typing.Optional[Nodegroup]:
        '''(experimental) The node group that hosts the default capacity for this cluster.

        This will be ``undefined`` if the ``defaultCapacityType`` is ``EC2`` or
        ``defaultCapacityType`` is ``NODEGROUP`` but default capacity is set to 0.

        :stability: experimental
        '''
        return typing.cast(typing.Optional[Nodegroup], jsii.get(self, "defaultNodegroup"))

    @builtins.property
    @jsii.member(jsii_name="eksPodIdentityAgent")
    def eks_pod_identity_agent(self) -> typing.Optional[IAddon]:
        '''(experimental) Retrieves the EKS Pod Identity Agent addon for the EKS cluster.

        The EKS Pod Identity Agent is responsible for managing the temporary credentials
        used by pods in the cluster to access AWS resources. It runs as a DaemonSet on
        each node and provides the necessary credentials to the pods based on their
        associated service account.

        :stability: experimental
        '''
        return typing.cast(typing.Optional[IAddon], jsii.get(self, "eksPodIdentityAgent"))

    @builtins.property
    @jsii.member(jsii_name="ipFamily")
    def ip_family(self) -> typing.Optional[IpFamily]:
        '''(experimental) Specify which IP family is used to assign Kubernetes pod and service IP addresses.

        :default: - IpFamily.IP_V4

        :see: https://docs.aws.amazon.com/eks/latest/APIReference/API_KubernetesNetworkConfigRequest.html#AmazonEKS-Type-KubernetesNetworkConfigRequest-ipFamily
        :stability: experimental
        '''
        return typing.cast(typing.Optional[IpFamily], jsii.get(self, "ipFamily"))

    @builtins.property
    @jsii.member(jsii_name="kubectlProvider")
    def kubectl_provider(self) -> typing.Optional[IKubectlProvider]:
        '''
        :stability: experimental
        '''
        return typing.cast(typing.Optional[IKubectlProvider], jsii.get(self, "kubectlProvider"))


class FargateCluster(
    Cluster,
    metaclass=jsii.JSIIMeta,
    jsii_type="@aws-cdk/aws-eks-v2-alpha.FargateCluster",
):
    '''(experimental) Defines an EKS cluster that runs entirely on AWS Fargate.

    The cluster is created with a default Fargate Profile that matches the
    "default" and "kube-system" namespaces. You can add additional profiles using
    ``addFargateProfile``.

    :stability: experimental
    :exampleMetadata: infused

    Example::

        cluster = eks.FargateCluster(self, "MyCluster",
            version=eks.KubernetesVersion.V1_33
        )
    '''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        default_profile: typing.Optional[typing.Union[FargateProfileOptions, typing.Dict[builtins.str, typing.Any]]] = None,
        version: KubernetesVersion,
        alb_controller: typing.Optional[typing.Union[AlbControllerOptions, typing.Dict[builtins.str, typing.Any]]] = None,
        cluster_logging: typing.Optional[typing.Sequence[ClusterLoggingTypes]] = None,
        cluster_name: typing.Optional[builtins.str] = None,
        core_dns_compute_type: typing.Optional[CoreDnsComputeType] = None,
        endpoint_access: typing.Optional[EndpointAccess] = None,
        ip_family: typing.Optional[IpFamily] = None,
        kubectl_provider_options: typing.Optional[typing.Union[KubectlProviderOptions, typing.Dict[builtins.str, typing.Any]]] = None,
        masters_role: typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole] = None,
        prune: typing.Optional[builtins.bool] = None,
        role: typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole] = None,
        secrets_encryption_key: typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey] = None,
        security_group: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup] = None,
        service_ipv4_cidr: typing.Optional[builtins.str] = None,
        tags: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        vpc: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IVpc] = None,
        vpc_subnets: typing.Optional[typing.Sequence[typing.Union[_aws_cdk_aws_ec2_ceddda9d.SubnetSelection, typing.Dict[builtins.str, typing.Any]]]] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param default_profile: (experimental) Fargate Profile to create along with the cluster. Default: - A profile called "default" with 'default' and 'kube-system' selectors will be created if this is left undefined.
        :param version: (experimental) The Kubernetes version to run in the cluster.
        :param alb_controller: (experimental) Install the AWS Load Balancer Controller onto the cluster. Default: - The controller is not installed.
        :param cluster_logging: (experimental) The cluster log types which you want to enable. Default: - none
        :param cluster_name: (experimental) Name for the cluster. Default: - Automatically generated name
        :param core_dns_compute_type: (experimental) Controls the "eks.amazonaws.com/compute-type" annotation in the CoreDNS configuration on your cluster to determine which compute type to use for CoreDNS. Default: CoreDnsComputeType.EC2 (for ``FargateCluster`` the default is FARGATE)
        :param endpoint_access: (experimental) Configure access to the Kubernetes API server endpoint.. Default: EndpointAccess.PUBLIC_AND_PRIVATE
        :param ip_family: (experimental) Specify which IP family is used to assign Kubernetes pod and service IP addresses. Default: - IpFamily.IP_V4
        :param kubectl_provider_options: (experimental) Options for creating the kubectl provider - a lambda function that executes ``kubectl`` and ``helm`` against the cluster. If defined, ``kubectlLayer`` is a required property. If not defined, kubectl provider will not be created by default.
        :param masters_role: (experimental) An IAM role that will be added to the ``system:masters`` Kubernetes RBAC group. Default: - no masters role.
        :param prune: (experimental) Indicates whether Kubernetes resources added through ``addManifest()`` can be automatically pruned. When this is enabled (default), prune labels will be allocated and injected to each resource. These labels will then be used when issuing the ``kubectl apply`` operation with the ``--prune`` switch. Default: true
        :param role: (experimental) Role that provides permissions for the Kubernetes control plane to make calls to AWS API operations on your behalf. Default: - A role is automatically created for you
        :param secrets_encryption_key: (experimental) KMS secret for envelope encryption for Kubernetes secrets. Default: - By default, Kubernetes stores all secret object data within etcd and all etcd volumes used by Amazon EKS are encrypted at the disk-level using AWS-Managed encryption keys.
        :param security_group: (experimental) Security Group to use for Control Plane ENIs. Default: - A security group is automatically created
        :param service_ipv4_cidr: (experimental) The CIDR block to assign Kubernetes service IP addresses from. Default: - Kubernetes assigns addresses from either the 10.100.0.0/16 or 172.20.0.0/16 CIDR blocks
        :param tags: (experimental) The tags assigned to the EKS cluster. Default: - none
        :param vpc: (experimental) The VPC in which to create the Cluster. Default: - a VPC with default configuration will be created and can be accessed through ``cluster.vpc``.
        :param vpc_subnets: (experimental) Where to place EKS Control Plane ENIs. For example, to only select private subnets, supply the following: ``vpcSubnets: [{ subnetType: ec2.SubnetType.PRIVATE_WITH_EGRESS }]`` Default: - All public and private subnets

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__673db9ae76799e064c85ea6382670fd3efa0ca3c8a72239cc0723fff0872a344)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = FargateClusterProps(
            default_profile=default_profile,
            version=version,
            alb_controller=alb_controller,
            cluster_logging=cluster_logging,
            cluster_name=cluster_name,
            core_dns_compute_type=core_dns_compute_type,
            endpoint_access=endpoint_access,
            ip_family=ip_family,
            kubectl_provider_options=kubectl_provider_options,
            masters_role=masters_role,
            prune=prune,
            role=role,
            secrets_encryption_key=secrets_encryption_key,
            security_group=security_group,
            service_ipv4_cidr=service_ipv4_cidr,
            tags=tags,
            vpc=vpc,
            vpc_subnets=vpc_subnets,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @jsii.python.classproperty
    @jsii.member(jsii_name="PROPERTY_INJECTION_ID")
    def PROPERTY_INJECTION_ID(cls) -> builtins.str:
        '''(experimental) Uniquely identifies this class.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "PROPERTY_INJECTION_ID"))

    @builtins.property
    @jsii.member(jsii_name="defaultProfile")
    def default_profile(self) -> FargateProfile:
        '''(experimental) Fargate Profile that was created with the cluster.

        :stability: experimental
        '''
        return typing.cast(FargateProfile, jsii.get(self, "defaultProfile"))


@jsii.data_type(
    jsii_type="@aws-cdk/aws-eks-v2-alpha.IngressLoadBalancerAddressOptions",
    jsii_struct_bases=[ServiceLoadBalancerAddressOptions],
    name_mapping={"namespace": "namespace", "timeout": "timeout"},
)
class IngressLoadBalancerAddressOptions(ServiceLoadBalancerAddressOptions):
    def __init__(
        self,
        *,
        namespace: typing.Optional[builtins.str] = None,
        timeout: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
    ) -> None:
        '''(experimental) Options for fetching an IngressLoadBalancerAddress.

        :param namespace: (experimental) The namespace the service belongs to. Default: 'default'
        :param timeout: (experimental) Timeout for waiting on the load balancer address. Default: Duration.minutes(5)

        :stability: experimental
        :exampleMetadata: fixture=_generated

        Example::

            # The code below shows an example of how to instantiate this type.
            # The values are placeholders you should change.
            import aws_cdk.aws_eks_v2_alpha as eks_v2_alpha
            import aws_cdk as cdk
            
            ingress_load_balancer_address_options = eks_v2_alpha.IngressLoadBalancerAddressOptions(
                namespace="namespace",
                timeout=cdk.Duration.minutes(30)
            )
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__867c24d91e82b6c927deaaa713ad154d44030f8a2d7da291636600790dfebd5e)
            check_type(argname="argument namespace", value=namespace, expected_type=type_hints["namespace"])
            check_type(argname="argument timeout", value=timeout, expected_type=type_hints["timeout"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if namespace is not None:
            self._values["namespace"] = namespace
        if timeout is not None:
            self._values["timeout"] = timeout

    @builtins.property
    def namespace(self) -> typing.Optional[builtins.str]:
        '''(experimental) The namespace the service belongs to.

        :default: 'default'

        :stability: experimental
        '''
        result = self._values.get("namespace")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def timeout(self) -> typing.Optional[_aws_cdk_ceddda9d.Duration]:
        '''(experimental) Timeout for waiting on the load balancer address.

        :default: Duration.minutes(5)

        :stability: experimental
        '''
        result = self._values.get("timeout")
        return typing.cast(typing.Optional[_aws_cdk_ceddda9d.Duration], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "IngressLoadBalancerAddressOptions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "AccessEntry",
    "AccessEntryAttributes",
    "AccessEntryProps",
    "AccessEntryType",
    "AccessPolicy",
    "AccessPolicyArn",
    "AccessPolicyNameOptions",
    "AccessPolicyProps",
    "AccessScope",
    "AccessScopeType",
    "Addon",
    "AddonAttributes",
    "AddonProps",
    "AlbController",
    "AlbControllerOptions",
    "AlbControllerProps",
    "AlbControllerVersion",
    "AlbScheme",
    "AutoScalingGroupCapacityOptions",
    "AutoScalingGroupOptions",
    "BootstrapOptions",
    "CapacityType",
    "Cluster",
    "ClusterAttributes",
    "ClusterCommonOptions",
    "ClusterLoggingTypes",
    "ClusterProps",
    "ComputeConfig",
    "CoreDnsComputeType",
    "CpuArch",
    "DefaultCapacityType",
    "EksOptimizedImage",
    "EksOptimizedImageProps",
    "EndpointAccess",
    "FargateCluster",
    "FargateClusterProps",
    "FargateProfile",
    "FargateProfileOptions",
    "FargateProfileProps",
    "HelmChart",
    "HelmChartOptions",
    "HelmChartProps",
    "IAccessEntry",
    "IAccessPolicy",
    "IAddon",
    "ICluster",
    "IKubectlProvider",
    "INodegroup",
    "IdentityType",
    "IngressLoadBalancerAddressOptions",
    "IpFamily",
    "KubectlProvider",
    "KubectlProviderAttributes",
    "KubectlProviderOptions",
    "KubectlProviderProps",
    "KubernetesManifest",
    "KubernetesManifestOptions",
    "KubernetesManifestProps",
    "KubernetesObjectValue",
    "KubernetesObjectValueProps",
    "KubernetesPatch",
    "KubernetesPatchProps",
    "KubernetesVersion",
    "LaunchTemplateSpec",
    "MachineImageType",
    "NodeType",
    "Nodegroup",
    "NodegroupAmiType",
    "NodegroupOptions",
    "NodegroupProps",
    "NodegroupRemoteAccess",
    "OpenIdConnectProvider",
    "OpenIdConnectProviderProps",
    "PatchType",
    "Selector",
    "ServiceAccount",
    "ServiceAccountOptions",
    "ServiceAccountProps",
    "ServiceLoadBalancerAddressOptions",
    "TaintEffect",
    "TaintSpec",
]

publication.publish()

def _typecheckingstub__a1c42761d8ad618e710840d7ce74bb7a2f8a514feedccc8036a6981b147024bc(
    *,
    access_entry_arn: builtins.str,
    access_entry_name: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__28312253bcbfe1c95acff9f4dd1b5759694a940428c1c62932fe961a5a9ba258(
    *,
    access_policies: typing.Sequence[IAccessPolicy],
    cluster: ICluster,
    principal: builtins.str,
    access_entry_name: typing.Optional[builtins.str] = None,
    access_entry_type: typing.Optional[AccessEntryType] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b6bcee6a7fdd4d7280e30d78ff502c787d282b5a96f4540c76eac9d188ec3da3(
    policy_name: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__155fac0a7fd65467d537ff4154d30c6ff4695350828b6ec7f85303a397092bd7(
    policy_name: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__18c9055694d7edcbddf83f561177ec54d0045caca2dff5354a29ccaf0421b493(
    *,
    access_scope_type: AccessScopeType,
    namespaces: typing.Optional[typing.Sequence[builtins.str]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__67dd0dd6c6160b9fa70474d028bdae828b4c8b27179b498fbd95c4ed4b19c3d8(
    *,
    access_scope: typing.Union[AccessScope, typing.Dict[builtins.str, typing.Any]],
    policy: AccessPolicyArn,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2b5165802a21d1fa47a765766414c1a219e1b28c0ea0666a761a47a6014d6d15(
    *,
    type: AccessScopeType,
    namespaces: typing.Optional[typing.Sequence[builtins.str]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c45f5324dae53f08d3805a9ed526230051bfa314a37fce62f6c6559495f0a9ef(
    *,
    addon_name: builtins.str,
    cluster_name: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ce116d5a90e7137ae9a49817a403d4e436125d6de14d8cc0d64941c9bbf10338(
    *,
    addon_name: builtins.str,
    cluster: ICluster,
    addon_version: typing.Optional[builtins.str] = None,
    configuration_values: typing.Optional[typing.Mapping[builtins.str, typing.Any]] = None,
    preserve_on_delete: typing.Optional[builtins.bool] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6c1fc18874adc65eddee4779680e882efdd136a784f11a6821fbb017354e4821(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    cluster: Cluster,
    version: AlbControllerVersion,
    policy: typing.Any = None,
    repository: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b7d42172ce30796b336d53a283aaf2d1861ef8f3513b5174f100f1d0ca21f07e(
    scope: _constructs_77d1e7e8.Construct,
    *,
    cluster: Cluster,
    version: AlbControllerVersion,
    policy: typing.Any = None,
    repository: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a1139b37be2b46399f7ef96eec4f70ca36576851005d609b6f8a06ff3509e8ad(
    *,
    version: AlbControllerVersion,
    policy: typing.Any = None,
    repository: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8534a14f2dfaef545def42149b259d669b343d67a1d2e725421704e573f3ee13(
    *,
    version: AlbControllerVersion,
    policy: typing.Any = None,
    repository: typing.Optional[builtins.str] = None,
    cluster: Cluster,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1167bdec41553341107a601373e40e2bbf5ffeb8e179efc1ad19421c7989edf6(
    version: builtins.str,
    helm_chart_version: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__eb99c268be8192566d7bfb495648a3dadbee5b1ea942e5f4d69e1a57935ac540(
    *,
    allow_all_outbound: typing.Optional[builtins.bool] = None,
    associate_public_ip_address: typing.Optional[builtins.bool] = None,
    auto_scaling_group_name: typing.Optional[builtins.str] = None,
    az_capacity_distribution_strategy: typing.Optional[_aws_cdk_aws_autoscaling_ceddda9d.CapacityDistributionStrategy] = None,
    block_devices: typing.Optional[typing.Sequence[typing.Union[_aws_cdk_aws_autoscaling_ceddda9d.BlockDevice, typing.Dict[builtins.str, typing.Any]]]] = None,
    capacity_rebalance: typing.Optional[builtins.bool] = None,
    cooldown: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
    default_instance_warmup: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
    desired_capacity: typing.Optional[jsii.Number] = None,
    group_metrics: typing.Optional[typing.Sequence[_aws_cdk_aws_autoscaling_ceddda9d.GroupMetrics]] = None,
    health_check: typing.Optional[_aws_cdk_aws_autoscaling_ceddda9d.HealthCheck] = None,
    health_checks: typing.Optional[_aws_cdk_aws_autoscaling_ceddda9d.HealthChecks] = None,
    ignore_unmodified_size_properties: typing.Optional[builtins.bool] = None,
    instance_monitoring: typing.Optional[_aws_cdk_aws_autoscaling_ceddda9d.Monitoring] = None,
    key_name: typing.Optional[builtins.str] = None,
    key_pair: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IKeyPair] = None,
    max_capacity: typing.Optional[jsii.Number] = None,
    max_instance_lifetime: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
    min_capacity: typing.Optional[jsii.Number] = None,
    new_instances_protected_from_scale_in: typing.Optional[builtins.bool] = None,
    notifications: typing.Optional[typing.Sequence[typing.Union[_aws_cdk_aws_autoscaling_ceddda9d.NotificationConfiguration, typing.Dict[builtins.str, typing.Any]]]] = None,
    signals: typing.Optional[_aws_cdk_aws_autoscaling_ceddda9d.Signals] = None,
    spot_price: typing.Optional[builtins.str] = None,
    ssm_session_permissions: typing.Optional[builtins.bool] = None,
    termination_policies: typing.Optional[typing.Sequence[_aws_cdk_aws_autoscaling_ceddda9d.TerminationPolicy]] = None,
    termination_policy_custom_lambda_function_arn: typing.Optional[builtins.str] = None,
    update_policy: typing.Optional[_aws_cdk_aws_autoscaling_ceddda9d.UpdatePolicy] = None,
    vpc_subnets: typing.Optional[typing.Union[_aws_cdk_aws_ec2_ceddda9d.SubnetSelection, typing.Dict[builtins.str, typing.Any]]] = None,
    instance_type: _aws_cdk_aws_ec2_ceddda9d.InstanceType,
    bootstrap_enabled: typing.Optional[builtins.bool] = None,
    bootstrap_options: typing.Optional[typing.Union[BootstrapOptions, typing.Dict[builtins.str, typing.Any]]] = None,
    machine_image_type: typing.Optional[MachineImageType] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__80c4d5f46701b7f97c3792dbf2230ae20b5bfabf12a3d73e5e01c6c755b4b3d9(
    *,
    bootstrap_enabled: typing.Optional[builtins.bool] = None,
    bootstrap_options: typing.Optional[typing.Union[BootstrapOptions, typing.Dict[builtins.str, typing.Any]]] = None,
    machine_image_type: typing.Optional[MachineImageType] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__93623b95a0480231b16717efee254b138fdefc282e67783dd4ac43cd0f30e33c(
    *,
    additional_args: typing.Optional[builtins.str] = None,
    aws_api_retry_attempts: typing.Optional[jsii.Number] = None,
    dns_cluster_ip: typing.Optional[builtins.str] = None,
    docker_config_json: typing.Optional[builtins.str] = None,
    enable_docker_bridge: typing.Optional[builtins.bool] = None,
    kubelet_extra_args: typing.Optional[builtins.str] = None,
    use_max_pods: typing.Optional[builtins.bool] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__000c78cc58b69c9c1f9d75052e6a7ba89be1dd825fcc3b2701bdc2609e77c79a(
    *,
    cluster_name: builtins.str,
    cluster_certificate_authority_data: typing.Optional[builtins.str] = None,
    cluster_encryption_config_key_arn: typing.Optional[builtins.str] = None,
    cluster_endpoint: typing.Optional[builtins.str] = None,
    cluster_security_group_id: typing.Optional[builtins.str] = None,
    ip_family: typing.Optional[IpFamily] = None,
    kubectl_provider: typing.Optional[IKubectlProvider] = None,
    kubectl_provider_options: typing.Optional[typing.Union[KubectlProviderOptions, typing.Dict[builtins.str, typing.Any]]] = None,
    open_id_connect_provider: typing.Optional[_aws_cdk_aws_iam_ceddda9d.IOpenIdConnectProvider] = None,
    prune: typing.Optional[builtins.bool] = None,
    security_group_ids: typing.Optional[typing.Sequence[builtins.str]] = None,
    vpc: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IVpc] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__522396bf3ea38086bd92ddd50181dc1757140cccc27f7d0415c200a262a260a5(
    *,
    version: KubernetesVersion,
    alb_controller: typing.Optional[typing.Union[AlbControllerOptions, typing.Dict[builtins.str, typing.Any]]] = None,
    cluster_logging: typing.Optional[typing.Sequence[ClusterLoggingTypes]] = None,
    cluster_name: typing.Optional[builtins.str] = None,
    core_dns_compute_type: typing.Optional[CoreDnsComputeType] = None,
    endpoint_access: typing.Optional[EndpointAccess] = None,
    ip_family: typing.Optional[IpFamily] = None,
    kubectl_provider_options: typing.Optional[typing.Union[KubectlProviderOptions, typing.Dict[builtins.str, typing.Any]]] = None,
    masters_role: typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole] = None,
    prune: typing.Optional[builtins.bool] = None,
    role: typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole] = None,
    secrets_encryption_key: typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey] = None,
    security_group: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup] = None,
    service_ipv4_cidr: typing.Optional[builtins.str] = None,
    tags: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    vpc: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IVpc] = None,
    vpc_subnets: typing.Optional[typing.Sequence[typing.Union[_aws_cdk_aws_ec2_ceddda9d.SubnetSelection, typing.Dict[builtins.str, typing.Any]]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__cdebba88d00ede95b7f48fc97c266609fdb0fc0ef3bb709493d319c84ab460db(
    *,
    version: KubernetesVersion,
    alb_controller: typing.Optional[typing.Union[AlbControllerOptions, typing.Dict[builtins.str, typing.Any]]] = None,
    cluster_logging: typing.Optional[typing.Sequence[ClusterLoggingTypes]] = None,
    cluster_name: typing.Optional[builtins.str] = None,
    core_dns_compute_type: typing.Optional[CoreDnsComputeType] = None,
    endpoint_access: typing.Optional[EndpointAccess] = None,
    ip_family: typing.Optional[IpFamily] = None,
    kubectl_provider_options: typing.Optional[typing.Union[KubectlProviderOptions, typing.Dict[builtins.str, typing.Any]]] = None,
    masters_role: typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole] = None,
    prune: typing.Optional[builtins.bool] = None,
    role: typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole] = None,
    secrets_encryption_key: typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey] = None,
    security_group: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup] = None,
    service_ipv4_cidr: typing.Optional[builtins.str] = None,
    tags: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    vpc: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IVpc] = None,
    vpc_subnets: typing.Optional[typing.Sequence[typing.Union[_aws_cdk_aws_ec2_ceddda9d.SubnetSelection, typing.Dict[builtins.str, typing.Any]]]] = None,
    bootstrap_cluster_creator_admin_permissions: typing.Optional[builtins.bool] = None,
    compute: typing.Optional[typing.Union[ComputeConfig, typing.Dict[builtins.str, typing.Any]]] = None,
    default_capacity: typing.Optional[jsii.Number] = None,
    default_capacity_instance: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.InstanceType] = None,
    default_capacity_type: typing.Optional[DefaultCapacityType] = None,
    output_config_command: typing.Optional[builtins.bool] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ecd4e0b2b1c23fafd1f01982b69fda08d5f3b0615f7bf8fe543ae2d8e6784f6e(
    *,
    node_pools: typing.Optional[typing.Sequence[builtins.str]] = None,
    node_role: typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5d60c600375f3cd4d2de211326df14f63e8e0248643232223ecaa3a7b785bd59(
    scope: _constructs_77d1e7e8.Construct,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__eb5af32c1a878ac8b2da202202fb401d5b46e60face624044d2514c385431f61(
    *,
    cpu_arch: typing.Optional[CpuArch] = None,
    kubernetes_version: typing.Optional[builtins.str] = None,
    node_type: typing.Optional[NodeType] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a2ac5f9f350e9a81225b8d655b582f3953844cf3cd196d2153d2ac97f3457e25(
    *cidr: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__89419afd037884b6a69d80af0bf5c1fe35164b8d31e7e5746501350e5dce60d0(
    *,
    version: KubernetesVersion,
    alb_controller: typing.Optional[typing.Union[AlbControllerOptions, typing.Dict[builtins.str, typing.Any]]] = None,
    cluster_logging: typing.Optional[typing.Sequence[ClusterLoggingTypes]] = None,
    cluster_name: typing.Optional[builtins.str] = None,
    core_dns_compute_type: typing.Optional[CoreDnsComputeType] = None,
    endpoint_access: typing.Optional[EndpointAccess] = None,
    ip_family: typing.Optional[IpFamily] = None,
    kubectl_provider_options: typing.Optional[typing.Union[KubectlProviderOptions, typing.Dict[builtins.str, typing.Any]]] = None,
    masters_role: typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole] = None,
    prune: typing.Optional[builtins.bool] = None,
    role: typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole] = None,
    secrets_encryption_key: typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey] = None,
    security_group: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup] = None,
    service_ipv4_cidr: typing.Optional[builtins.str] = None,
    tags: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    vpc: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IVpc] = None,
    vpc_subnets: typing.Optional[typing.Sequence[typing.Union[_aws_cdk_aws_ec2_ceddda9d.SubnetSelection, typing.Dict[builtins.str, typing.Any]]]] = None,
    default_profile: typing.Optional[typing.Union[FargateProfileOptions, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8fda2e7322d0839708496820fcb933c83a2eca4719746d8d6c30b513e2d6ae21(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    cluster: Cluster,
    selectors: typing.Sequence[typing.Union[Selector, typing.Dict[builtins.str, typing.Any]]],
    fargate_profile_name: typing.Optional[builtins.str] = None,
    pod_execution_role: typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole] = None,
    subnet_selection: typing.Optional[typing.Union[_aws_cdk_aws_ec2_ceddda9d.SubnetSelection, typing.Dict[builtins.str, typing.Any]]] = None,
    vpc: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IVpc] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__13ac7e4d5e707c67c365ab240566b231d61479b53823a8c1813c0ca790a3fa4b(
    *,
    selectors: typing.Sequence[typing.Union[Selector, typing.Dict[builtins.str, typing.Any]]],
    fargate_profile_name: typing.Optional[builtins.str] = None,
    pod_execution_role: typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole] = None,
    subnet_selection: typing.Optional[typing.Union[_aws_cdk_aws_ec2_ceddda9d.SubnetSelection, typing.Dict[builtins.str, typing.Any]]] = None,
    vpc: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IVpc] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fe54fadef84522ce1ddcbcb9cb688cea9c28ea444936beae0d6ab3cc18f646f5(
    *,
    selectors: typing.Sequence[typing.Union[Selector, typing.Dict[builtins.str, typing.Any]]],
    fargate_profile_name: typing.Optional[builtins.str] = None,
    pod_execution_role: typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole] = None,
    subnet_selection: typing.Optional[typing.Union[_aws_cdk_aws_ec2_ceddda9d.SubnetSelection, typing.Dict[builtins.str, typing.Any]]] = None,
    vpc: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IVpc] = None,
    cluster: Cluster,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e2ded6c2419a82e0debe530842e0b88f5af59ae5ecfe5fa58ccf3c9665442b61(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    cluster: ICluster,
    atomic: typing.Optional[builtins.bool] = None,
    chart: typing.Optional[builtins.str] = None,
    chart_asset: typing.Optional[_aws_cdk_aws_s3_assets_ceddda9d.Asset] = None,
    create_namespace: typing.Optional[builtins.bool] = None,
    namespace: typing.Optional[builtins.str] = None,
    release: typing.Optional[builtins.str] = None,
    repository: typing.Optional[builtins.str] = None,
    skip_crds: typing.Optional[builtins.bool] = None,
    timeout: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
    values: typing.Optional[typing.Mapping[builtins.str, typing.Any]] = None,
    version: typing.Optional[builtins.str] = None,
    wait: typing.Optional[builtins.bool] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__10ed29c454f002893e5586eb49b74f48903e50b690a353a03efcf7da45eb8f19(
    *,
    atomic: typing.Optional[builtins.bool] = None,
    chart: typing.Optional[builtins.str] = None,
    chart_asset: typing.Optional[_aws_cdk_aws_s3_assets_ceddda9d.Asset] = None,
    create_namespace: typing.Optional[builtins.bool] = None,
    namespace: typing.Optional[builtins.str] = None,
    release: typing.Optional[builtins.str] = None,
    repository: typing.Optional[builtins.str] = None,
    skip_crds: typing.Optional[builtins.bool] = None,
    timeout: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
    values: typing.Optional[typing.Mapping[builtins.str, typing.Any]] = None,
    version: typing.Optional[builtins.str] = None,
    wait: typing.Optional[builtins.bool] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b8d67c7be3f3c54dd9f759c893537dddbe6975848be6b4893d2c359372a076f9(
    *,
    atomic: typing.Optional[builtins.bool] = None,
    chart: typing.Optional[builtins.str] = None,
    chart_asset: typing.Optional[_aws_cdk_aws_s3_assets_ceddda9d.Asset] = None,
    create_namespace: typing.Optional[builtins.bool] = None,
    namespace: typing.Optional[builtins.str] = None,
    release: typing.Optional[builtins.str] = None,
    repository: typing.Optional[builtins.str] = None,
    skip_crds: typing.Optional[builtins.bool] = None,
    timeout: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
    values: typing.Optional[typing.Mapping[builtins.str, typing.Any]] = None,
    version: typing.Optional[builtins.str] = None,
    wait: typing.Optional[builtins.bool] = None,
    cluster: ICluster,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f459ac98d924ed6307c30338ff2aa989532034bca8648f0d213388ac6fa624ea(
    id: builtins.str,
    chart: _constructs_77d1e7e8.Construct,
    *,
    ingress_alb: typing.Optional[builtins.bool] = None,
    ingress_alb_scheme: typing.Optional[AlbScheme] = None,
    prune: typing.Optional[builtins.bool] = None,
    skip_validation: typing.Optional[builtins.bool] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__52256e6c30e726782e2fe2c664d6fe326d73b190eff84afda390022980e9565a(
    id: builtins.str,
    *,
    atomic: typing.Optional[builtins.bool] = None,
    chart: typing.Optional[builtins.str] = None,
    chart_asset: typing.Optional[_aws_cdk_aws_s3_assets_ceddda9d.Asset] = None,
    create_namespace: typing.Optional[builtins.bool] = None,
    namespace: typing.Optional[builtins.str] = None,
    release: typing.Optional[builtins.str] = None,
    repository: typing.Optional[builtins.str] = None,
    skip_crds: typing.Optional[builtins.bool] = None,
    timeout: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
    values: typing.Optional[typing.Mapping[builtins.str, typing.Any]] = None,
    version: typing.Optional[builtins.str] = None,
    wait: typing.Optional[builtins.bool] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__60918ce77747e9408d3a9d728c009990501845848cdfc39f8b7a0bcd4166d8f7(
    id: builtins.str,
    *manifest: typing.Mapping[builtins.str, typing.Any],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__54c7d27762cad0e201d56f32d63c9ea04e919c371197f80bb76628ae8827fca4(
    id: builtins.str,
    *,
    annotations: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    identity_type: typing.Optional[IdentityType] = None,
    labels: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    name: typing.Optional[builtins.str] = None,
    namespace: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ae7e85ee5fe1351899045b2f6a355bd8e6513d98bf420901c3f7e9e06d7b60ae(
    auto_scaling_group: _aws_cdk_aws_autoscaling_ceddda9d.AutoScalingGroup,
    *,
    bootstrap_enabled: typing.Optional[builtins.bool] = None,
    bootstrap_options: typing.Optional[typing.Union[BootstrapOptions, typing.Dict[builtins.str, typing.Any]]] = None,
    machine_image_type: typing.Optional[MachineImageType] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2727744972a89db9aea3f964a70a4c06bff58e13dbaf1fadf0d01bd8c4807569(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    cluster: ICluster,
    kubectl_layer: _aws_cdk_aws_lambda_ceddda9d.ILayerVersion,
    awscli_layer: typing.Optional[_aws_cdk_aws_lambda_ceddda9d.ILayerVersion] = None,
    environment: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    memory: typing.Optional[_aws_cdk_ceddda9d.Size] = None,
    private_subnets: typing.Optional[typing.Sequence[_aws_cdk_aws_ec2_ceddda9d.ISubnet]] = None,
    role: typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole] = None,
    security_group: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d01c897b7d6625a93468ddad4e123eb600739f04d7e53af0cccd0459dccff9ee(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    service_token: builtins.str,
    role: typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5f0476065e77a8fff5af95995870110c067c55720127c4719f2ef78397a74418(
    scope: _constructs_77d1e7e8.Construct,
    cluster: ICluster,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__43b2bf79b275491320586dc0b1c56ce24a179ad7f0a6e5dec512ed8b26df6e6f(
    *,
    service_token: builtins.str,
    role: typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9277e03d81f2504be1f4bfdbebaa07d5981427081ee7df98e56f401e95b72da2(
    *,
    kubectl_layer: _aws_cdk_aws_lambda_ceddda9d.ILayerVersion,
    awscli_layer: typing.Optional[_aws_cdk_aws_lambda_ceddda9d.ILayerVersion] = None,
    environment: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    memory: typing.Optional[_aws_cdk_ceddda9d.Size] = None,
    private_subnets: typing.Optional[typing.Sequence[_aws_cdk_aws_ec2_ceddda9d.ISubnet]] = None,
    role: typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole] = None,
    security_group: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5a43e0389ce84d427182514777711bd5e0d20341c50e14d2bba6a20b786e2989(
    *,
    kubectl_layer: _aws_cdk_aws_lambda_ceddda9d.ILayerVersion,
    awscli_layer: typing.Optional[_aws_cdk_aws_lambda_ceddda9d.ILayerVersion] = None,
    environment: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    memory: typing.Optional[_aws_cdk_ceddda9d.Size] = None,
    private_subnets: typing.Optional[typing.Sequence[_aws_cdk_aws_ec2_ceddda9d.ISubnet]] = None,
    role: typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole] = None,
    security_group: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup] = None,
    cluster: ICluster,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a98f85227580b8191bcd0e8f3f6195758157c48b7d98ccefd42d9d059b17ec94(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    cluster: ICluster,
    manifest: typing.Sequence[typing.Mapping[builtins.str, typing.Any]],
    overwrite: typing.Optional[builtins.bool] = None,
    ingress_alb: typing.Optional[builtins.bool] = None,
    ingress_alb_scheme: typing.Optional[AlbScheme] = None,
    prune: typing.Optional[builtins.bool] = None,
    skip_validation: typing.Optional[builtins.bool] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9213887feeb82fa12f23b39945263ce6d3b80422fa394db44cae4209a6d123b7(
    *,
    ingress_alb: typing.Optional[builtins.bool] = None,
    ingress_alb_scheme: typing.Optional[AlbScheme] = None,
    prune: typing.Optional[builtins.bool] = None,
    skip_validation: typing.Optional[builtins.bool] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1d422d0928845d93f04b27e21267a606598597ae4ac81109f31e2bdb34966aaa(
    *,
    ingress_alb: typing.Optional[builtins.bool] = None,
    ingress_alb_scheme: typing.Optional[AlbScheme] = None,
    prune: typing.Optional[builtins.bool] = None,
    skip_validation: typing.Optional[builtins.bool] = None,
    cluster: ICluster,
    manifest: typing.Sequence[typing.Mapping[builtins.str, typing.Any]],
    overwrite: typing.Optional[builtins.bool] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b33d1e78eda8d7f720836ea00e003335099872a491e2a4ff85cdef6f95c7cf05(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    cluster: ICluster,
    json_path: builtins.str,
    object_name: builtins.str,
    object_type: builtins.str,
    object_namespace: typing.Optional[builtins.str] = None,
    timeout: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3176fefda15b476ceac8b1c85f1ea17547b109979e2d9bc914fbddf92b82f9d1(
    *,
    cluster: ICluster,
    json_path: builtins.str,
    object_name: builtins.str,
    object_type: builtins.str,
    object_namespace: typing.Optional[builtins.str] = None,
    timeout: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b8e7dfe37990c2f03d7477c4bedbe6018b058a419a1ffc65a19a4914b9c0cd09(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    apply_patch: typing.Mapping[builtins.str, typing.Any],
    cluster: ICluster,
    resource_name: builtins.str,
    restore_patch: typing.Mapping[builtins.str, typing.Any],
    patch_type: typing.Optional[PatchType] = None,
    resource_namespace: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6a2a8250f9a8e2560086c3b4a14c105177bdade8b60ad3fff1746c21a40baf74(
    *,
    apply_patch: typing.Mapping[builtins.str, typing.Any],
    cluster: ICluster,
    resource_name: builtins.str,
    restore_patch: typing.Mapping[builtins.str, typing.Any],
    patch_type: typing.Optional[PatchType] = None,
    resource_namespace: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d63266ad2e560fe6dfe332fdec56b7db18121e33667f27bf25a1a952eae8a7fa(
    version: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fa14fa5ca62ae0433f472a1652360ff8e5957789e80aa8f86fdaa0feef3f8416(
    *,
    id: builtins.str,
    version: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fc8b0755389df345d97a19957b1626674e36777445f00245597a6b40ca83a096(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    cluster: ICluster,
    ami_type: typing.Optional[NodegroupAmiType] = None,
    capacity_type: typing.Optional[CapacityType] = None,
    desired_size: typing.Optional[jsii.Number] = None,
    disk_size: typing.Optional[jsii.Number] = None,
    enable_node_auto_repair: typing.Optional[builtins.bool] = None,
    force_update: typing.Optional[builtins.bool] = None,
    instance_type: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.InstanceType] = None,
    instance_types: typing.Optional[typing.Sequence[_aws_cdk_aws_ec2_ceddda9d.InstanceType]] = None,
    labels: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    launch_template_spec: typing.Optional[typing.Union[LaunchTemplateSpec, typing.Dict[builtins.str, typing.Any]]] = None,
    max_size: typing.Optional[jsii.Number] = None,
    max_unavailable: typing.Optional[jsii.Number] = None,
    max_unavailable_percentage: typing.Optional[jsii.Number] = None,
    min_size: typing.Optional[jsii.Number] = None,
    nodegroup_name: typing.Optional[builtins.str] = None,
    node_role: typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole] = None,
    release_version: typing.Optional[builtins.str] = None,
    remote_access: typing.Optional[typing.Union[NodegroupRemoteAccess, typing.Dict[builtins.str, typing.Any]]] = None,
    subnets: typing.Optional[typing.Union[_aws_cdk_aws_ec2_ceddda9d.SubnetSelection, typing.Dict[builtins.str, typing.Any]]] = None,
    tags: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    taints: typing.Optional[typing.Sequence[typing.Union[TaintSpec, typing.Dict[builtins.str, typing.Any]]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ba37b072ec60d2b3168ea14dba461b6b0b311846e547be16bde6effd1a73a6d5(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    nodegroup_name: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9f3bb52aa005520d24284a00deee84fca7e8c4afe54a8bdd40771517f0d53904(
    *,
    ami_type: typing.Optional[NodegroupAmiType] = None,
    capacity_type: typing.Optional[CapacityType] = None,
    desired_size: typing.Optional[jsii.Number] = None,
    disk_size: typing.Optional[jsii.Number] = None,
    enable_node_auto_repair: typing.Optional[builtins.bool] = None,
    force_update: typing.Optional[builtins.bool] = None,
    instance_type: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.InstanceType] = None,
    instance_types: typing.Optional[typing.Sequence[_aws_cdk_aws_ec2_ceddda9d.InstanceType]] = None,
    labels: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    launch_template_spec: typing.Optional[typing.Union[LaunchTemplateSpec, typing.Dict[builtins.str, typing.Any]]] = None,
    max_size: typing.Optional[jsii.Number] = None,
    max_unavailable: typing.Optional[jsii.Number] = None,
    max_unavailable_percentage: typing.Optional[jsii.Number] = None,
    min_size: typing.Optional[jsii.Number] = None,
    nodegroup_name: typing.Optional[builtins.str] = None,
    node_role: typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole] = None,
    release_version: typing.Optional[builtins.str] = None,
    remote_access: typing.Optional[typing.Union[NodegroupRemoteAccess, typing.Dict[builtins.str, typing.Any]]] = None,
    subnets: typing.Optional[typing.Union[_aws_cdk_aws_ec2_ceddda9d.SubnetSelection, typing.Dict[builtins.str, typing.Any]]] = None,
    tags: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    taints: typing.Optional[typing.Sequence[typing.Union[TaintSpec, typing.Dict[builtins.str, typing.Any]]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1eebacdf94f3e813ed7347b7e8a9a3d1a5527b9a5a2d8f9ef83d77bc6fd8b442(
    *,
    ami_type: typing.Optional[NodegroupAmiType] = None,
    capacity_type: typing.Optional[CapacityType] = None,
    desired_size: typing.Optional[jsii.Number] = None,
    disk_size: typing.Optional[jsii.Number] = None,
    enable_node_auto_repair: typing.Optional[builtins.bool] = None,
    force_update: typing.Optional[builtins.bool] = None,
    instance_type: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.InstanceType] = None,
    instance_types: typing.Optional[typing.Sequence[_aws_cdk_aws_ec2_ceddda9d.InstanceType]] = None,
    labels: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    launch_template_spec: typing.Optional[typing.Union[LaunchTemplateSpec, typing.Dict[builtins.str, typing.Any]]] = None,
    max_size: typing.Optional[jsii.Number] = None,
    max_unavailable: typing.Optional[jsii.Number] = None,
    max_unavailable_percentage: typing.Optional[jsii.Number] = None,
    min_size: typing.Optional[jsii.Number] = None,
    nodegroup_name: typing.Optional[builtins.str] = None,
    node_role: typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole] = None,
    release_version: typing.Optional[builtins.str] = None,
    remote_access: typing.Optional[typing.Union[NodegroupRemoteAccess, typing.Dict[builtins.str, typing.Any]]] = None,
    subnets: typing.Optional[typing.Union[_aws_cdk_aws_ec2_ceddda9d.SubnetSelection, typing.Dict[builtins.str, typing.Any]]] = None,
    tags: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    taints: typing.Optional[typing.Sequence[typing.Union[TaintSpec, typing.Dict[builtins.str, typing.Any]]]] = None,
    cluster: ICluster,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7e2d48859c362dd7583430ca612f6286dff54e738afd7db71bb5614a75b195c8(
    *,
    ssh_key_name: builtins.str,
    source_security_groups: typing.Optional[typing.Sequence[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ff947c100a9f93eae1804845d85376aa51e32fdc8dfbb887925e502cb46615fa(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    url: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e51c0e0b152fc05e514c652e218aa91a83ae3d3ffd37ce3c81cc7ef7aa158ea6(
    *,
    url: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9911766762b7aab73e519cbbd248d7c596d3fc57d9bb6c5111982ceac3893b38(
    *,
    namespace: builtins.str,
    labels: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__59d2cd5450f84e9b32d879613fee8749090a043d987b87cb3f41235259318083(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    cluster: ICluster,
    annotations: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    identity_type: typing.Optional[IdentityType] = None,
    labels: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    name: typing.Optional[builtins.str] = None,
    namespace: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9354abb1e4d2f8a5301e08be5aee342f6dba512efb916f84bf95a8ac5bc0edd9(
    statement: _aws_cdk_aws_iam_ceddda9d.PolicyStatement,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__100d788900bbaab34be52e0189b4ff18d53d1a8f3f871d71d199b39f885f7053(
    statement: _aws_cdk_aws_iam_ceddda9d.PolicyStatement,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b8aeba614d1b7fb1055e46177bab0671bb8b977ba1fb52885245e6ee59b7d8af(
    *,
    annotations: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    identity_type: typing.Optional[IdentityType] = None,
    labels: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    name: typing.Optional[builtins.str] = None,
    namespace: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__072f92804a73eaaceb4eaa101eddd03353373a90b6e44c6b0370811577a1994b(
    *,
    annotations: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    identity_type: typing.Optional[IdentityType] = None,
    labels: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    name: typing.Optional[builtins.str] = None,
    namespace: typing.Optional[builtins.str] = None,
    cluster: ICluster,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__375437ae14574762dafcddb85a25a9451aa14c4728ce35f797cdeb227139785a(
    *,
    namespace: typing.Optional[builtins.str] = None,
    timeout: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9637a1b82876a86812c888482a6f065b486e8650308c6323b8b663373188e7d6(
    *,
    effect: typing.Optional[TaintEffect] = None,
    key: typing.Optional[builtins.str] = None,
    value: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c50b24f7efb06e6404385f9fd709494fbb499d37a9547274f526781a807c0b75(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    access_policies: typing.Sequence[IAccessPolicy],
    cluster: ICluster,
    principal: builtins.str,
    access_entry_name: typing.Optional[builtins.str] = None,
    access_entry_type: typing.Optional[AccessEntryType] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c2abef686b152cdabe07352f560805c65fcae0787d860d12d8ca21861a8e3488(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    access_entry_arn: builtins.str,
    access_entry_name: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__edc2c9e628394d869cfeb6eb8ca2671134840ebfe051a9c9166ea8f353aa81f8(
    new_access_policies: typing.Sequence[IAccessPolicy],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8cf50f783b482d05db39cc523377d9b9a874a916a6213b18b9a007c2f1c00b0e(
    policy_name: builtins.str,
    *,
    access_scope_type: AccessScopeType,
    namespaces: typing.Optional[typing.Sequence[builtins.str]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__49ab56d851f25a3b483cf3839b4b364bfa85f97144cd71c949220f7361a05c63(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    addon_name: builtins.str,
    cluster: ICluster,
    addon_version: typing.Optional[builtins.str] = None,
    configuration_values: typing.Optional[typing.Mapping[builtins.str, typing.Any]] = None,
    preserve_on_delete: typing.Optional[builtins.bool] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f8bf18bbe5d4f8271614a12a9fcab91c0eaff06abd225596e97aaff6845d2c23(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    addon_arn: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5aec0251268136a09ee648fead3099643ab09a7ead60028d0e0218a81d386aa0(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    addon_name: builtins.str,
    cluster_name: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f953a3ebdf317cd4c17c2caf66c079973022b58e6c5cf124f9d5f0089f9171fd(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    bootstrap_cluster_creator_admin_permissions: typing.Optional[builtins.bool] = None,
    compute: typing.Optional[typing.Union[ComputeConfig, typing.Dict[builtins.str, typing.Any]]] = None,
    default_capacity: typing.Optional[jsii.Number] = None,
    default_capacity_instance: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.InstanceType] = None,
    default_capacity_type: typing.Optional[DefaultCapacityType] = None,
    output_config_command: typing.Optional[builtins.bool] = None,
    version: KubernetesVersion,
    alb_controller: typing.Optional[typing.Union[AlbControllerOptions, typing.Dict[builtins.str, typing.Any]]] = None,
    cluster_logging: typing.Optional[typing.Sequence[ClusterLoggingTypes]] = None,
    cluster_name: typing.Optional[builtins.str] = None,
    core_dns_compute_type: typing.Optional[CoreDnsComputeType] = None,
    endpoint_access: typing.Optional[EndpointAccess] = None,
    ip_family: typing.Optional[IpFamily] = None,
    kubectl_provider_options: typing.Optional[typing.Union[KubectlProviderOptions, typing.Dict[builtins.str, typing.Any]]] = None,
    masters_role: typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole] = None,
    prune: typing.Optional[builtins.bool] = None,
    role: typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole] = None,
    secrets_encryption_key: typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey] = None,
    security_group: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup] = None,
    service_ipv4_cidr: typing.Optional[builtins.str] = None,
    tags: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    vpc: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IVpc] = None,
    vpc_subnets: typing.Optional[typing.Sequence[typing.Union[_aws_cdk_aws_ec2_ceddda9d.SubnetSelection, typing.Dict[builtins.str, typing.Any]]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__92b8acf77f490c0c9dcfc8e22cfd896c75a58145ffa99499186d2e970f3b81ad(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    cluster_name: builtins.str,
    cluster_certificate_authority_data: typing.Optional[builtins.str] = None,
    cluster_encryption_config_key_arn: typing.Optional[builtins.str] = None,
    cluster_endpoint: typing.Optional[builtins.str] = None,
    cluster_security_group_id: typing.Optional[builtins.str] = None,
    ip_family: typing.Optional[IpFamily] = None,
    kubectl_provider: typing.Optional[IKubectlProvider] = None,
    kubectl_provider_options: typing.Optional[typing.Union[KubectlProviderOptions, typing.Dict[builtins.str, typing.Any]]] = None,
    open_id_connect_provider: typing.Optional[_aws_cdk_aws_iam_ceddda9d.IOpenIdConnectProvider] = None,
    prune: typing.Optional[builtins.bool] = None,
    security_group_ids: typing.Optional[typing.Sequence[builtins.str]] = None,
    vpc: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IVpc] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9693df090efed8f99d9380bbafdd596bd520fbaf6c8708b00b81560ee70628bb(
    id: builtins.str,
    *,
    instance_type: _aws_cdk_aws_ec2_ceddda9d.InstanceType,
    bootstrap_enabled: typing.Optional[builtins.bool] = None,
    bootstrap_options: typing.Optional[typing.Union[BootstrapOptions, typing.Dict[builtins.str, typing.Any]]] = None,
    machine_image_type: typing.Optional[MachineImageType] = None,
    allow_all_outbound: typing.Optional[builtins.bool] = None,
    associate_public_ip_address: typing.Optional[builtins.bool] = None,
    auto_scaling_group_name: typing.Optional[builtins.str] = None,
    az_capacity_distribution_strategy: typing.Optional[_aws_cdk_aws_autoscaling_ceddda9d.CapacityDistributionStrategy] = None,
    block_devices: typing.Optional[typing.Sequence[typing.Union[_aws_cdk_aws_autoscaling_ceddda9d.BlockDevice, typing.Dict[builtins.str, typing.Any]]]] = None,
    capacity_rebalance: typing.Optional[builtins.bool] = None,
    cooldown: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
    default_instance_warmup: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
    desired_capacity: typing.Optional[jsii.Number] = None,
    group_metrics: typing.Optional[typing.Sequence[_aws_cdk_aws_autoscaling_ceddda9d.GroupMetrics]] = None,
    health_check: typing.Optional[_aws_cdk_aws_autoscaling_ceddda9d.HealthCheck] = None,
    health_checks: typing.Optional[_aws_cdk_aws_autoscaling_ceddda9d.HealthChecks] = None,
    ignore_unmodified_size_properties: typing.Optional[builtins.bool] = None,
    instance_monitoring: typing.Optional[_aws_cdk_aws_autoscaling_ceddda9d.Monitoring] = None,
    key_name: typing.Optional[builtins.str] = None,
    key_pair: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IKeyPair] = None,
    max_capacity: typing.Optional[jsii.Number] = None,
    max_instance_lifetime: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
    min_capacity: typing.Optional[jsii.Number] = None,
    new_instances_protected_from_scale_in: typing.Optional[builtins.bool] = None,
    notifications: typing.Optional[typing.Sequence[typing.Union[_aws_cdk_aws_autoscaling_ceddda9d.NotificationConfiguration, typing.Dict[builtins.str, typing.Any]]]] = None,
    signals: typing.Optional[_aws_cdk_aws_autoscaling_ceddda9d.Signals] = None,
    spot_price: typing.Optional[builtins.str] = None,
    ssm_session_permissions: typing.Optional[builtins.bool] = None,
    termination_policies: typing.Optional[typing.Sequence[_aws_cdk_aws_autoscaling_ceddda9d.TerminationPolicy]] = None,
    termination_policy_custom_lambda_function_arn: typing.Optional[builtins.str] = None,
    update_policy: typing.Optional[_aws_cdk_aws_autoscaling_ceddda9d.UpdatePolicy] = None,
    vpc_subnets: typing.Optional[typing.Union[_aws_cdk_aws_ec2_ceddda9d.SubnetSelection, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fd88626e858659904edafa02fcbf622da5c2eba9e7e88a2512e50d8bf55d51eb(
    id: builtins.str,
    chart: _constructs_77d1e7e8.Construct,
    *,
    ingress_alb: typing.Optional[builtins.bool] = None,
    ingress_alb_scheme: typing.Optional[AlbScheme] = None,
    prune: typing.Optional[builtins.bool] = None,
    skip_validation: typing.Optional[builtins.bool] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__270d94658e88e002a679c76d9279cdccae0092dfe69e76cb95c6369f63472767(
    id: builtins.str,
    *,
    selectors: typing.Sequence[typing.Union[Selector, typing.Dict[builtins.str, typing.Any]]],
    fargate_profile_name: typing.Optional[builtins.str] = None,
    pod_execution_role: typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole] = None,
    subnet_selection: typing.Optional[typing.Union[_aws_cdk_aws_ec2_ceddda9d.SubnetSelection, typing.Dict[builtins.str, typing.Any]]] = None,
    vpc: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IVpc] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__331a0171c170acae0c4098b1da2d9d25e1be7a7ab7af71e57bda308b57563a5e(
    id: builtins.str,
    *,
    atomic: typing.Optional[builtins.bool] = None,
    chart: typing.Optional[builtins.str] = None,
    chart_asset: typing.Optional[_aws_cdk_aws_s3_assets_ceddda9d.Asset] = None,
    create_namespace: typing.Optional[builtins.bool] = None,
    namespace: typing.Optional[builtins.str] = None,
    release: typing.Optional[builtins.str] = None,
    repository: typing.Optional[builtins.str] = None,
    skip_crds: typing.Optional[builtins.bool] = None,
    timeout: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
    values: typing.Optional[typing.Mapping[builtins.str, typing.Any]] = None,
    version: typing.Optional[builtins.str] = None,
    wait: typing.Optional[builtins.bool] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__da5cdafdeba9df51e152027ddb1b45b77bb781a77f295eb73b5927f04d5e7b9d(
    id: builtins.str,
    *manifest: typing.Mapping[builtins.str, typing.Any],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__53ffb8b8a0e8d695d7a8d656e57c375a99ce7420e23269e0c1ffb12ebd16fcda(
    id: builtins.str,
    *,
    ami_type: typing.Optional[NodegroupAmiType] = None,
    capacity_type: typing.Optional[CapacityType] = None,
    desired_size: typing.Optional[jsii.Number] = None,
    disk_size: typing.Optional[jsii.Number] = None,
    enable_node_auto_repair: typing.Optional[builtins.bool] = None,
    force_update: typing.Optional[builtins.bool] = None,
    instance_type: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.InstanceType] = None,
    instance_types: typing.Optional[typing.Sequence[_aws_cdk_aws_ec2_ceddda9d.InstanceType]] = None,
    labels: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    launch_template_spec: typing.Optional[typing.Union[LaunchTemplateSpec, typing.Dict[builtins.str, typing.Any]]] = None,
    max_size: typing.Optional[jsii.Number] = None,
    max_unavailable: typing.Optional[jsii.Number] = None,
    max_unavailable_percentage: typing.Optional[jsii.Number] = None,
    min_size: typing.Optional[jsii.Number] = None,
    nodegroup_name: typing.Optional[builtins.str] = None,
    node_role: typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole] = None,
    release_version: typing.Optional[builtins.str] = None,
    remote_access: typing.Optional[typing.Union[NodegroupRemoteAccess, typing.Dict[builtins.str, typing.Any]]] = None,
    subnets: typing.Optional[typing.Union[_aws_cdk_aws_ec2_ceddda9d.SubnetSelection, typing.Dict[builtins.str, typing.Any]]] = None,
    tags: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    taints: typing.Optional[typing.Sequence[typing.Union[TaintSpec, typing.Dict[builtins.str, typing.Any]]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__36a54546780efd88d87f4fa87074bbbd7bbe7dae77512314baf0271c80334b19(
    id: builtins.str,
    *,
    annotations: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    identity_type: typing.Optional[IdentityType] = None,
    labels: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    name: typing.Optional[builtins.str] = None,
    namespace: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2c30a42f1e6c85140faa9a09d0e623dfa0cbf0f349bc35215f806313ad22faa4(
    auto_scaling_group: _aws_cdk_aws_autoscaling_ceddda9d.AutoScalingGroup,
    *,
    bootstrap_enabled: typing.Optional[builtins.bool] = None,
    bootstrap_options: typing.Optional[typing.Union[BootstrapOptions, typing.Dict[builtins.str, typing.Any]]] = None,
    machine_image_type: typing.Optional[MachineImageType] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4fb18943d5a03fdc5b5261720fbcac024d7eadc01b68d2188ca3863fb0079137(
    ingress_name: builtins.str,
    *,
    namespace: typing.Optional[builtins.str] = None,
    timeout: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1af0e770bf9ab42af4d91256c3401240b72d64175dbc01d02cd356e1b0abe7c4(
    service_name: builtins.str,
    *,
    namespace: typing.Optional[builtins.str] = None,
    timeout: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__90b4483311d0a7d87252ed390a8138277fb3ae083bf9d3d36921f72d3de1fd5a(
    id: builtins.str,
    principal: builtins.str,
    access_policies: typing.Sequence[IAccessPolicy],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e1d4f786977ba522de732fe537d5732729fd14835a49d9c2277539b21b2eddc1(
    id: builtins.str,
    principal: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__673db9ae76799e064c85ea6382670fd3efa0ca3c8a72239cc0723fff0872a344(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    default_profile: typing.Optional[typing.Union[FargateProfileOptions, typing.Dict[builtins.str, typing.Any]]] = None,
    version: KubernetesVersion,
    alb_controller: typing.Optional[typing.Union[AlbControllerOptions, typing.Dict[builtins.str, typing.Any]]] = None,
    cluster_logging: typing.Optional[typing.Sequence[ClusterLoggingTypes]] = None,
    cluster_name: typing.Optional[builtins.str] = None,
    core_dns_compute_type: typing.Optional[CoreDnsComputeType] = None,
    endpoint_access: typing.Optional[EndpointAccess] = None,
    ip_family: typing.Optional[IpFamily] = None,
    kubectl_provider_options: typing.Optional[typing.Union[KubectlProviderOptions, typing.Dict[builtins.str, typing.Any]]] = None,
    masters_role: typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole] = None,
    prune: typing.Optional[builtins.bool] = None,
    role: typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole] = None,
    secrets_encryption_key: typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey] = None,
    security_group: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup] = None,
    service_ipv4_cidr: typing.Optional[builtins.str] = None,
    tags: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    vpc: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IVpc] = None,
    vpc_subnets: typing.Optional[typing.Sequence[typing.Union[_aws_cdk_aws_ec2_ceddda9d.SubnetSelection, typing.Dict[builtins.str, typing.Any]]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__867c24d91e82b6c927deaaa713ad154d44030f8a2d7da291636600790dfebd5e(
    *,
    namespace: typing.Optional[builtins.str] = None,
    timeout: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
) -> None:
    """Type checking stubs"""
    pass
