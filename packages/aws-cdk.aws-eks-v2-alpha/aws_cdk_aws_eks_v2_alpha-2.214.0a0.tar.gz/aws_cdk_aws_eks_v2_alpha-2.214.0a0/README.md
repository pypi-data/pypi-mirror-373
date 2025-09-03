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
