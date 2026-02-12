import * as pulumi from "@pulumi/pulumi";
import * as aws from "@pulumi/aws";

// ---------------------------------------------------------------------------
// Configuration
// ---------------------------------------------------------------------------
const config = new pulumi.Config();
const containerPort = config.getNumber("containerPort") ?? 80;
const cpu = config.getNumber("cpu") ?? 256;
const memory = config.getNumber("memory") ?? 512;
const desiredCount = config.getNumber("desiredCount") ?? 1;
const stackName = pulumi.getStack();

// ---------------------------------------------------------------------------
// VPC – use the default VPC & its subnets for simplicity
// ---------------------------------------------------------------------------
const defaultVpc = pulumi.output(aws.ec2.getVpc({ default: true }));
const defaultVpcId = defaultVpc.id;

const defaultSubnets = defaultVpc.id.apply(vpcId =>
    aws.ec2.getSubnets({
        filters: [{ name: "vpc-id", values: [vpcId] }],
    }),
);
const subnetIds = defaultSubnets.ids;

// ---------------------------------------------------------------------------
// Security Groups
// ---------------------------------------------------------------------------

// ALB security group – allow inbound HTTP from the internet
const albSg = new aws.ec2.SecurityGroup("alb-sg", {
    vpcId: defaultVpcId,
    description: "Allow HTTP inbound to ALB",
    ingress: [{
        protocol: "tcp",
        fromPort: 80,
        toPort: 80,
        cidrBlocks: ["0.0.0.0/0"],
    }],
    egress: [{
        protocol: "-1",
        fromPort: 0,
        toPort: 0,
        cidrBlocks: ["0.0.0.0/0"],
    }],
    tags: {
        Name: `${stackName}-alb-sg`,
        ManagedBy: "Pulumi",
    },
});

// ECS task security group – allow inbound from the ALB only
const taskSg = new aws.ec2.SecurityGroup("task-sg", {
    vpcId: defaultVpcId,
    description: "Allow inbound from ALB to ECS tasks",
    ingress: [{
        protocol: "tcp",
        fromPort: containerPort,
        toPort: containerPort,
        securityGroups: [albSg.id],
    }],
    egress: [{
        protocol: "-1",
        fromPort: 0,
        toPort: 0,
        cidrBlocks: ["0.0.0.0/0"],
    }],
    tags: {
        Name: `${stackName}-task-sg`,
        ManagedBy: "Pulumi",
    },
});

// ---------------------------------------------------------------------------
// Application Load Balancer
// ---------------------------------------------------------------------------
const alb = new aws.lb.LoadBalancer("app-lb", {
    loadBalancerType: "application",
    securityGroups: [albSg.id],
    subnets: subnetIds,
    tags: {
        Name: `${stackName}-alb`,
        ManagedBy: "Pulumi",
    },
});

const targetGroup = new aws.lb.TargetGroup("app-tg", {
    port: containerPort,
    protocol: "HTTP",
    targetType: "ip",
    vpcId: defaultVpcId,
    healthCheck: {
        path: "/",
        protocol: "HTTP",
        matcher: "200",
        interval: 30,
        timeout: 5,
        healthyThreshold: 2,
        unhealthyThreshold: 3,
    },
    tags: {
        Name: `${stackName}-tg`,
        ManagedBy: "Pulumi",
    },
});

const listener = new aws.lb.Listener("app-listener", {
    loadBalancerArn: alb.arn,
    port: 80,
    protocol: "HTTP",
    defaultActions: [{
        type: "forward",
        targetGroupArn: targetGroup.arn,
    }],
});

// ---------------------------------------------------------------------------
// ECS Cluster
// ---------------------------------------------------------------------------
const cluster = new aws.ecs.Cluster("app-cluster", {
    settings: [{
        name: "containerInsights",
        value: "enabled",
    }],
    tags: {
        Name: `${stackName}-cluster`,
        ManagedBy: "Pulumi",
    },
});

// ---------------------------------------------------------------------------
// IAM – Task execution role (allows ECS to pull images & write logs)
// ---------------------------------------------------------------------------
const executionRole = new aws.iam.Role("task-exec-role", {
    assumeRolePolicy: JSON.stringify({
        Version: "2012-10-17",
        Statement: [{
            Action: "sts:AssumeRole",
            Effect: "Allow",
            Principal: { Service: "ecs-tasks.amazonaws.com" },
        }],
    }),
    tags: {
        Name: `${stackName}-task-exec-role`,
        ManagedBy: "Pulumi",
    },
});

new aws.iam.RolePolicyAttachment("task-exec-policy", {
    role: executionRole.name,
    policyArn: "arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy",
});

// ---------------------------------------------------------------------------
// CloudWatch Log Group
// ---------------------------------------------------------------------------
const logGroup = new aws.cloudwatch.LogGroup("app-log-group", {
    retentionInDays: 7,
    tags: {
        Name: `${stackName}-logs`,
        ManagedBy: "Pulumi",
    },
});

// ---------------------------------------------------------------------------
// ECS Task Definition – "Hello World" nginx container
// ---------------------------------------------------------------------------
const taskDefinition = new aws.ecs.TaskDefinition("app-task", {
    family: `${stackName}-hello-world`,
    cpu: cpu.toString(),
    memory: memory.toString(),
    networkMode: "awsvpc",
    requiresCompatibilities: ["FARGATE"],
    executionRoleArn: executionRole.arn,
    containerDefinitions: pulumi.all([logGroup.name]).apply(([lgName]) =>
        JSON.stringify([{
            name: "hello-world",
            image: "nginx:latest",
            essential: true,
            portMappings: [{
                containerPort: containerPort,
                hostPort: containerPort,
                protocol: "tcp",
            }],
            environment: [{
                name: "NGINX_PORT",
                value: containerPort.toString(),
            }],
            logConfiguration: {
                logDriver: "awslogs",
                options: {
                    "awslogs-group": lgName,
                    "awslogs-region": aws.config.region ?? "us-east-1",
                    "awslogs-stream-prefix": "ecs",
                },
            },
        }]),
    ),
    tags: {
        Name: `${stackName}-task`,
        ManagedBy: "Pulumi",
    },
});

// ---------------------------------------------------------------------------
// ECS Service
// ---------------------------------------------------------------------------
const service = new aws.ecs.Service("app-svc", {
    cluster: cluster.arn,
    taskDefinition: taskDefinition.arn,
    desiredCount: desiredCount,
    launchType: "FARGATE",
    networkConfiguration: {
        assignPublicIp: true,
        subnets: subnetIds,
        securityGroups: [taskSg.id],
    },
    loadBalancers: [{
        targetGroupArn: targetGroup.arn,
        containerName: "hello-world",
        containerPort: containerPort,
    }],
    deploymentCircuitBreaker: {
        enable: true,
        rollback: true,
    },
    tags: {
        Name: `${stackName}-svc`,
        ManagedBy: "Pulumi",
    },
}, { dependsOn: [listener] });

// ---------------------------------------------------------------------------
// Exports
// ---------------------------------------------------------------------------
export const clusterName = cluster.name;
export const serviceName = service.name;
export const albDnsName = alb.dnsName;
export const url = pulumi.interpolate`http://${alb.dnsName}`;
