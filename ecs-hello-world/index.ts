import * as pulumi from "@pulumi/pulumi";
import * as aws from "@pulumi/aws";
import * as awsx from "@pulumi/awsx";

// ---------------------------------------------------------------------------
// Configuration
// ---------------------------------------------------------------------------
const config = new pulumi.Config();
const containerPort = config.getNumber("containerPort") || 80;
const cpu = config.getNumber("cpu") || 256;
const memory = config.getNumber("memory") || 512;
const desiredCount = config.getNumber("desiredCount") || 2;

const stack = pulumi.getStack();

// ---------------------------------------------------------------------------
// VPC – a multi-AZ VPC with public & private subnets
// ---------------------------------------------------------------------------
const vpc = new awsx.ec2.Vpc("hello-vpc", {
    cidrBlock: "10.0.0.0/16",
    numberOfAvailabilityZones: 2,
    natGateways: {
        strategy: awsx.ec2.NatGatewayStrategy.Single, // cost-optimised; use OnePerAz for prod HA
    },
    subnetSpecs: [
        { type: awsx.ec2.SubnetType.Public, cidrMask: 24 },
        { type: awsx.ec2.SubnetType.Private, cidrMask: 24 },
    ],
    tags: { Name: `hello-vpc-${stack}` },
});

// ---------------------------------------------------------------------------
// ECS Cluster
// ---------------------------------------------------------------------------
const cluster = new aws.ecs.Cluster("hello-cluster", {
    settings: [{
        name: "containerInsights",
        value: "enabled",
    }],
    tags: {
        Environment: stack,
        ManagedBy: "Pulumi",
    },
});

// ---------------------------------------------------------------------------
// Application Load Balancer (internet-facing, in public subnets)
// ---------------------------------------------------------------------------
const alb = new awsx.lb.ApplicationLoadBalancer("hello-alb", {
    subnetIds: vpc.publicSubnetIds,
    defaultTargetGroupPort: containerPort,
    tags: {
        Environment: stack,
        ManagedBy: "Pulumi",
    },
});

// ---------------------------------------------------------------------------
// CloudWatch Log Group for container logs
// ---------------------------------------------------------------------------
const logGroup = new aws.cloudwatch.LogGroup("hello-logs", {
    name: `/ecs/${stack}/hello-world`,
    retentionInDays: 14,
    tags: {
        Environment: stack,
        ManagedBy: "Pulumi",
    },
});

// ---------------------------------------------------------------------------
// ECS Fargate Service – runs a Hello World NGINX container
// ---------------------------------------------------------------------------
const service = new awsx.ecs.FargateService("hello-service", {
    cluster: cluster.arn,
    desiredCount: desiredCount,
    networkConfiguration: {
        subnets: vpc.privateSubnetIds,
        securityGroups: [],     // awsx creates a default SG when empty
    },
    taskDefinitionArgs: {
        container: {
            name: "hello-world",
            // Official NGINX image that serves the default "Welcome to nginx!" page
            image: "nginx:latest",
            cpu: cpu,
            memory: memory,
            essential: true,
            portMappings: [{
                containerPort: containerPort,
                targetGroup: alb.defaultTargetGroup,
            }],
            logConfiguration: {
                logDriver: "awslogs",
                options: {
                    "awslogs-group": logGroup.name,
                    "awslogs-region": aws.config.region!,
                    "awslogs-stream-prefix": "hello",
                },
            },
        },
    },
    tags: {
        Environment: stack,
        ManagedBy: "Pulumi",
    },
});

// ---------------------------------------------------------------------------
// Exports
// ---------------------------------------------------------------------------
export const url = pulumi.interpolate`http://${alb.loadBalancer.dnsName}`;
export const clusterName = cluster.name;
export const vpcId = vpc.vpcId;
