# Amazon VpcV2 Construct Library

<!--BEGIN STABILITY BANNER-->---


![cdk-constructs: Developer Preview](https://img.shields.io/badge/cdk--constructs-developer--preview-informational.svg?style=for-the-badge)

> The APIs of higher level constructs in this module are in **developer preview** before they
> become stable. We will only make breaking changes to address unforeseen API issues. Therefore,
> these APIs are not subject to [Semantic Versioning](https://semver.org/), and breaking changes
> will be announced in release notes. This means that while you may use them, you may need to
> update your source code when upgrading to a newer version of this package.

---
<!--END STABILITY BANNER-->

## VpcV2

`VpcV2` is a re-write of the [`ec2.Vpc`](https://docs.aws.amazon.com/cdk/api/v2/docs/aws-cdk-lib.aws_ec2.Vpc.html) construct. This new construct enables higher level of customization
on the VPC being created. `VpcV2` implements the existing [`IVpc`](https://docs.aws.amazon.com/cdk/api/v2/docs/aws-cdk-lib.aws_ec2.IVpc.html), therefore,
`VpcV2` is compatible with other constructs that accepts `IVpc` (e.g. [`ApplicationLoadBalancer`](https://docs.aws.amazon.com/cdk/api/v2/docs/aws-cdk-lib.aws_elasticloadbalancingv2.ApplicationLoadBalancer.html#construct-props)).

`VpcV2` supports the addition of both primary and secondary addresses. The primary address must be an IPv4 address, which can be specified as a CIDR string or assigned from an IPAM pool. Secondary addresses can be either IPv4 or IPv6.
By default, `VpcV2` assigns `10.0.0.0/16` as the primary CIDR if no other CIDR is specified.

Below is an example of creating a VPC with both IPv4 and IPv6 support:

```python
stack = Stack()
VpcV2(self, "Vpc",
    primary_address_block=IpAddresses.ipv4("10.0.0.0/24"),
    secondary_address_blocks=[
        IpAddresses.amazon_provided_ipv6(cidr_block_name="AmazonProvidedIpv6")
    ]
)
```

`VpcV2` does not automatically create subnets or allocate IP addresses, which is different from the `Vpc` construct.

## SubnetV2

`SubnetV2` is a re-write of the [`ec2.Subnet`](https://docs.aws.amazon.com/cdk/api/v2/docs/aws-cdk-lib.aws_ec2.Subnet.html) construct.
This new construct can be used to add subnets to a `VpcV2` instance:
Note: When defining a subnet with `SubnetV2`, CDK automatically creates a new route table, unless a route table is explicitly provided as an input to the construct.
To enable the `mapPublicIpOnLaunch` feature (which is `false` by default), set the property to `true` when creating the subnet.

```python
stack = Stack()
my_vpc = VpcV2(self, "Vpc",
    secondary_address_blocks=[
        IpAddresses.amazon_provided_ipv6(cidr_block_name="AmazonProvidedIp")
    ]
)

SubnetV2(self, "subnetA",
    vpc=my_vpc,
    availability_zone="us-east-1a",
    ipv4_cidr_block=IpCidr("10.0.0.0/24"),
    ipv6_cidr_block=IpCidr("2a05:d02c:25:4000::/60"),
    subnet_type=SubnetType.PUBLIC,
    map_public_ip_on_launch=True
)
```

Since `VpcV2` does not create subnets automatically, users have full control over IP addresses allocation across subnets.

## IP Addresses Management

Additional CIDRs can be added to the VPC via the `secondaryAddressBlocks` property.
The following example illustrates the options of defining these secondary address blocks using `IPAM`:

Note: There’s currently an issue with IPAM pool deletion that may affect the `cdk --destroy` command. This is because IPAM takes time to detect when the IP address pool has been deallocated after the VPC is deleted. The current workaround is to wait until the IP address is fully deallocated from the pool before retrying the deletion. Below command can be used to check allocations for a pool using CLI

```shell
aws ec2 get-ipam-pool-allocations --ipam-pool-id <ipam-pool-id>
```

Ref: https://docs.aws.amazon.com/cli/latest/reference/ec2/get-ipam-pool-allocations.html

```python
stack = Stack()
ipam = Ipam(self, "Ipam",
    operating_regions=["us-west-1"]
)
ipam_public_pool = ipam.public_scope.add_pool("PublicPoolA",
    address_family=AddressFamily.IP_V6,
    aws_service=AwsServiceName.EC2,
    locale="us-west-1",
    public_ip_source=IpamPoolPublicIpSource.AMAZON
)
ipam_public_pool.provision_cidr("PublicPoolACidrA", netmask_length=52)

ipam_private_pool = ipam.private_scope.add_pool("PrivatePoolA",
    address_family=AddressFamily.IP_V4
)
ipam_private_pool.provision_cidr("PrivatePoolACidrA", netmask_length=8)

VpcV2(self, "Vpc",
    primary_address_block=IpAddresses.ipv4("10.0.0.0/24"),
    secondary_address_blocks=[
        IpAddresses.amazon_provided_ipv6(cidr_block_name="AmazonIpv6"),
        IpAddresses.ipv6_ipam(
            ipam_pool=ipam_public_pool,
            netmask_length=52,
            cidr_block_name="ipv6Ipam"
        ),
        IpAddresses.ipv4_ipam(
            ipam_pool=ipam_private_pool,
            netmask_length=8,
            cidr_block_name="ipv4Ipam"
        )
    ]
)
```

### Bring your own IPv6 addresses (BYOIP)

If you have your own IP address that you would like to use with EC2, you can set up an IPv6 pool via the AWS CLI, and use that pool ID in your application.

Once you have certified your IP address block with an ROA and have obtained an X-509 certificate, you can run the following command to provision your CIDR block in your AWS account:

```shell
aws ec2 provision-byoip-cidr --region <region> --cidr <your CIDR block> --cidr-authorization-context Message="1|aws|<account>|<your CIDR block>|<expiration date>|SHA256".Signature="<signature>"
```

When your BYOIP CIDR is provisioned, you can run the following command to retrieve your IPv6 pool ID, which will be used in your VPC declaration:

```shell
aws ec2 describe-byoip-cidr --region <region>
```

For more help on setting up your IPv6 address, please review the [EC2 Documentation](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/ec2-byoip.html).

Once you have provisioned your address block, you can use the IPv6 in your VPC as follows:

```python
my_vpc = VpcV2(self, "Vpc",
    primary_address_block=IpAddresses.ipv4("10.1.0.0/16"),
    secondary_address_blocks=[IpAddresses.ipv6_byoip_pool(
        cidr_block_name="MyByoipCidrBlock",
        ipv6_pool_id="ipv6pool-ec2-someHashValue",
        ipv6_cidr_block="2001:db8::/32"
    )],
    enable_dns_hostnames=True,
    enable_dns_support=True
)
```

## Routing

`RouteTable` is a new construct that allows for route tables to be customized in a variety of ways. Using this construct, a customized route table can be added to the subnets defined using `SubnetV2`.
For instance, the following example shows how a custom route table can be created and appended to a `SubnetV2`:

```python
my_vpc = VpcV2(self, "Vpc")
route_table = RouteTable(self, "RouteTable",
    vpc=my_vpc
)
subnet = SubnetV2(self, "Subnet",
    vpc=my_vpc,
    route_table=route_table,
    availability_zone="eu-west-2a",
    ipv4_cidr_block=IpCidr("10.0.0.0/24"),
    subnet_type=SubnetType.PRIVATE_ISOLATED
)
```

`Routes` can be created to link subnets to various different AWS services via gateways and endpoints. Each unique route target has its own dedicated construct that can be routed to a given subnet via the `Route` construct. An example using the `InternetGateway` construct can be seen below:

```python
stack = Stack()
my_vpc = VpcV2(self, "Vpc")
route_table = RouteTable(self, "RouteTable",
    vpc=my_vpc
)
subnet = SubnetV2(self, "Subnet",
    vpc=my_vpc,
    availability_zone="eu-west-2a",
    ipv4_cidr_block=IpCidr("10.0.0.0/24"),
    subnet_type=SubnetType.PRIVATE_ISOLATED
)

igw = InternetGateway(self, "IGW",
    vpc=my_vpc
)
Route(self, "IgwRoute",
    route_table=route_table,
    destination="0.0.0.0/0",
    target={"gateway": igw}
)
```

Alternatively, `Routes` can also be created via method `addRoute` in the `RouteTable` class. An example using the `EgressOnlyInternetGateway` construct can be seen below:
Note: `EgressOnlyInternetGateway` can only be used to set up outbound IPv6 routing.

```python
stack = Stack()
my_vpc = VpcV2(self, "Vpc",
    primary_address_block=IpAddresses.ipv4("10.1.0.0/16"),
    secondary_address_blocks=[IpAddresses.amazon_provided_ipv6(
        cidr_block_name="AmazonProvided"
    )]
)

eigw = EgressOnlyInternetGateway(self, "EIGW",
    vpc=my_vpc
)

route_table = RouteTable(self, "RouteTable",
    vpc=my_vpc
)

route_table.add_route("EIGW", "::/0", {"gateway": eigw})
```

Other route targets may require a deeper set of parameters to set up properly. For instance, the example below illustrates how to set up a `NatGateway`:

```python
my_vpc = VpcV2(self, "Vpc")
route_table = RouteTable(self, "RouteTable",
    vpc=my_vpc
)
subnet = SubnetV2(self, "Subnet",
    vpc=my_vpc,
    availability_zone="eu-west-2a",
    ipv4_cidr_block=IpCidr("10.0.0.0/24"),
    subnet_type=SubnetType.PRIVATE_ISOLATED
)

natgw = NatGateway(self, "NatGW",
    subnet=subnet,
    vpc=my_vpc,
    connectivity_type=NatConnectivityType.PRIVATE,
    private_ip_address="10.0.0.42"
)
Route(self, "NatGwRoute",
    route_table=route_table,
    destination="0.0.0.0/0",
    target={"gateway": natgw}
)
```

It is also possible to set up endpoints connecting other AWS services. For instance, the example below illustrates the linking of a Dynamo DB endpoint via the existing `ec2.GatewayVpcEndpoint` construct as a route target:

```python
stack = Stack()
my_vpc = VpcV2(self, "Vpc")
route_table = RouteTable(self, "RouteTable",
    vpc=my_vpc
)
subnet = SubnetV2(self, "Subnet",
    vpc=my_vpc,
    availability_zone="eu-west-2a",
    ipv4_cidr_block=IpCidr("10.0.0.0/24"),
    subnet_type=SubnetType.PRIVATE
)

dynamo_endpoint = ec2.GatewayVpcEndpoint(self, "DynamoEndpoint",
    service=ec2.GatewayVpcEndpointAwsService.DYNAMODB,
    vpc=my_vpc,
    subnets=[subnet]
)
Route(self, "DynamoDBRoute",
    route_table=route_table,
    destination="0.0.0.0/0",
    target={"endpoint": dynamo_endpoint}
)
```

## VPC Peering Connection

VPC peering connection allows you to connect two VPCs and route traffic between them using private IP addresses. The VpcV2 construct supports creating VPC peering connections through the `VPCPeeringConnection` construct from the `route` module.

Peering Connection cannot be established between two VPCs with overlapping CIDR ranges. Please make sure the two VPC CIDRs do not overlap with each other else it will throw an error.

For more information, see [What is VPC peering?](https://docs.aws.amazon.com/vpc/latest/peering/what-is-vpc-peering.html).

The following show examples of how to create a peering connection between two VPCs for all possible combinations of same-account or cross-account, and same-region or cross-region configurations.

Note: You cannot create a VPC peering connection between VPCs that have matching or overlapping CIDR blocks

**Case 1: Same Account and Same Region Peering Connection**

```python
stack = Stack()

vpc_a = VpcV2(self, "VpcA",
    primary_address_block=IpAddresses.ipv4("10.0.0.0/16")
)

vpc_b = VpcV2(self, "VpcB",
    primary_address_block=IpAddresses.ipv4("10.1.0.0/16")
)

peering_connection = vpc_a.create_peering_connection("sameAccountSameRegionPeering",
    acceptor_vpc=vpc_b
)
```

**Case 2: Same Account and Cross Region Peering Connection**

There is no difference from Case 1 when calling `createPeeringConnection`. The only change is that one of the VPCs are created in another stack with a different region. To establish cross region VPC peering connection, acceptorVpc needs to be imported to the requestor VPC stack using `fromVpcV2Attributes` method.

```python
app = App()

stack_a = Stack(app, "VpcStackA", env=Environment(account="000000000000", region="us-east-1"))
stack_b = Stack(app, "VpcStackB", env=Environment(account="000000000000", region="us-west-2"))

vpc_a = VpcV2(stack_a, "VpcA",
    primary_address_block=IpAddresses.ipv4("10.0.0.0/16")
)

VpcV2(stack_b, "VpcB",
    primary_address_block=IpAddresses.ipv4("10.1.0.0/16")
)

vpc_b = VpcV2.from_vpc_v2_attributes(stack_a, "ImportedVpcB",
    vpc_id="MockVpcBid",
    vpc_cidr_block="10.1.0.0/16",
    region="us-west-2",
    owner_account_id="000000000000"
)

peering_connection = vpc_a.create_peering_connection("sameAccountCrossRegionPeering",
    acceptor_vpc=vpc_b
)
```

**Case 3: Cross Account Peering Connection**

For cross-account connections, the acceptor account needs an IAM role that grants the requestor account permission to initiate the connection. Create a new IAM role in the acceptor account using method `createAcceptorVpcRole` to provide the necessary permissions.

Once role is created in account, provide role arn for field `peerRoleArn` under method `createPeeringConnection`

```python
stack = Stack()

acceptor_vpc = VpcV2(self, "VpcA",
    primary_address_block=IpAddresses.ipv4("10.0.0.0/16")
)

acceptor_role_arn = acceptor_vpc.create_acceptor_vpc_role("000000000000")
```

After creating an IAM role in the acceptor account, we can initiate the peering connection request from the requestor VPC. Import acceptorVpc to the stack using `fromVpcV2Attributes` method, it is recommended to specify owner account id of the acceptor VPC in case of cross account peering connection, if acceptor VPC is hosted in different region provide region value for import as well.
The following code snippet demonstrates how to set up VPC peering between two VPCs in different AWS accounts using CDK:

```python
stack = Stack()

acceptor_vpc = VpcV2.from_vpc_v2_attributes(self, "acceptorVpc",
    vpc_id="vpc-XXXX",
    vpc_cidr_block="10.0.0.0/16",
    region="us-east-2",
    owner_account_id="111111111111"
)

acceptor_role_arn = "arn:aws:iam::111111111111:role/VpcPeeringRole"

requestor_vpc = VpcV2(self, "VpcB",
    primary_address_block=IpAddresses.ipv4("10.1.0.0/16")
)

peering_connection = requestor_vpc.create_peering_connection("crossAccountCrossRegionPeering",
    acceptor_vpc=acceptor_vpc,
    peer_role_arn=acceptor_role_arn
)
```

### Route Table Configuration

After establishing the VPC peering connection, routes must be added to the respective route tables in the VPCs to enable traffic flow. If a route is added to the requestor stack, information will be able to flow from the requestor VPC to the acceptor VPC, but not in the reverse direction. For bi-directional communication, routes need to be added in both VPCs from their respective stacks.

For more information, see [Update your route tables for a VPC peering connection](https://docs.aws.amazon.com/vpc/latest/peering/vpc-peering-routing.html).

```python
stack = Stack()

acceptor_vpc = VpcV2(self, "VpcA",
    primary_address_block=IpAddresses.ipv4("10.0.0.0/16")
)

requestor_vpc = VpcV2(self, "VpcB",
    primary_address_block=IpAddresses.ipv4("10.1.0.0/16")
)

peering_connection = requestor_vpc.create_peering_connection("peeringConnection",
    acceptor_vpc=acceptor_vpc
)

route_table = RouteTable(self, "RouteTable",
    vpc=requestor_vpc
)

route_table.add_route("vpcPeeringRoute", "10.0.0.0/16", {"gateway": peering_connection})
```

This can also be done using AWS CLI. For more information, see [create-route](https://docs.aws.amazon.com/cli/latest/reference/ec2/create-route.html).

```bash
# Add a route to the requestor VPC route table
aws ec2 create-route --route-table-id rtb-requestor --destination-cidr-block 10.0.0.0/16 --vpc-peering-connection-id pcx-xxxxxxxx

# For bi-directional add a route in the acceptor vpc account as well
aws ec2 create-route --route-table-id rtb-acceptor --destination-cidr-block 10.1.0.0/16 --vpc-peering-connection-id pcx-xxxxxxxx
```

### Deleting the Peering Connection

To delete a VPC peering connection, use the following command:

```bash
aws ec2 delete-vpc-peering-connection --vpc-peering-connection-id pcx-xxxxxxxx
```

For more information, see [Delete a VPC peering connection](https://docs.aws.amazon.com/vpc/latest/peering/create-vpc-peering-connection.html#delete-vpc-peering-connection).

## Adding Egress-Only Internet Gateway to VPC

An egress-only internet gateway is a horizontally scaled, redundant, and highly available VPC component that allows outbound communication over IPv6 from instances in your VPC to the internet, and prevents the internet from initiating an IPv6 connection with your instances.

For more information see [Enable outbound IPv6 traffic using an egress-only internet gateway](https://docs.aws.amazon.com/vpc/latest/userguide/egress-only-internet-gateway.html).

VpcV2 supports adding an egress only internet gateway to VPC using the `addEgressOnlyInternetGateway` method.

By default, this method sets up a route to all outbound IPv6 address ranges, unless a specific destination is provided by the user. It can only be configured for IPv6-enabled VPCs.
The `Subnets` parameter accepts a `SubnetFilter`, which can be based on a `SubnetType` in VpcV2. A new route will be added to the route tables of all subnets that match this filter.

```python
stack = Stack()
my_vpc = VpcV2(self, "Vpc",
    primary_address_block=IpAddresses.ipv4("10.1.0.0/16"),
    secondary_address_blocks=[IpAddresses.amazon_provided_ipv6(
        cidr_block_name="AmazonProvided"
    )]
)
route_table = RouteTable(self, "RouteTable",
    vpc=my_vpc
)
subnet = SubnetV2(self, "Subnet",
    vpc=my_vpc,
    availability_zone="eu-west-2a",
    ipv4_cidr_block=IpCidr("10.0.0.0/24"),
    ipv6_cidr_block=IpCidr("2001:db8:1::/64"),
    subnet_type=SubnetType.PRIVATE
)

my_vpc.add_egress_only_internet_gateway(
    subnets=[ec2.SubnetSelection(subnet_type=SubnetType.PRIVATE)],
    destination="::/60"
)
```

## Adding NATGateway to the VPC

A NAT gateway is a Network Address Translation (NAT) service.You can use a NAT gateway so that instances in a private subnet can connect to services outside your VPC but external services cannot initiate a connection with those instances.

For more information, see [NAT gateway basics](https://docs.aws.amazon.com/vpc/latest/userguide/vpc-nat-gateway.html).

When you create a NAT gateway, you specify one of the following connectivity types:

**Public – (Default)**: Instances in private subnets can connect to the internet through a public NAT gateway, but cannot receive unsolicited inbound connections from the internet

**Private**: Instances in private subnets can connect to other VPCs or your on-premises network through a private NAT gateway.

To define the NAT gateway connectivity type as `ConnectivityType.Public`, you need to ensure that there is an IGW(Internet Gateway) attached to the subnet's VPC.
Since a NATGW is associated with a particular subnet, providing `subnet` field in the input props is mandatory.

Additionally, you can set up a route in any route table with the target set to the NAT Gateway. The function `addNatGateway` returns a `NATGateway` object that you can reference later.

The code example below provides the definition for adding a NAT gateway to your subnet:

```python
stack = Stack()
my_vpc = VpcV2(self, "Vpc")
route_table = RouteTable(self, "RouteTable",
    vpc=my_vpc
)
subnet = SubnetV2(self, "Subnet",
    vpc=my_vpc,
    availability_zone="eu-west-2a",
    ipv4_cidr_block=IpCidr("10.0.0.0/24"),
    subnet_type=SubnetType.PUBLIC
)

my_vpc.add_internet_gateway()
my_vpc.add_nat_gateway(
    subnet=subnet,
    connectivity_type=NatConnectivityType.PUBLIC
)
```

## Enable VPNGateway for the VPC

A virtual private gateway is the endpoint on the VPC side of your VPN connection.

For more information, see [What is AWS Site-to-Site VPN?](https://docs.aws.amazon.com/vpn/latest/s2svpn/VPC_VPN.html).

VPN route propagation is a feature in Amazon Web Services (AWS) that automatically updates route tables in your Virtual Private Cloud (VPC) with routes learned from a VPN connection.

To enable VPN route propagation, use the `vpnRoutePropagation` property to specify the subnets as an input to the function. VPN route propagation will then be enabled for each subnet with the corresponding route table IDs.

Additionally, you can set up a route in any route table with the target set to the VPN Gateway. The function `enableVpnGatewayV2` returns a `VPNGatewayV2` object that you can reference later.

The code example below provides the definition for setting up a VPN gateway with `vpnRoutePropagation` enabled:

```python
stack = Stack()
my_vpc = VpcV2(self, "Vpc")
vpn_gateway = my_vpc.enable_vpn_gateway_v2(
    vpn_route_propagation=[ec2.SubnetSelection(subnet_type=SubnetType.PUBLIC)],
    type=VpnConnectionType.IPSEC_1
)

route_table = RouteTable(stack, "routeTable",
    vpc=my_vpc
)

Route(stack, "route",
    destination="172.31.0.0/24",
    target={"gateway": vpn_gateway},
    route_table=route_table
)
```

## Adding InternetGateway to the VPC

An internet gateway is a horizontally scaled, redundant, and highly available VPC component that allows communication between your VPC and the internet. It supports both IPv4 and IPv6 traffic.

For more information, see [Enable VPC internet access using internet gateways](https://docs.aws.amazon.com/vpc/latest/userguide/vpc-igw-internet-access.html).

You can add an internet gateway to a VPC using `addInternetGateway` method. By default, this method creates a route in all Public Subnets with outbound destination set to `0.0.0.0` for IPv4 and `::0` for IPv6 enabled VPC.
Instead of using the default settings, you can configure a custom destination range by providing an optional input `destination` to the method.
In addition to the custom IP range, you can also choose to filter subnets where default routes should be created.

The code example below shows how to add an internet gateway with a custom outbound destination IP range:

```python
stack = Stack()
my_vpc = VpcV2(self, "Vpc")

subnet = SubnetV2(self, "Subnet",
    vpc=my_vpc,
    availability_zone="eu-west-2a",
    ipv4_cidr_block=IpCidr("10.0.0.0/24"),
    subnet_type=SubnetType.PUBLIC
)

my_vpc.add_internet_gateway(
    ipv4_destination="192.168.0.0/16"
)
```

The following code examples demonstrates how to add an internet gateway with a custom outbound destination IP range for specific subnets:

```python
stack = Stack()
my_vpc = VpcV2(self, "Vpc")

my_subnet = SubnetV2(self, "Subnet",
    vpc=my_vpc,
    availability_zone="eu-west-2a",
    ipv4_cidr_block=IpCidr("10.0.0.0/24"),
    subnet_type=SubnetType.PUBLIC
)

my_vpc.add_internet_gateway(
    ipv4_destination="192.168.0.0/16",
    subnets=[my_subnet]
)
```

```python
stack = Stack()
my_vpc = VpcV2(self, "Vpc")

my_vpc.add_internet_gateway(
    ipv4_destination="192.168.0.0/16",
    subnets=[ec2.SubnetSelection(subnet_type=SubnetType.PRIVATE_WITH_EGRESS)]
)
```

## Importing an existing VPC

You can import an existing VPC and its subnets using the `VpcV2.fromVpcV2Attributes()` method or an individual subnet using `SubnetV2.fromSubnetV2Attributes()` method.

### Importing a VPC

To import an existing VPC, use the `VpcV2.fromVpcV2Attributes()` method. You'll need to provide the VPC ID, primary CIDR block, and information about the subnets. You can import secondary address as well created through IPAM, BYOIP(IPv4) or enabled through Amazon Provided IPv6. You must provide VPC Id and its primary CIDR block for importing it.

If you wish to add a new subnet to imported VPC, new subnet's IP range(IPv4) will be validated against provided secondary and primary address block to confirm that it is within the the range of VPC.

Here's an example of importing a VPC with only the required parameters

```python
stack = Stack()

imported_vpc = VpcV2.from_vpc_v2_attributes(stack, "ImportedVpc",
    vpc_id="mockVpcID",
    vpc_cidr_block="10.0.0.0/16"
)
```

In case of cross account or cross region VPC, its recommended to provide region and ownerAccountId so that these values for the VPC can be used to populate correct arn value for the VPC. If a VPC region and account ID is not provided, then region and account configured in the stack will be used. Furthermore, these fields will be referenced later while setting up VPC peering connection, so its necessary to set these fields to a correct value.

Below is an example of importing a cross region and cross account VPC, VPC arn for this case would be 'arn:aws:ec2:us-west-2:123456789012:vpc/mockVpcID'

```python
stack = Stack()

# Importing a cross account or cross region VPC
imported_vpc = VpcV2.from_vpc_v2_attributes(stack, "ImportedVpc",
    vpc_id="mockVpcID",
    vpc_cidr_block="10.0.0.0/16",
    owner_account_id="123456789012",
    region="us-west-2"
)
```

Here's an example of how to import a VPC with multiple CIDR blocks, IPv6 support, and different subnet types:

In this example, we're importing a VPC with:

* A primary CIDR block (10.1.0.0/16)
* One secondary IPv4 CIDR block (10.2.0.0/16)
* Two secondary address using IPAM pool (IPv4 and IPv6)
* VPC has Amazon-provided IPv6 CIDR enabled
* An isolated subnet in us-west-2a
* A public subnet in us-west-2b

```python
stack = Stack()

imported_vpc = VpcV2.from_vpc_v2_attributes(self, "ImportedVPC",
    vpc_id="vpc-XXX",
    vpc_cidr_block="10.1.0.0/16",
    secondary_cidr_blocks=[VPCCidrBlockattributes(
        cidr_block="10.2.0.0/16",
        cidr_block_name="ImportedBlock1"
    ), VPCCidrBlockattributes(
        ipv6_ipam_pool_id="ipam-pool-XXX",
        ipv6_netmask_length=52,
        cidr_block_name="ImportedIpamIpv6"
    ), VPCCidrBlockattributes(
        ipv4_ipam_pool_id="ipam-pool-XXX",
        ipv4_ipam_provisioned_cidrs=["10.2.0.0/16"],
        cidr_block_name="ImportedIpamIpv4"
    ), VPCCidrBlockattributes(
        amazon_provided_ipv6_cidr_block=True
    )
    ],
    subnets=[SubnetV2Attributes(
        subnet_name="IsolatedSubnet2",
        subnet_id="subnet-03cd773c0fe08ed26",
        subnet_type=SubnetType.PRIVATE_ISOLATED,
        availability_zone="us-west-2a",
        ipv4_cidr_block="10.2.0.0/24",
        route_table_id="rtb-0871c310f98da2cbb"
    ), SubnetV2Attributes(
        subnet_id="subnet-0fa477e01db27d820",
        subnet_type=SubnetType.PUBLIC,
        availability_zone="us-west-2b",
        ipv4_cidr_block="10.3.0.0/24",
        route_table_id="rtb-014f3043098fe4b96"
    )]
)

# You can now use the imported VPC in your stack

# Adding a new subnet to the imported VPC
imported_subnet = SubnetV2(self, "NewSubnet",
    availability_zone="us-west-2a",
    ipv4_cidr_block=IpCidr("10.2.2.0/24"),
    vpc=imported_vpc,
    subnet_type=SubnetType.PUBLIC
)

# Adding gateways to the imported VPC
imported_vpc.add_internet_gateway()
imported_vpc.add_nat_gateway(subnet=imported_subnet)
imported_vpc.add_egress_only_internet_gateway()
```

You can add more subnets as needed by including additional entries in the `isolatedSubnets`, `publicSubnets`, or other subnet type arrays (e.g., `privateSubnets`).

### Importing Subnets

You can also import individual subnets using the `SubnetV2.fromSubnetV2Attributes()` method. This is useful when you need to work with specific subnets independently of a VPC.

Here's an example of how to import a subnet:

```python
SubnetV2.from_subnet_v2_attributes(self, "ImportedSubnet",
    subnet_id="subnet-0123456789abcdef0",
    availability_zone="us-west-2a",
    ipv4_cidr_block="10.2.0.0/24",
    route_table_id="rtb-0871c310f98da2cbb",
    subnet_type=SubnetType.PRIVATE_ISOLATED
)
```

By importing existing VPCs and subnets, you can easily integrate your existing AWS infrastructure with new resources created through CDK. This is particularly useful when you need to work with pre-existing network configurations or when you're migrating existing infrastructure to CDK.

### Tagging VPC and its components

By default, when a resource name is given to the construct, it automatically adds a tag with the key `Name` and the value set to the provided resource name. To add additional custom tags, use the Tag Manager, like this: `Tags.of(myConstruct).add('key', 'value');`.

For example, if the `vpcName` is set to `TestVpc`, the following code will add a tag to the VPC with `key: Name` and `value: TestVpc`.

```python
vpc = VpcV2(self, "VPC-integ-test-tag",
    primary_address_block=IpAddresses.ipv4("10.1.0.0/16"),
    enable_dns_hostnames=True,
    enable_dns_support=True,
    vpc_name="CDKintegTestVPC"
)

# Add custom tags if needed
Tags.of(vpc).add("Environment", "Production")
```

## Transit Gateway

The AWS Transit Gateway construct library allows you to create and configure Transit Gateway resources using AWS CDK.

See [AWS Transit Gateway Docs](docs.aws.amazon.com/vpc/latest/tgw/what-is-transit-gateway.html) for more info.

### Overview

The Transit Gateway construct (`TransitGateway`) is the main entry point for creating and managing your Transit Gateway infrastructure. It provides methods to create route tables, attach VPCs, and configure cross-account access.

The Transit Gateway construct library provides four main constructs:

* `TransitGateway`: The central hub for your network connections
* `TransitGatewayRouteTable`: Manages routing between attached networks
* `TransitGatewayVpcAttachment`: Connects VPCs to the Transit Gateway
* `TransitGatewayRoute`: Defines routing rules within your Transit Gateway

### Basic Usage

To create a minimal deployable `TransitGateway`:

```python
transit_gateway = TransitGateway(self, "MyTransitGateway")
```

### Default Transit Gateway Route Table

By default, `TransitGateway` is created with a default `TransitGatewayRouteTable`, for which automatic Associations and automatic Propagations are enabled.

> Note: When you create a default Transit Gateway in AWS Console, a default Transit Gateway Route Table is automatically created by AWS. However, when using the CDK Transit Gateway L2 construct, the underlying L1 construct is configured with `defaultRouteTableAssociation` and `defaultRouteTablePropagation` explicitly disabled. This ensures that AWS does not create the default route table, allowing the CDK to define a custom default route table instead.
>
> As a result, in the AWS Console, the **Default association route table** and **Default propagation route table** settings will appear as disabled. Despite this, the CDK still provides automatic association and propagation functionality through its internal implementation, which can be controlled using the `defaultRouteTableAssociation` and `defaultRouteTablePropagation` properties within the CDK.

You can disable the automatic Association/Propagation on the default `TransitGatewayRouteTable` via the `TransitGateway` properties. This will still create a default route table for you:

```python
transit_gateway = TransitGateway(self, "MyTransitGateway",
    default_route_table_association=False,
    default_route_table_propagation=False
)
```

### Transit Gateway Route Table Management

Add additional Transit Gateway Route Tables using the `addRouteTable()` method:

```python
transit_gateway = TransitGateway(self, "MyTransitGateway")

route_table = transit_gateway.add_route_table("CustomRouteTable")
```

### Attaching VPCs to the Transit Gateway

Currently only VPC to Transit Gateway attachments are supported.

Create an attachment from a VPC to the Transit Gateway using the `attachVpc()` method:

```python
my_vpc = VpcV2(self, "Vpc")
subnet1 = SubnetV2(self, "Subnet",
    vpc=my_vpc,
    availability_zone="eu-west-2a",
    ipv4_cidr_block=IpCidr("10.0.0.0/24"),
    subnet_type=SubnetType.PUBLIC
)

subnet2 = SubnetV2(self, "Subnet",
    vpc=my_vpc,
    availability_zone="eu-west-2a",
    ipv4_cidr_block=IpCidr("10.0.1.0/24"),
    subnet_type=SubnetType.PUBLIC
)

transit_gateway = TransitGateway(self, "MyTransitGateway")

# Create a basic attachment
attachment = transit_gateway.attach_vpc("VpcAttachment",
    vpc=my_vpc,
    subnets=[subnet1, subnet2]
)

# Create an attachment with optional parameters
attachment_with_options = transit_gateway.attach_vpc("VpcAttachmentWithOptions",
    vpc=my_vpc,
    subnets=[subnet1],
    vpc_attachment_options={
        "dns_support": True,
        "appliance_mode_support": True,
        "ipv6_support": True,
        "security_group_referencing_support": True
    }
)
```

If you want to automatically associate and propagate routes with transit gateway route tables, you can pass the `associationRouteTable` and `propagationRouteTables` parameters. This will automatically create the necessary associations and propagations based on the provided route tables.

```python
my_vpc = VpcV2(self, "Vpc")
subnet1 = SubnetV2(self, "Subnet",
    vpc=my_vpc,
    availability_zone="eu-west-2a",
    ipv4_cidr_block=IpCidr("10.0.0.0/24"),
    subnet_type=SubnetType.PUBLIC
)

subnet2 = SubnetV2(self, "Subnet",
    vpc=my_vpc,
    availability_zone="eu-west-2a",
    ipv4_cidr_block=IpCidr("10.0.1.0/24"),
    subnet_type=SubnetType.PUBLIC
)

transit_gateway = TransitGateway(self, "MyTransitGateway")
association_route_table = transit_gateway.add_route_table("AssociationRouteTable")
propagation_route_table1 = transit_gateway.add_route_table("PropagationRouteTable1")
propagation_route_table2 = transit_gateway.add_route_table("PropagationRouteTable2")

# Create an attachment with automatically created association + propagations
attachment_with_routes = transit_gateway.attach_vpc("VpcAttachment",
    vpc=my_vpc,
    subnets=[subnet1, subnet2],
    association_route_table=association_route_table,
    propagation_route_tables=[propagation_route_table1, propagation_route_table2]
)
```

In this example, the `associationRouteTable` is set to `associationRouteTable`, and `propagationRouteTables` is set to an array containing `propagationRouteTable1` and `propagationRouteTable2`. This triggers the automatic creation of route table associations and route propagations between the Transit Gateway and the specified route tables.

### Adding static routes to the route table

Add static routes using either the `addRoute()` method to add an active route or `addBlackholeRoute()` to add a blackhole route:

```python
transit_gateway = TransitGateway(self, "MyTransitGateway")
route_table = transit_gateway.add_route_table("CustomRouteTable")

my_vpc = VpcV2(self, "Vpc")
subnet = SubnetV2(self, "Subnet",
    vpc=my_vpc,
    availability_zone="eu-west-2a",
    ipv4_cidr_block=IpCidr("10.0.0.0/24"),
    subnet_type=SubnetType.PUBLIC
)

attachment = transit_gateway.attach_vpc("VpcAttachment",
    vpc=my_vpc,
    subnets=[subnet]
)

# Add a static route to direct traffic
route_table.add_route("StaticRoute", attachment, "10.0.0.0/16")

# Block unwanted traffic with a blackhole route
route_table.add_blackhole_route("BlackholeRoute", "172.16.0.0/16")
```

### Route Table Associations and Propagations

Configure route table associations and enable route propagation:

```python
transit_gateway = TransitGateway(self, "MyTransitGateway")
route_table = transit_gateway.add_route_table("CustomRouteTable")
my_vpc = VpcV2(self, "Vpc")
subnet = SubnetV2(self, "Subnet",
    vpc=my_vpc,
    availability_zone="eu-west-2a",
    ipv4_cidr_block=IpCidr("10.0.0.0/24"),
    subnet_type=SubnetType.PUBLIC
)
attachment = transit_gateway.attach_vpc("VpcAttachment",
    vpc=my_vpc,
    subnets=[subnet]
)

# Associate an attachment with a route table
route_table.add_association("Association", attachment)

# Enable route propagation for an attachment
route_table.enable_propagation("Propagation", attachment)
```

**Associations** — The linking of a Transit Gateway attachment to a specific route table, which determines which routes that attachment will use for routing decisions.

**Propagation** — The automatic advertisement of routes from an attachment to a route table, allowing the route table to learn about available network destinations.
