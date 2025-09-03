r'''
# Amazon GameLift Construct Library

<!--BEGIN STABILITY BANNER-->---


![cdk-constructs: Experimental](https://img.shields.io/badge/cdk--constructs-experimental-important.svg?style=for-the-badge)

> The APIs of higher level constructs in this module are experimental and under active development.
> They are subject to non-backward compatible changes or removal in any future version. These are
> not subject to the [Semantic Versioning](https://semver.org/) model and breaking changes will be
> announced in the release notes. This means that while you may use them, you may need to update
> your source code when upgrading to a newer version of this package.

---
<!--END STABILITY BANNER-->

[Amazon GameLift](https://docs.aws.amazon.com/gamelift/latest/developerguide/gamelift-intro.html) is a service used
to deploy, operate, and scale dedicated, low-cost servers in the cloud for session-based multiplayer games. Built
on AWS global computing infrastructure, GameLift helps deliver high-performance, high-reliability game servers
while dynamically scaling your resource usage to meet worldwide player demand.

GameLift is composed of three main components:

* GameLift FlexMatch which is a customizable matchmaking service for
  multiplayer games. With FlexMatch, you can
  build a custom set of rules that defines what a multiplayer match looks like
  for your game, and determines how to
  evaluate and select compatible players for each match. You can also customize
  key aspects of the matchmaking
  process to fit your game, including fine-tuning the matching algorithm.
* GameLift hosting for custom or realtime servers which helps you deploy,
  operate, and scale dedicated game servers. It regulates the resources needed to
  host games, finds available game servers to host new game sessions, and puts
  players into games.
* GameLift FleetIQ to optimize the use of low-cost Amazon Elastic Compute Cloud
  (Amazon EC2) Spot Instances for cloud-based game hosting. With GameLift
  FleetIQ, you can work directly with your hosting resources in Amazon EC2 and
  Amazon EC2 Auto Scaling while taking advantage of GameLift optimizations to
  deliver inexpensive, resilient game hosting for your players

This module is part of the [AWS Cloud Development Kit](https://github.com/aws/aws-cdk) project. It allows you to define components for your matchmaking
configuration or game server fleet management system.

## GameLift FlexMatch

### Defining a Matchmaking configuration

FlexMatch is available both as a GameLift game hosting solution (including
Realtime Servers) and as a standalone matchmaking service. To set up a
FlexMatch matchmaker to process matchmaking requests, you have to create a
matchmaking configuration based on a RuleSet.

More details about matchmaking ruleSet are covered [below](#matchmaking-ruleset).

There is two types of Matchmaking configuration:

Through a game session queue system to let FlexMatch forms matches and uses the specified GameLift queue to start a game session for the match.

```python
# queue: gamelift.GameSessionQueue
# rule_set: gamelift.MatchmakingRuleSet


gamelift.QueuedMatchmakingConfiguration(self, "QueuedMatchmakingConfiguration",
    matchmaking_configuration_name="test-queued-config-name",
    game_session_queues=[queue],
    rule_set=rule_set
)
```

Or through a standalone version to let FlexMatch forms matches and returns match information in an event.

```python
# rule_set: gamelift.MatchmakingRuleSet


gamelift.StandaloneMatchmakingConfiguration(self, "StandaloneMatchmaking",
    matchmaking_configuration_name="test-standalone-config-name",
    rule_set=rule_set
)
```

More details about Game session queue are covered [below](#game-session-queue).

### Matchmaking RuleSet

Every FlexMatch matchmaker must have a rule set. The rule set determines the
two key elements of a match: your game's team structure and size, and how to
group players together for the best possible match.

For example, a rule set might describe a match like this: Create a match with
two teams of four to eight players each, one team is the cowboy and the other
team the aliens. A team can have novice and experienced players, but the
average skill of the two teams must be within 10 points of each other. If no
match is made after 30 seconds, gradually relax the skill requirements.

```python
gamelift.MatchmakingRuleSet(self, "RuleSet",
    matchmaking_rule_set_name="my-test-ruleset",
    content=gamelift.RuleSetContent.from_json_file(path.join(__dirname, "my-ruleset", "ruleset.json"))
)
```

### FlexMatch Monitoring

You can monitor GameLift FlexMatch activity for matchmaking configurations and
matchmaking rules using Amazon CloudWatch. These statistics are used to provide
a historical perspective on how your Gamelift FlexMatch solution is performing.

#### FlexMatch Metrics

GameLift FlexMatch sends metrics to CloudWatch so that you can collect and
analyze the activity of your matchmaking solution, including match acceptance
workflow, ticket consumtion.

You can then use CloudWatch alarms to alert you, for example, when matches has
been rejected (potential matches that were rejected by at least one player
since the last report) exceed a certain thresold which could means that you may
have an issue in your matchmaking rules.

CDK provides methods for accessing GameLift FlexMatch metrics with default configuration,
such as `metricRuleEvaluationsPassed`, or `metricRuleEvaluationsFailed` (see
[`IMatchmakingRuleSet`](https://docs.aws.amazon.com/cdk/api/latest/docs/@aws-cdk_aws-gamelift.IMatchmakingRuleSet.html)
for a full list). CDK also provides a generic `metric` method that can be used
to produce metric configurations for any metric provided by GameLift FlexMatch;
the configurations are pre-populated with the correct dimensions for the
matchmaking configuration.

```python
# matchmaking_rule_set: gamelift.MatchmakingRuleSet

# Alarm that triggers when the per-second average of not placed matches exceed 10%
rule_evaluation_ratio = cloudwatch.MathExpression(
    expression="1 - (ruleEvaluationsPassed / ruleEvaluationsFailed)",
    using_metrics={
        "rule_evaluations_passed": matchmaking_rule_set.metric_rule_evaluations_passed(statistic=cloudwatch.Statistic.SUM),
        "rule_evaluations_failed": matchmaking_rule_set.metric("ruleEvaluationsFailed")
    }
)
cloudwatch.Alarm(self, "Alarm",
    metric=rule_evaluation_ratio,
    threshold=0.1,
    evaluation_periods=3
)
```

See: [Monitoring Using CloudWatch Metrics](https://docs.aws.amazon.com/gamelift/latest/developerguide/monitoring-cloudwatch.html)
in the *Amazon GameLift Developer Guide*.

## GameLift Hosting

### Uploading builds and scripts to GameLift

Before deploying your GameLift-enabled multiplayer game servers for hosting with the GameLift service, you need to upload
your game server files. This section provides guidance on preparing and uploading custom game server build
files or Realtime Servers server script files. When you upload files, you create a GameLift build or script resource, which
you then deploy on fleets of hosting resources.

To troubleshoot fleet activation problems related to the server script, see [Debug GameLift fleet issues](https://docs.aws.amazon.com/gamelift/latest/developerguide/fleets-creating-debug.html).

#### Upload a custom server build to GameLift

Before uploading your configured game server to GameLift for hosting, package the game build files into a build directory.
This directory must include all components required to run your game servers and host game sessions, including the following:

* Game server binaries – The binary files required to run the game server. A build can include binaries for multiple game
  servers built to run on the same platform. For a list of supported platforms, see [Download Amazon GameLift SDKs](https://docs.aws.amazon.com/gamelift/latest/developerguide/gamelift-supported.html).
* Dependencies – Any dependent files that your game server executables require to run. Examples include assets, configuration
  files, and dependent libraries.
* Install script – A script file to handle tasks that are required to fully install your game build on GameLift hosting
  servers. Place this file at the root of the build directory. GameLift runs the install script as part of fleet creation.

You can set up any application in your build, including your install script, to access your resources securely on other AWS
services.

```python
# bucket: s3.Bucket

build = gamelift.Build(self, "Build",
    content=gamelift.Content.from_bucket(bucket, "sample-asset-key")
)

CfnOutput(self, "BuildArn", value=build.build_arn)
CfnOutput(self, "BuildId", value=build.build_id)
```

To specify a server SDK version you used when integrating your game server build with Amazon GameLift use the `serverSdkVersion` parameter:

> See [Integrate games with custom game servers](https://docs.aws.amazon.com/gamelift/latest/developerguide/integration-custom-intro.html) for more details.

```python
# bucket: s3.Bucket

build = gamelift.Build(self, "Build",
    content=gamelift.Content.from_bucket(bucket, "sample-asset-key"),
    server_sdk_version="5.0.0"
)
```

#### Upload a realtime server Script

Your server script can include one or more files combined into a single .zip file for uploading. The .zip file must contain
all files that your script needs to run.

You can store your zipped script files in either a local file directory or in an Amazon Simple Storage Service (Amazon S3)
bucket or defines a directory asset which is archived as a .zip file and uploaded to S3 during deployment.

After you create the script resource, GameLift deploys the script with a new Realtime Servers fleet. GameLift installs your
server script onto each instance in the fleet, placing the script files in `/local/game`.

```python
# bucket: s3.Bucket

gamelift.Script(self, "Script",
    content=gamelift.Content.from_bucket(bucket, "sample-asset-key")
)
```

### Defining a GameLift Fleet

#### Creating a custom game server fleet

Your uploaded game servers are hosted on GameLift virtual computing resources,
called instances. You set up your hosting resources by creating a fleet of
instances and deploying them to run your game servers. You can design a fleet
to fit your game's needs.

```python
gamelift.BuildFleet(self, "Game server fleet",
    fleet_name="test-fleet",
    content=gamelift.Build.from_asset(self, "Build", path.join(__dirname, "CustomerGameServer")),
    instance_type=ec2.InstanceType.of(ec2.InstanceClass.C4, ec2.InstanceSize.LARGE),
    runtime_configuration=gamelift.RuntimeConfiguration(
        server_processes=[gamelift.ServerProcess(
            launch_path="test-launch-path"
        )]
    )
)
```

### Managing game servers launch configuration

GameLift uses a fleet's runtime configuration to determine the type and number
of processes to run on each instance in the fleet. At a minimum, a runtime
configuration contains one server process configuration that represents one
game server executable. You can also define additional server process
configurations to run other types of processes related to your game. Each
server process configuration contains the following information:

* The file name and path of an executable in your game build.
* Optionally Parameters to pass to the process on launch.
* The number of processes to run concurrently.

A GameLift instance is limited to 50 processes running concurrently.

```python
# build: gamelift.Build

# Server processes can be delcared in a declarative way through the constructor
fleet = gamelift.BuildFleet(self, "Game server fleet",
    fleet_name="test-fleet",
    content=build,
    instance_type=ec2.InstanceType.of(ec2.InstanceClass.C4, ec2.InstanceSize.LARGE),
    runtime_configuration=gamelift.RuntimeConfiguration(
        server_processes=[gamelift.ServerProcess(
            launch_path="/local/game/GameLiftExampleServer.x86_64",
            parameters="-logFile /local/game/logs/myserver1935.log -port 1935",
            concurrent_executions=100
        )]
    )
)
```

See [Managing how game servers are launched for hosting](https://docs.aws.amazon.com/gamelift/latest/developerguide/fleets-multiprocess.html)
in the *Amazon GameLift Developer Guide*.

### Defining an instance type

GameLift uses Amazon Elastic Compute Cloud (Amazon EC2) resources, called
instances, to deploy your game servers and host game sessions for your players.
When setting up a new fleet, you decide what type of instances your game needs
and how to run game server processes on them (using a runtime configuration). All instances in a fleet use the same type of resources and the same runtime
configuration. You can edit a fleet's runtime configuration and other fleet
properties, but the type of resources cannot be changed.

```python
# build: gamelift.Build

gamelift.BuildFleet(self, "Game server fleet",
    fleet_name="test-fleet",
    content=build,
    instance_type=ec2.InstanceType.of(ec2.InstanceClass.C5, ec2.InstanceSize.LARGE),
    runtime_configuration=gamelift.RuntimeConfiguration(
        server_processes=[gamelift.ServerProcess(
            launch_path="/local/game/GameLiftExampleServer.x86_64"
        )]
    )
)
```

### Using Spot instances

When setting up your hosting resources, you have the option of using Spot
Instances, On-Demand Instances, or a combination.

By default, fleet are using on demand capacity.

```python
# build: gamelift.Build

gamelift.BuildFleet(self, "Game server fleet",
    fleet_name="test-fleet",
    content=build,
    instance_type=ec2.InstanceType.of(ec2.InstanceClass.C4, ec2.InstanceSize.LARGE),
    runtime_configuration=gamelift.RuntimeConfiguration(
        server_processes=[gamelift.ServerProcess(
            launch_path="/local/game/GameLiftExampleServer.x86_64"
        )]
    ),
    use_spot=True
)
```

### Allowing Ingress traffic

The allowed IP address ranges and port settings that allow inbound traffic to
access game sessions on this fleet.

New game sessions are assigned an IP address/port number combination, which
must fall into the fleet's allowed ranges. Fleets with custom game builds must
have permissions explicitly set. For Realtime Servers fleets, GameLift
automatically opens two port ranges, one for TCP messaging and one for UDP.

```python
# build: gamelift.Build


fleet = gamelift.BuildFleet(self, "Game server fleet",
    fleet_name="test-fleet",
    content=build,
    instance_type=ec2.InstanceType.of(ec2.InstanceClass.C4, ec2.InstanceSize.LARGE),
    runtime_configuration=gamelift.RuntimeConfiguration(
        server_processes=[gamelift.ServerProcess(
            launch_path="/local/game/GameLiftExampleServer.x86_64"
        )]
    ),
    ingress_rules=[gamelift.IngressRule(
        source=gamelift.Peer.any_ipv4(),
        port=gamelift.Port.tcp_range(100, 200)
    )]
)
# Allowing a specific CIDR for port 1111 on UDP Protocol
fleet.add_ingress_rule(gamelift.Peer.ipv4("1.2.3.4/32"), gamelift.Port.udp(1111))
```

### Managing locations

A single Amazon GameLift fleet has a home Region by default (the Region you
deploy it to), but it can deploy resources to any number of GameLift supported
Regions. Select Regions based on where your players are located and your
latency needs.

By default, home region is used as default location but we can add new locations if needed and define desired capacity

```python
# build: gamelift.Build


# Locations can be added directly through constructor
fleet = gamelift.BuildFleet(self, "Game server fleet",
    fleet_name="test-fleet",
    content=build,
    instance_type=ec2.InstanceType.of(ec2.InstanceClass.C4, ec2.InstanceSize.LARGE),
    runtime_configuration=gamelift.RuntimeConfiguration(
        server_processes=[gamelift.ServerProcess(
            launch_path="/local/game/GameLiftExampleServer.x86_64"
        )]
    ),
    locations=[gamelift.Location(
        region="eu-west-1",
        capacity=gamelift.LocationCapacity(
            desired_capacity=5,
            min_size=2,
            max_size=10
        )
    ), gamelift.Location(
        region="us-east-1",
        capacity=gamelift.LocationCapacity(
            desired_capacity=5,
            min_size=2,
            max_size=10
        )
    )]
)

# Or through dedicated methods
fleet.add_location("ap-southeast-1", 5, 2, 10)
```

### Specifying an IAM role for a Fleet

Some GameLift features require you to extend limited access to your AWS
resources. This is done by creating an AWS IAM role. The GameLift Fleet class
automatically created an IAM role with all the minimum necessary permissions
for GameLift to access your resources. If you wish, you may
specify your own IAM role.

```python
# build: gamelift.Build

role = iam.Role(self, "Role",
    assumed_by=iam.CompositePrincipal(iam.ServicePrincipal("gamelift.amazonaws.com"))
)
role.add_managed_policy(iam.ManagedPolicy.from_aws_managed_policy_name("CloudWatchAgentServerPolicy"))

fleet = gamelift.BuildFleet(self, "Game server fleet",
    fleet_name="test-fleet",
    content=build,
    instance_type=ec2.InstanceType.of(ec2.InstanceClass.C5, ec2.InstanceSize.LARGE),
    runtime_configuration=gamelift.RuntimeConfiguration(
        server_processes=[gamelift.ServerProcess(
            launch_path="/local/game/GameLiftExampleServer.x86_64"
        )]
    ),
    role=role
)

# Actions can also be grantted through dedicated method
fleet.grant(role, "gamelift:ListFleets")
```

### Alias

A GameLift alias is used to abstract a fleet designation. Fleet designations
tell Amazon GameLift where to search for available resources when creating new
game sessions for players. By using aliases instead of specific fleet IDs, you
can more easily and seamlessly switch player traffic from one fleet to another
by changing the alias's target location.

```python
# fleet: gamelift.BuildFleet


# Add an alias to an existing fleet using a dedicated fleet method
live_alias = fleet.add_alias("live")

# You can also create a standalone alias
gamelift.Alias(self, "TerminalAlias",
    alias_name="terminal-alias",
    terminal_message="A terminal message"
)
```

See [Add an alias to a GameLift fleet](https://docs.aws.amazon.com/gamelift/latest/developerguide/aliases-creating.html)
in the *Amazon GameLift Developer Guide*.

### Monitoring your Fleet

GameLift is integrated with CloudWatch, so you can monitor the performance of
your game servers via logs and metrics.

#### Fleet Metrics

GameLift Fleet sends metrics to CloudWatch so that you can collect and analyze
the activity of your Fleet, including game  and player sessions and server
processes.

You can then use CloudWatch alarms to alert you, for example, when matches has
been rejected (potential matches that were rejected by at least one player
since the last report) exceed a certain threshold which could means that you may
have an issue in your matchmaking rules.

CDK provides methods for accessing GameLift Fleet metrics with default configuration,
such as `metricActiveInstances`, or `metricIdleInstances` (see [`IFleet`](https://docs.aws.amazon.com/cdk/api/latest/docs/@aws-cdk_aws-gamelift.IFleet.html)
for a full list). CDK also provides a generic `metric` method that can be used
to produce metric configurations for any metric provided by GameLift Fleet,
Game sessions or server processes; the configurations are pre-populated with
the correct dimensions for the matchmaking configuration.

```python
# fleet: gamelift.BuildFleet

# Alarm that triggers when the per-second average of not used instances exceed 10%
instances_used_ratio = cloudwatch.MathExpression(
    expression="1 - (activeInstances / idleInstances)",
    using_metrics={
        "active_instances": fleet.metric("ActiveInstances", statistic=cloudwatch.Statistic.SUM),
        "idle_instances": fleet.metric_idle_instances()
    }
)
cloudwatch.Alarm(self, "Alarm",
    metric=instances_used_ratio,
    threshold=0.1,
    evaluation_periods=3
)
```

See: [Monitoring Using CloudWatch Metrics](https://docs.aws.amazon.com/gamelift/latest/developerguide/monitoring-cloudwatch.html)
in the *Amazon GameLift Developer Guide*.

## Game session queue

The game session queue is the primary mechanism for processing new game session
requests and locating available game servers to host them. Although it is
possible to request a new game session be hosted on specific fleet or location.

The `GameSessionQueue` resource creates a placement queue that processes requests for
new game sessions. A queue uses FleetIQ algorithms to determine the best placement
locations and find an available game server, then prompts the game server to start a
new game session. Queues can have destinations (GameLift fleets or aliases), which
determine where the queue can place new game sessions. A queue can have destinations
with varied fleet type (Spot and On-Demand), instance type, and AWS Region.

```python
# fleet: gamelift.BuildFleet
# alias: gamelift.Alias


queue = gamelift.GameSessionQueue(self, "GameSessionQueue",
    game_session_queue_name="my-queue-name",
    destinations=[fleet]
)
queue.add_destination(alias)
```

A more complex configuration can also be definied to override how FleetIQ algorithms prioritize game session placement in order to favour a destination based on `Cost`, `Latency`, `Destination order`or `Location`.

```python
# fleet: gamelift.BuildFleet
# topic: sns.Topic


gamelift.GameSessionQueue(self, "MyGameSessionQueue",
    game_session_queue_name="test-gameSessionQueue",
    custom_event_data="test-event-data",
    allowed_locations=["eu-west-1", "eu-west-2"],
    destinations=[fleet],
    notification_target=topic,
    player_latency_policies=[gamelift.PlayerLatencyPolicy(
        maximum_individual_player_latency=Duration.millis(100),
        policy_duration=Duration.seconds(300)
    )],
    priority_configuration=gamelift.PriorityConfiguration(
        location_order=["eu-west-1", "eu-west-2"
        ],
        priority_order=[gamelift.PriorityType.LATENCY, gamelift.PriorityType.COST, gamelift.PriorityType.DESTINATION, gamelift.PriorityType.LOCATION
        ]
    ),
    timeout=Duration.seconds(300)
)
```

See [Setting up GameLift queues for game session placement](https://docs.aws.amazon.com/gamelift/latest/developerguide/realtime-script-uploading.html)
in the *Amazon GameLift Developer Guide*.

## GameLift FleetIQ

The GameLift FleetIQ solution is a game hosting layer that supplements the full
set of computing resource management tools that you get with Amazon EC2 and
Auto Scaling. This solution lets you directly manage your Amazon EC2 and Auto
Scaling resources and integrate as needed with other AWS services.

### Defining a Game Server Group

When using GameLift FleetIQ, you prepare to launch Amazon EC2 instances as
usual: make an Amazon Machine Image (AMI) with your game server software,
create an Amazon EC2 launch template, and define configuration settings for an
Auto Scaling group. However, instead of creating an Auto Scaling group
directly, you create a GameLift FleetIQ game server group with your Amazon EC2
and Auto Scaling resources and configuration. All game server groups must have
at least two instance types defined for it.

Once a game server group and Auto Scaling group are up and running with
instances deployed, when updating a Game Server Group instance, only certain
properties in the Auto Scaling group may be overwrite. For all other Auto
Scaling group properties, such as MinSize, MaxSize, and LaunchTemplate, you can
modify these directly on the Auto Scaling group using the AWS Console or
dedicated Api.

```python
# launch_template: ec2.ILaunchTemplate
# vpc: ec2.IVpc


gamelift.GameServerGroup(self, "Game server group",
    game_server_group_name="sample-gameservergroup-name",
    instance_definitions=[gamelift.InstanceDefinition(
        instance_type=ec2.InstanceType.of(ec2.InstanceClass.C5, ec2.InstanceSize.LARGE)
    ), gamelift.InstanceDefinition(
        instance_type=ec2.InstanceType.of(ec2.InstanceClass.C4, ec2.InstanceSize.LARGE)
    )],
    launch_template=launch_template,
    vpc=vpc
)
```

See [Manage game server groups](https://docs.aws.amazon.com/gamelift/latest/fleetiqguide/gsg-integrate-gameservergroup.html)
in the *Amazon GameLift FleetIQ Developer Guide*.

### Scaling Policy

The scaling policy uses the metric `PercentUtilizedGameServers` to maintain a
buffer of idle game servers that can immediately accommodate new games and
players.

```python
# launch_template: ec2.ILaunchTemplate
# vpc: ec2.IVpc


gamelift.GameServerGroup(self, "Game server group",
    game_server_group_name="sample-gameservergroup-name",
    instance_definitions=[gamelift.InstanceDefinition(
        instance_type=ec2.InstanceType.of(ec2.InstanceClass.C5, ec2.InstanceSize.LARGE)
    ), gamelift.InstanceDefinition(
        instance_type=ec2.InstanceType.of(ec2.InstanceClass.C4, ec2.InstanceSize.LARGE)
    )],
    launch_template=launch_template,
    vpc=vpc,
    auto_scaling_policy=gamelift.AutoScalingPolicy(
        estimated_instance_warmup=Duration.minutes(5),
        target_tracking_configuration=5
    )
)
```

See [Manage game server groups](https://docs.aws.amazon.com/gamelift/latest/fleetiqguide/gsg-integrate-gameservergroup.html)
in the *Amazon GameLift FleetIQ Developer Guide*.

### Specifying an IAM role for GameLift

The GameLift FleetIQ class automatically creates an IAM role with all the minimum necessary
permissions for GameLift to access your Amazon EC2 Auto Scaling groups. If you wish, you may
specify your own IAM role. It must have the correct permissions, or FleetIQ creation or resource usage may fail.

```python
# launch_template: ec2.ILaunchTemplate
# vpc: ec2.IVpc


role = iam.Role(self, "Role",
    assumed_by=iam.CompositePrincipal(iam.ServicePrincipal("gamelift.amazonaws.com"),
    iam.ServicePrincipal("autoscaling.amazonaws.com"))
)
role.add_managed_policy(iam.ManagedPolicy.from_aws_managed_policy_name("GameLiftGameServerGroupPolicy"))

gamelift.GameServerGroup(self, "Game server group",
    game_server_group_name="sample-gameservergroup-name",
    instance_definitions=[gamelift.InstanceDefinition(
        instance_type=ec2.InstanceType.of(ec2.InstanceClass.C5, ec2.InstanceSize.LARGE)
    ), gamelift.InstanceDefinition(
        instance_type=ec2.InstanceType.of(ec2.InstanceClass.C4, ec2.InstanceSize.LARGE)
    )],
    launch_template=launch_template,
    vpc=vpc,
    role=role
)
```

See [Controlling Access](https://docs.aws.amazon.com/gamelift/latest/fleetiqguide/gsg-iam-permissions-roles.html)
in the *Amazon GameLift FleetIQ Developer Guide*.

### Specifying VPC Subnets

GameLift FleetIQ use by default, all supported GameLift FleetIQ Availability
Zones in your chosen region. You can override this parameter to specify VPCs
subnets that you've set up.

This property cannot be updated after the game server group is created, and the
corresponding Auto Scaling group will always use the property value that is set
with this request, even if the Auto Scaling group is updated directly.

```python
# launch_template: ec2.ILaunchTemplate
# vpc: ec2.IVpc


gamelift.GameServerGroup(self, "GameServerGroup",
    game_server_group_name="sample-gameservergroup-name",
    instance_definitions=[gamelift.InstanceDefinition(
        instance_type=ec2.InstanceType.of(ec2.InstanceClass.C5, ec2.InstanceSize.LARGE)
    ), gamelift.InstanceDefinition(
        instance_type=ec2.InstanceType.of(ec2.InstanceClass.C4, ec2.InstanceSize.LARGE)
    )],
    launch_template=launch_template,
    vpc=vpc,
    vpc_subnets=ec2.SubnetSelection(subnet_type=ec2.SubnetType.PUBLIC)
)
```

### FleetIQ Monitoring

GameLift FleetIQ sends metrics to CloudWatch so that you can collect and
analyze the activity of your Game server fleet, including the number of
utilized game servers, and the number of game server interruption due to
limited Spot availability.

You can then use CloudWatch alarms to alert you, for example, when the portion
of game servers that are currently supporting game executions exceed a certain
threshold which could means that your autoscaling policy need to be adjust to
add more instances to match with player demand.

CDK provides a generic `metric` method that can be used
to produce metric configurations for any metric provided by GameLift FleetIQ;
the configurations are pre-populated with the correct dimensions for the
matchmaking configuration.

```python
# game_server_group: gamelift.IGameServerGroup

# Alarm that triggers when the percent of utilized game servers exceed 90%
cloudwatch.Alarm(self, "Alarm",
    metric=game_server_group.metric("UtilizedGameServers"),
    threshold=0.9,
    evaluation_periods=2
)
```

See: [Monitoring with CloudWatch](https://docs.aws.amazon.com/gamelift/latest/fleetiqguide/gsg-metrics.html)
in the *Amazon GameLift FleetIQ Developer Guide*.
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
import aws_cdk.aws_cloudwatch as _aws_cdk_aws_cloudwatch_ceddda9d
import aws_cdk.aws_ec2 as _aws_cdk_aws_ec2_ceddda9d
import aws_cdk.aws_gamelift as _aws_cdk_aws_gamelift_ceddda9d
import aws_cdk.aws_iam as _aws_cdk_aws_iam_ceddda9d
import aws_cdk.aws_kms as _aws_cdk_aws_kms_ceddda9d
import aws_cdk.aws_s3 as _aws_cdk_aws_s3_ceddda9d
import aws_cdk.aws_s3_assets as _aws_cdk_aws_s3_assets_ceddda9d
import aws_cdk.aws_sns as _aws_cdk_aws_sns_ceddda9d
import constructs as _constructs_77d1e7e8


@jsii.data_type(
    jsii_type="@aws-cdk/aws-gamelift-alpha.AliasAttributes",
    jsii_struct_bases=[],
    name_mapping={"alias_arn": "aliasArn", "alias_id": "aliasId"},
)
class AliasAttributes:
    def __init__(
        self,
        *,
        alias_arn: typing.Optional[builtins.str] = None,
        alias_id: typing.Optional[builtins.str] = None,
    ) -> None:
        '''(experimental) A full specification of an alias that can be used to import it fluently into the CDK application.

        :param alias_arn: (experimental) The ARN of the alias. At least one of ``aliasArn`` and ``aliasId`` must be provided. Default: derived from ``aliasId``.
        :param alias_id: (experimental) The identifier of the alias. At least one of ``aliasId`` and ``aliasArn`` must be provided. Default: derived from ``aliasArn``.

        :stability: experimental
        :exampleMetadata: fixture=_generated

        Example::

            # The code below shows an example of how to instantiate this type.
            # The values are placeholders you should change.
            import aws_cdk.aws_gamelift_alpha as gamelift_alpha
            
            alias_attributes = gamelift_alpha.AliasAttributes(
                alias_arn="aliasArn",
                alias_id="aliasId"
            )
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__04279523a0cc50838f54aa501c7a3727907d986b95b950c0f5c999e3feebe6be)
            check_type(argname="argument alias_arn", value=alias_arn, expected_type=type_hints["alias_arn"])
            check_type(argname="argument alias_id", value=alias_id, expected_type=type_hints["alias_id"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if alias_arn is not None:
            self._values["alias_arn"] = alias_arn
        if alias_id is not None:
            self._values["alias_id"] = alias_id

    @builtins.property
    def alias_arn(self) -> typing.Optional[builtins.str]:
        '''(experimental) The ARN of the alias.

        At least one of ``aliasArn`` and ``aliasId`` must be provided.

        :default: derived from ``aliasId``.

        :stability: experimental
        '''
        result = self._values.get("alias_arn")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def alias_id(self) -> typing.Optional[builtins.str]:
        '''(experimental) The identifier of the alias.

        At least one of ``aliasId`` and ``aliasArn``  must be provided.

        :default: derived from ``aliasArn``.

        :stability: experimental
        '''
        result = self._values.get("alias_id")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "AliasAttributes(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@aws-cdk/aws-gamelift-alpha.AliasOptions",
    jsii_struct_bases=[],
    name_mapping={"description": "description"},
)
class AliasOptions:
    def __init__(self, *, description: typing.Optional[builtins.str] = None) -> None:
        '''(experimental) Options for ``gamelift.Alias``.

        :param description: (experimental) Description for the alias. Default: No description

        :stability: experimental
        :exampleMetadata: fixture=_generated

        Example::

            # The code below shows an example of how to instantiate this type.
            # The values are placeholders you should change.
            import aws_cdk.aws_gamelift_alpha as gamelift_alpha
            
            alias_options = gamelift_alpha.AliasOptions(
                description="description"
            )
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2287dbf19acdb26798b6177f68979aba4e2d99cac4684391d3b94f547845d855)
            check_type(argname="argument description", value=description, expected_type=type_hints["description"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if description is not None:
            self._values["description"] = description

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        '''(experimental) Description for the alias.

        :default: No description

        :stability: experimental
        '''
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "AliasOptions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@aws-cdk/aws-gamelift-alpha.AliasProps",
    jsii_struct_bases=[],
    name_mapping={
        "alias_name": "aliasName",
        "description": "description",
        "fleet": "fleet",
        "terminal_message": "terminalMessage",
    },
)
class AliasProps:
    def __init__(
        self,
        *,
        alias_name: builtins.str,
        description: typing.Optional[builtins.str] = None,
        fleet: typing.Optional["IFleet"] = None,
        terminal_message: typing.Optional[builtins.str] = None,
    ) -> None:
        '''(experimental) Properties for a new Fleet alias.

        :param alias_name: (experimental) Name of this alias.
        :param description: (experimental) A human-readable description of the alias. Default: no description
        :param fleet: (experimental) A fleet that the alias points to. If specified, the alias resolves to one specific fleet. At least one of ``fleet`` and ``terminalMessage`` must be provided. Default: no fleet that the alias points to.
        :param terminal_message: (experimental) The message text to be used with a terminal routing strategy. At least one of ``fleet`` and ``terminalMessage`` must be provided. Default: no terminal message

        :stability: experimental
        :exampleMetadata: infused

        Example::

            # fleet: gamelift.BuildFleet
            
            
            # Add an alias to an existing fleet using a dedicated fleet method
            live_alias = fleet.add_alias("live")
            
            # You can also create a standalone alias
            gamelift.Alias(self, "TerminalAlias",
                alias_name="terminal-alias",
                terminal_message="A terminal message"
            )
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e7632247cd09762e30337d9fcf6bc1dbf7d405ef72c3e8f1f9195436c713ecc0)
            check_type(argname="argument alias_name", value=alias_name, expected_type=type_hints["alias_name"])
            check_type(argname="argument description", value=description, expected_type=type_hints["description"])
            check_type(argname="argument fleet", value=fleet, expected_type=type_hints["fleet"])
            check_type(argname="argument terminal_message", value=terminal_message, expected_type=type_hints["terminal_message"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "alias_name": alias_name,
        }
        if description is not None:
            self._values["description"] = description
        if fleet is not None:
            self._values["fleet"] = fleet
        if terminal_message is not None:
            self._values["terminal_message"] = terminal_message

    @builtins.property
    def alias_name(self) -> builtins.str:
        '''(experimental) Name of this alias.

        :stability: experimental
        '''
        result = self._values.get("alias_name")
        assert result is not None, "Required property 'alias_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        '''(experimental) A human-readable description of the alias.

        :default: no description

        :stability: experimental
        '''
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def fleet(self) -> typing.Optional["IFleet"]:
        '''(experimental) A fleet that the alias points to. If specified, the alias resolves to one specific fleet.

        At least one of ``fleet`` and ``terminalMessage`` must be provided.

        :default: no fleet that the alias points to.

        :stability: experimental
        '''
        result = self._values.get("fleet")
        return typing.cast(typing.Optional["IFleet"], result)

    @builtins.property
    def terminal_message(self) -> typing.Optional[builtins.str]:
        '''(experimental) The message text to be used with a terminal routing strategy.

        At least one of ``fleet`` and ``terminalMessage`` must be provided.

        :default: no terminal message

        :stability: experimental
        '''
        result = self._values.get("terminal_message")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "AliasProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@aws-cdk/aws-gamelift-alpha.AutoScalingPolicy",
    jsii_struct_bases=[],
    name_mapping={
        "target_tracking_configuration": "targetTrackingConfiguration",
        "estimated_instance_warmup": "estimatedInstanceWarmup",
    },
)
class AutoScalingPolicy:
    def __init__(
        self,
        *,
        target_tracking_configuration: jsii.Number,
        estimated_instance_warmup: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
    ) -> None:
        '''(experimental) Configuration settings for intelligent automatic scaling that uses target tracking.

        After the Auto Scaling group is created, all updates to Auto Scaling policies, including changing this policy and adding or removing other policies, is done directly on the Auto Scaling group.

        :param target_tracking_configuration: (experimental) Settings for a target-based scaling policy applied to Auto Scaling group. These settings are used to create a target-based policy that tracks the GameLift FleetIQ metric ``PercentUtilizedGameServers`` and specifies a target value for the metric. As player usage changes, the policy triggers to adjust the game server group capacity so that the metric returns to the target value.
        :param estimated_instance_warmup: (experimental) Length of time, it takes for a new instance to start new game server processes and register with GameLift FleetIQ. Specifying a warm-up time can be useful, particularly with game servers that take a long time to start up, because it avoids prematurely starting new instances. Default: no instance warmup duration settled

        :stability: experimental
        :exampleMetadata: infused

        Example::

            # launch_template: ec2.ILaunchTemplate
            # vpc: ec2.IVpc
            
            
            gamelift.GameServerGroup(self, "Game server group",
                game_server_group_name="sample-gameservergroup-name",
                instance_definitions=[gamelift.InstanceDefinition(
                    instance_type=ec2.InstanceType.of(ec2.InstanceClass.C5, ec2.InstanceSize.LARGE)
                ), gamelift.InstanceDefinition(
                    instance_type=ec2.InstanceType.of(ec2.InstanceClass.C4, ec2.InstanceSize.LARGE)
                )],
                launch_template=launch_template,
                vpc=vpc,
                auto_scaling_policy=gamelift.AutoScalingPolicy(
                    estimated_instance_warmup=Duration.minutes(5),
                    target_tracking_configuration=5
                )
            )
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0177fa2ab17f9865574fd09ad3d1f990ef0d7423199d06387b69eb189ae89e7e)
            check_type(argname="argument target_tracking_configuration", value=target_tracking_configuration, expected_type=type_hints["target_tracking_configuration"])
            check_type(argname="argument estimated_instance_warmup", value=estimated_instance_warmup, expected_type=type_hints["estimated_instance_warmup"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "target_tracking_configuration": target_tracking_configuration,
        }
        if estimated_instance_warmup is not None:
            self._values["estimated_instance_warmup"] = estimated_instance_warmup

    @builtins.property
    def target_tracking_configuration(self) -> jsii.Number:
        '''(experimental) Settings for a target-based scaling policy applied to Auto Scaling group.

        These settings are used to create a target-based policy that tracks the GameLift FleetIQ metric ``PercentUtilizedGameServers`` and specifies a target value for the metric.

        As player usage changes, the policy triggers to adjust the game server group capacity so that the metric returns to the target value.

        :stability: experimental
        '''
        result = self._values.get("target_tracking_configuration")
        assert result is not None, "Required property 'target_tracking_configuration' is missing"
        return typing.cast(jsii.Number, result)

    @builtins.property
    def estimated_instance_warmup(self) -> typing.Optional[_aws_cdk_ceddda9d.Duration]:
        '''(experimental) Length of time, it takes for a new instance to start new game server processes and register with GameLift FleetIQ.

        Specifying a warm-up time can be useful, particularly with game servers that take a long time to start up, because it avoids prematurely starting new instances.

        :default: no instance warmup duration settled

        :stability: experimental
        '''
        result = self._values.get("estimated_instance_warmup")
        return typing.cast(typing.Optional[_aws_cdk_ceddda9d.Duration], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "AutoScalingPolicy(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.enum(jsii_type="@aws-cdk/aws-gamelift-alpha.BalancingStrategy")
class BalancingStrategy(enum.Enum):
    '''(experimental) Indicates how GameLift FleetIQ balances the use of Spot Instances and On-Demand Instances in the game server group.

    :stability: experimental
    '''

    SPOT_ONLY = "SPOT_ONLY"
    '''(experimental) Only Spot Instances are used in the game server group.

    If Spot Instances are unavailable or not viable for game hosting, the game server group provides no hosting capacity until Spot Instances can again be used.
    Until then, no new instances are started, and the existing nonviable Spot Instances are terminated (after current gameplay ends) and are not replaced.

    :stability: experimental
    '''
    SPOT_PREFERRED = "SPOT_PREFERRED"
    '''(experimental) Spot Instances are used whenever available in the game server group.

    If Spot Instances are unavailable, the game server group continues to provide hosting capacity by falling back to On-Demand Instances.
    Existing nonviable Spot Instances are terminated (after current gameplay ends) and are replaced with new On-Demand Instances.

    :stability: experimental
    '''
    ON_DEMAND_ONLY = "ON_DEMAND_ONLY"
    '''(experimental) Only On-Demand Instances are used in the game server group.

    No Spot Instances are used, even when available, while this balancing strategy is in force.

    :stability: experimental
    '''


@jsii.data_type(
    jsii_type="@aws-cdk/aws-gamelift-alpha.BuildAttributes",
    jsii_struct_bases=[],
    name_mapping={"build_arn": "buildArn", "build_id": "buildId", "role": "role"},
)
class BuildAttributes:
    def __init__(
        self,
        *,
        build_arn: typing.Optional[builtins.str] = None,
        build_id: typing.Optional[builtins.str] = None,
        role: typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole] = None,
    ) -> None:
        '''(experimental) Represents a Build content defined outside of this stack.

        :param build_arn: (experimental) The ARN of the build. At least one of ``buildArn`` and ``buildId`` must be provided. Default: derived from ``buildId``.
        :param build_id: (experimental) The identifier of the build. At least one of ``buildId`` and ``buildArn`` must be provided. Default: derived from ``buildArn``.
        :param role: (experimental) The IAM role assumed by GameLift to access server build in S3. Default: the imported fleet cannot be granted access to other resources as an ``iam.IGrantable``.

        :stability: experimental
        :exampleMetadata: fixture=_generated

        Example::

            # The code below shows an example of how to instantiate this type.
            # The values are placeholders you should change.
            import aws_cdk.aws_gamelift_alpha as gamelift_alpha
            from aws_cdk import aws_iam as iam
            
            # role: iam.Role
            
            build_attributes = gamelift_alpha.BuildAttributes(
                build_arn="buildArn",
                build_id="buildId",
                role=role
            )
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__eeffd58e73fe7a51fe98048a49a3129ed94d23f43d5263361781c6e0b0b71d7b)
            check_type(argname="argument build_arn", value=build_arn, expected_type=type_hints["build_arn"])
            check_type(argname="argument build_id", value=build_id, expected_type=type_hints["build_id"])
            check_type(argname="argument role", value=role, expected_type=type_hints["role"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if build_arn is not None:
            self._values["build_arn"] = build_arn
        if build_id is not None:
            self._values["build_id"] = build_id
        if role is not None:
            self._values["role"] = role

    @builtins.property
    def build_arn(self) -> typing.Optional[builtins.str]:
        '''(experimental) The ARN of the build.

        At least one of ``buildArn`` and ``buildId`` must be provided.

        :default: derived from ``buildId``.

        :stability: experimental
        '''
        result = self._values.get("build_arn")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def build_id(self) -> typing.Optional[builtins.str]:
        '''(experimental) The identifier of the build.

        At least one of ``buildId`` and ``buildArn``  must be provided.

        :default: derived from ``buildArn``.

        :stability: experimental
        '''
        result = self._values.get("build_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def role(self) -> typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole]:
        '''(experimental) The IAM role assumed by GameLift to access server build in S3.

        :default: the imported fleet cannot be granted access to other resources as an ``iam.IGrantable``.

        :stability: experimental
        '''
        result = self._values.get("role")
        return typing.cast(typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "BuildAttributes(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@aws-cdk/aws-gamelift-alpha.BuildProps",
    jsii_struct_bases=[],
    name_mapping={
        "content": "content",
        "build_name": "buildName",
        "build_version": "buildVersion",
        "operating_system": "operatingSystem",
        "role": "role",
        "server_sdk_version": "serverSdkVersion",
    },
)
class BuildProps:
    def __init__(
        self,
        *,
        content: "Content",
        build_name: typing.Optional[builtins.str] = None,
        build_version: typing.Optional[builtins.str] = None,
        operating_system: typing.Optional["OperatingSystem"] = None,
        role: typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole] = None,
        server_sdk_version: typing.Optional[builtins.str] = None,
    ) -> None:
        '''(experimental) Properties for a new build.

        :param content: (experimental) The game build file storage.
        :param build_name: (experimental) Name of this build. Default: No name
        :param build_version: (experimental) Version of this build. Default: No version
        :param operating_system: (experimental) The operating system that the game server binaries are built to run on. Default: No version
        :param role: (experimental) The IAM role assumed by GameLift to access server build in S3. If providing a custom role, it needs to trust the GameLift service principal (gamelift.amazonaws.com) and be granted sufficient permissions to have Read access to a specific key content into a specific S3 bucket. Below an example of required permission: { "Version": "2012-10-17", "Statement": [{ "Effect": "Allow", "Action": [ "s3:GetObject", "s3:GetObjectVersion" ], "Resource": "arn:aws:s3:::bucket-name/object-name" }] } Default: - a role will be created with default permissions.
        :param server_sdk_version: (experimental) A server SDK version you used when integrating your game server build with Amazon GameLift. Default: - 4.0.2

        :stability: experimental
        :exampleMetadata: infused

        Example::

            # bucket: s3.Bucket
            
            build = gamelift.Build(self, "Build",
                content=gamelift.Content.from_bucket(bucket, "sample-asset-key")
            )
            
            CfnOutput(self, "BuildArn", value=build.build_arn)
            CfnOutput(self, "BuildId", value=build.build_id)
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4f4a75ef0e23a8dbf4114398dbe9a7b2d5f6435cf277ff83bdd799761bf35919)
            check_type(argname="argument content", value=content, expected_type=type_hints["content"])
            check_type(argname="argument build_name", value=build_name, expected_type=type_hints["build_name"])
            check_type(argname="argument build_version", value=build_version, expected_type=type_hints["build_version"])
            check_type(argname="argument operating_system", value=operating_system, expected_type=type_hints["operating_system"])
            check_type(argname="argument role", value=role, expected_type=type_hints["role"])
            check_type(argname="argument server_sdk_version", value=server_sdk_version, expected_type=type_hints["server_sdk_version"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "content": content,
        }
        if build_name is not None:
            self._values["build_name"] = build_name
        if build_version is not None:
            self._values["build_version"] = build_version
        if operating_system is not None:
            self._values["operating_system"] = operating_system
        if role is not None:
            self._values["role"] = role
        if server_sdk_version is not None:
            self._values["server_sdk_version"] = server_sdk_version

    @builtins.property
    def content(self) -> "Content":
        '''(experimental) The game build file storage.

        :stability: experimental
        '''
        result = self._values.get("content")
        assert result is not None, "Required property 'content' is missing"
        return typing.cast("Content", result)

    @builtins.property
    def build_name(self) -> typing.Optional[builtins.str]:
        '''(experimental) Name of this build.

        :default: No name

        :stability: experimental
        '''
        result = self._values.get("build_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def build_version(self) -> typing.Optional[builtins.str]:
        '''(experimental) Version of this build.

        :default: No version

        :stability: experimental
        '''
        result = self._values.get("build_version")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def operating_system(self) -> typing.Optional["OperatingSystem"]:
        '''(experimental) The operating system that the game server binaries are built to run on.

        :default: No version

        :stability: experimental
        '''
        result = self._values.get("operating_system")
        return typing.cast(typing.Optional["OperatingSystem"], result)

    @builtins.property
    def role(self) -> typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole]:
        '''(experimental) The IAM role assumed by GameLift to access server build in S3.

        If providing a custom role, it needs to trust the GameLift service principal (gamelift.amazonaws.com) and be granted sufficient permissions
        to have Read access to a specific key content into a specific S3 bucket.
        Below an example of required permission:
        {
        "Version": "2012-10-17",
        "Statement": [{
        "Effect": "Allow",
        "Action": [
        "s3:GetObject",
        "s3:GetObjectVersion"
        ],
        "Resource": "arn:aws:s3:::bucket-name/object-name"
        }]
        }

        :default: - a role will be created with default permissions.

        :see: https://docs.aws.amazon.com/gamelift/latest/developerguide/security_iam_id-based-policy-examples.html#security_iam_id-based-policy-examples-access-storage-loc
        :stability: experimental
        '''
        result = self._values.get("role")
        return typing.cast(typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole], result)

    @builtins.property
    def server_sdk_version(self) -> typing.Optional[builtins.str]:
        '''(experimental) A server SDK version you used when integrating your game server build with Amazon GameLift.

        :default: - 4.0.2

        :see: https://docs.aws.amazon.com/gamelift/latest/developerguide/integration-custom-intro.html
        :stability: experimental
        '''
        result = self._values.get("server_sdk_version")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "BuildProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class Content(
    metaclass=jsii.JSIIAbstractClass,
    jsii_type="@aws-cdk/aws-gamelift-alpha.Content",
):
    '''(experimental) Before deploying your GameLift-enabled multiplayer game servers for hosting with the GameLift service, you need to upload your game server files.

    The class helps you on preparing and uploading custom game server build files or Realtime Servers server script files.

    :stability: experimental
    :exampleMetadata: infused

    Example::

        # bucket: s3.Bucket
        
        build = gamelift.Build(self, "Build",
            content=gamelift.Content.from_bucket(bucket, "sample-asset-key"),
            server_sdk_version="5.0.0"
        )
    '''

    def __init__(self) -> None:
        '''
        :stability: experimental
        '''
        jsii.create(self.__class__, self, [])

    @jsii.member(jsii_name="fromAsset")
    @builtins.classmethod
    def from_asset(
        cls,
        path: builtins.str,
        *,
        deploy_time: typing.Optional[builtins.bool] = None,
        display_name: typing.Optional[builtins.str] = None,
        readers: typing.Optional[typing.Sequence[_aws_cdk_aws_iam_ceddda9d.IGrantable]] = None,
        source_kms_key: typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey] = None,
        asset_hash: typing.Optional[builtins.str] = None,
        asset_hash_type: typing.Optional[_aws_cdk_ceddda9d.AssetHashType] = None,
        bundling: typing.Optional[typing.Union[_aws_cdk_ceddda9d.BundlingOptions, typing.Dict[builtins.str, typing.Any]]] = None,
        exclude: typing.Optional[typing.Sequence[builtins.str]] = None,
        follow_symlinks: typing.Optional[_aws_cdk_ceddda9d.SymlinkFollowMode] = None,
        ignore_mode: typing.Optional[_aws_cdk_ceddda9d.IgnoreMode] = None,
    ) -> "AssetContent":
        '''(experimental) Loads the game content from a local disk path.

        :param path: Either a directory with the game content bundle or a .zip file.
        :param deploy_time: Whether or not the asset needs to exist beyond deployment time; i.e. are copied over to a different location and not needed afterwards. Setting this property to true has an impact on the lifecycle of the asset, because we will assume that it is safe to delete after the CloudFormation deployment succeeds. For example, Lambda Function assets are copied over to Lambda during deployment. Therefore, it is not necessary to store the asset in S3, so we consider those deployTime assets. Default: false
        :param display_name: A display name for this asset. If supplied, the display name will be used in locations where the asset identifier is printed, like in the CLI progress information. If the same asset is added multiple times, the display name of the first occurrence is used. The default is the construct path of the Asset construct, with respect to the enclosing stack. If the asset is produced by a construct helper function (such as ``lambda.Code.fromAsset()``), this will look like ``MyFunction/Code``. We use the stack-relative construct path so that in the common case where you have multiple stacks with the same asset, we won't show something like ``/MyBetaStack/MyFunction/Code`` when you are actually deploying to production. Default: - Stack-relative construct path
        :param readers: A list of principals that should be able to read this asset from S3. You can use ``asset.grantRead(principal)`` to grant read permissions later. Default: - No principals that can read file asset.
        :param source_kms_key: The ARN of the KMS key used to encrypt the handler code. Default: - the default server-side encryption with Amazon S3 managed keys(SSE-S3) key will be used.
        :param asset_hash: Specify a custom hash for this asset. If ``assetHashType`` is set it must be set to ``AssetHashType.CUSTOM``. For consistency, this custom hash will be SHA256 hashed and encoded as hex. The resulting hash will be the asset hash. NOTE: the hash is used in order to identify a specific revision of the asset, and used for optimizing and caching deployment activities related to this asset such as packaging, uploading to Amazon S3, etc. If you chose to customize the hash, you will need to make sure it is updated every time the asset changes, or otherwise it is possible that some deployments will not be invalidated. Default: - based on ``assetHashType``
        :param asset_hash_type: Specifies the type of hash to calculate for this asset. If ``assetHash`` is configured, this option must be ``undefined`` or ``AssetHashType.CUSTOM``. Default: - the default is ``AssetHashType.SOURCE``, but if ``assetHash`` is explicitly specified this value defaults to ``AssetHashType.CUSTOM``.
        :param bundling: Bundle the asset by executing a command in a Docker container or a custom bundling provider. The asset path will be mounted at ``/asset-input``. The Docker container is responsible for putting content at ``/asset-output``. The content at ``/asset-output`` will be zipped and used as the final asset. Default: - uploaded as-is to S3 if the asset is a regular file or a .zip file, archived into a .zip file and uploaded to S3 otherwise
        :param exclude: File paths matching the patterns will be excluded. See ``ignoreMode`` to set the matching behavior. Has no effect on Assets bundled using the ``bundling`` property. Default: - nothing is excluded
        :param follow_symlinks: A strategy for how to handle symlinks. Default: SymlinkFollowMode.NEVER
        :param ignore_mode: The ignore behavior to use for ``exclude`` patterns. Default: IgnoreMode.GLOB

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__56f24a9c36c82910107482c5b3fd186832948b0896de7f43b6d0cfc0065ea27e)
            check_type(argname="argument path", value=path, expected_type=type_hints["path"])
        options = _aws_cdk_aws_s3_assets_ceddda9d.AssetOptions(
            deploy_time=deploy_time,
            display_name=display_name,
            readers=readers,
            source_kms_key=source_kms_key,
            asset_hash=asset_hash,
            asset_hash_type=asset_hash_type,
            bundling=bundling,
            exclude=exclude,
            follow_symlinks=follow_symlinks,
            ignore_mode=ignore_mode,
        )

        return typing.cast("AssetContent", jsii.sinvoke(cls, "fromAsset", [path, options]))

    @jsii.member(jsii_name="fromBucket")
    @builtins.classmethod
    def from_bucket(
        cls,
        bucket: _aws_cdk_aws_s3_ceddda9d.IBucket,
        key: builtins.str,
        object_version: typing.Optional[builtins.str] = None,
    ) -> "S3Content":
        '''(experimental) Game content as an S3 object.

        :param bucket: The S3 bucket.
        :param key: The object key.
        :param object_version: Optional S3 ob ject version.

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e4efd80abc10f6730064317b68ae3759c6140bb0ed64b2bcb4fe1f331b2675c8)
            check_type(argname="argument bucket", value=bucket, expected_type=type_hints["bucket"])
            check_type(argname="argument key", value=key, expected_type=type_hints["key"])
            check_type(argname="argument object_version", value=object_version, expected_type=type_hints["object_version"])
        return typing.cast("S3Content", jsii.sinvoke(cls, "fromBucket", [bucket, key, object_version]))

    @jsii.member(jsii_name="bind")
    @abc.abstractmethod
    def bind(
        self,
        scope: _constructs_77d1e7e8.Construct,
        role: _aws_cdk_aws_iam_ceddda9d.IRole,
    ) -> "ContentConfig":
        '''(experimental) Called when the Build is initialized to allow this object to bind.

        :param scope: -
        :param role: -

        :stability: experimental
        '''
        ...


class _ContentProxy(Content):
    @jsii.member(jsii_name="bind")
    def bind(
        self,
        scope: _constructs_77d1e7e8.Construct,
        role: _aws_cdk_aws_iam_ceddda9d.IRole,
    ) -> "ContentConfig":
        '''(experimental) Called when the Build is initialized to allow this object to bind.

        :param scope: -
        :param role: -

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__02578964481495d6c165471c27f8a101e606642894654fc650791d9c9110f39c)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument role", value=role, expected_type=type_hints["role"])
        return typing.cast("ContentConfig", jsii.invoke(self, "bind", [scope, role]))

# Adding a "__jsii_proxy_class__(): typing.Type" function to the abstract class
typing.cast(typing.Any, Content).__jsii_proxy_class__ = lambda : _ContentProxy


@jsii.data_type(
    jsii_type="@aws-cdk/aws-gamelift-alpha.ContentConfig",
    jsii_struct_bases=[],
    name_mapping={"s3_location": "s3Location"},
)
class ContentConfig:
    def __init__(
        self,
        *,
        s3_location: typing.Union[_aws_cdk_aws_s3_ceddda9d.Location, typing.Dict[builtins.str, typing.Any]],
    ) -> None:
        '''(experimental) Result of binding ``Content`` into a ``Build``.

        :param s3_location: (experimental) The location of the content in S3.

        :stability: experimental
        :exampleMetadata: fixture=_generated

        Example::

            # The code below shows an example of how to instantiate this type.
            # The values are placeholders you should change.
            import aws_cdk.aws_gamelift_alpha as gamelift_alpha
            
            content_config = gamelift_alpha.ContentConfig(
                s3_location=Location(
                    bucket_name="bucketName",
                    object_key="objectKey",
            
                    # the properties below are optional
                    object_version="objectVersion"
                )
            )
        '''
        if isinstance(s3_location, dict):
            s3_location = _aws_cdk_aws_s3_ceddda9d.Location(**s3_location)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__23a167cb97741dac66b4d985310b521515726f1ddd0b3c22facfb54e2b1f0da8)
            check_type(argname="argument s3_location", value=s3_location, expected_type=type_hints["s3_location"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "s3_location": s3_location,
        }

    @builtins.property
    def s3_location(self) -> _aws_cdk_aws_s3_ceddda9d.Location:
        '''(experimental) The location of the content in S3.

        :stability: experimental
        '''
        result = self._values.get("s3_location")
        assert result is not None, "Required property 's3_location' is missing"
        return typing.cast(_aws_cdk_aws_s3_ceddda9d.Location, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ContentConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.enum(jsii_type="@aws-cdk/aws-gamelift-alpha.DeleteOption")
class DeleteOption(enum.Enum):
    '''(experimental) The type of delete to perform.

    To delete a game server group, specify the DeleteOption.

    :stability: experimental
    '''

    SAFE_DELETE = "SAFE_DELETE"
    '''(experimental) Terminates the game server group and Amazon EC2 Auto Scaling group only when it has no game servers that are in UTILIZED status.

    :stability: experimental
    '''
    FORCE_DELETE = "FORCE_DELETE"
    '''(experimental) Terminates the game server group, including all active game servers regardless of their utilization status, and the Amazon EC2 Auto Scaling group.

    :stability: experimental
    '''
    RETAIN = "RETAIN"
    '''(experimental) Does a safe delete of the game server group but retains the Amazon EC2 Auto Scaling group as is.

    :stability: experimental
    '''


@jsii.data_type(
    jsii_type="@aws-cdk/aws-gamelift-alpha.FleetAttributes",
    jsii_struct_bases=[],
    name_mapping={"fleet_arn": "fleetArn", "fleet_id": "fleetId", "role": "role"},
)
class FleetAttributes:
    def __init__(
        self,
        *,
        fleet_arn: typing.Optional[builtins.str] = None,
        fleet_id: typing.Optional[builtins.str] = None,
        role: typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole] = None,
    ) -> None:
        '''(experimental) A full specification of a fleet that can be used to import it fluently into the CDK application.

        :param fleet_arn: (experimental) The ARN of the fleet. At least one of ``fleetArn`` and ``fleetId`` must be provided. Default: derived from ``fleetId``.
        :param fleet_id: (experimental) The identifier of the fleet. At least one of ``fleetId`` and ``fleetArn`` must be provided. Default: derived from ``fleetArn``.
        :param role: (experimental) The IAM role assumed by GameLift fleet instances to access AWS ressources. Default: the imported fleet cannot be granted access to other resources as an ``iam.IGrantable``.

        :stability: experimental
        :exampleMetadata: fixture=_generated

        Example::

            # The code below shows an example of how to instantiate this type.
            # The values are placeholders you should change.
            import aws_cdk.aws_gamelift_alpha as gamelift_alpha
            from aws_cdk import aws_iam as iam
            
            # role: iam.Role
            
            fleet_attributes = gamelift_alpha.FleetAttributes(
                fleet_arn="fleetArn",
                fleet_id="fleetId",
                role=role
            )
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__35d532df97dc03beb2ad5bd1cb5393dfd16d91e9e6e0537dec0cc5074288536c)
            check_type(argname="argument fleet_arn", value=fleet_arn, expected_type=type_hints["fleet_arn"])
            check_type(argname="argument fleet_id", value=fleet_id, expected_type=type_hints["fleet_id"])
            check_type(argname="argument role", value=role, expected_type=type_hints["role"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if fleet_arn is not None:
            self._values["fleet_arn"] = fleet_arn
        if fleet_id is not None:
            self._values["fleet_id"] = fleet_id
        if role is not None:
            self._values["role"] = role

    @builtins.property
    def fleet_arn(self) -> typing.Optional[builtins.str]:
        '''(experimental) The ARN of the fleet.

        At least one of ``fleetArn`` and ``fleetId`` must be provided.

        :default: derived from ``fleetId``.

        :stability: experimental
        '''
        result = self._values.get("fleet_arn")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def fleet_id(self) -> typing.Optional[builtins.str]:
        '''(experimental) The identifier of the fleet.

        At least one of ``fleetId`` and ``fleetArn``  must be provided.

        :default: derived from ``fleetArn``.

        :stability: experimental
        '''
        result = self._values.get("fleet_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def role(self) -> typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole]:
        '''(experimental) The IAM role assumed by GameLift fleet instances to access AWS ressources.

        :default: the imported fleet cannot be granted access to other resources as an ``iam.IGrantable``.

        :stability: experimental
        '''
        result = self._values.get("role")
        return typing.cast(typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "FleetAttributes(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@aws-cdk/aws-gamelift-alpha.FleetProps",
    jsii_struct_bases=[],
    name_mapping={
        "fleet_name": "fleetName",
        "instance_type": "instanceType",
        "runtime_configuration": "runtimeConfiguration",
        "description": "description",
        "desired_capacity": "desiredCapacity",
        "locations": "locations",
        "max_size": "maxSize",
        "metric_group": "metricGroup",
        "min_size": "minSize",
        "peer_vpc": "peerVpc",
        "protect_new_game_session": "protectNewGameSession",
        "resource_creation_limit_policy": "resourceCreationLimitPolicy",
        "role": "role",
        "use_certificate": "useCertificate",
        "use_spot": "useSpot",
    },
)
class FleetProps:
    def __init__(
        self,
        *,
        fleet_name: builtins.str,
        instance_type: _aws_cdk_aws_ec2_ceddda9d.InstanceType,
        runtime_configuration: typing.Union["RuntimeConfiguration", typing.Dict[builtins.str, typing.Any]],
        description: typing.Optional[builtins.str] = None,
        desired_capacity: typing.Optional[jsii.Number] = None,
        locations: typing.Optional[typing.Sequence[typing.Union["Location", typing.Dict[builtins.str, typing.Any]]]] = None,
        max_size: typing.Optional[jsii.Number] = None,
        metric_group: typing.Optional[builtins.str] = None,
        min_size: typing.Optional[jsii.Number] = None,
        peer_vpc: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IVpc] = None,
        protect_new_game_session: typing.Optional[builtins.bool] = None,
        resource_creation_limit_policy: typing.Optional[typing.Union["ResourceCreationLimitPolicy", typing.Dict[builtins.str, typing.Any]]] = None,
        role: typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole] = None,
        use_certificate: typing.Optional[builtins.bool] = None,
        use_spot: typing.Optional[builtins.bool] = None,
    ) -> None:
        '''(experimental) Properties for a new Gamelift fleet.

        :param fleet_name: (experimental) A descriptive label that is associated with a fleet. Fleet names do not need to be unique.
        :param instance_type: (experimental) The GameLift-supported Amazon EC2 instance type to use for all fleet instances. Instance type determines the computing resources that will be used to host your game servers, including CPU, memory, storage, and networking capacity.
        :param runtime_configuration: (experimental) A collection of server process configurations that describe the set of processes to run on each instance in a fleet. Server processes run either an executable in a custom game build or a Realtime Servers script. GameLift launches the configured processes, manages their life cycle, and replaces them as needed. Each instance checks regularly for an updated runtime configuration. A GameLift instance is limited to 50 processes running concurrently. To calculate the total number of processes in a runtime configuration, add the values of the ConcurrentExecutions parameter for each ServerProcess.
        :param description: (experimental) A human-readable description of the fleet. Default: no description is provided
        :param desired_capacity: (experimental) The number of EC2 instances that you want this fleet to host. When creating a new fleet, GameLift automatically sets this value to "1" and initiates a single instance. Once the fleet is active, update this value to trigger GameLift to add or remove instances from the fleet. Default: Default capacity is 0
        :param locations: (experimental) A set of remote locations to deploy additional instances to and manage as part of the fleet. This parameter can only be used when creating fleets in AWS Regions that support multiple locations. You can add any GameLift-supported AWS Region as a remote location, in the form of an AWS Region code such as ``us-west-2``. To create a fleet with instances in the home region only, omit this parameter. Default: Create a fleet with instances in the home region only
        :param max_size: (experimental) The maximum number of instances that are allowed in the specified fleet location. Default: the default is 1
        :param metric_group: (experimental) The name of an AWS CloudWatch metric group to add this fleet to. A metric group is used to aggregate the metrics for multiple fleets. You can specify an existing metric group name or set a new name to create a new metric group. A fleet can be included in only one metric group at a time. Default: Fleet metrics are aggregated with other fleets in the default metric group
        :param min_size: (experimental) The minimum number of instances that are allowed in the specified fleet location. Default: the default is 0
        :param peer_vpc: (experimental) A VPC peering connection between your GameLift-hosted game servers and your other non-GameLift resources. Use Amazon Virtual Private Cloud (VPC) peering connections to enable your game servers to communicate directly and privately with your other AWS resources, such as a web service or a repository. You can establish VPC peering with any resources that run on AWS and are managed by an AWS account that you have access to. The VPC must be in the same Region as your fleet. Warning: Be sure to create a VPC Peering authorization through Gamelift Service API. Default: no vpc peering
        :param protect_new_game_session: (experimental) The status of termination protection for active game sessions on the fleet. By default, new game sessions are protected and cannot be terminated during a scale-down event. Default: true - Game sessions in ``ACTIVE`` status cannot be terminated during a scale-down event.
        :param resource_creation_limit_policy: (experimental) A policy that limits the number of game sessions that an individual player can create on instances in this fleet within a specified span of time. Default: No resource creation limit policy
        :param role: (experimental) The IAM role assumed by GameLift fleet instances to access AWS ressources. With a role set, any application that runs on an instance in this fleet can assume the role, including install scripts, server processes, and daemons (background processes). If providing a custom role, it needs to trust the GameLift service principal (gamelift.amazonaws.com). No permission is required by default. This property cannot be changed after the fleet is created. Default: - a role will be created with default trust to Gamelift service principal.
        :param use_certificate: (experimental) Prompts GameLift to generate a TLS/SSL certificate for the fleet. GameLift uses the certificates to encrypt traffic between game clients and the game servers running on GameLift. You can't change this property after you create the fleet. Additionnal info: AWS Certificate Manager (ACM) certificates expire after 13 months. Certificate expiration can cause fleets to fail, preventing players from connecting to instances in the fleet. We recommend you replace fleets before 13 months, consider using fleet aliases for a smooth transition. Default: TLS/SSL certificate are generated for the fleet
        :param use_spot: (experimental) Indicates whether to use On-Demand or Spot instances for this fleet. By default, fleet use on demand capacity. This property cannot be changed after the fleet is created. Default: Gamelift fleet use on demand capacity

        :stability: experimental
        :exampleMetadata: fixture=_generated

        Example::

            # The code below shows an example of how to instantiate this type.
            # The values are placeholders you should change.
            import aws_cdk.aws_gamelift_alpha as gamelift_alpha
            import aws_cdk as cdk
            from aws_cdk import aws_ec2 as ec2
            from aws_cdk import aws_iam as iam
            
            # instance_type: ec2.InstanceType
            # role: iam.Role
            # vpc: ec2.Vpc
            
            fleet_props = gamelift_alpha.FleetProps(
                fleet_name="fleetName",
                instance_type=instance_type,
                runtime_configuration=gamelift_alpha.RuntimeConfiguration(
                    server_processes=[gamelift_alpha.ServerProcess(
                        launch_path="launchPath",
            
                        # the properties below are optional
                        concurrent_executions=123,
                        parameters="parameters"
                    )],
            
                    # the properties below are optional
                    game_session_activation_timeout=cdk.Duration.minutes(30),
                    max_concurrent_game_session_activations=123
                ),
            
                # the properties below are optional
                description="description",
                desired_capacity=123,
                locations=[gamelift_alpha.Location(
                    region="region",
            
                    # the properties below are optional
                    capacity=gamelift_alpha.LocationCapacity(
                        desired_capacity=123,
                        max_size=123,
                        min_size=123
                    )
                )],
                max_size=123,
                metric_group="metricGroup",
                min_size=123,
                peer_vpc=vpc,
                protect_new_game_session=False,
                resource_creation_limit_policy=gamelift_alpha.ResourceCreationLimitPolicy(
                    new_game_sessions_per_creator=123,
                    policy_period=cdk.Duration.minutes(30)
                ),
                role=role,
                use_certificate=False,
                use_spot=False
            )
        '''
        if isinstance(runtime_configuration, dict):
            runtime_configuration = RuntimeConfiguration(**runtime_configuration)
        if isinstance(resource_creation_limit_policy, dict):
            resource_creation_limit_policy = ResourceCreationLimitPolicy(**resource_creation_limit_policy)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b81a93e51de6b03726329d65b2414826a941e9123fb0a5ec20bcad7f184a4382)
            check_type(argname="argument fleet_name", value=fleet_name, expected_type=type_hints["fleet_name"])
            check_type(argname="argument instance_type", value=instance_type, expected_type=type_hints["instance_type"])
            check_type(argname="argument runtime_configuration", value=runtime_configuration, expected_type=type_hints["runtime_configuration"])
            check_type(argname="argument description", value=description, expected_type=type_hints["description"])
            check_type(argname="argument desired_capacity", value=desired_capacity, expected_type=type_hints["desired_capacity"])
            check_type(argname="argument locations", value=locations, expected_type=type_hints["locations"])
            check_type(argname="argument max_size", value=max_size, expected_type=type_hints["max_size"])
            check_type(argname="argument metric_group", value=metric_group, expected_type=type_hints["metric_group"])
            check_type(argname="argument min_size", value=min_size, expected_type=type_hints["min_size"])
            check_type(argname="argument peer_vpc", value=peer_vpc, expected_type=type_hints["peer_vpc"])
            check_type(argname="argument protect_new_game_session", value=protect_new_game_session, expected_type=type_hints["protect_new_game_session"])
            check_type(argname="argument resource_creation_limit_policy", value=resource_creation_limit_policy, expected_type=type_hints["resource_creation_limit_policy"])
            check_type(argname="argument role", value=role, expected_type=type_hints["role"])
            check_type(argname="argument use_certificate", value=use_certificate, expected_type=type_hints["use_certificate"])
            check_type(argname="argument use_spot", value=use_spot, expected_type=type_hints["use_spot"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "fleet_name": fleet_name,
            "instance_type": instance_type,
            "runtime_configuration": runtime_configuration,
        }
        if description is not None:
            self._values["description"] = description
        if desired_capacity is not None:
            self._values["desired_capacity"] = desired_capacity
        if locations is not None:
            self._values["locations"] = locations
        if max_size is not None:
            self._values["max_size"] = max_size
        if metric_group is not None:
            self._values["metric_group"] = metric_group
        if min_size is not None:
            self._values["min_size"] = min_size
        if peer_vpc is not None:
            self._values["peer_vpc"] = peer_vpc
        if protect_new_game_session is not None:
            self._values["protect_new_game_session"] = protect_new_game_session
        if resource_creation_limit_policy is not None:
            self._values["resource_creation_limit_policy"] = resource_creation_limit_policy
        if role is not None:
            self._values["role"] = role
        if use_certificate is not None:
            self._values["use_certificate"] = use_certificate
        if use_spot is not None:
            self._values["use_spot"] = use_spot

    @builtins.property
    def fleet_name(self) -> builtins.str:
        '''(experimental) A descriptive label that is associated with a fleet.

        Fleet names do not need to be unique.

        :stability: experimental
        '''
        result = self._values.get("fleet_name")
        assert result is not None, "Required property 'fleet_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def instance_type(self) -> _aws_cdk_aws_ec2_ceddda9d.InstanceType:
        '''(experimental) The GameLift-supported Amazon EC2 instance type to use for all fleet instances.

        Instance type determines the computing resources that will be used to host your game servers, including CPU, memory, storage, and networking capacity.

        :see: http://aws.amazon.com/ec2/instance-types/ for detailed descriptions of Amazon EC2 instance types.
        :stability: experimental
        '''
        result = self._values.get("instance_type")
        assert result is not None, "Required property 'instance_type' is missing"
        return typing.cast(_aws_cdk_aws_ec2_ceddda9d.InstanceType, result)

    @builtins.property
    def runtime_configuration(self) -> "RuntimeConfiguration":
        '''(experimental) A collection of server process configurations that describe the set of processes to run on each instance in a fleet.

        Server processes run either an executable in a custom game build or a Realtime Servers script.
        GameLift launches the configured processes, manages their life cycle, and replaces them as needed.
        Each instance checks regularly for an updated runtime configuration.

        A GameLift instance is limited to 50 processes running concurrently.
        To calculate the total number of processes in a runtime configuration, add the values of the ConcurrentExecutions parameter for each ServerProcess.

        :see: https://docs.aws.amazon.com/gamelift/latest/developerguide/fleets-multiprocess.html
        :stability: experimental
        '''
        result = self._values.get("runtime_configuration")
        assert result is not None, "Required property 'runtime_configuration' is missing"
        return typing.cast("RuntimeConfiguration", result)

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        '''(experimental) A human-readable description of the fleet.

        :default: no description is provided

        :stability: experimental
        '''
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def desired_capacity(self) -> typing.Optional[jsii.Number]:
        '''(experimental) The number of EC2 instances that you want this fleet to host.

        When creating a new fleet, GameLift automatically sets this value to "1" and initiates a single instance.
        Once the fleet is active, update this value to trigger GameLift to add or remove instances from the fleet.

        :default: Default capacity is 0

        :stability: experimental
        '''
        result = self._values.get("desired_capacity")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def locations(self) -> typing.Optional[typing.List["Location"]]:
        '''(experimental) A set of remote locations to deploy additional instances to and manage as part of the fleet.

        This parameter can only be used when creating fleets in AWS Regions that support multiple locations.
        You can add any GameLift-supported AWS Region as a remote location, in the form of an AWS Region code such as ``us-west-2``.
        To create a fleet with instances in the home region only, omit this parameter.

        :default: Create a fleet with instances in the home region only

        :stability: experimental
        '''
        result = self._values.get("locations")
        return typing.cast(typing.Optional[typing.List["Location"]], result)

    @builtins.property
    def max_size(self) -> typing.Optional[jsii.Number]:
        '''(experimental) The maximum number of instances that are allowed in the specified fleet location.

        :default: the default is 1

        :stability: experimental
        '''
        result = self._values.get("max_size")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def metric_group(self) -> typing.Optional[builtins.str]:
        '''(experimental) The name of an AWS CloudWatch metric group to add this fleet to.

        A metric group is used to aggregate the metrics for multiple fleets.
        You can specify an existing metric group name or set a new name to create a new metric group.
        A fleet can be included in only one metric group at a time.

        :default: Fleet metrics are aggregated with other fleets in the default metric group

        :stability: experimental
        '''
        result = self._values.get("metric_group")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def min_size(self) -> typing.Optional[jsii.Number]:
        '''(experimental) The minimum number of instances that are allowed in the specified fleet location.

        :default: the default is 0

        :stability: experimental
        '''
        result = self._values.get("min_size")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def peer_vpc(self) -> typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IVpc]:
        '''(experimental) A VPC peering connection between your GameLift-hosted game servers and your other non-GameLift resources.

        Use Amazon Virtual Private Cloud (VPC) peering connections to enable your game servers to communicate directly and privately with your other AWS resources, such as a web service or a repository.
        You can establish VPC peering with any resources that run on AWS and are managed by an AWS account that you have access to.
        The VPC must be in the same Region as your fleet.

        Warning:
        Be sure to create a VPC Peering authorization through Gamelift Service API.

        :default: no vpc peering

        :see: https://docs.aws.amazon.com/gamelift/latest/developerguide/vpc-peering.html
        :stability: experimental
        '''
        result = self._values.get("peer_vpc")
        return typing.cast(typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IVpc], result)

    @builtins.property
    def protect_new_game_session(self) -> typing.Optional[builtins.bool]:
        '''(experimental) The status of termination protection for active game sessions on the fleet.

        By default, new game sessions are protected and cannot be terminated during a scale-down event.

        :default: true - Game sessions in ``ACTIVE`` status cannot be terminated during a scale-down event.

        :stability: experimental
        '''
        result = self._values.get("protect_new_game_session")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def resource_creation_limit_policy(
        self,
    ) -> typing.Optional["ResourceCreationLimitPolicy"]:
        '''(experimental) A policy that limits the number of game sessions that an individual player can create on instances in this fleet within a specified span of time.

        :default: No resource creation limit policy

        :stability: experimental
        '''
        result = self._values.get("resource_creation_limit_policy")
        return typing.cast(typing.Optional["ResourceCreationLimitPolicy"], result)

    @builtins.property
    def role(self) -> typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole]:
        '''(experimental) The IAM role assumed by GameLift fleet instances to access AWS ressources.

        With a role set, any application that runs on an instance in this fleet can assume the role, including install scripts, server processes, and daemons (background processes).
        If providing a custom role, it needs to trust the GameLift service principal (gamelift.amazonaws.com).
        No permission is required by default.

        This property cannot be changed after the fleet is created.

        :default: - a role will be created with default trust to Gamelift service principal.

        :see: https://docs.aws.amazon.com/gamelift/latest/developerguide/gamelift-sdk-server-resources.html
        :stability: experimental
        '''
        result = self._values.get("role")
        return typing.cast(typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole], result)

    @builtins.property
    def use_certificate(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Prompts GameLift to generate a TLS/SSL certificate for the fleet.

        GameLift uses the certificates to encrypt traffic between game clients and the game servers running on GameLift.

        You can't change this property after you create the fleet.

        Additionnal info:
        AWS Certificate Manager (ACM) certificates expire after 13 months.
        Certificate expiration can cause fleets to fail, preventing players from connecting to instances in the fleet.
        We recommend you replace fleets before 13 months, consider using fleet aliases for a smooth transition.

        :default: TLS/SSL certificate are generated for the fleet

        :stability: experimental
        '''
        result = self._values.get("use_certificate")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def use_spot(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Indicates whether to use On-Demand or Spot instances for this fleet. By default, fleet use on demand capacity.

        This property cannot be changed after the fleet is created.

        :default: Gamelift fleet use on demand capacity

        :see: https://docs.aws.amazon.com/gamelift/latest/developerguide/gamelift-ec2-instances.html#gamelift-ec2-instances-spot
        :stability: experimental
        '''
        result = self._values.get("use_spot")
        return typing.cast(typing.Optional[builtins.bool], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "FleetProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@aws-cdk/aws-gamelift-alpha.GameProperty",
    jsii_struct_bases=[],
    name_mapping={"key": "key", "value": "value"},
)
class GameProperty:
    def __init__(self, *, key: builtins.str, value: builtins.str) -> None:
        '''(experimental) A set of custom properties for a game session, formatted as key-value pairs.

        These properties are passed to a game server process with a request to start a new game session.

        This parameter is not used for Standalone FlexMatch mode.

        :param key: (experimental) The game property identifier.
        :param value: (experimental) The game property value.

        :see: https://docs.aws.amazon.com/gamelift/latest/developerguide/gamelift-sdk-server-api.html#gamelift-sdk-server-startsession
        :stability: experimental
        :exampleMetadata: fixture=_generated

        Example::

            # The code below shows an example of how to instantiate this type.
            # The values are placeholders you should change.
            import aws_cdk.aws_gamelift_alpha as gamelift_alpha
            
            game_property = gamelift_alpha.GameProperty(
                key="key",
                value="value"
            )
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0e8980d178329ea7c3dcc75b375385b207b175d8e61a252631f5104bb4fad972)
            check_type(argname="argument key", value=key, expected_type=type_hints["key"])
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "key": key,
            "value": value,
        }

    @builtins.property
    def key(self) -> builtins.str:
        '''(experimental) The game property identifier.

        :stability: experimental
        '''
        result = self._values.get("key")
        assert result is not None, "Required property 'key' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def value(self) -> builtins.str:
        '''(experimental) The game property value.

        :stability: experimental
        '''
        result = self._values.get("value")
        assert result is not None, "Required property 'value' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "GameProperty(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@aws-cdk/aws-gamelift-alpha.GameServerGroupAttributes",
    jsii_struct_bases=[],
    name_mapping={
        "auto_scaling_group_arn": "autoScalingGroupArn",
        "game_server_group_arn": "gameServerGroupArn",
        "game_server_group_name": "gameServerGroupName",
        "role": "role",
    },
)
class GameServerGroupAttributes:
    def __init__(
        self,
        *,
        auto_scaling_group_arn: builtins.str,
        game_server_group_arn: typing.Optional[builtins.str] = None,
        game_server_group_name: typing.Optional[builtins.str] = None,
        role: typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole] = None,
    ) -> None:
        '''(experimental) Represents a GameServerGroup content defined outside of this stack.

        :param auto_scaling_group_arn: (experimental) The ARN of the generated AutoScaling group. Default: the imported game server group does not have autoscaling group information
        :param game_server_group_arn: (experimental) The ARN of the game server group. At least one of ``gameServerGroupArn`` and ``gameServerGroupName`` must be provided. Default: derived from ``gameServerGroupName``.
        :param game_server_group_name: (experimental) The name of the game server group. At least one of ``gameServerGroupArn`` and ``gameServerGroupName`` must be provided. Default: derived from ``gameServerGroupArn``.
        :param role: (experimental) The IAM role that allows Amazon GameLift to access your Amazon EC2 Auto Scaling groups. Default: the imported game server group cannot be granted access to other resources as an ``iam.IGrantable``.

        :stability: experimental
        :exampleMetadata: fixture=_generated

        Example::

            # The code below shows an example of how to instantiate this type.
            # The values are placeholders you should change.
            import aws_cdk.aws_gamelift_alpha as gamelift_alpha
            from aws_cdk import aws_iam as iam
            
            # role: iam.Role
            
            game_server_group_attributes = gamelift_alpha.GameServerGroupAttributes(
                auto_scaling_group_arn="autoScalingGroupArn",
            
                # the properties below are optional
                game_server_group_arn="gameServerGroupArn",
                game_server_group_name="gameServerGroupName",
                role=role
            )
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a95367b408716c3da6316646dac97baa91d468c4be616abe0e3fb8c79f67d991)
            check_type(argname="argument auto_scaling_group_arn", value=auto_scaling_group_arn, expected_type=type_hints["auto_scaling_group_arn"])
            check_type(argname="argument game_server_group_arn", value=game_server_group_arn, expected_type=type_hints["game_server_group_arn"])
            check_type(argname="argument game_server_group_name", value=game_server_group_name, expected_type=type_hints["game_server_group_name"])
            check_type(argname="argument role", value=role, expected_type=type_hints["role"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "auto_scaling_group_arn": auto_scaling_group_arn,
        }
        if game_server_group_arn is not None:
            self._values["game_server_group_arn"] = game_server_group_arn
        if game_server_group_name is not None:
            self._values["game_server_group_name"] = game_server_group_name
        if role is not None:
            self._values["role"] = role

    @builtins.property
    def auto_scaling_group_arn(self) -> builtins.str:
        '''(experimental) The ARN of the generated AutoScaling group.

        :default: the imported game server group does not have autoscaling group information

        :stability: experimental
        '''
        result = self._values.get("auto_scaling_group_arn")
        assert result is not None, "Required property 'auto_scaling_group_arn' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def game_server_group_arn(self) -> typing.Optional[builtins.str]:
        '''(experimental) The ARN of the game server group.

        At least one of ``gameServerGroupArn`` and ``gameServerGroupName`` must be provided.

        :default: derived from ``gameServerGroupName``.

        :stability: experimental
        '''
        result = self._values.get("game_server_group_arn")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def game_server_group_name(self) -> typing.Optional[builtins.str]:
        '''(experimental) The name of the game server group.

        At least one of ``gameServerGroupArn`` and ``gameServerGroupName`` must be provided.

        :default: derived from ``gameServerGroupArn``.

        :stability: experimental
        '''
        result = self._values.get("game_server_group_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def role(self) -> typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole]:
        '''(experimental) The IAM role that allows Amazon GameLift to access your Amazon EC2 Auto Scaling groups.

        :default: the imported game server group cannot be granted access to other resources as an ``iam.IGrantable``.

        :stability: experimental
        '''
        result = self._values.get("role")
        return typing.cast(typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "GameServerGroupAttributes(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@aws-cdk/aws-gamelift-alpha.GameServerGroupProps",
    jsii_struct_bases=[],
    name_mapping={
        "game_server_group_name": "gameServerGroupName",
        "instance_definitions": "instanceDefinitions",
        "launch_template": "launchTemplate",
        "vpc": "vpc",
        "auto_scaling_policy": "autoScalingPolicy",
        "balancing_strategy": "balancingStrategy",
        "delete_option": "deleteOption",
        "max_size": "maxSize",
        "min_size": "minSize",
        "protect_game_server": "protectGameServer",
        "role": "role",
        "vpc_subnets": "vpcSubnets",
    },
)
class GameServerGroupProps:
    def __init__(
        self,
        *,
        game_server_group_name: builtins.str,
        instance_definitions: typing.Sequence[typing.Union["InstanceDefinition", typing.Dict[builtins.str, typing.Any]]],
        launch_template: _aws_cdk_aws_ec2_ceddda9d.ILaunchTemplate,
        vpc: _aws_cdk_aws_ec2_ceddda9d.IVpc,
        auto_scaling_policy: typing.Optional[typing.Union[AutoScalingPolicy, typing.Dict[builtins.str, typing.Any]]] = None,
        balancing_strategy: typing.Optional[BalancingStrategy] = None,
        delete_option: typing.Optional[DeleteOption] = None,
        max_size: typing.Optional[jsii.Number] = None,
        min_size: typing.Optional[jsii.Number] = None,
        protect_game_server: typing.Optional[builtins.bool] = None,
        role: typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole] = None,
        vpc_subnets: typing.Optional[typing.Union[_aws_cdk_aws_ec2_ceddda9d.SubnetSelection, typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''(experimental) Properties for a new Gamelift FleetIQ Game server group.

        :param game_server_group_name: (experimental) A developer-defined identifier for the game server group. The name is unique for each Region in each AWS account.
        :param instance_definitions: (experimental) The set of Amazon EC2 instance types that GameLift FleetIQ can use when balancing and automatically scaling instances in the corresponding Auto Scaling group.
        :param launch_template: (experimental) The Amazon EC2 launch template that contains configuration settings and game server code to be deployed to all instances in the game server group. After the Auto Scaling group is created, update this value directly in the Auto Scaling group using the AWS console or APIs. NOTE: If you specify network interfaces in your launch template, you must explicitly set the property AssociatePublicIpAddress to ``true``. If no network interface is specified in the launch template, GameLift FleetIQ uses your account's default VPC.
        :param vpc: (experimental) The VPC network to place the game server group in. By default, all GameLift FleetIQ-supported Availability Zones are used. You can use this parameter to specify VPCs that you've set up. This property cannot be updated after the game server group is created, and the corresponding Auto Scaling group will always use the property value that is set with this request, even if the Auto Scaling group is updated directly.
        :param auto_scaling_policy: (experimental) Configuration settings to define a scaling policy for the Auto Scaling group that is optimized for game hosting. The scaling policy uses the metric ``PercentUtilizedGameServers`` to maintain a buffer of idle game servers that can immediately accommodate new games and players. After the Auto Scaling group is created, update this value directly in the Auto Scaling group using the AWS console or APIs. Default: no autoscaling policy settled
        :param balancing_strategy: (experimental) Indicates how GameLift FleetIQ balances the use of Spot Instances and On-Demand Instances in the game server group. Default: SPOT_PREFERRED
        :param delete_option: (experimental) The type of delete to perform. To delete a game server group, specify the DeleteOption Default: SAFE_DELETE
        :param max_size: (experimental) The maximum number of instances allowed in the Amazon EC2 Auto Scaling group. During automatic scaling events, GameLift FleetIQ and EC2 do not scale up the group above this maximum. After the Auto Scaling group is created, update this value directly in the Auto Scaling group using the AWS console or APIs. Default: the default is 1
        :param min_size: (experimental) The minimum number of instances allowed in the Amazon EC2 Auto Scaling group. During automatic scaling events, GameLift FleetIQ and Amazon EC2 do not scale down the group below this minimum. In production, this value should be set to at least 1. After the Auto Scaling group is created, update this value directly in the Auto Scaling group using the AWS console or APIs. Default: the default is 0
        :param protect_game_server: (experimental) A flag that indicates whether instances in the game server group are protected from early termination. Unprotected instances that have active game servers running might be terminated during a scale-down event, causing players to be dropped from the game. Protected instances cannot be terminated while there are active game servers running except in the event of a forced game server group deletion. An exception to this is with Spot Instances, which can be terminated by AWS regardless of protection status. Default: game servers running might be terminated during a scale-down event
        :param role: (experimental) The IAM role that allows Amazon GameLift to access your Amazon EC2 Auto Scaling groups. Default: - a role will be created with default trust to Gamelift and Autoscaling service principal with a default policy ``GameLiftGameServerGroupPolicy`` attached.
        :param vpc_subnets: (experimental) Game server group subnet selection. Default: all GameLift FleetIQ-supported Availability Zones are used.

        :stability: experimental
        :exampleMetadata: infused

        Example::

            # launch_template: ec2.ILaunchTemplate
            # vpc: ec2.IVpc
            
            
            gamelift.GameServerGroup(self, "GameServerGroup",
                game_server_group_name="sample-gameservergroup-name",
                instance_definitions=[gamelift.InstanceDefinition(
                    instance_type=ec2.InstanceType.of(ec2.InstanceClass.C5, ec2.InstanceSize.LARGE)
                ), gamelift.InstanceDefinition(
                    instance_type=ec2.InstanceType.of(ec2.InstanceClass.C4, ec2.InstanceSize.LARGE)
                )],
                launch_template=launch_template,
                vpc=vpc,
                vpc_subnets=ec2.SubnetSelection(subnet_type=ec2.SubnetType.PUBLIC)
            )
        '''
        if isinstance(auto_scaling_policy, dict):
            auto_scaling_policy = AutoScalingPolicy(**auto_scaling_policy)
        if isinstance(vpc_subnets, dict):
            vpc_subnets = _aws_cdk_aws_ec2_ceddda9d.SubnetSelection(**vpc_subnets)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__940bf2cd04369fce6e5224d911d6b8cccc442bf95877315cc6c35048dddb278b)
            check_type(argname="argument game_server_group_name", value=game_server_group_name, expected_type=type_hints["game_server_group_name"])
            check_type(argname="argument instance_definitions", value=instance_definitions, expected_type=type_hints["instance_definitions"])
            check_type(argname="argument launch_template", value=launch_template, expected_type=type_hints["launch_template"])
            check_type(argname="argument vpc", value=vpc, expected_type=type_hints["vpc"])
            check_type(argname="argument auto_scaling_policy", value=auto_scaling_policy, expected_type=type_hints["auto_scaling_policy"])
            check_type(argname="argument balancing_strategy", value=balancing_strategy, expected_type=type_hints["balancing_strategy"])
            check_type(argname="argument delete_option", value=delete_option, expected_type=type_hints["delete_option"])
            check_type(argname="argument max_size", value=max_size, expected_type=type_hints["max_size"])
            check_type(argname="argument min_size", value=min_size, expected_type=type_hints["min_size"])
            check_type(argname="argument protect_game_server", value=protect_game_server, expected_type=type_hints["protect_game_server"])
            check_type(argname="argument role", value=role, expected_type=type_hints["role"])
            check_type(argname="argument vpc_subnets", value=vpc_subnets, expected_type=type_hints["vpc_subnets"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "game_server_group_name": game_server_group_name,
            "instance_definitions": instance_definitions,
            "launch_template": launch_template,
            "vpc": vpc,
        }
        if auto_scaling_policy is not None:
            self._values["auto_scaling_policy"] = auto_scaling_policy
        if balancing_strategy is not None:
            self._values["balancing_strategy"] = balancing_strategy
        if delete_option is not None:
            self._values["delete_option"] = delete_option
        if max_size is not None:
            self._values["max_size"] = max_size
        if min_size is not None:
            self._values["min_size"] = min_size
        if protect_game_server is not None:
            self._values["protect_game_server"] = protect_game_server
        if role is not None:
            self._values["role"] = role
        if vpc_subnets is not None:
            self._values["vpc_subnets"] = vpc_subnets

    @builtins.property
    def game_server_group_name(self) -> builtins.str:
        '''(experimental) A developer-defined identifier for the game server group.

        The name is unique for each Region in each AWS account.

        :stability: experimental
        '''
        result = self._values.get("game_server_group_name")
        assert result is not None, "Required property 'game_server_group_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def instance_definitions(self) -> typing.List["InstanceDefinition"]:
        '''(experimental) The set of Amazon EC2 instance types that GameLift FleetIQ can use when balancing and automatically scaling instances in the corresponding Auto Scaling group.

        :stability: experimental
        '''
        result = self._values.get("instance_definitions")
        assert result is not None, "Required property 'instance_definitions' is missing"
        return typing.cast(typing.List["InstanceDefinition"], result)

    @builtins.property
    def launch_template(self) -> _aws_cdk_aws_ec2_ceddda9d.ILaunchTemplate:
        '''(experimental) The Amazon EC2 launch template that contains configuration settings and game server code to be deployed to all instances in the game server group.

        After the Auto Scaling group is created, update this value directly in the Auto Scaling group using the AWS console or APIs.

        NOTE:
        If you specify network interfaces in your launch template, you must explicitly set the property AssociatePublicIpAddress to ``true``.
        If no network interface is specified in the launch template, GameLift FleetIQ uses your account's default VPC.

        :see: https://docs.aws.amazon.com/autoscaling/ec2/userguide/create-launch-template.html
        :stability: experimental
        '''
        result = self._values.get("launch_template")
        assert result is not None, "Required property 'launch_template' is missing"
        return typing.cast(_aws_cdk_aws_ec2_ceddda9d.ILaunchTemplate, result)

    @builtins.property
    def vpc(self) -> _aws_cdk_aws_ec2_ceddda9d.IVpc:
        '''(experimental) The VPC network to place the game server group in.

        By default, all GameLift FleetIQ-supported Availability Zones are used.

        You can use this parameter to specify VPCs that you've set up.

        This property cannot be updated after the game server group is created,
        and the corresponding Auto Scaling group will always use the property value that is set with this request,
        even if the Auto Scaling group is updated directly.

        :stability: experimental
        '''
        result = self._values.get("vpc")
        assert result is not None, "Required property 'vpc' is missing"
        return typing.cast(_aws_cdk_aws_ec2_ceddda9d.IVpc, result)

    @builtins.property
    def auto_scaling_policy(self) -> typing.Optional[AutoScalingPolicy]:
        '''(experimental) Configuration settings to define a scaling policy for the Auto Scaling group that is optimized for game hosting.

        The scaling policy uses the metric ``PercentUtilizedGameServers`` to maintain a buffer of idle game servers that can immediately accommodate new games and players.

        After the Auto Scaling group is created, update this value directly in the Auto Scaling group using the AWS console or APIs.

        :default: no autoscaling policy settled

        :stability: experimental
        '''
        result = self._values.get("auto_scaling_policy")
        return typing.cast(typing.Optional[AutoScalingPolicy], result)

    @builtins.property
    def balancing_strategy(self) -> typing.Optional[BalancingStrategy]:
        '''(experimental) Indicates how GameLift FleetIQ balances the use of Spot Instances and On-Demand Instances in the game server group.

        :default: SPOT_PREFERRED

        :stability: experimental
        '''
        result = self._values.get("balancing_strategy")
        return typing.cast(typing.Optional[BalancingStrategy], result)

    @builtins.property
    def delete_option(self) -> typing.Optional[DeleteOption]:
        '''(experimental) The type of delete to perform.

        To delete a game server group, specify the DeleteOption

        :default: SAFE_DELETE

        :stability: experimental
        '''
        result = self._values.get("delete_option")
        return typing.cast(typing.Optional[DeleteOption], result)

    @builtins.property
    def max_size(self) -> typing.Optional[jsii.Number]:
        '''(experimental) The maximum number of instances allowed in the Amazon EC2 Auto Scaling group.

        During automatic scaling events, GameLift FleetIQ and EC2 do not scale up the group above this maximum.

        After the Auto Scaling group is created, update this value directly in the Auto Scaling group using the AWS console or APIs.

        :default: the default is 1

        :stability: experimental
        '''
        result = self._values.get("max_size")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def min_size(self) -> typing.Optional[jsii.Number]:
        '''(experimental) The minimum number of instances allowed in the Amazon EC2 Auto Scaling group.

        During automatic scaling events, GameLift FleetIQ and Amazon EC2 do not scale down the group below this minimum.

        In production, this value should be set to at least 1.

        After the Auto Scaling group is created, update this value directly in the Auto Scaling group using the AWS console or APIs.

        :default: the default is 0

        :stability: experimental
        '''
        result = self._values.get("min_size")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def protect_game_server(self) -> typing.Optional[builtins.bool]:
        '''(experimental) A flag that indicates whether instances in the game server group are protected from early termination.

        Unprotected instances that have active game servers running might be terminated during a scale-down event, causing players to be dropped from the game.
        Protected instances cannot be terminated while there are active game servers running except in the event of a forced game server group deletion.

        An exception to this is with Spot Instances, which can be terminated by AWS regardless of protection status.

        :default: game servers running might be terminated during a scale-down event

        :stability: experimental
        '''
        result = self._values.get("protect_game_server")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def role(self) -> typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole]:
        '''(experimental) The IAM role that allows Amazon GameLift to access your Amazon EC2 Auto Scaling groups.

        :default: - a role will be created with default trust to Gamelift and Autoscaling service principal with a default policy ``GameLiftGameServerGroupPolicy`` attached.

        :see: https://docs.aws.amazon.com/gamelift/latest/fleetiqguide/gsg-iam-permissions-roles.html
        :stability: experimental
        '''
        result = self._values.get("role")
        return typing.cast(typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole], result)

    @builtins.property
    def vpc_subnets(self) -> typing.Optional[_aws_cdk_aws_ec2_ceddda9d.SubnetSelection]:
        '''(experimental) Game server group subnet selection.

        :default: all GameLift FleetIQ-supported Availability Zones are used.

        :stability: experimental
        '''
        result = self._values.get("vpc_subnets")
        return typing.cast(typing.Optional[_aws_cdk_aws_ec2_ceddda9d.SubnetSelection], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "GameServerGroupProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@aws-cdk/aws-gamelift-alpha.GameSessionQueueAttributes",
    jsii_struct_bases=[],
    name_mapping={
        "game_session_queue_arn": "gameSessionQueueArn",
        "game_session_queue_name": "gameSessionQueueName",
    },
)
class GameSessionQueueAttributes:
    def __init__(
        self,
        *,
        game_session_queue_arn: typing.Optional[builtins.str] = None,
        game_session_queue_name: typing.Optional[builtins.str] = None,
    ) -> None:
        '''(experimental) A full specification of an gameSessionQueue that can be used to import it fluently into the CDK application.

        :param game_session_queue_arn: (experimental) The ARN of the gameSessionQueue. At least one of ``gameSessionQueueArn`` and ``gameSessionQueueName`` must be provided. Default: derived from ``gameSessionQueueName``.
        :param game_session_queue_name: (experimental) The name of the gameSessionQueue. At least one of ``gameSessionQueueName`` and ``gameSessionQueueArn`` must be provided. Default: derived from ``gameSessionQueueArn``.

        :stability: experimental
        :exampleMetadata: fixture=_generated

        Example::

            # The code below shows an example of how to instantiate this type.
            # The values are placeholders you should change.
            import aws_cdk.aws_gamelift_alpha as gamelift_alpha
            
            game_session_queue_attributes = gamelift_alpha.GameSessionQueueAttributes(
                game_session_queue_arn="gameSessionQueueArn",
                game_session_queue_name="gameSessionQueueName"
            )
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__78641a197786fbf0ecb0cc47203e19aadf2baf2f21a8db53e544cc8922167bdc)
            check_type(argname="argument game_session_queue_arn", value=game_session_queue_arn, expected_type=type_hints["game_session_queue_arn"])
            check_type(argname="argument game_session_queue_name", value=game_session_queue_name, expected_type=type_hints["game_session_queue_name"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if game_session_queue_arn is not None:
            self._values["game_session_queue_arn"] = game_session_queue_arn
        if game_session_queue_name is not None:
            self._values["game_session_queue_name"] = game_session_queue_name

    @builtins.property
    def game_session_queue_arn(self) -> typing.Optional[builtins.str]:
        '''(experimental) The ARN of the gameSessionQueue.

        At least one of ``gameSessionQueueArn`` and ``gameSessionQueueName`` must be provided.

        :default: derived from ``gameSessionQueueName``.

        :stability: experimental
        '''
        result = self._values.get("game_session_queue_arn")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def game_session_queue_name(self) -> typing.Optional[builtins.str]:
        '''(experimental) The name of the gameSessionQueue.

        At least one of ``gameSessionQueueName`` and ``gameSessionQueueArn``  must be provided.

        :default: derived from ``gameSessionQueueArn``.

        :stability: experimental
        '''
        result = self._values.get("game_session_queue_name")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "GameSessionQueueAttributes(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@aws-cdk/aws-gamelift-alpha.GameSessionQueueProps",
    jsii_struct_bases=[],
    name_mapping={
        "destinations": "destinations",
        "game_session_queue_name": "gameSessionQueueName",
        "allowed_locations": "allowedLocations",
        "custom_event_data": "customEventData",
        "notification_target": "notificationTarget",
        "player_latency_policies": "playerLatencyPolicies",
        "priority_configuration": "priorityConfiguration",
        "timeout": "timeout",
    },
)
class GameSessionQueueProps:
    def __init__(
        self,
        *,
        destinations: typing.Sequence["IGameSessionQueueDestination"],
        game_session_queue_name: builtins.str,
        allowed_locations: typing.Optional[typing.Sequence[builtins.str]] = None,
        custom_event_data: typing.Optional[builtins.str] = None,
        notification_target: typing.Optional[_aws_cdk_aws_sns_ceddda9d.ITopic] = None,
        player_latency_policies: typing.Optional[typing.Sequence[typing.Union["PlayerLatencyPolicy", typing.Dict[builtins.str, typing.Any]]]] = None,
        priority_configuration: typing.Optional[typing.Union["PriorityConfiguration", typing.Dict[builtins.str, typing.Any]]] = None,
        timeout: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
    ) -> None:
        '''(experimental) Properties for a new Fleet gameSessionQueue.

        :param destinations: (experimental) A list of fleets and/or fleet alias that can be used to fulfill game session placement requests in the queue. Destinations are listed in order of placement preference.
        :param game_session_queue_name: (experimental) Name of this gameSessionQueue.
        :param allowed_locations: (experimental) A list of locations where a queue is allowed to place new game sessions. Locations are specified in the form of AWS Region codes, such as ``us-west-2``. For queues that have multi-location fleets, you can use a filter configuration allow placement with some, but not all of these locations. Default: game sessions can be placed in any queue location
        :param custom_event_data: (experimental) Information to be added to all events that are related to this game session queue. Default: no customer event data
        :param notification_target: (experimental) An SNS topic is set up to receive game session placement notifications. Default: no notification
        :param player_latency_policies: (experimental) A set of policies that act as a sliding cap on player latency. FleetIQ works to deliver low latency for most players in a game session. These policies ensure that no individual player can be placed into a game with unreasonably high latency. Use multiple policies to gradually relax latency requirements a step at a time. Multiple policies are applied based on their maximum allowed latency, starting with the lowest value. Default: no player latency policy
        :param priority_configuration: (experimental) Custom settings to use when prioritizing destinations and locations for game session placements. This configuration replaces the FleetIQ default prioritization process. Priority types that are not explicitly named will be automatically applied at the end of the prioritization process. Default: no priority configuration
        :param timeout: (experimental) The maximum time, that a new game session placement request remains in the queue. When a request exceeds this time, the game session placement changes to a ``TIMED_OUT`` status. Default: 50 seconds

        :stability: experimental
        :exampleMetadata: infused

        Example::

            # fleet: gamelift.BuildFleet
            # alias: gamelift.Alias
            
            
            queue = gamelift.GameSessionQueue(self, "GameSessionQueue",
                game_session_queue_name="my-queue-name",
                destinations=[fleet]
            )
            queue.add_destination(alias)
        '''
        if isinstance(priority_configuration, dict):
            priority_configuration = PriorityConfiguration(**priority_configuration)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d7ec2128913b26e96704a23d51e9a927d5c7288d3b8b35b1869614f35fa19015)
            check_type(argname="argument destinations", value=destinations, expected_type=type_hints["destinations"])
            check_type(argname="argument game_session_queue_name", value=game_session_queue_name, expected_type=type_hints["game_session_queue_name"])
            check_type(argname="argument allowed_locations", value=allowed_locations, expected_type=type_hints["allowed_locations"])
            check_type(argname="argument custom_event_data", value=custom_event_data, expected_type=type_hints["custom_event_data"])
            check_type(argname="argument notification_target", value=notification_target, expected_type=type_hints["notification_target"])
            check_type(argname="argument player_latency_policies", value=player_latency_policies, expected_type=type_hints["player_latency_policies"])
            check_type(argname="argument priority_configuration", value=priority_configuration, expected_type=type_hints["priority_configuration"])
            check_type(argname="argument timeout", value=timeout, expected_type=type_hints["timeout"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "destinations": destinations,
            "game_session_queue_name": game_session_queue_name,
        }
        if allowed_locations is not None:
            self._values["allowed_locations"] = allowed_locations
        if custom_event_data is not None:
            self._values["custom_event_data"] = custom_event_data
        if notification_target is not None:
            self._values["notification_target"] = notification_target
        if player_latency_policies is not None:
            self._values["player_latency_policies"] = player_latency_policies
        if priority_configuration is not None:
            self._values["priority_configuration"] = priority_configuration
        if timeout is not None:
            self._values["timeout"] = timeout

    @builtins.property
    def destinations(self) -> typing.List["IGameSessionQueueDestination"]:
        '''(experimental) A list of fleets and/or fleet alias that can be used to fulfill game session placement requests in the queue.

        Destinations are listed in order of placement preference.

        :stability: experimental
        '''
        result = self._values.get("destinations")
        assert result is not None, "Required property 'destinations' is missing"
        return typing.cast(typing.List["IGameSessionQueueDestination"], result)

    @builtins.property
    def game_session_queue_name(self) -> builtins.str:
        '''(experimental) Name of this gameSessionQueue.

        :stability: experimental
        '''
        result = self._values.get("game_session_queue_name")
        assert result is not None, "Required property 'game_session_queue_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def allowed_locations(self) -> typing.Optional[typing.List[builtins.str]]:
        '''(experimental) A list of locations where a queue is allowed to place new game sessions.

        Locations are specified in the form of AWS Region codes, such as ``us-west-2``.

        For queues that have multi-location fleets, you can use a filter configuration allow placement with some, but not all of these locations.

        :default: game sessions can be placed in any queue location

        :stability: experimental
        '''
        result = self._values.get("allowed_locations")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def custom_event_data(self) -> typing.Optional[builtins.str]:
        '''(experimental) Information to be added to all events that are related to this game session queue.

        :default: no customer event data

        :stability: experimental
        '''
        result = self._values.get("custom_event_data")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def notification_target(self) -> typing.Optional[_aws_cdk_aws_sns_ceddda9d.ITopic]:
        '''(experimental) An SNS topic is set up to receive game session placement notifications.

        :default: no notification

        :see: https://docs.aws.amazon.com/gamelift/latest/developerguide/queue-notification.html
        :stability: experimental
        '''
        result = self._values.get("notification_target")
        return typing.cast(typing.Optional[_aws_cdk_aws_sns_ceddda9d.ITopic], result)

    @builtins.property
    def player_latency_policies(
        self,
    ) -> typing.Optional[typing.List["PlayerLatencyPolicy"]]:
        '''(experimental) A set of policies that act as a sliding cap on player latency.

        FleetIQ works to deliver low latency for most players in a game session.
        These policies ensure that no individual player can be placed into a game with unreasonably high latency.
        Use multiple policies to gradually relax latency requirements a step at a time.
        Multiple policies are applied based on their maximum allowed latency, starting with the lowest value.

        :default: no player latency policy

        :stability: experimental
        '''
        result = self._values.get("player_latency_policies")
        return typing.cast(typing.Optional[typing.List["PlayerLatencyPolicy"]], result)

    @builtins.property
    def priority_configuration(self) -> typing.Optional["PriorityConfiguration"]:
        '''(experimental) Custom settings to use when prioritizing destinations and locations for game session placements.

        This configuration replaces the FleetIQ default prioritization process.

        Priority types that are not explicitly named will be automatically applied at the end of the prioritization process.

        :default: no priority configuration

        :stability: experimental
        '''
        result = self._values.get("priority_configuration")
        return typing.cast(typing.Optional["PriorityConfiguration"], result)

    @builtins.property
    def timeout(self) -> typing.Optional[_aws_cdk_ceddda9d.Duration]:
        '''(experimental) The maximum time, that a new game session placement request remains in the queue.

        When a request exceeds this time, the game session placement changes to a ``TIMED_OUT`` status.

        :default: 50 seconds

        :stability: experimental
        '''
        result = self._values.get("timeout")
        return typing.cast(typing.Optional[_aws_cdk_ceddda9d.Duration], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "GameSessionQueueProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.interface(jsii_type="@aws-cdk/aws-gamelift-alpha.IBuild")
class IBuild(
    _aws_cdk_ceddda9d.IResource,
    _aws_cdk_aws_iam_ceddda9d.IGrantable,
    typing_extensions.Protocol,
):
    '''(experimental) Your custom-built game server software that runs on GameLift and hosts game sessions for your players.

    A game build represents the set of files that run your game server on a particular operating system.
    You can have many different builds, such as for different flavors of your game.
    The game build must be integrated with the GameLift service.
    You upload game build files to the GameLift service in the Regions where you plan to set up fleets.

    :see: https://docs.aws.amazon.com/gamelift/latest/developerguide/gamelift-build-cli-uploading.html
    :stability: experimental
    '''

    @builtins.property
    @jsii.member(jsii_name="buildArn")
    def build_arn(self) -> builtins.str:
        '''(experimental) The ARN of the build.

        :stability: experimental
        :attribute: true
        '''
        ...

    @builtins.property
    @jsii.member(jsii_name="buildId")
    def build_id(self) -> builtins.str:
        '''(experimental) The Identifier of the build.

        :stability: experimental
        :attribute: true
        '''
        ...


class _IBuildProxy(
    jsii.proxy_for(_aws_cdk_ceddda9d.IResource), # type: ignore[misc]
    jsii.proxy_for(_aws_cdk_aws_iam_ceddda9d.IGrantable), # type: ignore[misc]
):
    '''(experimental) Your custom-built game server software that runs on GameLift and hosts game sessions for your players.

    A game build represents the set of files that run your game server on a particular operating system.
    You can have many different builds, such as for different flavors of your game.
    The game build must be integrated with the GameLift service.
    You upload game build files to the GameLift service in the Regions where you plan to set up fleets.

    :see: https://docs.aws.amazon.com/gamelift/latest/developerguide/gamelift-build-cli-uploading.html
    :stability: experimental
    '''

    __jsii_type__: typing.ClassVar[str] = "@aws-cdk/aws-gamelift-alpha.IBuild"

    @builtins.property
    @jsii.member(jsii_name="buildArn")
    def build_arn(self) -> builtins.str:
        '''(experimental) The ARN of the build.

        :stability: experimental
        :attribute: true
        '''
        return typing.cast(builtins.str, jsii.get(self, "buildArn"))

    @builtins.property
    @jsii.member(jsii_name="buildId")
    def build_id(self) -> builtins.str:
        '''(experimental) The Identifier of the build.

        :stability: experimental
        :attribute: true
        '''
        return typing.cast(builtins.str, jsii.get(self, "buildId"))

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, IBuild).__jsii_proxy_class__ = lambda : _IBuildProxy


@jsii.interface(jsii_type="@aws-cdk/aws-gamelift-alpha.IGameServerGroup")
class IGameServerGroup(
    _aws_cdk_ceddda9d.IResource,
    _aws_cdk_aws_iam_ceddda9d.IGrantable,
    typing_extensions.Protocol,
):
    '''(experimental) Represent a GameLift FleetIQ game server group.

    :stability: experimental
    '''

    @builtins.property
    @jsii.member(jsii_name="autoScalingGroupArn")
    def auto_scaling_group_arn(self) -> builtins.str:
        '''(experimental) The ARN of the generated AutoScaling group.

        :stability: experimental
        :attribute: true
        '''
        ...

    @builtins.property
    @jsii.member(jsii_name="gameServerGroupArn")
    def game_server_group_arn(self) -> builtins.str:
        '''(experimental) The ARN of the game server group.

        :stability: experimental
        :attribute: true
        '''
        ...

    @builtins.property
    @jsii.member(jsii_name="gameServerGroupName")
    def game_server_group_name(self) -> builtins.str:
        '''(experimental) The name of the game server group.

        :stability: experimental
        :attribute: true
        '''
        ...

    @jsii.member(jsii_name="grant")
    def grant(
        self,
        grantee: _aws_cdk_aws_iam_ceddda9d.IGrantable,
        *actions: builtins.str,
    ) -> _aws_cdk_aws_iam_ceddda9d.Grant:
        '''(experimental) Grant the ``grantee`` identity permissions to perform ``actions``.

        :param grantee: -
        :param actions: -

        :stability: experimental
        '''
        ...

    @jsii.member(jsii_name="metric")
    def metric(
        self,
        metric_name: builtins.str,
        *,
        account: typing.Optional[builtins.str] = None,
        color: typing.Optional[builtins.str] = None,
        dimensions_map: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        id: typing.Optional[builtins.str] = None,
        label: typing.Optional[builtins.str] = None,
        period: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        region: typing.Optional[builtins.str] = None,
        stack_account: typing.Optional[builtins.str] = None,
        stack_region: typing.Optional[builtins.str] = None,
        statistic: typing.Optional[builtins.str] = None,
        unit: typing.Optional[_aws_cdk_aws_cloudwatch_ceddda9d.Unit] = None,
        visible: typing.Optional[builtins.bool] = None,
    ) -> _aws_cdk_aws_cloudwatch_ceddda9d.Metric:
        '''(experimental) Return the given named metric for this fleet.

        :param metric_name: -
        :param account: Account which this metric comes from. Default: - Deployment account.
        :param color: The hex color code, prefixed with '#' (e.g. '#00ff00'), to use when this metric is rendered on a graph. The ``Color`` class has a set of standard colors that can be used here. Default: - Automatic color
        :param dimensions_map: Dimensions of the metric. Default: - No dimensions.
        :param id: Unique identifier for this metric when used in dashboard widgets. The id can be used as a variable to represent this metric in math expressions. Valid characters are letters, numbers, and underscore. The first character must be a lowercase letter. Default: - No ID
        :param label: Label for this metric when added to a Graph in a Dashboard. You can use `dynamic labels <https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/graph-dynamic-labels.html>`_ to show summary information about the entire displayed time series in the legend. For example, if you use:: [max: ${MAX}] MyMetric As the metric label, the maximum value in the visible range will be shown next to the time series name in the graph's legend. Default: - No label
        :param period: The period over which the specified statistic is applied. Default: Duration.minutes(5)
        :param region: Region which this metric comes from. Default: - Deployment region.
        :param stack_account: Account of the stack this metric is attached to. Default: - Deployment account.
        :param stack_region: Region of the stack this metric is attached to. Default: - Deployment region.
        :param statistic: What function to use for aggregating. Use the ``aws_cloudwatch.Stats`` helper class to construct valid input strings. Can be one of the following: - "Minimum" | "min" - "Maximum" | "max" - "Average" | "avg" - "Sum" | "sum" - "SampleCount | "n" - "pNN.NN" - "tmNN.NN" | "tm(NN.NN%:NN.NN%)" - "iqm" - "wmNN.NN" | "wm(NN.NN%:NN.NN%)" - "tcNN.NN" | "tc(NN.NN%:NN.NN%)" - "tsNN.NN" | "ts(NN.NN%:NN.NN%)" Default: Average
        :param unit: Unit used to filter the metric stream. Only refer to datums emitted to the metric stream with the given unit and ignore all others. Only useful when datums are being emitted to the same metric stream under different units. The default is to use all matric datums in the stream, regardless of unit, which is recommended in nearly all cases. CloudWatch does not honor this property for graphs. Default: - All metric datums in the given metric stream
        :param visible: Whether this metric should be visible in dashboard graphs. Setting this to false is useful when you want to hide raw metrics that are used in math expressions, and show only the expression results. Default: true

        :stability: experimental
        '''
        ...


class _IGameServerGroupProxy(
    jsii.proxy_for(_aws_cdk_ceddda9d.IResource), # type: ignore[misc]
    jsii.proxy_for(_aws_cdk_aws_iam_ceddda9d.IGrantable), # type: ignore[misc]
):
    '''(experimental) Represent a GameLift FleetIQ game server group.

    :stability: experimental
    '''

    __jsii_type__: typing.ClassVar[str] = "@aws-cdk/aws-gamelift-alpha.IGameServerGroup"

    @builtins.property
    @jsii.member(jsii_name="autoScalingGroupArn")
    def auto_scaling_group_arn(self) -> builtins.str:
        '''(experimental) The ARN of the generated AutoScaling group.

        :stability: experimental
        :attribute: true
        '''
        return typing.cast(builtins.str, jsii.get(self, "autoScalingGroupArn"))

    @builtins.property
    @jsii.member(jsii_name="gameServerGroupArn")
    def game_server_group_arn(self) -> builtins.str:
        '''(experimental) The ARN of the game server group.

        :stability: experimental
        :attribute: true
        '''
        return typing.cast(builtins.str, jsii.get(self, "gameServerGroupArn"))

    @builtins.property
    @jsii.member(jsii_name="gameServerGroupName")
    def game_server_group_name(self) -> builtins.str:
        '''(experimental) The name of the game server group.

        :stability: experimental
        :attribute: true
        '''
        return typing.cast(builtins.str, jsii.get(self, "gameServerGroupName"))

    @jsii.member(jsii_name="grant")
    def grant(
        self,
        grantee: _aws_cdk_aws_iam_ceddda9d.IGrantable,
        *actions: builtins.str,
    ) -> _aws_cdk_aws_iam_ceddda9d.Grant:
        '''(experimental) Grant the ``grantee`` identity permissions to perform ``actions``.

        :param grantee: -
        :param actions: -

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0b3232859da16b7aade55f24dcd15023d4567f8b71ec1a2c52f45e83a0e4d6e0)
            check_type(argname="argument grantee", value=grantee, expected_type=type_hints["grantee"])
            check_type(argname="argument actions", value=actions, expected_type=typing.Tuple[type_hints["actions"], ...]) # pyright: ignore [reportGeneralTypeIssues]
        return typing.cast(_aws_cdk_aws_iam_ceddda9d.Grant, jsii.invoke(self, "grant", [grantee, *actions]))

    @jsii.member(jsii_name="metric")
    def metric(
        self,
        metric_name: builtins.str,
        *,
        account: typing.Optional[builtins.str] = None,
        color: typing.Optional[builtins.str] = None,
        dimensions_map: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        id: typing.Optional[builtins.str] = None,
        label: typing.Optional[builtins.str] = None,
        period: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        region: typing.Optional[builtins.str] = None,
        stack_account: typing.Optional[builtins.str] = None,
        stack_region: typing.Optional[builtins.str] = None,
        statistic: typing.Optional[builtins.str] = None,
        unit: typing.Optional[_aws_cdk_aws_cloudwatch_ceddda9d.Unit] = None,
        visible: typing.Optional[builtins.bool] = None,
    ) -> _aws_cdk_aws_cloudwatch_ceddda9d.Metric:
        '''(experimental) Return the given named metric for this fleet.

        :param metric_name: -
        :param account: Account which this metric comes from. Default: - Deployment account.
        :param color: The hex color code, prefixed with '#' (e.g. '#00ff00'), to use when this metric is rendered on a graph. The ``Color`` class has a set of standard colors that can be used here. Default: - Automatic color
        :param dimensions_map: Dimensions of the metric. Default: - No dimensions.
        :param id: Unique identifier for this metric when used in dashboard widgets. The id can be used as a variable to represent this metric in math expressions. Valid characters are letters, numbers, and underscore. The first character must be a lowercase letter. Default: - No ID
        :param label: Label for this metric when added to a Graph in a Dashboard. You can use `dynamic labels <https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/graph-dynamic-labels.html>`_ to show summary information about the entire displayed time series in the legend. For example, if you use:: [max: ${MAX}] MyMetric As the metric label, the maximum value in the visible range will be shown next to the time series name in the graph's legend. Default: - No label
        :param period: The period over which the specified statistic is applied. Default: Duration.minutes(5)
        :param region: Region which this metric comes from. Default: - Deployment region.
        :param stack_account: Account of the stack this metric is attached to. Default: - Deployment account.
        :param stack_region: Region of the stack this metric is attached to. Default: - Deployment region.
        :param statistic: What function to use for aggregating. Use the ``aws_cloudwatch.Stats`` helper class to construct valid input strings. Can be one of the following: - "Minimum" | "min" - "Maximum" | "max" - "Average" | "avg" - "Sum" | "sum" - "SampleCount | "n" - "pNN.NN" - "tmNN.NN" | "tm(NN.NN%:NN.NN%)" - "iqm" - "wmNN.NN" | "wm(NN.NN%:NN.NN%)" - "tcNN.NN" | "tc(NN.NN%:NN.NN%)" - "tsNN.NN" | "ts(NN.NN%:NN.NN%)" Default: Average
        :param unit: Unit used to filter the metric stream. Only refer to datums emitted to the metric stream with the given unit and ignore all others. Only useful when datums are being emitted to the same metric stream under different units. The default is to use all matric datums in the stream, regardless of unit, which is recommended in nearly all cases. CloudWatch does not honor this property for graphs. Default: - All metric datums in the given metric stream
        :param visible: Whether this metric should be visible in dashboard graphs. Setting this to false is useful when you want to hide raw metrics that are used in math expressions, and show only the expression results. Default: true

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__eb2e31bcab4aa310be1c38dd2ab3f2b978168d82caac15a042b955b86628ef1b)
            check_type(argname="argument metric_name", value=metric_name, expected_type=type_hints["metric_name"])
        props = _aws_cdk_aws_cloudwatch_ceddda9d.MetricOptions(
            account=account,
            color=color,
            dimensions_map=dimensions_map,
            id=id,
            label=label,
            period=period,
            region=region,
            stack_account=stack_account,
            stack_region=stack_region,
            statistic=statistic,
            unit=unit,
            visible=visible,
        )

        return typing.cast(_aws_cdk_aws_cloudwatch_ceddda9d.Metric, jsii.invoke(self, "metric", [metric_name, props]))

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, IGameServerGroup).__jsii_proxy_class__ = lambda : _IGameServerGroupProxy


@jsii.interface(jsii_type="@aws-cdk/aws-gamelift-alpha.IGameSessionQueue")
class IGameSessionQueue(_aws_cdk_ceddda9d.IResource, typing_extensions.Protocol):
    '''(experimental) Represents a Gamelift GameSessionQueue for a Gamelift fleet destination.

    :stability: experimental
    '''

    @builtins.property
    @jsii.member(jsii_name="gameSessionQueueArn")
    def game_session_queue_arn(self) -> builtins.str:
        '''(experimental) The ARN of the gameSessionQueue.

        :stability: experimental
        :attribute: true
        '''
        ...

    @builtins.property
    @jsii.member(jsii_name="gameSessionQueueName")
    def game_session_queue_name(self) -> builtins.str:
        '''(experimental) The Name of the gameSessionQueue.

        :stability: experimental
        :attribute: true
        '''
        ...

    @jsii.member(jsii_name="metric")
    def metric(
        self,
        metric_name: builtins.str,
        *,
        account: typing.Optional[builtins.str] = None,
        color: typing.Optional[builtins.str] = None,
        dimensions_map: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        id: typing.Optional[builtins.str] = None,
        label: typing.Optional[builtins.str] = None,
        period: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        region: typing.Optional[builtins.str] = None,
        stack_account: typing.Optional[builtins.str] = None,
        stack_region: typing.Optional[builtins.str] = None,
        statistic: typing.Optional[builtins.str] = None,
        unit: typing.Optional[_aws_cdk_aws_cloudwatch_ceddda9d.Unit] = None,
        visible: typing.Optional[builtins.bool] = None,
    ) -> _aws_cdk_aws_cloudwatch_ceddda9d.Metric:
        '''(experimental) Return the given named metric for this fleet.

        :param metric_name: -
        :param account: Account which this metric comes from. Default: - Deployment account.
        :param color: The hex color code, prefixed with '#' (e.g. '#00ff00'), to use when this metric is rendered on a graph. The ``Color`` class has a set of standard colors that can be used here. Default: - Automatic color
        :param dimensions_map: Dimensions of the metric. Default: - No dimensions.
        :param id: Unique identifier for this metric when used in dashboard widgets. The id can be used as a variable to represent this metric in math expressions. Valid characters are letters, numbers, and underscore. The first character must be a lowercase letter. Default: - No ID
        :param label: Label for this metric when added to a Graph in a Dashboard. You can use `dynamic labels <https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/graph-dynamic-labels.html>`_ to show summary information about the entire displayed time series in the legend. For example, if you use:: [max: ${MAX}] MyMetric As the metric label, the maximum value in the visible range will be shown next to the time series name in the graph's legend. Default: - No label
        :param period: The period over which the specified statistic is applied. Default: Duration.minutes(5)
        :param region: Region which this metric comes from. Default: - Deployment region.
        :param stack_account: Account of the stack this metric is attached to. Default: - Deployment account.
        :param stack_region: Region of the stack this metric is attached to. Default: - Deployment region.
        :param statistic: What function to use for aggregating. Use the ``aws_cloudwatch.Stats`` helper class to construct valid input strings. Can be one of the following: - "Minimum" | "min" - "Maximum" | "max" - "Average" | "avg" - "Sum" | "sum" - "SampleCount | "n" - "pNN.NN" - "tmNN.NN" | "tm(NN.NN%:NN.NN%)" - "iqm" - "wmNN.NN" | "wm(NN.NN%:NN.NN%)" - "tcNN.NN" | "tc(NN.NN%:NN.NN%)" - "tsNN.NN" | "ts(NN.NN%:NN.NN%)" Default: Average
        :param unit: Unit used to filter the metric stream. Only refer to datums emitted to the metric stream with the given unit and ignore all others. Only useful when datums are being emitted to the same metric stream under different units. The default is to use all matric datums in the stream, regardless of unit, which is recommended in nearly all cases. CloudWatch does not honor this property for graphs. Default: - All metric datums in the given metric stream
        :param visible: Whether this metric should be visible in dashboard graphs. Setting this to false is useful when you want to hide raw metrics that are used in math expressions, and show only the expression results. Default: true

        :stability: experimental
        '''
        ...

    @jsii.member(jsii_name="metricAverageWaitTime")
    def metric_average_wait_time(
        self,
        *,
        account: typing.Optional[builtins.str] = None,
        color: typing.Optional[builtins.str] = None,
        dimensions_map: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        id: typing.Optional[builtins.str] = None,
        label: typing.Optional[builtins.str] = None,
        period: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        region: typing.Optional[builtins.str] = None,
        stack_account: typing.Optional[builtins.str] = None,
        stack_region: typing.Optional[builtins.str] = None,
        statistic: typing.Optional[builtins.str] = None,
        unit: typing.Optional[_aws_cdk_aws_cloudwatch_ceddda9d.Unit] = None,
        visible: typing.Optional[builtins.bool] = None,
    ) -> _aws_cdk_aws_cloudwatch_ceddda9d.Metric:
        '''(experimental) Average amount of time that game session placement requests in the queue with status PENDING have been waiting to be fulfilled.

        :param account: Account which this metric comes from. Default: - Deployment account.
        :param color: The hex color code, prefixed with '#' (e.g. '#00ff00'), to use when this metric is rendered on a graph. The ``Color`` class has a set of standard colors that can be used here. Default: - Automatic color
        :param dimensions_map: Dimensions of the metric. Default: - No dimensions.
        :param id: Unique identifier for this metric when used in dashboard widgets. The id can be used as a variable to represent this metric in math expressions. Valid characters are letters, numbers, and underscore. The first character must be a lowercase letter. Default: - No ID
        :param label: Label for this metric when added to a Graph in a Dashboard. You can use `dynamic labels <https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/graph-dynamic-labels.html>`_ to show summary information about the entire displayed time series in the legend. For example, if you use:: [max: ${MAX}] MyMetric As the metric label, the maximum value in the visible range will be shown next to the time series name in the graph's legend. Default: - No label
        :param period: The period over which the specified statistic is applied. Default: Duration.minutes(5)
        :param region: Region which this metric comes from. Default: - Deployment region.
        :param stack_account: Account of the stack this metric is attached to. Default: - Deployment account.
        :param stack_region: Region of the stack this metric is attached to. Default: - Deployment region.
        :param statistic: What function to use for aggregating. Use the ``aws_cloudwatch.Stats`` helper class to construct valid input strings. Can be one of the following: - "Minimum" | "min" - "Maximum" | "max" - "Average" | "avg" - "Sum" | "sum" - "SampleCount | "n" - "pNN.NN" - "tmNN.NN" | "tm(NN.NN%:NN.NN%)" - "iqm" - "wmNN.NN" | "wm(NN.NN%:NN.NN%)" - "tcNN.NN" | "tc(NN.NN%:NN.NN%)" - "tsNN.NN" | "ts(NN.NN%:NN.NN%)" Default: Average
        :param unit: Unit used to filter the metric stream. Only refer to datums emitted to the metric stream with the given unit and ignore all others. Only useful when datums are being emitted to the same metric stream under different units. The default is to use all matric datums in the stream, regardless of unit, which is recommended in nearly all cases. CloudWatch does not honor this property for graphs. Default: - All metric datums in the given metric stream
        :param visible: Whether this metric should be visible in dashboard graphs. Setting this to false is useful when you want to hide raw metrics that are used in math expressions, and show only the expression results. Default: true

        :stability: experimental
        '''
        ...

    @jsii.member(jsii_name="metricPlacementsCanceled")
    def metric_placements_canceled(
        self,
        *,
        account: typing.Optional[builtins.str] = None,
        color: typing.Optional[builtins.str] = None,
        dimensions_map: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        id: typing.Optional[builtins.str] = None,
        label: typing.Optional[builtins.str] = None,
        period: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        region: typing.Optional[builtins.str] = None,
        stack_account: typing.Optional[builtins.str] = None,
        stack_region: typing.Optional[builtins.str] = None,
        statistic: typing.Optional[builtins.str] = None,
        unit: typing.Optional[_aws_cdk_aws_cloudwatch_ceddda9d.Unit] = None,
        visible: typing.Optional[builtins.bool] = None,
    ) -> _aws_cdk_aws_cloudwatch_ceddda9d.Metric:
        '''(experimental) Game session placement requests that were canceled before timing out since the last report.

        :param account: Account which this metric comes from. Default: - Deployment account.
        :param color: The hex color code, prefixed with '#' (e.g. '#00ff00'), to use when this metric is rendered on a graph. The ``Color`` class has a set of standard colors that can be used here. Default: - Automatic color
        :param dimensions_map: Dimensions of the metric. Default: - No dimensions.
        :param id: Unique identifier for this metric when used in dashboard widgets. The id can be used as a variable to represent this metric in math expressions. Valid characters are letters, numbers, and underscore. The first character must be a lowercase letter. Default: - No ID
        :param label: Label for this metric when added to a Graph in a Dashboard. You can use `dynamic labels <https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/graph-dynamic-labels.html>`_ to show summary information about the entire displayed time series in the legend. For example, if you use:: [max: ${MAX}] MyMetric As the metric label, the maximum value in the visible range will be shown next to the time series name in the graph's legend. Default: - No label
        :param period: The period over which the specified statistic is applied. Default: Duration.minutes(5)
        :param region: Region which this metric comes from. Default: - Deployment region.
        :param stack_account: Account of the stack this metric is attached to. Default: - Deployment account.
        :param stack_region: Region of the stack this metric is attached to. Default: - Deployment region.
        :param statistic: What function to use for aggregating. Use the ``aws_cloudwatch.Stats`` helper class to construct valid input strings. Can be one of the following: - "Minimum" | "min" - "Maximum" | "max" - "Average" | "avg" - "Sum" | "sum" - "SampleCount | "n" - "pNN.NN" - "tmNN.NN" | "tm(NN.NN%:NN.NN%)" - "iqm" - "wmNN.NN" | "wm(NN.NN%:NN.NN%)" - "tcNN.NN" | "tc(NN.NN%:NN.NN%)" - "tsNN.NN" | "ts(NN.NN%:NN.NN%)" Default: Average
        :param unit: Unit used to filter the metric stream. Only refer to datums emitted to the metric stream with the given unit and ignore all others. Only useful when datums are being emitted to the same metric stream under different units. The default is to use all matric datums in the stream, regardless of unit, which is recommended in nearly all cases. CloudWatch does not honor this property for graphs. Default: - All metric datums in the given metric stream
        :param visible: Whether this metric should be visible in dashboard graphs. Setting this to false is useful when you want to hide raw metrics that are used in math expressions, and show only the expression results. Default: true

        :stability: experimental
        '''
        ...

    @jsii.member(jsii_name="metricPlacementsFailed")
    def metric_placements_failed(
        self,
        *,
        account: typing.Optional[builtins.str] = None,
        color: typing.Optional[builtins.str] = None,
        dimensions_map: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        id: typing.Optional[builtins.str] = None,
        label: typing.Optional[builtins.str] = None,
        period: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        region: typing.Optional[builtins.str] = None,
        stack_account: typing.Optional[builtins.str] = None,
        stack_region: typing.Optional[builtins.str] = None,
        statistic: typing.Optional[builtins.str] = None,
        unit: typing.Optional[_aws_cdk_aws_cloudwatch_ceddda9d.Unit] = None,
        visible: typing.Optional[builtins.bool] = None,
    ) -> _aws_cdk_aws_cloudwatch_ceddda9d.Metric:
        '''(experimental) Game session placement requests that failed for any reason since the last report.

        :param account: Account which this metric comes from. Default: - Deployment account.
        :param color: The hex color code, prefixed with '#' (e.g. '#00ff00'), to use when this metric is rendered on a graph. The ``Color`` class has a set of standard colors that can be used here. Default: - Automatic color
        :param dimensions_map: Dimensions of the metric. Default: - No dimensions.
        :param id: Unique identifier for this metric when used in dashboard widgets. The id can be used as a variable to represent this metric in math expressions. Valid characters are letters, numbers, and underscore. The first character must be a lowercase letter. Default: - No ID
        :param label: Label for this metric when added to a Graph in a Dashboard. You can use `dynamic labels <https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/graph-dynamic-labels.html>`_ to show summary information about the entire displayed time series in the legend. For example, if you use:: [max: ${MAX}] MyMetric As the metric label, the maximum value in the visible range will be shown next to the time series name in the graph's legend. Default: - No label
        :param period: The period over which the specified statistic is applied. Default: Duration.minutes(5)
        :param region: Region which this metric comes from. Default: - Deployment region.
        :param stack_account: Account of the stack this metric is attached to. Default: - Deployment account.
        :param stack_region: Region of the stack this metric is attached to. Default: - Deployment region.
        :param statistic: What function to use for aggregating. Use the ``aws_cloudwatch.Stats`` helper class to construct valid input strings. Can be one of the following: - "Minimum" | "min" - "Maximum" | "max" - "Average" | "avg" - "Sum" | "sum" - "SampleCount | "n" - "pNN.NN" - "tmNN.NN" | "tm(NN.NN%:NN.NN%)" - "iqm" - "wmNN.NN" | "wm(NN.NN%:NN.NN%)" - "tcNN.NN" | "tc(NN.NN%:NN.NN%)" - "tsNN.NN" | "ts(NN.NN%:NN.NN%)" Default: Average
        :param unit: Unit used to filter the metric stream. Only refer to datums emitted to the metric stream with the given unit and ignore all others. Only useful when datums are being emitted to the same metric stream under different units. The default is to use all matric datums in the stream, regardless of unit, which is recommended in nearly all cases. CloudWatch does not honor this property for graphs. Default: - All metric datums in the given metric stream
        :param visible: Whether this metric should be visible in dashboard graphs. Setting this to false is useful when you want to hide raw metrics that are used in math expressions, and show only the expression results. Default: true

        :stability: experimental
        '''
        ...

    @jsii.member(jsii_name="metricPlacementsStarted")
    def metric_placements_started(
        self,
        *,
        account: typing.Optional[builtins.str] = None,
        color: typing.Optional[builtins.str] = None,
        dimensions_map: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        id: typing.Optional[builtins.str] = None,
        label: typing.Optional[builtins.str] = None,
        period: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        region: typing.Optional[builtins.str] = None,
        stack_account: typing.Optional[builtins.str] = None,
        stack_region: typing.Optional[builtins.str] = None,
        statistic: typing.Optional[builtins.str] = None,
        unit: typing.Optional[_aws_cdk_aws_cloudwatch_ceddda9d.Unit] = None,
        visible: typing.Optional[builtins.bool] = None,
    ) -> _aws_cdk_aws_cloudwatch_ceddda9d.Metric:
        '''(experimental) New game session placement requests that were added to the queue since the last report.

        :param account: Account which this metric comes from. Default: - Deployment account.
        :param color: The hex color code, prefixed with '#' (e.g. '#00ff00'), to use when this metric is rendered on a graph. The ``Color`` class has a set of standard colors that can be used here. Default: - Automatic color
        :param dimensions_map: Dimensions of the metric. Default: - No dimensions.
        :param id: Unique identifier for this metric when used in dashboard widgets. The id can be used as a variable to represent this metric in math expressions. Valid characters are letters, numbers, and underscore. The first character must be a lowercase letter. Default: - No ID
        :param label: Label for this metric when added to a Graph in a Dashboard. You can use `dynamic labels <https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/graph-dynamic-labels.html>`_ to show summary information about the entire displayed time series in the legend. For example, if you use:: [max: ${MAX}] MyMetric As the metric label, the maximum value in the visible range will be shown next to the time series name in the graph's legend. Default: - No label
        :param period: The period over which the specified statistic is applied. Default: Duration.minutes(5)
        :param region: Region which this metric comes from. Default: - Deployment region.
        :param stack_account: Account of the stack this metric is attached to. Default: - Deployment account.
        :param stack_region: Region of the stack this metric is attached to. Default: - Deployment region.
        :param statistic: What function to use for aggregating. Use the ``aws_cloudwatch.Stats`` helper class to construct valid input strings. Can be one of the following: - "Minimum" | "min" - "Maximum" | "max" - "Average" | "avg" - "Sum" | "sum" - "SampleCount | "n" - "pNN.NN" - "tmNN.NN" | "tm(NN.NN%:NN.NN%)" - "iqm" - "wmNN.NN" | "wm(NN.NN%:NN.NN%)" - "tcNN.NN" | "tc(NN.NN%:NN.NN%)" - "tsNN.NN" | "ts(NN.NN%:NN.NN%)" Default: Average
        :param unit: Unit used to filter the metric stream. Only refer to datums emitted to the metric stream with the given unit and ignore all others. Only useful when datums are being emitted to the same metric stream under different units. The default is to use all matric datums in the stream, regardless of unit, which is recommended in nearly all cases. CloudWatch does not honor this property for graphs. Default: - All metric datums in the given metric stream
        :param visible: Whether this metric should be visible in dashboard graphs. Setting this to false is useful when you want to hide raw metrics that are used in math expressions, and show only the expression results. Default: true

        :stability: experimental
        '''
        ...

    @jsii.member(jsii_name="metricPlacementsSucceeded")
    def metric_placements_succeeded(
        self,
        *,
        account: typing.Optional[builtins.str] = None,
        color: typing.Optional[builtins.str] = None,
        dimensions_map: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        id: typing.Optional[builtins.str] = None,
        label: typing.Optional[builtins.str] = None,
        period: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        region: typing.Optional[builtins.str] = None,
        stack_account: typing.Optional[builtins.str] = None,
        stack_region: typing.Optional[builtins.str] = None,
        statistic: typing.Optional[builtins.str] = None,
        unit: typing.Optional[_aws_cdk_aws_cloudwatch_ceddda9d.Unit] = None,
        visible: typing.Optional[builtins.bool] = None,
    ) -> _aws_cdk_aws_cloudwatch_ceddda9d.Metric:
        '''(experimental) Game session placement requests that resulted in a new game session since the last report.

        :param account: Account which this metric comes from. Default: - Deployment account.
        :param color: The hex color code, prefixed with '#' (e.g. '#00ff00'), to use when this metric is rendered on a graph. The ``Color`` class has a set of standard colors that can be used here. Default: - Automatic color
        :param dimensions_map: Dimensions of the metric. Default: - No dimensions.
        :param id: Unique identifier for this metric when used in dashboard widgets. The id can be used as a variable to represent this metric in math expressions. Valid characters are letters, numbers, and underscore. The first character must be a lowercase letter. Default: - No ID
        :param label: Label for this metric when added to a Graph in a Dashboard. You can use `dynamic labels <https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/graph-dynamic-labels.html>`_ to show summary information about the entire displayed time series in the legend. For example, if you use:: [max: ${MAX}] MyMetric As the metric label, the maximum value in the visible range will be shown next to the time series name in the graph's legend. Default: - No label
        :param period: The period over which the specified statistic is applied. Default: Duration.minutes(5)
        :param region: Region which this metric comes from. Default: - Deployment region.
        :param stack_account: Account of the stack this metric is attached to. Default: - Deployment account.
        :param stack_region: Region of the stack this metric is attached to. Default: - Deployment region.
        :param statistic: What function to use for aggregating. Use the ``aws_cloudwatch.Stats`` helper class to construct valid input strings. Can be one of the following: - "Minimum" | "min" - "Maximum" | "max" - "Average" | "avg" - "Sum" | "sum" - "SampleCount | "n" - "pNN.NN" - "tmNN.NN" | "tm(NN.NN%:NN.NN%)" - "iqm" - "wmNN.NN" | "wm(NN.NN%:NN.NN%)" - "tcNN.NN" | "tc(NN.NN%:NN.NN%)" - "tsNN.NN" | "ts(NN.NN%:NN.NN%)" Default: Average
        :param unit: Unit used to filter the metric stream. Only refer to datums emitted to the metric stream with the given unit and ignore all others. Only useful when datums are being emitted to the same metric stream under different units. The default is to use all matric datums in the stream, regardless of unit, which is recommended in nearly all cases. CloudWatch does not honor this property for graphs. Default: - All metric datums in the given metric stream
        :param visible: Whether this metric should be visible in dashboard graphs. Setting this to false is useful when you want to hide raw metrics that are used in math expressions, and show only the expression results. Default: true

        :stability: experimental
        '''
        ...

    @jsii.member(jsii_name="metricPlacementsTimedOut")
    def metric_placements_timed_out(
        self,
        *,
        account: typing.Optional[builtins.str] = None,
        color: typing.Optional[builtins.str] = None,
        dimensions_map: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        id: typing.Optional[builtins.str] = None,
        label: typing.Optional[builtins.str] = None,
        period: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        region: typing.Optional[builtins.str] = None,
        stack_account: typing.Optional[builtins.str] = None,
        stack_region: typing.Optional[builtins.str] = None,
        statistic: typing.Optional[builtins.str] = None,
        unit: typing.Optional[_aws_cdk_aws_cloudwatch_ceddda9d.Unit] = None,
        visible: typing.Optional[builtins.bool] = None,
    ) -> _aws_cdk_aws_cloudwatch_ceddda9d.Metric:
        '''(experimental) Game session placement requests that reached the queue's timeout limit without being fulfilled since the last report.

        :param account: Account which this metric comes from. Default: - Deployment account.
        :param color: The hex color code, prefixed with '#' (e.g. '#00ff00'), to use when this metric is rendered on a graph. The ``Color`` class has a set of standard colors that can be used here. Default: - Automatic color
        :param dimensions_map: Dimensions of the metric. Default: - No dimensions.
        :param id: Unique identifier for this metric when used in dashboard widgets. The id can be used as a variable to represent this metric in math expressions. Valid characters are letters, numbers, and underscore. The first character must be a lowercase letter. Default: - No ID
        :param label: Label for this metric when added to a Graph in a Dashboard. You can use `dynamic labels <https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/graph-dynamic-labels.html>`_ to show summary information about the entire displayed time series in the legend. For example, if you use:: [max: ${MAX}] MyMetric As the metric label, the maximum value in the visible range will be shown next to the time series name in the graph's legend. Default: - No label
        :param period: The period over which the specified statistic is applied. Default: Duration.minutes(5)
        :param region: Region which this metric comes from. Default: - Deployment region.
        :param stack_account: Account of the stack this metric is attached to. Default: - Deployment account.
        :param stack_region: Region of the stack this metric is attached to. Default: - Deployment region.
        :param statistic: What function to use for aggregating. Use the ``aws_cloudwatch.Stats`` helper class to construct valid input strings. Can be one of the following: - "Minimum" | "min" - "Maximum" | "max" - "Average" | "avg" - "Sum" | "sum" - "SampleCount | "n" - "pNN.NN" - "tmNN.NN" | "tm(NN.NN%:NN.NN%)" - "iqm" - "wmNN.NN" | "wm(NN.NN%:NN.NN%)" - "tcNN.NN" | "tc(NN.NN%:NN.NN%)" - "tsNN.NN" | "ts(NN.NN%:NN.NN%)" Default: Average
        :param unit: Unit used to filter the metric stream. Only refer to datums emitted to the metric stream with the given unit and ignore all others. Only useful when datums are being emitted to the same metric stream under different units. The default is to use all matric datums in the stream, regardless of unit, which is recommended in nearly all cases. CloudWatch does not honor this property for graphs. Default: - All metric datums in the given metric stream
        :param visible: Whether this metric should be visible in dashboard graphs. Setting this to false is useful when you want to hide raw metrics that are used in math expressions, and show only the expression results. Default: true

        :stability: experimental
        '''
        ...


class _IGameSessionQueueProxy(
    jsii.proxy_for(_aws_cdk_ceddda9d.IResource), # type: ignore[misc]
):
    '''(experimental) Represents a Gamelift GameSessionQueue for a Gamelift fleet destination.

    :stability: experimental
    '''

    __jsii_type__: typing.ClassVar[str] = "@aws-cdk/aws-gamelift-alpha.IGameSessionQueue"

    @builtins.property
    @jsii.member(jsii_name="gameSessionQueueArn")
    def game_session_queue_arn(self) -> builtins.str:
        '''(experimental) The ARN of the gameSessionQueue.

        :stability: experimental
        :attribute: true
        '''
        return typing.cast(builtins.str, jsii.get(self, "gameSessionQueueArn"))

    @builtins.property
    @jsii.member(jsii_name="gameSessionQueueName")
    def game_session_queue_name(self) -> builtins.str:
        '''(experimental) The Name of the gameSessionQueue.

        :stability: experimental
        :attribute: true
        '''
        return typing.cast(builtins.str, jsii.get(self, "gameSessionQueueName"))

    @jsii.member(jsii_name="metric")
    def metric(
        self,
        metric_name: builtins.str,
        *,
        account: typing.Optional[builtins.str] = None,
        color: typing.Optional[builtins.str] = None,
        dimensions_map: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        id: typing.Optional[builtins.str] = None,
        label: typing.Optional[builtins.str] = None,
        period: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        region: typing.Optional[builtins.str] = None,
        stack_account: typing.Optional[builtins.str] = None,
        stack_region: typing.Optional[builtins.str] = None,
        statistic: typing.Optional[builtins.str] = None,
        unit: typing.Optional[_aws_cdk_aws_cloudwatch_ceddda9d.Unit] = None,
        visible: typing.Optional[builtins.bool] = None,
    ) -> _aws_cdk_aws_cloudwatch_ceddda9d.Metric:
        '''(experimental) Return the given named metric for this fleet.

        :param metric_name: -
        :param account: Account which this metric comes from. Default: - Deployment account.
        :param color: The hex color code, prefixed with '#' (e.g. '#00ff00'), to use when this metric is rendered on a graph. The ``Color`` class has a set of standard colors that can be used here. Default: - Automatic color
        :param dimensions_map: Dimensions of the metric. Default: - No dimensions.
        :param id: Unique identifier for this metric when used in dashboard widgets. The id can be used as a variable to represent this metric in math expressions. Valid characters are letters, numbers, and underscore. The first character must be a lowercase letter. Default: - No ID
        :param label: Label for this metric when added to a Graph in a Dashboard. You can use `dynamic labels <https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/graph-dynamic-labels.html>`_ to show summary information about the entire displayed time series in the legend. For example, if you use:: [max: ${MAX}] MyMetric As the metric label, the maximum value in the visible range will be shown next to the time series name in the graph's legend. Default: - No label
        :param period: The period over which the specified statistic is applied. Default: Duration.minutes(5)
        :param region: Region which this metric comes from. Default: - Deployment region.
        :param stack_account: Account of the stack this metric is attached to. Default: - Deployment account.
        :param stack_region: Region of the stack this metric is attached to. Default: - Deployment region.
        :param statistic: What function to use for aggregating. Use the ``aws_cloudwatch.Stats`` helper class to construct valid input strings. Can be one of the following: - "Minimum" | "min" - "Maximum" | "max" - "Average" | "avg" - "Sum" | "sum" - "SampleCount | "n" - "pNN.NN" - "tmNN.NN" | "tm(NN.NN%:NN.NN%)" - "iqm" - "wmNN.NN" | "wm(NN.NN%:NN.NN%)" - "tcNN.NN" | "tc(NN.NN%:NN.NN%)" - "tsNN.NN" | "ts(NN.NN%:NN.NN%)" Default: Average
        :param unit: Unit used to filter the metric stream. Only refer to datums emitted to the metric stream with the given unit and ignore all others. Only useful when datums are being emitted to the same metric stream under different units. The default is to use all matric datums in the stream, regardless of unit, which is recommended in nearly all cases. CloudWatch does not honor this property for graphs. Default: - All metric datums in the given metric stream
        :param visible: Whether this metric should be visible in dashboard graphs. Setting this to false is useful when you want to hide raw metrics that are used in math expressions, and show only the expression results. Default: true

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f6cb0fd1e45ac1f577cf83574c1b14669b35aff1cfbe39ce2729783223f80f7a)
            check_type(argname="argument metric_name", value=metric_name, expected_type=type_hints["metric_name"])
        props = _aws_cdk_aws_cloudwatch_ceddda9d.MetricOptions(
            account=account,
            color=color,
            dimensions_map=dimensions_map,
            id=id,
            label=label,
            period=period,
            region=region,
            stack_account=stack_account,
            stack_region=stack_region,
            statistic=statistic,
            unit=unit,
            visible=visible,
        )

        return typing.cast(_aws_cdk_aws_cloudwatch_ceddda9d.Metric, jsii.invoke(self, "metric", [metric_name, props]))

    @jsii.member(jsii_name="metricAverageWaitTime")
    def metric_average_wait_time(
        self,
        *,
        account: typing.Optional[builtins.str] = None,
        color: typing.Optional[builtins.str] = None,
        dimensions_map: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        id: typing.Optional[builtins.str] = None,
        label: typing.Optional[builtins.str] = None,
        period: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        region: typing.Optional[builtins.str] = None,
        stack_account: typing.Optional[builtins.str] = None,
        stack_region: typing.Optional[builtins.str] = None,
        statistic: typing.Optional[builtins.str] = None,
        unit: typing.Optional[_aws_cdk_aws_cloudwatch_ceddda9d.Unit] = None,
        visible: typing.Optional[builtins.bool] = None,
    ) -> _aws_cdk_aws_cloudwatch_ceddda9d.Metric:
        '''(experimental) Average amount of time that game session placement requests in the queue with status PENDING have been waiting to be fulfilled.

        :param account: Account which this metric comes from. Default: - Deployment account.
        :param color: The hex color code, prefixed with '#' (e.g. '#00ff00'), to use when this metric is rendered on a graph. The ``Color`` class has a set of standard colors that can be used here. Default: - Automatic color
        :param dimensions_map: Dimensions of the metric. Default: - No dimensions.
        :param id: Unique identifier for this metric when used in dashboard widgets. The id can be used as a variable to represent this metric in math expressions. Valid characters are letters, numbers, and underscore. The first character must be a lowercase letter. Default: - No ID
        :param label: Label for this metric when added to a Graph in a Dashboard. You can use `dynamic labels <https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/graph-dynamic-labels.html>`_ to show summary information about the entire displayed time series in the legend. For example, if you use:: [max: ${MAX}] MyMetric As the metric label, the maximum value in the visible range will be shown next to the time series name in the graph's legend. Default: - No label
        :param period: The period over which the specified statistic is applied. Default: Duration.minutes(5)
        :param region: Region which this metric comes from. Default: - Deployment region.
        :param stack_account: Account of the stack this metric is attached to. Default: - Deployment account.
        :param stack_region: Region of the stack this metric is attached to. Default: - Deployment region.
        :param statistic: What function to use for aggregating. Use the ``aws_cloudwatch.Stats`` helper class to construct valid input strings. Can be one of the following: - "Minimum" | "min" - "Maximum" | "max" - "Average" | "avg" - "Sum" | "sum" - "SampleCount | "n" - "pNN.NN" - "tmNN.NN" | "tm(NN.NN%:NN.NN%)" - "iqm" - "wmNN.NN" | "wm(NN.NN%:NN.NN%)" - "tcNN.NN" | "tc(NN.NN%:NN.NN%)" - "tsNN.NN" | "ts(NN.NN%:NN.NN%)" Default: Average
        :param unit: Unit used to filter the metric stream. Only refer to datums emitted to the metric stream with the given unit and ignore all others. Only useful when datums are being emitted to the same metric stream under different units. The default is to use all matric datums in the stream, regardless of unit, which is recommended in nearly all cases. CloudWatch does not honor this property for graphs. Default: - All metric datums in the given metric stream
        :param visible: Whether this metric should be visible in dashboard graphs. Setting this to false is useful when you want to hide raw metrics that are used in math expressions, and show only the expression results. Default: true

        :stability: experimental
        '''
        props = _aws_cdk_aws_cloudwatch_ceddda9d.MetricOptions(
            account=account,
            color=color,
            dimensions_map=dimensions_map,
            id=id,
            label=label,
            period=period,
            region=region,
            stack_account=stack_account,
            stack_region=stack_region,
            statistic=statistic,
            unit=unit,
            visible=visible,
        )

        return typing.cast(_aws_cdk_aws_cloudwatch_ceddda9d.Metric, jsii.invoke(self, "metricAverageWaitTime", [props]))

    @jsii.member(jsii_name="metricPlacementsCanceled")
    def metric_placements_canceled(
        self,
        *,
        account: typing.Optional[builtins.str] = None,
        color: typing.Optional[builtins.str] = None,
        dimensions_map: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        id: typing.Optional[builtins.str] = None,
        label: typing.Optional[builtins.str] = None,
        period: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        region: typing.Optional[builtins.str] = None,
        stack_account: typing.Optional[builtins.str] = None,
        stack_region: typing.Optional[builtins.str] = None,
        statistic: typing.Optional[builtins.str] = None,
        unit: typing.Optional[_aws_cdk_aws_cloudwatch_ceddda9d.Unit] = None,
        visible: typing.Optional[builtins.bool] = None,
    ) -> _aws_cdk_aws_cloudwatch_ceddda9d.Metric:
        '''(experimental) Game session placement requests that were canceled before timing out since the last report.

        :param account: Account which this metric comes from. Default: - Deployment account.
        :param color: The hex color code, prefixed with '#' (e.g. '#00ff00'), to use when this metric is rendered on a graph. The ``Color`` class has a set of standard colors that can be used here. Default: - Automatic color
        :param dimensions_map: Dimensions of the metric. Default: - No dimensions.
        :param id: Unique identifier for this metric when used in dashboard widgets. The id can be used as a variable to represent this metric in math expressions. Valid characters are letters, numbers, and underscore. The first character must be a lowercase letter. Default: - No ID
        :param label: Label for this metric when added to a Graph in a Dashboard. You can use `dynamic labels <https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/graph-dynamic-labels.html>`_ to show summary information about the entire displayed time series in the legend. For example, if you use:: [max: ${MAX}] MyMetric As the metric label, the maximum value in the visible range will be shown next to the time series name in the graph's legend. Default: - No label
        :param period: The period over which the specified statistic is applied. Default: Duration.minutes(5)
        :param region: Region which this metric comes from. Default: - Deployment region.
        :param stack_account: Account of the stack this metric is attached to. Default: - Deployment account.
        :param stack_region: Region of the stack this metric is attached to. Default: - Deployment region.
        :param statistic: What function to use for aggregating. Use the ``aws_cloudwatch.Stats`` helper class to construct valid input strings. Can be one of the following: - "Minimum" | "min" - "Maximum" | "max" - "Average" | "avg" - "Sum" | "sum" - "SampleCount | "n" - "pNN.NN" - "tmNN.NN" | "tm(NN.NN%:NN.NN%)" - "iqm" - "wmNN.NN" | "wm(NN.NN%:NN.NN%)" - "tcNN.NN" | "tc(NN.NN%:NN.NN%)" - "tsNN.NN" | "ts(NN.NN%:NN.NN%)" Default: Average
        :param unit: Unit used to filter the metric stream. Only refer to datums emitted to the metric stream with the given unit and ignore all others. Only useful when datums are being emitted to the same metric stream under different units. The default is to use all matric datums in the stream, regardless of unit, which is recommended in nearly all cases. CloudWatch does not honor this property for graphs. Default: - All metric datums in the given metric stream
        :param visible: Whether this metric should be visible in dashboard graphs. Setting this to false is useful when you want to hide raw metrics that are used in math expressions, and show only the expression results. Default: true

        :stability: experimental
        '''
        props = _aws_cdk_aws_cloudwatch_ceddda9d.MetricOptions(
            account=account,
            color=color,
            dimensions_map=dimensions_map,
            id=id,
            label=label,
            period=period,
            region=region,
            stack_account=stack_account,
            stack_region=stack_region,
            statistic=statistic,
            unit=unit,
            visible=visible,
        )

        return typing.cast(_aws_cdk_aws_cloudwatch_ceddda9d.Metric, jsii.invoke(self, "metricPlacementsCanceled", [props]))

    @jsii.member(jsii_name="metricPlacementsFailed")
    def metric_placements_failed(
        self,
        *,
        account: typing.Optional[builtins.str] = None,
        color: typing.Optional[builtins.str] = None,
        dimensions_map: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        id: typing.Optional[builtins.str] = None,
        label: typing.Optional[builtins.str] = None,
        period: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        region: typing.Optional[builtins.str] = None,
        stack_account: typing.Optional[builtins.str] = None,
        stack_region: typing.Optional[builtins.str] = None,
        statistic: typing.Optional[builtins.str] = None,
        unit: typing.Optional[_aws_cdk_aws_cloudwatch_ceddda9d.Unit] = None,
        visible: typing.Optional[builtins.bool] = None,
    ) -> _aws_cdk_aws_cloudwatch_ceddda9d.Metric:
        '''(experimental) Game session placement requests that failed for any reason since the last report.

        :param account: Account which this metric comes from. Default: - Deployment account.
        :param color: The hex color code, prefixed with '#' (e.g. '#00ff00'), to use when this metric is rendered on a graph. The ``Color`` class has a set of standard colors that can be used here. Default: - Automatic color
        :param dimensions_map: Dimensions of the metric. Default: - No dimensions.
        :param id: Unique identifier for this metric when used in dashboard widgets. The id can be used as a variable to represent this metric in math expressions. Valid characters are letters, numbers, and underscore. The first character must be a lowercase letter. Default: - No ID
        :param label: Label for this metric when added to a Graph in a Dashboard. You can use `dynamic labels <https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/graph-dynamic-labels.html>`_ to show summary information about the entire displayed time series in the legend. For example, if you use:: [max: ${MAX}] MyMetric As the metric label, the maximum value in the visible range will be shown next to the time series name in the graph's legend. Default: - No label
        :param period: The period over which the specified statistic is applied. Default: Duration.minutes(5)
        :param region: Region which this metric comes from. Default: - Deployment region.
        :param stack_account: Account of the stack this metric is attached to. Default: - Deployment account.
        :param stack_region: Region of the stack this metric is attached to. Default: - Deployment region.
        :param statistic: What function to use for aggregating. Use the ``aws_cloudwatch.Stats`` helper class to construct valid input strings. Can be one of the following: - "Minimum" | "min" - "Maximum" | "max" - "Average" | "avg" - "Sum" | "sum" - "SampleCount | "n" - "pNN.NN" - "tmNN.NN" | "tm(NN.NN%:NN.NN%)" - "iqm" - "wmNN.NN" | "wm(NN.NN%:NN.NN%)" - "tcNN.NN" | "tc(NN.NN%:NN.NN%)" - "tsNN.NN" | "ts(NN.NN%:NN.NN%)" Default: Average
        :param unit: Unit used to filter the metric stream. Only refer to datums emitted to the metric stream with the given unit and ignore all others. Only useful when datums are being emitted to the same metric stream under different units. The default is to use all matric datums in the stream, regardless of unit, which is recommended in nearly all cases. CloudWatch does not honor this property for graphs. Default: - All metric datums in the given metric stream
        :param visible: Whether this metric should be visible in dashboard graphs. Setting this to false is useful when you want to hide raw metrics that are used in math expressions, and show only the expression results. Default: true

        :stability: experimental
        '''
        props = _aws_cdk_aws_cloudwatch_ceddda9d.MetricOptions(
            account=account,
            color=color,
            dimensions_map=dimensions_map,
            id=id,
            label=label,
            period=period,
            region=region,
            stack_account=stack_account,
            stack_region=stack_region,
            statistic=statistic,
            unit=unit,
            visible=visible,
        )

        return typing.cast(_aws_cdk_aws_cloudwatch_ceddda9d.Metric, jsii.invoke(self, "metricPlacementsFailed", [props]))

    @jsii.member(jsii_name="metricPlacementsStarted")
    def metric_placements_started(
        self,
        *,
        account: typing.Optional[builtins.str] = None,
        color: typing.Optional[builtins.str] = None,
        dimensions_map: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        id: typing.Optional[builtins.str] = None,
        label: typing.Optional[builtins.str] = None,
        period: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        region: typing.Optional[builtins.str] = None,
        stack_account: typing.Optional[builtins.str] = None,
        stack_region: typing.Optional[builtins.str] = None,
        statistic: typing.Optional[builtins.str] = None,
        unit: typing.Optional[_aws_cdk_aws_cloudwatch_ceddda9d.Unit] = None,
        visible: typing.Optional[builtins.bool] = None,
    ) -> _aws_cdk_aws_cloudwatch_ceddda9d.Metric:
        '''(experimental) New game session placement requests that were added to the queue since the last report.

        :param account: Account which this metric comes from. Default: - Deployment account.
        :param color: The hex color code, prefixed with '#' (e.g. '#00ff00'), to use when this metric is rendered on a graph. The ``Color`` class has a set of standard colors that can be used here. Default: - Automatic color
        :param dimensions_map: Dimensions of the metric. Default: - No dimensions.
        :param id: Unique identifier for this metric when used in dashboard widgets. The id can be used as a variable to represent this metric in math expressions. Valid characters are letters, numbers, and underscore. The first character must be a lowercase letter. Default: - No ID
        :param label: Label for this metric when added to a Graph in a Dashboard. You can use `dynamic labels <https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/graph-dynamic-labels.html>`_ to show summary information about the entire displayed time series in the legend. For example, if you use:: [max: ${MAX}] MyMetric As the metric label, the maximum value in the visible range will be shown next to the time series name in the graph's legend. Default: - No label
        :param period: The period over which the specified statistic is applied. Default: Duration.minutes(5)
        :param region: Region which this metric comes from. Default: - Deployment region.
        :param stack_account: Account of the stack this metric is attached to. Default: - Deployment account.
        :param stack_region: Region of the stack this metric is attached to. Default: - Deployment region.
        :param statistic: What function to use for aggregating. Use the ``aws_cloudwatch.Stats`` helper class to construct valid input strings. Can be one of the following: - "Minimum" | "min" - "Maximum" | "max" - "Average" | "avg" - "Sum" | "sum" - "SampleCount | "n" - "pNN.NN" - "tmNN.NN" | "tm(NN.NN%:NN.NN%)" - "iqm" - "wmNN.NN" | "wm(NN.NN%:NN.NN%)" - "tcNN.NN" | "tc(NN.NN%:NN.NN%)" - "tsNN.NN" | "ts(NN.NN%:NN.NN%)" Default: Average
        :param unit: Unit used to filter the metric stream. Only refer to datums emitted to the metric stream with the given unit and ignore all others. Only useful when datums are being emitted to the same metric stream under different units. The default is to use all matric datums in the stream, regardless of unit, which is recommended in nearly all cases. CloudWatch does not honor this property for graphs. Default: - All metric datums in the given metric stream
        :param visible: Whether this metric should be visible in dashboard graphs. Setting this to false is useful when you want to hide raw metrics that are used in math expressions, and show only the expression results. Default: true

        :stability: experimental
        '''
        props = _aws_cdk_aws_cloudwatch_ceddda9d.MetricOptions(
            account=account,
            color=color,
            dimensions_map=dimensions_map,
            id=id,
            label=label,
            period=period,
            region=region,
            stack_account=stack_account,
            stack_region=stack_region,
            statistic=statistic,
            unit=unit,
            visible=visible,
        )

        return typing.cast(_aws_cdk_aws_cloudwatch_ceddda9d.Metric, jsii.invoke(self, "metricPlacementsStarted", [props]))

    @jsii.member(jsii_name="metricPlacementsSucceeded")
    def metric_placements_succeeded(
        self,
        *,
        account: typing.Optional[builtins.str] = None,
        color: typing.Optional[builtins.str] = None,
        dimensions_map: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        id: typing.Optional[builtins.str] = None,
        label: typing.Optional[builtins.str] = None,
        period: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        region: typing.Optional[builtins.str] = None,
        stack_account: typing.Optional[builtins.str] = None,
        stack_region: typing.Optional[builtins.str] = None,
        statistic: typing.Optional[builtins.str] = None,
        unit: typing.Optional[_aws_cdk_aws_cloudwatch_ceddda9d.Unit] = None,
        visible: typing.Optional[builtins.bool] = None,
    ) -> _aws_cdk_aws_cloudwatch_ceddda9d.Metric:
        '''(experimental) Game session placement requests that resulted in a new game session since the last report.

        :param account: Account which this metric comes from. Default: - Deployment account.
        :param color: The hex color code, prefixed with '#' (e.g. '#00ff00'), to use when this metric is rendered on a graph. The ``Color`` class has a set of standard colors that can be used here. Default: - Automatic color
        :param dimensions_map: Dimensions of the metric. Default: - No dimensions.
        :param id: Unique identifier for this metric when used in dashboard widgets. The id can be used as a variable to represent this metric in math expressions. Valid characters are letters, numbers, and underscore. The first character must be a lowercase letter. Default: - No ID
        :param label: Label for this metric when added to a Graph in a Dashboard. You can use `dynamic labels <https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/graph-dynamic-labels.html>`_ to show summary information about the entire displayed time series in the legend. For example, if you use:: [max: ${MAX}] MyMetric As the metric label, the maximum value in the visible range will be shown next to the time series name in the graph's legend. Default: - No label
        :param period: The period over which the specified statistic is applied. Default: Duration.minutes(5)
        :param region: Region which this metric comes from. Default: - Deployment region.
        :param stack_account: Account of the stack this metric is attached to. Default: - Deployment account.
        :param stack_region: Region of the stack this metric is attached to. Default: - Deployment region.
        :param statistic: What function to use for aggregating. Use the ``aws_cloudwatch.Stats`` helper class to construct valid input strings. Can be one of the following: - "Minimum" | "min" - "Maximum" | "max" - "Average" | "avg" - "Sum" | "sum" - "SampleCount | "n" - "pNN.NN" - "tmNN.NN" | "tm(NN.NN%:NN.NN%)" - "iqm" - "wmNN.NN" | "wm(NN.NN%:NN.NN%)" - "tcNN.NN" | "tc(NN.NN%:NN.NN%)" - "tsNN.NN" | "ts(NN.NN%:NN.NN%)" Default: Average
        :param unit: Unit used to filter the metric stream. Only refer to datums emitted to the metric stream with the given unit and ignore all others. Only useful when datums are being emitted to the same metric stream under different units. The default is to use all matric datums in the stream, regardless of unit, which is recommended in nearly all cases. CloudWatch does not honor this property for graphs. Default: - All metric datums in the given metric stream
        :param visible: Whether this metric should be visible in dashboard graphs. Setting this to false is useful when you want to hide raw metrics that are used in math expressions, and show only the expression results. Default: true

        :stability: experimental
        '''
        props = _aws_cdk_aws_cloudwatch_ceddda9d.MetricOptions(
            account=account,
            color=color,
            dimensions_map=dimensions_map,
            id=id,
            label=label,
            period=period,
            region=region,
            stack_account=stack_account,
            stack_region=stack_region,
            statistic=statistic,
            unit=unit,
            visible=visible,
        )

        return typing.cast(_aws_cdk_aws_cloudwatch_ceddda9d.Metric, jsii.invoke(self, "metricPlacementsSucceeded", [props]))

    @jsii.member(jsii_name="metricPlacementsTimedOut")
    def metric_placements_timed_out(
        self,
        *,
        account: typing.Optional[builtins.str] = None,
        color: typing.Optional[builtins.str] = None,
        dimensions_map: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        id: typing.Optional[builtins.str] = None,
        label: typing.Optional[builtins.str] = None,
        period: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        region: typing.Optional[builtins.str] = None,
        stack_account: typing.Optional[builtins.str] = None,
        stack_region: typing.Optional[builtins.str] = None,
        statistic: typing.Optional[builtins.str] = None,
        unit: typing.Optional[_aws_cdk_aws_cloudwatch_ceddda9d.Unit] = None,
        visible: typing.Optional[builtins.bool] = None,
    ) -> _aws_cdk_aws_cloudwatch_ceddda9d.Metric:
        '''(experimental) Game session placement requests that reached the queue's timeout limit without being fulfilled since the last report.

        :param account: Account which this metric comes from. Default: - Deployment account.
        :param color: The hex color code, prefixed with '#' (e.g. '#00ff00'), to use when this metric is rendered on a graph. The ``Color`` class has a set of standard colors that can be used here. Default: - Automatic color
        :param dimensions_map: Dimensions of the metric. Default: - No dimensions.
        :param id: Unique identifier for this metric when used in dashboard widgets. The id can be used as a variable to represent this metric in math expressions. Valid characters are letters, numbers, and underscore. The first character must be a lowercase letter. Default: - No ID
        :param label: Label for this metric when added to a Graph in a Dashboard. You can use `dynamic labels <https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/graph-dynamic-labels.html>`_ to show summary information about the entire displayed time series in the legend. For example, if you use:: [max: ${MAX}] MyMetric As the metric label, the maximum value in the visible range will be shown next to the time series name in the graph's legend. Default: - No label
        :param period: The period over which the specified statistic is applied. Default: Duration.minutes(5)
        :param region: Region which this metric comes from. Default: - Deployment region.
        :param stack_account: Account of the stack this metric is attached to. Default: - Deployment account.
        :param stack_region: Region of the stack this metric is attached to. Default: - Deployment region.
        :param statistic: What function to use for aggregating. Use the ``aws_cloudwatch.Stats`` helper class to construct valid input strings. Can be one of the following: - "Minimum" | "min" - "Maximum" | "max" - "Average" | "avg" - "Sum" | "sum" - "SampleCount | "n" - "pNN.NN" - "tmNN.NN" | "tm(NN.NN%:NN.NN%)" - "iqm" - "wmNN.NN" | "wm(NN.NN%:NN.NN%)" - "tcNN.NN" | "tc(NN.NN%:NN.NN%)" - "tsNN.NN" | "ts(NN.NN%:NN.NN%)" Default: Average
        :param unit: Unit used to filter the metric stream. Only refer to datums emitted to the metric stream with the given unit and ignore all others. Only useful when datums are being emitted to the same metric stream under different units. The default is to use all matric datums in the stream, regardless of unit, which is recommended in nearly all cases. CloudWatch does not honor this property for graphs. Default: - All metric datums in the given metric stream
        :param visible: Whether this metric should be visible in dashboard graphs. Setting this to false is useful when you want to hide raw metrics that are used in math expressions, and show only the expression results. Default: true

        :stability: experimental
        '''
        props = _aws_cdk_aws_cloudwatch_ceddda9d.MetricOptions(
            account=account,
            color=color,
            dimensions_map=dimensions_map,
            id=id,
            label=label,
            period=period,
            region=region,
            stack_account=stack_account,
            stack_region=stack_region,
            statistic=statistic,
            unit=unit,
            visible=visible,
        )

        return typing.cast(_aws_cdk_aws_cloudwatch_ceddda9d.Metric, jsii.invoke(self, "metricPlacementsTimedOut", [props]))

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, IGameSessionQueue).__jsii_proxy_class__ = lambda : _IGameSessionQueueProxy


@jsii.interface(jsii_type="@aws-cdk/aws-gamelift-alpha.IGameSessionQueueDestination")
class IGameSessionQueueDestination(typing_extensions.Protocol):
    '''(experimental) Represents a game session queue destination.

    :stability: experimental
    '''

    @builtins.property
    @jsii.member(jsii_name="resourceArnForDestination")
    def resource_arn_for_destination(self) -> builtins.str:
        '''(experimental) The ARN(s) to put into the destination field for a game session queue.

        This property is for cdk modules to consume only. You should not need to use this property.
        Instead, use dedicated identifier on each components.

        :stability: experimental
        '''
        ...


class _IGameSessionQueueDestinationProxy:
    '''(experimental) Represents a game session queue destination.

    :stability: experimental
    '''

    __jsii_type__: typing.ClassVar[str] = "@aws-cdk/aws-gamelift-alpha.IGameSessionQueueDestination"

    @builtins.property
    @jsii.member(jsii_name="resourceArnForDestination")
    def resource_arn_for_destination(self) -> builtins.str:
        '''(experimental) The ARN(s) to put into the destination field for a game session queue.

        This property is for cdk modules to consume only. You should not need to use this property.
        Instead, use dedicated identifier on each components.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "resourceArnForDestination"))

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, IGameSessionQueueDestination).__jsii_proxy_class__ = lambda : _IGameSessionQueueDestinationProxy


@jsii.interface(jsii_type="@aws-cdk/aws-gamelift-alpha.IMatchmakingConfiguration")
class IMatchmakingConfiguration(
    _aws_cdk_ceddda9d.IResource,
    typing_extensions.Protocol,
):
    '''(experimental) Represents a Gamelift matchmaking configuration.

    :stability: experimental
    '''

    @builtins.property
    @jsii.member(jsii_name="matchmakingConfigurationArn")
    def matchmaking_configuration_arn(self) -> builtins.str:
        '''(experimental) The ARN of the matchmaking configuration.

        :stability: experimental
        :attribute: true
        '''
        ...

    @builtins.property
    @jsii.member(jsii_name="matchmakingConfigurationName")
    def matchmaking_configuration_name(self) -> builtins.str:
        '''(experimental) The name of the matchmaking configuration.

        :stability: experimental
        :attribute: true
        '''
        ...

    @builtins.property
    @jsii.member(jsii_name="notificationTarget")
    def notification_target(self) -> typing.Optional[_aws_cdk_aws_sns_ceddda9d.ITopic]:
        '''(experimental) The notification target for matchmaking events.

        :stability: experimental
        :attribute: true
        '''
        ...

    @jsii.member(jsii_name="metric")
    def metric(
        self,
        metric_name: builtins.str,
        *,
        account: typing.Optional[builtins.str] = None,
        color: typing.Optional[builtins.str] = None,
        dimensions_map: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        id: typing.Optional[builtins.str] = None,
        label: typing.Optional[builtins.str] = None,
        period: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        region: typing.Optional[builtins.str] = None,
        stack_account: typing.Optional[builtins.str] = None,
        stack_region: typing.Optional[builtins.str] = None,
        statistic: typing.Optional[builtins.str] = None,
        unit: typing.Optional[_aws_cdk_aws_cloudwatch_ceddda9d.Unit] = None,
        visible: typing.Optional[builtins.bool] = None,
    ) -> _aws_cdk_aws_cloudwatch_ceddda9d.Metric:
        '''(experimental) Return the given named metric for this matchmaking configuration.

        :param metric_name: -
        :param account: Account which this metric comes from. Default: - Deployment account.
        :param color: The hex color code, prefixed with '#' (e.g. '#00ff00'), to use when this metric is rendered on a graph. The ``Color`` class has a set of standard colors that can be used here. Default: - Automatic color
        :param dimensions_map: Dimensions of the metric. Default: - No dimensions.
        :param id: Unique identifier for this metric when used in dashboard widgets. The id can be used as a variable to represent this metric in math expressions. Valid characters are letters, numbers, and underscore. The first character must be a lowercase letter. Default: - No ID
        :param label: Label for this metric when added to a Graph in a Dashboard. You can use `dynamic labels <https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/graph-dynamic-labels.html>`_ to show summary information about the entire displayed time series in the legend. For example, if you use:: [max: ${MAX}] MyMetric As the metric label, the maximum value in the visible range will be shown next to the time series name in the graph's legend. Default: - No label
        :param period: The period over which the specified statistic is applied. Default: Duration.minutes(5)
        :param region: Region which this metric comes from. Default: - Deployment region.
        :param stack_account: Account of the stack this metric is attached to. Default: - Deployment account.
        :param stack_region: Region of the stack this metric is attached to. Default: - Deployment region.
        :param statistic: What function to use for aggregating. Use the ``aws_cloudwatch.Stats`` helper class to construct valid input strings. Can be one of the following: - "Minimum" | "min" - "Maximum" | "max" - "Average" | "avg" - "Sum" | "sum" - "SampleCount | "n" - "pNN.NN" - "tmNN.NN" | "tm(NN.NN%:NN.NN%)" - "iqm" - "wmNN.NN" | "wm(NN.NN%:NN.NN%)" - "tcNN.NN" | "tc(NN.NN%:NN.NN%)" - "tsNN.NN" | "ts(NN.NN%:NN.NN%)" Default: Average
        :param unit: Unit used to filter the metric stream. Only refer to datums emitted to the metric stream with the given unit and ignore all others. Only useful when datums are being emitted to the same metric stream under different units. The default is to use all matric datums in the stream, regardless of unit, which is recommended in nearly all cases. CloudWatch does not honor this property for graphs. Default: - All metric datums in the given metric stream
        :param visible: Whether this metric should be visible in dashboard graphs. Setting this to false is useful when you want to hide raw metrics that are used in math expressions, and show only the expression results. Default: true

        :stability: experimental
        '''
        ...

    @jsii.member(jsii_name="metricCurrentTickets")
    def metric_current_tickets(
        self,
        *,
        account: typing.Optional[builtins.str] = None,
        color: typing.Optional[builtins.str] = None,
        dimensions_map: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        id: typing.Optional[builtins.str] = None,
        label: typing.Optional[builtins.str] = None,
        period: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        region: typing.Optional[builtins.str] = None,
        stack_account: typing.Optional[builtins.str] = None,
        stack_region: typing.Optional[builtins.str] = None,
        statistic: typing.Optional[builtins.str] = None,
        unit: typing.Optional[_aws_cdk_aws_cloudwatch_ceddda9d.Unit] = None,
        visible: typing.Optional[builtins.bool] = None,
    ) -> _aws_cdk_aws_cloudwatch_ceddda9d.Metric:
        '''(experimental) Matchmaking requests currently being processed or waiting to be processed.

        :param account: Account which this metric comes from. Default: - Deployment account.
        :param color: The hex color code, prefixed with '#' (e.g. '#00ff00'), to use when this metric is rendered on a graph. The ``Color`` class has a set of standard colors that can be used here. Default: - Automatic color
        :param dimensions_map: Dimensions of the metric. Default: - No dimensions.
        :param id: Unique identifier for this metric when used in dashboard widgets. The id can be used as a variable to represent this metric in math expressions. Valid characters are letters, numbers, and underscore. The first character must be a lowercase letter. Default: - No ID
        :param label: Label for this metric when added to a Graph in a Dashboard. You can use `dynamic labels <https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/graph-dynamic-labels.html>`_ to show summary information about the entire displayed time series in the legend. For example, if you use:: [max: ${MAX}] MyMetric As the metric label, the maximum value in the visible range will be shown next to the time series name in the graph's legend. Default: - No label
        :param period: The period over which the specified statistic is applied. Default: Duration.minutes(5)
        :param region: Region which this metric comes from. Default: - Deployment region.
        :param stack_account: Account of the stack this metric is attached to. Default: - Deployment account.
        :param stack_region: Region of the stack this metric is attached to. Default: - Deployment region.
        :param statistic: What function to use for aggregating. Use the ``aws_cloudwatch.Stats`` helper class to construct valid input strings. Can be one of the following: - "Minimum" | "min" - "Maximum" | "max" - "Average" | "avg" - "Sum" | "sum" - "SampleCount | "n" - "pNN.NN" - "tmNN.NN" | "tm(NN.NN%:NN.NN%)" - "iqm" - "wmNN.NN" | "wm(NN.NN%:NN.NN%)" - "tcNN.NN" | "tc(NN.NN%:NN.NN%)" - "tsNN.NN" | "ts(NN.NN%:NN.NN%)" Default: Average
        :param unit: Unit used to filter the metric stream. Only refer to datums emitted to the metric stream with the given unit and ignore all others. Only useful when datums are being emitted to the same metric stream under different units. The default is to use all matric datums in the stream, regardless of unit, which is recommended in nearly all cases. CloudWatch does not honor this property for graphs. Default: - All metric datums in the given metric stream
        :param visible: Whether this metric should be visible in dashboard graphs. Setting this to false is useful when you want to hide raw metrics that are used in math expressions, and show only the expression results. Default: true

        :stability: experimental
        '''
        ...

    @jsii.member(jsii_name="metricMatchesAccepted")
    def metric_matches_accepted(
        self,
        *,
        account: typing.Optional[builtins.str] = None,
        color: typing.Optional[builtins.str] = None,
        dimensions_map: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        id: typing.Optional[builtins.str] = None,
        label: typing.Optional[builtins.str] = None,
        period: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        region: typing.Optional[builtins.str] = None,
        stack_account: typing.Optional[builtins.str] = None,
        stack_region: typing.Optional[builtins.str] = None,
        statistic: typing.Optional[builtins.str] = None,
        unit: typing.Optional[_aws_cdk_aws_cloudwatch_ceddda9d.Unit] = None,
        visible: typing.Optional[builtins.bool] = None,
    ) -> _aws_cdk_aws_cloudwatch_ceddda9d.Metric:
        '''(experimental) For matchmaking configurations that require acceptance, the potential matches that were accepted since the last report.

        :param account: Account which this metric comes from. Default: - Deployment account.
        :param color: The hex color code, prefixed with '#' (e.g. '#00ff00'), to use when this metric is rendered on a graph. The ``Color`` class has a set of standard colors that can be used here. Default: - Automatic color
        :param dimensions_map: Dimensions of the metric. Default: - No dimensions.
        :param id: Unique identifier for this metric when used in dashboard widgets. The id can be used as a variable to represent this metric in math expressions. Valid characters are letters, numbers, and underscore. The first character must be a lowercase letter. Default: - No ID
        :param label: Label for this metric when added to a Graph in a Dashboard. You can use `dynamic labels <https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/graph-dynamic-labels.html>`_ to show summary information about the entire displayed time series in the legend. For example, if you use:: [max: ${MAX}] MyMetric As the metric label, the maximum value in the visible range will be shown next to the time series name in the graph's legend. Default: - No label
        :param period: The period over which the specified statistic is applied. Default: Duration.minutes(5)
        :param region: Region which this metric comes from. Default: - Deployment region.
        :param stack_account: Account of the stack this metric is attached to. Default: - Deployment account.
        :param stack_region: Region of the stack this metric is attached to. Default: - Deployment region.
        :param statistic: What function to use for aggregating. Use the ``aws_cloudwatch.Stats`` helper class to construct valid input strings. Can be one of the following: - "Minimum" | "min" - "Maximum" | "max" - "Average" | "avg" - "Sum" | "sum" - "SampleCount | "n" - "pNN.NN" - "tmNN.NN" | "tm(NN.NN%:NN.NN%)" - "iqm" - "wmNN.NN" | "wm(NN.NN%:NN.NN%)" - "tcNN.NN" | "tc(NN.NN%:NN.NN%)" - "tsNN.NN" | "ts(NN.NN%:NN.NN%)" Default: Average
        :param unit: Unit used to filter the metric stream. Only refer to datums emitted to the metric stream with the given unit and ignore all others. Only useful when datums are being emitted to the same metric stream under different units. The default is to use all matric datums in the stream, regardless of unit, which is recommended in nearly all cases. CloudWatch does not honor this property for graphs. Default: - All metric datums in the given metric stream
        :param visible: Whether this metric should be visible in dashboard graphs. Setting this to false is useful when you want to hide raw metrics that are used in math expressions, and show only the expression results. Default: true

        :stability: experimental
        '''
        ...

    @jsii.member(jsii_name="metricMatchesCreated")
    def metric_matches_created(
        self,
        *,
        account: typing.Optional[builtins.str] = None,
        color: typing.Optional[builtins.str] = None,
        dimensions_map: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        id: typing.Optional[builtins.str] = None,
        label: typing.Optional[builtins.str] = None,
        period: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        region: typing.Optional[builtins.str] = None,
        stack_account: typing.Optional[builtins.str] = None,
        stack_region: typing.Optional[builtins.str] = None,
        statistic: typing.Optional[builtins.str] = None,
        unit: typing.Optional[_aws_cdk_aws_cloudwatch_ceddda9d.Unit] = None,
        visible: typing.Optional[builtins.bool] = None,
    ) -> _aws_cdk_aws_cloudwatch_ceddda9d.Metric:
        '''(experimental) Potential matches that were created since the last report.

        :param account: Account which this metric comes from. Default: - Deployment account.
        :param color: The hex color code, prefixed with '#' (e.g. '#00ff00'), to use when this metric is rendered on a graph. The ``Color`` class has a set of standard colors that can be used here. Default: - Automatic color
        :param dimensions_map: Dimensions of the metric. Default: - No dimensions.
        :param id: Unique identifier for this metric when used in dashboard widgets. The id can be used as a variable to represent this metric in math expressions. Valid characters are letters, numbers, and underscore. The first character must be a lowercase letter. Default: - No ID
        :param label: Label for this metric when added to a Graph in a Dashboard. You can use `dynamic labels <https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/graph-dynamic-labels.html>`_ to show summary information about the entire displayed time series in the legend. For example, if you use:: [max: ${MAX}] MyMetric As the metric label, the maximum value in the visible range will be shown next to the time series name in the graph's legend. Default: - No label
        :param period: The period over which the specified statistic is applied. Default: Duration.minutes(5)
        :param region: Region which this metric comes from. Default: - Deployment region.
        :param stack_account: Account of the stack this metric is attached to. Default: - Deployment account.
        :param stack_region: Region of the stack this metric is attached to. Default: - Deployment region.
        :param statistic: What function to use for aggregating. Use the ``aws_cloudwatch.Stats`` helper class to construct valid input strings. Can be one of the following: - "Minimum" | "min" - "Maximum" | "max" - "Average" | "avg" - "Sum" | "sum" - "SampleCount | "n" - "pNN.NN" - "tmNN.NN" | "tm(NN.NN%:NN.NN%)" - "iqm" - "wmNN.NN" | "wm(NN.NN%:NN.NN%)" - "tcNN.NN" | "tc(NN.NN%:NN.NN%)" - "tsNN.NN" | "ts(NN.NN%:NN.NN%)" Default: Average
        :param unit: Unit used to filter the metric stream. Only refer to datums emitted to the metric stream with the given unit and ignore all others. Only useful when datums are being emitted to the same metric stream under different units. The default is to use all matric datums in the stream, regardless of unit, which is recommended in nearly all cases. CloudWatch does not honor this property for graphs. Default: - All metric datums in the given metric stream
        :param visible: Whether this metric should be visible in dashboard graphs. Setting this to false is useful when you want to hide raw metrics that are used in math expressions, and show only the expression results. Default: true

        :stability: experimental
        '''
        ...

    @jsii.member(jsii_name="metricMatchesPlaced")
    def metric_matches_placed(
        self,
        *,
        account: typing.Optional[builtins.str] = None,
        color: typing.Optional[builtins.str] = None,
        dimensions_map: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        id: typing.Optional[builtins.str] = None,
        label: typing.Optional[builtins.str] = None,
        period: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        region: typing.Optional[builtins.str] = None,
        stack_account: typing.Optional[builtins.str] = None,
        stack_region: typing.Optional[builtins.str] = None,
        statistic: typing.Optional[builtins.str] = None,
        unit: typing.Optional[_aws_cdk_aws_cloudwatch_ceddda9d.Unit] = None,
        visible: typing.Optional[builtins.bool] = None,
    ) -> _aws_cdk_aws_cloudwatch_ceddda9d.Metric:
        '''(experimental) Matches that were successfully placed into a game session since the last report.

        :param account: Account which this metric comes from. Default: - Deployment account.
        :param color: The hex color code, prefixed with '#' (e.g. '#00ff00'), to use when this metric is rendered on a graph. The ``Color`` class has a set of standard colors that can be used here. Default: - Automatic color
        :param dimensions_map: Dimensions of the metric. Default: - No dimensions.
        :param id: Unique identifier for this metric when used in dashboard widgets. The id can be used as a variable to represent this metric in math expressions. Valid characters are letters, numbers, and underscore. The first character must be a lowercase letter. Default: - No ID
        :param label: Label for this metric when added to a Graph in a Dashboard. You can use `dynamic labels <https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/graph-dynamic-labels.html>`_ to show summary information about the entire displayed time series in the legend. For example, if you use:: [max: ${MAX}] MyMetric As the metric label, the maximum value in the visible range will be shown next to the time series name in the graph's legend. Default: - No label
        :param period: The period over which the specified statistic is applied. Default: Duration.minutes(5)
        :param region: Region which this metric comes from. Default: - Deployment region.
        :param stack_account: Account of the stack this metric is attached to. Default: - Deployment account.
        :param stack_region: Region of the stack this metric is attached to. Default: - Deployment region.
        :param statistic: What function to use for aggregating. Use the ``aws_cloudwatch.Stats`` helper class to construct valid input strings. Can be one of the following: - "Minimum" | "min" - "Maximum" | "max" - "Average" | "avg" - "Sum" | "sum" - "SampleCount | "n" - "pNN.NN" - "tmNN.NN" | "tm(NN.NN%:NN.NN%)" - "iqm" - "wmNN.NN" | "wm(NN.NN%:NN.NN%)" - "tcNN.NN" | "tc(NN.NN%:NN.NN%)" - "tsNN.NN" | "ts(NN.NN%:NN.NN%)" Default: Average
        :param unit: Unit used to filter the metric stream. Only refer to datums emitted to the metric stream with the given unit and ignore all others. Only useful when datums are being emitted to the same metric stream under different units. The default is to use all matric datums in the stream, regardless of unit, which is recommended in nearly all cases. CloudWatch does not honor this property for graphs. Default: - All metric datums in the given metric stream
        :param visible: Whether this metric should be visible in dashboard graphs. Setting this to false is useful when you want to hide raw metrics that are used in math expressions, and show only the expression results. Default: true

        :stability: experimental
        '''
        ...

    @jsii.member(jsii_name="metricMatchesRejected")
    def metric_matches_rejected(
        self,
        *,
        account: typing.Optional[builtins.str] = None,
        color: typing.Optional[builtins.str] = None,
        dimensions_map: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        id: typing.Optional[builtins.str] = None,
        label: typing.Optional[builtins.str] = None,
        period: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        region: typing.Optional[builtins.str] = None,
        stack_account: typing.Optional[builtins.str] = None,
        stack_region: typing.Optional[builtins.str] = None,
        statistic: typing.Optional[builtins.str] = None,
        unit: typing.Optional[_aws_cdk_aws_cloudwatch_ceddda9d.Unit] = None,
        visible: typing.Optional[builtins.bool] = None,
    ) -> _aws_cdk_aws_cloudwatch_ceddda9d.Metric:
        '''(experimental) For matchmaking configurations that require acceptance, the potential matches that were rejected by at least one player since the last report.

        :param account: Account which this metric comes from. Default: - Deployment account.
        :param color: The hex color code, prefixed with '#' (e.g. '#00ff00'), to use when this metric is rendered on a graph. The ``Color`` class has a set of standard colors that can be used here. Default: - Automatic color
        :param dimensions_map: Dimensions of the metric. Default: - No dimensions.
        :param id: Unique identifier for this metric when used in dashboard widgets. The id can be used as a variable to represent this metric in math expressions. Valid characters are letters, numbers, and underscore. The first character must be a lowercase letter. Default: - No ID
        :param label: Label for this metric when added to a Graph in a Dashboard. You can use `dynamic labels <https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/graph-dynamic-labels.html>`_ to show summary information about the entire displayed time series in the legend. For example, if you use:: [max: ${MAX}] MyMetric As the metric label, the maximum value in the visible range will be shown next to the time series name in the graph's legend. Default: - No label
        :param period: The period over which the specified statistic is applied. Default: Duration.minutes(5)
        :param region: Region which this metric comes from. Default: - Deployment region.
        :param stack_account: Account of the stack this metric is attached to. Default: - Deployment account.
        :param stack_region: Region of the stack this metric is attached to. Default: - Deployment region.
        :param statistic: What function to use for aggregating. Use the ``aws_cloudwatch.Stats`` helper class to construct valid input strings. Can be one of the following: - "Minimum" | "min" - "Maximum" | "max" - "Average" | "avg" - "Sum" | "sum" - "SampleCount | "n" - "pNN.NN" - "tmNN.NN" | "tm(NN.NN%:NN.NN%)" - "iqm" - "wmNN.NN" | "wm(NN.NN%:NN.NN%)" - "tcNN.NN" | "tc(NN.NN%:NN.NN%)" - "tsNN.NN" | "ts(NN.NN%:NN.NN%)" Default: Average
        :param unit: Unit used to filter the metric stream. Only refer to datums emitted to the metric stream with the given unit and ignore all others. Only useful when datums are being emitted to the same metric stream under different units. The default is to use all matric datums in the stream, regardless of unit, which is recommended in nearly all cases. CloudWatch does not honor this property for graphs. Default: - All metric datums in the given metric stream
        :param visible: Whether this metric should be visible in dashboard graphs. Setting this to false is useful when you want to hide raw metrics that are used in math expressions, and show only the expression results. Default: true

        :stability: experimental
        '''
        ...

    @jsii.member(jsii_name="metricPlayersStarted")
    def metric_players_started(
        self,
        *,
        account: typing.Optional[builtins.str] = None,
        color: typing.Optional[builtins.str] = None,
        dimensions_map: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        id: typing.Optional[builtins.str] = None,
        label: typing.Optional[builtins.str] = None,
        period: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        region: typing.Optional[builtins.str] = None,
        stack_account: typing.Optional[builtins.str] = None,
        stack_region: typing.Optional[builtins.str] = None,
        statistic: typing.Optional[builtins.str] = None,
        unit: typing.Optional[_aws_cdk_aws_cloudwatch_ceddda9d.Unit] = None,
        visible: typing.Optional[builtins.bool] = None,
    ) -> _aws_cdk_aws_cloudwatch_ceddda9d.Metric:
        '''(experimental) Players in matchmaking tickets that were added since the last report.

        :param account: Account which this metric comes from. Default: - Deployment account.
        :param color: The hex color code, prefixed with '#' (e.g. '#00ff00'), to use when this metric is rendered on a graph. The ``Color`` class has a set of standard colors that can be used here. Default: - Automatic color
        :param dimensions_map: Dimensions of the metric. Default: - No dimensions.
        :param id: Unique identifier for this metric when used in dashboard widgets. The id can be used as a variable to represent this metric in math expressions. Valid characters are letters, numbers, and underscore. The first character must be a lowercase letter. Default: - No ID
        :param label: Label for this metric when added to a Graph in a Dashboard. You can use `dynamic labels <https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/graph-dynamic-labels.html>`_ to show summary information about the entire displayed time series in the legend. For example, if you use:: [max: ${MAX}] MyMetric As the metric label, the maximum value in the visible range will be shown next to the time series name in the graph's legend. Default: - No label
        :param period: The period over which the specified statistic is applied. Default: Duration.minutes(5)
        :param region: Region which this metric comes from. Default: - Deployment region.
        :param stack_account: Account of the stack this metric is attached to. Default: - Deployment account.
        :param stack_region: Region of the stack this metric is attached to. Default: - Deployment region.
        :param statistic: What function to use for aggregating. Use the ``aws_cloudwatch.Stats`` helper class to construct valid input strings. Can be one of the following: - "Minimum" | "min" - "Maximum" | "max" - "Average" | "avg" - "Sum" | "sum" - "SampleCount | "n" - "pNN.NN" - "tmNN.NN" | "tm(NN.NN%:NN.NN%)" - "iqm" - "wmNN.NN" | "wm(NN.NN%:NN.NN%)" - "tcNN.NN" | "tc(NN.NN%:NN.NN%)" - "tsNN.NN" | "ts(NN.NN%:NN.NN%)" Default: Average
        :param unit: Unit used to filter the metric stream. Only refer to datums emitted to the metric stream with the given unit and ignore all others. Only useful when datums are being emitted to the same metric stream under different units. The default is to use all matric datums in the stream, regardless of unit, which is recommended in nearly all cases. CloudWatch does not honor this property for graphs. Default: - All metric datums in the given metric stream
        :param visible: Whether this metric should be visible in dashboard graphs. Setting this to false is useful when you want to hide raw metrics that are used in math expressions, and show only the expression results. Default: true

        :stability: experimental
        '''
        ...

    @jsii.member(jsii_name="metricTimeToMatch")
    def metric_time_to_match(
        self,
        *,
        account: typing.Optional[builtins.str] = None,
        color: typing.Optional[builtins.str] = None,
        dimensions_map: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        id: typing.Optional[builtins.str] = None,
        label: typing.Optional[builtins.str] = None,
        period: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        region: typing.Optional[builtins.str] = None,
        stack_account: typing.Optional[builtins.str] = None,
        stack_region: typing.Optional[builtins.str] = None,
        statistic: typing.Optional[builtins.str] = None,
        unit: typing.Optional[_aws_cdk_aws_cloudwatch_ceddda9d.Unit] = None,
        visible: typing.Optional[builtins.bool] = None,
    ) -> _aws_cdk_aws_cloudwatch_ceddda9d.Metric:
        '''(experimental) For matchmaking requests that were put into a potential match before the last report, the amount of time between ticket creation and potential match creation.

        Units: seconds

        :param account: Account which this metric comes from. Default: - Deployment account.
        :param color: The hex color code, prefixed with '#' (e.g. '#00ff00'), to use when this metric is rendered on a graph. The ``Color`` class has a set of standard colors that can be used here. Default: - Automatic color
        :param dimensions_map: Dimensions of the metric. Default: - No dimensions.
        :param id: Unique identifier for this metric when used in dashboard widgets. The id can be used as a variable to represent this metric in math expressions. Valid characters are letters, numbers, and underscore. The first character must be a lowercase letter. Default: - No ID
        :param label: Label for this metric when added to a Graph in a Dashboard. You can use `dynamic labels <https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/graph-dynamic-labels.html>`_ to show summary information about the entire displayed time series in the legend. For example, if you use:: [max: ${MAX}] MyMetric As the metric label, the maximum value in the visible range will be shown next to the time series name in the graph's legend. Default: - No label
        :param period: The period over which the specified statistic is applied. Default: Duration.minutes(5)
        :param region: Region which this metric comes from. Default: - Deployment region.
        :param stack_account: Account of the stack this metric is attached to. Default: - Deployment account.
        :param stack_region: Region of the stack this metric is attached to. Default: - Deployment region.
        :param statistic: What function to use for aggregating. Use the ``aws_cloudwatch.Stats`` helper class to construct valid input strings. Can be one of the following: - "Minimum" | "min" - "Maximum" | "max" - "Average" | "avg" - "Sum" | "sum" - "SampleCount | "n" - "pNN.NN" - "tmNN.NN" | "tm(NN.NN%:NN.NN%)" - "iqm" - "wmNN.NN" | "wm(NN.NN%:NN.NN%)" - "tcNN.NN" | "tc(NN.NN%:NN.NN%)" - "tsNN.NN" | "ts(NN.NN%:NN.NN%)" Default: Average
        :param unit: Unit used to filter the metric stream. Only refer to datums emitted to the metric stream with the given unit and ignore all others. Only useful when datums are being emitted to the same metric stream under different units. The default is to use all matric datums in the stream, regardless of unit, which is recommended in nearly all cases. CloudWatch does not honor this property for graphs. Default: - All metric datums in the given metric stream
        :param visible: Whether this metric should be visible in dashboard graphs. Setting this to false is useful when you want to hide raw metrics that are used in math expressions, and show only the expression results. Default: true

        :stability: experimental
        '''
        ...


class _IMatchmakingConfigurationProxy(
    jsii.proxy_for(_aws_cdk_ceddda9d.IResource), # type: ignore[misc]
):
    '''(experimental) Represents a Gamelift matchmaking configuration.

    :stability: experimental
    '''

    __jsii_type__: typing.ClassVar[str] = "@aws-cdk/aws-gamelift-alpha.IMatchmakingConfiguration"

    @builtins.property
    @jsii.member(jsii_name="matchmakingConfigurationArn")
    def matchmaking_configuration_arn(self) -> builtins.str:
        '''(experimental) The ARN of the matchmaking configuration.

        :stability: experimental
        :attribute: true
        '''
        return typing.cast(builtins.str, jsii.get(self, "matchmakingConfigurationArn"))

    @builtins.property
    @jsii.member(jsii_name="matchmakingConfigurationName")
    def matchmaking_configuration_name(self) -> builtins.str:
        '''(experimental) The name of the matchmaking configuration.

        :stability: experimental
        :attribute: true
        '''
        return typing.cast(builtins.str, jsii.get(self, "matchmakingConfigurationName"))

    @builtins.property
    @jsii.member(jsii_name="notificationTarget")
    def notification_target(self) -> typing.Optional[_aws_cdk_aws_sns_ceddda9d.ITopic]:
        '''(experimental) The notification target for matchmaking events.

        :stability: experimental
        :attribute: true
        '''
        return typing.cast(typing.Optional[_aws_cdk_aws_sns_ceddda9d.ITopic], jsii.get(self, "notificationTarget"))

    @jsii.member(jsii_name="metric")
    def metric(
        self,
        metric_name: builtins.str,
        *,
        account: typing.Optional[builtins.str] = None,
        color: typing.Optional[builtins.str] = None,
        dimensions_map: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        id: typing.Optional[builtins.str] = None,
        label: typing.Optional[builtins.str] = None,
        period: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        region: typing.Optional[builtins.str] = None,
        stack_account: typing.Optional[builtins.str] = None,
        stack_region: typing.Optional[builtins.str] = None,
        statistic: typing.Optional[builtins.str] = None,
        unit: typing.Optional[_aws_cdk_aws_cloudwatch_ceddda9d.Unit] = None,
        visible: typing.Optional[builtins.bool] = None,
    ) -> _aws_cdk_aws_cloudwatch_ceddda9d.Metric:
        '''(experimental) Return the given named metric for this matchmaking configuration.

        :param metric_name: -
        :param account: Account which this metric comes from. Default: - Deployment account.
        :param color: The hex color code, prefixed with '#' (e.g. '#00ff00'), to use when this metric is rendered on a graph. The ``Color`` class has a set of standard colors that can be used here. Default: - Automatic color
        :param dimensions_map: Dimensions of the metric. Default: - No dimensions.
        :param id: Unique identifier for this metric when used in dashboard widgets. The id can be used as a variable to represent this metric in math expressions. Valid characters are letters, numbers, and underscore. The first character must be a lowercase letter. Default: - No ID
        :param label: Label for this metric when added to a Graph in a Dashboard. You can use `dynamic labels <https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/graph-dynamic-labels.html>`_ to show summary information about the entire displayed time series in the legend. For example, if you use:: [max: ${MAX}] MyMetric As the metric label, the maximum value in the visible range will be shown next to the time series name in the graph's legend. Default: - No label
        :param period: The period over which the specified statistic is applied. Default: Duration.minutes(5)
        :param region: Region which this metric comes from. Default: - Deployment region.
        :param stack_account: Account of the stack this metric is attached to. Default: - Deployment account.
        :param stack_region: Region of the stack this metric is attached to. Default: - Deployment region.
        :param statistic: What function to use for aggregating. Use the ``aws_cloudwatch.Stats`` helper class to construct valid input strings. Can be one of the following: - "Minimum" | "min" - "Maximum" | "max" - "Average" | "avg" - "Sum" | "sum" - "SampleCount | "n" - "pNN.NN" - "tmNN.NN" | "tm(NN.NN%:NN.NN%)" - "iqm" - "wmNN.NN" | "wm(NN.NN%:NN.NN%)" - "tcNN.NN" | "tc(NN.NN%:NN.NN%)" - "tsNN.NN" | "ts(NN.NN%:NN.NN%)" Default: Average
        :param unit: Unit used to filter the metric stream. Only refer to datums emitted to the metric stream with the given unit and ignore all others. Only useful when datums are being emitted to the same metric stream under different units. The default is to use all matric datums in the stream, regardless of unit, which is recommended in nearly all cases. CloudWatch does not honor this property for graphs. Default: - All metric datums in the given metric stream
        :param visible: Whether this metric should be visible in dashboard graphs. Setting this to false is useful when you want to hide raw metrics that are used in math expressions, and show only the expression results. Default: true

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a50e8154463101cfe0acdbd65a141a2f33f32607ac527b4e424e2760e53974f1)
            check_type(argname="argument metric_name", value=metric_name, expected_type=type_hints["metric_name"])
        props = _aws_cdk_aws_cloudwatch_ceddda9d.MetricOptions(
            account=account,
            color=color,
            dimensions_map=dimensions_map,
            id=id,
            label=label,
            period=period,
            region=region,
            stack_account=stack_account,
            stack_region=stack_region,
            statistic=statistic,
            unit=unit,
            visible=visible,
        )

        return typing.cast(_aws_cdk_aws_cloudwatch_ceddda9d.Metric, jsii.invoke(self, "metric", [metric_name, props]))

    @jsii.member(jsii_name="metricCurrentTickets")
    def metric_current_tickets(
        self,
        *,
        account: typing.Optional[builtins.str] = None,
        color: typing.Optional[builtins.str] = None,
        dimensions_map: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        id: typing.Optional[builtins.str] = None,
        label: typing.Optional[builtins.str] = None,
        period: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        region: typing.Optional[builtins.str] = None,
        stack_account: typing.Optional[builtins.str] = None,
        stack_region: typing.Optional[builtins.str] = None,
        statistic: typing.Optional[builtins.str] = None,
        unit: typing.Optional[_aws_cdk_aws_cloudwatch_ceddda9d.Unit] = None,
        visible: typing.Optional[builtins.bool] = None,
    ) -> _aws_cdk_aws_cloudwatch_ceddda9d.Metric:
        '''(experimental) Matchmaking requests currently being processed or waiting to be processed.

        :param account: Account which this metric comes from. Default: - Deployment account.
        :param color: The hex color code, prefixed with '#' (e.g. '#00ff00'), to use when this metric is rendered on a graph. The ``Color`` class has a set of standard colors that can be used here. Default: - Automatic color
        :param dimensions_map: Dimensions of the metric. Default: - No dimensions.
        :param id: Unique identifier for this metric when used in dashboard widgets. The id can be used as a variable to represent this metric in math expressions. Valid characters are letters, numbers, and underscore. The first character must be a lowercase letter. Default: - No ID
        :param label: Label for this metric when added to a Graph in a Dashboard. You can use `dynamic labels <https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/graph-dynamic-labels.html>`_ to show summary information about the entire displayed time series in the legend. For example, if you use:: [max: ${MAX}] MyMetric As the metric label, the maximum value in the visible range will be shown next to the time series name in the graph's legend. Default: - No label
        :param period: The period over which the specified statistic is applied. Default: Duration.minutes(5)
        :param region: Region which this metric comes from. Default: - Deployment region.
        :param stack_account: Account of the stack this metric is attached to. Default: - Deployment account.
        :param stack_region: Region of the stack this metric is attached to. Default: - Deployment region.
        :param statistic: What function to use for aggregating. Use the ``aws_cloudwatch.Stats`` helper class to construct valid input strings. Can be one of the following: - "Minimum" | "min" - "Maximum" | "max" - "Average" | "avg" - "Sum" | "sum" - "SampleCount | "n" - "pNN.NN" - "tmNN.NN" | "tm(NN.NN%:NN.NN%)" - "iqm" - "wmNN.NN" | "wm(NN.NN%:NN.NN%)" - "tcNN.NN" | "tc(NN.NN%:NN.NN%)" - "tsNN.NN" | "ts(NN.NN%:NN.NN%)" Default: Average
        :param unit: Unit used to filter the metric stream. Only refer to datums emitted to the metric stream with the given unit and ignore all others. Only useful when datums are being emitted to the same metric stream under different units. The default is to use all matric datums in the stream, regardless of unit, which is recommended in nearly all cases. CloudWatch does not honor this property for graphs. Default: - All metric datums in the given metric stream
        :param visible: Whether this metric should be visible in dashboard graphs. Setting this to false is useful when you want to hide raw metrics that are used in math expressions, and show only the expression results. Default: true

        :stability: experimental
        '''
        props = _aws_cdk_aws_cloudwatch_ceddda9d.MetricOptions(
            account=account,
            color=color,
            dimensions_map=dimensions_map,
            id=id,
            label=label,
            period=period,
            region=region,
            stack_account=stack_account,
            stack_region=stack_region,
            statistic=statistic,
            unit=unit,
            visible=visible,
        )

        return typing.cast(_aws_cdk_aws_cloudwatch_ceddda9d.Metric, jsii.invoke(self, "metricCurrentTickets", [props]))

    @jsii.member(jsii_name="metricMatchesAccepted")
    def metric_matches_accepted(
        self,
        *,
        account: typing.Optional[builtins.str] = None,
        color: typing.Optional[builtins.str] = None,
        dimensions_map: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        id: typing.Optional[builtins.str] = None,
        label: typing.Optional[builtins.str] = None,
        period: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        region: typing.Optional[builtins.str] = None,
        stack_account: typing.Optional[builtins.str] = None,
        stack_region: typing.Optional[builtins.str] = None,
        statistic: typing.Optional[builtins.str] = None,
        unit: typing.Optional[_aws_cdk_aws_cloudwatch_ceddda9d.Unit] = None,
        visible: typing.Optional[builtins.bool] = None,
    ) -> _aws_cdk_aws_cloudwatch_ceddda9d.Metric:
        '''(experimental) For matchmaking configurations that require acceptance, the potential matches that were accepted since the last report.

        :param account: Account which this metric comes from. Default: - Deployment account.
        :param color: The hex color code, prefixed with '#' (e.g. '#00ff00'), to use when this metric is rendered on a graph. The ``Color`` class has a set of standard colors that can be used here. Default: - Automatic color
        :param dimensions_map: Dimensions of the metric. Default: - No dimensions.
        :param id: Unique identifier for this metric when used in dashboard widgets. The id can be used as a variable to represent this metric in math expressions. Valid characters are letters, numbers, and underscore. The first character must be a lowercase letter. Default: - No ID
        :param label: Label for this metric when added to a Graph in a Dashboard. You can use `dynamic labels <https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/graph-dynamic-labels.html>`_ to show summary information about the entire displayed time series in the legend. For example, if you use:: [max: ${MAX}] MyMetric As the metric label, the maximum value in the visible range will be shown next to the time series name in the graph's legend. Default: - No label
        :param period: The period over which the specified statistic is applied. Default: Duration.minutes(5)
        :param region: Region which this metric comes from. Default: - Deployment region.
        :param stack_account: Account of the stack this metric is attached to. Default: - Deployment account.
        :param stack_region: Region of the stack this metric is attached to. Default: - Deployment region.
        :param statistic: What function to use for aggregating. Use the ``aws_cloudwatch.Stats`` helper class to construct valid input strings. Can be one of the following: - "Minimum" | "min" - "Maximum" | "max" - "Average" | "avg" - "Sum" | "sum" - "SampleCount | "n" - "pNN.NN" - "tmNN.NN" | "tm(NN.NN%:NN.NN%)" - "iqm" - "wmNN.NN" | "wm(NN.NN%:NN.NN%)" - "tcNN.NN" | "tc(NN.NN%:NN.NN%)" - "tsNN.NN" | "ts(NN.NN%:NN.NN%)" Default: Average
        :param unit: Unit used to filter the metric stream. Only refer to datums emitted to the metric stream with the given unit and ignore all others. Only useful when datums are being emitted to the same metric stream under different units. The default is to use all matric datums in the stream, regardless of unit, which is recommended in nearly all cases. CloudWatch does not honor this property for graphs. Default: - All metric datums in the given metric stream
        :param visible: Whether this metric should be visible in dashboard graphs. Setting this to false is useful when you want to hide raw metrics that are used in math expressions, and show only the expression results. Default: true

        :stability: experimental
        '''
        props = _aws_cdk_aws_cloudwatch_ceddda9d.MetricOptions(
            account=account,
            color=color,
            dimensions_map=dimensions_map,
            id=id,
            label=label,
            period=period,
            region=region,
            stack_account=stack_account,
            stack_region=stack_region,
            statistic=statistic,
            unit=unit,
            visible=visible,
        )

        return typing.cast(_aws_cdk_aws_cloudwatch_ceddda9d.Metric, jsii.invoke(self, "metricMatchesAccepted", [props]))

    @jsii.member(jsii_name="metricMatchesCreated")
    def metric_matches_created(
        self,
        *,
        account: typing.Optional[builtins.str] = None,
        color: typing.Optional[builtins.str] = None,
        dimensions_map: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        id: typing.Optional[builtins.str] = None,
        label: typing.Optional[builtins.str] = None,
        period: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        region: typing.Optional[builtins.str] = None,
        stack_account: typing.Optional[builtins.str] = None,
        stack_region: typing.Optional[builtins.str] = None,
        statistic: typing.Optional[builtins.str] = None,
        unit: typing.Optional[_aws_cdk_aws_cloudwatch_ceddda9d.Unit] = None,
        visible: typing.Optional[builtins.bool] = None,
    ) -> _aws_cdk_aws_cloudwatch_ceddda9d.Metric:
        '''(experimental) Potential matches that were created since the last report.

        :param account: Account which this metric comes from. Default: - Deployment account.
        :param color: The hex color code, prefixed with '#' (e.g. '#00ff00'), to use when this metric is rendered on a graph. The ``Color`` class has a set of standard colors that can be used here. Default: - Automatic color
        :param dimensions_map: Dimensions of the metric. Default: - No dimensions.
        :param id: Unique identifier for this metric when used in dashboard widgets. The id can be used as a variable to represent this metric in math expressions. Valid characters are letters, numbers, and underscore. The first character must be a lowercase letter. Default: - No ID
        :param label: Label for this metric when added to a Graph in a Dashboard. You can use `dynamic labels <https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/graph-dynamic-labels.html>`_ to show summary information about the entire displayed time series in the legend. For example, if you use:: [max: ${MAX}] MyMetric As the metric label, the maximum value in the visible range will be shown next to the time series name in the graph's legend. Default: - No label
        :param period: The period over which the specified statistic is applied. Default: Duration.minutes(5)
        :param region: Region which this metric comes from. Default: - Deployment region.
        :param stack_account: Account of the stack this metric is attached to. Default: - Deployment account.
        :param stack_region: Region of the stack this metric is attached to. Default: - Deployment region.
        :param statistic: What function to use for aggregating. Use the ``aws_cloudwatch.Stats`` helper class to construct valid input strings. Can be one of the following: - "Minimum" | "min" - "Maximum" | "max" - "Average" | "avg" - "Sum" | "sum" - "SampleCount | "n" - "pNN.NN" - "tmNN.NN" | "tm(NN.NN%:NN.NN%)" - "iqm" - "wmNN.NN" | "wm(NN.NN%:NN.NN%)" - "tcNN.NN" | "tc(NN.NN%:NN.NN%)" - "tsNN.NN" | "ts(NN.NN%:NN.NN%)" Default: Average
        :param unit: Unit used to filter the metric stream. Only refer to datums emitted to the metric stream with the given unit and ignore all others. Only useful when datums are being emitted to the same metric stream under different units. The default is to use all matric datums in the stream, regardless of unit, which is recommended in nearly all cases. CloudWatch does not honor this property for graphs. Default: - All metric datums in the given metric stream
        :param visible: Whether this metric should be visible in dashboard graphs. Setting this to false is useful when you want to hide raw metrics that are used in math expressions, and show only the expression results. Default: true

        :stability: experimental
        '''
        props = _aws_cdk_aws_cloudwatch_ceddda9d.MetricOptions(
            account=account,
            color=color,
            dimensions_map=dimensions_map,
            id=id,
            label=label,
            period=period,
            region=region,
            stack_account=stack_account,
            stack_region=stack_region,
            statistic=statistic,
            unit=unit,
            visible=visible,
        )

        return typing.cast(_aws_cdk_aws_cloudwatch_ceddda9d.Metric, jsii.invoke(self, "metricMatchesCreated", [props]))

    @jsii.member(jsii_name="metricMatchesPlaced")
    def metric_matches_placed(
        self,
        *,
        account: typing.Optional[builtins.str] = None,
        color: typing.Optional[builtins.str] = None,
        dimensions_map: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        id: typing.Optional[builtins.str] = None,
        label: typing.Optional[builtins.str] = None,
        period: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        region: typing.Optional[builtins.str] = None,
        stack_account: typing.Optional[builtins.str] = None,
        stack_region: typing.Optional[builtins.str] = None,
        statistic: typing.Optional[builtins.str] = None,
        unit: typing.Optional[_aws_cdk_aws_cloudwatch_ceddda9d.Unit] = None,
        visible: typing.Optional[builtins.bool] = None,
    ) -> _aws_cdk_aws_cloudwatch_ceddda9d.Metric:
        '''(experimental) Matches that were successfully placed into a game session since the last report.

        :param account: Account which this metric comes from. Default: - Deployment account.
        :param color: The hex color code, prefixed with '#' (e.g. '#00ff00'), to use when this metric is rendered on a graph. The ``Color`` class has a set of standard colors that can be used here. Default: - Automatic color
        :param dimensions_map: Dimensions of the metric. Default: - No dimensions.
        :param id: Unique identifier for this metric when used in dashboard widgets. The id can be used as a variable to represent this metric in math expressions. Valid characters are letters, numbers, and underscore. The first character must be a lowercase letter. Default: - No ID
        :param label: Label for this metric when added to a Graph in a Dashboard. You can use `dynamic labels <https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/graph-dynamic-labels.html>`_ to show summary information about the entire displayed time series in the legend. For example, if you use:: [max: ${MAX}] MyMetric As the metric label, the maximum value in the visible range will be shown next to the time series name in the graph's legend. Default: - No label
        :param period: The period over which the specified statistic is applied. Default: Duration.minutes(5)
        :param region: Region which this metric comes from. Default: - Deployment region.
        :param stack_account: Account of the stack this metric is attached to. Default: - Deployment account.
        :param stack_region: Region of the stack this metric is attached to. Default: - Deployment region.
        :param statistic: What function to use for aggregating. Use the ``aws_cloudwatch.Stats`` helper class to construct valid input strings. Can be one of the following: - "Minimum" | "min" - "Maximum" | "max" - "Average" | "avg" - "Sum" | "sum" - "SampleCount | "n" - "pNN.NN" - "tmNN.NN" | "tm(NN.NN%:NN.NN%)" - "iqm" - "wmNN.NN" | "wm(NN.NN%:NN.NN%)" - "tcNN.NN" | "tc(NN.NN%:NN.NN%)" - "tsNN.NN" | "ts(NN.NN%:NN.NN%)" Default: Average
        :param unit: Unit used to filter the metric stream. Only refer to datums emitted to the metric stream with the given unit and ignore all others. Only useful when datums are being emitted to the same metric stream under different units. The default is to use all matric datums in the stream, regardless of unit, which is recommended in nearly all cases. CloudWatch does not honor this property for graphs. Default: - All metric datums in the given metric stream
        :param visible: Whether this metric should be visible in dashboard graphs. Setting this to false is useful when you want to hide raw metrics that are used in math expressions, and show only the expression results. Default: true

        :stability: experimental
        '''
        props = _aws_cdk_aws_cloudwatch_ceddda9d.MetricOptions(
            account=account,
            color=color,
            dimensions_map=dimensions_map,
            id=id,
            label=label,
            period=period,
            region=region,
            stack_account=stack_account,
            stack_region=stack_region,
            statistic=statistic,
            unit=unit,
            visible=visible,
        )

        return typing.cast(_aws_cdk_aws_cloudwatch_ceddda9d.Metric, jsii.invoke(self, "metricMatchesPlaced", [props]))

    @jsii.member(jsii_name="metricMatchesRejected")
    def metric_matches_rejected(
        self,
        *,
        account: typing.Optional[builtins.str] = None,
        color: typing.Optional[builtins.str] = None,
        dimensions_map: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        id: typing.Optional[builtins.str] = None,
        label: typing.Optional[builtins.str] = None,
        period: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        region: typing.Optional[builtins.str] = None,
        stack_account: typing.Optional[builtins.str] = None,
        stack_region: typing.Optional[builtins.str] = None,
        statistic: typing.Optional[builtins.str] = None,
        unit: typing.Optional[_aws_cdk_aws_cloudwatch_ceddda9d.Unit] = None,
        visible: typing.Optional[builtins.bool] = None,
    ) -> _aws_cdk_aws_cloudwatch_ceddda9d.Metric:
        '''(experimental) For matchmaking configurations that require acceptance, the potential matches that were rejected by at least one player since the last report.

        :param account: Account which this metric comes from. Default: - Deployment account.
        :param color: The hex color code, prefixed with '#' (e.g. '#00ff00'), to use when this metric is rendered on a graph. The ``Color`` class has a set of standard colors that can be used here. Default: - Automatic color
        :param dimensions_map: Dimensions of the metric. Default: - No dimensions.
        :param id: Unique identifier for this metric when used in dashboard widgets. The id can be used as a variable to represent this metric in math expressions. Valid characters are letters, numbers, and underscore. The first character must be a lowercase letter. Default: - No ID
        :param label: Label for this metric when added to a Graph in a Dashboard. You can use `dynamic labels <https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/graph-dynamic-labels.html>`_ to show summary information about the entire displayed time series in the legend. For example, if you use:: [max: ${MAX}] MyMetric As the metric label, the maximum value in the visible range will be shown next to the time series name in the graph's legend. Default: - No label
        :param period: The period over which the specified statistic is applied. Default: Duration.minutes(5)
        :param region: Region which this metric comes from. Default: - Deployment region.
        :param stack_account: Account of the stack this metric is attached to. Default: - Deployment account.
        :param stack_region: Region of the stack this metric is attached to. Default: - Deployment region.
        :param statistic: What function to use for aggregating. Use the ``aws_cloudwatch.Stats`` helper class to construct valid input strings. Can be one of the following: - "Minimum" | "min" - "Maximum" | "max" - "Average" | "avg" - "Sum" | "sum" - "SampleCount | "n" - "pNN.NN" - "tmNN.NN" | "tm(NN.NN%:NN.NN%)" - "iqm" - "wmNN.NN" | "wm(NN.NN%:NN.NN%)" - "tcNN.NN" | "tc(NN.NN%:NN.NN%)" - "tsNN.NN" | "ts(NN.NN%:NN.NN%)" Default: Average
        :param unit: Unit used to filter the metric stream. Only refer to datums emitted to the metric stream with the given unit and ignore all others. Only useful when datums are being emitted to the same metric stream under different units. The default is to use all matric datums in the stream, regardless of unit, which is recommended in nearly all cases. CloudWatch does not honor this property for graphs. Default: - All metric datums in the given metric stream
        :param visible: Whether this metric should be visible in dashboard graphs. Setting this to false is useful when you want to hide raw metrics that are used in math expressions, and show only the expression results. Default: true

        :stability: experimental
        '''
        props = _aws_cdk_aws_cloudwatch_ceddda9d.MetricOptions(
            account=account,
            color=color,
            dimensions_map=dimensions_map,
            id=id,
            label=label,
            period=period,
            region=region,
            stack_account=stack_account,
            stack_region=stack_region,
            statistic=statistic,
            unit=unit,
            visible=visible,
        )

        return typing.cast(_aws_cdk_aws_cloudwatch_ceddda9d.Metric, jsii.invoke(self, "metricMatchesRejected", [props]))

    @jsii.member(jsii_name="metricPlayersStarted")
    def metric_players_started(
        self,
        *,
        account: typing.Optional[builtins.str] = None,
        color: typing.Optional[builtins.str] = None,
        dimensions_map: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        id: typing.Optional[builtins.str] = None,
        label: typing.Optional[builtins.str] = None,
        period: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        region: typing.Optional[builtins.str] = None,
        stack_account: typing.Optional[builtins.str] = None,
        stack_region: typing.Optional[builtins.str] = None,
        statistic: typing.Optional[builtins.str] = None,
        unit: typing.Optional[_aws_cdk_aws_cloudwatch_ceddda9d.Unit] = None,
        visible: typing.Optional[builtins.bool] = None,
    ) -> _aws_cdk_aws_cloudwatch_ceddda9d.Metric:
        '''(experimental) Players in matchmaking tickets that were added since the last report.

        :param account: Account which this metric comes from. Default: - Deployment account.
        :param color: The hex color code, prefixed with '#' (e.g. '#00ff00'), to use when this metric is rendered on a graph. The ``Color`` class has a set of standard colors that can be used here. Default: - Automatic color
        :param dimensions_map: Dimensions of the metric. Default: - No dimensions.
        :param id: Unique identifier for this metric when used in dashboard widgets. The id can be used as a variable to represent this metric in math expressions. Valid characters are letters, numbers, and underscore. The first character must be a lowercase letter. Default: - No ID
        :param label: Label for this metric when added to a Graph in a Dashboard. You can use `dynamic labels <https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/graph-dynamic-labels.html>`_ to show summary information about the entire displayed time series in the legend. For example, if you use:: [max: ${MAX}] MyMetric As the metric label, the maximum value in the visible range will be shown next to the time series name in the graph's legend. Default: - No label
        :param period: The period over which the specified statistic is applied. Default: Duration.minutes(5)
        :param region: Region which this metric comes from. Default: - Deployment region.
        :param stack_account: Account of the stack this metric is attached to. Default: - Deployment account.
        :param stack_region: Region of the stack this metric is attached to. Default: - Deployment region.
        :param statistic: What function to use for aggregating. Use the ``aws_cloudwatch.Stats`` helper class to construct valid input strings. Can be one of the following: - "Minimum" | "min" - "Maximum" | "max" - "Average" | "avg" - "Sum" | "sum" - "SampleCount | "n" - "pNN.NN" - "tmNN.NN" | "tm(NN.NN%:NN.NN%)" - "iqm" - "wmNN.NN" | "wm(NN.NN%:NN.NN%)" - "tcNN.NN" | "tc(NN.NN%:NN.NN%)" - "tsNN.NN" | "ts(NN.NN%:NN.NN%)" Default: Average
        :param unit: Unit used to filter the metric stream. Only refer to datums emitted to the metric stream with the given unit and ignore all others. Only useful when datums are being emitted to the same metric stream under different units. The default is to use all matric datums in the stream, regardless of unit, which is recommended in nearly all cases. CloudWatch does not honor this property for graphs. Default: - All metric datums in the given metric stream
        :param visible: Whether this metric should be visible in dashboard graphs. Setting this to false is useful when you want to hide raw metrics that are used in math expressions, and show only the expression results. Default: true

        :stability: experimental
        '''
        props = _aws_cdk_aws_cloudwatch_ceddda9d.MetricOptions(
            account=account,
            color=color,
            dimensions_map=dimensions_map,
            id=id,
            label=label,
            period=period,
            region=region,
            stack_account=stack_account,
            stack_region=stack_region,
            statistic=statistic,
            unit=unit,
            visible=visible,
        )

        return typing.cast(_aws_cdk_aws_cloudwatch_ceddda9d.Metric, jsii.invoke(self, "metricPlayersStarted", [props]))

    @jsii.member(jsii_name="metricTimeToMatch")
    def metric_time_to_match(
        self,
        *,
        account: typing.Optional[builtins.str] = None,
        color: typing.Optional[builtins.str] = None,
        dimensions_map: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        id: typing.Optional[builtins.str] = None,
        label: typing.Optional[builtins.str] = None,
        period: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        region: typing.Optional[builtins.str] = None,
        stack_account: typing.Optional[builtins.str] = None,
        stack_region: typing.Optional[builtins.str] = None,
        statistic: typing.Optional[builtins.str] = None,
        unit: typing.Optional[_aws_cdk_aws_cloudwatch_ceddda9d.Unit] = None,
        visible: typing.Optional[builtins.bool] = None,
    ) -> _aws_cdk_aws_cloudwatch_ceddda9d.Metric:
        '''(experimental) For matchmaking requests that were put into a potential match before the last report, the amount of time between ticket creation and potential match creation.

        Units: seconds

        :param account: Account which this metric comes from. Default: - Deployment account.
        :param color: The hex color code, prefixed with '#' (e.g. '#00ff00'), to use when this metric is rendered on a graph. The ``Color`` class has a set of standard colors that can be used here. Default: - Automatic color
        :param dimensions_map: Dimensions of the metric. Default: - No dimensions.
        :param id: Unique identifier for this metric when used in dashboard widgets. The id can be used as a variable to represent this metric in math expressions. Valid characters are letters, numbers, and underscore. The first character must be a lowercase letter. Default: - No ID
        :param label: Label for this metric when added to a Graph in a Dashboard. You can use `dynamic labels <https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/graph-dynamic-labels.html>`_ to show summary information about the entire displayed time series in the legend. For example, if you use:: [max: ${MAX}] MyMetric As the metric label, the maximum value in the visible range will be shown next to the time series name in the graph's legend. Default: - No label
        :param period: The period over which the specified statistic is applied. Default: Duration.minutes(5)
        :param region: Region which this metric comes from. Default: - Deployment region.
        :param stack_account: Account of the stack this metric is attached to. Default: - Deployment account.
        :param stack_region: Region of the stack this metric is attached to. Default: - Deployment region.
        :param statistic: What function to use for aggregating. Use the ``aws_cloudwatch.Stats`` helper class to construct valid input strings. Can be one of the following: - "Minimum" | "min" - "Maximum" | "max" - "Average" | "avg" - "Sum" | "sum" - "SampleCount | "n" - "pNN.NN" - "tmNN.NN" | "tm(NN.NN%:NN.NN%)" - "iqm" - "wmNN.NN" | "wm(NN.NN%:NN.NN%)" - "tcNN.NN" | "tc(NN.NN%:NN.NN%)" - "tsNN.NN" | "ts(NN.NN%:NN.NN%)" Default: Average
        :param unit: Unit used to filter the metric stream. Only refer to datums emitted to the metric stream with the given unit and ignore all others. Only useful when datums are being emitted to the same metric stream under different units. The default is to use all matric datums in the stream, regardless of unit, which is recommended in nearly all cases. CloudWatch does not honor this property for graphs. Default: - All metric datums in the given metric stream
        :param visible: Whether this metric should be visible in dashboard graphs. Setting this to false is useful when you want to hide raw metrics that are used in math expressions, and show only the expression results. Default: true

        :stability: experimental
        '''
        props = _aws_cdk_aws_cloudwatch_ceddda9d.MetricOptions(
            account=account,
            color=color,
            dimensions_map=dimensions_map,
            id=id,
            label=label,
            period=period,
            region=region,
            stack_account=stack_account,
            stack_region=stack_region,
            statistic=statistic,
            unit=unit,
            visible=visible,
        )

        return typing.cast(_aws_cdk_aws_cloudwatch_ceddda9d.Metric, jsii.invoke(self, "metricTimeToMatch", [props]))

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, IMatchmakingConfiguration).__jsii_proxy_class__ = lambda : _IMatchmakingConfigurationProxy


@jsii.interface(jsii_type="@aws-cdk/aws-gamelift-alpha.IMatchmakingRuleSet")
class IMatchmakingRuleSet(_aws_cdk_ceddda9d.IResource, typing_extensions.Protocol):
    '''(experimental) Represents a Gamelift matchmaking ruleset.

    :stability: experimental
    '''

    @builtins.property
    @jsii.member(jsii_name="matchmakingRuleSetArn")
    def matchmaking_rule_set_arn(self) -> builtins.str:
        '''(experimental) The ARN of the ruleSet.

        :stability: experimental
        :attribute: true
        '''
        ...

    @builtins.property
    @jsii.member(jsii_name="matchmakingRuleSetName")
    def matchmaking_rule_set_name(self) -> builtins.str:
        '''(experimental) The unique name of the ruleSet.

        :stability: experimental
        :attribute: true
        '''
        ...

    @jsii.member(jsii_name="metric")
    def metric(
        self,
        metric_name: builtins.str,
        *,
        account: typing.Optional[builtins.str] = None,
        color: typing.Optional[builtins.str] = None,
        dimensions_map: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        id: typing.Optional[builtins.str] = None,
        label: typing.Optional[builtins.str] = None,
        period: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        region: typing.Optional[builtins.str] = None,
        stack_account: typing.Optional[builtins.str] = None,
        stack_region: typing.Optional[builtins.str] = None,
        statistic: typing.Optional[builtins.str] = None,
        unit: typing.Optional[_aws_cdk_aws_cloudwatch_ceddda9d.Unit] = None,
        visible: typing.Optional[builtins.bool] = None,
    ) -> _aws_cdk_aws_cloudwatch_ceddda9d.Metric:
        '''(experimental) Return the given named metric for this matchmaking ruleSet.

        :param metric_name: -
        :param account: Account which this metric comes from. Default: - Deployment account.
        :param color: The hex color code, prefixed with '#' (e.g. '#00ff00'), to use when this metric is rendered on a graph. The ``Color`` class has a set of standard colors that can be used here. Default: - Automatic color
        :param dimensions_map: Dimensions of the metric. Default: - No dimensions.
        :param id: Unique identifier for this metric when used in dashboard widgets. The id can be used as a variable to represent this metric in math expressions. Valid characters are letters, numbers, and underscore. The first character must be a lowercase letter. Default: - No ID
        :param label: Label for this metric when added to a Graph in a Dashboard. You can use `dynamic labels <https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/graph-dynamic-labels.html>`_ to show summary information about the entire displayed time series in the legend. For example, if you use:: [max: ${MAX}] MyMetric As the metric label, the maximum value in the visible range will be shown next to the time series name in the graph's legend. Default: - No label
        :param period: The period over which the specified statistic is applied. Default: Duration.minutes(5)
        :param region: Region which this metric comes from. Default: - Deployment region.
        :param stack_account: Account of the stack this metric is attached to. Default: - Deployment account.
        :param stack_region: Region of the stack this metric is attached to. Default: - Deployment region.
        :param statistic: What function to use for aggregating. Use the ``aws_cloudwatch.Stats`` helper class to construct valid input strings. Can be one of the following: - "Minimum" | "min" - "Maximum" | "max" - "Average" | "avg" - "Sum" | "sum" - "SampleCount | "n" - "pNN.NN" - "tmNN.NN" | "tm(NN.NN%:NN.NN%)" - "iqm" - "wmNN.NN" | "wm(NN.NN%:NN.NN%)" - "tcNN.NN" | "tc(NN.NN%:NN.NN%)" - "tsNN.NN" | "ts(NN.NN%:NN.NN%)" Default: Average
        :param unit: Unit used to filter the metric stream. Only refer to datums emitted to the metric stream with the given unit and ignore all others. Only useful when datums are being emitted to the same metric stream under different units. The default is to use all matric datums in the stream, regardless of unit, which is recommended in nearly all cases. CloudWatch does not honor this property for graphs. Default: - All metric datums in the given metric stream
        :param visible: Whether this metric should be visible in dashboard graphs. Setting this to false is useful when you want to hide raw metrics that are used in math expressions, and show only the expression results. Default: true

        :stability: experimental
        '''
        ...

    @jsii.member(jsii_name="metricRuleEvaluationsFailed")
    def metric_rule_evaluations_failed(
        self,
        *,
        account: typing.Optional[builtins.str] = None,
        color: typing.Optional[builtins.str] = None,
        dimensions_map: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        id: typing.Optional[builtins.str] = None,
        label: typing.Optional[builtins.str] = None,
        period: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        region: typing.Optional[builtins.str] = None,
        stack_account: typing.Optional[builtins.str] = None,
        stack_region: typing.Optional[builtins.str] = None,
        statistic: typing.Optional[builtins.str] = None,
        unit: typing.Optional[_aws_cdk_aws_cloudwatch_ceddda9d.Unit] = None,
        visible: typing.Optional[builtins.bool] = None,
    ) -> _aws_cdk_aws_cloudwatch_ceddda9d.Metric:
        '''(experimental) Rule evaluations during matchmaking that failed since the last report.

        This metric is limited to the top 50 rules.

        :param account: Account which this metric comes from. Default: - Deployment account.
        :param color: The hex color code, prefixed with '#' (e.g. '#00ff00'), to use when this metric is rendered on a graph. The ``Color`` class has a set of standard colors that can be used here. Default: - Automatic color
        :param dimensions_map: Dimensions of the metric. Default: - No dimensions.
        :param id: Unique identifier for this metric when used in dashboard widgets. The id can be used as a variable to represent this metric in math expressions. Valid characters are letters, numbers, and underscore. The first character must be a lowercase letter. Default: - No ID
        :param label: Label for this metric when added to a Graph in a Dashboard. You can use `dynamic labels <https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/graph-dynamic-labels.html>`_ to show summary information about the entire displayed time series in the legend. For example, if you use:: [max: ${MAX}] MyMetric As the metric label, the maximum value in the visible range will be shown next to the time series name in the graph's legend. Default: - No label
        :param period: The period over which the specified statistic is applied. Default: Duration.minutes(5)
        :param region: Region which this metric comes from. Default: - Deployment region.
        :param stack_account: Account of the stack this metric is attached to. Default: - Deployment account.
        :param stack_region: Region of the stack this metric is attached to. Default: - Deployment region.
        :param statistic: What function to use for aggregating. Use the ``aws_cloudwatch.Stats`` helper class to construct valid input strings. Can be one of the following: - "Minimum" | "min" - "Maximum" | "max" - "Average" | "avg" - "Sum" | "sum" - "SampleCount | "n" - "pNN.NN" - "tmNN.NN" | "tm(NN.NN%:NN.NN%)" - "iqm" - "wmNN.NN" | "wm(NN.NN%:NN.NN%)" - "tcNN.NN" | "tc(NN.NN%:NN.NN%)" - "tsNN.NN" | "ts(NN.NN%:NN.NN%)" Default: Average
        :param unit: Unit used to filter the metric stream. Only refer to datums emitted to the metric stream with the given unit and ignore all others. Only useful when datums are being emitted to the same metric stream under different units. The default is to use all matric datums in the stream, regardless of unit, which is recommended in nearly all cases. CloudWatch does not honor this property for graphs. Default: - All metric datums in the given metric stream
        :param visible: Whether this metric should be visible in dashboard graphs. Setting this to false is useful when you want to hide raw metrics that are used in math expressions, and show only the expression results. Default: true

        :stability: experimental
        '''
        ...

    @jsii.member(jsii_name="metricRuleEvaluationsPassed")
    def metric_rule_evaluations_passed(
        self,
        *,
        account: typing.Optional[builtins.str] = None,
        color: typing.Optional[builtins.str] = None,
        dimensions_map: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        id: typing.Optional[builtins.str] = None,
        label: typing.Optional[builtins.str] = None,
        period: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        region: typing.Optional[builtins.str] = None,
        stack_account: typing.Optional[builtins.str] = None,
        stack_region: typing.Optional[builtins.str] = None,
        statistic: typing.Optional[builtins.str] = None,
        unit: typing.Optional[_aws_cdk_aws_cloudwatch_ceddda9d.Unit] = None,
        visible: typing.Optional[builtins.bool] = None,
    ) -> _aws_cdk_aws_cloudwatch_ceddda9d.Metric:
        '''(experimental) Rule evaluations during the matchmaking process that passed since the last report.

        This metric is limited to the top 50 rules.

        :param account: Account which this metric comes from. Default: - Deployment account.
        :param color: The hex color code, prefixed with '#' (e.g. '#00ff00'), to use when this metric is rendered on a graph. The ``Color`` class has a set of standard colors that can be used here. Default: - Automatic color
        :param dimensions_map: Dimensions of the metric. Default: - No dimensions.
        :param id: Unique identifier for this metric when used in dashboard widgets. The id can be used as a variable to represent this metric in math expressions. Valid characters are letters, numbers, and underscore. The first character must be a lowercase letter. Default: - No ID
        :param label: Label for this metric when added to a Graph in a Dashboard. You can use `dynamic labels <https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/graph-dynamic-labels.html>`_ to show summary information about the entire displayed time series in the legend. For example, if you use:: [max: ${MAX}] MyMetric As the metric label, the maximum value in the visible range will be shown next to the time series name in the graph's legend. Default: - No label
        :param period: The period over which the specified statistic is applied. Default: Duration.minutes(5)
        :param region: Region which this metric comes from. Default: - Deployment region.
        :param stack_account: Account of the stack this metric is attached to. Default: - Deployment account.
        :param stack_region: Region of the stack this metric is attached to. Default: - Deployment region.
        :param statistic: What function to use for aggregating. Use the ``aws_cloudwatch.Stats`` helper class to construct valid input strings. Can be one of the following: - "Minimum" | "min" - "Maximum" | "max" - "Average" | "avg" - "Sum" | "sum" - "SampleCount | "n" - "pNN.NN" - "tmNN.NN" | "tm(NN.NN%:NN.NN%)" - "iqm" - "wmNN.NN" | "wm(NN.NN%:NN.NN%)" - "tcNN.NN" | "tc(NN.NN%:NN.NN%)" - "tsNN.NN" | "ts(NN.NN%:NN.NN%)" Default: Average
        :param unit: Unit used to filter the metric stream. Only refer to datums emitted to the metric stream with the given unit and ignore all others. Only useful when datums are being emitted to the same metric stream under different units. The default is to use all matric datums in the stream, regardless of unit, which is recommended in nearly all cases. CloudWatch does not honor this property for graphs. Default: - All metric datums in the given metric stream
        :param visible: Whether this metric should be visible in dashboard graphs. Setting this to false is useful when you want to hide raw metrics that are used in math expressions, and show only the expression results. Default: true

        :stability: experimental
        '''
        ...


class _IMatchmakingRuleSetProxy(
    jsii.proxy_for(_aws_cdk_ceddda9d.IResource), # type: ignore[misc]
):
    '''(experimental) Represents a Gamelift matchmaking ruleset.

    :stability: experimental
    '''

    __jsii_type__: typing.ClassVar[str] = "@aws-cdk/aws-gamelift-alpha.IMatchmakingRuleSet"

    @builtins.property
    @jsii.member(jsii_name="matchmakingRuleSetArn")
    def matchmaking_rule_set_arn(self) -> builtins.str:
        '''(experimental) The ARN of the ruleSet.

        :stability: experimental
        :attribute: true
        '''
        return typing.cast(builtins.str, jsii.get(self, "matchmakingRuleSetArn"))

    @builtins.property
    @jsii.member(jsii_name="matchmakingRuleSetName")
    def matchmaking_rule_set_name(self) -> builtins.str:
        '''(experimental) The unique name of the ruleSet.

        :stability: experimental
        :attribute: true
        '''
        return typing.cast(builtins.str, jsii.get(self, "matchmakingRuleSetName"))

    @jsii.member(jsii_name="metric")
    def metric(
        self,
        metric_name: builtins.str,
        *,
        account: typing.Optional[builtins.str] = None,
        color: typing.Optional[builtins.str] = None,
        dimensions_map: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        id: typing.Optional[builtins.str] = None,
        label: typing.Optional[builtins.str] = None,
        period: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        region: typing.Optional[builtins.str] = None,
        stack_account: typing.Optional[builtins.str] = None,
        stack_region: typing.Optional[builtins.str] = None,
        statistic: typing.Optional[builtins.str] = None,
        unit: typing.Optional[_aws_cdk_aws_cloudwatch_ceddda9d.Unit] = None,
        visible: typing.Optional[builtins.bool] = None,
    ) -> _aws_cdk_aws_cloudwatch_ceddda9d.Metric:
        '''(experimental) Return the given named metric for this matchmaking ruleSet.

        :param metric_name: -
        :param account: Account which this metric comes from. Default: - Deployment account.
        :param color: The hex color code, prefixed with '#' (e.g. '#00ff00'), to use when this metric is rendered on a graph. The ``Color`` class has a set of standard colors that can be used here. Default: - Automatic color
        :param dimensions_map: Dimensions of the metric. Default: - No dimensions.
        :param id: Unique identifier for this metric when used in dashboard widgets. The id can be used as a variable to represent this metric in math expressions. Valid characters are letters, numbers, and underscore. The first character must be a lowercase letter. Default: - No ID
        :param label: Label for this metric when added to a Graph in a Dashboard. You can use `dynamic labels <https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/graph-dynamic-labels.html>`_ to show summary information about the entire displayed time series in the legend. For example, if you use:: [max: ${MAX}] MyMetric As the metric label, the maximum value in the visible range will be shown next to the time series name in the graph's legend. Default: - No label
        :param period: The period over which the specified statistic is applied. Default: Duration.minutes(5)
        :param region: Region which this metric comes from. Default: - Deployment region.
        :param stack_account: Account of the stack this metric is attached to. Default: - Deployment account.
        :param stack_region: Region of the stack this metric is attached to. Default: - Deployment region.
        :param statistic: What function to use for aggregating. Use the ``aws_cloudwatch.Stats`` helper class to construct valid input strings. Can be one of the following: - "Minimum" | "min" - "Maximum" | "max" - "Average" | "avg" - "Sum" | "sum" - "SampleCount | "n" - "pNN.NN" - "tmNN.NN" | "tm(NN.NN%:NN.NN%)" - "iqm" - "wmNN.NN" | "wm(NN.NN%:NN.NN%)" - "tcNN.NN" | "tc(NN.NN%:NN.NN%)" - "tsNN.NN" | "ts(NN.NN%:NN.NN%)" Default: Average
        :param unit: Unit used to filter the metric stream. Only refer to datums emitted to the metric stream with the given unit and ignore all others. Only useful when datums are being emitted to the same metric stream under different units. The default is to use all matric datums in the stream, regardless of unit, which is recommended in nearly all cases. CloudWatch does not honor this property for graphs. Default: - All metric datums in the given metric stream
        :param visible: Whether this metric should be visible in dashboard graphs. Setting this to false is useful when you want to hide raw metrics that are used in math expressions, and show only the expression results. Default: true

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__bb308959f14dabfed37c94209e0915eae0046d24f306489e7e1089933e4ccd89)
            check_type(argname="argument metric_name", value=metric_name, expected_type=type_hints["metric_name"])
        props = _aws_cdk_aws_cloudwatch_ceddda9d.MetricOptions(
            account=account,
            color=color,
            dimensions_map=dimensions_map,
            id=id,
            label=label,
            period=period,
            region=region,
            stack_account=stack_account,
            stack_region=stack_region,
            statistic=statistic,
            unit=unit,
            visible=visible,
        )

        return typing.cast(_aws_cdk_aws_cloudwatch_ceddda9d.Metric, jsii.invoke(self, "metric", [metric_name, props]))

    @jsii.member(jsii_name="metricRuleEvaluationsFailed")
    def metric_rule_evaluations_failed(
        self,
        *,
        account: typing.Optional[builtins.str] = None,
        color: typing.Optional[builtins.str] = None,
        dimensions_map: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        id: typing.Optional[builtins.str] = None,
        label: typing.Optional[builtins.str] = None,
        period: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        region: typing.Optional[builtins.str] = None,
        stack_account: typing.Optional[builtins.str] = None,
        stack_region: typing.Optional[builtins.str] = None,
        statistic: typing.Optional[builtins.str] = None,
        unit: typing.Optional[_aws_cdk_aws_cloudwatch_ceddda9d.Unit] = None,
        visible: typing.Optional[builtins.bool] = None,
    ) -> _aws_cdk_aws_cloudwatch_ceddda9d.Metric:
        '''(experimental) Rule evaluations during matchmaking that failed since the last report.

        This metric is limited to the top 50 rules.

        :param account: Account which this metric comes from. Default: - Deployment account.
        :param color: The hex color code, prefixed with '#' (e.g. '#00ff00'), to use when this metric is rendered on a graph. The ``Color`` class has a set of standard colors that can be used here. Default: - Automatic color
        :param dimensions_map: Dimensions of the metric. Default: - No dimensions.
        :param id: Unique identifier for this metric when used in dashboard widgets. The id can be used as a variable to represent this metric in math expressions. Valid characters are letters, numbers, and underscore. The first character must be a lowercase letter. Default: - No ID
        :param label: Label for this metric when added to a Graph in a Dashboard. You can use `dynamic labels <https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/graph-dynamic-labels.html>`_ to show summary information about the entire displayed time series in the legend. For example, if you use:: [max: ${MAX}] MyMetric As the metric label, the maximum value in the visible range will be shown next to the time series name in the graph's legend. Default: - No label
        :param period: The period over which the specified statistic is applied. Default: Duration.minutes(5)
        :param region: Region which this metric comes from. Default: - Deployment region.
        :param stack_account: Account of the stack this metric is attached to. Default: - Deployment account.
        :param stack_region: Region of the stack this metric is attached to. Default: - Deployment region.
        :param statistic: What function to use for aggregating. Use the ``aws_cloudwatch.Stats`` helper class to construct valid input strings. Can be one of the following: - "Minimum" | "min" - "Maximum" | "max" - "Average" | "avg" - "Sum" | "sum" - "SampleCount | "n" - "pNN.NN" - "tmNN.NN" | "tm(NN.NN%:NN.NN%)" - "iqm" - "wmNN.NN" | "wm(NN.NN%:NN.NN%)" - "tcNN.NN" | "tc(NN.NN%:NN.NN%)" - "tsNN.NN" | "ts(NN.NN%:NN.NN%)" Default: Average
        :param unit: Unit used to filter the metric stream. Only refer to datums emitted to the metric stream with the given unit and ignore all others. Only useful when datums are being emitted to the same metric stream under different units. The default is to use all matric datums in the stream, regardless of unit, which is recommended in nearly all cases. CloudWatch does not honor this property for graphs. Default: - All metric datums in the given metric stream
        :param visible: Whether this metric should be visible in dashboard graphs. Setting this to false is useful when you want to hide raw metrics that are used in math expressions, and show only the expression results. Default: true

        :stability: experimental
        '''
        props = _aws_cdk_aws_cloudwatch_ceddda9d.MetricOptions(
            account=account,
            color=color,
            dimensions_map=dimensions_map,
            id=id,
            label=label,
            period=period,
            region=region,
            stack_account=stack_account,
            stack_region=stack_region,
            statistic=statistic,
            unit=unit,
            visible=visible,
        )

        return typing.cast(_aws_cdk_aws_cloudwatch_ceddda9d.Metric, jsii.invoke(self, "metricRuleEvaluationsFailed", [props]))

    @jsii.member(jsii_name="metricRuleEvaluationsPassed")
    def metric_rule_evaluations_passed(
        self,
        *,
        account: typing.Optional[builtins.str] = None,
        color: typing.Optional[builtins.str] = None,
        dimensions_map: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        id: typing.Optional[builtins.str] = None,
        label: typing.Optional[builtins.str] = None,
        period: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        region: typing.Optional[builtins.str] = None,
        stack_account: typing.Optional[builtins.str] = None,
        stack_region: typing.Optional[builtins.str] = None,
        statistic: typing.Optional[builtins.str] = None,
        unit: typing.Optional[_aws_cdk_aws_cloudwatch_ceddda9d.Unit] = None,
        visible: typing.Optional[builtins.bool] = None,
    ) -> _aws_cdk_aws_cloudwatch_ceddda9d.Metric:
        '''(experimental) Rule evaluations during the matchmaking process that passed since the last report.

        This metric is limited to the top 50 rules.

        :param account: Account which this metric comes from. Default: - Deployment account.
        :param color: The hex color code, prefixed with '#' (e.g. '#00ff00'), to use when this metric is rendered on a graph. The ``Color`` class has a set of standard colors that can be used here. Default: - Automatic color
        :param dimensions_map: Dimensions of the metric. Default: - No dimensions.
        :param id: Unique identifier for this metric when used in dashboard widgets. The id can be used as a variable to represent this metric in math expressions. Valid characters are letters, numbers, and underscore. The first character must be a lowercase letter. Default: - No ID
        :param label: Label for this metric when added to a Graph in a Dashboard. You can use `dynamic labels <https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/graph-dynamic-labels.html>`_ to show summary information about the entire displayed time series in the legend. For example, if you use:: [max: ${MAX}] MyMetric As the metric label, the maximum value in the visible range will be shown next to the time series name in the graph's legend. Default: - No label
        :param period: The period over which the specified statistic is applied. Default: Duration.minutes(5)
        :param region: Region which this metric comes from. Default: - Deployment region.
        :param stack_account: Account of the stack this metric is attached to. Default: - Deployment account.
        :param stack_region: Region of the stack this metric is attached to. Default: - Deployment region.
        :param statistic: What function to use for aggregating. Use the ``aws_cloudwatch.Stats`` helper class to construct valid input strings. Can be one of the following: - "Minimum" | "min" - "Maximum" | "max" - "Average" | "avg" - "Sum" | "sum" - "SampleCount | "n" - "pNN.NN" - "tmNN.NN" | "tm(NN.NN%:NN.NN%)" - "iqm" - "wmNN.NN" | "wm(NN.NN%:NN.NN%)" - "tcNN.NN" | "tc(NN.NN%:NN.NN%)" - "tsNN.NN" | "ts(NN.NN%:NN.NN%)" Default: Average
        :param unit: Unit used to filter the metric stream. Only refer to datums emitted to the metric stream with the given unit and ignore all others. Only useful when datums are being emitted to the same metric stream under different units. The default is to use all matric datums in the stream, regardless of unit, which is recommended in nearly all cases. CloudWatch does not honor this property for graphs. Default: - All metric datums in the given metric stream
        :param visible: Whether this metric should be visible in dashboard graphs. Setting this to false is useful when you want to hide raw metrics that are used in math expressions, and show only the expression results. Default: true

        :stability: experimental
        '''
        props = _aws_cdk_aws_cloudwatch_ceddda9d.MetricOptions(
            account=account,
            color=color,
            dimensions_map=dimensions_map,
            id=id,
            label=label,
            period=period,
            region=region,
            stack_account=stack_account,
            stack_region=stack_region,
            statistic=statistic,
            unit=unit,
            visible=visible,
        )

        return typing.cast(_aws_cdk_aws_cloudwatch_ceddda9d.Metric, jsii.invoke(self, "metricRuleEvaluationsPassed", [props]))

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, IMatchmakingRuleSet).__jsii_proxy_class__ = lambda : _IMatchmakingRuleSetProxy


@jsii.interface(jsii_type="@aws-cdk/aws-gamelift-alpha.IPeer")
class IPeer(typing_extensions.Protocol):
    '''(experimental) Interface for classes that provide the peer-specification parts of an inbound permission.

    :stability: experimental
    '''

    @builtins.property
    @jsii.member(jsii_name="uniqueId")
    def unique_id(self) -> builtins.str:
        '''(experimental) A unique identifier for this connection peer.

        :stability: experimental
        '''
        ...

    @jsii.member(jsii_name="toJson")
    def to_json(self) -> typing.Any:
        '''(experimental) Produce the ingress rule JSON for the given connection.

        :stability: experimental
        '''
        ...


class _IPeerProxy:
    '''(experimental) Interface for classes that provide the peer-specification parts of an inbound permission.

    :stability: experimental
    '''

    __jsii_type__: typing.ClassVar[str] = "@aws-cdk/aws-gamelift-alpha.IPeer"

    @builtins.property
    @jsii.member(jsii_name="uniqueId")
    def unique_id(self) -> builtins.str:
        '''(experimental) A unique identifier for this connection peer.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "uniqueId"))

    @jsii.member(jsii_name="toJson")
    def to_json(self) -> typing.Any:
        '''(experimental) Produce the ingress rule JSON for the given connection.

        :stability: experimental
        '''
        return typing.cast(typing.Any, jsii.invoke(self, "toJson", []))

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, IPeer).__jsii_proxy_class__ = lambda : _IPeerProxy


@jsii.interface(jsii_type="@aws-cdk/aws-gamelift-alpha.IRuleSetBody")
class IRuleSetBody(typing_extensions.Protocol):
    '''(experimental) Interface to represent Matchmaking RuleSet schema.

    :stability: experimental
    '''

    pass


class _IRuleSetBodyProxy:
    '''(experimental) Interface to represent Matchmaking RuleSet schema.

    :stability: experimental
    '''

    __jsii_type__: typing.ClassVar[str] = "@aws-cdk/aws-gamelift-alpha.IRuleSetBody"
    pass

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, IRuleSetBody).__jsii_proxy_class__ = lambda : _IRuleSetBodyProxy


@jsii.interface(jsii_type="@aws-cdk/aws-gamelift-alpha.IRuleSetContent")
class IRuleSetContent(typing_extensions.Protocol):
    '''(experimental) Interface to represent a Matchmaking RuleSet content.

    :stability: experimental
    '''

    @builtins.property
    @jsii.member(jsii_name="content")
    def content(self) -> IRuleSetBody:
        '''(experimental) RuleSet body content.

        :stability: experimental
        :attribute: true
        '''
        ...

    @jsii.member(jsii_name="bind")
    def bind(self, _scope: _constructs_77d1e7e8.Construct) -> "RuleSetBodyConfig":
        '''(experimental) Called when the matchmaking ruleSet is initialized to allow this object to bind to the stack and add resources.

        :param _scope: The binding scope.

        :stability: experimental
        '''
        ...


class _IRuleSetContentProxy:
    '''(experimental) Interface to represent a Matchmaking RuleSet content.

    :stability: experimental
    '''

    __jsii_type__: typing.ClassVar[str] = "@aws-cdk/aws-gamelift-alpha.IRuleSetContent"

    @builtins.property
    @jsii.member(jsii_name="content")
    def content(self) -> IRuleSetBody:
        '''(experimental) RuleSet body content.

        :stability: experimental
        :attribute: true
        '''
        return typing.cast(IRuleSetBody, jsii.get(self, "content"))

    @jsii.member(jsii_name="bind")
    def bind(self, _scope: _constructs_77d1e7e8.Construct) -> "RuleSetBodyConfig":
        '''(experimental) Called when the matchmaking ruleSet is initialized to allow this object to bind to the stack and add resources.

        :param _scope: The binding scope.

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__87a43d24fc90cc52e193a87bea4e3e876df261fb5a71a0e18268bc490d1b487a)
            check_type(argname="argument _scope", value=_scope, expected_type=type_hints["_scope"])
        return typing.cast("RuleSetBodyConfig", jsii.invoke(self, "bind", [_scope]))

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, IRuleSetContent).__jsii_proxy_class__ = lambda : _IRuleSetContentProxy


@jsii.interface(jsii_type="@aws-cdk/aws-gamelift-alpha.IScript")
class IScript(
    _aws_cdk_ceddda9d.IResource,
    _aws_cdk_aws_iam_ceddda9d.IGrantable,
    typing_extensions.Protocol,
):
    '''(experimental) Your configuration and custom game logic for use with Realtime Servers.

    Realtime Servers are provided by GameLift to use instead of a custom-built game server.
    You configure Realtime Servers for your game clients by creating a script using JavaScript,
    and add custom game logic as appropriate to host game sessions for your players.
    You upload the Realtime script to the GameLift service in the Regions where you plan to set up fleets.

    :see: https://docs.aws.amazon.com/gamelift/latest/developerguide/realtime-script-uploading.html
    :stability: experimental
    '''

    @builtins.property
    @jsii.member(jsii_name="scriptArn")
    def script_arn(self) -> builtins.str:
        '''(experimental) The ARN of the realtime server script.

        :stability: experimental
        :attribute: true
        '''
        ...

    @builtins.property
    @jsii.member(jsii_name="scriptId")
    def script_id(self) -> builtins.str:
        '''(experimental) The Identifier of the realtime server script.

        :stability: experimental
        :attribute: true
        '''
        ...


class _IScriptProxy(
    jsii.proxy_for(_aws_cdk_ceddda9d.IResource), # type: ignore[misc]
    jsii.proxy_for(_aws_cdk_aws_iam_ceddda9d.IGrantable), # type: ignore[misc]
):
    '''(experimental) Your configuration and custom game logic for use with Realtime Servers.

    Realtime Servers are provided by GameLift to use instead of a custom-built game server.
    You configure Realtime Servers for your game clients by creating a script using JavaScript,
    and add custom game logic as appropriate to host game sessions for your players.
    You upload the Realtime script to the GameLift service in the Regions where you plan to set up fleets.

    :see: https://docs.aws.amazon.com/gamelift/latest/developerguide/realtime-script-uploading.html
    :stability: experimental
    '''

    __jsii_type__: typing.ClassVar[str] = "@aws-cdk/aws-gamelift-alpha.IScript"

    @builtins.property
    @jsii.member(jsii_name="scriptArn")
    def script_arn(self) -> builtins.str:
        '''(experimental) The ARN of the realtime server script.

        :stability: experimental
        :attribute: true
        '''
        return typing.cast(builtins.str, jsii.get(self, "scriptArn"))

    @builtins.property
    @jsii.member(jsii_name="scriptId")
    def script_id(self) -> builtins.str:
        '''(experimental) The Identifier of the realtime server script.

        :stability: experimental
        :attribute: true
        '''
        return typing.cast(builtins.str, jsii.get(self, "scriptId"))

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, IScript).__jsii_proxy_class__ = lambda : _IScriptProxy


@jsii.data_type(
    jsii_type="@aws-cdk/aws-gamelift-alpha.IngressRule",
    jsii_struct_bases=[],
    name_mapping={"port": "port", "source": "source"},
)
class IngressRule:
    def __init__(self, *, port: "Port", source: IPeer) -> None:
        '''(experimental) A range of IP addresses and port settings that allow inbound traffic to connect to server processes on an instance in a fleet.

        New game sessions are assigned an IP address/port number combination, which must fall into the fleet's allowed ranges.

        Fleets with custom game builds must have permissions explicitly set.
        For Realtime Servers fleets, GameLift automatically opens two port ranges, one for TCP messaging and one for UDP.

        :param port: (experimental) The port range used for ingress traffic.
        :param source: (experimental) A range of allowed IP addresses .

        :stability: experimental
        :exampleMetadata: fixture=_generated

        Example::

            # The code below shows an example of how to instantiate this type.
            # The values are placeholders you should change.
            import aws_cdk.aws_gamelift_alpha as gamelift_alpha
            
            # peer: gamelift_alpha.IPeer
            # port: gamelift_alpha.Port
            
            ingress_rule = gamelift_alpha.IngressRule(
                port=port,
                source=peer
            )
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6510250919afd16d4c4d6bbae10e8435306ebb5e312a6ce7d11e010dc8dd9b63)
            check_type(argname="argument port", value=port, expected_type=type_hints["port"])
            check_type(argname="argument source", value=source, expected_type=type_hints["source"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "port": port,
            "source": source,
        }

    @builtins.property
    def port(self) -> "Port":
        '''(experimental) The port range used for ingress traffic.

        :stability: experimental
        '''
        result = self._values.get("port")
        assert result is not None, "Required property 'port' is missing"
        return typing.cast("Port", result)

    @builtins.property
    def source(self) -> IPeer:
        '''(experimental) A range of allowed IP addresses .

        :stability: experimental
        '''
        result = self._values.get("source")
        assert result is not None, "Required property 'source' is missing"
        return typing.cast(IPeer, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "IngressRule(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@aws-cdk/aws-gamelift-alpha.InstanceDefinition",
    jsii_struct_bases=[],
    name_mapping={"instance_type": "instanceType", "weight": "weight"},
)
class InstanceDefinition:
    def __init__(
        self,
        *,
        instance_type: _aws_cdk_aws_ec2_ceddda9d.InstanceType,
        weight: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''(experimental) An allowed instance type for a game server group.

        All game server groups must have at least two instance types defined for it.
        GameLift FleetIQ periodically evaluates each defined instance type for viability.
        It then updates the Auto Scaling group with the list of viable instance types.

        :param instance_type: (experimental) An Amazon EC2 instance type designation.
        :param weight: (experimental) Instance weighting that indicates how much this instance type contributes to the total capacity of a game server group. Instance weights are used by GameLift FleetIQ to calculate the instance type's cost per unit hour and better identify the most cost-effective options. Default: default value is 1

        :stability: experimental
        :exampleMetadata: fixture=_generated

        Example::

            # The code below shows an example of how to instantiate this type.
            # The values are placeholders you should change.
            import aws_cdk.aws_gamelift_alpha as gamelift_alpha
            from aws_cdk import aws_ec2 as ec2
            
            # instance_type: ec2.InstanceType
            
            instance_definition = gamelift_alpha.InstanceDefinition(
                instance_type=instance_type,
            
                # the properties below are optional
                weight=123
            )
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__38eeb158eee88455262b802bd304c5096c809aafb0994d6be07a78c309eeaba3)
            check_type(argname="argument instance_type", value=instance_type, expected_type=type_hints["instance_type"])
            check_type(argname="argument weight", value=weight, expected_type=type_hints["weight"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "instance_type": instance_type,
        }
        if weight is not None:
            self._values["weight"] = weight

    @builtins.property
    def instance_type(self) -> _aws_cdk_aws_ec2_ceddda9d.InstanceType:
        '''(experimental) An Amazon EC2 instance type designation.

        :stability: experimental
        '''
        result = self._values.get("instance_type")
        assert result is not None, "Required property 'instance_type' is missing"
        return typing.cast(_aws_cdk_aws_ec2_ceddda9d.InstanceType, result)

    @builtins.property
    def weight(self) -> typing.Optional[jsii.Number]:
        '''(experimental) Instance weighting that indicates how much this instance type contributes to the total capacity of a game server group.

        Instance weights are used by GameLift FleetIQ to calculate the instance type's cost per unit hour and better identify the most cost-effective options.

        :default: default value is 1

        :see: https://docs.aws.amazon.com/autoscaling/ec2/userguide/asg-instance-weighting.html
        :stability: experimental
        '''
        result = self._values.get("weight")
        return typing.cast(typing.Optional[jsii.Number], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "InstanceDefinition(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@aws-cdk/aws-gamelift-alpha.Location",
    jsii_struct_bases=[],
    name_mapping={"region": "region", "capacity": "capacity"},
)
class Location:
    def __init__(
        self,
        *,
        region: builtins.str,
        capacity: typing.Optional[typing.Union["LocationCapacity", typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''(experimental) A remote location where a multi-location fleet can deploy EC2 instances for game hosting.

        :param region: (experimental) An AWS Region code.
        :param capacity: (experimental) Current resource capacity settings in a specified fleet or location. The location value might refer to a fleet's remote location or its home Region. Default: no capacity settings on the specified location

        :stability: experimental
        :exampleMetadata: fixture=_generated

        Example::

            # The code below shows an example of how to instantiate this type.
            # The values are placeholders you should change.
            import aws_cdk.aws_gamelift_alpha as gamelift_alpha
            
            location = gamelift_alpha.Location(
                region="region",
            
                # the properties below are optional
                capacity=gamelift_alpha.LocationCapacity(
                    desired_capacity=123,
                    max_size=123,
                    min_size=123
                )
            )
        '''
        if isinstance(capacity, dict):
            capacity = LocationCapacity(**capacity)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__51da9aed387e2484fabd92a592d5c9962664ed75c99f4386aceb3966a4c0bcf6)
            check_type(argname="argument region", value=region, expected_type=type_hints["region"])
            check_type(argname="argument capacity", value=capacity, expected_type=type_hints["capacity"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "region": region,
        }
        if capacity is not None:
            self._values["capacity"] = capacity

    @builtins.property
    def region(self) -> builtins.str:
        '''(experimental) An AWS Region code.

        :stability: experimental
        '''
        result = self._values.get("region")
        assert result is not None, "Required property 'region' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def capacity(self) -> typing.Optional["LocationCapacity"]:
        '''(experimental) Current resource capacity settings in a specified fleet or location.

        The location value might refer to a fleet's remote location or its home Region.

        :default: no capacity settings on the specified location

        :stability: experimental
        '''
        result = self._values.get("capacity")
        return typing.cast(typing.Optional["LocationCapacity"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "Location(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@aws-cdk/aws-gamelift-alpha.LocationCapacity",
    jsii_struct_bases=[],
    name_mapping={
        "desired_capacity": "desiredCapacity",
        "max_size": "maxSize",
        "min_size": "minSize",
    },
)
class LocationCapacity:
    def __init__(
        self,
        *,
        desired_capacity: typing.Optional[jsii.Number] = None,
        max_size: typing.Optional[jsii.Number] = None,
        min_size: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''(experimental) Current resource capacity settings in a specified fleet or location.

        The location value might refer to a fleet's remote location or its home Region.

        :param desired_capacity: (experimental) The number of Amazon EC2 instances you want to maintain in the specified fleet location. This value must fall between the minimum and maximum size limits. Default: the default value is 0
        :param max_size: (experimental) The maximum number of instances that are allowed in the specified fleet location. Default: the default value is 1
        :param min_size: (experimental) The minimum number of instances that are allowed in the specified fleet location. Default: the default value is 0

        :stability: experimental
        :exampleMetadata: infused

        Example::

            # build: gamelift.Build
            
            
            # Locations can be added directly through constructor
            fleet = gamelift.BuildFleet(self, "Game server fleet",
                fleet_name="test-fleet",
                content=build,
                instance_type=ec2.InstanceType.of(ec2.InstanceClass.C4, ec2.InstanceSize.LARGE),
                runtime_configuration=gamelift.RuntimeConfiguration(
                    server_processes=[gamelift.ServerProcess(
                        launch_path="/local/game/GameLiftExampleServer.x86_64"
                    )]
                ),
                locations=[gamelift.Location(
                    region="eu-west-1",
                    capacity=gamelift.LocationCapacity(
                        desired_capacity=5,
                        min_size=2,
                        max_size=10
                    )
                ), gamelift.Location(
                    region="us-east-1",
                    capacity=gamelift.LocationCapacity(
                        desired_capacity=5,
                        min_size=2,
                        max_size=10
                    )
                )]
            )
            
            # Or through dedicated methods
            fleet.add_location("ap-southeast-1", 5, 2, 10)
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d5927ec30cf31c390246d4f5cd91620953cce8312a7fc880d9df8e3c3d66884a)
            check_type(argname="argument desired_capacity", value=desired_capacity, expected_type=type_hints["desired_capacity"])
            check_type(argname="argument max_size", value=max_size, expected_type=type_hints["max_size"])
            check_type(argname="argument min_size", value=min_size, expected_type=type_hints["min_size"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if desired_capacity is not None:
            self._values["desired_capacity"] = desired_capacity
        if max_size is not None:
            self._values["max_size"] = max_size
        if min_size is not None:
            self._values["min_size"] = min_size

    @builtins.property
    def desired_capacity(self) -> typing.Optional[jsii.Number]:
        '''(experimental) The number of Amazon EC2 instances you want to maintain in the specified fleet location.

        This value must fall between the minimum and maximum size limits.

        :default: the default value is 0

        :stability: experimental
        '''
        result = self._values.get("desired_capacity")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def max_size(self) -> typing.Optional[jsii.Number]:
        '''(experimental) The maximum number of instances that are allowed in the specified fleet location.

        :default: the default value is 1

        :stability: experimental
        '''
        result = self._values.get("max_size")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def min_size(self) -> typing.Optional[jsii.Number]:
        '''(experimental) The minimum number of instances that are allowed in the specified fleet location.

        :default: the default value is 0

        :stability: experimental
        '''
        result = self._values.get("min_size")
        return typing.cast(typing.Optional[jsii.Number], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "LocationCapacity(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@aws-cdk/aws-gamelift-alpha.MatchmakingConfigurationAttributes",
    jsii_struct_bases=[],
    name_mapping={
        "matchmaking_configuration_arn": "matchmakingConfigurationArn",
        "matchmaking_configuration_name": "matchmakingConfigurationName",
        "notification_target": "notificationTarget",
    },
)
class MatchmakingConfigurationAttributes:
    def __init__(
        self,
        *,
        matchmaking_configuration_arn: typing.Optional[builtins.str] = None,
        matchmaking_configuration_name: typing.Optional[builtins.str] = None,
        notification_target: typing.Optional[_aws_cdk_aws_sns_ceddda9d.ITopic] = None,
    ) -> None:
        '''(experimental) A full specification of a matchmaking configuration that can be used to import it fluently into the CDK application.

        :param matchmaking_configuration_arn: (experimental) The ARN of the Matchmaking configuration. At least one of ``matchmakingConfigurationArn`` and ``matchmakingConfigurationName`` must be provided. Default: derived from ``matchmakingConfigurationName``.
        :param matchmaking_configuration_name: (experimental) The identifier of the Matchmaking configuration. At least one of ``matchmakingConfigurationName`` and ``matchmakingConfigurationArn`` must be provided. Default: derived from ``matchmakingConfigurationArn``.
        :param notification_target: (experimental) An SNS topic ARN that is set up to receive matchmaking notifications. Default: no notification target binded to imported ressource

        :stability: experimental
        :exampleMetadata: fixture=_generated

        Example::

            # The code below shows an example of how to instantiate this type.
            # The values are placeholders you should change.
            import aws_cdk.aws_gamelift_alpha as gamelift_alpha
            from aws_cdk import aws_sns as sns
            
            # topic: sns.Topic
            
            matchmaking_configuration_attributes = gamelift_alpha.MatchmakingConfigurationAttributes(
                matchmaking_configuration_arn="matchmakingConfigurationArn",
                matchmaking_configuration_name="matchmakingConfigurationName",
                notification_target=topic
            )
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f8840f19ad853f8b5315e04970dd0ce5ff95adb7384a7f49ac85ca98bc687bbe)
            check_type(argname="argument matchmaking_configuration_arn", value=matchmaking_configuration_arn, expected_type=type_hints["matchmaking_configuration_arn"])
            check_type(argname="argument matchmaking_configuration_name", value=matchmaking_configuration_name, expected_type=type_hints["matchmaking_configuration_name"])
            check_type(argname="argument notification_target", value=notification_target, expected_type=type_hints["notification_target"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if matchmaking_configuration_arn is not None:
            self._values["matchmaking_configuration_arn"] = matchmaking_configuration_arn
        if matchmaking_configuration_name is not None:
            self._values["matchmaking_configuration_name"] = matchmaking_configuration_name
        if notification_target is not None:
            self._values["notification_target"] = notification_target

    @builtins.property
    def matchmaking_configuration_arn(self) -> typing.Optional[builtins.str]:
        '''(experimental) The ARN of the Matchmaking configuration.

        At least one of ``matchmakingConfigurationArn`` and ``matchmakingConfigurationName`` must be provided.

        :default: derived from ``matchmakingConfigurationName``.

        :stability: experimental
        '''
        result = self._values.get("matchmaking_configuration_arn")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def matchmaking_configuration_name(self) -> typing.Optional[builtins.str]:
        '''(experimental) The identifier of the Matchmaking configuration.

        At least one of ``matchmakingConfigurationName`` and ``matchmakingConfigurationArn``  must be provided.

        :default: derived from ``matchmakingConfigurationArn``.

        :stability: experimental
        '''
        result = self._values.get("matchmaking_configuration_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def notification_target(self) -> typing.Optional[_aws_cdk_aws_sns_ceddda9d.ITopic]:
        '''(experimental) An SNS topic ARN that is set up to receive matchmaking notifications.

        :default: no notification target binded to imported ressource

        :see: https://docs.aws.amazon.com/gamelift/latest/flexmatchguide/match-notification.html
        :stability: experimental
        '''
        result = self._values.get("notification_target")
        return typing.cast(typing.Optional[_aws_cdk_aws_sns_ceddda9d.ITopic], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "MatchmakingConfigurationAttributes(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.implements(IMatchmakingConfiguration)
class MatchmakingConfigurationBase(
    _aws_cdk_ceddda9d.Resource,
    metaclass=jsii.JSIIAbstractClass,
    jsii_type="@aws-cdk/aws-gamelift-alpha.MatchmakingConfigurationBase",
):
    '''(experimental) Base class for new and imported GameLift Matchmaking configuration.

    :stability: experimental
    :exampleMetadata: fixture=_generated

    Example::

        # The code below shows an example of how to instantiate this type.
        # The values are placeholders you should change.
        import aws_cdk.aws_gamelift_alpha as gamelift_alpha
        from aws_cdk import aws_sns as sns
        
        # topic: sns.Topic
        
        matchmaking_configuration_base = gamelift_alpha.MatchmakingConfigurationBase.from_matchmaking_configuration_attributes(self, "MyMatchmakingConfigurationBase",
            matchmaking_configuration_arn="matchmakingConfigurationArn",
            matchmaking_configuration_name="matchmakingConfigurationName",
            notification_target=topic
        )
    '''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        account: typing.Optional[builtins.str] = None,
        environment_from_arn: typing.Optional[builtins.str] = None,
        physical_name: typing.Optional[builtins.str] = None,
        region: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param account: The AWS account ID this resource belongs to. Default: - the resource is in the same account as the stack it belongs to
        :param environment_from_arn: ARN to deduce region and account from. The ARN is parsed and the account and region are taken from the ARN. This should be used for imported resources. Cannot be supplied together with either ``account`` or ``region``. Default: - take environment from ``account``, ``region`` parameters, or use Stack environment.
        :param physical_name: The value passed in by users to the physical name prop of the resource. - ``undefined`` implies that a physical name will be allocated by CloudFormation during deployment. - a concrete value implies a specific physical name - ``PhysicalName.GENERATE_IF_NEEDED`` is a marker that indicates that a physical will only be generated by the CDK if it is needed for cross-environment references. Otherwise, it will be allocated by CloudFormation. Default: - The physical name will be allocated by CloudFormation at deployment time
        :param region: The AWS region this resource belongs to. Default: - the resource is in the same region as the stack it belongs to
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__179a3e243ff415e081f70b60e1298d914f259d43851a71a98b5fd134edf627aa)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = _aws_cdk_ceddda9d.ResourceProps(
            account=account,
            environment_from_arn=environment_from_arn,
            physical_name=physical_name,
            region=region,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @jsii.member(jsii_name="fromMatchmakingConfigurationAttributes")
    @builtins.classmethod
    def from_matchmaking_configuration_attributes(
        cls,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        matchmaking_configuration_arn: typing.Optional[builtins.str] = None,
        matchmaking_configuration_name: typing.Optional[builtins.str] = None,
        notification_target: typing.Optional[_aws_cdk_aws_sns_ceddda9d.ITopic] = None,
    ) -> IMatchmakingConfiguration:
        '''(experimental) Import an existing matchmaking configuration from its attributes.

        :param scope: -
        :param id: -
        :param matchmaking_configuration_arn: (experimental) The ARN of the Matchmaking configuration. At least one of ``matchmakingConfigurationArn`` and ``matchmakingConfigurationName`` must be provided. Default: derived from ``matchmakingConfigurationName``.
        :param matchmaking_configuration_name: (experimental) The identifier of the Matchmaking configuration. At least one of ``matchmakingConfigurationName`` and ``matchmakingConfigurationArn`` must be provided. Default: derived from ``matchmakingConfigurationArn``.
        :param notification_target: (experimental) An SNS topic ARN that is set up to receive matchmaking notifications. Default: no notification target binded to imported ressource

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7d238ab385dcb4a94ac7158dcf0b7c35d37d1df2b7f2aac4980cdb67fd219833)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        attrs = MatchmakingConfigurationAttributes(
            matchmaking_configuration_arn=matchmaking_configuration_arn,
            matchmaking_configuration_name=matchmaking_configuration_name,
            notification_target=notification_target,
        )

        return typing.cast(IMatchmakingConfiguration, jsii.sinvoke(cls, "fromMatchmakingConfigurationAttributes", [scope, id, attrs]))

    @jsii.member(jsii_name="metric")
    def metric(
        self,
        metric_name: builtins.str,
        *,
        account: typing.Optional[builtins.str] = None,
        color: typing.Optional[builtins.str] = None,
        dimensions_map: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        id: typing.Optional[builtins.str] = None,
        label: typing.Optional[builtins.str] = None,
        period: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        region: typing.Optional[builtins.str] = None,
        stack_account: typing.Optional[builtins.str] = None,
        stack_region: typing.Optional[builtins.str] = None,
        statistic: typing.Optional[builtins.str] = None,
        unit: typing.Optional[_aws_cdk_aws_cloudwatch_ceddda9d.Unit] = None,
        visible: typing.Optional[builtins.bool] = None,
    ) -> _aws_cdk_aws_cloudwatch_ceddda9d.Metric:
        '''(experimental) Return the given named metric for this matchmaking configuration.

        :param metric_name: -
        :param account: Account which this metric comes from. Default: - Deployment account.
        :param color: The hex color code, prefixed with '#' (e.g. '#00ff00'), to use when this metric is rendered on a graph. The ``Color`` class has a set of standard colors that can be used here. Default: - Automatic color
        :param dimensions_map: Dimensions of the metric. Default: - No dimensions.
        :param id: Unique identifier for this metric when used in dashboard widgets. The id can be used as a variable to represent this metric in math expressions. Valid characters are letters, numbers, and underscore. The first character must be a lowercase letter. Default: - No ID
        :param label: Label for this metric when added to a Graph in a Dashboard. You can use `dynamic labels <https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/graph-dynamic-labels.html>`_ to show summary information about the entire displayed time series in the legend. For example, if you use:: [max: ${MAX}] MyMetric As the metric label, the maximum value in the visible range will be shown next to the time series name in the graph's legend. Default: - No label
        :param period: The period over which the specified statistic is applied. Default: Duration.minutes(5)
        :param region: Region which this metric comes from. Default: - Deployment region.
        :param stack_account: Account of the stack this metric is attached to. Default: - Deployment account.
        :param stack_region: Region of the stack this metric is attached to. Default: - Deployment region.
        :param statistic: What function to use for aggregating. Use the ``aws_cloudwatch.Stats`` helper class to construct valid input strings. Can be one of the following: - "Minimum" | "min" - "Maximum" | "max" - "Average" | "avg" - "Sum" | "sum" - "SampleCount | "n" - "pNN.NN" - "tmNN.NN" | "tm(NN.NN%:NN.NN%)" - "iqm" - "wmNN.NN" | "wm(NN.NN%:NN.NN%)" - "tcNN.NN" | "tc(NN.NN%:NN.NN%)" - "tsNN.NN" | "ts(NN.NN%:NN.NN%)" Default: Average
        :param unit: Unit used to filter the metric stream. Only refer to datums emitted to the metric stream with the given unit and ignore all others. Only useful when datums are being emitted to the same metric stream under different units. The default is to use all matric datums in the stream, regardless of unit, which is recommended in nearly all cases. CloudWatch does not honor this property for graphs. Default: - All metric datums in the given metric stream
        :param visible: Whether this metric should be visible in dashboard graphs. Setting this to false is useful when you want to hide raw metrics that are used in math expressions, and show only the expression results. Default: true

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__fb0c4e1998ca3a69efa6e5fb13e4eb602af45edecdd69f97c1a8ed63e0b26a78)
            check_type(argname="argument metric_name", value=metric_name, expected_type=type_hints["metric_name"])
        props = _aws_cdk_aws_cloudwatch_ceddda9d.MetricOptions(
            account=account,
            color=color,
            dimensions_map=dimensions_map,
            id=id,
            label=label,
            period=period,
            region=region,
            stack_account=stack_account,
            stack_region=stack_region,
            statistic=statistic,
            unit=unit,
            visible=visible,
        )

        return typing.cast(_aws_cdk_aws_cloudwatch_ceddda9d.Metric, jsii.invoke(self, "metric", [metric_name, props]))

    @jsii.member(jsii_name="metricCurrentTickets")
    def metric_current_tickets(
        self,
        *,
        account: typing.Optional[builtins.str] = None,
        color: typing.Optional[builtins.str] = None,
        dimensions_map: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        id: typing.Optional[builtins.str] = None,
        label: typing.Optional[builtins.str] = None,
        period: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        region: typing.Optional[builtins.str] = None,
        stack_account: typing.Optional[builtins.str] = None,
        stack_region: typing.Optional[builtins.str] = None,
        statistic: typing.Optional[builtins.str] = None,
        unit: typing.Optional[_aws_cdk_aws_cloudwatch_ceddda9d.Unit] = None,
        visible: typing.Optional[builtins.bool] = None,
    ) -> _aws_cdk_aws_cloudwatch_ceddda9d.Metric:
        '''(experimental) Matchmaking requests currently being processed or waiting to be processed.

        :param account: Account which this metric comes from. Default: - Deployment account.
        :param color: The hex color code, prefixed with '#' (e.g. '#00ff00'), to use when this metric is rendered on a graph. The ``Color`` class has a set of standard colors that can be used here. Default: - Automatic color
        :param dimensions_map: Dimensions of the metric. Default: - No dimensions.
        :param id: Unique identifier for this metric when used in dashboard widgets. The id can be used as a variable to represent this metric in math expressions. Valid characters are letters, numbers, and underscore. The first character must be a lowercase letter. Default: - No ID
        :param label: Label for this metric when added to a Graph in a Dashboard. You can use `dynamic labels <https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/graph-dynamic-labels.html>`_ to show summary information about the entire displayed time series in the legend. For example, if you use:: [max: ${MAX}] MyMetric As the metric label, the maximum value in the visible range will be shown next to the time series name in the graph's legend. Default: - No label
        :param period: The period over which the specified statistic is applied. Default: Duration.minutes(5)
        :param region: Region which this metric comes from. Default: - Deployment region.
        :param stack_account: Account of the stack this metric is attached to. Default: - Deployment account.
        :param stack_region: Region of the stack this metric is attached to. Default: - Deployment region.
        :param statistic: What function to use for aggregating. Use the ``aws_cloudwatch.Stats`` helper class to construct valid input strings. Can be one of the following: - "Minimum" | "min" - "Maximum" | "max" - "Average" | "avg" - "Sum" | "sum" - "SampleCount | "n" - "pNN.NN" - "tmNN.NN" | "tm(NN.NN%:NN.NN%)" - "iqm" - "wmNN.NN" | "wm(NN.NN%:NN.NN%)" - "tcNN.NN" | "tc(NN.NN%:NN.NN%)" - "tsNN.NN" | "ts(NN.NN%:NN.NN%)" Default: Average
        :param unit: Unit used to filter the metric stream. Only refer to datums emitted to the metric stream with the given unit and ignore all others. Only useful when datums are being emitted to the same metric stream under different units. The default is to use all matric datums in the stream, regardless of unit, which is recommended in nearly all cases. CloudWatch does not honor this property for graphs. Default: - All metric datums in the given metric stream
        :param visible: Whether this metric should be visible in dashboard graphs. Setting this to false is useful when you want to hide raw metrics that are used in math expressions, and show only the expression results. Default: true

        :stability: experimental
        '''
        props = _aws_cdk_aws_cloudwatch_ceddda9d.MetricOptions(
            account=account,
            color=color,
            dimensions_map=dimensions_map,
            id=id,
            label=label,
            period=period,
            region=region,
            stack_account=stack_account,
            stack_region=stack_region,
            statistic=statistic,
            unit=unit,
            visible=visible,
        )

        return typing.cast(_aws_cdk_aws_cloudwatch_ceddda9d.Metric, jsii.invoke(self, "metricCurrentTickets", [props]))

    @jsii.member(jsii_name="metricMatchesAccepted")
    def metric_matches_accepted(
        self,
        *,
        account: typing.Optional[builtins.str] = None,
        color: typing.Optional[builtins.str] = None,
        dimensions_map: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        id: typing.Optional[builtins.str] = None,
        label: typing.Optional[builtins.str] = None,
        period: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        region: typing.Optional[builtins.str] = None,
        stack_account: typing.Optional[builtins.str] = None,
        stack_region: typing.Optional[builtins.str] = None,
        statistic: typing.Optional[builtins.str] = None,
        unit: typing.Optional[_aws_cdk_aws_cloudwatch_ceddda9d.Unit] = None,
        visible: typing.Optional[builtins.bool] = None,
    ) -> _aws_cdk_aws_cloudwatch_ceddda9d.Metric:
        '''(experimental) For matchmaking configurations that require acceptance, the potential matches that were accepted since the last report.

        :param account: Account which this metric comes from. Default: - Deployment account.
        :param color: The hex color code, prefixed with '#' (e.g. '#00ff00'), to use when this metric is rendered on a graph. The ``Color`` class has a set of standard colors that can be used here. Default: - Automatic color
        :param dimensions_map: Dimensions of the metric. Default: - No dimensions.
        :param id: Unique identifier for this metric when used in dashboard widgets. The id can be used as a variable to represent this metric in math expressions. Valid characters are letters, numbers, and underscore. The first character must be a lowercase letter. Default: - No ID
        :param label: Label for this metric when added to a Graph in a Dashboard. You can use `dynamic labels <https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/graph-dynamic-labels.html>`_ to show summary information about the entire displayed time series in the legend. For example, if you use:: [max: ${MAX}] MyMetric As the metric label, the maximum value in the visible range will be shown next to the time series name in the graph's legend. Default: - No label
        :param period: The period over which the specified statistic is applied. Default: Duration.minutes(5)
        :param region: Region which this metric comes from. Default: - Deployment region.
        :param stack_account: Account of the stack this metric is attached to. Default: - Deployment account.
        :param stack_region: Region of the stack this metric is attached to. Default: - Deployment region.
        :param statistic: What function to use for aggregating. Use the ``aws_cloudwatch.Stats`` helper class to construct valid input strings. Can be one of the following: - "Minimum" | "min" - "Maximum" | "max" - "Average" | "avg" - "Sum" | "sum" - "SampleCount | "n" - "pNN.NN" - "tmNN.NN" | "tm(NN.NN%:NN.NN%)" - "iqm" - "wmNN.NN" | "wm(NN.NN%:NN.NN%)" - "tcNN.NN" | "tc(NN.NN%:NN.NN%)" - "tsNN.NN" | "ts(NN.NN%:NN.NN%)" Default: Average
        :param unit: Unit used to filter the metric stream. Only refer to datums emitted to the metric stream with the given unit and ignore all others. Only useful when datums are being emitted to the same metric stream under different units. The default is to use all matric datums in the stream, regardless of unit, which is recommended in nearly all cases. CloudWatch does not honor this property for graphs. Default: - All metric datums in the given metric stream
        :param visible: Whether this metric should be visible in dashboard graphs. Setting this to false is useful when you want to hide raw metrics that are used in math expressions, and show only the expression results. Default: true

        :stability: experimental
        '''
        props = _aws_cdk_aws_cloudwatch_ceddda9d.MetricOptions(
            account=account,
            color=color,
            dimensions_map=dimensions_map,
            id=id,
            label=label,
            period=period,
            region=region,
            stack_account=stack_account,
            stack_region=stack_region,
            statistic=statistic,
            unit=unit,
            visible=visible,
        )

        return typing.cast(_aws_cdk_aws_cloudwatch_ceddda9d.Metric, jsii.invoke(self, "metricMatchesAccepted", [props]))

    @jsii.member(jsii_name="metricMatchesCreated")
    def metric_matches_created(
        self,
        *,
        account: typing.Optional[builtins.str] = None,
        color: typing.Optional[builtins.str] = None,
        dimensions_map: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        id: typing.Optional[builtins.str] = None,
        label: typing.Optional[builtins.str] = None,
        period: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        region: typing.Optional[builtins.str] = None,
        stack_account: typing.Optional[builtins.str] = None,
        stack_region: typing.Optional[builtins.str] = None,
        statistic: typing.Optional[builtins.str] = None,
        unit: typing.Optional[_aws_cdk_aws_cloudwatch_ceddda9d.Unit] = None,
        visible: typing.Optional[builtins.bool] = None,
    ) -> _aws_cdk_aws_cloudwatch_ceddda9d.Metric:
        '''(experimental) Potential matches that were created since the last report.

        :param account: Account which this metric comes from. Default: - Deployment account.
        :param color: The hex color code, prefixed with '#' (e.g. '#00ff00'), to use when this metric is rendered on a graph. The ``Color`` class has a set of standard colors that can be used here. Default: - Automatic color
        :param dimensions_map: Dimensions of the metric. Default: - No dimensions.
        :param id: Unique identifier for this metric when used in dashboard widgets. The id can be used as a variable to represent this metric in math expressions. Valid characters are letters, numbers, and underscore. The first character must be a lowercase letter. Default: - No ID
        :param label: Label for this metric when added to a Graph in a Dashboard. You can use `dynamic labels <https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/graph-dynamic-labels.html>`_ to show summary information about the entire displayed time series in the legend. For example, if you use:: [max: ${MAX}] MyMetric As the metric label, the maximum value in the visible range will be shown next to the time series name in the graph's legend. Default: - No label
        :param period: The period over which the specified statistic is applied. Default: Duration.minutes(5)
        :param region: Region which this metric comes from. Default: - Deployment region.
        :param stack_account: Account of the stack this metric is attached to. Default: - Deployment account.
        :param stack_region: Region of the stack this metric is attached to. Default: - Deployment region.
        :param statistic: What function to use for aggregating. Use the ``aws_cloudwatch.Stats`` helper class to construct valid input strings. Can be one of the following: - "Minimum" | "min" - "Maximum" | "max" - "Average" | "avg" - "Sum" | "sum" - "SampleCount | "n" - "pNN.NN" - "tmNN.NN" | "tm(NN.NN%:NN.NN%)" - "iqm" - "wmNN.NN" | "wm(NN.NN%:NN.NN%)" - "tcNN.NN" | "tc(NN.NN%:NN.NN%)" - "tsNN.NN" | "ts(NN.NN%:NN.NN%)" Default: Average
        :param unit: Unit used to filter the metric stream. Only refer to datums emitted to the metric stream with the given unit and ignore all others. Only useful when datums are being emitted to the same metric stream under different units. The default is to use all matric datums in the stream, regardless of unit, which is recommended in nearly all cases. CloudWatch does not honor this property for graphs. Default: - All metric datums in the given metric stream
        :param visible: Whether this metric should be visible in dashboard graphs. Setting this to false is useful when you want to hide raw metrics that are used in math expressions, and show only the expression results. Default: true

        :stability: experimental
        '''
        props = _aws_cdk_aws_cloudwatch_ceddda9d.MetricOptions(
            account=account,
            color=color,
            dimensions_map=dimensions_map,
            id=id,
            label=label,
            period=period,
            region=region,
            stack_account=stack_account,
            stack_region=stack_region,
            statistic=statistic,
            unit=unit,
            visible=visible,
        )

        return typing.cast(_aws_cdk_aws_cloudwatch_ceddda9d.Metric, jsii.invoke(self, "metricMatchesCreated", [props]))

    @jsii.member(jsii_name="metricMatchesPlaced")
    def metric_matches_placed(
        self,
        *,
        account: typing.Optional[builtins.str] = None,
        color: typing.Optional[builtins.str] = None,
        dimensions_map: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        id: typing.Optional[builtins.str] = None,
        label: typing.Optional[builtins.str] = None,
        period: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        region: typing.Optional[builtins.str] = None,
        stack_account: typing.Optional[builtins.str] = None,
        stack_region: typing.Optional[builtins.str] = None,
        statistic: typing.Optional[builtins.str] = None,
        unit: typing.Optional[_aws_cdk_aws_cloudwatch_ceddda9d.Unit] = None,
        visible: typing.Optional[builtins.bool] = None,
    ) -> _aws_cdk_aws_cloudwatch_ceddda9d.Metric:
        '''(experimental) Matches that were successfully placed into a game session since the last report.

        :param account: Account which this metric comes from. Default: - Deployment account.
        :param color: The hex color code, prefixed with '#' (e.g. '#00ff00'), to use when this metric is rendered on a graph. The ``Color`` class has a set of standard colors that can be used here. Default: - Automatic color
        :param dimensions_map: Dimensions of the metric. Default: - No dimensions.
        :param id: Unique identifier for this metric when used in dashboard widgets. The id can be used as a variable to represent this metric in math expressions. Valid characters are letters, numbers, and underscore. The first character must be a lowercase letter. Default: - No ID
        :param label: Label for this metric when added to a Graph in a Dashboard. You can use `dynamic labels <https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/graph-dynamic-labels.html>`_ to show summary information about the entire displayed time series in the legend. For example, if you use:: [max: ${MAX}] MyMetric As the metric label, the maximum value in the visible range will be shown next to the time series name in the graph's legend. Default: - No label
        :param period: The period over which the specified statistic is applied. Default: Duration.minutes(5)
        :param region: Region which this metric comes from. Default: - Deployment region.
        :param stack_account: Account of the stack this metric is attached to. Default: - Deployment account.
        :param stack_region: Region of the stack this metric is attached to. Default: - Deployment region.
        :param statistic: What function to use for aggregating. Use the ``aws_cloudwatch.Stats`` helper class to construct valid input strings. Can be one of the following: - "Minimum" | "min" - "Maximum" | "max" - "Average" | "avg" - "Sum" | "sum" - "SampleCount | "n" - "pNN.NN" - "tmNN.NN" | "tm(NN.NN%:NN.NN%)" - "iqm" - "wmNN.NN" | "wm(NN.NN%:NN.NN%)" - "tcNN.NN" | "tc(NN.NN%:NN.NN%)" - "tsNN.NN" | "ts(NN.NN%:NN.NN%)" Default: Average
        :param unit: Unit used to filter the metric stream. Only refer to datums emitted to the metric stream with the given unit and ignore all others. Only useful when datums are being emitted to the same metric stream under different units. The default is to use all matric datums in the stream, regardless of unit, which is recommended in nearly all cases. CloudWatch does not honor this property for graphs. Default: - All metric datums in the given metric stream
        :param visible: Whether this metric should be visible in dashboard graphs. Setting this to false is useful when you want to hide raw metrics that are used in math expressions, and show only the expression results. Default: true

        :stability: experimental
        '''
        props = _aws_cdk_aws_cloudwatch_ceddda9d.MetricOptions(
            account=account,
            color=color,
            dimensions_map=dimensions_map,
            id=id,
            label=label,
            period=period,
            region=region,
            stack_account=stack_account,
            stack_region=stack_region,
            statistic=statistic,
            unit=unit,
            visible=visible,
        )

        return typing.cast(_aws_cdk_aws_cloudwatch_ceddda9d.Metric, jsii.invoke(self, "metricMatchesPlaced", [props]))

    @jsii.member(jsii_name="metricMatchesRejected")
    def metric_matches_rejected(
        self,
        *,
        account: typing.Optional[builtins.str] = None,
        color: typing.Optional[builtins.str] = None,
        dimensions_map: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        id: typing.Optional[builtins.str] = None,
        label: typing.Optional[builtins.str] = None,
        period: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        region: typing.Optional[builtins.str] = None,
        stack_account: typing.Optional[builtins.str] = None,
        stack_region: typing.Optional[builtins.str] = None,
        statistic: typing.Optional[builtins.str] = None,
        unit: typing.Optional[_aws_cdk_aws_cloudwatch_ceddda9d.Unit] = None,
        visible: typing.Optional[builtins.bool] = None,
    ) -> _aws_cdk_aws_cloudwatch_ceddda9d.Metric:
        '''(experimental) For matchmaking configurations that require acceptance, the potential matches that were rejected by at least one player since the last report.

        :param account: Account which this metric comes from. Default: - Deployment account.
        :param color: The hex color code, prefixed with '#' (e.g. '#00ff00'), to use when this metric is rendered on a graph. The ``Color`` class has a set of standard colors that can be used here. Default: - Automatic color
        :param dimensions_map: Dimensions of the metric. Default: - No dimensions.
        :param id: Unique identifier for this metric when used in dashboard widgets. The id can be used as a variable to represent this metric in math expressions. Valid characters are letters, numbers, and underscore. The first character must be a lowercase letter. Default: - No ID
        :param label: Label for this metric when added to a Graph in a Dashboard. You can use `dynamic labels <https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/graph-dynamic-labels.html>`_ to show summary information about the entire displayed time series in the legend. For example, if you use:: [max: ${MAX}] MyMetric As the metric label, the maximum value in the visible range will be shown next to the time series name in the graph's legend. Default: - No label
        :param period: The period over which the specified statistic is applied. Default: Duration.minutes(5)
        :param region: Region which this metric comes from. Default: - Deployment region.
        :param stack_account: Account of the stack this metric is attached to. Default: - Deployment account.
        :param stack_region: Region of the stack this metric is attached to. Default: - Deployment region.
        :param statistic: What function to use for aggregating. Use the ``aws_cloudwatch.Stats`` helper class to construct valid input strings. Can be one of the following: - "Minimum" | "min" - "Maximum" | "max" - "Average" | "avg" - "Sum" | "sum" - "SampleCount | "n" - "pNN.NN" - "tmNN.NN" | "tm(NN.NN%:NN.NN%)" - "iqm" - "wmNN.NN" | "wm(NN.NN%:NN.NN%)" - "tcNN.NN" | "tc(NN.NN%:NN.NN%)" - "tsNN.NN" | "ts(NN.NN%:NN.NN%)" Default: Average
        :param unit: Unit used to filter the metric stream. Only refer to datums emitted to the metric stream with the given unit and ignore all others. Only useful when datums are being emitted to the same metric stream under different units. The default is to use all matric datums in the stream, regardless of unit, which is recommended in nearly all cases. CloudWatch does not honor this property for graphs. Default: - All metric datums in the given metric stream
        :param visible: Whether this metric should be visible in dashboard graphs. Setting this to false is useful when you want to hide raw metrics that are used in math expressions, and show only the expression results. Default: true

        :stability: experimental
        '''
        props = _aws_cdk_aws_cloudwatch_ceddda9d.MetricOptions(
            account=account,
            color=color,
            dimensions_map=dimensions_map,
            id=id,
            label=label,
            period=period,
            region=region,
            stack_account=stack_account,
            stack_region=stack_region,
            statistic=statistic,
            unit=unit,
            visible=visible,
        )

        return typing.cast(_aws_cdk_aws_cloudwatch_ceddda9d.Metric, jsii.invoke(self, "metricMatchesRejected", [props]))

    @jsii.member(jsii_name="metricPlayersStarted")
    def metric_players_started(
        self,
        *,
        account: typing.Optional[builtins.str] = None,
        color: typing.Optional[builtins.str] = None,
        dimensions_map: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        id: typing.Optional[builtins.str] = None,
        label: typing.Optional[builtins.str] = None,
        period: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        region: typing.Optional[builtins.str] = None,
        stack_account: typing.Optional[builtins.str] = None,
        stack_region: typing.Optional[builtins.str] = None,
        statistic: typing.Optional[builtins.str] = None,
        unit: typing.Optional[_aws_cdk_aws_cloudwatch_ceddda9d.Unit] = None,
        visible: typing.Optional[builtins.bool] = None,
    ) -> _aws_cdk_aws_cloudwatch_ceddda9d.Metric:
        '''(experimental) Players in matchmaking tickets that were added since the last report.

        :param account: Account which this metric comes from. Default: - Deployment account.
        :param color: The hex color code, prefixed with '#' (e.g. '#00ff00'), to use when this metric is rendered on a graph. The ``Color`` class has a set of standard colors that can be used here. Default: - Automatic color
        :param dimensions_map: Dimensions of the metric. Default: - No dimensions.
        :param id: Unique identifier for this metric when used in dashboard widgets. The id can be used as a variable to represent this metric in math expressions. Valid characters are letters, numbers, and underscore. The first character must be a lowercase letter. Default: - No ID
        :param label: Label for this metric when added to a Graph in a Dashboard. You can use `dynamic labels <https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/graph-dynamic-labels.html>`_ to show summary information about the entire displayed time series in the legend. For example, if you use:: [max: ${MAX}] MyMetric As the metric label, the maximum value in the visible range will be shown next to the time series name in the graph's legend. Default: - No label
        :param period: The period over which the specified statistic is applied. Default: Duration.minutes(5)
        :param region: Region which this metric comes from. Default: - Deployment region.
        :param stack_account: Account of the stack this metric is attached to. Default: - Deployment account.
        :param stack_region: Region of the stack this metric is attached to. Default: - Deployment region.
        :param statistic: What function to use for aggregating. Use the ``aws_cloudwatch.Stats`` helper class to construct valid input strings. Can be one of the following: - "Minimum" | "min" - "Maximum" | "max" - "Average" | "avg" - "Sum" | "sum" - "SampleCount | "n" - "pNN.NN" - "tmNN.NN" | "tm(NN.NN%:NN.NN%)" - "iqm" - "wmNN.NN" | "wm(NN.NN%:NN.NN%)" - "tcNN.NN" | "tc(NN.NN%:NN.NN%)" - "tsNN.NN" | "ts(NN.NN%:NN.NN%)" Default: Average
        :param unit: Unit used to filter the metric stream. Only refer to datums emitted to the metric stream with the given unit and ignore all others. Only useful when datums are being emitted to the same metric stream under different units. The default is to use all matric datums in the stream, regardless of unit, which is recommended in nearly all cases. CloudWatch does not honor this property for graphs. Default: - All metric datums in the given metric stream
        :param visible: Whether this metric should be visible in dashboard graphs. Setting this to false is useful when you want to hide raw metrics that are used in math expressions, and show only the expression results. Default: true

        :stability: experimental
        '''
        props = _aws_cdk_aws_cloudwatch_ceddda9d.MetricOptions(
            account=account,
            color=color,
            dimensions_map=dimensions_map,
            id=id,
            label=label,
            period=period,
            region=region,
            stack_account=stack_account,
            stack_region=stack_region,
            statistic=statistic,
            unit=unit,
            visible=visible,
        )

        return typing.cast(_aws_cdk_aws_cloudwatch_ceddda9d.Metric, jsii.invoke(self, "metricPlayersStarted", [props]))

    @jsii.member(jsii_name="metricTimeToMatch")
    def metric_time_to_match(
        self,
        *,
        account: typing.Optional[builtins.str] = None,
        color: typing.Optional[builtins.str] = None,
        dimensions_map: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        id: typing.Optional[builtins.str] = None,
        label: typing.Optional[builtins.str] = None,
        period: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        region: typing.Optional[builtins.str] = None,
        stack_account: typing.Optional[builtins.str] = None,
        stack_region: typing.Optional[builtins.str] = None,
        statistic: typing.Optional[builtins.str] = None,
        unit: typing.Optional[_aws_cdk_aws_cloudwatch_ceddda9d.Unit] = None,
        visible: typing.Optional[builtins.bool] = None,
    ) -> _aws_cdk_aws_cloudwatch_ceddda9d.Metric:
        '''(experimental) For matchmaking requests that were put into a potential match before the last report, the amount of time between ticket creation and potential match creation.

        Units: seconds

        :param account: Account which this metric comes from. Default: - Deployment account.
        :param color: The hex color code, prefixed with '#' (e.g. '#00ff00'), to use when this metric is rendered on a graph. The ``Color`` class has a set of standard colors that can be used here. Default: - Automatic color
        :param dimensions_map: Dimensions of the metric. Default: - No dimensions.
        :param id: Unique identifier for this metric when used in dashboard widgets. The id can be used as a variable to represent this metric in math expressions. Valid characters are letters, numbers, and underscore. The first character must be a lowercase letter. Default: - No ID
        :param label: Label for this metric when added to a Graph in a Dashboard. You can use `dynamic labels <https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/graph-dynamic-labels.html>`_ to show summary information about the entire displayed time series in the legend. For example, if you use:: [max: ${MAX}] MyMetric As the metric label, the maximum value in the visible range will be shown next to the time series name in the graph's legend. Default: - No label
        :param period: The period over which the specified statistic is applied. Default: Duration.minutes(5)
        :param region: Region which this metric comes from. Default: - Deployment region.
        :param stack_account: Account of the stack this metric is attached to. Default: - Deployment account.
        :param stack_region: Region of the stack this metric is attached to. Default: - Deployment region.
        :param statistic: What function to use for aggregating. Use the ``aws_cloudwatch.Stats`` helper class to construct valid input strings. Can be one of the following: - "Minimum" | "min" - "Maximum" | "max" - "Average" | "avg" - "Sum" | "sum" - "SampleCount | "n" - "pNN.NN" - "tmNN.NN" | "tm(NN.NN%:NN.NN%)" - "iqm" - "wmNN.NN" | "wm(NN.NN%:NN.NN%)" - "tcNN.NN" | "tc(NN.NN%:NN.NN%)" - "tsNN.NN" | "ts(NN.NN%:NN.NN%)" Default: Average
        :param unit: Unit used to filter the metric stream. Only refer to datums emitted to the metric stream with the given unit and ignore all others. Only useful when datums are being emitted to the same metric stream under different units. The default is to use all matric datums in the stream, regardless of unit, which is recommended in nearly all cases. CloudWatch does not honor this property for graphs. Default: - All metric datums in the given metric stream
        :param visible: Whether this metric should be visible in dashboard graphs. Setting this to false is useful when you want to hide raw metrics that are used in math expressions, and show only the expression results. Default: true

        :stability: experimental
        '''
        props = _aws_cdk_aws_cloudwatch_ceddda9d.MetricOptions(
            account=account,
            color=color,
            dimensions_map=dimensions_map,
            id=id,
            label=label,
            period=period,
            region=region,
            stack_account=stack_account,
            stack_region=stack_region,
            statistic=statistic,
            unit=unit,
            visible=visible,
        )

        return typing.cast(_aws_cdk_aws_cloudwatch_ceddda9d.Metric, jsii.invoke(self, "metricTimeToMatch", [props]))

    @builtins.property
    @jsii.member(jsii_name="matchmakingConfigurationArn")
    @abc.abstractmethod
    def matchmaking_configuration_arn(self) -> builtins.str:
        '''(experimental) The ARN of the matchmaking configuration.

        :stability: experimental
        '''
        ...

    @builtins.property
    @jsii.member(jsii_name="matchmakingConfigurationName")
    @abc.abstractmethod
    def matchmaking_configuration_name(self) -> builtins.str:
        '''(experimental) The Identifier of the matchmaking configuration.

        :stability: experimental
        '''
        ...

    @builtins.property
    @jsii.member(jsii_name="notificationTarget")
    @abc.abstractmethod
    def notification_target(self) -> typing.Optional[_aws_cdk_aws_sns_ceddda9d.ITopic]:
        '''(experimental) The notification target for matchmaking events.

        :stability: experimental
        '''
        ...


class _MatchmakingConfigurationBaseProxy(
    MatchmakingConfigurationBase,
    jsii.proxy_for(_aws_cdk_ceddda9d.Resource), # type: ignore[misc]
):
    @builtins.property
    @jsii.member(jsii_name="matchmakingConfigurationArn")
    def matchmaking_configuration_arn(self) -> builtins.str:
        '''(experimental) The ARN of the matchmaking configuration.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "matchmakingConfigurationArn"))

    @builtins.property
    @jsii.member(jsii_name="matchmakingConfigurationName")
    def matchmaking_configuration_name(self) -> builtins.str:
        '''(experimental) The Identifier of the matchmaking configuration.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "matchmakingConfigurationName"))

    @builtins.property
    @jsii.member(jsii_name="notificationTarget")
    def notification_target(self) -> typing.Optional[_aws_cdk_aws_sns_ceddda9d.ITopic]:
        '''(experimental) The notification target for matchmaking events.

        :stability: experimental
        '''
        return typing.cast(typing.Optional[_aws_cdk_aws_sns_ceddda9d.ITopic], jsii.get(self, "notificationTarget"))

# Adding a "__jsii_proxy_class__(): typing.Type" function to the abstract class
typing.cast(typing.Any, MatchmakingConfigurationBase).__jsii_proxy_class__ = lambda : _MatchmakingConfigurationBaseProxy


@jsii.data_type(
    jsii_type="@aws-cdk/aws-gamelift-alpha.MatchmakingConfigurationProps",
    jsii_struct_bases=[],
    name_mapping={
        "matchmaking_configuration_name": "matchmakingConfigurationName",
        "rule_set": "ruleSet",
        "acceptance_timeout": "acceptanceTimeout",
        "custom_event_data": "customEventData",
        "description": "description",
        "notification_target": "notificationTarget",
        "request_timeout": "requestTimeout",
        "require_acceptance": "requireAcceptance",
    },
)
class MatchmakingConfigurationProps:
    def __init__(
        self,
        *,
        matchmaking_configuration_name: builtins.str,
        rule_set: IMatchmakingRuleSet,
        acceptance_timeout: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        custom_event_data: typing.Optional[builtins.str] = None,
        description: typing.Optional[builtins.str] = None,
        notification_target: typing.Optional[_aws_cdk_aws_sns_ceddda9d.ITopic] = None,
        request_timeout: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        require_acceptance: typing.Optional[builtins.bool] = None,
    ) -> None:
        '''(experimental) Properties for a new Gamelift matchmaking configuration.

        :param matchmaking_configuration_name: (experimental) A unique identifier for the matchmaking configuration. This name is used to identify the configuration associated with a matchmaking request or ticket.
        :param rule_set: (experimental) A matchmaking rule set to use with this configuration. A matchmaking configuration can only use rule sets that are defined in the same Region.
        :param acceptance_timeout: (experimental) The length of time (in seconds) to wait for players to accept a proposed match, if acceptance is required. Default: 300 seconds
        :param custom_event_data: (experimental) Information to add to all events related to the matchmaking configuration. Default: no custom data added to events
        :param description: (experimental) A human-readable description of the matchmaking configuration. Default: no description is provided
        :param notification_target: (experimental) An SNS topic ARN that is set up to receive matchmaking notifications. Default: no notification target
        :param request_timeout: (experimental) The maximum duration, that a matchmaking ticket can remain in process before timing out. Requests that fail due to timing out can be resubmitted as needed. Default: 300 seconds
        :param require_acceptance: (experimental) A flag that determines whether a match that was created with this configuration must be accepted by the matched players. With this option enabled, matchmaking tickets use the status ``REQUIRES_ACCEPTANCE`` to indicate when a completed potential match is waiting for player acceptance. Default: Acceptance is not required

        :stability: experimental
        :exampleMetadata: fixture=_generated

        Example::

            # The code below shows an example of how to instantiate this type.
            # The values are placeholders you should change.
            import aws_cdk.aws_gamelift_alpha as gamelift_alpha
            import aws_cdk as cdk
            from aws_cdk import aws_sns as sns
            
            # matchmaking_rule_set: gamelift_alpha.MatchmakingRuleSet
            # topic: sns.Topic
            
            matchmaking_configuration_props = gamelift_alpha.MatchmakingConfigurationProps(
                matchmaking_configuration_name="matchmakingConfigurationName",
                rule_set=matchmaking_rule_set,
            
                # the properties below are optional
                acceptance_timeout=cdk.Duration.minutes(30),
                custom_event_data="customEventData",
                description="description",
                notification_target=topic,
                request_timeout=cdk.Duration.minutes(30),
                require_acceptance=False
            )
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7d2425c20be5f5ce626404bc1ba92acded1944eca3e6a4be3b797bb9371b83f3)
            check_type(argname="argument matchmaking_configuration_name", value=matchmaking_configuration_name, expected_type=type_hints["matchmaking_configuration_name"])
            check_type(argname="argument rule_set", value=rule_set, expected_type=type_hints["rule_set"])
            check_type(argname="argument acceptance_timeout", value=acceptance_timeout, expected_type=type_hints["acceptance_timeout"])
            check_type(argname="argument custom_event_data", value=custom_event_data, expected_type=type_hints["custom_event_data"])
            check_type(argname="argument description", value=description, expected_type=type_hints["description"])
            check_type(argname="argument notification_target", value=notification_target, expected_type=type_hints["notification_target"])
            check_type(argname="argument request_timeout", value=request_timeout, expected_type=type_hints["request_timeout"])
            check_type(argname="argument require_acceptance", value=require_acceptance, expected_type=type_hints["require_acceptance"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "matchmaking_configuration_name": matchmaking_configuration_name,
            "rule_set": rule_set,
        }
        if acceptance_timeout is not None:
            self._values["acceptance_timeout"] = acceptance_timeout
        if custom_event_data is not None:
            self._values["custom_event_data"] = custom_event_data
        if description is not None:
            self._values["description"] = description
        if notification_target is not None:
            self._values["notification_target"] = notification_target
        if request_timeout is not None:
            self._values["request_timeout"] = request_timeout
        if require_acceptance is not None:
            self._values["require_acceptance"] = require_acceptance

    @builtins.property
    def matchmaking_configuration_name(self) -> builtins.str:
        '''(experimental) A unique identifier for the matchmaking configuration.

        This name is used to identify the configuration associated with a matchmaking request or ticket.

        :stability: experimental
        '''
        result = self._values.get("matchmaking_configuration_name")
        assert result is not None, "Required property 'matchmaking_configuration_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def rule_set(self) -> IMatchmakingRuleSet:
        '''(experimental) A matchmaking rule set to use with this configuration.

        A matchmaking configuration can only use rule sets that are defined in the same Region.

        :stability: experimental
        '''
        result = self._values.get("rule_set")
        assert result is not None, "Required property 'rule_set' is missing"
        return typing.cast(IMatchmakingRuleSet, result)

    @builtins.property
    def acceptance_timeout(self) -> typing.Optional[_aws_cdk_ceddda9d.Duration]:
        '''(experimental) The length of time (in seconds) to wait for players to accept a proposed match, if acceptance is required.

        :default: 300 seconds

        :stability: experimental
        '''
        result = self._values.get("acceptance_timeout")
        return typing.cast(typing.Optional[_aws_cdk_ceddda9d.Duration], result)

    @builtins.property
    def custom_event_data(self) -> typing.Optional[builtins.str]:
        '''(experimental) Information to add to all events related to the matchmaking configuration.

        :default: no custom data added to events

        :stability: experimental
        '''
        result = self._values.get("custom_event_data")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        '''(experimental) A human-readable description of the matchmaking configuration.

        :default: no description is provided

        :stability: experimental
        '''
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def notification_target(self) -> typing.Optional[_aws_cdk_aws_sns_ceddda9d.ITopic]:
        '''(experimental) An SNS topic ARN that is set up to receive matchmaking notifications.

        :default: no notification target

        :see: https://docs.aws.amazon.com/gamelift/latest/flexmatchguide/match-notification.html
        :stability: experimental
        '''
        result = self._values.get("notification_target")
        return typing.cast(typing.Optional[_aws_cdk_aws_sns_ceddda9d.ITopic], result)

    @builtins.property
    def request_timeout(self) -> typing.Optional[_aws_cdk_ceddda9d.Duration]:
        '''(experimental) The maximum duration, that a matchmaking ticket can remain in process before timing out.

        Requests that fail due to timing out can be resubmitted as needed.

        :default: 300 seconds

        :stability: experimental
        '''
        result = self._values.get("request_timeout")
        return typing.cast(typing.Optional[_aws_cdk_ceddda9d.Duration], result)

    @builtins.property
    def require_acceptance(self) -> typing.Optional[builtins.bool]:
        '''(experimental) A flag that determines whether a match that was created with this configuration must be accepted by the matched players.

        With this option enabled, matchmaking tickets use the status ``REQUIRES_ACCEPTANCE`` to indicate when a completed potential match is waiting for player acceptance.

        :default: Acceptance is not required

        :stability: experimental
        '''
        result = self._values.get("require_acceptance")
        return typing.cast(typing.Optional[builtins.bool], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "MatchmakingConfigurationProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@aws-cdk/aws-gamelift-alpha.MatchmakingRuleSetAttributes",
    jsii_struct_bases=[],
    name_mapping={
        "matchmaking_rule_set_arn": "matchmakingRuleSetArn",
        "matchmaking_rule_set_name": "matchmakingRuleSetName",
    },
)
class MatchmakingRuleSetAttributes:
    def __init__(
        self,
        *,
        matchmaking_rule_set_arn: typing.Optional[builtins.str] = None,
        matchmaking_rule_set_name: typing.Optional[builtins.str] = None,
    ) -> None:
        '''(experimental) A full specification of a matchmaking ruleSet that can be used to import it fluently into the CDK application.

        :param matchmaking_rule_set_arn: (experimental) The ARN of the matchmaking ruleSet. At least one of ``matchmakingRuleSetArn`` and ``matchmakingRuleSetName`` must be provided. Default: derived from ``matchmakingRuleSetName``.
        :param matchmaking_rule_set_name: (experimental) The unique name of the matchmaking ruleSet. At least one of ``ruleSetName`` and ``matchmakingRuleSetArn`` must be provided. Default: derived from ``matchmakingRuleSetArn``.

        :stability: experimental
        :exampleMetadata: fixture=_generated

        Example::

            # The code below shows an example of how to instantiate this type.
            # The values are placeholders you should change.
            import aws_cdk.aws_gamelift_alpha as gamelift_alpha
            
            matchmaking_rule_set_attributes = gamelift_alpha.MatchmakingRuleSetAttributes(
                matchmaking_rule_set_arn="matchmakingRuleSetArn",
                matchmaking_rule_set_name="matchmakingRuleSetName"
            )
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e72f6b34f251ccf25dc2f85814396b89033d882b6daef2385941c85b9f9a0156)
            check_type(argname="argument matchmaking_rule_set_arn", value=matchmaking_rule_set_arn, expected_type=type_hints["matchmaking_rule_set_arn"])
            check_type(argname="argument matchmaking_rule_set_name", value=matchmaking_rule_set_name, expected_type=type_hints["matchmaking_rule_set_name"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if matchmaking_rule_set_arn is not None:
            self._values["matchmaking_rule_set_arn"] = matchmaking_rule_set_arn
        if matchmaking_rule_set_name is not None:
            self._values["matchmaking_rule_set_name"] = matchmaking_rule_set_name

    @builtins.property
    def matchmaking_rule_set_arn(self) -> typing.Optional[builtins.str]:
        '''(experimental) The ARN of the matchmaking ruleSet.

        At least one of ``matchmakingRuleSetArn`` and ``matchmakingRuleSetName`` must be provided.

        :default: derived from ``matchmakingRuleSetName``.

        :stability: experimental
        '''
        result = self._values.get("matchmaking_rule_set_arn")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def matchmaking_rule_set_name(self) -> typing.Optional[builtins.str]:
        '''(experimental) The unique name of the matchmaking ruleSet.

        At least one of ``ruleSetName`` and ``matchmakingRuleSetArn``  must be provided.

        :default: derived from ``matchmakingRuleSetArn``.

        :stability: experimental
        '''
        result = self._values.get("matchmaking_rule_set_name")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "MatchmakingRuleSetAttributes(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.implements(IMatchmakingRuleSet)
class MatchmakingRuleSetBase(
    _aws_cdk_ceddda9d.Resource,
    metaclass=jsii.JSIIAbstractClass,
    jsii_type="@aws-cdk/aws-gamelift-alpha.MatchmakingRuleSetBase",
):
    '''(experimental) Base class for new and imported GameLift matchmaking ruleSet.

    :stability: experimental
    '''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        account: typing.Optional[builtins.str] = None,
        environment_from_arn: typing.Optional[builtins.str] = None,
        physical_name: typing.Optional[builtins.str] = None,
        region: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param account: The AWS account ID this resource belongs to. Default: - the resource is in the same account as the stack it belongs to
        :param environment_from_arn: ARN to deduce region and account from. The ARN is parsed and the account and region are taken from the ARN. This should be used for imported resources. Cannot be supplied together with either ``account`` or ``region``. Default: - take environment from ``account``, ``region`` parameters, or use Stack environment.
        :param physical_name: The value passed in by users to the physical name prop of the resource. - ``undefined`` implies that a physical name will be allocated by CloudFormation during deployment. - a concrete value implies a specific physical name - ``PhysicalName.GENERATE_IF_NEEDED`` is a marker that indicates that a physical will only be generated by the CDK if it is needed for cross-environment references. Otherwise, it will be allocated by CloudFormation. Default: - The physical name will be allocated by CloudFormation at deployment time
        :param region: The AWS region this resource belongs to. Default: - the resource is in the same region as the stack it belongs to
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__aac55b7eb2aa8da44cfab32e5743d05917cef63fff77ffac643b515b1fe31623)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = _aws_cdk_ceddda9d.ResourceProps(
            account=account,
            environment_from_arn=environment_from_arn,
            physical_name=physical_name,
            region=region,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @jsii.member(jsii_name="metric")
    def metric(
        self,
        metric_name: builtins.str,
        *,
        account: typing.Optional[builtins.str] = None,
        color: typing.Optional[builtins.str] = None,
        dimensions_map: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        id: typing.Optional[builtins.str] = None,
        label: typing.Optional[builtins.str] = None,
        period: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        region: typing.Optional[builtins.str] = None,
        stack_account: typing.Optional[builtins.str] = None,
        stack_region: typing.Optional[builtins.str] = None,
        statistic: typing.Optional[builtins.str] = None,
        unit: typing.Optional[_aws_cdk_aws_cloudwatch_ceddda9d.Unit] = None,
        visible: typing.Optional[builtins.bool] = None,
    ) -> _aws_cdk_aws_cloudwatch_ceddda9d.Metric:
        '''(experimental) Return the given named metric for this matchmaking ruleSet.

        :param metric_name: -
        :param account: Account which this metric comes from. Default: - Deployment account.
        :param color: The hex color code, prefixed with '#' (e.g. '#00ff00'), to use when this metric is rendered on a graph. The ``Color`` class has a set of standard colors that can be used here. Default: - Automatic color
        :param dimensions_map: Dimensions of the metric. Default: - No dimensions.
        :param id: Unique identifier for this metric when used in dashboard widgets. The id can be used as a variable to represent this metric in math expressions. Valid characters are letters, numbers, and underscore. The first character must be a lowercase letter. Default: - No ID
        :param label: Label for this metric when added to a Graph in a Dashboard. You can use `dynamic labels <https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/graph-dynamic-labels.html>`_ to show summary information about the entire displayed time series in the legend. For example, if you use:: [max: ${MAX}] MyMetric As the metric label, the maximum value in the visible range will be shown next to the time series name in the graph's legend. Default: - No label
        :param period: The period over which the specified statistic is applied. Default: Duration.minutes(5)
        :param region: Region which this metric comes from. Default: - Deployment region.
        :param stack_account: Account of the stack this metric is attached to. Default: - Deployment account.
        :param stack_region: Region of the stack this metric is attached to. Default: - Deployment region.
        :param statistic: What function to use for aggregating. Use the ``aws_cloudwatch.Stats`` helper class to construct valid input strings. Can be one of the following: - "Minimum" | "min" - "Maximum" | "max" - "Average" | "avg" - "Sum" | "sum" - "SampleCount | "n" - "pNN.NN" - "tmNN.NN" | "tm(NN.NN%:NN.NN%)" - "iqm" - "wmNN.NN" | "wm(NN.NN%:NN.NN%)" - "tcNN.NN" | "tc(NN.NN%:NN.NN%)" - "tsNN.NN" | "ts(NN.NN%:NN.NN%)" Default: Average
        :param unit: Unit used to filter the metric stream. Only refer to datums emitted to the metric stream with the given unit and ignore all others. Only useful when datums are being emitted to the same metric stream under different units. The default is to use all matric datums in the stream, regardless of unit, which is recommended in nearly all cases. CloudWatch does not honor this property for graphs. Default: - All metric datums in the given metric stream
        :param visible: Whether this metric should be visible in dashboard graphs. Setting this to false is useful when you want to hide raw metrics that are used in math expressions, and show only the expression results. Default: true

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__21e8fcdb8f8c901f59f09a68a217b7ff098b01c5bbee77ad99eca65f22883d1a)
            check_type(argname="argument metric_name", value=metric_name, expected_type=type_hints["metric_name"])
        props = _aws_cdk_aws_cloudwatch_ceddda9d.MetricOptions(
            account=account,
            color=color,
            dimensions_map=dimensions_map,
            id=id,
            label=label,
            period=period,
            region=region,
            stack_account=stack_account,
            stack_region=stack_region,
            statistic=statistic,
            unit=unit,
            visible=visible,
        )

        return typing.cast(_aws_cdk_aws_cloudwatch_ceddda9d.Metric, jsii.invoke(self, "metric", [metric_name, props]))

    @jsii.member(jsii_name="metricRuleEvaluationsFailed")
    def metric_rule_evaluations_failed(
        self,
        *,
        account: typing.Optional[builtins.str] = None,
        color: typing.Optional[builtins.str] = None,
        dimensions_map: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        id: typing.Optional[builtins.str] = None,
        label: typing.Optional[builtins.str] = None,
        period: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        region: typing.Optional[builtins.str] = None,
        stack_account: typing.Optional[builtins.str] = None,
        stack_region: typing.Optional[builtins.str] = None,
        statistic: typing.Optional[builtins.str] = None,
        unit: typing.Optional[_aws_cdk_aws_cloudwatch_ceddda9d.Unit] = None,
        visible: typing.Optional[builtins.bool] = None,
    ) -> _aws_cdk_aws_cloudwatch_ceddda9d.Metric:
        '''(experimental) Rule evaluations during matchmaking that failed since the last report.

        This metric is limited to the top 50 rules.

        :param account: Account which this metric comes from. Default: - Deployment account.
        :param color: The hex color code, prefixed with '#' (e.g. '#00ff00'), to use when this metric is rendered on a graph. The ``Color`` class has a set of standard colors that can be used here. Default: - Automatic color
        :param dimensions_map: Dimensions of the metric. Default: - No dimensions.
        :param id: Unique identifier for this metric when used in dashboard widgets. The id can be used as a variable to represent this metric in math expressions. Valid characters are letters, numbers, and underscore. The first character must be a lowercase letter. Default: - No ID
        :param label: Label for this metric when added to a Graph in a Dashboard. You can use `dynamic labels <https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/graph-dynamic-labels.html>`_ to show summary information about the entire displayed time series in the legend. For example, if you use:: [max: ${MAX}] MyMetric As the metric label, the maximum value in the visible range will be shown next to the time series name in the graph's legend. Default: - No label
        :param period: The period over which the specified statistic is applied. Default: Duration.minutes(5)
        :param region: Region which this metric comes from. Default: - Deployment region.
        :param stack_account: Account of the stack this metric is attached to. Default: - Deployment account.
        :param stack_region: Region of the stack this metric is attached to. Default: - Deployment region.
        :param statistic: What function to use for aggregating. Use the ``aws_cloudwatch.Stats`` helper class to construct valid input strings. Can be one of the following: - "Minimum" | "min" - "Maximum" | "max" - "Average" | "avg" - "Sum" | "sum" - "SampleCount | "n" - "pNN.NN" - "tmNN.NN" | "tm(NN.NN%:NN.NN%)" - "iqm" - "wmNN.NN" | "wm(NN.NN%:NN.NN%)" - "tcNN.NN" | "tc(NN.NN%:NN.NN%)" - "tsNN.NN" | "ts(NN.NN%:NN.NN%)" Default: Average
        :param unit: Unit used to filter the metric stream. Only refer to datums emitted to the metric stream with the given unit and ignore all others. Only useful when datums are being emitted to the same metric stream under different units. The default is to use all matric datums in the stream, regardless of unit, which is recommended in nearly all cases. CloudWatch does not honor this property for graphs. Default: - All metric datums in the given metric stream
        :param visible: Whether this metric should be visible in dashboard graphs. Setting this to false is useful when you want to hide raw metrics that are used in math expressions, and show only the expression results. Default: true

        :stability: experimental
        '''
        props = _aws_cdk_aws_cloudwatch_ceddda9d.MetricOptions(
            account=account,
            color=color,
            dimensions_map=dimensions_map,
            id=id,
            label=label,
            period=period,
            region=region,
            stack_account=stack_account,
            stack_region=stack_region,
            statistic=statistic,
            unit=unit,
            visible=visible,
        )

        return typing.cast(_aws_cdk_aws_cloudwatch_ceddda9d.Metric, jsii.invoke(self, "metricRuleEvaluationsFailed", [props]))

    @jsii.member(jsii_name="metricRuleEvaluationsPassed")
    def metric_rule_evaluations_passed(
        self,
        *,
        account: typing.Optional[builtins.str] = None,
        color: typing.Optional[builtins.str] = None,
        dimensions_map: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        id: typing.Optional[builtins.str] = None,
        label: typing.Optional[builtins.str] = None,
        period: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        region: typing.Optional[builtins.str] = None,
        stack_account: typing.Optional[builtins.str] = None,
        stack_region: typing.Optional[builtins.str] = None,
        statistic: typing.Optional[builtins.str] = None,
        unit: typing.Optional[_aws_cdk_aws_cloudwatch_ceddda9d.Unit] = None,
        visible: typing.Optional[builtins.bool] = None,
    ) -> _aws_cdk_aws_cloudwatch_ceddda9d.Metric:
        '''(experimental) Rule evaluations during the matchmaking process that passed since the last report.

        This metric is limited to the top 50 rules.

        :param account: Account which this metric comes from. Default: - Deployment account.
        :param color: The hex color code, prefixed with '#' (e.g. '#00ff00'), to use when this metric is rendered on a graph. The ``Color`` class has a set of standard colors that can be used here. Default: - Automatic color
        :param dimensions_map: Dimensions of the metric. Default: - No dimensions.
        :param id: Unique identifier for this metric when used in dashboard widgets. The id can be used as a variable to represent this metric in math expressions. Valid characters are letters, numbers, and underscore. The first character must be a lowercase letter. Default: - No ID
        :param label: Label for this metric when added to a Graph in a Dashboard. You can use `dynamic labels <https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/graph-dynamic-labels.html>`_ to show summary information about the entire displayed time series in the legend. For example, if you use:: [max: ${MAX}] MyMetric As the metric label, the maximum value in the visible range will be shown next to the time series name in the graph's legend. Default: - No label
        :param period: The period over which the specified statistic is applied. Default: Duration.minutes(5)
        :param region: Region which this metric comes from. Default: - Deployment region.
        :param stack_account: Account of the stack this metric is attached to. Default: - Deployment account.
        :param stack_region: Region of the stack this metric is attached to. Default: - Deployment region.
        :param statistic: What function to use for aggregating. Use the ``aws_cloudwatch.Stats`` helper class to construct valid input strings. Can be one of the following: - "Minimum" | "min" - "Maximum" | "max" - "Average" | "avg" - "Sum" | "sum" - "SampleCount | "n" - "pNN.NN" - "tmNN.NN" | "tm(NN.NN%:NN.NN%)" - "iqm" - "wmNN.NN" | "wm(NN.NN%:NN.NN%)" - "tcNN.NN" | "tc(NN.NN%:NN.NN%)" - "tsNN.NN" | "ts(NN.NN%:NN.NN%)" Default: Average
        :param unit: Unit used to filter the metric stream. Only refer to datums emitted to the metric stream with the given unit and ignore all others. Only useful when datums are being emitted to the same metric stream under different units. The default is to use all matric datums in the stream, regardless of unit, which is recommended in nearly all cases. CloudWatch does not honor this property for graphs. Default: - All metric datums in the given metric stream
        :param visible: Whether this metric should be visible in dashboard graphs. Setting this to false is useful when you want to hide raw metrics that are used in math expressions, and show only the expression results. Default: true

        :stability: experimental
        '''
        props = _aws_cdk_aws_cloudwatch_ceddda9d.MetricOptions(
            account=account,
            color=color,
            dimensions_map=dimensions_map,
            id=id,
            label=label,
            period=period,
            region=region,
            stack_account=stack_account,
            stack_region=stack_region,
            statistic=statistic,
            unit=unit,
            visible=visible,
        )

        return typing.cast(_aws_cdk_aws_cloudwatch_ceddda9d.Metric, jsii.invoke(self, "metricRuleEvaluationsPassed", [props]))

    @builtins.property
    @jsii.member(jsii_name="matchmakingRuleSetArn")
    @abc.abstractmethod
    def matchmaking_rule_set_arn(self) -> builtins.str:
        '''(experimental) The ARN of the ruleSet.

        :stability: experimental
        '''
        ...

    @builtins.property
    @jsii.member(jsii_name="matchmakingRuleSetName")
    @abc.abstractmethod
    def matchmaking_rule_set_name(self) -> builtins.str:
        '''(experimental) The unique name of the ruleSet.

        :stability: experimental
        '''
        ...


class _MatchmakingRuleSetBaseProxy(
    MatchmakingRuleSetBase,
    jsii.proxy_for(_aws_cdk_ceddda9d.Resource), # type: ignore[misc]
):
    @builtins.property
    @jsii.member(jsii_name="matchmakingRuleSetArn")
    def matchmaking_rule_set_arn(self) -> builtins.str:
        '''(experimental) The ARN of the ruleSet.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "matchmakingRuleSetArn"))

    @builtins.property
    @jsii.member(jsii_name="matchmakingRuleSetName")
    def matchmaking_rule_set_name(self) -> builtins.str:
        '''(experimental) The unique name of the ruleSet.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "matchmakingRuleSetName"))

# Adding a "__jsii_proxy_class__(): typing.Type" function to the abstract class
typing.cast(typing.Any, MatchmakingRuleSetBase).__jsii_proxy_class__ = lambda : _MatchmakingRuleSetBaseProxy


@jsii.data_type(
    jsii_type="@aws-cdk/aws-gamelift-alpha.MatchmakingRuleSetProps",
    jsii_struct_bases=[],
    name_mapping={
        "content": "content",
        "matchmaking_rule_set_name": "matchmakingRuleSetName",
    },
)
class MatchmakingRuleSetProps:
    def __init__(
        self,
        *,
        content: "RuleSetContent",
        matchmaking_rule_set_name: builtins.str,
    ) -> None:
        '''(experimental) Properties for a new matchmaking ruleSet.

        :param content: (experimental) A collection of matchmaking rules.
        :param matchmaking_rule_set_name: (experimental) A unique identifier for the matchmaking rule set. A matchmaking configuration identifies the rule set it uses by this name value. Note: the rule set name is different from the optional name field in the rule set body

        :stability: experimental
        :exampleMetadata: infused

        Example::

            gamelift.MatchmakingRuleSet(self, "RuleSet",
                matchmaking_rule_set_name="my-test-ruleset",
                content=gamelift.RuleSetContent.from_json_file(path.join(__dirname, "my-ruleset", "ruleset.json"))
            )
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__41ee98f07075e0ce2d6c3c1744990e7d34a79e68879b404561d88738e5f22466)
            check_type(argname="argument content", value=content, expected_type=type_hints["content"])
            check_type(argname="argument matchmaking_rule_set_name", value=matchmaking_rule_set_name, expected_type=type_hints["matchmaking_rule_set_name"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "content": content,
            "matchmaking_rule_set_name": matchmaking_rule_set_name,
        }

    @builtins.property
    def content(self) -> "RuleSetContent":
        '''(experimental) A collection of matchmaking rules.

        :stability: experimental
        '''
        result = self._values.get("content")
        assert result is not None, "Required property 'content' is missing"
        return typing.cast("RuleSetContent", result)

    @builtins.property
    def matchmaking_rule_set_name(self) -> builtins.str:
        '''(experimental) A unique identifier for the matchmaking rule set.

        A matchmaking configuration identifies the rule set it uses by this name value.

        Note: the rule set name is different from the optional name field in the rule set body

        :stability: experimental
        '''
        result = self._values.get("matchmaking_rule_set_name")
        assert result is not None, "Required property 'matchmaking_rule_set_name' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "MatchmakingRuleSetProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.enum(jsii_type="@aws-cdk/aws-gamelift-alpha.OperatingSystem")
class OperatingSystem(enum.Enum):
    '''(experimental) The operating system that the game server binaries are built to run on.

    :stability: experimental
    '''

    AMAZON_LINUX = "AMAZON_LINUX"
    '''(experimental) Amazon Linux operating system.

    :stability: experimental
    '''
    AMAZON_LINUX_2 = "AMAZON_LINUX_2"
    '''(experimental) Amazon Linux 2 operating system.

    :stability: experimental
    '''
    AMAZON_LINUX_2023 = "AMAZON_LINUX_2023"
    '''(experimental) Amazon Linux 2023 operating system.

    :stability: experimental
    '''
    WINDOWS_2012 = "WINDOWS_2012"
    '''(deprecated) Windows Server 2012 operating system.

    :deprecated:

    If you have active fleets using the Windows Server 2012 operating system,
    you can continue to create new builds using this OS until October 10, 2023, when Microsoft ends its support.
    All others must use Windows Server 2016 when creating new Windows-based builds.

    :stability: deprecated
    '''
    WINDOWS_2016 = "WINDOWS_2016"
    '''(experimental) Windows Server 2016 operating system.

    :stability: experimental
    '''


class Peer(metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-gamelift-alpha.Peer"):
    '''(experimental) Peer object factories.

    The static methods on this object can be used to create peer objects
    which represent a connection partner in inbound permission rules.

    Use this object if you need to represent connection partners using plain IP addresses.

    :stability: experimental
    :exampleMetadata: infused

    Example::

        # build: gamelift.Build
        
        
        fleet = gamelift.BuildFleet(self, "Game server fleet",
            fleet_name="test-fleet",
            content=build,
            instance_type=ec2.InstanceType.of(ec2.InstanceClass.C4, ec2.InstanceSize.LARGE),
            runtime_configuration=gamelift.RuntimeConfiguration(
                server_processes=[gamelift.ServerProcess(
                    launch_path="/local/game/GameLiftExampleServer.x86_64"
                )]
            ),
            ingress_rules=[gamelift.IngressRule(
                source=gamelift.Peer.any_ipv4(),
                port=gamelift.Port.tcp_range(100, 200)
            )]
        )
        # Allowing a specific CIDR for port 1111 on UDP Protocol
        fleet.add_ingress_rule(gamelift.Peer.ipv4("1.2.3.4/32"), gamelift.Port.udp(1111))
    '''

    def __init__(self) -> None:
        '''
        :stability: experimental
        '''
        jsii.create(self.__class__, self, [])

    @jsii.member(jsii_name="anyIpv4")
    @builtins.classmethod
    def any_ipv4(cls) -> IPeer:
        '''(experimental) Any IPv4 address.

        :stability: experimental
        '''
        return typing.cast(IPeer, jsii.sinvoke(cls, "anyIpv4", []))

    @jsii.member(jsii_name="ipv4")
    @builtins.classmethod
    def ipv4(cls, cidr_ip: builtins.str) -> IPeer:
        '''(experimental) Create an IPv4 peer from a CIDR.

        :param cidr_ip: -

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d9cafda50096fc350f9cc5b1c7ed43f6e6d3c926f878f41e6a1852c233640971)
            check_type(argname="argument cidr_ip", value=cidr_ip, expected_type=type_hints["cidr_ip"])
        return typing.cast(IPeer, jsii.sinvoke(cls, "ipv4", [cidr_ip]))


@jsii.data_type(
    jsii_type="@aws-cdk/aws-gamelift-alpha.PlayerLatencyPolicy",
    jsii_struct_bases=[],
    name_mapping={
        "maximum_individual_player_latency": "maximumIndividualPlayerLatency",
        "policy_duration": "policyDuration",
    },
)
class PlayerLatencyPolicy:
    def __init__(
        self,
        *,
        maximum_individual_player_latency: _aws_cdk_ceddda9d.Duration,
        policy_duration: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
    ) -> None:
        '''(experimental) The queue setting that determines the highest latency allowed for individual players when placing a game session.

        When a latency policy is in force, a game session cannot be placed with any fleet in a Region where a player reports latency higher than the cap.

        Latency policies are only enforced when the placement request contains player latency information.

        :param maximum_individual_player_latency: (experimental) The maximum latency value that is allowed for any player, in milliseconds. All policies must have a value set for this property.
        :param policy_duration: (experimental) The length of time, in seconds, that the policy is enforced while placing a new game session. Default: the policy is enforced until the queue times out.

        :stability: experimental
        :exampleMetadata: fixture=_generated

        Example::

            # The code below shows an example of how to instantiate this type.
            # The values are placeholders you should change.
            import aws_cdk.aws_gamelift_alpha as gamelift_alpha
            import aws_cdk as cdk
            
            player_latency_policy = gamelift_alpha.PlayerLatencyPolicy(
                maximum_individual_player_latency=cdk.Duration.minutes(30),
            
                # the properties below are optional
                policy_duration=cdk.Duration.minutes(30)
            )
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f6e81f6ee2a9d84a1b3aee29befab9a53abe967661221d80eb62a7201a98657e)
            check_type(argname="argument maximum_individual_player_latency", value=maximum_individual_player_latency, expected_type=type_hints["maximum_individual_player_latency"])
            check_type(argname="argument policy_duration", value=policy_duration, expected_type=type_hints["policy_duration"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "maximum_individual_player_latency": maximum_individual_player_latency,
        }
        if policy_duration is not None:
            self._values["policy_duration"] = policy_duration

    @builtins.property
    def maximum_individual_player_latency(self) -> _aws_cdk_ceddda9d.Duration:
        '''(experimental) The maximum latency value that is allowed for any player, in milliseconds.

        All policies must have a value set for this property.

        :stability: experimental
        '''
        result = self._values.get("maximum_individual_player_latency")
        assert result is not None, "Required property 'maximum_individual_player_latency' is missing"
        return typing.cast(_aws_cdk_ceddda9d.Duration, result)

    @builtins.property
    def policy_duration(self) -> typing.Optional[_aws_cdk_ceddda9d.Duration]:
        '''(experimental) The length of time, in seconds, that the policy is enforced while placing a new game session.

        :default: the policy is enforced until the queue times out.

        :stability: experimental
        '''
        result = self._values.get("policy_duration")
        return typing.cast(typing.Optional[_aws_cdk_ceddda9d.Duration], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "PlayerLatencyPolicy(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class Port(metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-gamelift-alpha.Port"):
    '''(experimental) Interface for classes that provide the connection-specification parts of a security group rule.

    :stability: experimental
    :exampleMetadata: infused

    Example::

        # build: gamelift.Build
        
        
        fleet = gamelift.BuildFleet(self, "Game server fleet",
            fleet_name="test-fleet",
            content=build,
            instance_type=ec2.InstanceType.of(ec2.InstanceClass.C4, ec2.InstanceSize.LARGE),
            runtime_configuration=gamelift.RuntimeConfiguration(
                server_processes=[gamelift.ServerProcess(
                    launch_path="/local/game/GameLiftExampleServer.x86_64"
                )]
            ),
            ingress_rules=[gamelift.IngressRule(
                source=gamelift.Peer.any_ipv4(),
                port=gamelift.Port.tcp_range(100, 200)
            )]
        )
        # Allowing a specific CIDR for port 1111 on UDP Protocol
        fleet.add_ingress_rule(gamelift.Peer.ipv4("1.2.3.4/32"), gamelift.Port.udp(1111))
    '''

    def __init__(
        self,
        *,
        from_port: jsii.Number,
        protocol: "Protocol",
        to_port: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param from_port: (experimental) A starting value for a range of allowed port numbers. For fleets using Windows and Linux builds, only ports 1026-60000 are valid.
        :param protocol: (experimental) The protocol for the range.
        :param to_port: (experimental) An ending value for a range of allowed port numbers. Port numbers are end-inclusive. This value must be higher than ``fromPort``. For fleets using Windows and Linux builds, only ports 1026-60000 are valid. Default: the ``fromPort`` value

        :stability: experimental
        '''
        props = PortProps(from_port=from_port, protocol=protocol, to_port=to_port)

        jsii.create(self.__class__, self, [props])

    @jsii.member(jsii_name="allTcp")
    @builtins.classmethod
    def all_tcp(cls) -> "Port":
        '''(experimental) Any TCP traffic.

        :stability: experimental
        '''
        return typing.cast("Port", jsii.sinvoke(cls, "allTcp", []))

    @jsii.member(jsii_name="allUdp")
    @builtins.classmethod
    def all_udp(cls) -> "Port":
        '''(experimental) Any UDP traffic.

        :stability: experimental
        '''
        return typing.cast("Port", jsii.sinvoke(cls, "allUdp", []))

    @jsii.member(jsii_name="tcp")
    @builtins.classmethod
    def tcp(cls, port: jsii.Number) -> "Port":
        '''(experimental) A single TCP port.

        :param port: -

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__807daa8efeb9458bfab28ef1059e4e060051b8f8a89d4cb96ad64f80804283b6)
            check_type(argname="argument port", value=port, expected_type=type_hints["port"])
        return typing.cast("Port", jsii.sinvoke(cls, "tcp", [port]))

    @jsii.member(jsii_name="tcpRange")
    @builtins.classmethod
    def tcp_range(cls, start_port: jsii.Number, end_port: jsii.Number) -> "Port":
        '''(experimental) A TCP port range.

        :param start_port: -
        :param end_port: -

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4f9b17c789979d40f73a7726940c2f66b5a2cf02cdbd1a2da5ba5afa03ebc7ff)
            check_type(argname="argument start_port", value=start_port, expected_type=type_hints["start_port"])
            check_type(argname="argument end_port", value=end_port, expected_type=type_hints["end_port"])
        return typing.cast("Port", jsii.sinvoke(cls, "tcpRange", [start_port, end_port]))

    @jsii.member(jsii_name="udp")
    @builtins.classmethod
    def udp(cls, port: jsii.Number) -> "Port":
        '''(experimental) A single UDP port.

        :param port: -

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8f9736f2e5142a4a1088ef03dcd38685d4abd204bf399b3b6b5b38fd4b7bce1f)
            check_type(argname="argument port", value=port, expected_type=type_hints["port"])
        return typing.cast("Port", jsii.sinvoke(cls, "udp", [port]))

    @jsii.member(jsii_name="udpRange")
    @builtins.classmethod
    def udp_range(cls, start_port: jsii.Number, end_port: jsii.Number) -> "Port":
        '''(experimental) A UDP port range.

        :param start_port: -
        :param end_port: -

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__fbefa015e5d4a84fc309cfdbc4ccad9117e9eea9f7f8c857ad92a9ac5db07ce8)
            check_type(argname="argument start_port", value=start_port, expected_type=type_hints["start_port"])
            check_type(argname="argument end_port", value=end_port, expected_type=type_hints["end_port"])
        return typing.cast("Port", jsii.sinvoke(cls, "udpRange", [start_port, end_port]))

    @jsii.member(jsii_name="toJson")
    def to_json(self) -> typing.Any:
        '''(experimental) Produce the ingress rule JSON for the given connection.

        :stability: experimental
        '''
        return typing.cast(typing.Any, jsii.invoke(self, "toJson", []))


@jsii.data_type(
    jsii_type="@aws-cdk/aws-gamelift-alpha.PortProps",
    jsii_struct_bases=[],
    name_mapping={
        "from_port": "fromPort",
        "protocol": "protocol",
        "to_port": "toPort",
    },
)
class PortProps:
    def __init__(
        self,
        *,
        from_port: jsii.Number,
        protocol: "Protocol",
        to_port: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''(experimental) Properties to create a port range.

        :param from_port: (experimental) A starting value for a range of allowed port numbers. For fleets using Windows and Linux builds, only ports 1026-60000 are valid.
        :param protocol: (experimental) The protocol for the range.
        :param to_port: (experimental) An ending value for a range of allowed port numbers. Port numbers are end-inclusive. This value must be higher than ``fromPort``. For fleets using Windows and Linux builds, only ports 1026-60000 are valid. Default: the ``fromPort`` value

        :stability: experimental
        :exampleMetadata: fixture=_generated

        Example::

            # The code below shows an example of how to instantiate this type.
            # The values are placeholders you should change.
            import aws_cdk.aws_gamelift_alpha as gamelift_alpha
            
            port_props = gamelift_alpha.PortProps(
                from_port=123,
                protocol=gamelift_alpha.Protocol.TCP,
            
                # the properties below are optional
                to_port=123
            )
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__67dc987c67cb3e38e0e5ff1854c8efa93b01f48235e9309346c6a96b55aad13e)
            check_type(argname="argument from_port", value=from_port, expected_type=type_hints["from_port"])
            check_type(argname="argument protocol", value=protocol, expected_type=type_hints["protocol"])
            check_type(argname="argument to_port", value=to_port, expected_type=type_hints["to_port"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "from_port": from_port,
            "protocol": protocol,
        }
        if to_port is not None:
            self._values["to_port"] = to_port

    @builtins.property
    def from_port(self) -> jsii.Number:
        '''(experimental) A starting value for a range of allowed port numbers.

        For fleets using Windows and Linux builds, only ports 1026-60000 are valid.

        :stability: experimental
        '''
        result = self._values.get("from_port")
        assert result is not None, "Required property 'from_port' is missing"
        return typing.cast(jsii.Number, result)

    @builtins.property
    def protocol(self) -> "Protocol":
        '''(experimental) The protocol for the range.

        :stability: experimental
        '''
        result = self._values.get("protocol")
        assert result is not None, "Required property 'protocol' is missing"
        return typing.cast("Protocol", result)

    @builtins.property
    def to_port(self) -> typing.Optional[jsii.Number]:
        '''(experimental) An ending value for a range of allowed port numbers.

        Port numbers are end-inclusive.
        This value must be higher than ``fromPort``.

        For fleets using Windows and Linux builds, only ports 1026-60000 are valid.

        :default: the ``fromPort`` value

        :stability: experimental
        '''
        result = self._values.get("to_port")
        return typing.cast(typing.Optional[jsii.Number], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "PortProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@aws-cdk/aws-gamelift-alpha.PriorityConfiguration",
    jsii_struct_bases=[],
    name_mapping={
        "location_order": "locationOrder",
        "priority_order": "priorityOrder",
    },
)
class PriorityConfiguration:
    def __init__(
        self,
        *,
        location_order: typing.Sequence[builtins.str],
        priority_order: typing.Sequence["PriorityType"],
    ) -> None:
        '''(experimental) Custom prioritization settings for use by a game session queue when placing new game sessions with available game servers.

        When defined, this configuration replaces the default FleetIQ prioritization process, which is as follows:

        - If player latency data is included in a game session request, destinations and locations are prioritized first based on lowest average latency (1), then on lowest hosting cost (2), then on destination list order (3), and finally on location (alphabetical) (4).
          This approach ensures that the queue's top priority is to place game sessions where average player latency is lowest, and--if latency is the same--where the hosting cost is less, etc.
        - If player latency data is not included, destinations and locations are prioritized first on destination list order (1), and then on location (alphabetical) (2).
          This approach ensures that the queue's top priority is to place game sessions on the first destination fleet listed. If that fleet has multiple locations, the game session is placed on the first location (when listed alphabetically).

        Changing the priority order will affect how game sessions are placed.

        :param location_order: (experimental) The prioritization order to use for fleet locations, when the PriorityOrder property includes LOCATION. Locations are identified by AWS Region codes such as `us-west-2. Each location can only be listed once.
        :param priority_order: (experimental) The recommended sequence to use when prioritizing where to place new game sessions. Each type can only be listed once.

        :stability: experimental
        :exampleMetadata: infused

        Example::

            # fleet: gamelift.BuildFleet
            # topic: sns.Topic
            
            
            gamelift.GameSessionQueue(self, "MyGameSessionQueue",
                game_session_queue_name="test-gameSessionQueue",
                custom_event_data="test-event-data",
                allowed_locations=["eu-west-1", "eu-west-2"],
                destinations=[fleet],
                notification_target=topic,
                player_latency_policies=[gamelift.PlayerLatencyPolicy(
                    maximum_individual_player_latency=Duration.millis(100),
                    policy_duration=Duration.seconds(300)
                )],
                priority_configuration=gamelift.PriorityConfiguration(
                    location_order=["eu-west-1", "eu-west-2"
                    ],
                    priority_order=[gamelift.PriorityType.LATENCY, gamelift.PriorityType.COST, gamelift.PriorityType.DESTINATION, gamelift.PriorityType.LOCATION
                    ]
                ),
                timeout=Duration.seconds(300)
            )
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__334f74ab81f780a210829644ea1fd8ba86575c76302264e1616a64a4f588da34)
            check_type(argname="argument location_order", value=location_order, expected_type=type_hints["location_order"])
            check_type(argname="argument priority_order", value=priority_order, expected_type=type_hints["priority_order"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "location_order": location_order,
            "priority_order": priority_order,
        }

    @builtins.property
    def location_order(self) -> typing.List[builtins.str]:
        '''(experimental) The prioritization order to use for fleet locations, when the PriorityOrder property includes LOCATION.

        Locations are identified by AWS Region codes such as `us-west-2.

        Each location can only be listed once.

        :stability: experimental
        '''
        result = self._values.get("location_order")
        assert result is not None, "Required property 'location_order' is missing"
        return typing.cast(typing.List[builtins.str], result)

    @builtins.property
    def priority_order(self) -> typing.List["PriorityType"]:
        '''(experimental) The recommended sequence to use when prioritizing where to place new game sessions.

        Each type can only be listed once.

        :stability: experimental
        '''
        result = self._values.get("priority_order")
        assert result is not None, "Required property 'priority_order' is missing"
        return typing.cast(typing.List["PriorityType"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "PriorityConfiguration(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.enum(jsii_type="@aws-cdk/aws-gamelift-alpha.PriorityType")
class PriorityType(enum.Enum):
    '''(experimental) Priority to condider when placing new game sessions.

    :stability: experimental
    :exampleMetadata: infused

    Example::

        # fleet: gamelift.BuildFleet
        # topic: sns.Topic
        
        
        gamelift.GameSessionQueue(self, "MyGameSessionQueue",
            game_session_queue_name="test-gameSessionQueue",
            custom_event_data="test-event-data",
            allowed_locations=["eu-west-1", "eu-west-2"],
            destinations=[fleet],
            notification_target=topic,
            player_latency_policies=[gamelift.PlayerLatencyPolicy(
                maximum_individual_player_latency=Duration.millis(100),
                policy_duration=Duration.seconds(300)
            )],
            priority_configuration=gamelift.PriorityConfiguration(
                location_order=["eu-west-1", "eu-west-2"
                ],
                priority_order=[gamelift.PriorityType.LATENCY, gamelift.PriorityType.COST, gamelift.PriorityType.DESTINATION, gamelift.PriorityType.LOCATION
                ]
            ),
            timeout=Duration.seconds(300)
        )
    '''

    LATENCY = "LATENCY"
    '''(experimental) FleetIQ prioritizes locations where the average player latency (provided in each game session request) is lowest.

    :stability: experimental
    '''
    COST = "COST"
    '''(experimental) FleetIQ prioritizes destinations with the lowest current hosting costs.

    Cost is evaluated based on the location, instance type, and fleet type (Spot or On-Demand) for each destination in the queue.

    :stability: experimental
    '''
    DESTINATION = "DESTINATION"
    '''(experimental) FleetIQ prioritizes based on the order that destinations are listed in the queue configuration.

    :stability: experimental
    '''
    LOCATION = "LOCATION"
    '''(experimental) FleetIQ prioritizes based on the provided order of locations, as defined in ``LocationOrder``.

    :stability: experimental
    '''


@jsii.enum(jsii_type="@aws-cdk/aws-gamelift-alpha.Protocol")
class Protocol(enum.Enum):
    '''(experimental) Protocol for use in Connection Rules.

    https://www.iana.org/assignments/protocol-numbers/protocol-numbers.xhtml

    :stability: experimental
    '''

    TCP = "TCP"
    '''
    :stability: experimental
    '''
    UDP = "UDP"
    '''
    :stability: experimental
    '''


class QueuedMatchmakingConfiguration(
    MatchmakingConfigurationBase,
    metaclass=jsii.JSIIMeta,
    jsii_type="@aws-cdk/aws-gamelift-alpha.QueuedMatchmakingConfiguration",
):
    '''(experimental) A FlexMatch matchmaker process does the work of building a game match.

    It manages the pool of matchmaking requests received, forms teams for a match, processes and selects players to find the best possible player groups, and initiates the process of placing and starting a game session for the match.
    This topic describes the key aspects of a matchmaker and how to configure one customized for your game.

    :see: https://docs.aws.amazon.com/gamelift/latest/flexmatchguide/match-configuration.html
    :stability: experimental
    :resource: AWS::GameLift::MatchmakingConfiguration
    :exampleMetadata: infused

    Example::

        # queue: gamelift.GameSessionQueue
        # rule_set: gamelift.MatchmakingRuleSet
        
        
        gamelift.QueuedMatchmakingConfiguration(self, "QueuedMatchmakingConfiguration",
            matchmaking_configuration_name="test-queued-config-name",
            game_session_queues=[queue],
            rule_set=rule_set
        )
    '''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        game_session_queues: typing.Sequence[IGameSessionQueue],
        additional_player_count: typing.Optional[jsii.Number] = None,
        game_properties: typing.Optional[typing.Sequence[typing.Union[GameProperty, typing.Dict[builtins.str, typing.Any]]]] = None,
        game_session_data: typing.Optional[builtins.str] = None,
        manual_backfill_mode: typing.Optional[builtins.bool] = None,
        matchmaking_configuration_name: builtins.str,
        rule_set: IMatchmakingRuleSet,
        acceptance_timeout: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        custom_event_data: typing.Optional[builtins.str] = None,
        description: typing.Optional[builtins.str] = None,
        notification_target: typing.Optional[_aws_cdk_aws_sns_ceddda9d.ITopic] = None,
        request_timeout: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        require_acceptance: typing.Optional[builtins.bool] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param game_session_queues: (experimental) Queues are used to start new GameLift-hosted game sessions for matches that are created with this matchmaking configuration. Queues can be located in any Region.
        :param additional_player_count: (experimental) The number of player slots in a match to keep open for future players. For example, if the configuration's rule set specifies a match for a single 12-person team, and the additional player count is set to 2, only 10 players are selected for the match. Default: no additional player slots
        :param game_properties: (experimental) A set of custom properties for a game session, formatted as key-value pairs. These properties are passed to a game server process with a request to start a new game session. Default: no additional game properties
        :param game_session_data: (experimental) A set of custom game session properties, formatted as a single string value. This data is passed to a game server process with a request to start a new game session. Default: no additional game session data
        :param manual_backfill_mode: (experimental) The method used to backfill game sessions that are created with this matchmaking configuration. - Choose manual when your game manages backfill requests manually or does not use the match backfill feature. - Otherwise backfill is settled to automatic to have GameLift create a ``StartMatchBackfill`` request whenever a game session has one or more open slots. Default: automatic backfill mode
        :param matchmaking_configuration_name: (experimental) A unique identifier for the matchmaking configuration. This name is used to identify the configuration associated with a matchmaking request or ticket.
        :param rule_set: (experimental) A matchmaking rule set to use with this configuration. A matchmaking configuration can only use rule sets that are defined in the same Region.
        :param acceptance_timeout: (experimental) The length of time (in seconds) to wait for players to accept a proposed match, if acceptance is required. Default: 300 seconds
        :param custom_event_data: (experimental) Information to add to all events related to the matchmaking configuration. Default: no custom data added to events
        :param description: (experimental) A human-readable description of the matchmaking configuration. Default: no description is provided
        :param notification_target: (experimental) An SNS topic ARN that is set up to receive matchmaking notifications. Default: no notification target
        :param request_timeout: (experimental) The maximum duration, that a matchmaking ticket can remain in process before timing out. Requests that fail due to timing out can be resubmitted as needed. Default: 300 seconds
        :param require_acceptance: (experimental) A flag that determines whether a match that was created with this configuration must be accepted by the matched players. With this option enabled, matchmaking tickets use the status ``REQUIRES_ACCEPTANCE`` to indicate when a completed potential match is waiting for player acceptance. Default: Acceptance is not required

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__be244137222f30ecbe1929614ba472a54f8614aa5e1cb09e77e3df6dbcd4a484)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = QueuedMatchmakingConfigurationProps(
            game_session_queues=game_session_queues,
            additional_player_count=additional_player_count,
            game_properties=game_properties,
            game_session_data=game_session_data,
            manual_backfill_mode=manual_backfill_mode,
            matchmaking_configuration_name=matchmaking_configuration_name,
            rule_set=rule_set,
            acceptance_timeout=acceptance_timeout,
            custom_event_data=custom_event_data,
            description=description,
            notification_target=notification_target,
            request_timeout=request_timeout,
            require_acceptance=require_acceptance,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @jsii.member(jsii_name="fromQueuedMatchmakingConfigurationArn")
    @builtins.classmethod
    def from_queued_matchmaking_configuration_arn(
        cls,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        matchmaking_configuration_arn: builtins.str,
    ) -> IMatchmakingConfiguration:
        '''(experimental) Import an existing matchmaking configuration from its ARN.

        :param scope: -
        :param id: -
        :param matchmaking_configuration_arn: -

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__781c8df696d40f03602d3bdb2a5baff0078e995e886b25c6bafc5ccc580d95a3)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument matchmaking_configuration_arn", value=matchmaking_configuration_arn, expected_type=type_hints["matchmaking_configuration_arn"])
        return typing.cast(IMatchmakingConfiguration, jsii.sinvoke(cls, "fromQueuedMatchmakingConfigurationArn", [scope, id, matchmaking_configuration_arn]))

    @jsii.member(jsii_name="fromQueuedMatchmakingConfigurationName")
    @builtins.classmethod
    def from_queued_matchmaking_configuration_name(
        cls,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        matchmaking_configuration_name: builtins.str,
    ) -> IMatchmakingConfiguration:
        '''(experimental) Import an existing matchmaking configuration from its name.

        :param scope: -
        :param id: -
        :param matchmaking_configuration_name: -

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7fbf1f3b09528f7cb315af51a7f12641235099066dd8d797ce40c9482c7a5395)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument matchmaking_configuration_name", value=matchmaking_configuration_name, expected_type=type_hints["matchmaking_configuration_name"])
        return typing.cast(IMatchmakingConfiguration, jsii.sinvoke(cls, "fromQueuedMatchmakingConfigurationName", [scope, id, matchmaking_configuration_name]))

    @jsii.member(jsii_name="addGameSessionQueue")
    def add_game_session_queue(self, game_session_queue: IGameSessionQueue) -> None:
        '''(experimental) Adds a game session queue destination to the matchmaking configuration.

        :param game_session_queue: A game session queue.

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4d5a3bfbfee3f6e91502b8aa315b930ba4cac1663f67c677da613d5e4356dae3)
            check_type(argname="argument game_session_queue", value=game_session_queue, expected_type=type_hints["game_session_queue"])
        return typing.cast(None, jsii.invoke(self, "addGameSessionQueue", [game_session_queue]))

    @jsii.python.classproperty
    @jsii.member(jsii_name="PROPERTY_INJECTION_ID")
    def PROPERTY_INJECTION_ID(cls) -> builtins.str:
        '''(experimental) Uniquely identifies this class.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "PROPERTY_INJECTION_ID"))

    @builtins.property
    @jsii.member(jsii_name="matchmakingConfigurationArn")
    def matchmaking_configuration_arn(self) -> builtins.str:
        '''(experimental) The ARN of the matchmaking configuration.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "matchmakingConfigurationArn"))

    @builtins.property
    @jsii.member(jsii_name="matchmakingConfigurationName")
    def matchmaking_configuration_name(self) -> builtins.str:
        '''(experimental) The name of the matchmaking configuration.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "matchmakingConfigurationName"))

    @builtins.property
    @jsii.member(jsii_name="notificationTarget")
    def notification_target(self) -> typing.Optional[_aws_cdk_aws_sns_ceddda9d.ITopic]:
        '''(experimental) The notification target for matchmaking events.

        :stability: experimental
        '''
        return typing.cast(typing.Optional[_aws_cdk_aws_sns_ceddda9d.ITopic], jsii.get(self, "notificationTarget"))


@jsii.data_type(
    jsii_type="@aws-cdk/aws-gamelift-alpha.QueuedMatchmakingConfigurationProps",
    jsii_struct_bases=[MatchmakingConfigurationProps],
    name_mapping={
        "matchmaking_configuration_name": "matchmakingConfigurationName",
        "rule_set": "ruleSet",
        "acceptance_timeout": "acceptanceTimeout",
        "custom_event_data": "customEventData",
        "description": "description",
        "notification_target": "notificationTarget",
        "request_timeout": "requestTimeout",
        "require_acceptance": "requireAcceptance",
        "game_session_queues": "gameSessionQueues",
        "additional_player_count": "additionalPlayerCount",
        "game_properties": "gameProperties",
        "game_session_data": "gameSessionData",
        "manual_backfill_mode": "manualBackfillMode",
    },
)
class QueuedMatchmakingConfigurationProps(MatchmakingConfigurationProps):
    def __init__(
        self,
        *,
        matchmaking_configuration_name: builtins.str,
        rule_set: IMatchmakingRuleSet,
        acceptance_timeout: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        custom_event_data: typing.Optional[builtins.str] = None,
        description: typing.Optional[builtins.str] = None,
        notification_target: typing.Optional[_aws_cdk_aws_sns_ceddda9d.ITopic] = None,
        request_timeout: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        require_acceptance: typing.Optional[builtins.bool] = None,
        game_session_queues: typing.Sequence[IGameSessionQueue],
        additional_player_count: typing.Optional[jsii.Number] = None,
        game_properties: typing.Optional[typing.Sequence[typing.Union[GameProperty, typing.Dict[builtins.str, typing.Any]]]] = None,
        game_session_data: typing.Optional[builtins.str] = None,
        manual_backfill_mode: typing.Optional[builtins.bool] = None,
    ) -> None:
        '''(experimental) Properties for a new queued matchmaking configuration.

        :param matchmaking_configuration_name: (experimental) A unique identifier for the matchmaking configuration. This name is used to identify the configuration associated with a matchmaking request or ticket.
        :param rule_set: (experimental) A matchmaking rule set to use with this configuration. A matchmaking configuration can only use rule sets that are defined in the same Region.
        :param acceptance_timeout: (experimental) The length of time (in seconds) to wait for players to accept a proposed match, if acceptance is required. Default: 300 seconds
        :param custom_event_data: (experimental) Information to add to all events related to the matchmaking configuration. Default: no custom data added to events
        :param description: (experimental) A human-readable description of the matchmaking configuration. Default: no description is provided
        :param notification_target: (experimental) An SNS topic ARN that is set up to receive matchmaking notifications. Default: no notification target
        :param request_timeout: (experimental) The maximum duration, that a matchmaking ticket can remain in process before timing out. Requests that fail due to timing out can be resubmitted as needed. Default: 300 seconds
        :param require_acceptance: (experimental) A flag that determines whether a match that was created with this configuration must be accepted by the matched players. With this option enabled, matchmaking tickets use the status ``REQUIRES_ACCEPTANCE`` to indicate when a completed potential match is waiting for player acceptance. Default: Acceptance is not required
        :param game_session_queues: (experimental) Queues are used to start new GameLift-hosted game sessions for matches that are created with this matchmaking configuration. Queues can be located in any Region.
        :param additional_player_count: (experimental) The number of player slots in a match to keep open for future players. For example, if the configuration's rule set specifies a match for a single 12-person team, and the additional player count is set to 2, only 10 players are selected for the match. Default: no additional player slots
        :param game_properties: (experimental) A set of custom properties for a game session, formatted as key-value pairs. These properties are passed to a game server process with a request to start a new game session. Default: no additional game properties
        :param game_session_data: (experimental) A set of custom game session properties, formatted as a single string value. This data is passed to a game server process with a request to start a new game session. Default: no additional game session data
        :param manual_backfill_mode: (experimental) The method used to backfill game sessions that are created with this matchmaking configuration. - Choose manual when your game manages backfill requests manually or does not use the match backfill feature. - Otherwise backfill is settled to automatic to have GameLift create a ``StartMatchBackfill`` request whenever a game session has one or more open slots. Default: automatic backfill mode

        :stability: experimental
        :exampleMetadata: infused

        Example::

            # queue: gamelift.GameSessionQueue
            # rule_set: gamelift.MatchmakingRuleSet
            
            
            gamelift.QueuedMatchmakingConfiguration(self, "QueuedMatchmakingConfiguration",
                matchmaking_configuration_name="test-queued-config-name",
                game_session_queues=[queue],
                rule_set=rule_set
            )
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__964b4cd698f029625433fe3a9d1ed9d87b9ad33c86cbca699f3e04a5750fb44f)
            check_type(argname="argument matchmaking_configuration_name", value=matchmaking_configuration_name, expected_type=type_hints["matchmaking_configuration_name"])
            check_type(argname="argument rule_set", value=rule_set, expected_type=type_hints["rule_set"])
            check_type(argname="argument acceptance_timeout", value=acceptance_timeout, expected_type=type_hints["acceptance_timeout"])
            check_type(argname="argument custom_event_data", value=custom_event_data, expected_type=type_hints["custom_event_data"])
            check_type(argname="argument description", value=description, expected_type=type_hints["description"])
            check_type(argname="argument notification_target", value=notification_target, expected_type=type_hints["notification_target"])
            check_type(argname="argument request_timeout", value=request_timeout, expected_type=type_hints["request_timeout"])
            check_type(argname="argument require_acceptance", value=require_acceptance, expected_type=type_hints["require_acceptance"])
            check_type(argname="argument game_session_queues", value=game_session_queues, expected_type=type_hints["game_session_queues"])
            check_type(argname="argument additional_player_count", value=additional_player_count, expected_type=type_hints["additional_player_count"])
            check_type(argname="argument game_properties", value=game_properties, expected_type=type_hints["game_properties"])
            check_type(argname="argument game_session_data", value=game_session_data, expected_type=type_hints["game_session_data"])
            check_type(argname="argument manual_backfill_mode", value=manual_backfill_mode, expected_type=type_hints["manual_backfill_mode"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "matchmaking_configuration_name": matchmaking_configuration_name,
            "rule_set": rule_set,
            "game_session_queues": game_session_queues,
        }
        if acceptance_timeout is not None:
            self._values["acceptance_timeout"] = acceptance_timeout
        if custom_event_data is not None:
            self._values["custom_event_data"] = custom_event_data
        if description is not None:
            self._values["description"] = description
        if notification_target is not None:
            self._values["notification_target"] = notification_target
        if request_timeout is not None:
            self._values["request_timeout"] = request_timeout
        if require_acceptance is not None:
            self._values["require_acceptance"] = require_acceptance
        if additional_player_count is not None:
            self._values["additional_player_count"] = additional_player_count
        if game_properties is not None:
            self._values["game_properties"] = game_properties
        if game_session_data is not None:
            self._values["game_session_data"] = game_session_data
        if manual_backfill_mode is not None:
            self._values["manual_backfill_mode"] = manual_backfill_mode

    @builtins.property
    def matchmaking_configuration_name(self) -> builtins.str:
        '''(experimental) A unique identifier for the matchmaking configuration.

        This name is used to identify the configuration associated with a matchmaking request or ticket.

        :stability: experimental
        '''
        result = self._values.get("matchmaking_configuration_name")
        assert result is not None, "Required property 'matchmaking_configuration_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def rule_set(self) -> IMatchmakingRuleSet:
        '''(experimental) A matchmaking rule set to use with this configuration.

        A matchmaking configuration can only use rule sets that are defined in the same Region.

        :stability: experimental
        '''
        result = self._values.get("rule_set")
        assert result is not None, "Required property 'rule_set' is missing"
        return typing.cast(IMatchmakingRuleSet, result)

    @builtins.property
    def acceptance_timeout(self) -> typing.Optional[_aws_cdk_ceddda9d.Duration]:
        '''(experimental) The length of time (in seconds) to wait for players to accept a proposed match, if acceptance is required.

        :default: 300 seconds

        :stability: experimental
        '''
        result = self._values.get("acceptance_timeout")
        return typing.cast(typing.Optional[_aws_cdk_ceddda9d.Duration], result)

    @builtins.property
    def custom_event_data(self) -> typing.Optional[builtins.str]:
        '''(experimental) Information to add to all events related to the matchmaking configuration.

        :default: no custom data added to events

        :stability: experimental
        '''
        result = self._values.get("custom_event_data")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        '''(experimental) A human-readable description of the matchmaking configuration.

        :default: no description is provided

        :stability: experimental
        '''
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def notification_target(self) -> typing.Optional[_aws_cdk_aws_sns_ceddda9d.ITopic]:
        '''(experimental) An SNS topic ARN that is set up to receive matchmaking notifications.

        :default: no notification target

        :see: https://docs.aws.amazon.com/gamelift/latest/flexmatchguide/match-notification.html
        :stability: experimental
        '''
        result = self._values.get("notification_target")
        return typing.cast(typing.Optional[_aws_cdk_aws_sns_ceddda9d.ITopic], result)

    @builtins.property
    def request_timeout(self) -> typing.Optional[_aws_cdk_ceddda9d.Duration]:
        '''(experimental) The maximum duration, that a matchmaking ticket can remain in process before timing out.

        Requests that fail due to timing out can be resubmitted as needed.

        :default: 300 seconds

        :stability: experimental
        '''
        result = self._values.get("request_timeout")
        return typing.cast(typing.Optional[_aws_cdk_ceddda9d.Duration], result)

    @builtins.property
    def require_acceptance(self) -> typing.Optional[builtins.bool]:
        '''(experimental) A flag that determines whether a match that was created with this configuration must be accepted by the matched players.

        With this option enabled, matchmaking tickets use the status ``REQUIRES_ACCEPTANCE`` to indicate when a completed potential match is waiting for player acceptance.

        :default: Acceptance is not required

        :stability: experimental
        '''
        result = self._values.get("require_acceptance")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def game_session_queues(self) -> typing.List[IGameSessionQueue]:
        '''(experimental) Queues are used to start new GameLift-hosted game sessions for matches that are created with this matchmaking configuration.

        Queues can be located in any Region.

        :stability: experimental
        '''
        result = self._values.get("game_session_queues")
        assert result is not None, "Required property 'game_session_queues' is missing"
        return typing.cast(typing.List[IGameSessionQueue], result)

    @builtins.property
    def additional_player_count(self) -> typing.Optional[jsii.Number]:
        '''(experimental) The number of player slots in a match to keep open for future players.

        For example, if the configuration's rule set specifies a match for a single 12-person team, and the additional player count is set to 2, only 10 players are selected for the match.

        :default: no additional player slots

        :stability: experimental
        '''
        result = self._values.get("additional_player_count")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def game_properties(self) -> typing.Optional[typing.List[GameProperty]]:
        '''(experimental) A set of custom properties for a game session, formatted as key-value pairs.

        These properties are passed to a game server process with a request to start a new game session.

        :default: no additional game properties

        :see: https://docs.aws.amazon.com/gamelift/latest/developerguide/gamelift-sdk-server-api.html#gamelift-sdk-server-startsession
        :stability: experimental
        '''
        result = self._values.get("game_properties")
        return typing.cast(typing.Optional[typing.List[GameProperty]], result)

    @builtins.property
    def game_session_data(self) -> typing.Optional[builtins.str]:
        '''(experimental) A set of custom game session properties, formatted as a single string value.

        This data is passed to a game server process with a request to start a new game session.

        :default: no additional game session data

        :see: https://docs.aws.amazon.com/gamelift/latest/developerguide/gamelift-sdk-server-api.html#gamelift-sdk-server-startsession
        :stability: experimental
        '''
        result = self._values.get("game_session_data")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def manual_backfill_mode(self) -> typing.Optional[builtins.bool]:
        '''(experimental) The method used to backfill game sessions that are created with this matchmaking configuration.

        - Choose manual when your game manages backfill requests manually or does not use the match backfill feature.
        - Otherwise backfill is settled to automatic to have GameLift create a ``StartMatchBackfill`` request whenever a game session has one or more open slots.

        :default: automatic backfill mode

        :see: https://docs.aws.amazon.com/gamelift/latest/flexmatchguide/match-backfill.html
        :stability: experimental
        '''
        result = self._values.get("manual_backfill_mode")
        return typing.cast(typing.Optional[builtins.bool], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "QueuedMatchmakingConfigurationProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@aws-cdk/aws-gamelift-alpha.ResourceCreationLimitPolicy",
    jsii_struct_bases=[],
    name_mapping={
        "new_game_sessions_per_creator": "newGameSessionsPerCreator",
        "policy_period": "policyPeriod",
    },
)
class ResourceCreationLimitPolicy:
    def __init__(
        self,
        *,
        new_game_sessions_per_creator: typing.Optional[jsii.Number] = None,
        policy_period: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
    ) -> None:
        '''(experimental) A policy that limits the number of game sessions a player can create on the same fleet.

        This optional policy gives game owners control over how players can consume available game server resources.
        A resource creation policy makes the following statement: "An individual player can create a maximum number of new game sessions within a specified time period".

        The policy is evaluated when a player tries to create a new game session.
        For example, assume you have a policy of 10 new game sessions and a time period of 60 minutes.
        On receiving a ``CreateGameSession`` request, Amazon GameLift checks that the player (identified by CreatorId) has created fewer than 10 game sessions in the past 60 minutes.

        :param new_game_sessions_per_creator: (experimental) The maximum number of game sessions that an individual can create during the policy period. Default: no limit on the number of game sessions that an individual can create during the policy period
        :param policy_period: (experimental) The time span used in evaluating the resource creation limit policy. Default: no policy period

        :stability: experimental
        :exampleMetadata: fixture=_generated

        Example::

            # The code below shows an example of how to instantiate this type.
            # The values are placeholders you should change.
            import aws_cdk.aws_gamelift_alpha as gamelift_alpha
            import aws_cdk as cdk
            
            resource_creation_limit_policy = gamelift_alpha.ResourceCreationLimitPolicy(
                new_game_sessions_per_creator=123,
                policy_period=cdk.Duration.minutes(30)
            )
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__510e179942276e17b717c9dac3c9c38778402766783bd9ee763473b55a6bb0b5)
            check_type(argname="argument new_game_sessions_per_creator", value=new_game_sessions_per_creator, expected_type=type_hints["new_game_sessions_per_creator"])
            check_type(argname="argument policy_period", value=policy_period, expected_type=type_hints["policy_period"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if new_game_sessions_per_creator is not None:
            self._values["new_game_sessions_per_creator"] = new_game_sessions_per_creator
        if policy_period is not None:
            self._values["policy_period"] = policy_period

    @builtins.property
    def new_game_sessions_per_creator(self) -> typing.Optional[jsii.Number]:
        '''(experimental) The maximum number of game sessions that an individual can create during the policy period.

        :default: no limit on the number of game sessions that an individual can create during the policy period

        :stability: experimental
        '''
        result = self._values.get("new_game_sessions_per_creator")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def policy_period(self) -> typing.Optional[_aws_cdk_ceddda9d.Duration]:
        '''(experimental) The time span used in evaluating the resource creation limit policy.

        :default: no policy period

        :stability: experimental
        '''
        result = self._values.get("policy_period")
        return typing.cast(typing.Optional[_aws_cdk_ceddda9d.Duration], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ResourceCreationLimitPolicy(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@aws-cdk/aws-gamelift-alpha.RuleSetBodyConfig",
    jsii_struct_bases=[],
    name_mapping={"rule_set_body": "ruleSetBody"},
)
class RuleSetBodyConfig:
    def __init__(self, *, rule_set_body: builtins.str) -> None:
        '''(experimental) Interface to represent output result of a RuleSetContent binding.

        :param rule_set_body: (experimental) Inline ruleSet body.

        :stability: experimental
        :exampleMetadata: fixture=_generated

        Example::

            # The code below shows an example of how to instantiate this type.
            # The values are placeholders you should change.
            import aws_cdk.aws_gamelift_alpha as gamelift_alpha
            
            rule_set_body_config = gamelift_alpha.RuleSetBodyConfig(
                rule_set_body="ruleSetBody"
            )
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5354ccd65eb1ccbc5870ac6dd16b6dd23cddb1833f4df0ebbf12c363778f54bf)
            check_type(argname="argument rule_set_body", value=rule_set_body, expected_type=type_hints["rule_set_body"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "rule_set_body": rule_set_body,
        }

    @builtins.property
    def rule_set_body(self) -> builtins.str:
        '''(experimental) Inline ruleSet body.

        :stability: experimental
        '''
        result = self._values.get("rule_set_body")
        assert result is not None, "Required property 'rule_set_body' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "RuleSetBodyConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.implements(IRuleSetContent)
class RuleSetContent(
    metaclass=jsii.JSIIMeta,
    jsii_type="@aws-cdk/aws-gamelift-alpha.RuleSetContent",
):
    '''(experimental) The rule set determines the two key elements of a match: your game's team structure and size, and how to group players together for the best possible match.

    For example, a rule set might describe a match like this:

    - Create a match with two teams of five players each, one team is the defenders and the other team the invaders.
    - A team can have novice and experienced players, but the average skill of the two teams must be within 10 points of each other.
    - If no match is made after 30 seconds, gradually relax the skill requirements.

    :stability: experimental
    :exampleMetadata: infused

    Example::

        gamelift.MatchmakingRuleSet(self, "RuleSet",
            matchmaking_rule_set_name="my-test-ruleset",
            content=gamelift.RuleSetContent.from_json_file(path.join(__dirname, "my-ruleset", "ruleset.json"))
        )
    '''

    def __init__(self, *, content: typing.Optional[IRuleSetBody] = None) -> None:
        '''
        :param content: (experimental) RuleSet body content. Default: use a default empty RuleSet body

        :stability: experimental
        '''
        props = RuleSetContentProps(content=content)

        jsii.create(self.__class__, self, [props])

    @jsii.member(jsii_name="fromInline")
    @builtins.classmethod
    def from_inline(cls, body: builtins.str) -> IRuleSetContent:
        '''(experimental) Inline body for Matchmaking ruleSet.

        :param body: The actual ruleSet body (maximum 65535 characters).

        :return: ``RuleSetContent`` with inline code.

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a0a5602cdb30daf4f053362ebca7fcb5ca050681e1317b1e7448969763688001)
            check_type(argname="argument body", value=body, expected_type=type_hints["body"])
        return typing.cast(IRuleSetContent, jsii.sinvoke(cls, "fromInline", [body]))

    @jsii.member(jsii_name="fromJsonFile")
    @builtins.classmethod
    def from_json_file(cls, path: builtins.str) -> IRuleSetContent:
        '''(experimental) Matchmaking ruleSet body from a file.

        :param path: The path to the ruleSet body file.

        :return: ``RuleSetContentBase`` based on JSON file content.

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1f3e0bae77877836e083593e18191cdb0489f082859455692e225eaa93c232cb)
            check_type(argname="argument path", value=path, expected_type=type_hints["path"])
        return typing.cast(IRuleSetContent, jsii.sinvoke(cls, "fromJsonFile", [path]))

    @jsii.member(jsii_name="bind")
    def bind(self, _scope: _constructs_77d1e7e8.Construct) -> RuleSetBodyConfig:
        '''(experimental) Called when the matchmaking ruleSet is initialized to allow this object to bind to the stack and add resources.

        :param _scope: The binding scope.

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9e4177f5a9a4221d007c0afaa057c80e113c2851b420d8475561ee3fdcd7f0b6)
            check_type(argname="argument _scope", value=_scope, expected_type=type_hints["_scope"])
        return typing.cast(RuleSetBodyConfig, jsii.invoke(self, "bind", [_scope]))

    @builtins.property
    @jsii.member(jsii_name="content")
    def content(self) -> IRuleSetBody:
        '''(experimental) RuleSet body content.

        :stability: experimental
        '''
        return typing.cast(IRuleSetBody, jsii.get(self, "content"))


@jsii.data_type(
    jsii_type="@aws-cdk/aws-gamelift-alpha.RuleSetContentProps",
    jsii_struct_bases=[],
    name_mapping={"content": "content"},
)
class RuleSetContentProps:
    def __init__(self, *, content: typing.Optional[IRuleSetBody] = None) -> None:
        '''(experimental) Properties for a new matchmaking ruleSet content.

        :param content: (experimental) RuleSet body content. Default: use a default empty RuleSet body

        :stability: experimental
        :exampleMetadata: fixture=_generated

        Example::

            # The code below shows an example of how to instantiate this type.
            # The values are placeholders you should change.
            import aws_cdk.aws_gamelift_alpha as gamelift_alpha
            
            # rule_set_body: gamelift_alpha.IRuleSetBody
            
            rule_set_content_props = gamelift_alpha.RuleSetContentProps(
                content=rule_set_body
            )
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3695b67c606f06a3aa5add6f464b5609bc21f42521bc364955f801406602e58c)
            check_type(argname="argument content", value=content, expected_type=type_hints["content"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if content is not None:
            self._values["content"] = content

    @builtins.property
    def content(self) -> typing.Optional[IRuleSetBody]:
        '''(experimental) RuleSet body content.

        :default: use a default empty RuleSet body

        :stability: experimental
        '''
        result = self._values.get("content")
        return typing.cast(typing.Optional[IRuleSetBody], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "RuleSetContentProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@aws-cdk/aws-gamelift-alpha.RuntimeConfiguration",
    jsii_struct_bases=[],
    name_mapping={
        "server_processes": "serverProcesses",
        "game_session_activation_timeout": "gameSessionActivationTimeout",
        "max_concurrent_game_session_activations": "maxConcurrentGameSessionActivations",
    },
)
class RuntimeConfiguration:
    def __init__(
        self,
        *,
        server_processes: typing.Sequence[typing.Union["ServerProcess", typing.Dict[builtins.str, typing.Any]]],
        game_session_activation_timeout: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        max_concurrent_game_session_activations: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''(experimental) A collection of server process configurations that describe the set of processes to run on each instance in a fleet.

        Server processes run either an executable in a custom game build or a Realtime Servers script.
        GameLift launches the configured processes, manages their life cycle, and replaces them as needed.
        Each instance checks regularly for an updated runtime configuration.

        A GameLift instance is limited to 50 processes running concurrently.
        To calculate the total number of processes in a runtime configuration, add the values of the ``ConcurrentExecutions`` parameter for each ``ServerProcess``.

        :param server_processes: (experimental) A collection of server process configurations that identify what server processes to run on each instance in a fleet.
        :param game_session_activation_timeout: (experimental) The maximum amount of time allowed to launch a new game session and have it report ready to host players. During this time, the game session is in status ``ACTIVATING``. If the game session does not become active before the timeout, it is ended and the game session status is changed to ``TERMINATED``. Default: by default game session activation timeout is 300 seconds
        :param max_concurrent_game_session_activations: (experimental) The number of game sessions in status ``ACTIVATING`` to allow on an instance. This setting limits the instance resources that can be used for new game activations at any one time. Default: no limit

        :see: https://docs.aws.amazon.com/gamelift/latest/developerguide/fleets-multiprocess.html
        :stability: experimental
        :exampleMetadata: infused

        Example::

            # build: gamelift.Build
            
            # Server processes can be delcared in a declarative way through the constructor
            fleet = gamelift.BuildFleet(self, "Game server fleet",
                fleet_name="test-fleet",
                content=build,
                instance_type=ec2.InstanceType.of(ec2.InstanceClass.C4, ec2.InstanceSize.LARGE),
                runtime_configuration=gamelift.RuntimeConfiguration(
                    server_processes=[gamelift.ServerProcess(
                        launch_path="/local/game/GameLiftExampleServer.x86_64",
                        parameters="-logFile /local/game/logs/myserver1935.log -port 1935",
                        concurrent_executions=100
                    )]
                )
            )
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__cf5e16edd407d4296fc803b4b9c4ae54a060599679202852ed91ce001469c0a3)
            check_type(argname="argument server_processes", value=server_processes, expected_type=type_hints["server_processes"])
            check_type(argname="argument game_session_activation_timeout", value=game_session_activation_timeout, expected_type=type_hints["game_session_activation_timeout"])
            check_type(argname="argument max_concurrent_game_session_activations", value=max_concurrent_game_session_activations, expected_type=type_hints["max_concurrent_game_session_activations"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "server_processes": server_processes,
        }
        if game_session_activation_timeout is not None:
            self._values["game_session_activation_timeout"] = game_session_activation_timeout
        if max_concurrent_game_session_activations is not None:
            self._values["max_concurrent_game_session_activations"] = max_concurrent_game_session_activations

    @builtins.property
    def server_processes(self) -> typing.List["ServerProcess"]:
        '''(experimental) A collection of server process configurations that identify what server processes to run on each instance in a fleet.

        :stability: experimental
        '''
        result = self._values.get("server_processes")
        assert result is not None, "Required property 'server_processes' is missing"
        return typing.cast(typing.List["ServerProcess"], result)

    @builtins.property
    def game_session_activation_timeout(
        self,
    ) -> typing.Optional[_aws_cdk_ceddda9d.Duration]:
        '''(experimental) The maximum amount of time allowed to launch a new game session and have it report ready to host players.

        During this time, the game session is in status ``ACTIVATING``.

        If the game session does not become active before the timeout, it is ended and the game session status is changed to ``TERMINATED``.

        :default: by default game session activation timeout is 300 seconds

        :stability: experimental
        '''
        result = self._values.get("game_session_activation_timeout")
        return typing.cast(typing.Optional[_aws_cdk_ceddda9d.Duration], result)

    @builtins.property
    def max_concurrent_game_session_activations(self) -> typing.Optional[jsii.Number]:
        '''(experimental) The number of game sessions in status ``ACTIVATING`` to allow on an instance.

        This setting limits the instance resources that can be used for new game activations at any one time.

        :default: no limit

        :stability: experimental
        '''
        result = self._values.get("max_concurrent_game_session_activations")
        return typing.cast(typing.Optional[jsii.Number], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "RuntimeConfiguration(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class S3Content(
    Content,
    metaclass=jsii.JSIIMeta,
    jsii_type="@aws-cdk/aws-gamelift-alpha.S3Content",
):
    '''(experimental) Game content from an S3 archive.

    :stability: experimental
    :exampleMetadata: fixture=_generated

    Example::

        # The code below shows an example of how to instantiate this type.
        # The values are placeholders you should change.
        import aws_cdk.aws_gamelift_alpha as gamelift_alpha
        from aws_cdk import aws_s3 as s3
        
        # bucket: s3.Bucket
        
        s3_content = gamelift_alpha.S3Content(bucket, "key", "objectVersion")
    '''

    def __init__(
        self,
        bucket: _aws_cdk_aws_s3_ceddda9d.IBucket,
        key: builtins.str,
        object_version: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param bucket: -
        :param key: -
        :param object_version: -

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e0b27857db7f0cfd9fbf597ef20acdd7208fe5d681f1d1413d36c0e67ba69702)
            check_type(argname="argument bucket", value=bucket, expected_type=type_hints["bucket"])
            check_type(argname="argument key", value=key, expected_type=type_hints["key"])
            check_type(argname="argument object_version", value=object_version, expected_type=type_hints["object_version"])
        jsii.create(self.__class__, self, [bucket, key, object_version])

    @jsii.member(jsii_name="bind")
    def bind(
        self,
        _scope: _constructs_77d1e7e8.Construct,
        role: _aws_cdk_aws_iam_ceddda9d.IRole,
    ) -> ContentConfig:
        '''(experimental) Called when the Build is initialized to allow this object to bind.

        :param _scope: -
        :param role: -

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a354a9ae95aa20c9c3ef605ca509f8d7ba3526192b9739e0c98ec864492580f8)
            check_type(argname="argument _scope", value=_scope, expected_type=type_hints["_scope"])
            check_type(argname="argument role", value=role, expected_type=type_hints["role"])
        return typing.cast(ContentConfig, jsii.invoke(self, "bind", [_scope, role]))


@jsii.data_type(
    jsii_type="@aws-cdk/aws-gamelift-alpha.ScriptAttributes",
    jsii_struct_bases=[],
    name_mapping={"script_arn": "scriptArn", "role": "role"},
)
class ScriptAttributes:
    def __init__(
        self,
        *,
        script_arn: builtins.str,
        role: typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole] = None,
    ) -> None:
        '''(experimental) Represents a Script content defined outside of this stack.

        :param script_arn: (experimental) The ARN of the realtime server script.
        :param role: (experimental) The IAM role assumed by GameLift to access server script in S3. Default: - undefined

        :stability: experimental
        :exampleMetadata: fixture=_generated

        Example::

            # The code below shows an example of how to instantiate this type.
            # The values are placeholders you should change.
            import aws_cdk.aws_gamelift_alpha as gamelift_alpha
            from aws_cdk import aws_iam as iam
            
            # role: iam.Role
            
            script_attributes = gamelift_alpha.ScriptAttributes(
                script_arn="scriptArn",
            
                # the properties below are optional
                role=role
            )
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__96ea2755dd72bb47adfb866f8b6ffd38ebfd4f9a8af11c16bb3e55d9344dce0c)
            check_type(argname="argument script_arn", value=script_arn, expected_type=type_hints["script_arn"])
            check_type(argname="argument role", value=role, expected_type=type_hints["role"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "script_arn": script_arn,
        }
        if role is not None:
            self._values["role"] = role

    @builtins.property
    def script_arn(self) -> builtins.str:
        '''(experimental) The ARN of the realtime server script.

        :stability: experimental
        '''
        result = self._values.get("script_arn")
        assert result is not None, "Required property 'script_arn' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def role(self) -> typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole]:
        '''(experimental) The IAM role assumed by GameLift to access server script in S3.

        :default: - undefined

        :stability: experimental
        '''
        result = self._values.get("role")
        return typing.cast(typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ScriptAttributes(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.implements(IScript)
class ScriptBase(
    _aws_cdk_ceddda9d.Resource,
    metaclass=jsii.JSIIAbstractClass,
    jsii_type="@aws-cdk/aws-gamelift-alpha.ScriptBase",
):
    '''(experimental) Base class for new and imported GameLift realtime server script.

    :stability: experimental
    '''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        account: typing.Optional[builtins.str] = None,
        environment_from_arn: typing.Optional[builtins.str] = None,
        physical_name: typing.Optional[builtins.str] = None,
        region: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param account: The AWS account ID this resource belongs to. Default: - the resource is in the same account as the stack it belongs to
        :param environment_from_arn: ARN to deduce region and account from. The ARN is parsed and the account and region are taken from the ARN. This should be used for imported resources. Cannot be supplied together with either ``account`` or ``region``. Default: - take environment from ``account``, ``region`` parameters, or use Stack environment.
        :param physical_name: The value passed in by users to the physical name prop of the resource. - ``undefined`` implies that a physical name will be allocated by CloudFormation during deployment. - a concrete value implies a specific physical name - ``PhysicalName.GENERATE_IF_NEEDED`` is a marker that indicates that a physical will only be generated by the CDK if it is needed for cross-environment references. Otherwise, it will be allocated by CloudFormation. Default: - The physical name will be allocated by CloudFormation at deployment time
        :param region: The AWS region this resource belongs to. Default: - the resource is in the same region as the stack it belongs to
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__166d20549f18e89ce130b2747aaffda5a11eef3e94e661bad723cb2553d3d32f)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = _aws_cdk_ceddda9d.ResourceProps(
            account=account,
            environment_from_arn=environment_from_arn,
            physical_name=physical_name,
            region=region,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @builtins.property
    @jsii.member(jsii_name="grantPrincipal")
    @abc.abstractmethod
    def grant_principal(self) -> _aws_cdk_aws_iam_ceddda9d.IPrincipal:
        '''(experimental) The principal to grant permissions to.

        :stability: experimental
        '''
        ...

    @builtins.property
    @jsii.member(jsii_name="scriptArn")
    @abc.abstractmethod
    def script_arn(self) -> builtins.str:
        '''(experimental) The ARN of the realtime server script.

        :stability: experimental
        '''
        ...

    @builtins.property
    @jsii.member(jsii_name="scriptId")
    @abc.abstractmethod
    def script_id(self) -> builtins.str:
        '''(experimental) The Identifier of the realtime server script.

        :stability: experimental
        '''
        ...


class _ScriptBaseProxy(
    ScriptBase,
    jsii.proxy_for(_aws_cdk_ceddda9d.Resource), # type: ignore[misc]
):
    @builtins.property
    @jsii.member(jsii_name="grantPrincipal")
    def grant_principal(self) -> _aws_cdk_aws_iam_ceddda9d.IPrincipal:
        '''(experimental) The principal to grant permissions to.

        :stability: experimental
        '''
        return typing.cast(_aws_cdk_aws_iam_ceddda9d.IPrincipal, jsii.get(self, "grantPrincipal"))

    @builtins.property
    @jsii.member(jsii_name="scriptArn")
    def script_arn(self) -> builtins.str:
        '''(experimental) The ARN of the realtime server script.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "scriptArn"))

    @builtins.property
    @jsii.member(jsii_name="scriptId")
    def script_id(self) -> builtins.str:
        '''(experimental) The Identifier of the realtime server script.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "scriptId"))

# Adding a "__jsii_proxy_class__(): typing.Type" function to the abstract class
typing.cast(typing.Any, ScriptBase).__jsii_proxy_class__ = lambda : _ScriptBaseProxy


@jsii.data_type(
    jsii_type="@aws-cdk/aws-gamelift-alpha.ScriptProps",
    jsii_struct_bases=[],
    name_mapping={
        "content": "content",
        "role": "role",
        "script_name": "scriptName",
        "script_version": "scriptVersion",
    },
)
class ScriptProps:
    def __init__(
        self,
        *,
        content: Content,
        role: typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole] = None,
        script_name: typing.Optional[builtins.str] = None,
        script_version: typing.Optional[builtins.str] = None,
    ) -> None:
        '''(experimental) Properties for a new realtime server script.

        :param content: (experimental) The game content.
        :param role: (experimental) The IAM role assumed by GameLift to access server script in S3. If providing a custom role, it needs to trust the GameLift service principal (gamelift.amazonaws.com) and be granted sufficient permissions to have Read access to a specific key content into a specific S3 bucket. Below an example of required permission: { "Version": "2012-10-17", "Statement": [{ "Effect": "Allow", "Action": [ "s3:GetObject", "s3:GetObjectVersion" ], "Resource": "arn:aws:s3:::bucket-name/object-name" }] } Default: - a role will be created with default permissions.
        :param script_name: (experimental) Name of this realtime server script. Default: No name
        :param script_version: (experimental) Version of this realtime server script. Default: No version

        :stability: experimental
        :exampleMetadata: infused

        Example::

            # bucket: s3.Bucket
            
            gamelift.Script(self, "Script",
                content=gamelift.Content.from_bucket(bucket, "sample-asset-key")
            )
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1f64cc150e31309fdfed340aa86a93c06b20569f4e57ea7bb8029b03454475e5)
            check_type(argname="argument content", value=content, expected_type=type_hints["content"])
            check_type(argname="argument role", value=role, expected_type=type_hints["role"])
            check_type(argname="argument script_name", value=script_name, expected_type=type_hints["script_name"])
            check_type(argname="argument script_version", value=script_version, expected_type=type_hints["script_version"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "content": content,
        }
        if role is not None:
            self._values["role"] = role
        if script_name is not None:
            self._values["script_name"] = script_name
        if script_version is not None:
            self._values["script_version"] = script_version

    @builtins.property
    def content(self) -> Content:
        '''(experimental) The game content.

        :stability: experimental
        '''
        result = self._values.get("content")
        assert result is not None, "Required property 'content' is missing"
        return typing.cast(Content, result)

    @builtins.property
    def role(self) -> typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole]:
        '''(experimental) The IAM role assumed by GameLift to access server script in S3.

        If providing a custom role, it needs to trust the GameLift service principal (gamelift.amazonaws.com) and be granted sufficient permissions
        to have Read access to a specific key content into a specific S3 bucket.
        Below an example of required permission:
        {
        "Version": "2012-10-17",
        "Statement": [{
        "Effect": "Allow",
        "Action": [
        "s3:GetObject",
        "s3:GetObjectVersion"
        ],
        "Resource": "arn:aws:s3:::bucket-name/object-name"
        }]
        }

        :default: - a role will be created with default permissions.

        :see: https://docs.aws.amazon.com/gamelift/latest/developerguide/security_iam_id-based-policy-examples.html#security_iam_id-based-policy-examples-access-storage-loc
        :stability: experimental
        '''
        result = self._values.get("role")
        return typing.cast(typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole], result)

    @builtins.property
    def script_name(self) -> typing.Optional[builtins.str]:
        '''(experimental) Name of this realtime server script.

        :default: No name

        :stability: experimental
        '''
        result = self._values.get("script_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def script_version(self) -> typing.Optional[builtins.str]:
        '''(experimental) Version of this realtime server script.

        :default: No version

        :stability: experimental
        '''
        result = self._values.get("script_version")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ScriptProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@aws-cdk/aws-gamelift-alpha.ServerProcess",
    jsii_struct_bases=[],
    name_mapping={
        "launch_path": "launchPath",
        "concurrent_executions": "concurrentExecutions",
        "parameters": "parameters",
    },
)
class ServerProcess:
    def __init__(
        self,
        *,
        launch_path: builtins.str,
        concurrent_executions: typing.Optional[jsii.Number] = None,
        parameters: typing.Optional[builtins.str] = None,
    ) -> None:
        '''(experimental) Configuration of a fleet server process.

        :param launch_path: (experimental) The location of a game build executable or the Realtime script file that contains the Init() function. Game builds and Realtime scripts are installed on instances at the root: - Windows (custom game builds only): ``C:\\game``. Example: ``C:\\game\\MyGame\\server.exe`` - Linux: ``/local/game``. Examples: ``/local/game/MyGame/server.exe`` or ``/local/game/MyRealtimeScript.js``
        :param concurrent_executions: (experimental) The number of server processes using this configuration that run concurrently on each instance. Minimum is ``1`` Default: 1
        :param parameters: (experimental) An optional list of parameters to pass to the server executable or Realtime script on launch. Default: no parameters

        :stability: experimental
        :exampleMetadata: fixture=_generated

        Example::

            # The code below shows an example of how to instantiate this type.
            # The values are placeholders you should change.
            import aws_cdk.aws_gamelift_alpha as gamelift_alpha
            
            server_process = gamelift_alpha.ServerProcess(
                launch_path="launchPath",
            
                # the properties below are optional
                concurrent_executions=123,
                parameters="parameters"
            )
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__16b9b91b83546a94dce8dcdbb8cdfceb8efe3a913f6fcbd4e9a67dbf38b78fc6)
            check_type(argname="argument launch_path", value=launch_path, expected_type=type_hints["launch_path"])
            check_type(argname="argument concurrent_executions", value=concurrent_executions, expected_type=type_hints["concurrent_executions"])
            check_type(argname="argument parameters", value=parameters, expected_type=type_hints["parameters"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "launch_path": launch_path,
        }
        if concurrent_executions is not None:
            self._values["concurrent_executions"] = concurrent_executions
        if parameters is not None:
            self._values["parameters"] = parameters

    @builtins.property
    def launch_path(self) -> builtins.str:
        '''(experimental) The location of a game build executable or the Realtime script file that contains the Init() function.

        Game builds and Realtime scripts are installed on instances at the root:

        - Windows (custom game builds only): ``C:\\game``. Example: ``C:\\game\\MyGame\\server.exe``
        - Linux: ``/local/game``. Examples: ``/local/game/MyGame/server.exe`` or ``/local/game/MyRealtimeScript.js``

        :stability: experimental
        '''
        result = self._values.get("launch_path")
        assert result is not None, "Required property 'launch_path' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def concurrent_executions(self) -> typing.Optional[jsii.Number]:
        '''(experimental) The number of server processes using this configuration that run concurrently on each instance.

        Minimum is ``1``

        :default: 1

        :stability: experimental
        '''
        result = self._values.get("concurrent_executions")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def parameters(self) -> typing.Optional[builtins.str]:
        '''(experimental) An optional list of parameters to pass to the server executable or Realtime script on launch.

        :default: no parameters

        :stability: experimental
        '''
        result = self._values.get("parameters")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ServerProcess(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class StandaloneMatchmakingConfiguration(
    MatchmakingConfigurationBase,
    metaclass=jsii.JSIIMeta,
    jsii_type="@aws-cdk/aws-gamelift-alpha.StandaloneMatchmakingConfiguration",
):
    '''(experimental) A FlexMatch matchmaker process does the work of building a game match.

    It manages the pool of matchmaking requests received, forms teams for a match, processes and selects players to find the best possible player groups, and initiates the process of placing and starting a game session for the match.
    This topic describes the key aspects of a matchmaker and how to configure one customized for your game.

    :see: https://docs.aws.amazon.com/gamelift/latest/flexmatchguide/match-configuration.html
    :stability: experimental
    :resource: AWS::GameLift::MatchmakingConfiguration
    :exampleMetadata: infused

    Example::

        # rule_set: gamelift.MatchmakingRuleSet
        
        
        gamelift.StandaloneMatchmakingConfiguration(self, "StandaloneMatchmaking",
            matchmaking_configuration_name="test-standalone-config-name",
            rule_set=rule_set
        )
    '''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        matchmaking_configuration_name: builtins.str,
        rule_set: IMatchmakingRuleSet,
        acceptance_timeout: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        custom_event_data: typing.Optional[builtins.str] = None,
        description: typing.Optional[builtins.str] = None,
        notification_target: typing.Optional[_aws_cdk_aws_sns_ceddda9d.ITopic] = None,
        request_timeout: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        require_acceptance: typing.Optional[builtins.bool] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param matchmaking_configuration_name: (experimental) A unique identifier for the matchmaking configuration. This name is used to identify the configuration associated with a matchmaking request or ticket.
        :param rule_set: (experimental) A matchmaking rule set to use with this configuration. A matchmaking configuration can only use rule sets that are defined in the same Region.
        :param acceptance_timeout: (experimental) The length of time (in seconds) to wait for players to accept a proposed match, if acceptance is required. Default: 300 seconds
        :param custom_event_data: (experimental) Information to add to all events related to the matchmaking configuration. Default: no custom data added to events
        :param description: (experimental) A human-readable description of the matchmaking configuration. Default: no description is provided
        :param notification_target: (experimental) An SNS topic ARN that is set up to receive matchmaking notifications. Default: no notification target
        :param request_timeout: (experimental) The maximum duration, that a matchmaking ticket can remain in process before timing out. Requests that fail due to timing out can be resubmitted as needed. Default: 300 seconds
        :param require_acceptance: (experimental) A flag that determines whether a match that was created with this configuration must be accepted by the matched players. With this option enabled, matchmaking tickets use the status ``REQUIRES_ACCEPTANCE`` to indicate when a completed potential match is waiting for player acceptance. Default: Acceptance is not required

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__154c82c2c0fb5d36e7cc47ebca648ca30fa0731aa50bf433bc6f20396b12cbbf)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = StandaloneMatchmakingConfigurationProps(
            matchmaking_configuration_name=matchmaking_configuration_name,
            rule_set=rule_set,
            acceptance_timeout=acceptance_timeout,
            custom_event_data=custom_event_data,
            description=description,
            notification_target=notification_target,
            request_timeout=request_timeout,
            require_acceptance=require_acceptance,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @jsii.member(jsii_name="fromStandaloneMatchmakingConfigurationArn")
    @builtins.classmethod
    def from_standalone_matchmaking_configuration_arn(
        cls,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        matchmaking_configuration_arn: builtins.str,
    ) -> IMatchmakingConfiguration:
        '''(experimental) Import an existing matchmaking configuration from its ARN.

        :param scope: -
        :param id: -
        :param matchmaking_configuration_arn: -

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3793d6f8154e15ae69df761a8dfca36610171696829c6d3bc7d9bd1ee9e7b6d7)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument matchmaking_configuration_arn", value=matchmaking_configuration_arn, expected_type=type_hints["matchmaking_configuration_arn"])
        return typing.cast(IMatchmakingConfiguration, jsii.sinvoke(cls, "fromStandaloneMatchmakingConfigurationArn", [scope, id, matchmaking_configuration_arn]))

    @jsii.member(jsii_name="fromStandaloneMatchmakingConfigurationName")
    @builtins.classmethod
    def from_standalone_matchmaking_configuration_name(
        cls,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        matchmaking_configuration_name: builtins.str,
    ) -> IMatchmakingConfiguration:
        '''(experimental) Import an existing matchmaking configuration from its name.

        :param scope: -
        :param id: -
        :param matchmaking_configuration_name: -

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__07c04bfca9c496a8644c2e6e10359ca3a4954a3a29632bc3f6c59cd1e39240ad)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument matchmaking_configuration_name", value=matchmaking_configuration_name, expected_type=type_hints["matchmaking_configuration_name"])
        return typing.cast(IMatchmakingConfiguration, jsii.sinvoke(cls, "fromStandaloneMatchmakingConfigurationName", [scope, id, matchmaking_configuration_name]))

    @jsii.python.classproperty
    @jsii.member(jsii_name="PROPERTY_INJECTION_ID")
    def PROPERTY_INJECTION_ID(cls) -> builtins.str:
        '''(experimental) Uniquely identifies this class.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "PROPERTY_INJECTION_ID"))

    @builtins.property
    @jsii.member(jsii_name="matchmakingConfigurationArn")
    def matchmaking_configuration_arn(self) -> builtins.str:
        '''(experimental) The ARN of the matchmaking configuration.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "matchmakingConfigurationArn"))

    @builtins.property
    @jsii.member(jsii_name="matchmakingConfigurationName")
    def matchmaking_configuration_name(self) -> builtins.str:
        '''(experimental) The Identifier of the matchmaking configuration.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "matchmakingConfigurationName"))

    @builtins.property
    @jsii.member(jsii_name="notificationTarget")
    def notification_target(self) -> typing.Optional[_aws_cdk_aws_sns_ceddda9d.ITopic]:
        '''(experimental) The notification target for matchmaking events.

        :stability: experimental
        '''
        return typing.cast(typing.Optional[_aws_cdk_aws_sns_ceddda9d.ITopic], jsii.get(self, "notificationTarget"))


@jsii.data_type(
    jsii_type="@aws-cdk/aws-gamelift-alpha.StandaloneMatchmakingConfigurationProps",
    jsii_struct_bases=[MatchmakingConfigurationProps],
    name_mapping={
        "matchmaking_configuration_name": "matchmakingConfigurationName",
        "rule_set": "ruleSet",
        "acceptance_timeout": "acceptanceTimeout",
        "custom_event_data": "customEventData",
        "description": "description",
        "notification_target": "notificationTarget",
        "request_timeout": "requestTimeout",
        "require_acceptance": "requireAcceptance",
    },
)
class StandaloneMatchmakingConfigurationProps(MatchmakingConfigurationProps):
    def __init__(
        self,
        *,
        matchmaking_configuration_name: builtins.str,
        rule_set: IMatchmakingRuleSet,
        acceptance_timeout: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        custom_event_data: typing.Optional[builtins.str] = None,
        description: typing.Optional[builtins.str] = None,
        notification_target: typing.Optional[_aws_cdk_aws_sns_ceddda9d.ITopic] = None,
        request_timeout: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        require_acceptance: typing.Optional[builtins.bool] = None,
    ) -> None:
        '''(experimental) Properties for a new standalone matchmaking configuration.

        :param matchmaking_configuration_name: (experimental) A unique identifier for the matchmaking configuration. This name is used to identify the configuration associated with a matchmaking request or ticket.
        :param rule_set: (experimental) A matchmaking rule set to use with this configuration. A matchmaking configuration can only use rule sets that are defined in the same Region.
        :param acceptance_timeout: (experimental) The length of time (in seconds) to wait for players to accept a proposed match, if acceptance is required. Default: 300 seconds
        :param custom_event_data: (experimental) Information to add to all events related to the matchmaking configuration. Default: no custom data added to events
        :param description: (experimental) A human-readable description of the matchmaking configuration. Default: no description is provided
        :param notification_target: (experimental) An SNS topic ARN that is set up to receive matchmaking notifications. Default: no notification target
        :param request_timeout: (experimental) The maximum duration, that a matchmaking ticket can remain in process before timing out. Requests that fail due to timing out can be resubmitted as needed. Default: 300 seconds
        :param require_acceptance: (experimental) A flag that determines whether a match that was created with this configuration must be accepted by the matched players. With this option enabled, matchmaking tickets use the status ``REQUIRES_ACCEPTANCE`` to indicate when a completed potential match is waiting for player acceptance. Default: Acceptance is not required

        :stability: experimental
        :exampleMetadata: infused

        Example::

            # rule_set: gamelift.MatchmakingRuleSet
            
            
            gamelift.StandaloneMatchmakingConfiguration(self, "StandaloneMatchmaking",
                matchmaking_configuration_name="test-standalone-config-name",
                rule_set=rule_set
            )
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__34016871359c2c8b76308f8d09850850ca95c46f84197bbb1a714abb1558d1db)
            check_type(argname="argument matchmaking_configuration_name", value=matchmaking_configuration_name, expected_type=type_hints["matchmaking_configuration_name"])
            check_type(argname="argument rule_set", value=rule_set, expected_type=type_hints["rule_set"])
            check_type(argname="argument acceptance_timeout", value=acceptance_timeout, expected_type=type_hints["acceptance_timeout"])
            check_type(argname="argument custom_event_data", value=custom_event_data, expected_type=type_hints["custom_event_data"])
            check_type(argname="argument description", value=description, expected_type=type_hints["description"])
            check_type(argname="argument notification_target", value=notification_target, expected_type=type_hints["notification_target"])
            check_type(argname="argument request_timeout", value=request_timeout, expected_type=type_hints["request_timeout"])
            check_type(argname="argument require_acceptance", value=require_acceptance, expected_type=type_hints["require_acceptance"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "matchmaking_configuration_name": matchmaking_configuration_name,
            "rule_set": rule_set,
        }
        if acceptance_timeout is not None:
            self._values["acceptance_timeout"] = acceptance_timeout
        if custom_event_data is not None:
            self._values["custom_event_data"] = custom_event_data
        if description is not None:
            self._values["description"] = description
        if notification_target is not None:
            self._values["notification_target"] = notification_target
        if request_timeout is not None:
            self._values["request_timeout"] = request_timeout
        if require_acceptance is not None:
            self._values["require_acceptance"] = require_acceptance

    @builtins.property
    def matchmaking_configuration_name(self) -> builtins.str:
        '''(experimental) A unique identifier for the matchmaking configuration.

        This name is used to identify the configuration associated with a matchmaking request or ticket.

        :stability: experimental
        '''
        result = self._values.get("matchmaking_configuration_name")
        assert result is not None, "Required property 'matchmaking_configuration_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def rule_set(self) -> IMatchmakingRuleSet:
        '''(experimental) A matchmaking rule set to use with this configuration.

        A matchmaking configuration can only use rule sets that are defined in the same Region.

        :stability: experimental
        '''
        result = self._values.get("rule_set")
        assert result is not None, "Required property 'rule_set' is missing"
        return typing.cast(IMatchmakingRuleSet, result)

    @builtins.property
    def acceptance_timeout(self) -> typing.Optional[_aws_cdk_ceddda9d.Duration]:
        '''(experimental) The length of time (in seconds) to wait for players to accept a proposed match, if acceptance is required.

        :default: 300 seconds

        :stability: experimental
        '''
        result = self._values.get("acceptance_timeout")
        return typing.cast(typing.Optional[_aws_cdk_ceddda9d.Duration], result)

    @builtins.property
    def custom_event_data(self) -> typing.Optional[builtins.str]:
        '''(experimental) Information to add to all events related to the matchmaking configuration.

        :default: no custom data added to events

        :stability: experimental
        '''
        result = self._values.get("custom_event_data")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        '''(experimental) A human-readable description of the matchmaking configuration.

        :default: no description is provided

        :stability: experimental
        '''
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def notification_target(self) -> typing.Optional[_aws_cdk_aws_sns_ceddda9d.ITopic]:
        '''(experimental) An SNS topic ARN that is set up to receive matchmaking notifications.

        :default: no notification target

        :see: https://docs.aws.amazon.com/gamelift/latest/flexmatchguide/match-notification.html
        :stability: experimental
        '''
        result = self._values.get("notification_target")
        return typing.cast(typing.Optional[_aws_cdk_aws_sns_ceddda9d.ITopic], result)

    @builtins.property
    def request_timeout(self) -> typing.Optional[_aws_cdk_ceddda9d.Duration]:
        '''(experimental) The maximum duration, that a matchmaking ticket can remain in process before timing out.

        Requests that fail due to timing out can be resubmitted as needed.

        :default: 300 seconds

        :stability: experimental
        '''
        result = self._values.get("request_timeout")
        return typing.cast(typing.Optional[_aws_cdk_ceddda9d.Duration], result)

    @builtins.property
    def require_acceptance(self) -> typing.Optional[builtins.bool]:
        '''(experimental) A flag that determines whether a match that was created with this configuration must be accepted by the matched players.

        With this option enabled, matchmaking tickets use the status ``REQUIRES_ACCEPTANCE`` to indicate when a completed potential match is waiting for player acceptance.

        :default: Acceptance is not required

        :stability: experimental
        '''
        result = self._values.get("require_acceptance")
        return typing.cast(typing.Optional[builtins.bool], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "StandaloneMatchmakingConfigurationProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class AssetContent(
    Content,
    metaclass=jsii.JSIIMeta,
    jsii_type="@aws-cdk/aws-gamelift-alpha.AssetContent",
):
    '''(experimental) Game content from a local directory.

    :stability: experimental
    :exampleMetadata: fixture=_generated

    Example::

        # The code below shows an example of how to instantiate this type.
        # The values are placeholders you should change.
        import aws_cdk.aws_gamelift_alpha as gamelift_alpha
        import aws_cdk as cdk
        from aws_cdk import aws_iam as iam
        from aws_cdk import aws_kms as kms
        
        # docker_image: cdk.DockerImage
        # grantable: iam.IGrantable
        # key: kms.Key
        # local_bundling: cdk.ILocalBundling
        
        asset_content = gamelift_alpha.AssetContent("path",
            asset_hash="assetHash",
            asset_hash_type=cdk.AssetHashType.SOURCE,
            bundling=cdk.BundlingOptions(
                image=docker_image,
        
                # the properties below are optional
                bundling_file_access=cdk.BundlingFileAccess.VOLUME_COPY,
                command=["command"],
                entrypoint=["entrypoint"],
                environment={
                    "environment_key": "environment"
                },
                local=local_bundling,
                network="network",
                output_type=cdk.BundlingOutput.ARCHIVED,
                platform="platform",
                security_opt="securityOpt",
                user="user",
                volumes=[cdk.DockerVolume(
                    container_path="containerPath",
                    host_path="hostPath",
        
                    # the properties below are optional
                    consistency=cdk.DockerVolumeConsistency.CONSISTENT
                )],
                volumes_from=["volumesFrom"],
                working_directory="workingDirectory"
            ),
            deploy_time=False,
            display_name="displayName",
            exclude=["exclude"],
            follow_symlinks=cdk.SymlinkFollowMode.NEVER,
            ignore_mode=cdk.IgnoreMode.GLOB,
            readers=[grantable],
            source_kMSKey=key
        )
    '''

    def __init__(
        self,
        path: builtins.str,
        *,
        deploy_time: typing.Optional[builtins.bool] = None,
        display_name: typing.Optional[builtins.str] = None,
        readers: typing.Optional[typing.Sequence[_aws_cdk_aws_iam_ceddda9d.IGrantable]] = None,
        source_kms_key: typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey] = None,
        asset_hash: typing.Optional[builtins.str] = None,
        asset_hash_type: typing.Optional[_aws_cdk_ceddda9d.AssetHashType] = None,
        bundling: typing.Optional[typing.Union[_aws_cdk_ceddda9d.BundlingOptions, typing.Dict[builtins.str, typing.Any]]] = None,
        exclude: typing.Optional[typing.Sequence[builtins.str]] = None,
        follow_symlinks: typing.Optional[_aws_cdk_ceddda9d.SymlinkFollowMode] = None,
        ignore_mode: typing.Optional[_aws_cdk_ceddda9d.IgnoreMode] = None,
    ) -> None:
        '''
        :param path: The path to the asset file or directory.
        :param deploy_time: Whether or not the asset needs to exist beyond deployment time; i.e. are copied over to a different location and not needed afterwards. Setting this property to true has an impact on the lifecycle of the asset, because we will assume that it is safe to delete after the CloudFormation deployment succeeds. For example, Lambda Function assets are copied over to Lambda during deployment. Therefore, it is not necessary to store the asset in S3, so we consider those deployTime assets. Default: false
        :param display_name: A display name for this asset. If supplied, the display name will be used in locations where the asset identifier is printed, like in the CLI progress information. If the same asset is added multiple times, the display name of the first occurrence is used. The default is the construct path of the Asset construct, with respect to the enclosing stack. If the asset is produced by a construct helper function (such as ``lambda.Code.fromAsset()``), this will look like ``MyFunction/Code``. We use the stack-relative construct path so that in the common case where you have multiple stacks with the same asset, we won't show something like ``/MyBetaStack/MyFunction/Code`` when you are actually deploying to production. Default: - Stack-relative construct path
        :param readers: A list of principals that should be able to read this asset from S3. You can use ``asset.grantRead(principal)`` to grant read permissions later. Default: - No principals that can read file asset.
        :param source_kms_key: The ARN of the KMS key used to encrypt the handler code. Default: - the default server-side encryption with Amazon S3 managed keys(SSE-S3) key will be used.
        :param asset_hash: Specify a custom hash for this asset. If ``assetHashType`` is set it must be set to ``AssetHashType.CUSTOM``. For consistency, this custom hash will be SHA256 hashed and encoded as hex. The resulting hash will be the asset hash. NOTE: the hash is used in order to identify a specific revision of the asset, and used for optimizing and caching deployment activities related to this asset such as packaging, uploading to Amazon S3, etc. If you chose to customize the hash, you will need to make sure it is updated every time the asset changes, or otherwise it is possible that some deployments will not be invalidated. Default: - based on ``assetHashType``
        :param asset_hash_type: Specifies the type of hash to calculate for this asset. If ``assetHash`` is configured, this option must be ``undefined`` or ``AssetHashType.CUSTOM``. Default: - the default is ``AssetHashType.SOURCE``, but if ``assetHash`` is explicitly specified this value defaults to ``AssetHashType.CUSTOM``.
        :param bundling: Bundle the asset by executing a command in a Docker container or a custom bundling provider. The asset path will be mounted at ``/asset-input``. The Docker container is responsible for putting content at ``/asset-output``. The content at ``/asset-output`` will be zipped and used as the final asset. Default: - uploaded as-is to S3 if the asset is a regular file or a .zip file, archived into a .zip file and uploaded to S3 otherwise
        :param exclude: File paths matching the patterns will be excluded. See ``ignoreMode`` to set the matching behavior. Has no effect on Assets bundled using the ``bundling`` property. Default: - nothing is excluded
        :param follow_symlinks: A strategy for how to handle symlinks. Default: SymlinkFollowMode.NEVER
        :param ignore_mode: The ignore behavior to use for ``exclude`` patterns. Default: IgnoreMode.GLOB

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__fbfe673262616ef52c985ab1e4f7220c127e7658477cda89ab362836b7456d63)
            check_type(argname="argument path", value=path, expected_type=type_hints["path"])
        options = _aws_cdk_aws_s3_assets_ceddda9d.AssetOptions(
            deploy_time=deploy_time,
            display_name=display_name,
            readers=readers,
            source_kms_key=source_kms_key,
            asset_hash=asset_hash,
            asset_hash_type=asset_hash_type,
            bundling=bundling,
            exclude=exclude,
            follow_symlinks=follow_symlinks,
            ignore_mode=ignore_mode,
        )

        jsii.create(self.__class__, self, [path, options])

    @jsii.member(jsii_name="bind")
    def bind(
        self,
        scope: _constructs_77d1e7e8.Construct,
        role: _aws_cdk_aws_iam_ceddda9d.IRole,
    ) -> ContentConfig:
        '''(experimental) Called when the Build is initialized to allow this object to bind.

        :param scope: -
        :param role: -

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__088d51b6537b57f99fb8a11bafc0f9452e787bbb2082ef8f1e59a5fac6f6ec3e)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument role", value=role, expected_type=type_hints["role"])
        return typing.cast(ContentConfig, jsii.invoke(self, "bind", [scope, role]))

    @builtins.property
    @jsii.member(jsii_name="path")
    def path(self) -> builtins.str:
        '''(experimental) The path to the asset file or directory.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "path"))


@jsii.implements(IBuild)
class BuildBase(
    _aws_cdk_ceddda9d.Resource,
    metaclass=jsii.JSIIAbstractClass,
    jsii_type="@aws-cdk/aws-gamelift-alpha.BuildBase",
):
    '''(experimental) Base class for new and imported GameLift server build.

    :stability: experimental
    '''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        account: typing.Optional[builtins.str] = None,
        environment_from_arn: typing.Optional[builtins.str] = None,
        physical_name: typing.Optional[builtins.str] = None,
        region: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param account: The AWS account ID this resource belongs to. Default: - the resource is in the same account as the stack it belongs to
        :param environment_from_arn: ARN to deduce region and account from. The ARN is parsed and the account and region are taken from the ARN. This should be used for imported resources. Cannot be supplied together with either ``account`` or ``region``. Default: - take environment from ``account``, ``region`` parameters, or use Stack environment.
        :param physical_name: The value passed in by users to the physical name prop of the resource. - ``undefined`` implies that a physical name will be allocated by CloudFormation during deployment. - a concrete value implies a specific physical name - ``PhysicalName.GENERATE_IF_NEEDED`` is a marker that indicates that a physical will only be generated by the CDK if it is needed for cross-environment references. Otherwise, it will be allocated by CloudFormation. Default: - The physical name will be allocated by CloudFormation at deployment time
        :param region: The AWS region this resource belongs to. Default: - the resource is in the same region as the stack it belongs to
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f91b9b3796935bd0b85afcc48cf565d44bb67b47cd97b5c0a12fbb150c5a01a7)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = _aws_cdk_ceddda9d.ResourceProps(
            account=account,
            environment_from_arn=environment_from_arn,
            physical_name=physical_name,
            region=region,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @builtins.property
    @jsii.member(jsii_name="buildArn")
    @abc.abstractmethod
    def build_arn(self) -> builtins.str:
        '''(experimental) The ARN of the build.

        :stability: experimental
        '''
        ...

    @builtins.property
    @jsii.member(jsii_name="buildId")
    @abc.abstractmethod
    def build_id(self) -> builtins.str:
        '''(experimental) The Identifier of the build.

        :stability: experimental
        '''
        ...

    @builtins.property
    @jsii.member(jsii_name="grantPrincipal")
    @abc.abstractmethod
    def grant_principal(self) -> _aws_cdk_aws_iam_ceddda9d.IPrincipal:
        '''(experimental) The principal to grant permissions to.

        :stability: experimental
        '''
        ...


class _BuildBaseProxy(
    BuildBase,
    jsii.proxy_for(_aws_cdk_ceddda9d.Resource), # type: ignore[misc]
):
    @builtins.property
    @jsii.member(jsii_name="buildArn")
    def build_arn(self) -> builtins.str:
        '''(experimental) The ARN of the build.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "buildArn"))

    @builtins.property
    @jsii.member(jsii_name="buildId")
    def build_id(self) -> builtins.str:
        '''(experimental) The Identifier of the build.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "buildId"))

    @builtins.property
    @jsii.member(jsii_name="grantPrincipal")
    def grant_principal(self) -> _aws_cdk_aws_iam_ceddda9d.IPrincipal:
        '''(experimental) The principal to grant permissions to.

        :stability: experimental
        '''
        return typing.cast(_aws_cdk_aws_iam_ceddda9d.IPrincipal, jsii.get(self, "grantPrincipal"))

# Adding a "__jsii_proxy_class__(): typing.Type" function to the abstract class
typing.cast(typing.Any, BuildBase).__jsii_proxy_class__ = lambda : _BuildBaseProxy


@jsii.data_type(
    jsii_type="@aws-cdk/aws-gamelift-alpha.BuildFleetProps",
    jsii_struct_bases=[FleetProps],
    name_mapping={
        "fleet_name": "fleetName",
        "instance_type": "instanceType",
        "runtime_configuration": "runtimeConfiguration",
        "description": "description",
        "desired_capacity": "desiredCapacity",
        "locations": "locations",
        "max_size": "maxSize",
        "metric_group": "metricGroup",
        "min_size": "minSize",
        "peer_vpc": "peerVpc",
        "protect_new_game_session": "protectNewGameSession",
        "resource_creation_limit_policy": "resourceCreationLimitPolicy",
        "role": "role",
        "use_certificate": "useCertificate",
        "use_spot": "useSpot",
        "content": "content",
        "ingress_rules": "ingressRules",
    },
)
class BuildFleetProps(FleetProps):
    def __init__(
        self,
        *,
        fleet_name: builtins.str,
        instance_type: _aws_cdk_aws_ec2_ceddda9d.InstanceType,
        runtime_configuration: typing.Union[RuntimeConfiguration, typing.Dict[builtins.str, typing.Any]],
        description: typing.Optional[builtins.str] = None,
        desired_capacity: typing.Optional[jsii.Number] = None,
        locations: typing.Optional[typing.Sequence[typing.Union[Location, typing.Dict[builtins.str, typing.Any]]]] = None,
        max_size: typing.Optional[jsii.Number] = None,
        metric_group: typing.Optional[builtins.str] = None,
        min_size: typing.Optional[jsii.Number] = None,
        peer_vpc: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IVpc] = None,
        protect_new_game_session: typing.Optional[builtins.bool] = None,
        resource_creation_limit_policy: typing.Optional[typing.Union[ResourceCreationLimitPolicy, typing.Dict[builtins.str, typing.Any]]] = None,
        role: typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole] = None,
        use_certificate: typing.Optional[builtins.bool] = None,
        use_spot: typing.Optional[builtins.bool] = None,
        content: IBuild,
        ingress_rules: typing.Optional[typing.Sequence[typing.Union[IngressRule, typing.Dict[builtins.str, typing.Any]]]] = None,
    ) -> None:
        '''(experimental) Properties for a new Gamelift build fleet.

        :param fleet_name: (experimental) A descriptive label that is associated with a fleet. Fleet names do not need to be unique.
        :param instance_type: (experimental) The GameLift-supported Amazon EC2 instance type to use for all fleet instances. Instance type determines the computing resources that will be used to host your game servers, including CPU, memory, storage, and networking capacity.
        :param runtime_configuration: (experimental) A collection of server process configurations that describe the set of processes to run on each instance in a fleet. Server processes run either an executable in a custom game build or a Realtime Servers script. GameLift launches the configured processes, manages their life cycle, and replaces them as needed. Each instance checks regularly for an updated runtime configuration. A GameLift instance is limited to 50 processes running concurrently. To calculate the total number of processes in a runtime configuration, add the values of the ConcurrentExecutions parameter for each ServerProcess.
        :param description: (experimental) A human-readable description of the fleet. Default: no description is provided
        :param desired_capacity: (experimental) The number of EC2 instances that you want this fleet to host. When creating a new fleet, GameLift automatically sets this value to "1" and initiates a single instance. Once the fleet is active, update this value to trigger GameLift to add or remove instances from the fleet. Default: Default capacity is 0
        :param locations: (experimental) A set of remote locations to deploy additional instances to and manage as part of the fleet. This parameter can only be used when creating fleets in AWS Regions that support multiple locations. You can add any GameLift-supported AWS Region as a remote location, in the form of an AWS Region code such as ``us-west-2``. To create a fleet with instances in the home region only, omit this parameter. Default: Create a fleet with instances in the home region only
        :param max_size: (experimental) The maximum number of instances that are allowed in the specified fleet location. Default: the default is 1
        :param metric_group: (experimental) The name of an AWS CloudWatch metric group to add this fleet to. A metric group is used to aggregate the metrics for multiple fleets. You can specify an existing metric group name or set a new name to create a new metric group. A fleet can be included in only one metric group at a time. Default: Fleet metrics are aggregated with other fleets in the default metric group
        :param min_size: (experimental) The minimum number of instances that are allowed in the specified fleet location. Default: the default is 0
        :param peer_vpc: (experimental) A VPC peering connection between your GameLift-hosted game servers and your other non-GameLift resources. Use Amazon Virtual Private Cloud (VPC) peering connections to enable your game servers to communicate directly and privately with your other AWS resources, such as a web service or a repository. You can establish VPC peering with any resources that run on AWS and are managed by an AWS account that you have access to. The VPC must be in the same Region as your fleet. Warning: Be sure to create a VPC Peering authorization through Gamelift Service API. Default: no vpc peering
        :param protect_new_game_session: (experimental) The status of termination protection for active game sessions on the fleet. By default, new game sessions are protected and cannot be terminated during a scale-down event. Default: true - Game sessions in ``ACTIVE`` status cannot be terminated during a scale-down event.
        :param resource_creation_limit_policy: (experimental) A policy that limits the number of game sessions that an individual player can create on instances in this fleet within a specified span of time. Default: No resource creation limit policy
        :param role: (experimental) The IAM role assumed by GameLift fleet instances to access AWS ressources. With a role set, any application that runs on an instance in this fleet can assume the role, including install scripts, server processes, and daemons (background processes). If providing a custom role, it needs to trust the GameLift service principal (gamelift.amazonaws.com). No permission is required by default. This property cannot be changed after the fleet is created. Default: - a role will be created with default trust to Gamelift service principal.
        :param use_certificate: (experimental) Prompts GameLift to generate a TLS/SSL certificate for the fleet. GameLift uses the certificates to encrypt traffic between game clients and the game servers running on GameLift. You can't change this property after you create the fleet. Additionnal info: AWS Certificate Manager (ACM) certificates expire after 13 months. Certificate expiration can cause fleets to fail, preventing players from connecting to instances in the fleet. We recommend you replace fleets before 13 months, consider using fleet aliases for a smooth transition. Default: TLS/SSL certificate are generated for the fleet
        :param use_spot: (experimental) Indicates whether to use On-Demand or Spot instances for this fleet. By default, fleet use on demand capacity. This property cannot be changed after the fleet is created. Default: Gamelift fleet use on demand capacity
        :param content: (experimental) A build to be deployed on the fleet. The build must have been successfully uploaded to Amazon GameLift and be in a ``READY`` status. This fleet setting cannot be changed once the fleet is created.
        :param ingress_rules: (experimental) The allowed IP address ranges and port settings that allow inbound traffic to access game sessions on this fleet. This property must be set before players can connect to game sessions. Default: no inbound traffic allowed

        :stability: experimental
        :exampleMetadata: infused

        Example::

            # build: gamelift.Build
            
            # Server processes can be delcared in a declarative way through the constructor
            fleet = gamelift.BuildFleet(self, "Game server fleet",
                fleet_name="test-fleet",
                content=build,
                instance_type=ec2.InstanceType.of(ec2.InstanceClass.C4, ec2.InstanceSize.LARGE),
                runtime_configuration=gamelift.RuntimeConfiguration(
                    server_processes=[gamelift.ServerProcess(
                        launch_path="/local/game/GameLiftExampleServer.x86_64",
                        parameters="-logFile /local/game/logs/myserver1935.log -port 1935",
                        concurrent_executions=100
                    )]
                )
            )
        '''
        if isinstance(runtime_configuration, dict):
            runtime_configuration = RuntimeConfiguration(**runtime_configuration)
        if isinstance(resource_creation_limit_policy, dict):
            resource_creation_limit_policy = ResourceCreationLimitPolicy(**resource_creation_limit_policy)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9418742f4dd29cadc75ff372ca21cc393ca180dfd8ecbddf8d173d1db503bb13)
            check_type(argname="argument fleet_name", value=fleet_name, expected_type=type_hints["fleet_name"])
            check_type(argname="argument instance_type", value=instance_type, expected_type=type_hints["instance_type"])
            check_type(argname="argument runtime_configuration", value=runtime_configuration, expected_type=type_hints["runtime_configuration"])
            check_type(argname="argument description", value=description, expected_type=type_hints["description"])
            check_type(argname="argument desired_capacity", value=desired_capacity, expected_type=type_hints["desired_capacity"])
            check_type(argname="argument locations", value=locations, expected_type=type_hints["locations"])
            check_type(argname="argument max_size", value=max_size, expected_type=type_hints["max_size"])
            check_type(argname="argument metric_group", value=metric_group, expected_type=type_hints["metric_group"])
            check_type(argname="argument min_size", value=min_size, expected_type=type_hints["min_size"])
            check_type(argname="argument peer_vpc", value=peer_vpc, expected_type=type_hints["peer_vpc"])
            check_type(argname="argument protect_new_game_session", value=protect_new_game_session, expected_type=type_hints["protect_new_game_session"])
            check_type(argname="argument resource_creation_limit_policy", value=resource_creation_limit_policy, expected_type=type_hints["resource_creation_limit_policy"])
            check_type(argname="argument role", value=role, expected_type=type_hints["role"])
            check_type(argname="argument use_certificate", value=use_certificate, expected_type=type_hints["use_certificate"])
            check_type(argname="argument use_spot", value=use_spot, expected_type=type_hints["use_spot"])
            check_type(argname="argument content", value=content, expected_type=type_hints["content"])
            check_type(argname="argument ingress_rules", value=ingress_rules, expected_type=type_hints["ingress_rules"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "fleet_name": fleet_name,
            "instance_type": instance_type,
            "runtime_configuration": runtime_configuration,
            "content": content,
        }
        if description is not None:
            self._values["description"] = description
        if desired_capacity is not None:
            self._values["desired_capacity"] = desired_capacity
        if locations is not None:
            self._values["locations"] = locations
        if max_size is not None:
            self._values["max_size"] = max_size
        if metric_group is not None:
            self._values["metric_group"] = metric_group
        if min_size is not None:
            self._values["min_size"] = min_size
        if peer_vpc is not None:
            self._values["peer_vpc"] = peer_vpc
        if protect_new_game_session is not None:
            self._values["protect_new_game_session"] = protect_new_game_session
        if resource_creation_limit_policy is not None:
            self._values["resource_creation_limit_policy"] = resource_creation_limit_policy
        if role is not None:
            self._values["role"] = role
        if use_certificate is not None:
            self._values["use_certificate"] = use_certificate
        if use_spot is not None:
            self._values["use_spot"] = use_spot
        if ingress_rules is not None:
            self._values["ingress_rules"] = ingress_rules

    @builtins.property
    def fleet_name(self) -> builtins.str:
        '''(experimental) A descriptive label that is associated with a fleet.

        Fleet names do not need to be unique.

        :stability: experimental
        '''
        result = self._values.get("fleet_name")
        assert result is not None, "Required property 'fleet_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def instance_type(self) -> _aws_cdk_aws_ec2_ceddda9d.InstanceType:
        '''(experimental) The GameLift-supported Amazon EC2 instance type to use for all fleet instances.

        Instance type determines the computing resources that will be used to host your game servers, including CPU, memory, storage, and networking capacity.

        :see: http://aws.amazon.com/ec2/instance-types/ for detailed descriptions of Amazon EC2 instance types.
        :stability: experimental
        '''
        result = self._values.get("instance_type")
        assert result is not None, "Required property 'instance_type' is missing"
        return typing.cast(_aws_cdk_aws_ec2_ceddda9d.InstanceType, result)

    @builtins.property
    def runtime_configuration(self) -> RuntimeConfiguration:
        '''(experimental) A collection of server process configurations that describe the set of processes to run on each instance in a fleet.

        Server processes run either an executable in a custom game build or a Realtime Servers script.
        GameLift launches the configured processes, manages their life cycle, and replaces them as needed.
        Each instance checks regularly for an updated runtime configuration.

        A GameLift instance is limited to 50 processes running concurrently.
        To calculate the total number of processes in a runtime configuration, add the values of the ConcurrentExecutions parameter for each ServerProcess.

        :see: https://docs.aws.amazon.com/gamelift/latest/developerguide/fleets-multiprocess.html
        :stability: experimental
        '''
        result = self._values.get("runtime_configuration")
        assert result is not None, "Required property 'runtime_configuration' is missing"
        return typing.cast(RuntimeConfiguration, result)

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        '''(experimental) A human-readable description of the fleet.

        :default: no description is provided

        :stability: experimental
        '''
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def desired_capacity(self) -> typing.Optional[jsii.Number]:
        '''(experimental) The number of EC2 instances that you want this fleet to host.

        When creating a new fleet, GameLift automatically sets this value to "1" and initiates a single instance.
        Once the fleet is active, update this value to trigger GameLift to add or remove instances from the fleet.

        :default: Default capacity is 0

        :stability: experimental
        '''
        result = self._values.get("desired_capacity")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def locations(self) -> typing.Optional[typing.List[Location]]:
        '''(experimental) A set of remote locations to deploy additional instances to and manage as part of the fleet.

        This parameter can only be used when creating fleets in AWS Regions that support multiple locations.
        You can add any GameLift-supported AWS Region as a remote location, in the form of an AWS Region code such as ``us-west-2``.
        To create a fleet with instances in the home region only, omit this parameter.

        :default: Create a fleet with instances in the home region only

        :stability: experimental
        '''
        result = self._values.get("locations")
        return typing.cast(typing.Optional[typing.List[Location]], result)

    @builtins.property
    def max_size(self) -> typing.Optional[jsii.Number]:
        '''(experimental) The maximum number of instances that are allowed in the specified fleet location.

        :default: the default is 1

        :stability: experimental
        '''
        result = self._values.get("max_size")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def metric_group(self) -> typing.Optional[builtins.str]:
        '''(experimental) The name of an AWS CloudWatch metric group to add this fleet to.

        A metric group is used to aggregate the metrics for multiple fleets.
        You can specify an existing metric group name or set a new name to create a new metric group.
        A fleet can be included in only one metric group at a time.

        :default: Fleet metrics are aggregated with other fleets in the default metric group

        :stability: experimental
        '''
        result = self._values.get("metric_group")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def min_size(self) -> typing.Optional[jsii.Number]:
        '''(experimental) The minimum number of instances that are allowed in the specified fleet location.

        :default: the default is 0

        :stability: experimental
        '''
        result = self._values.get("min_size")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def peer_vpc(self) -> typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IVpc]:
        '''(experimental) A VPC peering connection between your GameLift-hosted game servers and your other non-GameLift resources.

        Use Amazon Virtual Private Cloud (VPC) peering connections to enable your game servers to communicate directly and privately with your other AWS resources, such as a web service or a repository.
        You can establish VPC peering with any resources that run on AWS and are managed by an AWS account that you have access to.
        The VPC must be in the same Region as your fleet.

        Warning:
        Be sure to create a VPC Peering authorization through Gamelift Service API.

        :default: no vpc peering

        :see: https://docs.aws.amazon.com/gamelift/latest/developerguide/vpc-peering.html
        :stability: experimental
        '''
        result = self._values.get("peer_vpc")
        return typing.cast(typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IVpc], result)

    @builtins.property
    def protect_new_game_session(self) -> typing.Optional[builtins.bool]:
        '''(experimental) The status of termination protection for active game sessions on the fleet.

        By default, new game sessions are protected and cannot be terminated during a scale-down event.

        :default: true - Game sessions in ``ACTIVE`` status cannot be terminated during a scale-down event.

        :stability: experimental
        '''
        result = self._values.get("protect_new_game_session")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def resource_creation_limit_policy(
        self,
    ) -> typing.Optional[ResourceCreationLimitPolicy]:
        '''(experimental) A policy that limits the number of game sessions that an individual player can create on instances in this fleet within a specified span of time.

        :default: No resource creation limit policy

        :stability: experimental
        '''
        result = self._values.get("resource_creation_limit_policy")
        return typing.cast(typing.Optional[ResourceCreationLimitPolicy], result)

    @builtins.property
    def role(self) -> typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole]:
        '''(experimental) The IAM role assumed by GameLift fleet instances to access AWS ressources.

        With a role set, any application that runs on an instance in this fleet can assume the role, including install scripts, server processes, and daemons (background processes).
        If providing a custom role, it needs to trust the GameLift service principal (gamelift.amazonaws.com).
        No permission is required by default.

        This property cannot be changed after the fleet is created.

        :default: - a role will be created with default trust to Gamelift service principal.

        :see: https://docs.aws.amazon.com/gamelift/latest/developerguide/gamelift-sdk-server-resources.html
        :stability: experimental
        '''
        result = self._values.get("role")
        return typing.cast(typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole], result)

    @builtins.property
    def use_certificate(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Prompts GameLift to generate a TLS/SSL certificate for the fleet.

        GameLift uses the certificates to encrypt traffic between game clients and the game servers running on GameLift.

        You can't change this property after you create the fleet.

        Additionnal info:
        AWS Certificate Manager (ACM) certificates expire after 13 months.
        Certificate expiration can cause fleets to fail, preventing players from connecting to instances in the fleet.
        We recommend you replace fleets before 13 months, consider using fleet aliases for a smooth transition.

        :default: TLS/SSL certificate are generated for the fleet

        :stability: experimental
        '''
        result = self._values.get("use_certificate")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def use_spot(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Indicates whether to use On-Demand or Spot instances for this fleet. By default, fleet use on demand capacity.

        This property cannot be changed after the fleet is created.

        :default: Gamelift fleet use on demand capacity

        :see: https://docs.aws.amazon.com/gamelift/latest/developerguide/gamelift-ec2-instances.html#gamelift-ec2-instances-spot
        :stability: experimental
        '''
        result = self._values.get("use_spot")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def content(self) -> IBuild:
        '''(experimental) A build to be deployed on the fleet.

        The build must have been successfully uploaded to Amazon GameLift and be in a ``READY`` status.

        This fleet setting cannot be changed once the fleet is created.

        :stability: experimental
        '''
        result = self._values.get("content")
        assert result is not None, "Required property 'content' is missing"
        return typing.cast(IBuild, result)

    @builtins.property
    def ingress_rules(self) -> typing.Optional[typing.List[IngressRule]]:
        '''(experimental) The allowed IP address ranges and port settings that allow inbound traffic to access game sessions on this fleet.

        This property must be set before players can connect to game sessions.

        :default: no inbound traffic allowed

        :stability: experimental
        '''
        result = self._values.get("ingress_rules")
        return typing.cast(typing.Optional[typing.List[IngressRule]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "BuildFleetProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.implements(IGameServerGroup)
class GameServerGroupBase(
    _aws_cdk_ceddda9d.Resource,
    metaclass=jsii.JSIIAbstractClass,
    jsii_type="@aws-cdk/aws-gamelift-alpha.GameServerGroupBase",
):
    '''(experimental) Base class for new and imported GameLift FleetIQ game server group.

    :stability: experimental
    '''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        account: typing.Optional[builtins.str] = None,
        environment_from_arn: typing.Optional[builtins.str] = None,
        physical_name: typing.Optional[builtins.str] = None,
        region: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param account: The AWS account ID this resource belongs to. Default: - the resource is in the same account as the stack it belongs to
        :param environment_from_arn: ARN to deduce region and account from. The ARN is parsed and the account and region are taken from the ARN. This should be used for imported resources. Cannot be supplied together with either ``account`` or ``region``. Default: - take environment from ``account``, ``region`` parameters, or use Stack environment.
        :param physical_name: The value passed in by users to the physical name prop of the resource. - ``undefined`` implies that a physical name will be allocated by CloudFormation during deployment. - a concrete value implies a specific physical name - ``PhysicalName.GENERATE_IF_NEEDED`` is a marker that indicates that a physical will only be generated by the CDK if it is needed for cross-environment references. Otherwise, it will be allocated by CloudFormation. Default: - The physical name will be allocated by CloudFormation at deployment time
        :param region: The AWS region this resource belongs to. Default: - the resource is in the same region as the stack it belongs to
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3cb709ea0cc9b504c842aa150aa921febee13c957d7cccc041271e52227d956c)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = _aws_cdk_ceddda9d.ResourceProps(
            account=account,
            environment_from_arn=environment_from_arn,
            physical_name=physical_name,
            region=region,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @jsii.member(jsii_name="grant")
    def grant(
        self,
        grantee: _aws_cdk_aws_iam_ceddda9d.IGrantable,
        *actions: builtins.str,
    ) -> _aws_cdk_aws_iam_ceddda9d.Grant:
        '''(experimental) Grant the ``grantee`` identity permissions to perform ``actions``.

        :param grantee: -
        :param actions: -

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__bc98cc9f235cc2aacfbddfe6a1a444c59cf0ef97ba228263887d747a1a1d29ce)
            check_type(argname="argument grantee", value=grantee, expected_type=type_hints["grantee"])
            check_type(argname="argument actions", value=actions, expected_type=typing.Tuple[type_hints["actions"], ...]) # pyright: ignore [reportGeneralTypeIssues]
        return typing.cast(_aws_cdk_aws_iam_ceddda9d.Grant, jsii.invoke(self, "grant", [grantee, *actions]))

    @jsii.member(jsii_name="metric")
    def metric(
        self,
        metric_name: builtins.str,
        *,
        account: typing.Optional[builtins.str] = None,
        color: typing.Optional[builtins.str] = None,
        dimensions_map: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        id: typing.Optional[builtins.str] = None,
        label: typing.Optional[builtins.str] = None,
        period: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        region: typing.Optional[builtins.str] = None,
        stack_account: typing.Optional[builtins.str] = None,
        stack_region: typing.Optional[builtins.str] = None,
        statistic: typing.Optional[builtins.str] = None,
        unit: typing.Optional[_aws_cdk_aws_cloudwatch_ceddda9d.Unit] = None,
        visible: typing.Optional[builtins.bool] = None,
    ) -> _aws_cdk_aws_cloudwatch_ceddda9d.Metric:
        '''(experimental) Return the given named metric for this fleet.

        :param metric_name: -
        :param account: Account which this metric comes from. Default: - Deployment account.
        :param color: The hex color code, prefixed with '#' (e.g. '#00ff00'), to use when this metric is rendered on a graph. The ``Color`` class has a set of standard colors that can be used here. Default: - Automatic color
        :param dimensions_map: Dimensions of the metric. Default: - No dimensions.
        :param id: Unique identifier for this metric when used in dashboard widgets. The id can be used as a variable to represent this metric in math expressions. Valid characters are letters, numbers, and underscore. The first character must be a lowercase letter. Default: - No ID
        :param label: Label for this metric when added to a Graph in a Dashboard. You can use `dynamic labels <https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/graph-dynamic-labels.html>`_ to show summary information about the entire displayed time series in the legend. For example, if you use:: [max: ${MAX}] MyMetric As the metric label, the maximum value in the visible range will be shown next to the time series name in the graph's legend. Default: - No label
        :param period: The period over which the specified statistic is applied. Default: Duration.minutes(5)
        :param region: Region which this metric comes from. Default: - Deployment region.
        :param stack_account: Account of the stack this metric is attached to. Default: - Deployment account.
        :param stack_region: Region of the stack this metric is attached to. Default: - Deployment region.
        :param statistic: What function to use for aggregating. Use the ``aws_cloudwatch.Stats`` helper class to construct valid input strings. Can be one of the following: - "Minimum" | "min" - "Maximum" | "max" - "Average" | "avg" - "Sum" | "sum" - "SampleCount | "n" - "pNN.NN" - "tmNN.NN" | "tm(NN.NN%:NN.NN%)" - "iqm" - "wmNN.NN" | "wm(NN.NN%:NN.NN%)" - "tcNN.NN" | "tc(NN.NN%:NN.NN%)" - "tsNN.NN" | "ts(NN.NN%:NN.NN%)" Default: Average
        :param unit: Unit used to filter the metric stream. Only refer to datums emitted to the metric stream with the given unit and ignore all others. Only useful when datums are being emitted to the same metric stream under different units. The default is to use all matric datums in the stream, regardless of unit, which is recommended in nearly all cases. CloudWatch does not honor this property for graphs. Default: - All metric datums in the given metric stream
        :param visible: Whether this metric should be visible in dashboard graphs. Setting this to false is useful when you want to hide raw metrics that are used in math expressions, and show only the expression results. Default: true

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2d0af285f84a831b602a9af9d540b20e6d43d46920911983823552dac38c7558)
            check_type(argname="argument metric_name", value=metric_name, expected_type=type_hints["metric_name"])
        props = _aws_cdk_aws_cloudwatch_ceddda9d.MetricOptions(
            account=account,
            color=color,
            dimensions_map=dimensions_map,
            id=id,
            label=label,
            period=period,
            region=region,
            stack_account=stack_account,
            stack_region=stack_region,
            statistic=statistic,
            unit=unit,
            visible=visible,
        )

        return typing.cast(_aws_cdk_aws_cloudwatch_ceddda9d.Metric, jsii.invoke(self, "metric", [metric_name, props]))

    @builtins.property
    @jsii.member(jsii_name="autoScalingGroupArn")
    @abc.abstractmethod
    def auto_scaling_group_arn(self) -> builtins.str:
        '''(experimental) The ARN of the generated AutoScaling group.

        :stability: experimental
        '''
        ...

    @builtins.property
    @jsii.member(jsii_name="gameServerGroupArn")
    @abc.abstractmethod
    def game_server_group_arn(self) -> builtins.str:
        '''(experimental) The ARN of the game server group.

        :stability: experimental
        '''
        ...

    @builtins.property
    @jsii.member(jsii_name="gameServerGroupName")
    @abc.abstractmethod
    def game_server_group_name(self) -> builtins.str:
        '''(experimental) The name of the game server group.

        :stability: experimental
        '''
        ...

    @builtins.property
    @jsii.member(jsii_name="grantPrincipal")
    @abc.abstractmethod
    def grant_principal(self) -> _aws_cdk_aws_iam_ceddda9d.IPrincipal:
        '''(experimental) The principal this GameLift game server group is using.

        :stability: experimental
        '''
        ...


class _GameServerGroupBaseProxy(
    GameServerGroupBase,
    jsii.proxy_for(_aws_cdk_ceddda9d.Resource), # type: ignore[misc]
):
    @builtins.property
    @jsii.member(jsii_name="autoScalingGroupArn")
    def auto_scaling_group_arn(self) -> builtins.str:
        '''(experimental) The ARN of the generated AutoScaling group.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "autoScalingGroupArn"))

    @builtins.property
    @jsii.member(jsii_name="gameServerGroupArn")
    def game_server_group_arn(self) -> builtins.str:
        '''(experimental) The ARN of the game server group.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "gameServerGroupArn"))

    @builtins.property
    @jsii.member(jsii_name="gameServerGroupName")
    def game_server_group_name(self) -> builtins.str:
        '''(experimental) The name of the game server group.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "gameServerGroupName"))

    @builtins.property
    @jsii.member(jsii_name="grantPrincipal")
    def grant_principal(self) -> _aws_cdk_aws_iam_ceddda9d.IPrincipal:
        '''(experimental) The principal this GameLift game server group is using.

        :stability: experimental
        '''
        return typing.cast(_aws_cdk_aws_iam_ceddda9d.IPrincipal, jsii.get(self, "grantPrincipal"))

# Adding a "__jsii_proxy_class__(): typing.Type" function to the abstract class
typing.cast(typing.Any, GameServerGroupBase).__jsii_proxy_class__ = lambda : _GameServerGroupBaseProxy


@jsii.implements(IGameSessionQueue)
class GameSessionQueueBase(
    _aws_cdk_ceddda9d.Resource,
    metaclass=jsii.JSIIAbstractClass,
    jsii_type="@aws-cdk/aws-gamelift-alpha.GameSessionQueueBase",
):
    '''(experimental) Base class for new and imported GameLift GameSessionQueue.

    :stability: experimental
    '''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        account: typing.Optional[builtins.str] = None,
        environment_from_arn: typing.Optional[builtins.str] = None,
        physical_name: typing.Optional[builtins.str] = None,
        region: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param account: The AWS account ID this resource belongs to. Default: - the resource is in the same account as the stack it belongs to
        :param environment_from_arn: ARN to deduce region and account from. The ARN is parsed and the account and region are taken from the ARN. This should be used for imported resources. Cannot be supplied together with either ``account`` or ``region``. Default: - take environment from ``account``, ``region`` parameters, or use Stack environment.
        :param physical_name: The value passed in by users to the physical name prop of the resource. - ``undefined`` implies that a physical name will be allocated by CloudFormation during deployment. - a concrete value implies a specific physical name - ``PhysicalName.GENERATE_IF_NEEDED`` is a marker that indicates that a physical will only be generated by the CDK if it is needed for cross-environment references. Otherwise, it will be allocated by CloudFormation. Default: - The physical name will be allocated by CloudFormation at deployment time
        :param region: The AWS region this resource belongs to. Default: - the resource is in the same region as the stack it belongs to
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b4fac722db9ba55ff9ab2e7398f85630f80ba65dd3178e24f53fa3a7f6d95e69)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = _aws_cdk_ceddda9d.ResourceProps(
            account=account,
            environment_from_arn=environment_from_arn,
            physical_name=physical_name,
            region=region,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @jsii.member(jsii_name="metric")
    def metric(
        self,
        metric_name: builtins.str,
        *,
        account: typing.Optional[builtins.str] = None,
        color: typing.Optional[builtins.str] = None,
        dimensions_map: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        id: typing.Optional[builtins.str] = None,
        label: typing.Optional[builtins.str] = None,
        period: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        region: typing.Optional[builtins.str] = None,
        stack_account: typing.Optional[builtins.str] = None,
        stack_region: typing.Optional[builtins.str] = None,
        statistic: typing.Optional[builtins.str] = None,
        unit: typing.Optional[_aws_cdk_aws_cloudwatch_ceddda9d.Unit] = None,
        visible: typing.Optional[builtins.bool] = None,
    ) -> _aws_cdk_aws_cloudwatch_ceddda9d.Metric:
        '''(experimental) Return the given named metric for this fleet.

        :param metric_name: -
        :param account: Account which this metric comes from. Default: - Deployment account.
        :param color: The hex color code, prefixed with '#' (e.g. '#00ff00'), to use when this metric is rendered on a graph. The ``Color`` class has a set of standard colors that can be used here. Default: - Automatic color
        :param dimensions_map: Dimensions of the metric. Default: - No dimensions.
        :param id: Unique identifier for this metric when used in dashboard widgets. The id can be used as a variable to represent this metric in math expressions. Valid characters are letters, numbers, and underscore. The first character must be a lowercase letter. Default: - No ID
        :param label: Label for this metric when added to a Graph in a Dashboard. You can use `dynamic labels <https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/graph-dynamic-labels.html>`_ to show summary information about the entire displayed time series in the legend. For example, if you use:: [max: ${MAX}] MyMetric As the metric label, the maximum value in the visible range will be shown next to the time series name in the graph's legend. Default: - No label
        :param period: The period over which the specified statistic is applied. Default: Duration.minutes(5)
        :param region: Region which this metric comes from. Default: - Deployment region.
        :param stack_account: Account of the stack this metric is attached to. Default: - Deployment account.
        :param stack_region: Region of the stack this metric is attached to. Default: - Deployment region.
        :param statistic: What function to use for aggregating. Use the ``aws_cloudwatch.Stats`` helper class to construct valid input strings. Can be one of the following: - "Minimum" | "min" - "Maximum" | "max" - "Average" | "avg" - "Sum" | "sum" - "SampleCount | "n" - "pNN.NN" - "tmNN.NN" | "tm(NN.NN%:NN.NN%)" - "iqm" - "wmNN.NN" | "wm(NN.NN%:NN.NN%)" - "tcNN.NN" | "tc(NN.NN%:NN.NN%)" - "tsNN.NN" | "ts(NN.NN%:NN.NN%)" Default: Average
        :param unit: Unit used to filter the metric stream. Only refer to datums emitted to the metric stream with the given unit and ignore all others. Only useful when datums are being emitted to the same metric stream under different units. The default is to use all matric datums in the stream, regardless of unit, which is recommended in nearly all cases. CloudWatch does not honor this property for graphs. Default: - All metric datums in the given metric stream
        :param visible: Whether this metric should be visible in dashboard graphs. Setting this to false is useful when you want to hide raw metrics that are used in math expressions, and show only the expression results. Default: true

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__071d438e20836fe1d308788f6e0d2a6b79508aa39024c699dea4722f8a2de060)
            check_type(argname="argument metric_name", value=metric_name, expected_type=type_hints["metric_name"])
        props = _aws_cdk_aws_cloudwatch_ceddda9d.MetricOptions(
            account=account,
            color=color,
            dimensions_map=dimensions_map,
            id=id,
            label=label,
            period=period,
            region=region,
            stack_account=stack_account,
            stack_region=stack_region,
            statistic=statistic,
            unit=unit,
            visible=visible,
        )

        return typing.cast(_aws_cdk_aws_cloudwatch_ceddda9d.Metric, jsii.invoke(self, "metric", [metric_name, props]))

    @jsii.member(jsii_name="metricAverageWaitTime")
    def metric_average_wait_time(
        self,
        *,
        account: typing.Optional[builtins.str] = None,
        color: typing.Optional[builtins.str] = None,
        dimensions_map: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        id: typing.Optional[builtins.str] = None,
        label: typing.Optional[builtins.str] = None,
        period: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        region: typing.Optional[builtins.str] = None,
        stack_account: typing.Optional[builtins.str] = None,
        stack_region: typing.Optional[builtins.str] = None,
        statistic: typing.Optional[builtins.str] = None,
        unit: typing.Optional[_aws_cdk_aws_cloudwatch_ceddda9d.Unit] = None,
        visible: typing.Optional[builtins.bool] = None,
    ) -> _aws_cdk_aws_cloudwatch_ceddda9d.Metric:
        '''(experimental) Average amount of time that game session placement requests in the queue with status PENDING have been waiting to be fulfilled.

        :param account: Account which this metric comes from. Default: - Deployment account.
        :param color: The hex color code, prefixed with '#' (e.g. '#00ff00'), to use when this metric is rendered on a graph. The ``Color`` class has a set of standard colors that can be used here. Default: - Automatic color
        :param dimensions_map: Dimensions of the metric. Default: - No dimensions.
        :param id: Unique identifier for this metric when used in dashboard widgets. The id can be used as a variable to represent this metric in math expressions. Valid characters are letters, numbers, and underscore. The first character must be a lowercase letter. Default: - No ID
        :param label: Label for this metric when added to a Graph in a Dashboard. You can use `dynamic labels <https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/graph-dynamic-labels.html>`_ to show summary information about the entire displayed time series in the legend. For example, if you use:: [max: ${MAX}] MyMetric As the metric label, the maximum value in the visible range will be shown next to the time series name in the graph's legend. Default: - No label
        :param period: The period over which the specified statistic is applied. Default: Duration.minutes(5)
        :param region: Region which this metric comes from. Default: - Deployment region.
        :param stack_account: Account of the stack this metric is attached to. Default: - Deployment account.
        :param stack_region: Region of the stack this metric is attached to. Default: - Deployment region.
        :param statistic: What function to use for aggregating. Use the ``aws_cloudwatch.Stats`` helper class to construct valid input strings. Can be one of the following: - "Minimum" | "min" - "Maximum" | "max" - "Average" | "avg" - "Sum" | "sum" - "SampleCount | "n" - "pNN.NN" - "tmNN.NN" | "tm(NN.NN%:NN.NN%)" - "iqm" - "wmNN.NN" | "wm(NN.NN%:NN.NN%)" - "tcNN.NN" | "tc(NN.NN%:NN.NN%)" - "tsNN.NN" | "ts(NN.NN%:NN.NN%)" Default: Average
        :param unit: Unit used to filter the metric stream. Only refer to datums emitted to the metric stream with the given unit and ignore all others. Only useful when datums are being emitted to the same metric stream under different units. The default is to use all matric datums in the stream, regardless of unit, which is recommended in nearly all cases. CloudWatch does not honor this property for graphs. Default: - All metric datums in the given metric stream
        :param visible: Whether this metric should be visible in dashboard graphs. Setting this to false is useful when you want to hide raw metrics that are used in math expressions, and show only the expression results. Default: true

        :stability: experimental
        '''
        props = _aws_cdk_aws_cloudwatch_ceddda9d.MetricOptions(
            account=account,
            color=color,
            dimensions_map=dimensions_map,
            id=id,
            label=label,
            period=period,
            region=region,
            stack_account=stack_account,
            stack_region=stack_region,
            statistic=statistic,
            unit=unit,
            visible=visible,
        )

        return typing.cast(_aws_cdk_aws_cloudwatch_ceddda9d.Metric, jsii.invoke(self, "metricAverageWaitTime", [props]))

    @jsii.member(jsii_name="metricPlacementsCanceled")
    def metric_placements_canceled(
        self,
        *,
        account: typing.Optional[builtins.str] = None,
        color: typing.Optional[builtins.str] = None,
        dimensions_map: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        id: typing.Optional[builtins.str] = None,
        label: typing.Optional[builtins.str] = None,
        period: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        region: typing.Optional[builtins.str] = None,
        stack_account: typing.Optional[builtins.str] = None,
        stack_region: typing.Optional[builtins.str] = None,
        statistic: typing.Optional[builtins.str] = None,
        unit: typing.Optional[_aws_cdk_aws_cloudwatch_ceddda9d.Unit] = None,
        visible: typing.Optional[builtins.bool] = None,
    ) -> _aws_cdk_aws_cloudwatch_ceddda9d.Metric:
        '''(experimental) Game session placement requests that were canceled before timing out since the last report.

        :param account: Account which this metric comes from. Default: - Deployment account.
        :param color: The hex color code, prefixed with '#' (e.g. '#00ff00'), to use when this metric is rendered on a graph. The ``Color`` class has a set of standard colors that can be used here. Default: - Automatic color
        :param dimensions_map: Dimensions of the metric. Default: - No dimensions.
        :param id: Unique identifier for this metric when used in dashboard widgets. The id can be used as a variable to represent this metric in math expressions. Valid characters are letters, numbers, and underscore. The first character must be a lowercase letter. Default: - No ID
        :param label: Label for this metric when added to a Graph in a Dashboard. You can use `dynamic labels <https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/graph-dynamic-labels.html>`_ to show summary information about the entire displayed time series in the legend. For example, if you use:: [max: ${MAX}] MyMetric As the metric label, the maximum value in the visible range will be shown next to the time series name in the graph's legend. Default: - No label
        :param period: The period over which the specified statistic is applied. Default: Duration.minutes(5)
        :param region: Region which this metric comes from. Default: - Deployment region.
        :param stack_account: Account of the stack this metric is attached to. Default: - Deployment account.
        :param stack_region: Region of the stack this metric is attached to. Default: - Deployment region.
        :param statistic: What function to use for aggregating. Use the ``aws_cloudwatch.Stats`` helper class to construct valid input strings. Can be one of the following: - "Minimum" | "min" - "Maximum" | "max" - "Average" | "avg" - "Sum" | "sum" - "SampleCount | "n" - "pNN.NN" - "tmNN.NN" | "tm(NN.NN%:NN.NN%)" - "iqm" - "wmNN.NN" | "wm(NN.NN%:NN.NN%)" - "tcNN.NN" | "tc(NN.NN%:NN.NN%)" - "tsNN.NN" | "ts(NN.NN%:NN.NN%)" Default: Average
        :param unit: Unit used to filter the metric stream. Only refer to datums emitted to the metric stream with the given unit and ignore all others. Only useful when datums are being emitted to the same metric stream under different units. The default is to use all matric datums in the stream, regardless of unit, which is recommended in nearly all cases. CloudWatch does not honor this property for graphs. Default: - All metric datums in the given metric stream
        :param visible: Whether this metric should be visible in dashboard graphs. Setting this to false is useful when you want to hide raw metrics that are used in math expressions, and show only the expression results. Default: true

        :stability: experimental
        '''
        props = _aws_cdk_aws_cloudwatch_ceddda9d.MetricOptions(
            account=account,
            color=color,
            dimensions_map=dimensions_map,
            id=id,
            label=label,
            period=period,
            region=region,
            stack_account=stack_account,
            stack_region=stack_region,
            statistic=statistic,
            unit=unit,
            visible=visible,
        )

        return typing.cast(_aws_cdk_aws_cloudwatch_ceddda9d.Metric, jsii.invoke(self, "metricPlacementsCanceled", [props]))

    @jsii.member(jsii_name="metricPlacementsFailed")
    def metric_placements_failed(
        self,
        *,
        account: typing.Optional[builtins.str] = None,
        color: typing.Optional[builtins.str] = None,
        dimensions_map: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        id: typing.Optional[builtins.str] = None,
        label: typing.Optional[builtins.str] = None,
        period: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        region: typing.Optional[builtins.str] = None,
        stack_account: typing.Optional[builtins.str] = None,
        stack_region: typing.Optional[builtins.str] = None,
        statistic: typing.Optional[builtins.str] = None,
        unit: typing.Optional[_aws_cdk_aws_cloudwatch_ceddda9d.Unit] = None,
        visible: typing.Optional[builtins.bool] = None,
    ) -> _aws_cdk_aws_cloudwatch_ceddda9d.Metric:
        '''(experimental) Game session placement requests that failed for any reason since the last report.

        :param account: Account which this metric comes from. Default: - Deployment account.
        :param color: The hex color code, prefixed with '#' (e.g. '#00ff00'), to use when this metric is rendered on a graph. The ``Color`` class has a set of standard colors that can be used here. Default: - Automatic color
        :param dimensions_map: Dimensions of the metric. Default: - No dimensions.
        :param id: Unique identifier for this metric when used in dashboard widgets. The id can be used as a variable to represent this metric in math expressions. Valid characters are letters, numbers, and underscore. The first character must be a lowercase letter. Default: - No ID
        :param label: Label for this metric when added to a Graph in a Dashboard. You can use `dynamic labels <https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/graph-dynamic-labels.html>`_ to show summary information about the entire displayed time series in the legend. For example, if you use:: [max: ${MAX}] MyMetric As the metric label, the maximum value in the visible range will be shown next to the time series name in the graph's legend. Default: - No label
        :param period: The period over which the specified statistic is applied. Default: Duration.minutes(5)
        :param region: Region which this metric comes from. Default: - Deployment region.
        :param stack_account: Account of the stack this metric is attached to. Default: - Deployment account.
        :param stack_region: Region of the stack this metric is attached to. Default: - Deployment region.
        :param statistic: What function to use for aggregating. Use the ``aws_cloudwatch.Stats`` helper class to construct valid input strings. Can be one of the following: - "Minimum" | "min" - "Maximum" | "max" - "Average" | "avg" - "Sum" | "sum" - "SampleCount | "n" - "pNN.NN" - "tmNN.NN" | "tm(NN.NN%:NN.NN%)" - "iqm" - "wmNN.NN" | "wm(NN.NN%:NN.NN%)" - "tcNN.NN" | "tc(NN.NN%:NN.NN%)" - "tsNN.NN" | "ts(NN.NN%:NN.NN%)" Default: Average
        :param unit: Unit used to filter the metric stream. Only refer to datums emitted to the metric stream with the given unit and ignore all others. Only useful when datums are being emitted to the same metric stream under different units. The default is to use all matric datums in the stream, regardless of unit, which is recommended in nearly all cases. CloudWatch does not honor this property for graphs. Default: - All metric datums in the given metric stream
        :param visible: Whether this metric should be visible in dashboard graphs. Setting this to false is useful when you want to hide raw metrics that are used in math expressions, and show only the expression results. Default: true

        :stability: experimental
        '''
        props = _aws_cdk_aws_cloudwatch_ceddda9d.MetricOptions(
            account=account,
            color=color,
            dimensions_map=dimensions_map,
            id=id,
            label=label,
            period=period,
            region=region,
            stack_account=stack_account,
            stack_region=stack_region,
            statistic=statistic,
            unit=unit,
            visible=visible,
        )

        return typing.cast(_aws_cdk_aws_cloudwatch_ceddda9d.Metric, jsii.invoke(self, "metricPlacementsFailed", [props]))

    @jsii.member(jsii_name="metricPlacementsStarted")
    def metric_placements_started(
        self,
        *,
        account: typing.Optional[builtins.str] = None,
        color: typing.Optional[builtins.str] = None,
        dimensions_map: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        id: typing.Optional[builtins.str] = None,
        label: typing.Optional[builtins.str] = None,
        period: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        region: typing.Optional[builtins.str] = None,
        stack_account: typing.Optional[builtins.str] = None,
        stack_region: typing.Optional[builtins.str] = None,
        statistic: typing.Optional[builtins.str] = None,
        unit: typing.Optional[_aws_cdk_aws_cloudwatch_ceddda9d.Unit] = None,
        visible: typing.Optional[builtins.bool] = None,
    ) -> _aws_cdk_aws_cloudwatch_ceddda9d.Metric:
        '''(experimental) New game session placement requests that were added to the queue since the last report.

        :param account: Account which this metric comes from. Default: - Deployment account.
        :param color: The hex color code, prefixed with '#' (e.g. '#00ff00'), to use when this metric is rendered on a graph. The ``Color`` class has a set of standard colors that can be used here. Default: - Automatic color
        :param dimensions_map: Dimensions of the metric. Default: - No dimensions.
        :param id: Unique identifier for this metric when used in dashboard widgets. The id can be used as a variable to represent this metric in math expressions. Valid characters are letters, numbers, and underscore. The first character must be a lowercase letter. Default: - No ID
        :param label: Label for this metric when added to a Graph in a Dashboard. You can use `dynamic labels <https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/graph-dynamic-labels.html>`_ to show summary information about the entire displayed time series in the legend. For example, if you use:: [max: ${MAX}] MyMetric As the metric label, the maximum value in the visible range will be shown next to the time series name in the graph's legend. Default: - No label
        :param period: The period over which the specified statistic is applied. Default: Duration.minutes(5)
        :param region: Region which this metric comes from. Default: - Deployment region.
        :param stack_account: Account of the stack this metric is attached to. Default: - Deployment account.
        :param stack_region: Region of the stack this metric is attached to. Default: - Deployment region.
        :param statistic: What function to use for aggregating. Use the ``aws_cloudwatch.Stats`` helper class to construct valid input strings. Can be one of the following: - "Minimum" | "min" - "Maximum" | "max" - "Average" | "avg" - "Sum" | "sum" - "SampleCount | "n" - "pNN.NN" - "tmNN.NN" | "tm(NN.NN%:NN.NN%)" - "iqm" - "wmNN.NN" | "wm(NN.NN%:NN.NN%)" - "tcNN.NN" | "tc(NN.NN%:NN.NN%)" - "tsNN.NN" | "ts(NN.NN%:NN.NN%)" Default: Average
        :param unit: Unit used to filter the metric stream. Only refer to datums emitted to the metric stream with the given unit and ignore all others. Only useful when datums are being emitted to the same metric stream under different units. The default is to use all matric datums in the stream, regardless of unit, which is recommended in nearly all cases. CloudWatch does not honor this property for graphs. Default: - All metric datums in the given metric stream
        :param visible: Whether this metric should be visible in dashboard graphs. Setting this to false is useful when you want to hide raw metrics that are used in math expressions, and show only the expression results. Default: true

        :stability: experimental
        '''
        props = _aws_cdk_aws_cloudwatch_ceddda9d.MetricOptions(
            account=account,
            color=color,
            dimensions_map=dimensions_map,
            id=id,
            label=label,
            period=period,
            region=region,
            stack_account=stack_account,
            stack_region=stack_region,
            statistic=statistic,
            unit=unit,
            visible=visible,
        )

        return typing.cast(_aws_cdk_aws_cloudwatch_ceddda9d.Metric, jsii.invoke(self, "metricPlacementsStarted", [props]))

    @jsii.member(jsii_name="metricPlacementsSucceeded")
    def metric_placements_succeeded(
        self,
        *,
        account: typing.Optional[builtins.str] = None,
        color: typing.Optional[builtins.str] = None,
        dimensions_map: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        id: typing.Optional[builtins.str] = None,
        label: typing.Optional[builtins.str] = None,
        period: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        region: typing.Optional[builtins.str] = None,
        stack_account: typing.Optional[builtins.str] = None,
        stack_region: typing.Optional[builtins.str] = None,
        statistic: typing.Optional[builtins.str] = None,
        unit: typing.Optional[_aws_cdk_aws_cloudwatch_ceddda9d.Unit] = None,
        visible: typing.Optional[builtins.bool] = None,
    ) -> _aws_cdk_aws_cloudwatch_ceddda9d.Metric:
        '''(experimental) Game session placement requests that resulted in a new game session since the last report.

        :param account: Account which this metric comes from. Default: - Deployment account.
        :param color: The hex color code, prefixed with '#' (e.g. '#00ff00'), to use when this metric is rendered on a graph. The ``Color`` class has a set of standard colors that can be used here. Default: - Automatic color
        :param dimensions_map: Dimensions of the metric. Default: - No dimensions.
        :param id: Unique identifier for this metric when used in dashboard widgets. The id can be used as a variable to represent this metric in math expressions. Valid characters are letters, numbers, and underscore. The first character must be a lowercase letter. Default: - No ID
        :param label: Label for this metric when added to a Graph in a Dashboard. You can use `dynamic labels <https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/graph-dynamic-labels.html>`_ to show summary information about the entire displayed time series in the legend. For example, if you use:: [max: ${MAX}] MyMetric As the metric label, the maximum value in the visible range will be shown next to the time series name in the graph's legend. Default: - No label
        :param period: The period over which the specified statistic is applied. Default: Duration.minutes(5)
        :param region: Region which this metric comes from. Default: - Deployment region.
        :param stack_account: Account of the stack this metric is attached to. Default: - Deployment account.
        :param stack_region: Region of the stack this metric is attached to. Default: - Deployment region.
        :param statistic: What function to use for aggregating. Use the ``aws_cloudwatch.Stats`` helper class to construct valid input strings. Can be one of the following: - "Minimum" | "min" - "Maximum" | "max" - "Average" | "avg" - "Sum" | "sum" - "SampleCount | "n" - "pNN.NN" - "tmNN.NN" | "tm(NN.NN%:NN.NN%)" - "iqm" - "wmNN.NN" | "wm(NN.NN%:NN.NN%)" - "tcNN.NN" | "tc(NN.NN%:NN.NN%)" - "tsNN.NN" | "ts(NN.NN%:NN.NN%)" Default: Average
        :param unit: Unit used to filter the metric stream. Only refer to datums emitted to the metric stream with the given unit and ignore all others. Only useful when datums are being emitted to the same metric stream under different units. The default is to use all matric datums in the stream, regardless of unit, which is recommended in nearly all cases. CloudWatch does not honor this property for graphs. Default: - All metric datums in the given metric stream
        :param visible: Whether this metric should be visible in dashboard graphs. Setting this to false is useful when you want to hide raw metrics that are used in math expressions, and show only the expression results. Default: true

        :stability: experimental
        '''
        props = _aws_cdk_aws_cloudwatch_ceddda9d.MetricOptions(
            account=account,
            color=color,
            dimensions_map=dimensions_map,
            id=id,
            label=label,
            period=period,
            region=region,
            stack_account=stack_account,
            stack_region=stack_region,
            statistic=statistic,
            unit=unit,
            visible=visible,
        )

        return typing.cast(_aws_cdk_aws_cloudwatch_ceddda9d.Metric, jsii.invoke(self, "metricPlacementsSucceeded", [props]))

    @jsii.member(jsii_name="metricPlacementsTimedOut")
    def metric_placements_timed_out(
        self,
        *,
        account: typing.Optional[builtins.str] = None,
        color: typing.Optional[builtins.str] = None,
        dimensions_map: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        id: typing.Optional[builtins.str] = None,
        label: typing.Optional[builtins.str] = None,
        period: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        region: typing.Optional[builtins.str] = None,
        stack_account: typing.Optional[builtins.str] = None,
        stack_region: typing.Optional[builtins.str] = None,
        statistic: typing.Optional[builtins.str] = None,
        unit: typing.Optional[_aws_cdk_aws_cloudwatch_ceddda9d.Unit] = None,
        visible: typing.Optional[builtins.bool] = None,
    ) -> _aws_cdk_aws_cloudwatch_ceddda9d.Metric:
        '''(experimental) Game session placement requests that reached the queue's timeout limit without being fulfilled since the last report.

        :param account: Account which this metric comes from. Default: - Deployment account.
        :param color: The hex color code, prefixed with '#' (e.g. '#00ff00'), to use when this metric is rendered on a graph. The ``Color`` class has a set of standard colors that can be used here. Default: - Automatic color
        :param dimensions_map: Dimensions of the metric. Default: - No dimensions.
        :param id: Unique identifier for this metric when used in dashboard widgets. The id can be used as a variable to represent this metric in math expressions. Valid characters are letters, numbers, and underscore. The first character must be a lowercase letter. Default: - No ID
        :param label: Label for this metric when added to a Graph in a Dashboard. You can use `dynamic labels <https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/graph-dynamic-labels.html>`_ to show summary information about the entire displayed time series in the legend. For example, if you use:: [max: ${MAX}] MyMetric As the metric label, the maximum value in the visible range will be shown next to the time series name in the graph's legend. Default: - No label
        :param period: The period over which the specified statistic is applied. Default: Duration.minutes(5)
        :param region: Region which this metric comes from. Default: - Deployment region.
        :param stack_account: Account of the stack this metric is attached to. Default: - Deployment account.
        :param stack_region: Region of the stack this metric is attached to. Default: - Deployment region.
        :param statistic: What function to use for aggregating. Use the ``aws_cloudwatch.Stats`` helper class to construct valid input strings. Can be one of the following: - "Minimum" | "min" - "Maximum" | "max" - "Average" | "avg" - "Sum" | "sum" - "SampleCount | "n" - "pNN.NN" - "tmNN.NN" | "tm(NN.NN%:NN.NN%)" - "iqm" - "wmNN.NN" | "wm(NN.NN%:NN.NN%)" - "tcNN.NN" | "tc(NN.NN%:NN.NN%)" - "tsNN.NN" | "ts(NN.NN%:NN.NN%)" Default: Average
        :param unit: Unit used to filter the metric stream. Only refer to datums emitted to the metric stream with the given unit and ignore all others. Only useful when datums are being emitted to the same metric stream under different units. The default is to use all matric datums in the stream, regardless of unit, which is recommended in nearly all cases. CloudWatch does not honor this property for graphs. Default: - All metric datums in the given metric stream
        :param visible: Whether this metric should be visible in dashboard graphs. Setting this to false is useful when you want to hide raw metrics that are used in math expressions, and show only the expression results. Default: true

        :stability: experimental
        '''
        props = _aws_cdk_aws_cloudwatch_ceddda9d.MetricOptions(
            account=account,
            color=color,
            dimensions_map=dimensions_map,
            id=id,
            label=label,
            period=period,
            region=region,
            stack_account=stack_account,
            stack_region=stack_region,
            statistic=statistic,
            unit=unit,
            visible=visible,
        )

        return typing.cast(_aws_cdk_aws_cloudwatch_ceddda9d.Metric, jsii.invoke(self, "metricPlacementsTimedOut", [props]))

    @builtins.property
    @jsii.member(jsii_name="gameSessionQueueArn")
    @abc.abstractmethod
    def game_session_queue_arn(self) -> builtins.str:
        '''(experimental) The ARN of the gameSessionQueue.

        :stability: experimental
        '''
        ...

    @builtins.property
    @jsii.member(jsii_name="gameSessionQueueName")
    @abc.abstractmethod
    def game_session_queue_name(self) -> builtins.str:
        '''(experimental) The name of the gameSessionQueue.

        :stability: experimental
        '''
        ...


class _GameSessionQueueBaseProxy(
    GameSessionQueueBase,
    jsii.proxy_for(_aws_cdk_ceddda9d.Resource), # type: ignore[misc]
):
    @builtins.property
    @jsii.member(jsii_name="gameSessionQueueArn")
    def game_session_queue_arn(self) -> builtins.str:
        '''(experimental) The ARN of the gameSessionQueue.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "gameSessionQueueArn"))

    @builtins.property
    @jsii.member(jsii_name="gameSessionQueueName")
    def game_session_queue_name(self) -> builtins.str:
        '''(experimental) The name of the gameSessionQueue.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "gameSessionQueueName"))

# Adding a "__jsii_proxy_class__(): typing.Type" function to the abstract class
typing.cast(typing.Any, GameSessionQueueBase).__jsii_proxy_class__ = lambda : _GameSessionQueueBaseProxy


@jsii.interface(jsii_type="@aws-cdk/aws-gamelift-alpha.IAlias")
class IAlias(
    _aws_cdk_ceddda9d.IResource,
    IGameSessionQueueDestination,
    typing_extensions.Protocol,
):
    '''(experimental) Represents a Gamelift Alias for a Gamelift fleet destination.

    :stability: experimental
    '''

    @builtins.property
    @jsii.member(jsii_name="aliasArn")
    def alias_arn(self) -> builtins.str:
        '''(experimental) The ARN of the alias.

        :stability: experimental
        :attribute: true
        '''
        ...

    @builtins.property
    @jsii.member(jsii_name="aliasId")
    def alias_id(self) -> builtins.str:
        '''(experimental) The Identifier of the alias.

        :stability: experimental
        :attribute: true
        '''
        ...


class _IAliasProxy(
    jsii.proxy_for(_aws_cdk_ceddda9d.IResource), # type: ignore[misc]
    jsii.proxy_for(IGameSessionQueueDestination), # type: ignore[misc]
):
    '''(experimental) Represents a Gamelift Alias for a Gamelift fleet destination.

    :stability: experimental
    '''

    __jsii_type__: typing.ClassVar[str] = "@aws-cdk/aws-gamelift-alpha.IAlias"

    @builtins.property
    @jsii.member(jsii_name="aliasArn")
    def alias_arn(self) -> builtins.str:
        '''(experimental) The ARN of the alias.

        :stability: experimental
        :attribute: true
        '''
        return typing.cast(builtins.str, jsii.get(self, "aliasArn"))

    @builtins.property
    @jsii.member(jsii_name="aliasId")
    def alias_id(self) -> builtins.str:
        '''(experimental) The Identifier of the alias.

        :stability: experimental
        :attribute: true
        '''
        return typing.cast(builtins.str, jsii.get(self, "aliasId"))

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, IAlias).__jsii_proxy_class__ = lambda : _IAliasProxy


@jsii.interface(jsii_type="@aws-cdk/aws-gamelift-alpha.IFleet")
class IFleet(
    _aws_cdk_ceddda9d.IResource,
    _aws_cdk_aws_iam_ceddda9d.IGrantable,
    IGameSessionQueueDestination,
    typing_extensions.Protocol,
):
    '''(experimental) Represents a Gamelift fleet.

    :stability: experimental
    '''

    @builtins.property
    @jsii.member(jsii_name="fleetArn")
    def fleet_arn(self) -> builtins.str:
        '''(experimental) The ARN of the fleet.

        :stability: experimental
        :attribute: true
        '''
        ...

    @builtins.property
    @jsii.member(jsii_name="fleetId")
    def fleet_id(self) -> builtins.str:
        '''(experimental) The Identifier of the fleet.

        :stability: experimental
        :attribute: true
        '''
        ...

    @jsii.member(jsii_name="grant")
    def grant(
        self,
        grantee: _aws_cdk_aws_iam_ceddda9d.IGrantable,
        *actions: builtins.str,
    ) -> _aws_cdk_aws_iam_ceddda9d.Grant:
        '''(experimental) Grant the ``grantee`` identity permissions to perform ``actions``.

        :param grantee: -
        :param actions: -

        :stability: experimental
        '''
        ...

    @jsii.member(jsii_name="metric")
    def metric(
        self,
        metric_name: builtins.str,
        *,
        account: typing.Optional[builtins.str] = None,
        color: typing.Optional[builtins.str] = None,
        dimensions_map: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        id: typing.Optional[builtins.str] = None,
        label: typing.Optional[builtins.str] = None,
        period: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        region: typing.Optional[builtins.str] = None,
        stack_account: typing.Optional[builtins.str] = None,
        stack_region: typing.Optional[builtins.str] = None,
        statistic: typing.Optional[builtins.str] = None,
        unit: typing.Optional[_aws_cdk_aws_cloudwatch_ceddda9d.Unit] = None,
        visible: typing.Optional[builtins.bool] = None,
    ) -> _aws_cdk_aws_cloudwatch_ceddda9d.Metric:
        '''(experimental) Return the given named metric for this fleet.

        :param metric_name: -
        :param account: Account which this metric comes from. Default: - Deployment account.
        :param color: The hex color code, prefixed with '#' (e.g. '#00ff00'), to use when this metric is rendered on a graph. The ``Color`` class has a set of standard colors that can be used here. Default: - Automatic color
        :param dimensions_map: Dimensions of the metric. Default: - No dimensions.
        :param id: Unique identifier for this metric when used in dashboard widgets. The id can be used as a variable to represent this metric in math expressions. Valid characters are letters, numbers, and underscore. The first character must be a lowercase letter. Default: - No ID
        :param label: Label for this metric when added to a Graph in a Dashboard. You can use `dynamic labels <https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/graph-dynamic-labels.html>`_ to show summary information about the entire displayed time series in the legend. For example, if you use:: [max: ${MAX}] MyMetric As the metric label, the maximum value in the visible range will be shown next to the time series name in the graph's legend. Default: - No label
        :param period: The period over which the specified statistic is applied. Default: Duration.minutes(5)
        :param region: Region which this metric comes from. Default: - Deployment region.
        :param stack_account: Account of the stack this metric is attached to. Default: - Deployment account.
        :param stack_region: Region of the stack this metric is attached to. Default: - Deployment region.
        :param statistic: What function to use for aggregating. Use the ``aws_cloudwatch.Stats`` helper class to construct valid input strings. Can be one of the following: - "Minimum" | "min" - "Maximum" | "max" - "Average" | "avg" - "Sum" | "sum" - "SampleCount | "n" - "pNN.NN" - "tmNN.NN" | "tm(NN.NN%:NN.NN%)" - "iqm" - "wmNN.NN" | "wm(NN.NN%:NN.NN%)" - "tcNN.NN" | "tc(NN.NN%:NN.NN%)" - "tsNN.NN" | "ts(NN.NN%:NN.NN%)" Default: Average
        :param unit: Unit used to filter the metric stream. Only refer to datums emitted to the metric stream with the given unit and ignore all others. Only useful when datums are being emitted to the same metric stream under different units. The default is to use all matric datums in the stream, regardless of unit, which is recommended in nearly all cases. CloudWatch does not honor this property for graphs. Default: - All metric datums in the given metric stream
        :param visible: Whether this metric should be visible in dashboard graphs. Setting this to false is useful when you want to hide raw metrics that are used in math expressions, and show only the expression results. Default: true

        :stability: experimental
        '''
        ...

    @jsii.member(jsii_name="metricActiveInstances")
    def metric_active_instances(
        self,
        *,
        account: typing.Optional[builtins.str] = None,
        color: typing.Optional[builtins.str] = None,
        dimensions_map: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        id: typing.Optional[builtins.str] = None,
        label: typing.Optional[builtins.str] = None,
        period: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        region: typing.Optional[builtins.str] = None,
        stack_account: typing.Optional[builtins.str] = None,
        stack_region: typing.Optional[builtins.str] = None,
        statistic: typing.Optional[builtins.str] = None,
        unit: typing.Optional[_aws_cdk_aws_cloudwatch_ceddda9d.Unit] = None,
        visible: typing.Optional[builtins.bool] = None,
    ) -> _aws_cdk_aws_cloudwatch_ceddda9d.Metric:
        '''(experimental) Instances with ``ACTIVE`` status, which means they are running active server processes.

        The count includes idle instances and those that are hosting one or more game sessions.
        This metric measures current total instance capacity.

        This metric can be used with automatic scaling.

        :param account: Account which this metric comes from. Default: - Deployment account.
        :param color: The hex color code, prefixed with '#' (e.g. '#00ff00'), to use when this metric is rendered on a graph. The ``Color`` class has a set of standard colors that can be used here. Default: - Automatic color
        :param dimensions_map: Dimensions of the metric. Default: - No dimensions.
        :param id: Unique identifier for this metric when used in dashboard widgets. The id can be used as a variable to represent this metric in math expressions. Valid characters are letters, numbers, and underscore. The first character must be a lowercase letter. Default: - No ID
        :param label: Label for this metric when added to a Graph in a Dashboard. You can use `dynamic labels <https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/graph-dynamic-labels.html>`_ to show summary information about the entire displayed time series in the legend. For example, if you use:: [max: ${MAX}] MyMetric As the metric label, the maximum value in the visible range will be shown next to the time series name in the graph's legend. Default: - No label
        :param period: The period over which the specified statistic is applied. Default: Duration.minutes(5)
        :param region: Region which this metric comes from. Default: - Deployment region.
        :param stack_account: Account of the stack this metric is attached to. Default: - Deployment account.
        :param stack_region: Region of the stack this metric is attached to. Default: - Deployment region.
        :param statistic: What function to use for aggregating. Use the ``aws_cloudwatch.Stats`` helper class to construct valid input strings. Can be one of the following: - "Minimum" | "min" - "Maximum" | "max" - "Average" | "avg" - "Sum" | "sum" - "SampleCount | "n" - "pNN.NN" - "tmNN.NN" | "tm(NN.NN%:NN.NN%)" - "iqm" - "wmNN.NN" | "wm(NN.NN%:NN.NN%)" - "tcNN.NN" | "tc(NN.NN%:NN.NN%)" - "tsNN.NN" | "ts(NN.NN%:NN.NN%)" Default: Average
        :param unit: Unit used to filter the metric stream. Only refer to datums emitted to the metric stream with the given unit and ignore all others. Only useful when datums are being emitted to the same metric stream under different units. The default is to use all matric datums in the stream, regardless of unit, which is recommended in nearly all cases. CloudWatch does not honor this property for graphs. Default: - All metric datums in the given metric stream
        :param visible: Whether this metric should be visible in dashboard graphs. Setting this to false is useful when you want to hide raw metrics that are used in math expressions, and show only the expression results. Default: true

        :stability: experimental
        '''
        ...

    @jsii.member(jsii_name="metricDesiredInstances")
    def metric_desired_instances(
        self,
        *,
        account: typing.Optional[builtins.str] = None,
        color: typing.Optional[builtins.str] = None,
        dimensions_map: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        id: typing.Optional[builtins.str] = None,
        label: typing.Optional[builtins.str] = None,
        period: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        region: typing.Optional[builtins.str] = None,
        stack_account: typing.Optional[builtins.str] = None,
        stack_region: typing.Optional[builtins.str] = None,
        statistic: typing.Optional[builtins.str] = None,
        unit: typing.Optional[_aws_cdk_aws_cloudwatch_ceddda9d.Unit] = None,
        visible: typing.Optional[builtins.bool] = None,
    ) -> _aws_cdk_aws_cloudwatch_ceddda9d.Metric:
        '''(experimental) Target number of active instances that GameLift is working to maintain in the fleet.

        With automatic scaling, this value is determined based on the scaling policies currently in force.
        Without automatic scaling, this value is set manually.
        This metric is not available when viewing data for fleet metric groups.

        :param account: Account which this metric comes from. Default: - Deployment account.
        :param color: The hex color code, prefixed with '#' (e.g. '#00ff00'), to use when this metric is rendered on a graph. The ``Color`` class has a set of standard colors that can be used here. Default: - Automatic color
        :param dimensions_map: Dimensions of the metric. Default: - No dimensions.
        :param id: Unique identifier for this metric when used in dashboard widgets. The id can be used as a variable to represent this metric in math expressions. Valid characters are letters, numbers, and underscore. The first character must be a lowercase letter. Default: - No ID
        :param label: Label for this metric when added to a Graph in a Dashboard. You can use `dynamic labels <https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/graph-dynamic-labels.html>`_ to show summary information about the entire displayed time series in the legend. For example, if you use:: [max: ${MAX}] MyMetric As the metric label, the maximum value in the visible range will be shown next to the time series name in the graph's legend. Default: - No label
        :param period: The period over which the specified statistic is applied. Default: Duration.minutes(5)
        :param region: Region which this metric comes from. Default: - Deployment region.
        :param stack_account: Account of the stack this metric is attached to. Default: - Deployment account.
        :param stack_region: Region of the stack this metric is attached to. Default: - Deployment region.
        :param statistic: What function to use for aggregating. Use the ``aws_cloudwatch.Stats`` helper class to construct valid input strings. Can be one of the following: - "Minimum" | "min" - "Maximum" | "max" - "Average" | "avg" - "Sum" | "sum" - "SampleCount | "n" - "pNN.NN" - "tmNN.NN" | "tm(NN.NN%:NN.NN%)" - "iqm" - "wmNN.NN" | "wm(NN.NN%:NN.NN%)" - "tcNN.NN" | "tc(NN.NN%:NN.NN%)" - "tsNN.NN" | "ts(NN.NN%:NN.NN%)" Default: Average
        :param unit: Unit used to filter the metric stream. Only refer to datums emitted to the metric stream with the given unit and ignore all others. Only useful when datums are being emitted to the same metric stream under different units. The default is to use all matric datums in the stream, regardless of unit, which is recommended in nearly all cases. CloudWatch does not honor this property for graphs. Default: - All metric datums in the given metric stream
        :param visible: Whether this metric should be visible in dashboard graphs. Setting this to false is useful when you want to hide raw metrics that are used in math expressions, and show only the expression results. Default: true

        :stability: experimental
        '''
        ...

    @jsii.member(jsii_name="metricIdleInstances")
    def metric_idle_instances(
        self,
        *,
        account: typing.Optional[builtins.str] = None,
        color: typing.Optional[builtins.str] = None,
        dimensions_map: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        id: typing.Optional[builtins.str] = None,
        label: typing.Optional[builtins.str] = None,
        period: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        region: typing.Optional[builtins.str] = None,
        stack_account: typing.Optional[builtins.str] = None,
        stack_region: typing.Optional[builtins.str] = None,
        statistic: typing.Optional[builtins.str] = None,
        unit: typing.Optional[_aws_cdk_aws_cloudwatch_ceddda9d.Unit] = None,
        visible: typing.Optional[builtins.bool] = None,
    ) -> _aws_cdk_aws_cloudwatch_ceddda9d.Metric:
        '''(experimental) Active instances that are currently hosting zero (0) game sessions.

        This metric measures capacity that is available but unused.
        This metric can be used with automatic scaling.

        :param account: Account which this metric comes from. Default: - Deployment account.
        :param color: The hex color code, prefixed with '#' (e.g. '#00ff00'), to use when this metric is rendered on a graph. The ``Color`` class has a set of standard colors that can be used here. Default: - Automatic color
        :param dimensions_map: Dimensions of the metric. Default: - No dimensions.
        :param id: Unique identifier for this metric when used in dashboard widgets. The id can be used as a variable to represent this metric in math expressions. Valid characters are letters, numbers, and underscore. The first character must be a lowercase letter. Default: - No ID
        :param label: Label for this metric when added to a Graph in a Dashboard. You can use `dynamic labels <https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/graph-dynamic-labels.html>`_ to show summary information about the entire displayed time series in the legend. For example, if you use:: [max: ${MAX}] MyMetric As the metric label, the maximum value in the visible range will be shown next to the time series name in the graph's legend. Default: - No label
        :param period: The period over which the specified statistic is applied. Default: Duration.minutes(5)
        :param region: Region which this metric comes from. Default: - Deployment region.
        :param stack_account: Account of the stack this metric is attached to. Default: - Deployment account.
        :param stack_region: Region of the stack this metric is attached to. Default: - Deployment region.
        :param statistic: What function to use for aggregating. Use the ``aws_cloudwatch.Stats`` helper class to construct valid input strings. Can be one of the following: - "Minimum" | "min" - "Maximum" | "max" - "Average" | "avg" - "Sum" | "sum" - "SampleCount | "n" - "pNN.NN" - "tmNN.NN" | "tm(NN.NN%:NN.NN%)" - "iqm" - "wmNN.NN" | "wm(NN.NN%:NN.NN%)" - "tcNN.NN" | "tc(NN.NN%:NN.NN%)" - "tsNN.NN" | "ts(NN.NN%:NN.NN%)" Default: Average
        :param unit: Unit used to filter the metric stream. Only refer to datums emitted to the metric stream with the given unit and ignore all others. Only useful when datums are being emitted to the same metric stream under different units. The default is to use all matric datums in the stream, regardless of unit, which is recommended in nearly all cases. CloudWatch does not honor this property for graphs. Default: - All metric datums in the given metric stream
        :param visible: Whether this metric should be visible in dashboard graphs. Setting this to false is useful when you want to hide raw metrics that are used in math expressions, and show only the expression results. Default: true

        :stability: experimental
        '''
        ...

    @jsii.member(jsii_name="metricInstanceInterruptions")
    def metric_instance_interruptions(
        self,
        *,
        account: typing.Optional[builtins.str] = None,
        color: typing.Optional[builtins.str] = None,
        dimensions_map: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        id: typing.Optional[builtins.str] = None,
        label: typing.Optional[builtins.str] = None,
        period: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        region: typing.Optional[builtins.str] = None,
        stack_account: typing.Optional[builtins.str] = None,
        stack_region: typing.Optional[builtins.str] = None,
        statistic: typing.Optional[builtins.str] = None,
        unit: typing.Optional[_aws_cdk_aws_cloudwatch_ceddda9d.Unit] = None,
        visible: typing.Optional[builtins.bool] = None,
    ) -> _aws_cdk_aws_cloudwatch_ceddda9d.Metric:
        '''(experimental) Number of spot instances that have been interrupted.

        :param account: Account which this metric comes from. Default: - Deployment account.
        :param color: The hex color code, prefixed with '#' (e.g. '#00ff00'), to use when this metric is rendered on a graph. The ``Color`` class has a set of standard colors that can be used here. Default: - Automatic color
        :param dimensions_map: Dimensions of the metric. Default: - No dimensions.
        :param id: Unique identifier for this metric when used in dashboard widgets. The id can be used as a variable to represent this metric in math expressions. Valid characters are letters, numbers, and underscore. The first character must be a lowercase letter. Default: - No ID
        :param label: Label for this metric when added to a Graph in a Dashboard. You can use `dynamic labels <https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/graph-dynamic-labels.html>`_ to show summary information about the entire displayed time series in the legend. For example, if you use:: [max: ${MAX}] MyMetric As the metric label, the maximum value in the visible range will be shown next to the time series name in the graph's legend. Default: - No label
        :param period: The period over which the specified statistic is applied. Default: Duration.minutes(5)
        :param region: Region which this metric comes from. Default: - Deployment region.
        :param stack_account: Account of the stack this metric is attached to. Default: - Deployment account.
        :param stack_region: Region of the stack this metric is attached to. Default: - Deployment region.
        :param statistic: What function to use for aggregating. Use the ``aws_cloudwatch.Stats`` helper class to construct valid input strings. Can be one of the following: - "Minimum" | "min" - "Maximum" | "max" - "Average" | "avg" - "Sum" | "sum" - "SampleCount | "n" - "pNN.NN" - "tmNN.NN" | "tm(NN.NN%:NN.NN%)" - "iqm" - "wmNN.NN" | "wm(NN.NN%:NN.NN%)" - "tcNN.NN" | "tc(NN.NN%:NN.NN%)" - "tsNN.NN" | "ts(NN.NN%:NN.NN%)" Default: Average
        :param unit: Unit used to filter the metric stream. Only refer to datums emitted to the metric stream with the given unit and ignore all others. Only useful when datums are being emitted to the same metric stream under different units. The default is to use all matric datums in the stream, regardless of unit, which is recommended in nearly all cases. CloudWatch does not honor this property for graphs. Default: - All metric datums in the given metric stream
        :param visible: Whether this metric should be visible in dashboard graphs. Setting this to false is useful when you want to hide raw metrics that are used in math expressions, and show only the expression results. Default: true

        :stability: experimental
        '''
        ...

    @jsii.member(jsii_name="metricMaxInstances")
    def metric_max_instances(
        self,
        *,
        account: typing.Optional[builtins.str] = None,
        color: typing.Optional[builtins.str] = None,
        dimensions_map: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        id: typing.Optional[builtins.str] = None,
        label: typing.Optional[builtins.str] = None,
        period: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        region: typing.Optional[builtins.str] = None,
        stack_account: typing.Optional[builtins.str] = None,
        stack_region: typing.Optional[builtins.str] = None,
        statistic: typing.Optional[builtins.str] = None,
        unit: typing.Optional[_aws_cdk_aws_cloudwatch_ceddda9d.Unit] = None,
        visible: typing.Optional[builtins.bool] = None,
    ) -> _aws_cdk_aws_cloudwatch_ceddda9d.Metric:
        '''(experimental) Maximum number of instances that are allowed for the fleet.

        A fleet's instance maximum determines the capacity ceiling during manual or automatic scaling up.
        This metric is not available when viewing data for fleet metric groups.

        :param account: Account which this metric comes from. Default: - Deployment account.
        :param color: The hex color code, prefixed with '#' (e.g. '#00ff00'), to use when this metric is rendered on a graph. The ``Color`` class has a set of standard colors that can be used here. Default: - Automatic color
        :param dimensions_map: Dimensions of the metric. Default: - No dimensions.
        :param id: Unique identifier for this metric when used in dashboard widgets. The id can be used as a variable to represent this metric in math expressions. Valid characters are letters, numbers, and underscore. The first character must be a lowercase letter. Default: - No ID
        :param label: Label for this metric when added to a Graph in a Dashboard. You can use `dynamic labels <https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/graph-dynamic-labels.html>`_ to show summary information about the entire displayed time series in the legend. For example, if you use:: [max: ${MAX}] MyMetric As the metric label, the maximum value in the visible range will be shown next to the time series name in the graph's legend. Default: - No label
        :param period: The period over which the specified statistic is applied. Default: Duration.minutes(5)
        :param region: Region which this metric comes from. Default: - Deployment region.
        :param stack_account: Account of the stack this metric is attached to. Default: - Deployment account.
        :param stack_region: Region of the stack this metric is attached to. Default: - Deployment region.
        :param statistic: What function to use for aggregating. Use the ``aws_cloudwatch.Stats`` helper class to construct valid input strings. Can be one of the following: - "Minimum" | "min" - "Maximum" | "max" - "Average" | "avg" - "Sum" | "sum" - "SampleCount | "n" - "pNN.NN" - "tmNN.NN" | "tm(NN.NN%:NN.NN%)" - "iqm" - "wmNN.NN" | "wm(NN.NN%:NN.NN%)" - "tcNN.NN" | "tc(NN.NN%:NN.NN%)" - "tsNN.NN" | "ts(NN.NN%:NN.NN%)" Default: Average
        :param unit: Unit used to filter the metric stream. Only refer to datums emitted to the metric stream with the given unit and ignore all others. Only useful when datums are being emitted to the same metric stream under different units. The default is to use all matric datums in the stream, regardless of unit, which is recommended in nearly all cases. CloudWatch does not honor this property for graphs. Default: - All metric datums in the given metric stream
        :param visible: Whether this metric should be visible in dashboard graphs. Setting this to false is useful when you want to hide raw metrics that are used in math expressions, and show only the expression results. Default: true

        :stability: experimental
        '''
        ...

    @jsii.member(jsii_name="metricMinInstances")
    def metric_min_instances(
        self,
        *,
        account: typing.Optional[builtins.str] = None,
        color: typing.Optional[builtins.str] = None,
        dimensions_map: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        id: typing.Optional[builtins.str] = None,
        label: typing.Optional[builtins.str] = None,
        period: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        region: typing.Optional[builtins.str] = None,
        stack_account: typing.Optional[builtins.str] = None,
        stack_region: typing.Optional[builtins.str] = None,
        statistic: typing.Optional[builtins.str] = None,
        unit: typing.Optional[_aws_cdk_aws_cloudwatch_ceddda9d.Unit] = None,
        visible: typing.Optional[builtins.bool] = None,
    ) -> _aws_cdk_aws_cloudwatch_ceddda9d.Metric:
        '''(experimental) Minimum number of instances allowed for the fleet.

        A fleet's instance minimum determines the capacity floor during manual or automatic scaling down.
        This metric is not available when viewing data for fleet metric groups.

        :param account: Account which this metric comes from. Default: - Deployment account.
        :param color: The hex color code, prefixed with '#' (e.g. '#00ff00'), to use when this metric is rendered on a graph. The ``Color`` class has a set of standard colors that can be used here. Default: - Automatic color
        :param dimensions_map: Dimensions of the metric. Default: - No dimensions.
        :param id: Unique identifier for this metric when used in dashboard widgets. The id can be used as a variable to represent this metric in math expressions. Valid characters are letters, numbers, and underscore. The first character must be a lowercase letter. Default: - No ID
        :param label: Label for this metric when added to a Graph in a Dashboard. You can use `dynamic labels <https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/graph-dynamic-labels.html>`_ to show summary information about the entire displayed time series in the legend. For example, if you use:: [max: ${MAX}] MyMetric As the metric label, the maximum value in the visible range will be shown next to the time series name in the graph's legend. Default: - No label
        :param period: The period over which the specified statistic is applied. Default: Duration.minutes(5)
        :param region: Region which this metric comes from. Default: - Deployment region.
        :param stack_account: Account of the stack this metric is attached to. Default: - Deployment account.
        :param stack_region: Region of the stack this metric is attached to. Default: - Deployment region.
        :param statistic: What function to use for aggregating. Use the ``aws_cloudwatch.Stats`` helper class to construct valid input strings. Can be one of the following: - "Minimum" | "min" - "Maximum" | "max" - "Average" | "avg" - "Sum" | "sum" - "SampleCount | "n" - "pNN.NN" - "tmNN.NN" | "tm(NN.NN%:NN.NN%)" - "iqm" - "wmNN.NN" | "wm(NN.NN%:NN.NN%)" - "tcNN.NN" | "tc(NN.NN%:NN.NN%)" - "tsNN.NN" | "ts(NN.NN%:NN.NN%)" Default: Average
        :param unit: Unit used to filter the metric stream. Only refer to datums emitted to the metric stream with the given unit and ignore all others. Only useful when datums are being emitted to the same metric stream under different units. The default is to use all matric datums in the stream, regardless of unit, which is recommended in nearly all cases. CloudWatch does not honor this property for graphs. Default: - All metric datums in the given metric stream
        :param visible: Whether this metric should be visible in dashboard graphs. Setting this to false is useful when you want to hide raw metrics that are used in math expressions, and show only the expression results. Default: true

        :stability: experimental
        '''
        ...

    @jsii.member(jsii_name="metricPercentIdleInstances")
    def metric_percent_idle_instances(
        self,
        *,
        account: typing.Optional[builtins.str] = None,
        color: typing.Optional[builtins.str] = None,
        dimensions_map: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        id: typing.Optional[builtins.str] = None,
        label: typing.Optional[builtins.str] = None,
        period: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        region: typing.Optional[builtins.str] = None,
        stack_account: typing.Optional[builtins.str] = None,
        stack_region: typing.Optional[builtins.str] = None,
        statistic: typing.Optional[builtins.str] = None,
        unit: typing.Optional[_aws_cdk_aws_cloudwatch_ceddda9d.Unit] = None,
        visible: typing.Optional[builtins.bool] = None,
    ) -> _aws_cdk_aws_cloudwatch_ceddda9d.Metric:
        '''(experimental) Percentage of all active instances that are idle (calculated as IdleInstances / ActiveInstances).

        This metric can be used for automatic scaling.

        :param account: Account which this metric comes from. Default: - Deployment account.
        :param color: The hex color code, prefixed with '#' (e.g. '#00ff00'), to use when this metric is rendered on a graph. The ``Color`` class has a set of standard colors that can be used here. Default: - Automatic color
        :param dimensions_map: Dimensions of the metric. Default: - No dimensions.
        :param id: Unique identifier for this metric when used in dashboard widgets. The id can be used as a variable to represent this metric in math expressions. Valid characters are letters, numbers, and underscore. The first character must be a lowercase letter. Default: - No ID
        :param label: Label for this metric when added to a Graph in a Dashboard. You can use `dynamic labels <https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/graph-dynamic-labels.html>`_ to show summary information about the entire displayed time series in the legend. For example, if you use:: [max: ${MAX}] MyMetric As the metric label, the maximum value in the visible range will be shown next to the time series name in the graph's legend. Default: - No label
        :param period: The period over which the specified statistic is applied. Default: Duration.minutes(5)
        :param region: Region which this metric comes from. Default: - Deployment region.
        :param stack_account: Account of the stack this metric is attached to. Default: - Deployment account.
        :param stack_region: Region of the stack this metric is attached to. Default: - Deployment region.
        :param statistic: What function to use for aggregating. Use the ``aws_cloudwatch.Stats`` helper class to construct valid input strings. Can be one of the following: - "Minimum" | "min" - "Maximum" | "max" - "Average" | "avg" - "Sum" | "sum" - "SampleCount | "n" - "pNN.NN" - "tmNN.NN" | "tm(NN.NN%:NN.NN%)" - "iqm" - "wmNN.NN" | "wm(NN.NN%:NN.NN%)" - "tcNN.NN" | "tc(NN.NN%:NN.NN%)" - "tsNN.NN" | "ts(NN.NN%:NN.NN%)" Default: Average
        :param unit: Unit used to filter the metric stream. Only refer to datums emitted to the metric stream with the given unit and ignore all others. Only useful when datums are being emitted to the same metric stream under different units. The default is to use all matric datums in the stream, regardless of unit, which is recommended in nearly all cases. CloudWatch does not honor this property for graphs. Default: - All metric datums in the given metric stream
        :param visible: Whether this metric should be visible in dashboard graphs. Setting this to false is useful when you want to hide raw metrics that are used in math expressions, and show only the expression results. Default: true

        :stability: experimental
        '''
        ...


class _IFleetProxy(
    jsii.proxy_for(_aws_cdk_ceddda9d.IResource), # type: ignore[misc]
    jsii.proxy_for(_aws_cdk_aws_iam_ceddda9d.IGrantable), # type: ignore[misc]
    jsii.proxy_for(IGameSessionQueueDestination), # type: ignore[misc]
):
    '''(experimental) Represents a Gamelift fleet.

    :stability: experimental
    '''

    __jsii_type__: typing.ClassVar[str] = "@aws-cdk/aws-gamelift-alpha.IFleet"

    @builtins.property
    @jsii.member(jsii_name="fleetArn")
    def fleet_arn(self) -> builtins.str:
        '''(experimental) The ARN of the fleet.

        :stability: experimental
        :attribute: true
        '''
        return typing.cast(builtins.str, jsii.get(self, "fleetArn"))

    @builtins.property
    @jsii.member(jsii_name="fleetId")
    def fleet_id(self) -> builtins.str:
        '''(experimental) The Identifier of the fleet.

        :stability: experimental
        :attribute: true
        '''
        return typing.cast(builtins.str, jsii.get(self, "fleetId"))

    @jsii.member(jsii_name="grant")
    def grant(
        self,
        grantee: _aws_cdk_aws_iam_ceddda9d.IGrantable,
        *actions: builtins.str,
    ) -> _aws_cdk_aws_iam_ceddda9d.Grant:
        '''(experimental) Grant the ``grantee`` identity permissions to perform ``actions``.

        :param grantee: -
        :param actions: -

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ca0b1d9cf440a1667662692eea86859a891f53c0b744ac93f409e17507bf4e1f)
            check_type(argname="argument grantee", value=grantee, expected_type=type_hints["grantee"])
            check_type(argname="argument actions", value=actions, expected_type=typing.Tuple[type_hints["actions"], ...]) # pyright: ignore [reportGeneralTypeIssues]
        return typing.cast(_aws_cdk_aws_iam_ceddda9d.Grant, jsii.invoke(self, "grant", [grantee, *actions]))

    @jsii.member(jsii_name="metric")
    def metric(
        self,
        metric_name: builtins.str,
        *,
        account: typing.Optional[builtins.str] = None,
        color: typing.Optional[builtins.str] = None,
        dimensions_map: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        id: typing.Optional[builtins.str] = None,
        label: typing.Optional[builtins.str] = None,
        period: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        region: typing.Optional[builtins.str] = None,
        stack_account: typing.Optional[builtins.str] = None,
        stack_region: typing.Optional[builtins.str] = None,
        statistic: typing.Optional[builtins.str] = None,
        unit: typing.Optional[_aws_cdk_aws_cloudwatch_ceddda9d.Unit] = None,
        visible: typing.Optional[builtins.bool] = None,
    ) -> _aws_cdk_aws_cloudwatch_ceddda9d.Metric:
        '''(experimental) Return the given named metric for this fleet.

        :param metric_name: -
        :param account: Account which this metric comes from. Default: - Deployment account.
        :param color: The hex color code, prefixed with '#' (e.g. '#00ff00'), to use when this metric is rendered on a graph. The ``Color`` class has a set of standard colors that can be used here. Default: - Automatic color
        :param dimensions_map: Dimensions of the metric. Default: - No dimensions.
        :param id: Unique identifier for this metric when used in dashboard widgets. The id can be used as a variable to represent this metric in math expressions. Valid characters are letters, numbers, and underscore. The first character must be a lowercase letter. Default: - No ID
        :param label: Label for this metric when added to a Graph in a Dashboard. You can use `dynamic labels <https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/graph-dynamic-labels.html>`_ to show summary information about the entire displayed time series in the legend. For example, if you use:: [max: ${MAX}] MyMetric As the metric label, the maximum value in the visible range will be shown next to the time series name in the graph's legend. Default: - No label
        :param period: The period over which the specified statistic is applied. Default: Duration.minutes(5)
        :param region: Region which this metric comes from. Default: - Deployment region.
        :param stack_account: Account of the stack this metric is attached to. Default: - Deployment account.
        :param stack_region: Region of the stack this metric is attached to. Default: - Deployment region.
        :param statistic: What function to use for aggregating. Use the ``aws_cloudwatch.Stats`` helper class to construct valid input strings. Can be one of the following: - "Minimum" | "min" - "Maximum" | "max" - "Average" | "avg" - "Sum" | "sum" - "SampleCount | "n" - "pNN.NN" - "tmNN.NN" | "tm(NN.NN%:NN.NN%)" - "iqm" - "wmNN.NN" | "wm(NN.NN%:NN.NN%)" - "tcNN.NN" | "tc(NN.NN%:NN.NN%)" - "tsNN.NN" | "ts(NN.NN%:NN.NN%)" Default: Average
        :param unit: Unit used to filter the metric stream. Only refer to datums emitted to the metric stream with the given unit and ignore all others. Only useful when datums are being emitted to the same metric stream under different units. The default is to use all matric datums in the stream, regardless of unit, which is recommended in nearly all cases. CloudWatch does not honor this property for graphs. Default: - All metric datums in the given metric stream
        :param visible: Whether this metric should be visible in dashboard graphs. Setting this to false is useful when you want to hide raw metrics that are used in math expressions, and show only the expression results. Default: true

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b257572800d0f56ff6c7ae43e8988405d4a6610a079279420d0242daedb7f071)
            check_type(argname="argument metric_name", value=metric_name, expected_type=type_hints["metric_name"])
        props = _aws_cdk_aws_cloudwatch_ceddda9d.MetricOptions(
            account=account,
            color=color,
            dimensions_map=dimensions_map,
            id=id,
            label=label,
            period=period,
            region=region,
            stack_account=stack_account,
            stack_region=stack_region,
            statistic=statistic,
            unit=unit,
            visible=visible,
        )

        return typing.cast(_aws_cdk_aws_cloudwatch_ceddda9d.Metric, jsii.invoke(self, "metric", [metric_name, props]))

    @jsii.member(jsii_name="metricActiveInstances")
    def metric_active_instances(
        self,
        *,
        account: typing.Optional[builtins.str] = None,
        color: typing.Optional[builtins.str] = None,
        dimensions_map: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        id: typing.Optional[builtins.str] = None,
        label: typing.Optional[builtins.str] = None,
        period: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        region: typing.Optional[builtins.str] = None,
        stack_account: typing.Optional[builtins.str] = None,
        stack_region: typing.Optional[builtins.str] = None,
        statistic: typing.Optional[builtins.str] = None,
        unit: typing.Optional[_aws_cdk_aws_cloudwatch_ceddda9d.Unit] = None,
        visible: typing.Optional[builtins.bool] = None,
    ) -> _aws_cdk_aws_cloudwatch_ceddda9d.Metric:
        '''(experimental) Instances with ``ACTIVE`` status, which means they are running active server processes.

        The count includes idle instances and those that are hosting one or more game sessions.
        This metric measures current total instance capacity.

        This metric can be used with automatic scaling.

        :param account: Account which this metric comes from. Default: - Deployment account.
        :param color: The hex color code, prefixed with '#' (e.g. '#00ff00'), to use when this metric is rendered on a graph. The ``Color`` class has a set of standard colors that can be used here. Default: - Automatic color
        :param dimensions_map: Dimensions of the metric. Default: - No dimensions.
        :param id: Unique identifier for this metric when used in dashboard widgets. The id can be used as a variable to represent this metric in math expressions. Valid characters are letters, numbers, and underscore. The first character must be a lowercase letter. Default: - No ID
        :param label: Label for this metric when added to a Graph in a Dashboard. You can use `dynamic labels <https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/graph-dynamic-labels.html>`_ to show summary information about the entire displayed time series in the legend. For example, if you use:: [max: ${MAX}] MyMetric As the metric label, the maximum value in the visible range will be shown next to the time series name in the graph's legend. Default: - No label
        :param period: The period over which the specified statistic is applied. Default: Duration.minutes(5)
        :param region: Region which this metric comes from. Default: - Deployment region.
        :param stack_account: Account of the stack this metric is attached to. Default: - Deployment account.
        :param stack_region: Region of the stack this metric is attached to. Default: - Deployment region.
        :param statistic: What function to use for aggregating. Use the ``aws_cloudwatch.Stats`` helper class to construct valid input strings. Can be one of the following: - "Minimum" | "min" - "Maximum" | "max" - "Average" | "avg" - "Sum" | "sum" - "SampleCount | "n" - "pNN.NN" - "tmNN.NN" | "tm(NN.NN%:NN.NN%)" - "iqm" - "wmNN.NN" | "wm(NN.NN%:NN.NN%)" - "tcNN.NN" | "tc(NN.NN%:NN.NN%)" - "tsNN.NN" | "ts(NN.NN%:NN.NN%)" Default: Average
        :param unit: Unit used to filter the metric stream. Only refer to datums emitted to the metric stream with the given unit and ignore all others. Only useful when datums are being emitted to the same metric stream under different units. The default is to use all matric datums in the stream, regardless of unit, which is recommended in nearly all cases. CloudWatch does not honor this property for graphs. Default: - All metric datums in the given metric stream
        :param visible: Whether this metric should be visible in dashboard graphs. Setting this to false is useful when you want to hide raw metrics that are used in math expressions, and show only the expression results. Default: true

        :stability: experimental
        '''
        props = _aws_cdk_aws_cloudwatch_ceddda9d.MetricOptions(
            account=account,
            color=color,
            dimensions_map=dimensions_map,
            id=id,
            label=label,
            period=period,
            region=region,
            stack_account=stack_account,
            stack_region=stack_region,
            statistic=statistic,
            unit=unit,
            visible=visible,
        )

        return typing.cast(_aws_cdk_aws_cloudwatch_ceddda9d.Metric, jsii.invoke(self, "metricActiveInstances", [props]))

    @jsii.member(jsii_name="metricDesiredInstances")
    def metric_desired_instances(
        self,
        *,
        account: typing.Optional[builtins.str] = None,
        color: typing.Optional[builtins.str] = None,
        dimensions_map: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        id: typing.Optional[builtins.str] = None,
        label: typing.Optional[builtins.str] = None,
        period: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        region: typing.Optional[builtins.str] = None,
        stack_account: typing.Optional[builtins.str] = None,
        stack_region: typing.Optional[builtins.str] = None,
        statistic: typing.Optional[builtins.str] = None,
        unit: typing.Optional[_aws_cdk_aws_cloudwatch_ceddda9d.Unit] = None,
        visible: typing.Optional[builtins.bool] = None,
    ) -> _aws_cdk_aws_cloudwatch_ceddda9d.Metric:
        '''(experimental) Target number of active instances that GameLift is working to maintain in the fleet.

        With automatic scaling, this value is determined based on the scaling policies currently in force.
        Without automatic scaling, this value is set manually.
        This metric is not available when viewing data for fleet metric groups.

        :param account: Account which this metric comes from. Default: - Deployment account.
        :param color: The hex color code, prefixed with '#' (e.g. '#00ff00'), to use when this metric is rendered on a graph. The ``Color`` class has a set of standard colors that can be used here. Default: - Automatic color
        :param dimensions_map: Dimensions of the metric. Default: - No dimensions.
        :param id: Unique identifier for this metric when used in dashboard widgets. The id can be used as a variable to represent this metric in math expressions. Valid characters are letters, numbers, and underscore. The first character must be a lowercase letter. Default: - No ID
        :param label: Label for this metric when added to a Graph in a Dashboard. You can use `dynamic labels <https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/graph-dynamic-labels.html>`_ to show summary information about the entire displayed time series in the legend. For example, if you use:: [max: ${MAX}] MyMetric As the metric label, the maximum value in the visible range will be shown next to the time series name in the graph's legend. Default: - No label
        :param period: The period over which the specified statistic is applied. Default: Duration.minutes(5)
        :param region: Region which this metric comes from. Default: - Deployment region.
        :param stack_account: Account of the stack this metric is attached to. Default: - Deployment account.
        :param stack_region: Region of the stack this metric is attached to. Default: - Deployment region.
        :param statistic: What function to use for aggregating. Use the ``aws_cloudwatch.Stats`` helper class to construct valid input strings. Can be one of the following: - "Minimum" | "min" - "Maximum" | "max" - "Average" | "avg" - "Sum" | "sum" - "SampleCount | "n" - "pNN.NN" - "tmNN.NN" | "tm(NN.NN%:NN.NN%)" - "iqm" - "wmNN.NN" | "wm(NN.NN%:NN.NN%)" - "tcNN.NN" | "tc(NN.NN%:NN.NN%)" - "tsNN.NN" | "ts(NN.NN%:NN.NN%)" Default: Average
        :param unit: Unit used to filter the metric stream. Only refer to datums emitted to the metric stream with the given unit and ignore all others. Only useful when datums are being emitted to the same metric stream under different units. The default is to use all matric datums in the stream, regardless of unit, which is recommended in nearly all cases. CloudWatch does not honor this property for graphs. Default: - All metric datums in the given metric stream
        :param visible: Whether this metric should be visible in dashboard graphs. Setting this to false is useful when you want to hide raw metrics that are used in math expressions, and show only the expression results. Default: true

        :stability: experimental
        '''
        props = _aws_cdk_aws_cloudwatch_ceddda9d.MetricOptions(
            account=account,
            color=color,
            dimensions_map=dimensions_map,
            id=id,
            label=label,
            period=period,
            region=region,
            stack_account=stack_account,
            stack_region=stack_region,
            statistic=statistic,
            unit=unit,
            visible=visible,
        )

        return typing.cast(_aws_cdk_aws_cloudwatch_ceddda9d.Metric, jsii.invoke(self, "metricDesiredInstances", [props]))

    @jsii.member(jsii_name="metricIdleInstances")
    def metric_idle_instances(
        self,
        *,
        account: typing.Optional[builtins.str] = None,
        color: typing.Optional[builtins.str] = None,
        dimensions_map: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        id: typing.Optional[builtins.str] = None,
        label: typing.Optional[builtins.str] = None,
        period: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        region: typing.Optional[builtins.str] = None,
        stack_account: typing.Optional[builtins.str] = None,
        stack_region: typing.Optional[builtins.str] = None,
        statistic: typing.Optional[builtins.str] = None,
        unit: typing.Optional[_aws_cdk_aws_cloudwatch_ceddda9d.Unit] = None,
        visible: typing.Optional[builtins.bool] = None,
    ) -> _aws_cdk_aws_cloudwatch_ceddda9d.Metric:
        '''(experimental) Active instances that are currently hosting zero (0) game sessions.

        This metric measures capacity that is available but unused.
        This metric can be used with automatic scaling.

        :param account: Account which this metric comes from. Default: - Deployment account.
        :param color: The hex color code, prefixed with '#' (e.g. '#00ff00'), to use when this metric is rendered on a graph. The ``Color`` class has a set of standard colors that can be used here. Default: - Automatic color
        :param dimensions_map: Dimensions of the metric. Default: - No dimensions.
        :param id: Unique identifier for this metric when used in dashboard widgets. The id can be used as a variable to represent this metric in math expressions. Valid characters are letters, numbers, and underscore. The first character must be a lowercase letter. Default: - No ID
        :param label: Label for this metric when added to a Graph in a Dashboard. You can use `dynamic labels <https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/graph-dynamic-labels.html>`_ to show summary information about the entire displayed time series in the legend. For example, if you use:: [max: ${MAX}] MyMetric As the metric label, the maximum value in the visible range will be shown next to the time series name in the graph's legend. Default: - No label
        :param period: The period over which the specified statistic is applied. Default: Duration.minutes(5)
        :param region: Region which this metric comes from. Default: - Deployment region.
        :param stack_account: Account of the stack this metric is attached to. Default: - Deployment account.
        :param stack_region: Region of the stack this metric is attached to. Default: - Deployment region.
        :param statistic: What function to use for aggregating. Use the ``aws_cloudwatch.Stats`` helper class to construct valid input strings. Can be one of the following: - "Minimum" | "min" - "Maximum" | "max" - "Average" | "avg" - "Sum" | "sum" - "SampleCount | "n" - "pNN.NN" - "tmNN.NN" | "tm(NN.NN%:NN.NN%)" - "iqm" - "wmNN.NN" | "wm(NN.NN%:NN.NN%)" - "tcNN.NN" | "tc(NN.NN%:NN.NN%)" - "tsNN.NN" | "ts(NN.NN%:NN.NN%)" Default: Average
        :param unit: Unit used to filter the metric stream. Only refer to datums emitted to the metric stream with the given unit and ignore all others. Only useful when datums are being emitted to the same metric stream under different units. The default is to use all matric datums in the stream, regardless of unit, which is recommended in nearly all cases. CloudWatch does not honor this property for graphs. Default: - All metric datums in the given metric stream
        :param visible: Whether this metric should be visible in dashboard graphs. Setting this to false is useful when you want to hide raw metrics that are used in math expressions, and show only the expression results. Default: true

        :stability: experimental
        '''
        props = _aws_cdk_aws_cloudwatch_ceddda9d.MetricOptions(
            account=account,
            color=color,
            dimensions_map=dimensions_map,
            id=id,
            label=label,
            period=period,
            region=region,
            stack_account=stack_account,
            stack_region=stack_region,
            statistic=statistic,
            unit=unit,
            visible=visible,
        )

        return typing.cast(_aws_cdk_aws_cloudwatch_ceddda9d.Metric, jsii.invoke(self, "metricIdleInstances", [props]))

    @jsii.member(jsii_name="metricInstanceInterruptions")
    def metric_instance_interruptions(
        self,
        *,
        account: typing.Optional[builtins.str] = None,
        color: typing.Optional[builtins.str] = None,
        dimensions_map: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        id: typing.Optional[builtins.str] = None,
        label: typing.Optional[builtins.str] = None,
        period: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        region: typing.Optional[builtins.str] = None,
        stack_account: typing.Optional[builtins.str] = None,
        stack_region: typing.Optional[builtins.str] = None,
        statistic: typing.Optional[builtins.str] = None,
        unit: typing.Optional[_aws_cdk_aws_cloudwatch_ceddda9d.Unit] = None,
        visible: typing.Optional[builtins.bool] = None,
    ) -> _aws_cdk_aws_cloudwatch_ceddda9d.Metric:
        '''(experimental) Number of spot instances that have been interrupted.

        :param account: Account which this metric comes from. Default: - Deployment account.
        :param color: The hex color code, prefixed with '#' (e.g. '#00ff00'), to use when this metric is rendered on a graph. The ``Color`` class has a set of standard colors that can be used here. Default: - Automatic color
        :param dimensions_map: Dimensions of the metric. Default: - No dimensions.
        :param id: Unique identifier for this metric when used in dashboard widgets. The id can be used as a variable to represent this metric in math expressions. Valid characters are letters, numbers, and underscore. The first character must be a lowercase letter. Default: - No ID
        :param label: Label for this metric when added to a Graph in a Dashboard. You can use `dynamic labels <https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/graph-dynamic-labels.html>`_ to show summary information about the entire displayed time series in the legend. For example, if you use:: [max: ${MAX}] MyMetric As the metric label, the maximum value in the visible range will be shown next to the time series name in the graph's legend. Default: - No label
        :param period: The period over which the specified statistic is applied. Default: Duration.minutes(5)
        :param region: Region which this metric comes from. Default: - Deployment region.
        :param stack_account: Account of the stack this metric is attached to. Default: - Deployment account.
        :param stack_region: Region of the stack this metric is attached to. Default: - Deployment region.
        :param statistic: What function to use for aggregating. Use the ``aws_cloudwatch.Stats`` helper class to construct valid input strings. Can be one of the following: - "Minimum" | "min" - "Maximum" | "max" - "Average" | "avg" - "Sum" | "sum" - "SampleCount | "n" - "pNN.NN" - "tmNN.NN" | "tm(NN.NN%:NN.NN%)" - "iqm" - "wmNN.NN" | "wm(NN.NN%:NN.NN%)" - "tcNN.NN" | "tc(NN.NN%:NN.NN%)" - "tsNN.NN" | "ts(NN.NN%:NN.NN%)" Default: Average
        :param unit: Unit used to filter the metric stream. Only refer to datums emitted to the metric stream with the given unit and ignore all others. Only useful when datums are being emitted to the same metric stream under different units. The default is to use all matric datums in the stream, regardless of unit, which is recommended in nearly all cases. CloudWatch does not honor this property for graphs. Default: - All metric datums in the given metric stream
        :param visible: Whether this metric should be visible in dashboard graphs. Setting this to false is useful when you want to hide raw metrics that are used in math expressions, and show only the expression results. Default: true

        :stability: experimental
        '''
        props = _aws_cdk_aws_cloudwatch_ceddda9d.MetricOptions(
            account=account,
            color=color,
            dimensions_map=dimensions_map,
            id=id,
            label=label,
            period=period,
            region=region,
            stack_account=stack_account,
            stack_region=stack_region,
            statistic=statistic,
            unit=unit,
            visible=visible,
        )

        return typing.cast(_aws_cdk_aws_cloudwatch_ceddda9d.Metric, jsii.invoke(self, "metricInstanceInterruptions", [props]))

    @jsii.member(jsii_name="metricMaxInstances")
    def metric_max_instances(
        self,
        *,
        account: typing.Optional[builtins.str] = None,
        color: typing.Optional[builtins.str] = None,
        dimensions_map: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        id: typing.Optional[builtins.str] = None,
        label: typing.Optional[builtins.str] = None,
        period: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        region: typing.Optional[builtins.str] = None,
        stack_account: typing.Optional[builtins.str] = None,
        stack_region: typing.Optional[builtins.str] = None,
        statistic: typing.Optional[builtins.str] = None,
        unit: typing.Optional[_aws_cdk_aws_cloudwatch_ceddda9d.Unit] = None,
        visible: typing.Optional[builtins.bool] = None,
    ) -> _aws_cdk_aws_cloudwatch_ceddda9d.Metric:
        '''(experimental) Maximum number of instances that are allowed for the fleet.

        A fleet's instance maximum determines the capacity ceiling during manual or automatic scaling up.
        This metric is not available when viewing data for fleet metric groups.

        :param account: Account which this metric comes from. Default: - Deployment account.
        :param color: The hex color code, prefixed with '#' (e.g. '#00ff00'), to use when this metric is rendered on a graph. The ``Color`` class has a set of standard colors that can be used here. Default: - Automatic color
        :param dimensions_map: Dimensions of the metric. Default: - No dimensions.
        :param id: Unique identifier for this metric when used in dashboard widgets. The id can be used as a variable to represent this metric in math expressions. Valid characters are letters, numbers, and underscore. The first character must be a lowercase letter. Default: - No ID
        :param label: Label for this metric when added to a Graph in a Dashboard. You can use `dynamic labels <https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/graph-dynamic-labels.html>`_ to show summary information about the entire displayed time series in the legend. For example, if you use:: [max: ${MAX}] MyMetric As the metric label, the maximum value in the visible range will be shown next to the time series name in the graph's legend. Default: - No label
        :param period: The period over which the specified statistic is applied. Default: Duration.minutes(5)
        :param region: Region which this metric comes from. Default: - Deployment region.
        :param stack_account: Account of the stack this metric is attached to. Default: - Deployment account.
        :param stack_region: Region of the stack this metric is attached to. Default: - Deployment region.
        :param statistic: What function to use for aggregating. Use the ``aws_cloudwatch.Stats`` helper class to construct valid input strings. Can be one of the following: - "Minimum" | "min" - "Maximum" | "max" - "Average" | "avg" - "Sum" | "sum" - "SampleCount | "n" - "pNN.NN" - "tmNN.NN" | "tm(NN.NN%:NN.NN%)" - "iqm" - "wmNN.NN" | "wm(NN.NN%:NN.NN%)" - "tcNN.NN" | "tc(NN.NN%:NN.NN%)" - "tsNN.NN" | "ts(NN.NN%:NN.NN%)" Default: Average
        :param unit: Unit used to filter the metric stream. Only refer to datums emitted to the metric stream with the given unit and ignore all others. Only useful when datums are being emitted to the same metric stream under different units. The default is to use all matric datums in the stream, regardless of unit, which is recommended in nearly all cases. CloudWatch does not honor this property for graphs. Default: - All metric datums in the given metric stream
        :param visible: Whether this metric should be visible in dashboard graphs. Setting this to false is useful when you want to hide raw metrics that are used in math expressions, and show only the expression results. Default: true

        :stability: experimental
        '''
        props = _aws_cdk_aws_cloudwatch_ceddda9d.MetricOptions(
            account=account,
            color=color,
            dimensions_map=dimensions_map,
            id=id,
            label=label,
            period=period,
            region=region,
            stack_account=stack_account,
            stack_region=stack_region,
            statistic=statistic,
            unit=unit,
            visible=visible,
        )

        return typing.cast(_aws_cdk_aws_cloudwatch_ceddda9d.Metric, jsii.invoke(self, "metricMaxInstances", [props]))

    @jsii.member(jsii_name="metricMinInstances")
    def metric_min_instances(
        self,
        *,
        account: typing.Optional[builtins.str] = None,
        color: typing.Optional[builtins.str] = None,
        dimensions_map: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        id: typing.Optional[builtins.str] = None,
        label: typing.Optional[builtins.str] = None,
        period: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        region: typing.Optional[builtins.str] = None,
        stack_account: typing.Optional[builtins.str] = None,
        stack_region: typing.Optional[builtins.str] = None,
        statistic: typing.Optional[builtins.str] = None,
        unit: typing.Optional[_aws_cdk_aws_cloudwatch_ceddda9d.Unit] = None,
        visible: typing.Optional[builtins.bool] = None,
    ) -> _aws_cdk_aws_cloudwatch_ceddda9d.Metric:
        '''(experimental) Minimum number of instances allowed for the fleet.

        A fleet's instance minimum determines the capacity floor during manual or automatic scaling down.
        This metric is not available when viewing data for fleet metric groups.

        :param account: Account which this metric comes from. Default: - Deployment account.
        :param color: The hex color code, prefixed with '#' (e.g. '#00ff00'), to use when this metric is rendered on a graph. The ``Color`` class has a set of standard colors that can be used here. Default: - Automatic color
        :param dimensions_map: Dimensions of the metric. Default: - No dimensions.
        :param id: Unique identifier for this metric when used in dashboard widgets. The id can be used as a variable to represent this metric in math expressions. Valid characters are letters, numbers, and underscore. The first character must be a lowercase letter. Default: - No ID
        :param label: Label for this metric when added to a Graph in a Dashboard. You can use `dynamic labels <https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/graph-dynamic-labels.html>`_ to show summary information about the entire displayed time series in the legend. For example, if you use:: [max: ${MAX}] MyMetric As the metric label, the maximum value in the visible range will be shown next to the time series name in the graph's legend. Default: - No label
        :param period: The period over which the specified statistic is applied. Default: Duration.minutes(5)
        :param region: Region which this metric comes from. Default: - Deployment region.
        :param stack_account: Account of the stack this metric is attached to. Default: - Deployment account.
        :param stack_region: Region of the stack this metric is attached to. Default: - Deployment region.
        :param statistic: What function to use for aggregating. Use the ``aws_cloudwatch.Stats`` helper class to construct valid input strings. Can be one of the following: - "Minimum" | "min" - "Maximum" | "max" - "Average" | "avg" - "Sum" | "sum" - "SampleCount | "n" - "pNN.NN" - "tmNN.NN" | "tm(NN.NN%:NN.NN%)" - "iqm" - "wmNN.NN" | "wm(NN.NN%:NN.NN%)" - "tcNN.NN" | "tc(NN.NN%:NN.NN%)" - "tsNN.NN" | "ts(NN.NN%:NN.NN%)" Default: Average
        :param unit: Unit used to filter the metric stream. Only refer to datums emitted to the metric stream with the given unit and ignore all others. Only useful when datums are being emitted to the same metric stream under different units. The default is to use all matric datums in the stream, regardless of unit, which is recommended in nearly all cases. CloudWatch does not honor this property for graphs. Default: - All metric datums in the given metric stream
        :param visible: Whether this metric should be visible in dashboard graphs. Setting this to false is useful when you want to hide raw metrics that are used in math expressions, and show only the expression results. Default: true

        :stability: experimental
        '''
        props = _aws_cdk_aws_cloudwatch_ceddda9d.MetricOptions(
            account=account,
            color=color,
            dimensions_map=dimensions_map,
            id=id,
            label=label,
            period=period,
            region=region,
            stack_account=stack_account,
            stack_region=stack_region,
            statistic=statistic,
            unit=unit,
            visible=visible,
        )

        return typing.cast(_aws_cdk_aws_cloudwatch_ceddda9d.Metric, jsii.invoke(self, "metricMinInstances", [props]))

    @jsii.member(jsii_name="metricPercentIdleInstances")
    def metric_percent_idle_instances(
        self,
        *,
        account: typing.Optional[builtins.str] = None,
        color: typing.Optional[builtins.str] = None,
        dimensions_map: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        id: typing.Optional[builtins.str] = None,
        label: typing.Optional[builtins.str] = None,
        period: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        region: typing.Optional[builtins.str] = None,
        stack_account: typing.Optional[builtins.str] = None,
        stack_region: typing.Optional[builtins.str] = None,
        statistic: typing.Optional[builtins.str] = None,
        unit: typing.Optional[_aws_cdk_aws_cloudwatch_ceddda9d.Unit] = None,
        visible: typing.Optional[builtins.bool] = None,
    ) -> _aws_cdk_aws_cloudwatch_ceddda9d.Metric:
        '''(experimental) Percentage of all active instances that are idle (calculated as IdleInstances / ActiveInstances).

        This metric can be used for automatic scaling.

        :param account: Account which this metric comes from. Default: - Deployment account.
        :param color: The hex color code, prefixed with '#' (e.g. '#00ff00'), to use when this metric is rendered on a graph. The ``Color`` class has a set of standard colors that can be used here. Default: - Automatic color
        :param dimensions_map: Dimensions of the metric. Default: - No dimensions.
        :param id: Unique identifier for this metric when used in dashboard widgets. The id can be used as a variable to represent this metric in math expressions. Valid characters are letters, numbers, and underscore. The first character must be a lowercase letter. Default: - No ID
        :param label: Label for this metric when added to a Graph in a Dashboard. You can use `dynamic labels <https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/graph-dynamic-labels.html>`_ to show summary information about the entire displayed time series in the legend. For example, if you use:: [max: ${MAX}] MyMetric As the metric label, the maximum value in the visible range will be shown next to the time series name in the graph's legend. Default: - No label
        :param period: The period over which the specified statistic is applied. Default: Duration.minutes(5)
        :param region: Region which this metric comes from. Default: - Deployment region.
        :param stack_account: Account of the stack this metric is attached to. Default: - Deployment account.
        :param stack_region: Region of the stack this metric is attached to. Default: - Deployment region.
        :param statistic: What function to use for aggregating. Use the ``aws_cloudwatch.Stats`` helper class to construct valid input strings. Can be one of the following: - "Minimum" | "min" - "Maximum" | "max" - "Average" | "avg" - "Sum" | "sum" - "SampleCount | "n" - "pNN.NN" - "tmNN.NN" | "tm(NN.NN%:NN.NN%)" - "iqm" - "wmNN.NN" | "wm(NN.NN%:NN.NN%)" - "tcNN.NN" | "tc(NN.NN%:NN.NN%)" - "tsNN.NN" | "ts(NN.NN%:NN.NN%)" Default: Average
        :param unit: Unit used to filter the metric stream. Only refer to datums emitted to the metric stream with the given unit and ignore all others. Only useful when datums are being emitted to the same metric stream under different units. The default is to use all matric datums in the stream, regardless of unit, which is recommended in nearly all cases. CloudWatch does not honor this property for graphs. Default: - All metric datums in the given metric stream
        :param visible: Whether this metric should be visible in dashboard graphs. Setting this to false is useful when you want to hide raw metrics that are used in math expressions, and show only the expression results. Default: true

        :stability: experimental
        '''
        props = _aws_cdk_aws_cloudwatch_ceddda9d.MetricOptions(
            account=account,
            color=color,
            dimensions_map=dimensions_map,
            id=id,
            label=label,
            period=period,
            region=region,
            stack_account=stack_account,
            stack_region=stack_region,
            statistic=statistic,
            unit=unit,
            visible=visible,
        )

        return typing.cast(_aws_cdk_aws_cloudwatch_ceddda9d.Metric, jsii.invoke(self, "metricPercentIdleInstances", [props]))

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, IFleet).__jsii_proxy_class__ = lambda : _IFleetProxy


class MatchmakingRuleSet(
    MatchmakingRuleSetBase,
    metaclass=jsii.JSIIMeta,
    jsii_type="@aws-cdk/aws-gamelift-alpha.MatchmakingRuleSet",
):
    '''(experimental) Creates a new rule set for FlexMatch matchmaking.

    The rule set determines the two key elements of a match: your game's team structure and size, and how to group players together for the best possible match.

    For example, a rule set might describe a match like this:

    - Create a match with two teams of five players each, one team is the defenders and the other team the invaders.
    - A team can have novice and experienced players, but the average skill of the two teams must be within 10 points of each other.
    - If no match is made after 30 seconds, gradually relax the skill requirements.

    Rule sets must be defined in the same Region as the matchmaking configuration they are used with.

    :see: https://docs.aws.amazon.com/gamelift/latest/flexmatchguide/match-rulesets.html
    :stability: experimental
    :resource: AWS::GameLift::MatchmakingRuleSet
    :exampleMetadata: infused

    Example::

        gamelift.MatchmakingRuleSet(self, "RuleSet",
            matchmaking_rule_set_name="my-test-ruleset",
            content=gamelift.RuleSetContent.from_json_file(path.join(__dirname, "my-ruleset", "ruleset.json"))
        )
    '''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        content: RuleSetContent,
        matchmaking_rule_set_name: builtins.str,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param content: (experimental) A collection of matchmaking rules.
        :param matchmaking_rule_set_name: (experimental) A unique identifier for the matchmaking rule set. A matchmaking configuration identifies the rule set it uses by this name value. Note: the rule set name is different from the optional name field in the rule set body

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__976a3d8da3a70f4711298272591e84622378f07d7fbaf21a6fb79e1fcfacf9b2)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = MatchmakingRuleSetProps(
            content=content, matchmaking_rule_set_name=matchmaking_rule_set_name
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @jsii.member(jsii_name="fromMatchmakingRuleSetArn")
    @builtins.classmethod
    def from_matchmaking_rule_set_arn(
        cls,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        matchmaking_rule_set_arn: builtins.str,
    ) -> IMatchmakingRuleSet:
        '''(experimental) Import a ruleSet into CDK using its ARN.

        :param scope: -
        :param id: -
        :param matchmaking_rule_set_arn: -

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0efb57a36d82aae0aa58424e2aa02c3da7bb454a52b9347fa7515556f78db182)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument matchmaking_rule_set_arn", value=matchmaking_rule_set_arn, expected_type=type_hints["matchmaking_rule_set_arn"])
        return typing.cast(IMatchmakingRuleSet, jsii.sinvoke(cls, "fromMatchmakingRuleSetArn", [scope, id, matchmaking_rule_set_arn]))

    @jsii.member(jsii_name="fromMatchmakingRuleSetAttributes")
    @builtins.classmethod
    def from_matchmaking_rule_set_attributes(
        cls,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        matchmaking_rule_set_arn: typing.Optional[builtins.str] = None,
        matchmaking_rule_set_name: typing.Optional[builtins.str] = None,
    ) -> IMatchmakingRuleSet:
        '''(experimental) Import an existing matchmaking ruleSet from its attributes.

        :param scope: -
        :param id: -
        :param matchmaking_rule_set_arn: (experimental) The ARN of the matchmaking ruleSet. At least one of ``matchmakingRuleSetArn`` and ``matchmakingRuleSetName`` must be provided. Default: derived from ``matchmakingRuleSetName``.
        :param matchmaking_rule_set_name: (experimental) The unique name of the matchmaking ruleSet. At least one of ``ruleSetName`` and ``matchmakingRuleSetArn`` must be provided. Default: derived from ``matchmakingRuleSetArn``.

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4d23589bc2e008c65b6ea37647f8ca40b5ade669c71958c8ed3911847448a599)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        attrs = MatchmakingRuleSetAttributes(
            matchmaking_rule_set_arn=matchmaking_rule_set_arn,
            matchmaking_rule_set_name=matchmaking_rule_set_name,
        )

        return typing.cast(IMatchmakingRuleSet, jsii.sinvoke(cls, "fromMatchmakingRuleSetAttributes", [scope, id, attrs]))

    @jsii.member(jsii_name="fromMatchmakingRuleSetName")
    @builtins.classmethod
    def from_matchmaking_rule_set_name(
        cls,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        matchmaking_rule_set_name: builtins.str,
    ) -> IMatchmakingRuleSet:
        '''(experimental) Import a ruleSet into CDK using its name.

        :param scope: -
        :param id: -
        :param matchmaking_rule_set_name: -

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f9d54d5a829bb4319b6cd93eb55df3f25163baefad677da868c368ff06ab685d)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument matchmaking_rule_set_name", value=matchmaking_rule_set_name, expected_type=type_hints["matchmaking_rule_set_name"])
        return typing.cast(IMatchmakingRuleSet, jsii.sinvoke(cls, "fromMatchmakingRuleSetName", [scope, id, matchmaking_rule_set_name]))

    @jsii.python.classproperty
    @jsii.member(jsii_name="PROPERTY_INJECTION_ID")
    def PROPERTY_INJECTION_ID(cls) -> builtins.str:
        '''(experimental) Uniquely identifies this class.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "PROPERTY_INJECTION_ID"))

    @builtins.property
    @jsii.member(jsii_name="matchmakingRuleSetArn")
    def matchmaking_rule_set_arn(self) -> builtins.str:
        '''(experimental) The ARN of the ruleSet.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "matchmakingRuleSetArn"))

    @builtins.property
    @jsii.member(jsii_name="matchmakingRuleSetName")
    def matchmaking_rule_set_name(self) -> builtins.str:
        '''(experimental) The unique name of the ruleSet.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "matchmakingRuleSetName"))


class Script(
    ScriptBase,
    metaclass=jsii.JSIIMeta,
    jsii_type="@aws-cdk/aws-gamelift-alpha.Script",
):
    '''(experimental) A GameLift script, that is installed and runs on instances in an Amazon GameLift fleet.

    It consists of
    a zip file with all of the components of the realtime game server script.

    :see: https://docs.aws.amazon.com/gamelift/latest/developerguide/realtime-script-uploading.html
    :stability: experimental
    :resource: AWS::GameLift::Script
    :exampleMetadata: infused

    Example::

        # bucket: s3.Bucket
        
        gamelift.Script(self, "Script",
            content=gamelift.Content.from_bucket(bucket, "sample-asset-key")
        )
    '''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        content: Content,
        role: typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole] = None,
        script_name: typing.Optional[builtins.str] = None,
        script_version: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param content: (experimental) The game content.
        :param role: (experimental) The IAM role assumed by GameLift to access server script in S3. If providing a custom role, it needs to trust the GameLift service principal (gamelift.amazonaws.com) and be granted sufficient permissions to have Read access to a specific key content into a specific S3 bucket. Below an example of required permission: { "Version": "2012-10-17", "Statement": [{ "Effect": "Allow", "Action": [ "s3:GetObject", "s3:GetObjectVersion" ], "Resource": "arn:aws:s3:::bucket-name/object-name" }] } Default: - a role will be created with default permissions.
        :param script_name: (experimental) Name of this realtime server script. Default: No name
        :param script_version: (experimental) Version of this realtime server script. Default: No version

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b53a94d5041878dcde1f2700a726c30606268bb050cc9ba15de1b5d415318799)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = ScriptProps(
            content=content,
            role=role,
            script_name=script_name,
            script_version=script_version,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @jsii.member(jsii_name="fromAsset")
    @builtins.classmethod
    def from_asset(
        cls,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        path: builtins.str,
        *,
        deploy_time: typing.Optional[builtins.bool] = None,
        display_name: typing.Optional[builtins.str] = None,
        readers: typing.Optional[typing.Sequence[_aws_cdk_aws_iam_ceddda9d.IGrantable]] = None,
        source_kms_key: typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey] = None,
        asset_hash: typing.Optional[builtins.str] = None,
        asset_hash_type: typing.Optional[_aws_cdk_ceddda9d.AssetHashType] = None,
        bundling: typing.Optional[typing.Union[_aws_cdk_ceddda9d.BundlingOptions, typing.Dict[builtins.str, typing.Any]]] = None,
        exclude: typing.Optional[typing.Sequence[builtins.str]] = None,
        follow_symlinks: typing.Optional[_aws_cdk_ceddda9d.SymlinkFollowMode] = None,
        ignore_mode: typing.Optional[_aws_cdk_ceddda9d.IgnoreMode] = None,
    ) -> "Script":
        '''(experimental) Create a new realtime server script from asset content.

        :param scope: -
        :param id: -
        :param path: -
        :param deploy_time: Whether or not the asset needs to exist beyond deployment time; i.e. are copied over to a different location and not needed afterwards. Setting this property to true has an impact on the lifecycle of the asset, because we will assume that it is safe to delete after the CloudFormation deployment succeeds. For example, Lambda Function assets are copied over to Lambda during deployment. Therefore, it is not necessary to store the asset in S3, so we consider those deployTime assets. Default: false
        :param display_name: A display name for this asset. If supplied, the display name will be used in locations where the asset identifier is printed, like in the CLI progress information. If the same asset is added multiple times, the display name of the first occurrence is used. The default is the construct path of the Asset construct, with respect to the enclosing stack. If the asset is produced by a construct helper function (such as ``lambda.Code.fromAsset()``), this will look like ``MyFunction/Code``. We use the stack-relative construct path so that in the common case where you have multiple stacks with the same asset, we won't show something like ``/MyBetaStack/MyFunction/Code`` when you are actually deploying to production. Default: - Stack-relative construct path
        :param readers: A list of principals that should be able to read this asset from S3. You can use ``asset.grantRead(principal)`` to grant read permissions later. Default: - No principals that can read file asset.
        :param source_kms_key: The ARN of the KMS key used to encrypt the handler code. Default: - the default server-side encryption with Amazon S3 managed keys(SSE-S3) key will be used.
        :param asset_hash: Specify a custom hash for this asset. If ``assetHashType`` is set it must be set to ``AssetHashType.CUSTOM``. For consistency, this custom hash will be SHA256 hashed and encoded as hex. The resulting hash will be the asset hash. NOTE: the hash is used in order to identify a specific revision of the asset, and used for optimizing and caching deployment activities related to this asset such as packaging, uploading to Amazon S3, etc. If you chose to customize the hash, you will need to make sure it is updated every time the asset changes, or otherwise it is possible that some deployments will not be invalidated. Default: - based on ``assetHashType``
        :param asset_hash_type: Specifies the type of hash to calculate for this asset. If ``assetHash`` is configured, this option must be ``undefined`` or ``AssetHashType.CUSTOM``. Default: - the default is ``AssetHashType.SOURCE``, but if ``assetHash`` is explicitly specified this value defaults to ``AssetHashType.CUSTOM``.
        :param bundling: Bundle the asset by executing a command in a Docker container or a custom bundling provider. The asset path will be mounted at ``/asset-input``. The Docker container is responsible for putting content at ``/asset-output``. The content at ``/asset-output`` will be zipped and used as the final asset. Default: - uploaded as-is to S3 if the asset is a regular file or a .zip file, archived into a .zip file and uploaded to S3 otherwise
        :param exclude: File paths matching the patterns will be excluded. See ``ignoreMode`` to set the matching behavior. Has no effect on Assets bundled using the ``bundling`` property. Default: - nothing is excluded
        :param follow_symlinks: A strategy for how to handle symlinks. Default: SymlinkFollowMode.NEVER
        :param ignore_mode: The ignore behavior to use for ``exclude`` patterns. Default: IgnoreMode.GLOB

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__40705d5b1c0b3bdd28986e8a7f2c3187b99a079dc8c141894e5c2433835a68b1)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument path", value=path, expected_type=type_hints["path"])
        options = _aws_cdk_aws_s3_assets_ceddda9d.AssetOptions(
            deploy_time=deploy_time,
            display_name=display_name,
            readers=readers,
            source_kms_key=source_kms_key,
            asset_hash=asset_hash,
            asset_hash_type=asset_hash_type,
            bundling=bundling,
            exclude=exclude,
            follow_symlinks=follow_symlinks,
            ignore_mode=ignore_mode,
        )

        return typing.cast("Script", jsii.sinvoke(cls, "fromAsset", [scope, id, path, options]))

    @jsii.member(jsii_name="fromBucket")
    @builtins.classmethod
    def from_bucket(
        cls,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        bucket: _aws_cdk_aws_s3_ceddda9d.IBucket,
        key: builtins.str,
        object_version: typing.Optional[builtins.str] = None,
    ) -> "Script":
        '''(experimental) Create a new realtime server script from s3 content.

        :param scope: -
        :param id: -
        :param bucket: -
        :param key: -
        :param object_version: -

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d5fad313b14cfd67ea966c82bc187e0369c39b196ac64da5bdb241506aba4cd7)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument bucket", value=bucket, expected_type=type_hints["bucket"])
            check_type(argname="argument key", value=key, expected_type=type_hints["key"])
            check_type(argname="argument object_version", value=object_version, expected_type=type_hints["object_version"])
        return typing.cast("Script", jsii.sinvoke(cls, "fromBucket", [scope, id, bucket, key, object_version]))

    @jsii.member(jsii_name="fromScriptArn")
    @builtins.classmethod
    def from_script_arn(
        cls,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        script_arn: builtins.str,
    ) -> IScript:
        '''(experimental) Import a script into CDK using its ARN.

        :param scope: -
        :param id: -
        :param script_arn: -

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__bbdad5d39daf44e1fc3fa531ba2a75151b8c39459e79b65f5329ae4f58c76e4d)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument script_arn", value=script_arn, expected_type=type_hints["script_arn"])
        return typing.cast(IScript, jsii.sinvoke(cls, "fromScriptArn", [scope, id, script_arn]))

    @jsii.member(jsii_name="fromScriptAttributes")
    @builtins.classmethod
    def from_script_attributes(
        cls,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        script_arn: builtins.str,
        role: typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole] = None,
    ) -> IScript:
        '''(experimental) Import an existing realtime server script from its attributes.

        :param scope: -
        :param id: -
        :param script_arn: (experimental) The ARN of the realtime server script.
        :param role: (experimental) The IAM role assumed by GameLift to access server script in S3. Default: - undefined

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8942c32bd63e56f52bb6f580411825e7de3dfdb217dffa2eea170b0b146590ee)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        attrs = ScriptAttributes(script_arn=script_arn, role=role)

        return typing.cast(IScript, jsii.sinvoke(cls, "fromScriptAttributes", [scope, id, attrs]))

    @jsii.python.classproperty
    @jsii.member(jsii_name="PROPERTY_INJECTION_ID")
    def PROPERTY_INJECTION_ID(cls) -> builtins.str:
        '''(experimental) Uniquely identifies this class.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "PROPERTY_INJECTION_ID"))

    @builtins.property
    @jsii.member(jsii_name="grantPrincipal")
    def grant_principal(self) -> _aws_cdk_aws_iam_ceddda9d.IPrincipal:
        '''(experimental) The principal this GameLift script is using.

        :stability: experimental
        '''
        return typing.cast(_aws_cdk_aws_iam_ceddda9d.IPrincipal, jsii.get(self, "grantPrincipal"))

    @builtins.property
    @jsii.member(jsii_name="role")
    def role(self) -> _aws_cdk_aws_iam_ceddda9d.IRole:
        '''(experimental) The IAM role GameLift assumes to acccess server script content.

        :stability: experimental
        '''
        return typing.cast(_aws_cdk_aws_iam_ceddda9d.IRole, jsii.get(self, "role"))

    @builtins.property
    @jsii.member(jsii_name="scriptArn")
    def script_arn(self) -> builtins.str:
        '''(experimental) The ARN of the realtime server script.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "scriptArn"))

    @builtins.property
    @jsii.member(jsii_name="scriptId")
    def script_id(self) -> builtins.str:
        '''(experimental) The Identifier of the realtime server script.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "scriptId"))


@jsii.implements(IAlias)
class AliasBase(
    _aws_cdk_ceddda9d.Resource,
    metaclass=jsii.JSIIAbstractClass,
    jsii_type="@aws-cdk/aws-gamelift-alpha.AliasBase",
):
    '''(experimental) Base class for new and imported GameLift Alias.

    :stability: experimental
    '''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        account: typing.Optional[builtins.str] = None,
        environment_from_arn: typing.Optional[builtins.str] = None,
        physical_name: typing.Optional[builtins.str] = None,
        region: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param account: The AWS account ID this resource belongs to. Default: - the resource is in the same account as the stack it belongs to
        :param environment_from_arn: ARN to deduce region and account from. The ARN is parsed and the account and region are taken from the ARN. This should be used for imported resources. Cannot be supplied together with either ``account`` or ``region``. Default: - take environment from ``account``, ``region`` parameters, or use Stack environment.
        :param physical_name: The value passed in by users to the physical name prop of the resource. - ``undefined`` implies that a physical name will be allocated by CloudFormation during deployment. - a concrete value implies a specific physical name - ``PhysicalName.GENERATE_IF_NEEDED`` is a marker that indicates that a physical will only be generated by the CDK if it is needed for cross-environment references. Otherwise, it will be allocated by CloudFormation. Default: - The physical name will be allocated by CloudFormation at deployment time
        :param region: The AWS region this resource belongs to. Default: - the resource is in the same region as the stack it belongs to
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9ce95dded50fb4717285d87b394ed4234fe5244a5daae844cabcdff69627cb85)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = _aws_cdk_ceddda9d.ResourceProps(
            account=account,
            environment_from_arn=environment_from_arn,
            physical_name=physical_name,
            region=region,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @builtins.property
    @jsii.member(jsii_name="aliasArn")
    @abc.abstractmethod
    def alias_arn(self) -> builtins.str:
        '''(experimental) The ARN of the alias.

        :stability: experimental
        '''
        ...

    @builtins.property
    @jsii.member(jsii_name="aliasId")
    @abc.abstractmethod
    def alias_id(self) -> builtins.str:
        '''(experimental) The Identifier of the alias.

        :stability: experimental
        '''
        ...

    @builtins.property
    @jsii.member(jsii_name="resourceArnForDestination")
    def resource_arn_for_destination(self) -> builtins.str:
        '''(experimental) The ARN to put into the destination field of a game session queue.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "resourceArnForDestination"))


class _AliasBaseProxy(
    AliasBase,
    jsii.proxy_for(_aws_cdk_ceddda9d.Resource), # type: ignore[misc]
):
    @builtins.property
    @jsii.member(jsii_name="aliasArn")
    def alias_arn(self) -> builtins.str:
        '''(experimental) The ARN of the alias.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "aliasArn"))

    @builtins.property
    @jsii.member(jsii_name="aliasId")
    def alias_id(self) -> builtins.str:
        '''(experimental) The Identifier of the alias.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "aliasId"))

# Adding a "__jsii_proxy_class__(): typing.Type" function to the abstract class
typing.cast(typing.Any, AliasBase).__jsii_proxy_class__ = lambda : _AliasBaseProxy


class Build(
    BuildBase,
    metaclass=jsii.JSIIMeta,
    jsii_type="@aws-cdk/aws-gamelift-alpha.Build",
):
    '''(experimental) A GameLift build, that is installed and runs on instances in an Amazon GameLift fleet.

    It consists of
    a zip file with all of the components of the game server build.

    :see: https://docs.aws.amazon.com/gamelift/latest/developerguide/gamelift-build-cli-uploading.html
    :stability: experimental
    :resource: AWS::GameLift::Build
    :exampleMetadata: infused

    Example::

        # bucket: s3.Bucket
        
        build = gamelift.Build(self, "Build",
            content=gamelift.Content.from_bucket(bucket, "sample-asset-key")
        )
        
        CfnOutput(self, "BuildArn", value=build.build_arn)
        CfnOutput(self, "BuildId", value=build.build_id)
    '''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        content: Content,
        build_name: typing.Optional[builtins.str] = None,
        build_version: typing.Optional[builtins.str] = None,
        operating_system: typing.Optional[OperatingSystem] = None,
        role: typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole] = None,
        server_sdk_version: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param content: (experimental) The game build file storage.
        :param build_name: (experimental) Name of this build. Default: No name
        :param build_version: (experimental) Version of this build. Default: No version
        :param operating_system: (experimental) The operating system that the game server binaries are built to run on. Default: No version
        :param role: (experimental) The IAM role assumed by GameLift to access server build in S3. If providing a custom role, it needs to trust the GameLift service principal (gamelift.amazonaws.com) and be granted sufficient permissions to have Read access to a specific key content into a specific S3 bucket. Below an example of required permission: { "Version": "2012-10-17", "Statement": [{ "Effect": "Allow", "Action": [ "s3:GetObject", "s3:GetObjectVersion" ], "Resource": "arn:aws:s3:::bucket-name/object-name" }] } Default: - a role will be created with default permissions.
        :param server_sdk_version: (experimental) A server SDK version you used when integrating your game server build with Amazon GameLift. Default: - 4.0.2

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__acab12658d9c6cd950e90d4b6112c4156ce8e10d9afc5c09ec7bb623f57d07c2)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = BuildProps(
            content=content,
            build_name=build_name,
            build_version=build_version,
            operating_system=operating_system,
            role=role,
            server_sdk_version=server_sdk_version,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @jsii.member(jsii_name="fromAsset")
    @builtins.classmethod
    def from_asset(
        cls,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        path: builtins.str,
        *,
        deploy_time: typing.Optional[builtins.bool] = None,
        display_name: typing.Optional[builtins.str] = None,
        readers: typing.Optional[typing.Sequence[_aws_cdk_aws_iam_ceddda9d.IGrantable]] = None,
        source_kms_key: typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey] = None,
        asset_hash: typing.Optional[builtins.str] = None,
        asset_hash_type: typing.Optional[_aws_cdk_ceddda9d.AssetHashType] = None,
        bundling: typing.Optional[typing.Union[_aws_cdk_ceddda9d.BundlingOptions, typing.Dict[builtins.str, typing.Any]]] = None,
        exclude: typing.Optional[typing.Sequence[builtins.str]] = None,
        follow_symlinks: typing.Optional[_aws_cdk_ceddda9d.SymlinkFollowMode] = None,
        ignore_mode: typing.Optional[_aws_cdk_ceddda9d.IgnoreMode] = None,
    ) -> "Build":
        '''(experimental) Create a new Build from asset content.

        :param scope: -
        :param id: -
        :param path: -
        :param deploy_time: Whether or not the asset needs to exist beyond deployment time; i.e. are copied over to a different location and not needed afterwards. Setting this property to true has an impact on the lifecycle of the asset, because we will assume that it is safe to delete after the CloudFormation deployment succeeds. For example, Lambda Function assets are copied over to Lambda during deployment. Therefore, it is not necessary to store the asset in S3, so we consider those deployTime assets. Default: false
        :param display_name: A display name for this asset. If supplied, the display name will be used in locations where the asset identifier is printed, like in the CLI progress information. If the same asset is added multiple times, the display name of the first occurrence is used. The default is the construct path of the Asset construct, with respect to the enclosing stack. If the asset is produced by a construct helper function (such as ``lambda.Code.fromAsset()``), this will look like ``MyFunction/Code``. We use the stack-relative construct path so that in the common case where you have multiple stacks with the same asset, we won't show something like ``/MyBetaStack/MyFunction/Code`` when you are actually deploying to production. Default: - Stack-relative construct path
        :param readers: A list of principals that should be able to read this asset from S3. You can use ``asset.grantRead(principal)`` to grant read permissions later. Default: - No principals that can read file asset.
        :param source_kms_key: The ARN of the KMS key used to encrypt the handler code. Default: - the default server-side encryption with Amazon S3 managed keys(SSE-S3) key will be used.
        :param asset_hash: Specify a custom hash for this asset. If ``assetHashType`` is set it must be set to ``AssetHashType.CUSTOM``. For consistency, this custom hash will be SHA256 hashed and encoded as hex. The resulting hash will be the asset hash. NOTE: the hash is used in order to identify a specific revision of the asset, and used for optimizing and caching deployment activities related to this asset such as packaging, uploading to Amazon S3, etc. If you chose to customize the hash, you will need to make sure it is updated every time the asset changes, or otherwise it is possible that some deployments will not be invalidated. Default: - based on ``assetHashType``
        :param asset_hash_type: Specifies the type of hash to calculate for this asset. If ``assetHash`` is configured, this option must be ``undefined`` or ``AssetHashType.CUSTOM``. Default: - the default is ``AssetHashType.SOURCE``, but if ``assetHash`` is explicitly specified this value defaults to ``AssetHashType.CUSTOM``.
        :param bundling: Bundle the asset by executing a command in a Docker container or a custom bundling provider. The asset path will be mounted at ``/asset-input``. The Docker container is responsible for putting content at ``/asset-output``. The content at ``/asset-output`` will be zipped and used as the final asset. Default: - uploaded as-is to S3 if the asset is a regular file or a .zip file, archived into a .zip file and uploaded to S3 otherwise
        :param exclude: File paths matching the patterns will be excluded. See ``ignoreMode`` to set the matching behavior. Has no effect on Assets bundled using the ``bundling`` property. Default: - nothing is excluded
        :param follow_symlinks: A strategy for how to handle symlinks. Default: SymlinkFollowMode.NEVER
        :param ignore_mode: The ignore behavior to use for ``exclude`` patterns. Default: IgnoreMode.GLOB

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__771a5b67c3c157e54cfec46c95710a5920f03bde544ac928ed1f4eb24abfd610)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument path", value=path, expected_type=type_hints["path"])
        options = _aws_cdk_aws_s3_assets_ceddda9d.AssetOptions(
            deploy_time=deploy_time,
            display_name=display_name,
            readers=readers,
            source_kms_key=source_kms_key,
            asset_hash=asset_hash,
            asset_hash_type=asset_hash_type,
            bundling=bundling,
            exclude=exclude,
            follow_symlinks=follow_symlinks,
            ignore_mode=ignore_mode,
        )

        return typing.cast("Build", jsii.sinvoke(cls, "fromAsset", [scope, id, path, options]))

    @jsii.member(jsii_name="fromBucket")
    @builtins.classmethod
    def from_bucket(
        cls,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        bucket: _aws_cdk_aws_s3_ceddda9d.IBucket,
        key: builtins.str,
        object_version: typing.Optional[builtins.str] = None,
    ) -> "Build":
        '''(experimental) Create a new Build from s3 content.

        :param scope: -
        :param id: -
        :param bucket: -
        :param key: -
        :param object_version: -

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__01aa7b72ddb55b4e9c06c6216b9cff2482e318d6ad65b75aa6e4fa44e197f003)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument bucket", value=bucket, expected_type=type_hints["bucket"])
            check_type(argname="argument key", value=key, expected_type=type_hints["key"])
            check_type(argname="argument object_version", value=object_version, expected_type=type_hints["object_version"])
        return typing.cast("Build", jsii.sinvoke(cls, "fromBucket", [scope, id, bucket, key, object_version]))

    @jsii.member(jsii_name="fromBuildArn")
    @builtins.classmethod
    def from_build_arn(
        cls,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        build_arn: builtins.str,
    ) -> IBuild:
        '''(experimental) Import a build into CDK using its ARN.

        :param scope: -
        :param id: -
        :param build_arn: -

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__73ffb8bc096eeb5acc087de114546008b597c2f9769d8c1115e6b0f3472974c9)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument build_arn", value=build_arn, expected_type=type_hints["build_arn"])
        return typing.cast(IBuild, jsii.sinvoke(cls, "fromBuildArn", [scope, id, build_arn]))

    @jsii.member(jsii_name="fromBuildAttributes")
    @builtins.classmethod
    def from_build_attributes(
        cls,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        build_arn: typing.Optional[builtins.str] = None,
        build_id: typing.Optional[builtins.str] = None,
        role: typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole] = None,
    ) -> IBuild:
        '''(experimental) Import an existing build from its attributes.

        :param scope: -
        :param id: -
        :param build_arn: (experimental) The ARN of the build. At least one of ``buildArn`` and ``buildId`` must be provided. Default: derived from ``buildId``.
        :param build_id: (experimental) The identifier of the build. At least one of ``buildId`` and ``buildArn`` must be provided. Default: derived from ``buildArn``.
        :param role: (experimental) The IAM role assumed by GameLift to access server build in S3. Default: the imported fleet cannot be granted access to other resources as an ``iam.IGrantable``.

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f7d138525cf0c6ad71105d4422e4f3cd022412cb600abdd3c03e252467f7b478)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        attrs = BuildAttributes(build_arn=build_arn, build_id=build_id, role=role)

        return typing.cast(IBuild, jsii.sinvoke(cls, "fromBuildAttributes", [scope, id, attrs]))

    @jsii.member(jsii_name="fromBuildId")
    @builtins.classmethod
    def from_build_id(
        cls,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        build_id: builtins.str,
    ) -> IBuild:
        '''(experimental) Import a build into CDK using its identifier.

        :param scope: -
        :param id: -
        :param build_id: -

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__551e40ddeafd29db40fff59984f916c22299a859d987a82afa5e44182605017c)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument build_id", value=build_id, expected_type=type_hints["build_id"])
        return typing.cast(IBuild, jsii.sinvoke(cls, "fromBuildId", [scope, id, build_id]))

    @jsii.python.classproperty
    @jsii.member(jsii_name="PROPERTY_INJECTION_ID")
    def PROPERTY_INJECTION_ID(cls) -> builtins.str:
        '''(experimental) Uniquely identifies this class.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "PROPERTY_INJECTION_ID"))

    @builtins.property
    @jsii.member(jsii_name="buildArn")
    def build_arn(self) -> builtins.str:
        '''(experimental) The ARN of the build.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "buildArn"))

    @builtins.property
    @jsii.member(jsii_name="buildId")
    def build_id(self) -> builtins.str:
        '''(experimental) The Identifier of the build.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "buildId"))

    @builtins.property
    @jsii.member(jsii_name="grantPrincipal")
    def grant_principal(self) -> _aws_cdk_aws_iam_ceddda9d.IPrincipal:
        '''(experimental) The principal this GameLift Build is using.

        :stability: experimental
        '''
        return typing.cast(_aws_cdk_aws_iam_ceddda9d.IPrincipal, jsii.get(self, "grantPrincipal"))

    @builtins.property
    @jsii.member(jsii_name="role")
    def role(self) -> _aws_cdk_aws_iam_ceddda9d.IRole:
        '''(experimental) The IAM role GameLift assumes to acccess server build content.

        :stability: experimental
        '''
        return typing.cast(_aws_cdk_aws_iam_ceddda9d.IRole, jsii.get(self, "role"))


@jsii.implements(IFleet)
class FleetBase(
    _aws_cdk_ceddda9d.Resource,
    metaclass=jsii.JSIIAbstractClass,
    jsii_type="@aws-cdk/aws-gamelift-alpha.FleetBase",
):
    '''(experimental) Base class for new and imported GameLift fleet.

    :stability: experimental
    :exampleMetadata: fixture=_generated

    Example::

        # The code below shows an example of how to instantiate this type.
        # The values are placeholders you should change.
        import aws_cdk.aws_gamelift_alpha as gamelift_alpha
        from aws_cdk import aws_iam as iam
        
        # role: iam.Role
        
        fleet_base = gamelift_alpha.FleetBase.from_fleet_attributes(self, "MyFleetBase",
            fleet_arn="fleetArn",
            fleet_id="fleetId",
            role=role
        )
    '''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        account: typing.Optional[builtins.str] = None,
        environment_from_arn: typing.Optional[builtins.str] = None,
        physical_name: typing.Optional[builtins.str] = None,
        region: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param account: The AWS account ID this resource belongs to. Default: - the resource is in the same account as the stack it belongs to
        :param environment_from_arn: ARN to deduce region and account from. The ARN is parsed and the account and region are taken from the ARN. This should be used for imported resources. Cannot be supplied together with either ``account`` or ``region``. Default: - take environment from ``account``, ``region`` parameters, or use Stack environment.
        :param physical_name: The value passed in by users to the physical name prop of the resource. - ``undefined`` implies that a physical name will be allocated by CloudFormation during deployment. - a concrete value implies a specific physical name - ``PhysicalName.GENERATE_IF_NEEDED`` is a marker that indicates that a physical will only be generated by the CDK if it is needed for cross-environment references. Otherwise, it will be allocated by CloudFormation. Default: - The physical name will be allocated by CloudFormation at deployment time
        :param region: The AWS region this resource belongs to. Default: - the resource is in the same region as the stack it belongs to
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__12941e76da73d1fb0a8113ccb21bc7dcdf888b465317a85a82b38deabb69f666)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = _aws_cdk_ceddda9d.ResourceProps(
            account=account,
            environment_from_arn=environment_from_arn,
            physical_name=physical_name,
            region=region,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @jsii.member(jsii_name="fromFleetAttributes")
    @builtins.classmethod
    def from_fleet_attributes(
        cls,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        fleet_arn: typing.Optional[builtins.str] = None,
        fleet_id: typing.Optional[builtins.str] = None,
        role: typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole] = None,
    ) -> IFleet:
        '''(experimental) Import an existing fleet from its attributes.

        :param scope: -
        :param id: -
        :param fleet_arn: (experimental) The ARN of the fleet. At least one of ``fleetArn`` and ``fleetId`` must be provided. Default: derived from ``fleetId``.
        :param fleet_id: (experimental) The identifier of the fleet. At least one of ``fleetId`` and ``fleetArn`` must be provided. Default: derived from ``fleetArn``.
        :param role: (experimental) The IAM role assumed by GameLift fleet instances to access AWS ressources. Default: the imported fleet cannot be granted access to other resources as an ``iam.IGrantable``.

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__83ae99059a3f4b6d0eac7b382368760ade9295a9563b9f7ab96a3a3b11b363b8)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        attrs = FleetAttributes(fleet_arn=fleet_arn, fleet_id=fleet_id, role=role)

        return typing.cast(IFleet, jsii.sinvoke(cls, "fromFleetAttributes", [scope, id, attrs]))

    @jsii.member(jsii_name="addAlias")
    def add_alias(
        self,
        alias_name: builtins.str,
        *,
        description: typing.Optional[builtins.str] = None,
    ) -> "Alias":
        '''(experimental) Defines an alias for this fleet.

        Example::

           # fleet: gamelift.FleetBase


           fleet.add_alias("Live")

           # Is equivalent to

           gamelift.Alias(self, "AliasLive",
               alias_name="Live",
               fleet=fleet
           )

        :param alias_name: The name of the alias.
        :param description: (experimental) Description for the alias. Default: No description

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b00d5ccce3d0b3d9c2b51eae0baaeb059c52921521e42bf9c8d60d33da483fce)
            check_type(argname="argument alias_name", value=alias_name, expected_type=type_hints["alias_name"])
        options = AliasOptions(description=description)

        return typing.cast("Alias", jsii.invoke(self, "addAlias", [alias_name, options]))

    @jsii.member(jsii_name="addInternalLocation")
    def add_internal_location(
        self,
        *,
        region: builtins.str,
        capacity: typing.Optional[typing.Union[LocationCapacity, typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''(experimental) Adds a remote locations to deploy additional instances to and manage as part of the fleet.

        :param region: (experimental) An AWS Region code.
        :param capacity: (experimental) Current resource capacity settings in a specified fleet or location. The location value might refer to a fleet's remote location or its home Region. Default: no capacity settings on the specified location

        :stability: experimental
        '''
        location = Location(region=region, capacity=capacity)

        return typing.cast(None, jsii.invoke(self, "addInternalLocation", [location]))

    @jsii.member(jsii_name="addLocation")
    def add_location(
        self,
        region: builtins.str,
        desired_capacity: typing.Optional[jsii.Number] = None,
        min_size: typing.Optional[jsii.Number] = None,
        max_size: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''(experimental) Adds a remote locations to deploy additional instances to and manage as part of the fleet.

        :param region: The AWS region to add.
        :param desired_capacity: -
        :param min_size: -
        :param max_size: -

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e24f5b505687ec117a2611e69db366a71407d445998ae7af4fc53086225d78ec)
            check_type(argname="argument region", value=region, expected_type=type_hints["region"])
            check_type(argname="argument desired_capacity", value=desired_capacity, expected_type=type_hints["desired_capacity"])
            check_type(argname="argument min_size", value=min_size, expected_type=type_hints["min_size"])
            check_type(argname="argument max_size", value=max_size, expected_type=type_hints["max_size"])
        return typing.cast(None, jsii.invoke(self, "addLocation", [region, desired_capacity, min_size, max_size]))

    @jsii.member(jsii_name="grant")
    def grant(
        self,
        grantee: _aws_cdk_aws_iam_ceddda9d.IGrantable,
        *actions: builtins.str,
    ) -> _aws_cdk_aws_iam_ceddda9d.Grant:
        '''(experimental) Grant the ``grantee`` identity permissions to perform ``actions``.

        :param grantee: -
        :param actions: -

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1d7c1cafa704235e8c7c22f0babc5bcb076a129181d6569ac69e172e533f69c5)
            check_type(argname="argument grantee", value=grantee, expected_type=type_hints["grantee"])
            check_type(argname="argument actions", value=actions, expected_type=typing.Tuple[type_hints["actions"], ...]) # pyright: ignore [reportGeneralTypeIssues]
        return typing.cast(_aws_cdk_aws_iam_ceddda9d.Grant, jsii.invoke(self, "grant", [grantee, *actions]))

    @jsii.member(jsii_name="metric")
    def metric(
        self,
        metric_name: builtins.str,
        *,
        account: typing.Optional[builtins.str] = None,
        color: typing.Optional[builtins.str] = None,
        dimensions_map: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        id: typing.Optional[builtins.str] = None,
        label: typing.Optional[builtins.str] = None,
        period: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        region: typing.Optional[builtins.str] = None,
        stack_account: typing.Optional[builtins.str] = None,
        stack_region: typing.Optional[builtins.str] = None,
        statistic: typing.Optional[builtins.str] = None,
        unit: typing.Optional[_aws_cdk_aws_cloudwatch_ceddda9d.Unit] = None,
        visible: typing.Optional[builtins.bool] = None,
    ) -> _aws_cdk_aws_cloudwatch_ceddda9d.Metric:
        '''(experimental) Return the given named metric for this fleet.

        :param metric_name: -
        :param account: Account which this metric comes from. Default: - Deployment account.
        :param color: The hex color code, prefixed with '#' (e.g. '#00ff00'), to use when this metric is rendered on a graph. The ``Color`` class has a set of standard colors that can be used here. Default: - Automatic color
        :param dimensions_map: Dimensions of the metric. Default: - No dimensions.
        :param id: Unique identifier for this metric when used in dashboard widgets. The id can be used as a variable to represent this metric in math expressions. Valid characters are letters, numbers, and underscore. The first character must be a lowercase letter. Default: - No ID
        :param label: Label for this metric when added to a Graph in a Dashboard. You can use `dynamic labels <https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/graph-dynamic-labels.html>`_ to show summary information about the entire displayed time series in the legend. For example, if you use:: [max: ${MAX}] MyMetric As the metric label, the maximum value in the visible range will be shown next to the time series name in the graph's legend. Default: - No label
        :param period: The period over which the specified statistic is applied. Default: Duration.minutes(5)
        :param region: Region which this metric comes from. Default: - Deployment region.
        :param stack_account: Account of the stack this metric is attached to. Default: - Deployment account.
        :param stack_region: Region of the stack this metric is attached to. Default: - Deployment region.
        :param statistic: What function to use for aggregating. Use the ``aws_cloudwatch.Stats`` helper class to construct valid input strings. Can be one of the following: - "Minimum" | "min" - "Maximum" | "max" - "Average" | "avg" - "Sum" | "sum" - "SampleCount | "n" - "pNN.NN" - "tmNN.NN" | "tm(NN.NN%:NN.NN%)" - "iqm" - "wmNN.NN" | "wm(NN.NN%:NN.NN%)" - "tcNN.NN" | "tc(NN.NN%:NN.NN%)" - "tsNN.NN" | "ts(NN.NN%:NN.NN%)" Default: Average
        :param unit: Unit used to filter the metric stream. Only refer to datums emitted to the metric stream with the given unit and ignore all others. Only useful when datums are being emitted to the same metric stream under different units. The default is to use all matric datums in the stream, regardless of unit, which is recommended in nearly all cases. CloudWatch does not honor this property for graphs. Default: - All metric datums in the given metric stream
        :param visible: Whether this metric should be visible in dashboard graphs. Setting this to false is useful when you want to hide raw metrics that are used in math expressions, and show only the expression results. Default: true

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5bced8236ec32c93a595c407ba901878cc9d2256e8311b71c182205b0fb40a66)
            check_type(argname="argument metric_name", value=metric_name, expected_type=type_hints["metric_name"])
        props = _aws_cdk_aws_cloudwatch_ceddda9d.MetricOptions(
            account=account,
            color=color,
            dimensions_map=dimensions_map,
            id=id,
            label=label,
            period=period,
            region=region,
            stack_account=stack_account,
            stack_region=stack_region,
            statistic=statistic,
            unit=unit,
            visible=visible,
        )

        return typing.cast(_aws_cdk_aws_cloudwatch_ceddda9d.Metric, jsii.invoke(self, "metric", [metric_name, props]))

    @jsii.member(jsii_name="metricActiveInstances")
    def metric_active_instances(
        self,
        *,
        account: typing.Optional[builtins.str] = None,
        color: typing.Optional[builtins.str] = None,
        dimensions_map: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        id: typing.Optional[builtins.str] = None,
        label: typing.Optional[builtins.str] = None,
        period: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        region: typing.Optional[builtins.str] = None,
        stack_account: typing.Optional[builtins.str] = None,
        stack_region: typing.Optional[builtins.str] = None,
        statistic: typing.Optional[builtins.str] = None,
        unit: typing.Optional[_aws_cdk_aws_cloudwatch_ceddda9d.Unit] = None,
        visible: typing.Optional[builtins.bool] = None,
    ) -> _aws_cdk_aws_cloudwatch_ceddda9d.Metric:
        '''(experimental) Instances with ``ACTIVE`` status, which means they are running active server processes.

        The count includes idle instances and those that are hosting one or more game sessions.
        This metric measures current total instance capacity.

        This metric can be used with automatic scaling.

        :param account: Account which this metric comes from. Default: - Deployment account.
        :param color: The hex color code, prefixed with '#' (e.g. '#00ff00'), to use when this metric is rendered on a graph. The ``Color`` class has a set of standard colors that can be used here. Default: - Automatic color
        :param dimensions_map: Dimensions of the metric. Default: - No dimensions.
        :param id: Unique identifier for this metric when used in dashboard widgets. The id can be used as a variable to represent this metric in math expressions. Valid characters are letters, numbers, and underscore. The first character must be a lowercase letter. Default: - No ID
        :param label: Label for this metric when added to a Graph in a Dashboard. You can use `dynamic labels <https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/graph-dynamic-labels.html>`_ to show summary information about the entire displayed time series in the legend. For example, if you use:: [max: ${MAX}] MyMetric As the metric label, the maximum value in the visible range will be shown next to the time series name in the graph's legend. Default: - No label
        :param period: The period over which the specified statistic is applied. Default: Duration.minutes(5)
        :param region: Region which this metric comes from. Default: - Deployment region.
        :param stack_account: Account of the stack this metric is attached to. Default: - Deployment account.
        :param stack_region: Region of the stack this metric is attached to. Default: - Deployment region.
        :param statistic: What function to use for aggregating. Use the ``aws_cloudwatch.Stats`` helper class to construct valid input strings. Can be one of the following: - "Minimum" | "min" - "Maximum" | "max" - "Average" | "avg" - "Sum" | "sum" - "SampleCount | "n" - "pNN.NN" - "tmNN.NN" | "tm(NN.NN%:NN.NN%)" - "iqm" - "wmNN.NN" | "wm(NN.NN%:NN.NN%)" - "tcNN.NN" | "tc(NN.NN%:NN.NN%)" - "tsNN.NN" | "ts(NN.NN%:NN.NN%)" Default: Average
        :param unit: Unit used to filter the metric stream. Only refer to datums emitted to the metric stream with the given unit and ignore all others. Only useful when datums are being emitted to the same metric stream under different units. The default is to use all matric datums in the stream, regardless of unit, which is recommended in nearly all cases. CloudWatch does not honor this property for graphs. Default: - All metric datums in the given metric stream
        :param visible: Whether this metric should be visible in dashboard graphs. Setting this to false is useful when you want to hide raw metrics that are used in math expressions, and show only the expression results. Default: true

        :stability: experimental
        '''
        props = _aws_cdk_aws_cloudwatch_ceddda9d.MetricOptions(
            account=account,
            color=color,
            dimensions_map=dimensions_map,
            id=id,
            label=label,
            period=period,
            region=region,
            stack_account=stack_account,
            stack_region=stack_region,
            statistic=statistic,
            unit=unit,
            visible=visible,
        )

        return typing.cast(_aws_cdk_aws_cloudwatch_ceddda9d.Metric, jsii.invoke(self, "metricActiveInstances", [props]))

    @jsii.member(jsii_name="metricDesiredInstances")
    def metric_desired_instances(
        self,
        *,
        account: typing.Optional[builtins.str] = None,
        color: typing.Optional[builtins.str] = None,
        dimensions_map: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        id: typing.Optional[builtins.str] = None,
        label: typing.Optional[builtins.str] = None,
        period: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        region: typing.Optional[builtins.str] = None,
        stack_account: typing.Optional[builtins.str] = None,
        stack_region: typing.Optional[builtins.str] = None,
        statistic: typing.Optional[builtins.str] = None,
        unit: typing.Optional[_aws_cdk_aws_cloudwatch_ceddda9d.Unit] = None,
        visible: typing.Optional[builtins.bool] = None,
    ) -> _aws_cdk_aws_cloudwatch_ceddda9d.Metric:
        '''(experimental) Target number of active instances that GameLift is working to maintain in the fleet.

        With automatic scaling, this value is determined based on the scaling policies currently in force.
        Without automatic scaling, this value is set manually.
        This metric is not available when viewing data for fleet metric groups.

        :param account: Account which this metric comes from. Default: - Deployment account.
        :param color: The hex color code, prefixed with '#' (e.g. '#00ff00'), to use when this metric is rendered on a graph. The ``Color`` class has a set of standard colors that can be used here. Default: - Automatic color
        :param dimensions_map: Dimensions of the metric. Default: - No dimensions.
        :param id: Unique identifier for this metric when used in dashboard widgets. The id can be used as a variable to represent this metric in math expressions. Valid characters are letters, numbers, and underscore. The first character must be a lowercase letter. Default: - No ID
        :param label: Label for this metric when added to a Graph in a Dashboard. You can use `dynamic labels <https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/graph-dynamic-labels.html>`_ to show summary information about the entire displayed time series in the legend. For example, if you use:: [max: ${MAX}] MyMetric As the metric label, the maximum value in the visible range will be shown next to the time series name in the graph's legend. Default: - No label
        :param period: The period over which the specified statistic is applied. Default: Duration.minutes(5)
        :param region: Region which this metric comes from. Default: - Deployment region.
        :param stack_account: Account of the stack this metric is attached to. Default: - Deployment account.
        :param stack_region: Region of the stack this metric is attached to. Default: - Deployment region.
        :param statistic: What function to use for aggregating. Use the ``aws_cloudwatch.Stats`` helper class to construct valid input strings. Can be one of the following: - "Minimum" | "min" - "Maximum" | "max" - "Average" | "avg" - "Sum" | "sum" - "SampleCount | "n" - "pNN.NN" - "tmNN.NN" | "tm(NN.NN%:NN.NN%)" - "iqm" - "wmNN.NN" | "wm(NN.NN%:NN.NN%)" - "tcNN.NN" | "tc(NN.NN%:NN.NN%)" - "tsNN.NN" | "ts(NN.NN%:NN.NN%)" Default: Average
        :param unit: Unit used to filter the metric stream. Only refer to datums emitted to the metric stream with the given unit and ignore all others. Only useful when datums are being emitted to the same metric stream under different units. The default is to use all matric datums in the stream, regardless of unit, which is recommended in nearly all cases. CloudWatch does not honor this property for graphs. Default: - All metric datums in the given metric stream
        :param visible: Whether this metric should be visible in dashboard graphs. Setting this to false is useful when you want to hide raw metrics that are used in math expressions, and show only the expression results. Default: true

        :stability: experimental
        '''
        props = _aws_cdk_aws_cloudwatch_ceddda9d.MetricOptions(
            account=account,
            color=color,
            dimensions_map=dimensions_map,
            id=id,
            label=label,
            period=period,
            region=region,
            stack_account=stack_account,
            stack_region=stack_region,
            statistic=statistic,
            unit=unit,
            visible=visible,
        )

        return typing.cast(_aws_cdk_aws_cloudwatch_ceddda9d.Metric, jsii.invoke(self, "metricDesiredInstances", [props]))

    @jsii.member(jsii_name="metricIdleInstances")
    def metric_idle_instances(
        self,
        *,
        account: typing.Optional[builtins.str] = None,
        color: typing.Optional[builtins.str] = None,
        dimensions_map: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        id: typing.Optional[builtins.str] = None,
        label: typing.Optional[builtins.str] = None,
        period: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        region: typing.Optional[builtins.str] = None,
        stack_account: typing.Optional[builtins.str] = None,
        stack_region: typing.Optional[builtins.str] = None,
        statistic: typing.Optional[builtins.str] = None,
        unit: typing.Optional[_aws_cdk_aws_cloudwatch_ceddda9d.Unit] = None,
        visible: typing.Optional[builtins.bool] = None,
    ) -> _aws_cdk_aws_cloudwatch_ceddda9d.Metric:
        '''(experimental) Active instances that are currently hosting zero (0) game sessions.

        This metric measures capacity that is available but unused.
        This metric can be used with automatic scaling.

        :param account: Account which this metric comes from. Default: - Deployment account.
        :param color: The hex color code, prefixed with '#' (e.g. '#00ff00'), to use when this metric is rendered on a graph. The ``Color`` class has a set of standard colors that can be used here. Default: - Automatic color
        :param dimensions_map: Dimensions of the metric. Default: - No dimensions.
        :param id: Unique identifier for this metric when used in dashboard widgets. The id can be used as a variable to represent this metric in math expressions. Valid characters are letters, numbers, and underscore. The first character must be a lowercase letter. Default: - No ID
        :param label: Label for this metric when added to a Graph in a Dashboard. You can use `dynamic labels <https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/graph-dynamic-labels.html>`_ to show summary information about the entire displayed time series in the legend. For example, if you use:: [max: ${MAX}] MyMetric As the metric label, the maximum value in the visible range will be shown next to the time series name in the graph's legend. Default: - No label
        :param period: The period over which the specified statistic is applied. Default: Duration.minutes(5)
        :param region: Region which this metric comes from. Default: - Deployment region.
        :param stack_account: Account of the stack this metric is attached to. Default: - Deployment account.
        :param stack_region: Region of the stack this metric is attached to. Default: - Deployment region.
        :param statistic: What function to use for aggregating. Use the ``aws_cloudwatch.Stats`` helper class to construct valid input strings. Can be one of the following: - "Minimum" | "min" - "Maximum" | "max" - "Average" | "avg" - "Sum" | "sum" - "SampleCount | "n" - "pNN.NN" - "tmNN.NN" | "tm(NN.NN%:NN.NN%)" - "iqm" - "wmNN.NN" | "wm(NN.NN%:NN.NN%)" - "tcNN.NN" | "tc(NN.NN%:NN.NN%)" - "tsNN.NN" | "ts(NN.NN%:NN.NN%)" Default: Average
        :param unit: Unit used to filter the metric stream. Only refer to datums emitted to the metric stream with the given unit and ignore all others. Only useful when datums are being emitted to the same metric stream under different units. The default is to use all matric datums in the stream, regardless of unit, which is recommended in nearly all cases. CloudWatch does not honor this property for graphs. Default: - All metric datums in the given metric stream
        :param visible: Whether this metric should be visible in dashboard graphs. Setting this to false is useful when you want to hide raw metrics that are used in math expressions, and show only the expression results. Default: true

        :stability: experimental
        '''
        props = _aws_cdk_aws_cloudwatch_ceddda9d.MetricOptions(
            account=account,
            color=color,
            dimensions_map=dimensions_map,
            id=id,
            label=label,
            period=period,
            region=region,
            stack_account=stack_account,
            stack_region=stack_region,
            statistic=statistic,
            unit=unit,
            visible=visible,
        )

        return typing.cast(_aws_cdk_aws_cloudwatch_ceddda9d.Metric, jsii.invoke(self, "metricIdleInstances", [props]))

    @jsii.member(jsii_name="metricInstanceInterruptions")
    def metric_instance_interruptions(
        self,
        *,
        account: typing.Optional[builtins.str] = None,
        color: typing.Optional[builtins.str] = None,
        dimensions_map: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        id: typing.Optional[builtins.str] = None,
        label: typing.Optional[builtins.str] = None,
        period: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        region: typing.Optional[builtins.str] = None,
        stack_account: typing.Optional[builtins.str] = None,
        stack_region: typing.Optional[builtins.str] = None,
        statistic: typing.Optional[builtins.str] = None,
        unit: typing.Optional[_aws_cdk_aws_cloudwatch_ceddda9d.Unit] = None,
        visible: typing.Optional[builtins.bool] = None,
    ) -> _aws_cdk_aws_cloudwatch_ceddda9d.Metric:
        '''(experimental) Number of spot instances that have been interrupted.

        :param account: Account which this metric comes from. Default: - Deployment account.
        :param color: The hex color code, prefixed with '#' (e.g. '#00ff00'), to use when this metric is rendered on a graph. The ``Color`` class has a set of standard colors that can be used here. Default: - Automatic color
        :param dimensions_map: Dimensions of the metric. Default: - No dimensions.
        :param id: Unique identifier for this metric when used in dashboard widgets. The id can be used as a variable to represent this metric in math expressions. Valid characters are letters, numbers, and underscore. The first character must be a lowercase letter. Default: - No ID
        :param label: Label for this metric when added to a Graph in a Dashboard. You can use `dynamic labels <https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/graph-dynamic-labels.html>`_ to show summary information about the entire displayed time series in the legend. For example, if you use:: [max: ${MAX}] MyMetric As the metric label, the maximum value in the visible range will be shown next to the time series name in the graph's legend. Default: - No label
        :param period: The period over which the specified statistic is applied. Default: Duration.minutes(5)
        :param region: Region which this metric comes from. Default: - Deployment region.
        :param stack_account: Account of the stack this metric is attached to. Default: - Deployment account.
        :param stack_region: Region of the stack this metric is attached to. Default: - Deployment region.
        :param statistic: What function to use for aggregating. Use the ``aws_cloudwatch.Stats`` helper class to construct valid input strings. Can be one of the following: - "Minimum" | "min" - "Maximum" | "max" - "Average" | "avg" - "Sum" | "sum" - "SampleCount | "n" - "pNN.NN" - "tmNN.NN" | "tm(NN.NN%:NN.NN%)" - "iqm" - "wmNN.NN" | "wm(NN.NN%:NN.NN%)" - "tcNN.NN" | "tc(NN.NN%:NN.NN%)" - "tsNN.NN" | "ts(NN.NN%:NN.NN%)" Default: Average
        :param unit: Unit used to filter the metric stream. Only refer to datums emitted to the metric stream with the given unit and ignore all others. Only useful when datums are being emitted to the same metric stream under different units. The default is to use all matric datums in the stream, regardless of unit, which is recommended in nearly all cases. CloudWatch does not honor this property for graphs. Default: - All metric datums in the given metric stream
        :param visible: Whether this metric should be visible in dashboard graphs. Setting this to false is useful when you want to hide raw metrics that are used in math expressions, and show only the expression results. Default: true

        :stability: experimental
        '''
        props = _aws_cdk_aws_cloudwatch_ceddda9d.MetricOptions(
            account=account,
            color=color,
            dimensions_map=dimensions_map,
            id=id,
            label=label,
            period=period,
            region=region,
            stack_account=stack_account,
            stack_region=stack_region,
            statistic=statistic,
            unit=unit,
            visible=visible,
        )

        return typing.cast(_aws_cdk_aws_cloudwatch_ceddda9d.Metric, jsii.invoke(self, "metricInstanceInterruptions", [props]))

    @jsii.member(jsii_name="metricMaxInstances")
    def metric_max_instances(
        self,
        *,
        account: typing.Optional[builtins.str] = None,
        color: typing.Optional[builtins.str] = None,
        dimensions_map: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        id: typing.Optional[builtins.str] = None,
        label: typing.Optional[builtins.str] = None,
        period: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        region: typing.Optional[builtins.str] = None,
        stack_account: typing.Optional[builtins.str] = None,
        stack_region: typing.Optional[builtins.str] = None,
        statistic: typing.Optional[builtins.str] = None,
        unit: typing.Optional[_aws_cdk_aws_cloudwatch_ceddda9d.Unit] = None,
        visible: typing.Optional[builtins.bool] = None,
    ) -> _aws_cdk_aws_cloudwatch_ceddda9d.Metric:
        '''(experimental) Maximum number of instances that are allowed for the fleet.

        A fleet's instance maximum determines the capacity ceiling during manual or automatic scaling up.
        This metric is not available when viewing data for fleet metric groups.

        :param account: Account which this metric comes from. Default: - Deployment account.
        :param color: The hex color code, prefixed with '#' (e.g. '#00ff00'), to use when this metric is rendered on a graph. The ``Color`` class has a set of standard colors that can be used here. Default: - Automatic color
        :param dimensions_map: Dimensions of the metric. Default: - No dimensions.
        :param id: Unique identifier for this metric when used in dashboard widgets. The id can be used as a variable to represent this metric in math expressions. Valid characters are letters, numbers, and underscore. The first character must be a lowercase letter. Default: - No ID
        :param label: Label for this metric when added to a Graph in a Dashboard. You can use `dynamic labels <https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/graph-dynamic-labels.html>`_ to show summary information about the entire displayed time series in the legend. For example, if you use:: [max: ${MAX}] MyMetric As the metric label, the maximum value in the visible range will be shown next to the time series name in the graph's legend. Default: - No label
        :param period: The period over which the specified statistic is applied. Default: Duration.minutes(5)
        :param region: Region which this metric comes from. Default: - Deployment region.
        :param stack_account: Account of the stack this metric is attached to. Default: - Deployment account.
        :param stack_region: Region of the stack this metric is attached to. Default: - Deployment region.
        :param statistic: What function to use for aggregating. Use the ``aws_cloudwatch.Stats`` helper class to construct valid input strings. Can be one of the following: - "Minimum" | "min" - "Maximum" | "max" - "Average" | "avg" - "Sum" | "sum" - "SampleCount | "n" - "pNN.NN" - "tmNN.NN" | "tm(NN.NN%:NN.NN%)" - "iqm" - "wmNN.NN" | "wm(NN.NN%:NN.NN%)" - "tcNN.NN" | "tc(NN.NN%:NN.NN%)" - "tsNN.NN" | "ts(NN.NN%:NN.NN%)" Default: Average
        :param unit: Unit used to filter the metric stream. Only refer to datums emitted to the metric stream with the given unit and ignore all others. Only useful when datums are being emitted to the same metric stream under different units. The default is to use all matric datums in the stream, regardless of unit, which is recommended in nearly all cases. CloudWatch does not honor this property for graphs. Default: - All metric datums in the given metric stream
        :param visible: Whether this metric should be visible in dashboard graphs. Setting this to false is useful when you want to hide raw metrics that are used in math expressions, and show only the expression results. Default: true

        :stability: experimental
        '''
        props = _aws_cdk_aws_cloudwatch_ceddda9d.MetricOptions(
            account=account,
            color=color,
            dimensions_map=dimensions_map,
            id=id,
            label=label,
            period=period,
            region=region,
            stack_account=stack_account,
            stack_region=stack_region,
            statistic=statistic,
            unit=unit,
            visible=visible,
        )

        return typing.cast(_aws_cdk_aws_cloudwatch_ceddda9d.Metric, jsii.invoke(self, "metricMaxInstances", [props]))

    @jsii.member(jsii_name="metricMinInstances")
    def metric_min_instances(
        self,
        *,
        account: typing.Optional[builtins.str] = None,
        color: typing.Optional[builtins.str] = None,
        dimensions_map: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        id: typing.Optional[builtins.str] = None,
        label: typing.Optional[builtins.str] = None,
        period: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        region: typing.Optional[builtins.str] = None,
        stack_account: typing.Optional[builtins.str] = None,
        stack_region: typing.Optional[builtins.str] = None,
        statistic: typing.Optional[builtins.str] = None,
        unit: typing.Optional[_aws_cdk_aws_cloudwatch_ceddda9d.Unit] = None,
        visible: typing.Optional[builtins.bool] = None,
    ) -> _aws_cdk_aws_cloudwatch_ceddda9d.Metric:
        '''(experimental) Minimum number of instances allowed for the fleet.

        A fleet's instance minimum determines the capacity floor during manual or automatic scaling down.
        This metric is not available when viewing data for fleet metric groups.

        :param account: Account which this metric comes from. Default: - Deployment account.
        :param color: The hex color code, prefixed with '#' (e.g. '#00ff00'), to use when this metric is rendered on a graph. The ``Color`` class has a set of standard colors that can be used here. Default: - Automatic color
        :param dimensions_map: Dimensions of the metric. Default: - No dimensions.
        :param id: Unique identifier for this metric when used in dashboard widgets. The id can be used as a variable to represent this metric in math expressions. Valid characters are letters, numbers, and underscore. The first character must be a lowercase letter. Default: - No ID
        :param label: Label for this metric when added to a Graph in a Dashboard. You can use `dynamic labels <https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/graph-dynamic-labels.html>`_ to show summary information about the entire displayed time series in the legend. For example, if you use:: [max: ${MAX}] MyMetric As the metric label, the maximum value in the visible range will be shown next to the time series name in the graph's legend. Default: - No label
        :param period: The period over which the specified statistic is applied. Default: Duration.minutes(5)
        :param region: Region which this metric comes from. Default: - Deployment region.
        :param stack_account: Account of the stack this metric is attached to. Default: - Deployment account.
        :param stack_region: Region of the stack this metric is attached to. Default: - Deployment region.
        :param statistic: What function to use for aggregating. Use the ``aws_cloudwatch.Stats`` helper class to construct valid input strings. Can be one of the following: - "Minimum" | "min" - "Maximum" | "max" - "Average" | "avg" - "Sum" | "sum" - "SampleCount | "n" - "pNN.NN" - "tmNN.NN" | "tm(NN.NN%:NN.NN%)" - "iqm" - "wmNN.NN" | "wm(NN.NN%:NN.NN%)" - "tcNN.NN" | "tc(NN.NN%:NN.NN%)" - "tsNN.NN" | "ts(NN.NN%:NN.NN%)" Default: Average
        :param unit: Unit used to filter the metric stream. Only refer to datums emitted to the metric stream with the given unit and ignore all others. Only useful when datums are being emitted to the same metric stream under different units. The default is to use all matric datums in the stream, regardless of unit, which is recommended in nearly all cases. CloudWatch does not honor this property for graphs. Default: - All metric datums in the given metric stream
        :param visible: Whether this metric should be visible in dashboard graphs. Setting this to false is useful when you want to hide raw metrics that are used in math expressions, and show only the expression results. Default: true

        :stability: experimental
        '''
        props = _aws_cdk_aws_cloudwatch_ceddda9d.MetricOptions(
            account=account,
            color=color,
            dimensions_map=dimensions_map,
            id=id,
            label=label,
            period=period,
            region=region,
            stack_account=stack_account,
            stack_region=stack_region,
            statistic=statistic,
            unit=unit,
            visible=visible,
        )

        return typing.cast(_aws_cdk_aws_cloudwatch_ceddda9d.Metric, jsii.invoke(self, "metricMinInstances", [props]))

    @jsii.member(jsii_name="metricPercentIdleInstances")
    def metric_percent_idle_instances(
        self,
        *,
        account: typing.Optional[builtins.str] = None,
        color: typing.Optional[builtins.str] = None,
        dimensions_map: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        id: typing.Optional[builtins.str] = None,
        label: typing.Optional[builtins.str] = None,
        period: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        region: typing.Optional[builtins.str] = None,
        stack_account: typing.Optional[builtins.str] = None,
        stack_region: typing.Optional[builtins.str] = None,
        statistic: typing.Optional[builtins.str] = None,
        unit: typing.Optional[_aws_cdk_aws_cloudwatch_ceddda9d.Unit] = None,
        visible: typing.Optional[builtins.bool] = None,
    ) -> _aws_cdk_aws_cloudwatch_ceddda9d.Metric:
        '''(experimental) Percentage of all active instances that are idle (calculated as IdleInstances / ActiveInstances).

        This metric can be used for automatic scaling.

        :param account: Account which this metric comes from. Default: - Deployment account.
        :param color: The hex color code, prefixed with '#' (e.g. '#00ff00'), to use when this metric is rendered on a graph. The ``Color`` class has a set of standard colors that can be used here. Default: - Automatic color
        :param dimensions_map: Dimensions of the metric. Default: - No dimensions.
        :param id: Unique identifier for this metric when used in dashboard widgets. The id can be used as a variable to represent this metric in math expressions. Valid characters are letters, numbers, and underscore. The first character must be a lowercase letter. Default: - No ID
        :param label: Label for this metric when added to a Graph in a Dashboard. You can use `dynamic labels <https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/graph-dynamic-labels.html>`_ to show summary information about the entire displayed time series in the legend. For example, if you use:: [max: ${MAX}] MyMetric As the metric label, the maximum value in the visible range will be shown next to the time series name in the graph's legend. Default: - No label
        :param period: The period over which the specified statistic is applied. Default: Duration.minutes(5)
        :param region: Region which this metric comes from. Default: - Deployment region.
        :param stack_account: Account of the stack this metric is attached to. Default: - Deployment account.
        :param stack_region: Region of the stack this metric is attached to. Default: - Deployment region.
        :param statistic: What function to use for aggregating. Use the ``aws_cloudwatch.Stats`` helper class to construct valid input strings. Can be one of the following: - "Minimum" | "min" - "Maximum" | "max" - "Average" | "avg" - "Sum" | "sum" - "SampleCount | "n" - "pNN.NN" - "tmNN.NN" | "tm(NN.NN%:NN.NN%)" - "iqm" - "wmNN.NN" | "wm(NN.NN%:NN.NN%)" - "tcNN.NN" | "tc(NN.NN%:NN.NN%)" - "tsNN.NN" | "ts(NN.NN%:NN.NN%)" Default: Average
        :param unit: Unit used to filter the metric stream. Only refer to datums emitted to the metric stream with the given unit and ignore all others. Only useful when datums are being emitted to the same metric stream under different units. The default is to use all matric datums in the stream, regardless of unit, which is recommended in nearly all cases. CloudWatch does not honor this property for graphs. Default: - All metric datums in the given metric stream
        :param visible: Whether this metric should be visible in dashboard graphs. Setting this to false is useful when you want to hide raw metrics that are used in math expressions, and show only the expression results. Default: true

        :stability: experimental
        '''
        props = _aws_cdk_aws_cloudwatch_ceddda9d.MetricOptions(
            account=account,
            color=color,
            dimensions_map=dimensions_map,
            id=id,
            label=label,
            period=period,
            region=region,
            stack_account=stack_account,
            stack_region=stack_region,
            statistic=statistic,
            unit=unit,
            visible=visible,
        )

        return typing.cast(_aws_cdk_aws_cloudwatch_ceddda9d.Metric, jsii.invoke(self, "metricPercentIdleInstances", [props]))

    @jsii.member(jsii_name="parseLocationCapacity")
    def _parse_location_capacity(
        self,
        *,
        desired_capacity: typing.Optional[jsii.Number] = None,
        max_size: typing.Optional[jsii.Number] = None,
        min_size: typing.Optional[jsii.Number] = None,
    ) -> typing.Optional[_aws_cdk_aws_gamelift_ceddda9d.CfnFleet.LocationCapacityProperty]:
        '''
        :param desired_capacity: (experimental) The number of Amazon EC2 instances you want to maintain in the specified fleet location. This value must fall between the minimum and maximum size limits. Default: the default value is 0
        :param max_size: (experimental) The maximum number of instances that are allowed in the specified fleet location. Default: the default value is 1
        :param min_size: (experimental) The minimum number of instances that are allowed in the specified fleet location. Default: the default value is 0

        :stability: experimental
        '''
        capacity = LocationCapacity(
            desired_capacity=desired_capacity, max_size=max_size, min_size=min_size
        )

        return typing.cast(typing.Optional[_aws_cdk_aws_gamelift_ceddda9d.CfnFleet.LocationCapacityProperty], jsii.invoke(self, "parseLocationCapacity", [capacity]))

    @jsii.member(jsii_name="parseLocations")
    def _parse_locations(
        self,
    ) -> typing.Optional[typing.List[_aws_cdk_aws_gamelift_ceddda9d.CfnFleet.LocationConfigurationProperty]]:
        '''
        :stability: experimental
        '''
        return typing.cast(typing.Optional[typing.List[_aws_cdk_aws_gamelift_ceddda9d.CfnFleet.LocationConfigurationProperty]], jsii.invoke(self, "parseLocations", []))

    @jsii.member(jsii_name="parseResourceCreationLimitPolicy")
    def _parse_resource_creation_limit_policy(
        self,
        *,
        fleet_name: builtins.str,
        instance_type: _aws_cdk_aws_ec2_ceddda9d.InstanceType,
        runtime_configuration: typing.Union[RuntimeConfiguration, typing.Dict[builtins.str, typing.Any]],
        description: typing.Optional[builtins.str] = None,
        desired_capacity: typing.Optional[jsii.Number] = None,
        locations: typing.Optional[typing.Sequence[typing.Union[Location, typing.Dict[builtins.str, typing.Any]]]] = None,
        max_size: typing.Optional[jsii.Number] = None,
        metric_group: typing.Optional[builtins.str] = None,
        min_size: typing.Optional[jsii.Number] = None,
        peer_vpc: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IVpc] = None,
        protect_new_game_session: typing.Optional[builtins.bool] = None,
        resource_creation_limit_policy: typing.Optional[typing.Union[ResourceCreationLimitPolicy, typing.Dict[builtins.str, typing.Any]]] = None,
        role: typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole] = None,
        use_certificate: typing.Optional[builtins.bool] = None,
        use_spot: typing.Optional[builtins.bool] = None,
    ) -> typing.Optional[_aws_cdk_aws_gamelift_ceddda9d.CfnFleet.ResourceCreationLimitPolicyProperty]:
        '''
        :param fleet_name: (experimental) A descriptive label that is associated with a fleet. Fleet names do not need to be unique.
        :param instance_type: (experimental) The GameLift-supported Amazon EC2 instance type to use for all fleet instances. Instance type determines the computing resources that will be used to host your game servers, including CPU, memory, storage, and networking capacity.
        :param runtime_configuration: (experimental) A collection of server process configurations that describe the set of processes to run on each instance in a fleet. Server processes run either an executable in a custom game build or a Realtime Servers script. GameLift launches the configured processes, manages their life cycle, and replaces them as needed. Each instance checks regularly for an updated runtime configuration. A GameLift instance is limited to 50 processes running concurrently. To calculate the total number of processes in a runtime configuration, add the values of the ConcurrentExecutions parameter for each ServerProcess.
        :param description: (experimental) A human-readable description of the fleet. Default: no description is provided
        :param desired_capacity: (experimental) The number of EC2 instances that you want this fleet to host. When creating a new fleet, GameLift automatically sets this value to "1" and initiates a single instance. Once the fleet is active, update this value to trigger GameLift to add or remove instances from the fleet. Default: Default capacity is 0
        :param locations: (experimental) A set of remote locations to deploy additional instances to and manage as part of the fleet. This parameter can only be used when creating fleets in AWS Regions that support multiple locations. You can add any GameLift-supported AWS Region as a remote location, in the form of an AWS Region code such as ``us-west-2``. To create a fleet with instances in the home region only, omit this parameter. Default: Create a fleet with instances in the home region only
        :param max_size: (experimental) The maximum number of instances that are allowed in the specified fleet location. Default: the default is 1
        :param metric_group: (experimental) The name of an AWS CloudWatch metric group to add this fleet to. A metric group is used to aggregate the metrics for multiple fleets. You can specify an existing metric group name or set a new name to create a new metric group. A fleet can be included in only one metric group at a time. Default: Fleet metrics are aggregated with other fleets in the default metric group
        :param min_size: (experimental) The minimum number of instances that are allowed in the specified fleet location. Default: the default is 0
        :param peer_vpc: (experimental) A VPC peering connection between your GameLift-hosted game servers and your other non-GameLift resources. Use Amazon Virtual Private Cloud (VPC) peering connections to enable your game servers to communicate directly and privately with your other AWS resources, such as a web service or a repository. You can establish VPC peering with any resources that run on AWS and are managed by an AWS account that you have access to. The VPC must be in the same Region as your fleet. Warning: Be sure to create a VPC Peering authorization through Gamelift Service API. Default: no vpc peering
        :param protect_new_game_session: (experimental) The status of termination protection for active game sessions on the fleet. By default, new game sessions are protected and cannot be terminated during a scale-down event. Default: true - Game sessions in ``ACTIVE`` status cannot be terminated during a scale-down event.
        :param resource_creation_limit_policy: (experimental) A policy that limits the number of game sessions that an individual player can create on instances in this fleet within a specified span of time. Default: No resource creation limit policy
        :param role: (experimental) The IAM role assumed by GameLift fleet instances to access AWS ressources. With a role set, any application that runs on an instance in this fleet can assume the role, including install scripts, server processes, and daemons (background processes). If providing a custom role, it needs to trust the GameLift service principal (gamelift.amazonaws.com). No permission is required by default. This property cannot be changed after the fleet is created. Default: - a role will be created with default trust to Gamelift service principal.
        :param use_certificate: (experimental) Prompts GameLift to generate a TLS/SSL certificate for the fleet. GameLift uses the certificates to encrypt traffic between game clients and the game servers running on GameLift. You can't change this property after you create the fleet. Additionnal info: AWS Certificate Manager (ACM) certificates expire after 13 months. Certificate expiration can cause fleets to fail, preventing players from connecting to instances in the fleet. We recommend you replace fleets before 13 months, consider using fleet aliases for a smooth transition. Default: TLS/SSL certificate are generated for the fleet
        :param use_spot: (experimental) Indicates whether to use On-Demand or Spot instances for this fleet. By default, fleet use on demand capacity. This property cannot be changed after the fleet is created. Default: Gamelift fleet use on demand capacity

        :stability: experimental
        '''
        props = FleetProps(
            fleet_name=fleet_name,
            instance_type=instance_type,
            runtime_configuration=runtime_configuration,
            description=description,
            desired_capacity=desired_capacity,
            locations=locations,
            max_size=max_size,
            metric_group=metric_group,
            min_size=min_size,
            peer_vpc=peer_vpc,
            protect_new_game_session=protect_new_game_session,
            resource_creation_limit_policy=resource_creation_limit_policy,
            role=role,
            use_certificate=use_certificate,
            use_spot=use_spot,
        )

        return typing.cast(typing.Optional[_aws_cdk_aws_gamelift_ceddda9d.CfnFleet.ResourceCreationLimitPolicyProperty], jsii.invoke(self, "parseResourceCreationLimitPolicy", [props]))

    @jsii.member(jsii_name="parseRuntimeConfiguration")
    def _parse_runtime_configuration(
        self,
        *,
        fleet_name: builtins.str,
        instance_type: _aws_cdk_aws_ec2_ceddda9d.InstanceType,
        runtime_configuration: typing.Union[RuntimeConfiguration, typing.Dict[builtins.str, typing.Any]],
        description: typing.Optional[builtins.str] = None,
        desired_capacity: typing.Optional[jsii.Number] = None,
        locations: typing.Optional[typing.Sequence[typing.Union[Location, typing.Dict[builtins.str, typing.Any]]]] = None,
        max_size: typing.Optional[jsii.Number] = None,
        metric_group: typing.Optional[builtins.str] = None,
        min_size: typing.Optional[jsii.Number] = None,
        peer_vpc: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IVpc] = None,
        protect_new_game_session: typing.Optional[builtins.bool] = None,
        resource_creation_limit_policy: typing.Optional[typing.Union[ResourceCreationLimitPolicy, typing.Dict[builtins.str, typing.Any]]] = None,
        role: typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole] = None,
        use_certificate: typing.Optional[builtins.bool] = None,
        use_spot: typing.Optional[builtins.bool] = None,
    ) -> typing.Optional[_aws_cdk_aws_gamelift_ceddda9d.CfnFleet.RuntimeConfigurationProperty]:
        '''
        :param fleet_name: (experimental) A descriptive label that is associated with a fleet. Fleet names do not need to be unique.
        :param instance_type: (experimental) The GameLift-supported Amazon EC2 instance type to use for all fleet instances. Instance type determines the computing resources that will be used to host your game servers, including CPU, memory, storage, and networking capacity.
        :param runtime_configuration: (experimental) A collection of server process configurations that describe the set of processes to run on each instance in a fleet. Server processes run either an executable in a custom game build or a Realtime Servers script. GameLift launches the configured processes, manages their life cycle, and replaces them as needed. Each instance checks regularly for an updated runtime configuration. A GameLift instance is limited to 50 processes running concurrently. To calculate the total number of processes in a runtime configuration, add the values of the ConcurrentExecutions parameter for each ServerProcess.
        :param description: (experimental) A human-readable description of the fleet. Default: no description is provided
        :param desired_capacity: (experimental) The number of EC2 instances that you want this fleet to host. When creating a new fleet, GameLift automatically sets this value to "1" and initiates a single instance. Once the fleet is active, update this value to trigger GameLift to add or remove instances from the fleet. Default: Default capacity is 0
        :param locations: (experimental) A set of remote locations to deploy additional instances to and manage as part of the fleet. This parameter can only be used when creating fleets in AWS Regions that support multiple locations. You can add any GameLift-supported AWS Region as a remote location, in the form of an AWS Region code such as ``us-west-2``. To create a fleet with instances in the home region only, omit this parameter. Default: Create a fleet with instances in the home region only
        :param max_size: (experimental) The maximum number of instances that are allowed in the specified fleet location. Default: the default is 1
        :param metric_group: (experimental) The name of an AWS CloudWatch metric group to add this fleet to. A metric group is used to aggregate the metrics for multiple fleets. You can specify an existing metric group name or set a new name to create a new metric group. A fleet can be included in only one metric group at a time. Default: Fleet metrics are aggregated with other fleets in the default metric group
        :param min_size: (experimental) The minimum number of instances that are allowed in the specified fleet location. Default: the default is 0
        :param peer_vpc: (experimental) A VPC peering connection between your GameLift-hosted game servers and your other non-GameLift resources. Use Amazon Virtual Private Cloud (VPC) peering connections to enable your game servers to communicate directly and privately with your other AWS resources, such as a web service or a repository. You can establish VPC peering with any resources that run on AWS and are managed by an AWS account that you have access to. The VPC must be in the same Region as your fleet. Warning: Be sure to create a VPC Peering authorization through Gamelift Service API. Default: no vpc peering
        :param protect_new_game_session: (experimental) The status of termination protection for active game sessions on the fleet. By default, new game sessions are protected and cannot be terminated during a scale-down event. Default: true - Game sessions in ``ACTIVE`` status cannot be terminated during a scale-down event.
        :param resource_creation_limit_policy: (experimental) A policy that limits the number of game sessions that an individual player can create on instances in this fleet within a specified span of time. Default: No resource creation limit policy
        :param role: (experimental) The IAM role assumed by GameLift fleet instances to access AWS ressources. With a role set, any application that runs on an instance in this fleet can assume the role, including install scripts, server processes, and daemons (background processes). If providing a custom role, it needs to trust the GameLift service principal (gamelift.amazonaws.com). No permission is required by default. This property cannot be changed after the fleet is created. Default: - a role will be created with default trust to Gamelift service principal.
        :param use_certificate: (experimental) Prompts GameLift to generate a TLS/SSL certificate for the fleet. GameLift uses the certificates to encrypt traffic between game clients and the game servers running on GameLift. You can't change this property after you create the fleet. Additionnal info: AWS Certificate Manager (ACM) certificates expire after 13 months. Certificate expiration can cause fleets to fail, preventing players from connecting to instances in the fleet. We recommend you replace fleets before 13 months, consider using fleet aliases for a smooth transition. Default: TLS/SSL certificate are generated for the fleet
        :param use_spot: (experimental) Indicates whether to use On-Demand or Spot instances for this fleet. By default, fleet use on demand capacity. This property cannot be changed after the fleet is created. Default: Gamelift fleet use on demand capacity

        :stability: experimental
        '''
        props = FleetProps(
            fleet_name=fleet_name,
            instance_type=instance_type,
            runtime_configuration=runtime_configuration,
            description=description,
            desired_capacity=desired_capacity,
            locations=locations,
            max_size=max_size,
            metric_group=metric_group,
            min_size=min_size,
            peer_vpc=peer_vpc,
            protect_new_game_session=protect_new_game_session,
            resource_creation_limit_policy=resource_creation_limit_policy,
            role=role,
            use_certificate=use_certificate,
            use_spot=use_spot,
        )

        return typing.cast(typing.Optional[_aws_cdk_aws_gamelift_ceddda9d.CfnFleet.RuntimeConfigurationProperty], jsii.invoke(self, "parseRuntimeConfiguration", [props]))

    @jsii.member(jsii_name="warnVpcPeeringAuthorizations")
    def _warn_vpc_peering_authorizations(
        self,
        scope: _constructs_77d1e7e8.Construct,
    ) -> None:
        '''
        :param scope: -

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__68991ef0ce6784f9f286e5d071bc251c86b2b925331565c0ec03af23ef683754)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
        return typing.cast(None, jsii.invoke(self, "warnVpcPeeringAuthorizations", [scope]))

    @builtins.property
    @jsii.member(jsii_name="fleetArn")
    @abc.abstractmethod
    def fleet_arn(self) -> builtins.str:
        '''(experimental) The ARN of the fleet.

        :stability: experimental
        '''
        ...

    @builtins.property
    @jsii.member(jsii_name="fleetId")
    @abc.abstractmethod
    def fleet_id(self) -> builtins.str:
        '''(experimental) The Identifier of the fleet.

        :stability: experimental
        '''
        ...

    @builtins.property
    @jsii.member(jsii_name="grantPrincipal")
    @abc.abstractmethod
    def grant_principal(self) -> _aws_cdk_aws_iam_ceddda9d.IPrincipal:
        '''(experimental) The principal this GameLift fleet is using.

        :stability: experimental
        '''
        ...

    @builtins.property
    @jsii.member(jsii_name="resourceArnForDestination")
    def resource_arn_for_destination(self) -> builtins.str:
        '''(experimental) The ARN to put into the destination field of a game session queue.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "resourceArnForDestination"))


class _FleetBaseProxy(
    FleetBase,
    jsii.proxy_for(_aws_cdk_ceddda9d.Resource), # type: ignore[misc]
):
    @builtins.property
    @jsii.member(jsii_name="fleetArn")
    def fleet_arn(self) -> builtins.str:
        '''(experimental) The ARN of the fleet.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "fleetArn"))

    @builtins.property
    @jsii.member(jsii_name="fleetId")
    def fleet_id(self) -> builtins.str:
        '''(experimental) The Identifier of the fleet.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "fleetId"))

    @builtins.property
    @jsii.member(jsii_name="grantPrincipal")
    def grant_principal(self) -> _aws_cdk_aws_iam_ceddda9d.IPrincipal:
        '''(experimental) The principal this GameLift fleet is using.

        :stability: experimental
        '''
        return typing.cast(_aws_cdk_aws_iam_ceddda9d.IPrincipal, jsii.get(self, "grantPrincipal"))

# Adding a "__jsii_proxy_class__(): typing.Type" function to the abstract class
typing.cast(typing.Any, FleetBase).__jsii_proxy_class__ = lambda : _FleetBaseProxy


class GameServerGroup(
    GameServerGroupBase,
    metaclass=jsii.JSIIMeta,
    jsii_type="@aws-cdk/aws-gamelift-alpha.GameServerGroup",
):
    '''(experimental) Creates a GameLift FleetIQ game server group for managing game hosting on a collection of Amazon EC2 instances for game hosting.

    This operation creates the game server group, creates an Auto Scaling group in your AWS account, and establishes a link between the two groups.
    You can view the status of your game server groups in the GameLift console.
    Game server group metrics and events are emitted to Amazon CloudWatch.
    Before creating a new game server group, you must have the following:

    - An Amazon EC2 launch template that specifies how to launch Amazon EC2 instances with your game server build.
    - An IAM role that extends limited access to your AWS account to allow GameLift FleetIQ to create and interact with the Auto Scaling group.

    To create a new game server group, specify a unique group name, IAM role and Amazon EC2 launch template, and provide a list of instance types that can be used in the group.
    You must also set initial maximum and minimum limits on the group's instance count.
    You can optionally set an Auto Scaling policy with target tracking based on a GameLift FleetIQ metric.

    Once the game server group and corresponding Auto Scaling group are created, you have full access to change the Auto Scaling group's configuration as needed.
    Several properties that are set when creating a game server group, including maximum/minimum size and auto-scaling policy settings, must be updated directly in the Auto Scaling group.
    Keep in mind that some Auto Scaling group properties are periodically updated by GameLift FleetIQ as part of its balancing activities to optimize for availability and cost.

    :see: https://docs.aws.amazon.com/gamelift/latest/fleetiqguide/gsg-intro.html
    :stability: experimental
    :resource: AWS::GameLift::GameServerGroup
    :exampleMetadata: infused

    Example::

        # launch_template: ec2.ILaunchTemplate
        # vpc: ec2.IVpc
        
        
        gamelift.GameServerGroup(self, "GameServerGroup",
            game_server_group_name="sample-gameservergroup-name",
            instance_definitions=[gamelift.InstanceDefinition(
                instance_type=ec2.InstanceType.of(ec2.InstanceClass.C5, ec2.InstanceSize.LARGE)
            ), gamelift.InstanceDefinition(
                instance_type=ec2.InstanceType.of(ec2.InstanceClass.C4, ec2.InstanceSize.LARGE)
            )],
            launch_template=launch_template,
            vpc=vpc,
            vpc_subnets=ec2.SubnetSelection(subnet_type=ec2.SubnetType.PUBLIC)
        )
    '''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        game_server_group_name: builtins.str,
        instance_definitions: typing.Sequence[typing.Union[InstanceDefinition, typing.Dict[builtins.str, typing.Any]]],
        launch_template: _aws_cdk_aws_ec2_ceddda9d.ILaunchTemplate,
        vpc: _aws_cdk_aws_ec2_ceddda9d.IVpc,
        auto_scaling_policy: typing.Optional[typing.Union[AutoScalingPolicy, typing.Dict[builtins.str, typing.Any]]] = None,
        balancing_strategy: typing.Optional[BalancingStrategy] = None,
        delete_option: typing.Optional[DeleteOption] = None,
        max_size: typing.Optional[jsii.Number] = None,
        min_size: typing.Optional[jsii.Number] = None,
        protect_game_server: typing.Optional[builtins.bool] = None,
        role: typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole] = None,
        vpc_subnets: typing.Optional[typing.Union[_aws_cdk_aws_ec2_ceddda9d.SubnetSelection, typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param game_server_group_name: (experimental) A developer-defined identifier for the game server group. The name is unique for each Region in each AWS account.
        :param instance_definitions: (experimental) The set of Amazon EC2 instance types that GameLift FleetIQ can use when balancing and automatically scaling instances in the corresponding Auto Scaling group.
        :param launch_template: (experimental) The Amazon EC2 launch template that contains configuration settings and game server code to be deployed to all instances in the game server group. After the Auto Scaling group is created, update this value directly in the Auto Scaling group using the AWS console or APIs. NOTE: If you specify network interfaces in your launch template, you must explicitly set the property AssociatePublicIpAddress to ``true``. If no network interface is specified in the launch template, GameLift FleetIQ uses your account's default VPC.
        :param vpc: (experimental) The VPC network to place the game server group in. By default, all GameLift FleetIQ-supported Availability Zones are used. You can use this parameter to specify VPCs that you've set up. This property cannot be updated after the game server group is created, and the corresponding Auto Scaling group will always use the property value that is set with this request, even if the Auto Scaling group is updated directly.
        :param auto_scaling_policy: (experimental) Configuration settings to define a scaling policy for the Auto Scaling group that is optimized for game hosting. The scaling policy uses the metric ``PercentUtilizedGameServers`` to maintain a buffer of idle game servers that can immediately accommodate new games and players. After the Auto Scaling group is created, update this value directly in the Auto Scaling group using the AWS console or APIs. Default: no autoscaling policy settled
        :param balancing_strategy: (experimental) Indicates how GameLift FleetIQ balances the use of Spot Instances and On-Demand Instances in the game server group. Default: SPOT_PREFERRED
        :param delete_option: (experimental) The type of delete to perform. To delete a game server group, specify the DeleteOption Default: SAFE_DELETE
        :param max_size: (experimental) The maximum number of instances allowed in the Amazon EC2 Auto Scaling group. During automatic scaling events, GameLift FleetIQ and EC2 do not scale up the group above this maximum. After the Auto Scaling group is created, update this value directly in the Auto Scaling group using the AWS console or APIs. Default: the default is 1
        :param min_size: (experimental) The minimum number of instances allowed in the Amazon EC2 Auto Scaling group. During automatic scaling events, GameLift FleetIQ and Amazon EC2 do not scale down the group below this minimum. In production, this value should be set to at least 1. After the Auto Scaling group is created, update this value directly in the Auto Scaling group using the AWS console or APIs. Default: the default is 0
        :param protect_game_server: (experimental) A flag that indicates whether instances in the game server group are protected from early termination. Unprotected instances that have active game servers running might be terminated during a scale-down event, causing players to be dropped from the game. Protected instances cannot be terminated while there are active game servers running except in the event of a forced game server group deletion. An exception to this is with Spot Instances, which can be terminated by AWS regardless of protection status. Default: game servers running might be terminated during a scale-down event
        :param role: (experimental) The IAM role that allows Amazon GameLift to access your Amazon EC2 Auto Scaling groups. Default: - a role will be created with default trust to Gamelift and Autoscaling service principal with a default policy ``GameLiftGameServerGroupPolicy`` attached.
        :param vpc_subnets: (experimental) Game server group subnet selection. Default: all GameLift FleetIQ-supported Availability Zones are used.

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9d7010ffc2b4c1fb02cd1e07fe5bb1d68676dd11570fed2cd459c0505f8e45a8)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = GameServerGroupProps(
            game_server_group_name=game_server_group_name,
            instance_definitions=instance_definitions,
            launch_template=launch_template,
            vpc=vpc,
            auto_scaling_policy=auto_scaling_policy,
            balancing_strategy=balancing_strategy,
            delete_option=delete_option,
            max_size=max_size,
            min_size=min_size,
            protect_game_server=protect_game_server,
            role=role,
            vpc_subnets=vpc_subnets,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @jsii.member(jsii_name="fromGameServerGroupAttributes")
    @builtins.classmethod
    def from_game_server_group_attributes(
        cls,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        auto_scaling_group_arn: builtins.str,
        game_server_group_arn: typing.Optional[builtins.str] = None,
        game_server_group_name: typing.Optional[builtins.str] = None,
        role: typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole] = None,
    ) -> IGameServerGroup:
        '''(experimental) Import an existing game server group from its attributes.

        :param scope: -
        :param id: -
        :param auto_scaling_group_arn: (experimental) The ARN of the generated AutoScaling group. Default: the imported game server group does not have autoscaling group information
        :param game_server_group_arn: (experimental) The ARN of the game server group. At least one of ``gameServerGroupArn`` and ``gameServerGroupName`` must be provided. Default: derived from ``gameServerGroupName``.
        :param game_server_group_name: (experimental) The name of the game server group. At least one of ``gameServerGroupArn`` and ``gameServerGroupName`` must be provided. Default: derived from ``gameServerGroupArn``.
        :param role: (experimental) The IAM role that allows Amazon GameLift to access your Amazon EC2 Auto Scaling groups. Default: the imported game server group cannot be granted access to other resources as an ``iam.IGrantable``.

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__48d603aa779f14f81d3db2b3cd7ae4a0ff5b9261c16733151a59f20ac6a829e0)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        attrs = GameServerGroupAttributes(
            auto_scaling_group_arn=auto_scaling_group_arn,
            game_server_group_arn=game_server_group_arn,
            game_server_group_name=game_server_group_name,
            role=role,
        )

        return typing.cast(IGameServerGroup, jsii.sinvoke(cls, "fromGameServerGroupAttributes", [scope, id, attrs]))

    @jsii.member(jsii_name="parseAutoScalingPolicy")
    def _parse_auto_scaling_policy(
        self,
        *,
        game_server_group_name: builtins.str,
        instance_definitions: typing.Sequence[typing.Union[InstanceDefinition, typing.Dict[builtins.str, typing.Any]]],
        launch_template: _aws_cdk_aws_ec2_ceddda9d.ILaunchTemplate,
        vpc: _aws_cdk_aws_ec2_ceddda9d.IVpc,
        auto_scaling_policy: typing.Optional[typing.Union[AutoScalingPolicy, typing.Dict[builtins.str, typing.Any]]] = None,
        balancing_strategy: typing.Optional[BalancingStrategy] = None,
        delete_option: typing.Optional[DeleteOption] = None,
        max_size: typing.Optional[jsii.Number] = None,
        min_size: typing.Optional[jsii.Number] = None,
        protect_game_server: typing.Optional[builtins.bool] = None,
        role: typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole] = None,
        vpc_subnets: typing.Optional[typing.Union[_aws_cdk_aws_ec2_ceddda9d.SubnetSelection, typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> typing.Optional[_aws_cdk_aws_gamelift_ceddda9d.CfnGameServerGroup.AutoScalingPolicyProperty]:
        '''
        :param game_server_group_name: (experimental) A developer-defined identifier for the game server group. The name is unique for each Region in each AWS account.
        :param instance_definitions: (experimental) The set of Amazon EC2 instance types that GameLift FleetIQ can use when balancing and automatically scaling instances in the corresponding Auto Scaling group.
        :param launch_template: (experimental) The Amazon EC2 launch template that contains configuration settings and game server code to be deployed to all instances in the game server group. After the Auto Scaling group is created, update this value directly in the Auto Scaling group using the AWS console or APIs. NOTE: If you specify network interfaces in your launch template, you must explicitly set the property AssociatePublicIpAddress to ``true``. If no network interface is specified in the launch template, GameLift FleetIQ uses your account's default VPC.
        :param vpc: (experimental) The VPC network to place the game server group in. By default, all GameLift FleetIQ-supported Availability Zones are used. You can use this parameter to specify VPCs that you've set up. This property cannot be updated after the game server group is created, and the corresponding Auto Scaling group will always use the property value that is set with this request, even if the Auto Scaling group is updated directly.
        :param auto_scaling_policy: (experimental) Configuration settings to define a scaling policy for the Auto Scaling group that is optimized for game hosting. The scaling policy uses the metric ``PercentUtilizedGameServers`` to maintain a buffer of idle game servers that can immediately accommodate new games and players. After the Auto Scaling group is created, update this value directly in the Auto Scaling group using the AWS console or APIs. Default: no autoscaling policy settled
        :param balancing_strategy: (experimental) Indicates how GameLift FleetIQ balances the use of Spot Instances and On-Demand Instances in the game server group. Default: SPOT_PREFERRED
        :param delete_option: (experimental) The type of delete to perform. To delete a game server group, specify the DeleteOption Default: SAFE_DELETE
        :param max_size: (experimental) The maximum number of instances allowed in the Amazon EC2 Auto Scaling group. During automatic scaling events, GameLift FleetIQ and EC2 do not scale up the group above this maximum. After the Auto Scaling group is created, update this value directly in the Auto Scaling group using the AWS console or APIs. Default: the default is 1
        :param min_size: (experimental) The minimum number of instances allowed in the Amazon EC2 Auto Scaling group. During automatic scaling events, GameLift FleetIQ and Amazon EC2 do not scale down the group below this minimum. In production, this value should be set to at least 1. After the Auto Scaling group is created, update this value directly in the Auto Scaling group using the AWS console or APIs. Default: the default is 0
        :param protect_game_server: (experimental) A flag that indicates whether instances in the game server group are protected from early termination. Unprotected instances that have active game servers running might be terminated during a scale-down event, causing players to be dropped from the game. Protected instances cannot be terminated while there are active game servers running except in the event of a forced game server group deletion. An exception to this is with Spot Instances, which can be terminated by AWS regardless of protection status. Default: game servers running might be terminated during a scale-down event
        :param role: (experimental) The IAM role that allows Amazon GameLift to access your Amazon EC2 Auto Scaling groups. Default: - a role will be created with default trust to Gamelift and Autoscaling service principal with a default policy ``GameLiftGameServerGroupPolicy`` attached.
        :param vpc_subnets: (experimental) Game server group subnet selection. Default: all GameLift FleetIQ-supported Availability Zones are used.

        :stability: experimental
        '''
        props = GameServerGroupProps(
            game_server_group_name=game_server_group_name,
            instance_definitions=instance_definitions,
            launch_template=launch_template,
            vpc=vpc,
            auto_scaling_policy=auto_scaling_policy,
            balancing_strategy=balancing_strategy,
            delete_option=delete_option,
            max_size=max_size,
            min_size=min_size,
            protect_game_server=protect_game_server,
            role=role,
            vpc_subnets=vpc_subnets,
        )

        return typing.cast(typing.Optional[_aws_cdk_aws_gamelift_ceddda9d.CfnGameServerGroup.AutoScalingPolicyProperty], jsii.invoke(self, "parseAutoScalingPolicy", [props]))

    @jsii.member(jsii_name="parseInstanceDefinitions")
    def _parse_instance_definitions(
        self,
        *,
        game_server_group_name: builtins.str,
        instance_definitions: typing.Sequence[typing.Union[InstanceDefinition, typing.Dict[builtins.str, typing.Any]]],
        launch_template: _aws_cdk_aws_ec2_ceddda9d.ILaunchTemplate,
        vpc: _aws_cdk_aws_ec2_ceddda9d.IVpc,
        auto_scaling_policy: typing.Optional[typing.Union[AutoScalingPolicy, typing.Dict[builtins.str, typing.Any]]] = None,
        balancing_strategy: typing.Optional[BalancingStrategy] = None,
        delete_option: typing.Optional[DeleteOption] = None,
        max_size: typing.Optional[jsii.Number] = None,
        min_size: typing.Optional[jsii.Number] = None,
        protect_game_server: typing.Optional[builtins.bool] = None,
        role: typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole] = None,
        vpc_subnets: typing.Optional[typing.Union[_aws_cdk_aws_ec2_ceddda9d.SubnetSelection, typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> typing.List[_aws_cdk_aws_gamelift_ceddda9d.CfnGameServerGroup.InstanceDefinitionProperty]:
        '''
        :param game_server_group_name: (experimental) A developer-defined identifier for the game server group. The name is unique for each Region in each AWS account.
        :param instance_definitions: (experimental) The set of Amazon EC2 instance types that GameLift FleetIQ can use when balancing and automatically scaling instances in the corresponding Auto Scaling group.
        :param launch_template: (experimental) The Amazon EC2 launch template that contains configuration settings and game server code to be deployed to all instances in the game server group. After the Auto Scaling group is created, update this value directly in the Auto Scaling group using the AWS console or APIs. NOTE: If you specify network interfaces in your launch template, you must explicitly set the property AssociatePublicIpAddress to ``true``. If no network interface is specified in the launch template, GameLift FleetIQ uses your account's default VPC.
        :param vpc: (experimental) The VPC network to place the game server group in. By default, all GameLift FleetIQ-supported Availability Zones are used. You can use this parameter to specify VPCs that you've set up. This property cannot be updated after the game server group is created, and the corresponding Auto Scaling group will always use the property value that is set with this request, even if the Auto Scaling group is updated directly.
        :param auto_scaling_policy: (experimental) Configuration settings to define a scaling policy for the Auto Scaling group that is optimized for game hosting. The scaling policy uses the metric ``PercentUtilizedGameServers`` to maintain a buffer of idle game servers that can immediately accommodate new games and players. After the Auto Scaling group is created, update this value directly in the Auto Scaling group using the AWS console or APIs. Default: no autoscaling policy settled
        :param balancing_strategy: (experimental) Indicates how GameLift FleetIQ balances the use of Spot Instances and On-Demand Instances in the game server group. Default: SPOT_PREFERRED
        :param delete_option: (experimental) The type of delete to perform. To delete a game server group, specify the DeleteOption Default: SAFE_DELETE
        :param max_size: (experimental) The maximum number of instances allowed in the Amazon EC2 Auto Scaling group. During automatic scaling events, GameLift FleetIQ and EC2 do not scale up the group above this maximum. After the Auto Scaling group is created, update this value directly in the Auto Scaling group using the AWS console or APIs. Default: the default is 1
        :param min_size: (experimental) The minimum number of instances allowed in the Amazon EC2 Auto Scaling group. During automatic scaling events, GameLift FleetIQ and Amazon EC2 do not scale down the group below this minimum. In production, this value should be set to at least 1. After the Auto Scaling group is created, update this value directly in the Auto Scaling group using the AWS console or APIs. Default: the default is 0
        :param protect_game_server: (experimental) A flag that indicates whether instances in the game server group are protected from early termination. Unprotected instances that have active game servers running might be terminated during a scale-down event, causing players to be dropped from the game. Protected instances cannot be terminated while there are active game servers running except in the event of a forced game server group deletion. An exception to this is with Spot Instances, which can be terminated by AWS regardless of protection status. Default: game servers running might be terminated during a scale-down event
        :param role: (experimental) The IAM role that allows Amazon GameLift to access your Amazon EC2 Auto Scaling groups. Default: - a role will be created with default trust to Gamelift and Autoscaling service principal with a default policy ``GameLiftGameServerGroupPolicy`` attached.
        :param vpc_subnets: (experimental) Game server group subnet selection. Default: all GameLift FleetIQ-supported Availability Zones are used.

        :stability: experimental
        '''
        props = GameServerGroupProps(
            game_server_group_name=game_server_group_name,
            instance_definitions=instance_definitions,
            launch_template=launch_template,
            vpc=vpc,
            auto_scaling_policy=auto_scaling_policy,
            balancing_strategy=balancing_strategy,
            delete_option=delete_option,
            max_size=max_size,
            min_size=min_size,
            protect_game_server=protect_game_server,
            role=role,
            vpc_subnets=vpc_subnets,
        )

        return typing.cast(typing.List[_aws_cdk_aws_gamelift_ceddda9d.CfnGameServerGroup.InstanceDefinitionProperty], jsii.invoke(self, "parseInstanceDefinitions", [props]))

    @jsii.member(jsii_name="parseLaunchTemplate")
    def _parse_launch_template(
        self,
        *,
        game_server_group_name: builtins.str,
        instance_definitions: typing.Sequence[typing.Union[InstanceDefinition, typing.Dict[builtins.str, typing.Any]]],
        launch_template: _aws_cdk_aws_ec2_ceddda9d.ILaunchTemplate,
        vpc: _aws_cdk_aws_ec2_ceddda9d.IVpc,
        auto_scaling_policy: typing.Optional[typing.Union[AutoScalingPolicy, typing.Dict[builtins.str, typing.Any]]] = None,
        balancing_strategy: typing.Optional[BalancingStrategy] = None,
        delete_option: typing.Optional[DeleteOption] = None,
        max_size: typing.Optional[jsii.Number] = None,
        min_size: typing.Optional[jsii.Number] = None,
        protect_game_server: typing.Optional[builtins.bool] = None,
        role: typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole] = None,
        vpc_subnets: typing.Optional[typing.Union[_aws_cdk_aws_ec2_ceddda9d.SubnetSelection, typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> _aws_cdk_aws_gamelift_ceddda9d.CfnGameServerGroup.LaunchTemplateProperty:
        '''
        :param game_server_group_name: (experimental) A developer-defined identifier for the game server group. The name is unique for each Region in each AWS account.
        :param instance_definitions: (experimental) The set of Amazon EC2 instance types that GameLift FleetIQ can use when balancing and automatically scaling instances in the corresponding Auto Scaling group.
        :param launch_template: (experimental) The Amazon EC2 launch template that contains configuration settings and game server code to be deployed to all instances in the game server group. After the Auto Scaling group is created, update this value directly in the Auto Scaling group using the AWS console or APIs. NOTE: If you specify network interfaces in your launch template, you must explicitly set the property AssociatePublicIpAddress to ``true``. If no network interface is specified in the launch template, GameLift FleetIQ uses your account's default VPC.
        :param vpc: (experimental) The VPC network to place the game server group in. By default, all GameLift FleetIQ-supported Availability Zones are used. You can use this parameter to specify VPCs that you've set up. This property cannot be updated after the game server group is created, and the corresponding Auto Scaling group will always use the property value that is set with this request, even if the Auto Scaling group is updated directly.
        :param auto_scaling_policy: (experimental) Configuration settings to define a scaling policy for the Auto Scaling group that is optimized for game hosting. The scaling policy uses the metric ``PercentUtilizedGameServers`` to maintain a buffer of idle game servers that can immediately accommodate new games and players. After the Auto Scaling group is created, update this value directly in the Auto Scaling group using the AWS console or APIs. Default: no autoscaling policy settled
        :param balancing_strategy: (experimental) Indicates how GameLift FleetIQ balances the use of Spot Instances and On-Demand Instances in the game server group. Default: SPOT_PREFERRED
        :param delete_option: (experimental) The type of delete to perform. To delete a game server group, specify the DeleteOption Default: SAFE_DELETE
        :param max_size: (experimental) The maximum number of instances allowed in the Amazon EC2 Auto Scaling group. During automatic scaling events, GameLift FleetIQ and EC2 do not scale up the group above this maximum. After the Auto Scaling group is created, update this value directly in the Auto Scaling group using the AWS console or APIs. Default: the default is 1
        :param min_size: (experimental) The minimum number of instances allowed in the Amazon EC2 Auto Scaling group. During automatic scaling events, GameLift FleetIQ and Amazon EC2 do not scale down the group below this minimum. In production, this value should be set to at least 1. After the Auto Scaling group is created, update this value directly in the Auto Scaling group using the AWS console or APIs. Default: the default is 0
        :param protect_game_server: (experimental) A flag that indicates whether instances in the game server group are protected from early termination. Unprotected instances that have active game servers running might be terminated during a scale-down event, causing players to be dropped from the game. Protected instances cannot be terminated while there are active game servers running except in the event of a forced game server group deletion. An exception to this is with Spot Instances, which can be terminated by AWS regardless of protection status. Default: game servers running might be terminated during a scale-down event
        :param role: (experimental) The IAM role that allows Amazon GameLift to access your Amazon EC2 Auto Scaling groups. Default: - a role will be created with default trust to Gamelift and Autoscaling service principal with a default policy ``GameLiftGameServerGroupPolicy`` attached.
        :param vpc_subnets: (experimental) Game server group subnet selection. Default: all GameLift FleetIQ-supported Availability Zones are used.

        :stability: experimental
        '''
        props = GameServerGroupProps(
            game_server_group_name=game_server_group_name,
            instance_definitions=instance_definitions,
            launch_template=launch_template,
            vpc=vpc,
            auto_scaling_policy=auto_scaling_policy,
            balancing_strategy=balancing_strategy,
            delete_option=delete_option,
            max_size=max_size,
            min_size=min_size,
            protect_game_server=protect_game_server,
            role=role,
            vpc_subnets=vpc_subnets,
        )

        return typing.cast(_aws_cdk_aws_gamelift_ceddda9d.CfnGameServerGroup.LaunchTemplateProperty, jsii.invoke(self, "parseLaunchTemplate", [props]))

    @jsii.python.classproperty
    @jsii.member(jsii_name="PROPERTY_INJECTION_ID")
    def PROPERTY_INJECTION_ID(cls) -> builtins.str:
        '''(experimental) Uniquely identifies this class.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "PROPERTY_INJECTION_ID"))

    @builtins.property
    @jsii.member(jsii_name="autoScalingGroupArn")
    def auto_scaling_group_arn(self) -> builtins.str:
        '''(experimental) The ARN of the generated AutoScaling group.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "autoScalingGroupArn"))

    @builtins.property
    @jsii.member(jsii_name="gameServerGroupArn")
    def game_server_group_arn(self) -> builtins.str:
        '''(experimental) The ARN of the game server group.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "gameServerGroupArn"))

    @builtins.property
    @jsii.member(jsii_name="gameServerGroupName")
    def game_server_group_name(self) -> builtins.str:
        '''(experimental) The name of the game server group.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "gameServerGroupName"))

    @builtins.property
    @jsii.member(jsii_name="grantPrincipal")
    def grant_principal(self) -> _aws_cdk_aws_iam_ceddda9d.IPrincipal:
        '''(experimental) The principal this GameLift game server group is using.

        :stability: experimental
        '''
        return typing.cast(_aws_cdk_aws_iam_ceddda9d.IPrincipal, jsii.get(self, "grantPrincipal"))

    @builtins.property
    @jsii.member(jsii_name="role")
    def role(self) -> _aws_cdk_aws_iam_ceddda9d.IRole:
        '''(experimental) The IAM role that allows Amazon GameLift to access your Amazon EC2 Auto Scaling groups.

        :stability: experimental
        '''
        return typing.cast(_aws_cdk_aws_iam_ceddda9d.IRole, jsii.get(self, "role"))

    @builtins.property
    @jsii.member(jsii_name="vpc")
    def vpc(self) -> _aws_cdk_aws_ec2_ceddda9d.IVpc:
        '''(experimental) The VPC network to place the game server group in.

        :stability: experimental
        '''
        return typing.cast(_aws_cdk_aws_ec2_ceddda9d.IVpc, jsii.get(self, "vpc"))

    @builtins.property
    @jsii.member(jsii_name="vpcSubnets")
    def vpc_subnets(self) -> typing.Optional[_aws_cdk_aws_ec2_ceddda9d.SubnetSelection]:
        '''(experimental) The game server group's subnets.

        :stability: experimental
        '''
        return typing.cast(typing.Optional[_aws_cdk_aws_ec2_ceddda9d.SubnetSelection], jsii.get(self, "vpcSubnets"))


class GameSessionQueue(
    GameSessionQueueBase,
    metaclass=jsii.JSIIMeta,
    jsii_type="@aws-cdk/aws-gamelift-alpha.GameSessionQueue",
):
    '''(experimental) The GameSessionQueue resource creates a placement queue that processes requests for new game sessions.

    A queue uses FleetIQ algorithms to determine the best placement locations and find an available game server, then prompts the game server to start a new game session.
    Queues can have destinations (GameLift fleets or gameSessionQueuees), which determine where the queue can place new game sessions.
    A queue can have destinations with varied fleet type (Spot and On-Demand), instance type, and AWS Region.

    :stability: experimental
    :resource: AWS::GameLift::GameSessionQueue
    :exampleMetadata: infused

    Example::

        # fleet: gamelift.BuildFleet
        # alias: gamelift.Alias
        
        
        queue = gamelift.GameSessionQueue(self, "GameSessionQueue",
            game_session_queue_name="my-queue-name",
            destinations=[fleet]
        )
        queue.add_destination(alias)
    '''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        destinations: typing.Sequence[IGameSessionQueueDestination],
        game_session_queue_name: builtins.str,
        allowed_locations: typing.Optional[typing.Sequence[builtins.str]] = None,
        custom_event_data: typing.Optional[builtins.str] = None,
        notification_target: typing.Optional[_aws_cdk_aws_sns_ceddda9d.ITopic] = None,
        player_latency_policies: typing.Optional[typing.Sequence[typing.Union[PlayerLatencyPolicy, typing.Dict[builtins.str, typing.Any]]]] = None,
        priority_configuration: typing.Optional[typing.Union[PriorityConfiguration, typing.Dict[builtins.str, typing.Any]]] = None,
        timeout: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param destinations: (experimental) A list of fleets and/or fleet alias that can be used to fulfill game session placement requests in the queue. Destinations are listed in order of placement preference.
        :param game_session_queue_name: (experimental) Name of this gameSessionQueue.
        :param allowed_locations: (experimental) A list of locations where a queue is allowed to place new game sessions. Locations are specified in the form of AWS Region codes, such as ``us-west-2``. For queues that have multi-location fleets, you can use a filter configuration allow placement with some, but not all of these locations. Default: game sessions can be placed in any queue location
        :param custom_event_data: (experimental) Information to be added to all events that are related to this game session queue. Default: no customer event data
        :param notification_target: (experimental) An SNS topic is set up to receive game session placement notifications. Default: no notification
        :param player_latency_policies: (experimental) A set of policies that act as a sliding cap on player latency. FleetIQ works to deliver low latency for most players in a game session. These policies ensure that no individual player can be placed into a game with unreasonably high latency. Use multiple policies to gradually relax latency requirements a step at a time. Multiple policies are applied based on their maximum allowed latency, starting with the lowest value. Default: no player latency policy
        :param priority_configuration: (experimental) Custom settings to use when prioritizing destinations and locations for game session placements. This configuration replaces the FleetIQ default prioritization process. Priority types that are not explicitly named will be automatically applied at the end of the prioritization process. Default: no priority configuration
        :param timeout: (experimental) The maximum time, that a new game session placement request remains in the queue. When a request exceeds this time, the game session placement changes to a ``TIMED_OUT`` status. Default: 50 seconds

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__846520817af100925d03fe3dc61ab7cd70c568bf5abfde70677e06e42c232636)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = GameSessionQueueProps(
            destinations=destinations,
            game_session_queue_name=game_session_queue_name,
            allowed_locations=allowed_locations,
            custom_event_data=custom_event_data,
            notification_target=notification_target,
            player_latency_policies=player_latency_policies,
            priority_configuration=priority_configuration,
            timeout=timeout,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @jsii.member(jsii_name="fromGameSessionQueueArn")
    @builtins.classmethod
    def from_game_session_queue_arn(
        cls,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        game_session_queue_arn: builtins.str,
    ) -> IGameSessionQueue:
        '''(experimental) Import an existing gameSessionQueue from its ARN.

        :param scope: -
        :param id: -
        :param game_session_queue_arn: -

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6cb33d7a6d095570518d46828dd10e1034ae4dfa9fd69413f0de6b941264bc66)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument game_session_queue_arn", value=game_session_queue_arn, expected_type=type_hints["game_session_queue_arn"])
        return typing.cast(IGameSessionQueue, jsii.sinvoke(cls, "fromGameSessionQueueArn", [scope, id, game_session_queue_arn]))

    @jsii.member(jsii_name="fromGameSessionQueueAttributes")
    @builtins.classmethod
    def from_game_session_queue_attributes(
        cls,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        game_session_queue_arn: typing.Optional[builtins.str] = None,
        game_session_queue_name: typing.Optional[builtins.str] = None,
    ) -> IGameSessionQueue:
        '''(experimental) Import an existing gameSessionQueue from its attributes.

        :param scope: -
        :param id: -
        :param game_session_queue_arn: (experimental) The ARN of the gameSessionQueue. At least one of ``gameSessionQueueArn`` and ``gameSessionQueueName`` must be provided. Default: derived from ``gameSessionQueueName``.
        :param game_session_queue_name: (experimental) The name of the gameSessionQueue. At least one of ``gameSessionQueueName`` and ``gameSessionQueueArn`` must be provided. Default: derived from ``gameSessionQueueArn``.

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9abe3c8dfc0d7493f78870441d89e451d4012dea9b62447d44af88e912a94a09)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        attrs = GameSessionQueueAttributes(
            game_session_queue_arn=game_session_queue_arn,
            game_session_queue_name=game_session_queue_name,
        )

        return typing.cast(IGameSessionQueue, jsii.sinvoke(cls, "fromGameSessionQueueAttributes", [scope, id, attrs]))

    @jsii.member(jsii_name="fromGameSessionQueueName")
    @builtins.classmethod
    def from_game_session_queue_name(
        cls,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        game_session_queue_name: builtins.str,
    ) -> IGameSessionQueue:
        '''(experimental) Import an existing gameSessionQueue from its name.

        :param scope: -
        :param id: -
        :param game_session_queue_name: -

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__46707c5adccba8071b9aa0cfec2dac4419e4abf4a3801b5b7ad8ebe85740cf31)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument game_session_queue_name", value=game_session_queue_name, expected_type=type_hints["game_session_queue_name"])
        return typing.cast(IGameSessionQueue, jsii.sinvoke(cls, "fromGameSessionQueueName", [scope, id, game_session_queue_name]))

    @jsii.member(jsii_name="addDestination")
    def add_destination(self, destination: IGameSessionQueueDestination) -> None:
        '''(experimental) Adds a destination to fulfill requests for new game sessions.

        :param destination: A destination to add.

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0726b630a813fb456a6509ecd3b21784fcc7d6f8936316cac6394bff525110dc)
            check_type(argname="argument destination", value=destination, expected_type=type_hints["destination"])
        return typing.cast(None, jsii.invoke(self, "addDestination", [destination]))

    @jsii.member(jsii_name="parseFilterConfiguration")
    def _parse_filter_configuration(
        self,
        *,
        destinations: typing.Sequence[IGameSessionQueueDestination],
        game_session_queue_name: builtins.str,
        allowed_locations: typing.Optional[typing.Sequence[builtins.str]] = None,
        custom_event_data: typing.Optional[builtins.str] = None,
        notification_target: typing.Optional[_aws_cdk_aws_sns_ceddda9d.ITopic] = None,
        player_latency_policies: typing.Optional[typing.Sequence[typing.Union[PlayerLatencyPolicy, typing.Dict[builtins.str, typing.Any]]]] = None,
        priority_configuration: typing.Optional[typing.Union[PriorityConfiguration, typing.Dict[builtins.str, typing.Any]]] = None,
        timeout: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
    ) -> typing.Optional[_aws_cdk_aws_gamelift_ceddda9d.CfnGameSessionQueue.FilterConfigurationProperty]:
        '''
        :param destinations: (experimental) A list of fleets and/or fleet alias that can be used to fulfill game session placement requests in the queue. Destinations are listed in order of placement preference.
        :param game_session_queue_name: (experimental) Name of this gameSessionQueue.
        :param allowed_locations: (experimental) A list of locations where a queue is allowed to place new game sessions. Locations are specified in the form of AWS Region codes, such as ``us-west-2``. For queues that have multi-location fleets, you can use a filter configuration allow placement with some, but not all of these locations. Default: game sessions can be placed in any queue location
        :param custom_event_data: (experimental) Information to be added to all events that are related to this game session queue. Default: no customer event data
        :param notification_target: (experimental) An SNS topic is set up to receive game session placement notifications. Default: no notification
        :param player_latency_policies: (experimental) A set of policies that act as a sliding cap on player latency. FleetIQ works to deliver low latency for most players in a game session. These policies ensure that no individual player can be placed into a game with unreasonably high latency. Use multiple policies to gradually relax latency requirements a step at a time. Multiple policies are applied based on their maximum allowed latency, starting with the lowest value. Default: no player latency policy
        :param priority_configuration: (experimental) Custom settings to use when prioritizing destinations and locations for game session placements. This configuration replaces the FleetIQ default prioritization process. Priority types that are not explicitly named will be automatically applied at the end of the prioritization process. Default: no priority configuration
        :param timeout: (experimental) The maximum time, that a new game session placement request remains in the queue. When a request exceeds this time, the game session placement changes to a ``TIMED_OUT`` status. Default: 50 seconds

        :stability: experimental
        '''
        props = GameSessionQueueProps(
            destinations=destinations,
            game_session_queue_name=game_session_queue_name,
            allowed_locations=allowed_locations,
            custom_event_data=custom_event_data,
            notification_target=notification_target,
            player_latency_policies=player_latency_policies,
            priority_configuration=priority_configuration,
            timeout=timeout,
        )

        return typing.cast(typing.Optional[_aws_cdk_aws_gamelift_ceddda9d.CfnGameSessionQueue.FilterConfigurationProperty], jsii.invoke(self, "parseFilterConfiguration", [props]))

    @jsii.member(jsii_name="parsePlayerLatencyPolicies")
    def _parse_player_latency_policies(
        self,
        *,
        destinations: typing.Sequence[IGameSessionQueueDestination],
        game_session_queue_name: builtins.str,
        allowed_locations: typing.Optional[typing.Sequence[builtins.str]] = None,
        custom_event_data: typing.Optional[builtins.str] = None,
        notification_target: typing.Optional[_aws_cdk_aws_sns_ceddda9d.ITopic] = None,
        player_latency_policies: typing.Optional[typing.Sequence[typing.Union[PlayerLatencyPolicy, typing.Dict[builtins.str, typing.Any]]]] = None,
        priority_configuration: typing.Optional[typing.Union[PriorityConfiguration, typing.Dict[builtins.str, typing.Any]]] = None,
        timeout: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
    ) -> typing.Optional[typing.List[_aws_cdk_aws_gamelift_ceddda9d.CfnGameSessionQueue.PlayerLatencyPolicyProperty]]:
        '''
        :param destinations: (experimental) A list of fleets and/or fleet alias that can be used to fulfill game session placement requests in the queue. Destinations are listed in order of placement preference.
        :param game_session_queue_name: (experimental) Name of this gameSessionQueue.
        :param allowed_locations: (experimental) A list of locations where a queue is allowed to place new game sessions. Locations are specified in the form of AWS Region codes, such as ``us-west-2``. For queues that have multi-location fleets, you can use a filter configuration allow placement with some, but not all of these locations. Default: game sessions can be placed in any queue location
        :param custom_event_data: (experimental) Information to be added to all events that are related to this game session queue. Default: no customer event data
        :param notification_target: (experimental) An SNS topic is set up to receive game session placement notifications. Default: no notification
        :param player_latency_policies: (experimental) A set of policies that act as a sliding cap on player latency. FleetIQ works to deliver low latency for most players in a game session. These policies ensure that no individual player can be placed into a game with unreasonably high latency. Use multiple policies to gradually relax latency requirements a step at a time. Multiple policies are applied based on their maximum allowed latency, starting with the lowest value. Default: no player latency policy
        :param priority_configuration: (experimental) Custom settings to use when prioritizing destinations and locations for game session placements. This configuration replaces the FleetIQ default prioritization process. Priority types that are not explicitly named will be automatically applied at the end of the prioritization process. Default: no priority configuration
        :param timeout: (experimental) The maximum time, that a new game session placement request remains in the queue. When a request exceeds this time, the game session placement changes to a ``TIMED_OUT`` status. Default: 50 seconds

        :stability: experimental
        '''
        props = GameSessionQueueProps(
            destinations=destinations,
            game_session_queue_name=game_session_queue_name,
            allowed_locations=allowed_locations,
            custom_event_data=custom_event_data,
            notification_target=notification_target,
            player_latency_policies=player_latency_policies,
            priority_configuration=priority_configuration,
            timeout=timeout,
        )

        return typing.cast(typing.Optional[typing.List[_aws_cdk_aws_gamelift_ceddda9d.CfnGameSessionQueue.PlayerLatencyPolicyProperty]], jsii.invoke(self, "parsePlayerLatencyPolicies", [props]))

    @jsii.member(jsii_name="parsePriorityConfiguration")
    def _parse_priority_configuration(
        self,
        *,
        destinations: typing.Sequence[IGameSessionQueueDestination],
        game_session_queue_name: builtins.str,
        allowed_locations: typing.Optional[typing.Sequence[builtins.str]] = None,
        custom_event_data: typing.Optional[builtins.str] = None,
        notification_target: typing.Optional[_aws_cdk_aws_sns_ceddda9d.ITopic] = None,
        player_latency_policies: typing.Optional[typing.Sequence[typing.Union[PlayerLatencyPolicy, typing.Dict[builtins.str, typing.Any]]]] = None,
        priority_configuration: typing.Optional[typing.Union[PriorityConfiguration, typing.Dict[builtins.str, typing.Any]]] = None,
        timeout: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
    ) -> typing.Optional[_aws_cdk_aws_gamelift_ceddda9d.CfnGameSessionQueue.PriorityConfigurationProperty]:
        '''
        :param destinations: (experimental) A list of fleets and/or fleet alias that can be used to fulfill game session placement requests in the queue. Destinations are listed in order of placement preference.
        :param game_session_queue_name: (experimental) Name of this gameSessionQueue.
        :param allowed_locations: (experimental) A list of locations where a queue is allowed to place new game sessions. Locations are specified in the form of AWS Region codes, such as ``us-west-2``. For queues that have multi-location fleets, you can use a filter configuration allow placement with some, but not all of these locations. Default: game sessions can be placed in any queue location
        :param custom_event_data: (experimental) Information to be added to all events that are related to this game session queue. Default: no customer event data
        :param notification_target: (experimental) An SNS topic is set up to receive game session placement notifications. Default: no notification
        :param player_latency_policies: (experimental) A set of policies that act as a sliding cap on player latency. FleetIQ works to deliver low latency for most players in a game session. These policies ensure that no individual player can be placed into a game with unreasonably high latency. Use multiple policies to gradually relax latency requirements a step at a time. Multiple policies are applied based on their maximum allowed latency, starting with the lowest value. Default: no player latency policy
        :param priority_configuration: (experimental) Custom settings to use when prioritizing destinations and locations for game session placements. This configuration replaces the FleetIQ default prioritization process. Priority types that are not explicitly named will be automatically applied at the end of the prioritization process. Default: no priority configuration
        :param timeout: (experimental) The maximum time, that a new game session placement request remains in the queue. When a request exceeds this time, the game session placement changes to a ``TIMED_OUT`` status. Default: 50 seconds

        :stability: experimental
        '''
        props = GameSessionQueueProps(
            destinations=destinations,
            game_session_queue_name=game_session_queue_name,
            allowed_locations=allowed_locations,
            custom_event_data=custom_event_data,
            notification_target=notification_target,
            player_latency_policies=player_latency_policies,
            priority_configuration=priority_configuration,
            timeout=timeout,
        )

        return typing.cast(typing.Optional[_aws_cdk_aws_gamelift_ceddda9d.CfnGameSessionQueue.PriorityConfigurationProperty], jsii.invoke(self, "parsePriorityConfiguration", [props]))

    @jsii.python.classproperty
    @jsii.member(jsii_name="PROPERTY_INJECTION_ID")
    def PROPERTY_INJECTION_ID(cls) -> builtins.str:
        '''(experimental) Uniquely identifies this class.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "PROPERTY_INJECTION_ID"))

    @builtins.property
    @jsii.member(jsii_name="gameSessionQueueArn")
    def game_session_queue_arn(self) -> builtins.str:
        '''(experimental) The ARN of the gameSessionQueue.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "gameSessionQueueArn"))

    @builtins.property
    @jsii.member(jsii_name="gameSessionQueueName")
    def game_session_queue_name(self) -> builtins.str:
        '''(experimental) The Identifier of the gameSessionQueue.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "gameSessionQueueName"))


@jsii.interface(jsii_type="@aws-cdk/aws-gamelift-alpha.IBuildFleet")
class IBuildFleet(IFleet, typing_extensions.Protocol):
    '''(experimental) Represents a GameLift Fleet used to run a custom game build.

    :stability: experimental
    '''

    pass


class _IBuildFleetProxy(
    jsii.proxy_for(IFleet), # type: ignore[misc]
):
    '''(experimental) Represents a GameLift Fleet used to run a custom game build.

    :stability: experimental
    '''

    __jsii_type__: typing.ClassVar[str] = "@aws-cdk/aws-gamelift-alpha.IBuildFleet"
    pass

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, IBuildFleet).__jsii_proxy_class__ = lambda : _IBuildFleetProxy


class Alias(
    AliasBase,
    metaclass=jsii.JSIIMeta,
    jsii_type="@aws-cdk/aws-gamelift-alpha.Alias",
):
    '''(experimental) A Amazon GameLift alias is used to abstract a fleet designation.

    Fleet designations tell GameLift where to search for available resources when creating new game sessions for players.
    Use aliases instead of specific fleet IDs to seamlessly switch player traffic from one fleet to another by changing the alias's target location.

    Aliases are useful in games that don't use queues.
    Switching fleets in a queue is a simple matter of creating a new fleet, adding it to the queue, and removing the old fleet, none of which is visible to players.
    In contrast, game clients that don't use queues must specify which fleet to use when communicating with the GameLift service.
    Without aliases, a fleet switch requires updates to your game code and possibly distribution of an updated game clients to players.

    When updating the fleet-id an alias points to, there is a transition period of up to 2 minutes where game sessions on the alias may end up on the old fleet.

    :see: https://docs.aws.amazon.com/gamelift/latest/developerguide/aliases-creating.html
    :stability: experimental
    :resource: AWS::GameLift::Alias
    :exampleMetadata: infused

    Example::

        # fleet: gamelift.BuildFleet
        
        
        # Add an alias to an existing fleet using a dedicated fleet method
        live_alias = fleet.add_alias("live")
        
        # You can also create a standalone alias
        gamelift.Alias(self, "TerminalAlias",
            alias_name="terminal-alias",
            terminal_message="A terminal message"
        )
    '''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        alias_name: builtins.str,
        description: typing.Optional[builtins.str] = None,
        fleet: typing.Optional[IFleet] = None,
        terminal_message: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param alias_name: (experimental) Name of this alias.
        :param description: (experimental) A human-readable description of the alias. Default: no description
        :param fleet: (experimental) A fleet that the alias points to. If specified, the alias resolves to one specific fleet. At least one of ``fleet`` and ``terminalMessage`` must be provided. Default: no fleet that the alias points to.
        :param terminal_message: (experimental) The message text to be used with a terminal routing strategy. At least one of ``fleet`` and ``terminalMessage`` must be provided. Default: no terminal message

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9ca155302605299f39ebc02214b9c2ec1ec3ecb1d07672160bbfe85b446feb43)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = AliasProps(
            alias_name=alias_name,
            description=description,
            fleet=fleet,
            terminal_message=terminal_message,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @jsii.member(jsii_name="fromAliasArn")
    @builtins.classmethod
    def from_alias_arn(
        cls,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        alias_arn: builtins.str,
    ) -> IAlias:
        '''(experimental) Import an existing alias from its ARN.

        :param scope: -
        :param id: -
        :param alias_arn: -

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__02b9841ad4d64fe609fa4d225adb886af4e5300981093e8e23b9dade3b39154d)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument alias_arn", value=alias_arn, expected_type=type_hints["alias_arn"])
        return typing.cast(IAlias, jsii.sinvoke(cls, "fromAliasArn", [scope, id, alias_arn]))

    @jsii.member(jsii_name="fromAliasAttributes")
    @builtins.classmethod
    def from_alias_attributes(
        cls,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        alias_arn: typing.Optional[builtins.str] = None,
        alias_id: typing.Optional[builtins.str] = None,
    ) -> IAlias:
        '''(experimental) Import an existing alias from its attributes.

        :param scope: -
        :param id: -
        :param alias_arn: (experimental) The ARN of the alias. At least one of ``aliasArn`` and ``aliasId`` must be provided. Default: derived from ``aliasId``.
        :param alias_id: (experimental) The identifier of the alias. At least one of ``aliasId`` and ``aliasArn`` must be provided. Default: derived from ``aliasArn``.

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0a0852329e6582921470d2df6eb3f175d7598559ee0bbb5a199fc9ba6eed831a)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        attrs = AliasAttributes(alias_arn=alias_arn, alias_id=alias_id)

        return typing.cast(IAlias, jsii.sinvoke(cls, "fromAliasAttributes", [scope, id, attrs]))

    @jsii.member(jsii_name="fromAliasId")
    @builtins.classmethod
    def from_alias_id(
        cls,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        alias_id: builtins.str,
    ) -> IAlias:
        '''(experimental) Import an existing alias from its identifier.

        :param scope: -
        :param id: -
        :param alias_id: -

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__fddb71a5d89a4ff9a839d371c159d1513dc760d472525e873ec06490b9ed62db)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument alias_id", value=alias_id, expected_type=type_hints["alias_id"])
        return typing.cast(IAlias, jsii.sinvoke(cls, "fromAliasId", [scope, id, alias_id]))

    @jsii.python.classproperty
    @jsii.member(jsii_name="PROPERTY_INJECTION_ID")
    def PROPERTY_INJECTION_ID(cls) -> builtins.str:
        '''(experimental) Uniquely identifies this class.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "PROPERTY_INJECTION_ID"))

    @builtins.property
    @jsii.member(jsii_name="aliasArn")
    def alias_arn(self) -> builtins.str:
        '''(experimental) The ARN of the alias.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "aliasArn"))

    @builtins.property
    @jsii.member(jsii_name="aliasId")
    def alias_id(self) -> builtins.str:
        '''(experimental) The Identifier of the alias.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "aliasId"))

    @builtins.property
    @jsii.member(jsii_name="fleet")
    def fleet(self) -> typing.Optional[IFleet]:
        '''(experimental) A fleet that the alias points to.

        :stability: experimental
        '''
        return typing.cast(typing.Optional[IFleet], jsii.get(self, "fleet"))


@jsii.implements(IBuildFleet)
class BuildFleet(
    FleetBase,
    metaclass=jsii.JSIIMeta,
    jsii_type="@aws-cdk/aws-gamelift-alpha.BuildFleet",
):
    '''(experimental) A fleet contains Amazon Elastic Compute Cloud (Amazon EC2) instances that GameLift hosts.

    A fleet uses the configuration and scaling logic that you define to run your game server build. You can use a fleet directly without a queue.
    You can also associate multiple fleets with a GameLift queue.

    For example, you can use Spot Instance fleets configured with your preferred locations, along with a backup On-Demand Instance fleet with the same locations.
    Using multiple Spot Instance fleets of different instance types reduces the chance of needing On-Demand Instance placement.

    :stability: experimental
    :resource: AWS::GameLift::Fleet
    :exampleMetadata: infused

    Example::

        # build: gamelift.Build
        
        # Server processes can be delcared in a declarative way through the constructor
        fleet = gamelift.BuildFleet(self, "Game server fleet",
            fleet_name="test-fleet",
            content=build,
            instance_type=ec2.InstanceType.of(ec2.InstanceClass.C4, ec2.InstanceSize.LARGE),
            runtime_configuration=gamelift.RuntimeConfiguration(
                server_processes=[gamelift.ServerProcess(
                    launch_path="/local/game/GameLiftExampleServer.x86_64",
                    parameters="-logFile /local/game/logs/myserver1935.log -port 1935",
                    concurrent_executions=100
                )]
            )
        )
    '''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        content: IBuild,
        ingress_rules: typing.Optional[typing.Sequence[typing.Union[IngressRule, typing.Dict[builtins.str, typing.Any]]]] = None,
        fleet_name: builtins.str,
        instance_type: _aws_cdk_aws_ec2_ceddda9d.InstanceType,
        runtime_configuration: typing.Union[RuntimeConfiguration, typing.Dict[builtins.str, typing.Any]],
        description: typing.Optional[builtins.str] = None,
        desired_capacity: typing.Optional[jsii.Number] = None,
        locations: typing.Optional[typing.Sequence[typing.Union[Location, typing.Dict[builtins.str, typing.Any]]]] = None,
        max_size: typing.Optional[jsii.Number] = None,
        metric_group: typing.Optional[builtins.str] = None,
        min_size: typing.Optional[jsii.Number] = None,
        peer_vpc: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IVpc] = None,
        protect_new_game_session: typing.Optional[builtins.bool] = None,
        resource_creation_limit_policy: typing.Optional[typing.Union[ResourceCreationLimitPolicy, typing.Dict[builtins.str, typing.Any]]] = None,
        role: typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole] = None,
        use_certificate: typing.Optional[builtins.bool] = None,
        use_spot: typing.Optional[builtins.bool] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param content: (experimental) A build to be deployed on the fleet. The build must have been successfully uploaded to Amazon GameLift and be in a ``READY`` status. This fleet setting cannot be changed once the fleet is created.
        :param ingress_rules: (experimental) The allowed IP address ranges and port settings that allow inbound traffic to access game sessions on this fleet. This property must be set before players can connect to game sessions. Default: no inbound traffic allowed
        :param fleet_name: (experimental) A descriptive label that is associated with a fleet. Fleet names do not need to be unique.
        :param instance_type: (experimental) The GameLift-supported Amazon EC2 instance type to use for all fleet instances. Instance type determines the computing resources that will be used to host your game servers, including CPU, memory, storage, and networking capacity.
        :param runtime_configuration: (experimental) A collection of server process configurations that describe the set of processes to run on each instance in a fleet. Server processes run either an executable in a custom game build or a Realtime Servers script. GameLift launches the configured processes, manages their life cycle, and replaces them as needed. Each instance checks regularly for an updated runtime configuration. A GameLift instance is limited to 50 processes running concurrently. To calculate the total number of processes in a runtime configuration, add the values of the ConcurrentExecutions parameter for each ServerProcess.
        :param description: (experimental) A human-readable description of the fleet. Default: no description is provided
        :param desired_capacity: (experimental) The number of EC2 instances that you want this fleet to host. When creating a new fleet, GameLift automatically sets this value to "1" and initiates a single instance. Once the fleet is active, update this value to trigger GameLift to add or remove instances from the fleet. Default: Default capacity is 0
        :param locations: (experimental) A set of remote locations to deploy additional instances to and manage as part of the fleet. This parameter can only be used when creating fleets in AWS Regions that support multiple locations. You can add any GameLift-supported AWS Region as a remote location, in the form of an AWS Region code such as ``us-west-2``. To create a fleet with instances in the home region only, omit this parameter. Default: Create a fleet with instances in the home region only
        :param max_size: (experimental) The maximum number of instances that are allowed in the specified fleet location. Default: the default is 1
        :param metric_group: (experimental) The name of an AWS CloudWatch metric group to add this fleet to. A metric group is used to aggregate the metrics for multiple fleets. You can specify an existing metric group name or set a new name to create a new metric group. A fleet can be included in only one metric group at a time. Default: Fleet metrics are aggregated with other fleets in the default metric group
        :param min_size: (experimental) The minimum number of instances that are allowed in the specified fleet location. Default: the default is 0
        :param peer_vpc: (experimental) A VPC peering connection between your GameLift-hosted game servers and your other non-GameLift resources. Use Amazon Virtual Private Cloud (VPC) peering connections to enable your game servers to communicate directly and privately with your other AWS resources, such as a web service or a repository. You can establish VPC peering with any resources that run on AWS and are managed by an AWS account that you have access to. The VPC must be in the same Region as your fleet. Warning: Be sure to create a VPC Peering authorization through Gamelift Service API. Default: no vpc peering
        :param protect_new_game_session: (experimental) The status of termination protection for active game sessions on the fleet. By default, new game sessions are protected and cannot be terminated during a scale-down event. Default: true - Game sessions in ``ACTIVE`` status cannot be terminated during a scale-down event.
        :param resource_creation_limit_policy: (experimental) A policy that limits the number of game sessions that an individual player can create on instances in this fleet within a specified span of time. Default: No resource creation limit policy
        :param role: (experimental) The IAM role assumed by GameLift fleet instances to access AWS ressources. With a role set, any application that runs on an instance in this fleet can assume the role, including install scripts, server processes, and daemons (background processes). If providing a custom role, it needs to trust the GameLift service principal (gamelift.amazonaws.com). No permission is required by default. This property cannot be changed after the fleet is created. Default: - a role will be created with default trust to Gamelift service principal.
        :param use_certificate: (experimental) Prompts GameLift to generate a TLS/SSL certificate for the fleet. GameLift uses the certificates to encrypt traffic between game clients and the game servers running on GameLift. You can't change this property after you create the fleet. Additionnal info: AWS Certificate Manager (ACM) certificates expire after 13 months. Certificate expiration can cause fleets to fail, preventing players from connecting to instances in the fleet. We recommend you replace fleets before 13 months, consider using fleet aliases for a smooth transition. Default: TLS/SSL certificate are generated for the fleet
        :param use_spot: (experimental) Indicates whether to use On-Demand or Spot instances for this fleet. By default, fleet use on demand capacity. This property cannot be changed after the fleet is created. Default: Gamelift fleet use on demand capacity

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b0f96582da85e159c90711da4321ddc6d10a9be0aaa75bf5d139f2ada0d0a9ec)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = BuildFleetProps(
            content=content,
            ingress_rules=ingress_rules,
            fleet_name=fleet_name,
            instance_type=instance_type,
            runtime_configuration=runtime_configuration,
            description=description,
            desired_capacity=desired_capacity,
            locations=locations,
            max_size=max_size,
            metric_group=metric_group,
            min_size=min_size,
            peer_vpc=peer_vpc,
            protect_new_game_session=protect_new_game_session,
            resource_creation_limit_policy=resource_creation_limit_policy,
            role=role,
            use_certificate=use_certificate,
            use_spot=use_spot,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @jsii.member(jsii_name="fromBuildFleetArn")
    @builtins.classmethod
    def from_build_fleet_arn(
        cls,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        build_fleet_arn: builtins.str,
    ) -> IBuildFleet:
        '''(experimental) Import an existing fleet from its ARN.

        :param scope: -
        :param id: -
        :param build_fleet_arn: -

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ef7abe85750cf6ce2c0acf9b4d63ece12f0d8efc194a92c524abd18fef5d5d93)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument build_fleet_arn", value=build_fleet_arn, expected_type=type_hints["build_fleet_arn"])
        return typing.cast(IBuildFleet, jsii.sinvoke(cls, "fromBuildFleetArn", [scope, id, build_fleet_arn]))

    @jsii.member(jsii_name="fromBuildFleetId")
    @builtins.classmethod
    def from_build_fleet_id(
        cls,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        build_fleet_id: builtins.str,
    ) -> IBuildFleet:
        '''(experimental) Import an existing fleet from its identifier.

        :param scope: -
        :param id: -
        :param build_fleet_id: -

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a61afc3b99684bbcad3253856e305c24c5d37c7a1b410354b519756b5c5a3dfd)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument build_fleet_id", value=build_fleet_id, expected_type=type_hints["build_fleet_id"])
        return typing.cast(IBuildFleet, jsii.sinvoke(cls, "fromBuildFleetId", [scope, id, build_fleet_id]))

    @jsii.member(jsii_name="addIngressRule")
    def add_ingress_rule(self, source: IPeer, port: Port) -> None:
        '''(experimental) Adds an ingress rule to allow inbound traffic to access game sessions on this fleet.

        :param source: A range of allowed IP addresses.
        :param port: The port range used for ingress traffic.

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0ff1a5dfaf3ccd3895ed18ca2bad230faa4172c04c6bed9596351df73b837a68)
            check_type(argname="argument source", value=source, expected_type=type_hints["source"])
            check_type(argname="argument port", value=port, expected_type=type_hints["port"])
        return typing.cast(None, jsii.invoke(self, "addIngressRule", [source, port]))

    @jsii.python.classproperty
    @jsii.member(jsii_name="PROPERTY_INJECTION_ID")
    def PROPERTY_INJECTION_ID(cls) -> builtins.str:
        '''(experimental) Uniquely identifies this class.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "PROPERTY_INJECTION_ID"))

    @builtins.property
    @jsii.member(jsii_name="content")
    def content(self) -> IBuild:
        '''(experimental) The build content of the fleet.

        :stability: experimental
        '''
        return typing.cast(IBuild, jsii.get(self, "content"))

    @builtins.property
    @jsii.member(jsii_name="fleetArn")
    def fleet_arn(self) -> builtins.str:
        '''(experimental) The ARN of the fleet.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "fleetArn"))

    @builtins.property
    @jsii.member(jsii_name="fleetId")
    def fleet_id(self) -> builtins.str:
        '''(experimental) The Identifier of the fleet.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "fleetId"))

    @builtins.property
    @jsii.member(jsii_name="grantPrincipal")
    def grant_principal(self) -> _aws_cdk_aws_iam_ceddda9d.IPrincipal:
        '''(experimental) The principal this GameLift fleet is using.

        :stability: experimental
        '''
        return typing.cast(_aws_cdk_aws_iam_ceddda9d.IPrincipal, jsii.get(self, "grantPrincipal"))

    @builtins.property
    @jsii.member(jsii_name="role")
    def role(self) -> _aws_cdk_aws_iam_ceddda9d.IRole:
        '''(experimental) The IAM role GameLift assumes by fleet instances to access AWS ressources.

        :stability: experimental
        '''
        return typing.cast(_aws_cdk_aws_iam_ceddda9d.IRole, jsii.get(self, "role"))


__all__ = [
    "Alias",
    "AliasAttributes",
    "AliasBase",
    "AliasOptions",
    "AliasProps",
    "AssetContent",
    "AutoScalingPolicy",
    "BalancingStrategy",
    "Build",
    "BuildAttributes",
    "BuildBase",
    "BuildFleet",
    "BuildFleetProps",
    "BuildProps",
    "Content",
    "ContentConfig",
    "DeleteOption",
    "FleetAttributes",
    "FleetBase",
    "FleetProps",
    "GameProperty",
    "GameServerGroup",
    "GameServerGroupAttributes",
    "GameServerGroupBase",
    "GameServerGroupProps",
    "GameSessionQueue",
    "GameSessionQueueAttributes",
    "GameSessionQueueBase",
    "GameSessionQueueProps",
    "IAlias",
    "IBuild",
    "IBuildFleet",
    "IFleet",
    "IGameServerGroup",
    "IGameSessionQueue",
    "IGameSessionQueueDestination",
    "IMatchmakingConfiguration",
    "IMatchmakingRuleSet",
    "IPeer",
    "IRuleSetBody",
    "IRuleSetContent",
    "IScript",
    "IngressRule",
    "InstanceDefinition",
    "Location",
    "LocationCapacity",
    "MatchmakingConfigurationAttributes",
    "MatchmakingConfigurationBase",
    "MatchmakingConfigurationProps",
    "MatchmakingRuleSet",
    "MatchmakingRuleSetAttributes",
    "MatchmakingRuleSetBase",
    "MatchmakingRuleSetProps",
    "OperatingSystem",
    "Peer",
    "PlayerLatencyPolicy",
    "Port",
    "PortProps",
    "PriorityConfiguration",
    "PriorityType",
    "Protocol",
    "QueuedMatchmakingConfiguration",
    "QueuedMatchmakingConfigurationProps",
    "ResourceCreationLimitPolicy",
    "RuleSetBodyConfig",
    "RuleSetContent",
    "RuleSetContentProps",
    "RuntimeConfiguration",
    "S3Content",
    "Script",
    "ScriptAttributes",
    "ScriptBase",
    "ScriptProps",
    "ServerProcess",
    "StandaloneMatchmakingConfiguration",
    "StandaloneMatchmakingConfigurationProps",
]

publication.publish()

def _typecheckingstub__04279523a0cc50838f54aa501c7a3727907d986b95b950c0f5c999e3feebe6be(
    *,
    alias_arn: typing.Optional[builtins.str] = None,
    alias_id: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2287dbf19acdb26798b6177f68979aba4e2d99cac4684391d3b94f547845d855(
    *,
    description: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e7632247cd09762e30337d9fcf6bc1dbf7d405ef72c3e8f1f9195436c713ecc0(
    *,
    alias_name: builtins.str,
    description: typing.Optional[builtins.str] = None,
    fleet: typing.Optional[IFleet] = None,
    terminal_message: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0177fa2ab17f9865574fd09ad3d1f990ef0d7423199d06387b69eb189ae89e7e(
    *,
    target_tracking_configuration: jsii.Number,
    estimated_instance_warmup: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__eeffd58e73fe7a51fe98048a49a3129ed94d23f43d5263361781c6e0b0b71d7b(
    *,
    build_arn: typing.Optional[builtins.str] = None,
    build_id: typing.Optional[builtins.str] = None,
    role: typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4f4a75ef0e23a8dbf4114398dbe9a7b2d5f6435cf277ff83bdd799761bf35919(
    *,
    content: Content,
    build_name: typing.Optional[builtins.str] = None,
    build_version: typing.Optional[builtins.str] = None,
    operating_system: typing.Optional[OperatingSystem] = None,
    role: typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole] = None,
    server_sdk_version: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__56f24a9c36c82910107482c5b3fd186832948b0896de7f43b6d0cfc0065ea27e(
    path: builtins.str,
    *,
    deploy_time: typing.Optional[builtins.bool] = None,
    display_name: typing.Optional[builtins.str] = None,
    readers: typing.Optional[typing.Sequence[_aws_cdk_aws_iam_ceddda9d.IGrantable]] = None,
    source_kms_key: typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey] = None,
    asset_hash: typing.Optional[builtins.str] = None,
    asset_hash_type: typing.Optional[_aws_cdk_ceddda9d.AssetHashType] = None,
    bundling: typing.Optional[typing.Union[_aws_cdk_ceddda9d.BundlingOptions, typing.Dict[builtins.str, typing.Any]]] = None,
    exclude: typing.Optional[typing.Sequence[builtins.str]] = None,
    follow_symlinks: typing.Optional[_aws_cdk_ceddda9d.SymlinkFollowMode] = None,
    ignore_mode: typing.Optional[_aws_cdk_ceddda9d.IgnoreMode] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e4efd80abc10f6730064317b68ae3759c6140bb0ed64b2bcb4fe1f331b2675c8(
    bucket: _aws_cdk_aws_s3_ceddda9d.IBucket,
    key: builtins.str,
    object_version: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__02578964481495d6c165471c27f8a101e606642894654fc650791d9c9110f39c(
    scope: _constructs_77d1e7e8.Construct,
    role: _aws_cdk_aws_iam_ceddda9d.IRole,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__23a167cb97741dac66b4d985310b521515726f1ddd0b3c22facfb54e2b1f0da8(
    *,
    s3_location: typing.Union[_aws_cdk_aws_s3_ceddda9d.Location, typing.Dict[builtins.str, typing.Any]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__35d532df97dc03beb2ad5bd1cb5393dfd16d91e9e6e0537dec0cc5074288536c(
    *,
    fleet_arn: typing.Optional[builtins.str] = None,
    fleet_id: typing.Optional[builtins.str] = None,
    role: typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b81a93e51de6b03726329d65b2414826a941e9123fb0a5ec20bcad7f184a4382(
    *,
    fleet_name: builtins.str,
    instance_type: _aws_cdk_aws_ec2_ceddda9d.InstanceType,
    runtime_configuration: typing.Union[RuntimeConfiguration, typing.Dict[builtins.str, typing.Any]],
    description: typing.Optional[builtins.str] = None,
    desired_capacity: typing.Optional[jsii.Number] = None,
    locations: typing.Optional[typing.Sequence[typing.Union[Location, typing.Dict[builtins.str, typing.Any]]]] = None,
    max_size: typing.Optional[jsii.Number] = None,
    metric_group: typing.Optional[builtins.str] = None,
    min_size: typing.Optional[jsii.Number] = None,
    peer_vpc: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IVpc] = None,
    protect_new_game_session: typing.Optional[builtins.bool] = None,
    resource_creation_limit_policy: typing.Optional[typing.Union[ResourceCreationLimitPolicy, typing.Dict[builtins.str, typing.Any]]] = None,
    role: typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole] = None,
    use_certificate: typing.Optional[builtins.bool] = None,
    use_spot: typing.Optional[builtins.bool] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0e8980d178329ea7c3dcc75b375385b207b175d8e61a252631f5104bb4fad972(
    *,
    key: builtins.str,
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a95367b408716c3da6316646dac97baa91d468c4be616abe0e3fb8c79f67d991(
    *,
    auto_scaling_group_arn: builtins.str,
    game_server_group_arn: typing.Optional[builtins.str] = None,
    game_server_group_name: typing.Optional[builtins.str] = None,
    role: typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__940bf2cd04369fce6e5224d911d6b8cccc442bf95877315cc6c35048dddb278b(
    *,
    game_server_group_name: builtins.str,
    instance_definitions: typing.Sequence[typing.Union[InstanceDefinition, typing.Dict[builtins.str, typing.Any]]],
    launch_template: _aws_cdk_aws_ec2_ceddda9d.ILaunchTemplate,
    vpc: _aws_cdk_aws_ec2_ceddda9d.IVpc,
    auto_scaling_policy: typing.Optional[typing.Union[AutoScalingPolicy, typing.Dict[builtins.str, typing.Any]]] = None,
    balancing_strategy: typing.Optional[BalancingStrategy] = None,
    delete_option: typing.Optional[DeleteOption] = None,
    max_size: typing.Optional[jsii.Number] = None,
    min_size: typing.Optional[jsii.Number] = None,
    protect_game_server: typing.Optional[builtins.bool] = None,
    role: typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole] = None,
    vpc_subnets: typing.Optional[typing.Union[_aws_cdk_aws_ec2_ceddda9d.SubnetSelection, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__78641a197786fbf0ecb0cc47203e19aadf2baf2f21a8db53e544cc8922167bdc(
    *,
    game_session_queue_arn: typing.Optional[builtins.str] = None,
    game_session_queue_name: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d7ec2128913b26e96704a23d51e9a927d5c7288d3b8b35b1869614f35fa19015(
    *,
    destinations: typing.Sequence[IGameSessionQueueDestination],
    game_session_queue_name: builtins.str,
    allowed_locations: typing.Optional[typing.Sequence[builtins.str]] = None,
    custom_event_data: typing.Optional[builtins.str] = None,
    notification_target: typing.Optional[_aws_cdk_aws_sns_ceddda9d.ITopic] = None,
    player_latency_policies: typing.Optional[typing.Sequence[typing.Union[PlayerLatencyPolicy, typing.Dict[builtins.str, typing.Any]]]] = None,
    priority_configuration: typing.Optional[typing.Union[PriorityConfiguration, typing.Dict[builtins.str, typing.Any]]] = None,
    timeout: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0b3232859da16b7aade55f24dcd15023d4567f8b71ec1a2c52f45e83a0e4d6e0(
    grantee: _aws_cdk_aws_iam_ceddda9d.IGrantable,
    *actions: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__eb2e31bcab4aa310be1c38dd2ab3f2b978168d82caac15a042b955b86628ef1b(
    metric_name: builtins.str,
    *,
    account: typing.Optional[builtins.str] = None,
    color: typing.Optional[builtins.str] = None,
    dimensions_map: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    id: typing.Optional[builtins.str] = None,
    label: typing.Optional[builtins.str] = None,
    period: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
    region: typing.Optional[builtins.str] = None,
    stack_account: typing.Optional[builtins.str] = None,
    stack_region: typing.Optional[builtins.str] = None,
    statistic: typing.Optional[builtins.str] = None,
    unit: typing.Optional[_aws_cdk_aws_cloudwatch_ceddda9d.Unit] = None,
    visible: typing.Optional[builtins.bool] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f6cb0fd1e45ac1f577cf83574c1b14669b35aff1cfbe39ce2729783223f80f7a(
    metric_name: builtins.str,
    *,
    account: typing.Optional[builtins.str] = None,
    color: typing.Optional[builtins.str] = None,
    dimensions_map: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    id: typing.Optional[builtins.str] = None,
    label: typing.Optional[builtins.str] = None,
    period: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
    region: typing.Optional[builtins.str] = None,
    stack_account: typing.Optional[builtins.str] = None,
    stack_region: typing.Optional[builtins.str] = None,
    statistic: typing.Optional[builtins.str] = None,
    unit: typing.Optional[_aws_cdk_aws_cloudwatch_ceddda9d.Unit] = None,
    visible: typing.Optional[builtins.bool] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a50e8154463101cfe0acdbd65a141a2f33f32607ac527b4e424e2760e53974f1(
    metric_name: builtins.str,
    *,
    account: typing.Optional[builtins.str] = None,
    color: typing.Optional[builtins.str] = None,
    dimensions_map: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    id: typing.Optional[builtins.str] = None,
    label: typing.Optional[builtins.str] = None,
    period: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
    region: typing.Optional[builtins.str] = None,
    stack_account: typing.Optional[builtins.str] = None,
    stack_region: typing.Optional[builtins.str] = None,
    statistic: typing.Optional[builtins.str] = None,
    unit: typing.Optional[_aws_cdk_aws_cloudwatch_ceddda9d.Unit] = None,
    visible: typing.Optional[builtins.bool] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__bb308959f14dabfed37c94209e0915eae0046d24f306489e7e1089933e4ccd89(
    metric_name: builtins.str,
    *,
    account: typing.Optional[builtins.str] = None,
    color: typing.Optional[builtins.str] = None,
    dimensions_map: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    id: typing.Optional[builtins.str] = None,
    label: typing.Optional[builtins.str] = None,
    period: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
    region: typing.Optional[builtins.str] = None,
    stack_account: typing.Optional[builtins.str] = None,
    stack_region: typing.Optional[builtins.str] = None,
    statistic: typing.Optional[builtins.str] = None,
    unit: typing.Optional[_aws_cdk_aws_cloudwatch_ceddda9d.Unit] = None,
    visible: typing.Optional[builtins.bool] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__87a43d24fc90cc52e193a87bea4e3e876df261fb5a71a0e18268bc490d1b487a(
    _scope: _constructs_77d1e7e8.Construct,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6510250919afd16d4c4d6bbae10e8435306ebb5e312a6ce7d11e010dc8dd9b63(
    *,
    port: Port,
    source: IPeer,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__38eeb158eee88455262b802bd304c5096c809aafb0994d6be07a78c309eeaba3(
    *,
    instance_type: _aws_cdk_aws_ec2_ceddda9d.InstanceType,
    weight: typing.Optional[jsii.Number] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__51da9aed387e2484fabd92a592d5c9962664ed75c99f4386aceb3966a4c0bcf6(
    *,
    region: builtins.str,
    capacity: typing.Optional[typing.Union[LocationCapacity, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d5927ec30cf31c390246d4f5cd91620953cce8312a7fc880d9df8e3c3d66884a(
    *,
    desired_capacity: typing.Optional[jsii.Number] = None,
    max_size: typing.Optional[jsii.Number] = None,
    min_size: typing.Optional[jsii.Number] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f8840f19ad853f8b5315e04970dd0ce5ff95adb7384a7f49ac85ca98bc687bbe(
    *,
    matchmaking_configuration_arn: typing.Optional[builtins.str] = None,
    matchmaking_configuration_name: typing.Optional[builtins.str] = None,
    notification_target: typing.Optional[_aws_cdk_aws_sns_ceddda9d.ITopic] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__179a3e243ff415e081f70b60e1298d914f259d43851a71a98b5fd134edf627aa(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    account: typing.Optional[builtins.str] = None,
    environment_from_arn: typing.Optional[builtins.str] = None,
    physical_name: typing.Optional[builtins.str] = None,
    region: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7d238ab385dcb4a94ac7158dcf0b7c35d37d1df2b7f2aac4980cdb67fd219833(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    matchmaking_configuration_arn: typing.Optional[builtins.str] = None,
    matchmaking_configuration_name: typing.Optional[builtins.str] = None,
    notification_target: typing.Optional[_aws_cdk_aws_sns_ceddda9d.ITopic] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fb0c4e1998ca3a69efa6e5fb13e4eb602af45edecdd69f97c1a8ed63e0b26a78(
    metric_name: builtins.str,
    *,
    account: typing.Optional[builtins.str] = None,
    color: typing.Optional[builtins.str] = None,
    dimensions_map: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    id: typing.Optional[builtins.str] = None,
    label: typing.Optional[builtins.str] = None,
    period: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
    region: typing.Optional[builtins.str] = None,
    stack_account: typing.Optional[builtins.str] = None,
    stack_region: typing.Optional[builtins.str] = None,
    statistic: typing.Optional[builtins.str] = None,
    unit: typing.Optional[_aws_cdk_aws_cloudwatch_ceddda9d.Unit] = None,
    visible: typing.Optional[builtins.bool] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7d2425c20be5f5ce626404bc1ba92acded1944eca3e6a4be3b797bb9371b83f3(
    *,
    matchmaking_configuration_name: builtins.str,
    rule_set: IMatchmakingRuleSet,
    acceptance_timeout: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
    custom_event_data: typing.Optional[builtins.str] = None,
    description: typing.Optional[builtins.str] = None,
    notification_target: typing.Optional[_aws_cdk_aws_sns_ceddda9d.ITopic] = None,
    request_timeout: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
    require_acceptance: typing.Optional[builtins.bool] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e72f6b34f251ccf25dc2f85814396b89033d882b6daef2385941c85b9f9a0156(
    *,
    matchmaking_rule_set_arn: typing.Optional[builtins.str] = None,
    matchmaking_rule_set_name: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__aac55b7eb2aa8da44cfab32e5743d05917cef63fff77ffac643b515b1fe31623(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    account: typing.Optional[builtins.str] = None,
    environment_from_arn: typing.Optional[builtins.str] = None,
    physical_name: typing.Optional[builtins.str] = None,
    region: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__21e8fcdb8f8c901f59f09a68a217b7ff098b01c5bbee77ad99eca65f22883d1a(
    metric_name: builtins.str,
    *,
    account: typing.Optional[builtins.str] = None,
    color: typing.Optional[builtins.str] = None,
    dimensions_map: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    id: typing.Optional[builtins.str] = None,
    label: typing.Optional[builtins.str] = None,
    period: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
    region: typing.Optional[builtins.str] = None,
    stack_account: typing.Optional[builtins.str] = None,
    stack_region: typing.Optional[builtins.str] = None,
    statistic: typing.Optional[builtins.str] = None,
    unit: typing.Optional[_aws_cdk_aws_cloudwatch_ceddda9d.Unit] = None,
    visible: typing.Optional[builtins.bool] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__41ee98f07075e0ce2d6c3c1744990e7d34a79e68879b404561d88738e5f22466(
    *,
    content: RuleSetContent,
    matchmaking_rule_set_name: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d9cafda50096fc350f9cc5b1c7ed43f6e6d3c926f878f41e6a1852c233640971(
    cidr_ip: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f6e81f6ee2a9d84a1b3aee29befab9a53abe967661221d80eb62a7201a98657e(
    *,
    maximum_individual_player_latency: _aws_cdk_ceddda9d.Duration,
    policy_duration: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__807daa8efeb9458bfab28ef1059e4e060051b8f8a89d4cb96ad64f80804283b6(
    port: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4f9b17c789979d40f73a7726940c2f66b5a2cf02cdbd1a2da5ba5afa03ebc7ff(
    start_port: jsii.Number,
    end_port: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8f9736f2e5142a4a1088ef03dcd38685d4abd204bf399b3b6b5b38fd4b7bce1f(
    port: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fbefa015e5d4a84fc309cfdbc4ccad9117e9eea9f7f8c857ad92a9ac5db07ce8(
    start_port: jsii.Number,
    end_port: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__67dc987c67cb3e38e0e5ff1854c8efa93b01f48235e9309346c6a96b55aad13e(
    *,
    from_port: jsii.Number,
    protocol: Protocol,
    to_port: typing.Optional[jsii.Number] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__334f74ab81f780a210829644ea1fd8ba86575c76302264e1616a64a4f588da34(
    *,
    location_order: typing.Sequence[builtins.str],
    priority_order: typing.Sequence[PriorityType],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__be244137222f30ecbe1929614ba472a54f8614aa5e1cb09e77e3df6dbcd4a484(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    game_session_queues: typing.Sequence[IGameSessionQueue],
    additional_player_count: typing.Optional[jsii.Number] = None,
    game_properties: typing.Optional[typing.Sequence[typing.Union[GameProperty, typing.Dict[builtins.str, typing.Any]]]] = None,
    game_session_data: typing.Optional[builtins.str] = None,
    manual_backfill_mode: typing.Optional[builtins.bool] = None,
    matchmaking_configuration_name: builtins.str,
    rule_set: IMatchmakingRuleSet,
    acceptance_timeout: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
    custom_event_data: typing.Optional[builtins.str] = None,
    description: typing.Optional[builtins.str] = None,
    notification_target: typing.Optional[_aws_cdk_aws_sns_ceddda9d.ITopic] = None,
    request_timeout: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
    require_acceptance: typing.Optional[builtins.bool] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__781c8df696d40f03602d3bdb2a5baff0078e995e886b25c6bafc5ccc580d95a3(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    matchmaking_configuration_arn: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7fbf1f3b09528f7cb315af51a7f12641235099066dd8d797ce40c9482c7a5395(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    matchmaking_configuration_name: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4d5a3bfbfee3f6e91502b8aa315b930ba4cac1663f67c677da613d5e4356dae3(
    game_session_queue: IGameSessionQueue,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__964b4cd698f029625433fe3a9d1ed9d87b9ad33c86cbca699f3e04a5750fb44f(
    *,
    matchmaking_configuration_name: builtins.str,
    rule_set: IMatchmakingRuleSet,
    acceptance_timeout: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
    custom_event_data: typing.Optional[builtins.str] = None,
    description: typing.Optional[builtins.str] = None,
    notification_target: typing.Optional[_aws_cdk_aws_sns_ceddda9d.ITopic] = None,
    request_timeout: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
    require_acceptance: typing.Optional[builtins.bool] = None,
    game_session_queues: typing.Sequence[IGameSessionQueue],
    additional_player_count: typing.Optional[jsii.Number] = None,
    game_properties: typing.Optional[typing.Sequence[typing.Union[GameProperty, typing.Dict[builtins.str, typing.Any]]]] = None,
    game_session_data: typing.Optional[builtins.str] = None,
    manual_backfill_mode: typing.Optional[builtins.bool] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__510e179942276e17b717c9dac3c9c38778402766783bd9ee763473b55a6bb0b5(
    *,
    new_game_sessions_per_creator: typing.Optional[jsii.Number] = None,
    policy_period: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5354ccd65eb1ccbc5870ac6dd16b6dd23cddb1833f4df0ebbf12c363778f54bf(
    *,
    rule_set_body: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a0a5602cdb30daf4f053362ebca7fcb5ca050681e1317b1e7448969763688001(
    body: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1f3e0bae77877836e083593e18191cdb0489f082859455692e225eaa93c232cb(
    path: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9e4177f5a9a4221d007c0afaa057c80e113c2851b420d8475561ee3fdcd7f0b6(
    _scope: _constructs_77d1e7e8.Construct,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3695b67c606f06a3aa5add6f464b5609bc21f42521bc364955f801406602e58c(
    *,
    content: typing.Optional[IRuleSetBody] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__cf5e16edd407d4296fc803b4b9c4ae54a060599679202852ed91ce001469c0a3(
    *,
    server_processes: typing.Sequence[typing.Union[ServerProcess, typing.Dict[builtins.str, typing.Any]]],
    game_session_activation_timeout: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
    max_concurrent_game_session_activations: typing.Optional[jsii.Number] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e0b27857db7f0cfd9fbf597ef20acdd7208fe5d681f1d1413d36c0e67ba69702(
    bucket: _aws_cdk_aws_s3_ceddda9d.IBucket,
    key: builtins.str,
    object_version: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a354a9ae95aa20c9c3ef605ca509f8d7ba3526192b9739e0c98ec864492580f8(
    _scope: _constructs_77d1e7e8.Construct,
    role: _aws_cdk_aws_iam_ceddda9d.IRole,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__96ea2755dd72bb47adfb866f8b6ffd38ebfd4f9a8af11c16bb3e55d9344dce0c(
    *,
    script_arn: builtins.str,
    role: typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__166d20549f18e89ce130b2747aaffda5a11eef3e94e661bad723cb2553d3d32f(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    account: typing.Optional[builtins.str] = None,
    environment_from_arn: typing.Optional[builtins.str] = None,
    physical_name: typing.Optional[builtins.str] = None,
    region: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1f64cc150e31309fdfed340aa86a93c06b20569f4e57ea7bb8029b03454475e5(
    *,
    content: Content,
    role: typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole] = None,
    script_name: typing.Optional[builtins.str] = None,
    script_version: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__16b9b91b83546a94dce8dcdbb8cdfceb8efe3a913f6fcbd4e9a67dbf38b78fc6(
    *,
    launch_path: builtins.str,
    concurrent_executions: typing.Optional[jsii.Number] = None,
    parameters: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__154c82c2c0fb5d36e7cc47ebca648ca30fa0731aa50bf433bc6f20396b12cbbf(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    matchmaking_configuration_name: builtins.str,
    rule_set: IMatchmakingRuleSet,
    acceptance_timeout: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
    custom_event_data: typing.Optional[builtins.str] = None,
    description: typing.Optional[builtins.str] = None,
    notification_target: typing.Optional[_aws_cdk_aws_sns_ceddda9d.ITopic] = None,
    request_timeout: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
    require_acceptance: typing.Optional[builtins.bool] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3793d6f8154e15ae69df761a8dfca36610171696829c6d3bc7d9bd1ee9e7b6d7(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    matchmaking_configuration_arn: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__07c04bfca9c496a8644c2e6e10359ca3a4954a3a29632bc3f6c59cd1e39240ad(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    matchmaking_configuration_name: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__34016871359c2c8b76308f8d09850850ca95c46f84197bbb1a714abb1558d1db(
    *,
    matchmaking_configuration_name: builtins.str,
    rule_set: IMatchmakingRuleSet,
    acceptance_timeout: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
    custom_event_data: typing.Optional[builtins.str] = None,
    description: typing.Optional[builtins.str] = None,
    notification_target: typing.Optional[_aws_cdk_aws_sns_ceddda9d.ITopic] = None,
    request_timeout: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
    require_acceptance: typing.Optional[builtins.bool] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fbfe673262616ef52c985ab1e4f7220c127e7658477cda89ab362836b7456d63(
    path: builtins.str,
    *,
    deploy_time: typing.Optional[builtins.bool] = None,
    display_name: typing.Optional[builtins.str] = None,
    readers: typing.Optional[typing.Sequence[_aws_cdk_aws_iam_ceddda9d.IGrantable]] = None,
    source_kms_key: typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey] = None,
    asset_hash: typing.Optional[builtins.str] = None,
    asset_hash_type: typing.Optional[_aws_cdk_ceddda9d.AssetHashType] = None,
    bundling: typing.Optional[typing.Union[_aws_cdk_ceddda9d.BundlingOptions, typing.Dict[builtins.str, typing.Any]]] = None,
    exclude: typing.Optional[typing.Sequence[builtins.str]] = None,
    follow_symlinks: typing.Optional[_aws_cdk_ceddda9d.SymlinkFollowMode] = None,
    ignore_mode: typing.Optional[_aws_cdk_ceddda9d.IgnoreMode] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__088d51b6537b57f99fb8a11bafc0f9452e787bbb2082ef8f1e59a5fac6f6ec3e(
    scope: _constructs_77d1e7e8.Construct,
    role: _aws_cdk_aws_iam_ceddda9d.IRole,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f91b9b3796935bd0b85afcc48cf565d44bb67b47cd97b5c0a12fbb150c5a01a7(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    account: typing.Optional[builtins.str] = None,
    environment_from_arn: typing.Optional[builtins.str] = None,
    physical_name: typing.Optional[builtins.str] = None,
    region: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9418742f4dd29cadc75ff372ca21cc393ca180dfd8ecbddf8d173d1db503bb13(
    *,
    fleet_name: builtins.str,
    instance_type: _aws_cdk_aws_ec2_ceddda9d.InstanceType,
    runtime_configuration: typing.Union[RuntimeConfiguration, typing.Dict[builtins.str, typing.Any]],
    description: typing.Optional[builtins.str] = None,
    desired_capacity: typing.Optional[jsii.Number] = None,
    locations: typing.Optional[typing.Sequence[typing.Union[Location, typing.Dict[builtins.str, typing.Any]]]] = None,
    max_size: typing.Optional[jsii.Number] = None,
    metric_group: typing.Optional[builtins.str] = None,
    min_size: typing.Optional[jsii.Number] = None,
    peer_vpc: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IVpc] = None,
    protect_new_game_session: typing.Optional[builtins.bool] = None,
    resource_creation_limit_policy: typing.Optional[typing.Union[ResourceCreationLimitPolicy, typing.Dict[builtins.str, typing.Any]]] = None,
    role: typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole] = None,
    use_certificate: typing.Optional[builtins.bool] = None,
    use_spot: typing.Optional[builtins.bool] = None,
    content: IBuild,
    ingress_rules: typing.Optional[typing.Sequence[typing.Union[IngressRule, typing.Dict[builtins.str, typing.Any]]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3cb709ea0cc9b504c842aa150aa921febee13c957d7cccc041271e52227d956c(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    account: typing.Optional[builtins.str] = None,
    environment_from_arn: typing.Optional[builtins.str] = None,
    physical_name: typing.Optional[builtins.str] = None,
    region: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__bc98cc9f235cc2aacfbddfe6a1a444c59cf0ef97ba228263887d747a1a1d29ce(
    grantee: _aws_cdk_aws_iam_ceddda9d.IGrantable,
    *actions: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2d0af285f84a831b602a9af9d540b20e6d43d46920911983823552dac38c7558(
    metric_name: builtins.str,
    *,
    account: typing.Optional[builtins.str] = None,
    color: typing.Optional[builtins.str] = None,
    dimensions_map: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    id: typing.Optional[builtins.str] = None,
    label: typing.Optional[builtins.str] = None,
    period: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
    region: typing.Optional[builtins.str] = None,
    stack_account: typing.Optional[builtins.str] = None,
    stack_region: typing.Optional[builtins.str] = None,
    statistic: typing.Optional[builtins.str] = None,
    unit: typing.Optional[_aws_cdk_aws_cloudwatch_ceddda9d.Unit] = None,
    visible: typing.Optional[builtins.bool] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b4fac722db9ba55ff9ab2e7398f85630f80ba65dd3178e24f53fa3a7f6d95e69(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    account: typing.Optional[builtins.str] = None,
    environment_from_arn: typing.Optional[builtins.str] = None,
    physical_name: typing.Optional[builtins.str] = None,
    region: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__071d438e20836fe1d308788f6e0d2a6b79508aa39024c699dea4722f8a2de060(
    metric_name: builtins.str,
    *,
    account: typing.Optional[builtins.str] = None,
    color: typing.Optional[builtins.str] = None,
    dimensions_map: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    id: typing.Optional[builtins.str] = None,
    label: typing.Optional[builtins.str] = None,
    period: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
    region: typing.Optional[builtins.str] = None,
    stack_account: typing.Optional[builtins.str] = None,
    stack_region: typing.Optional[builtins.str] = None,
    statistic: typing.Optional[builtins.str] = None,
    unit: typing.Optional[_aws_cdk_aws_cloudwatch_ceddda9d.Unit] = None,
    visible: typing.Optional[builtins.bool] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ca0b1d9cf440a1667662692eea86859a891f53c0b744ac93f409e17507bf4e1f(
    grantee: _aws_cdk_aws_iam_ceddda9d.IGrantable,
    *actions: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b257572800d0f56ff6c7ae43e8988405d4a6610a079279420d0242daedb7f071(
    metric_name: builtins.str,
    *,
    account: typing.Optional[builtins.str] = None,
    color: typing.Optional[builtins.str] = None,
    dimensions_map: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    id: typing.Optional[builtins.str] = None,
    label: typing.Optional[builtins.str] = None,
    period: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
    region: typing.Optional[builtins.str] = None,
    stack_account: typing.Optional[builtins.str] = None,
    stack_region: typing.Optional[builtins.str] = None,
    statistic: typing.Optional[builtins.str] = None,
    unit: typing.Optional[_aws_cdk_aws_cloudwatch_ceddda9d.Unit] = None,
    visible: typing.Optional[builtins.bool] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__976a3d8da3a70f4711298272591e84622378f07d7fbaf21a6fb79e1fcfacf9b2(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    content: RuleSetContent,
    matchmaking_rule_set_name: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0efb57a36d82aae0aa58424e2aa02c3da7bb454a52b9347fa7515556f78db182(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    matchmaking_rule_set_arn: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4d23589bc2e008c65b6ea37647f8ca40b5ade669c71958c8ed3911847448a599(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    matchmaking_rule_set_arn: typing.Optional[builtins.str] = None,
    matchmaking_rule_set_name: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f9d54d5a829bb4319b6cd93eb55df3f25163baefad677da868c368ff06ab685d(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    matchmaking_rule_set_name: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b53a94d5041878dcde1f2700a726c30606268bb050cc9ba15de1b5d415318799(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    content: Content,
    role: typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole] = None,
    script_name: typing.Optional[builtins.str] = None,
    script_version: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__40705d5b1c0b3bdd28986e8a7f2c3187b99a079dc8c141894e5c2433835a68b1(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    path: builtins.str,
    *,
    deploy_time: typing.Optional[builtins.bool] = None,
    display_name: typing.Optional[builtins.str] = None,
    readers: typing.Optional[typing.Sequence[_aws_cdk_aws_iam_ceddda9d.IGrantable]] = None,
    source_kms_key: typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey] = None,
    asset_hash: typing.Optional[builtins.str] = None,
    asset_hash_type: typing.Optional[_aws_cdk_ceddda9d.AssetHashType] = None,
    bundling: typing.Optional[typing.Union[_aws_cdk_ceddda9d.BundlingOptions, typing.Dict[builtins.str, typing.Any]]] = None,
    exclude: typing.Optional[typing.Sequence[builtins.str]] = None,
    follow_symlinks: typing.Optional[_aws_cdk_ceddda9d.SymlinkFollowMode] = None,
    ignore_mode: typing.Optional[_aws_cdk_ceddda9d.IgnoreMode] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d5fad313b14cfd67ea966c82bc187e0369c39b196ac64da5bdb241506aba4cd7(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    bucket: _aws_cdk_aws_s3_ceddda9d.IBucket,
    key: builtins.str,
    object_version: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__bbdad5d39daf44e1fc3fa531ba2a75151b8c39459e79b65f5329ae4f58c76e4d(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    script_arn: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8942c32bd63e56f52bb6f580411825e7de3dfdb217dffa2eea170b0b146590ee(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    script_arn: builtins.str,
    role: typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9ce95dded50fb4717285d87b394ed4234fe5244a5daae844cabcdff69627cb85(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    account: typing.Optional[builtins.str] = None,
    environment_from_arn: typing.Optional[builtins.str] = None,
    physical_name: typing.Optional[builtins.str] = None,
    region: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__acab12658d9c6cd950e90d4b6112c4156ce8e10d9afc5c09ec7bb623f57d07c2(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    content: Content,
    build_name: typing.Optional[builtins.str] = None,
    build_version: typing.Optional[builtins.str] = None,
    operating_system: typing.Optional[OperatingSystem] = None,
    role: typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole] = None,
    server_sdk_version: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__771a5b67c3c157e54cfec46c95710a5920f03bde544ac928ed1f4eb24abfd610(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    path: builtins.str,
    *,
    deploy_time: typing.Optional[builtins.bool] = None,
    display_name: typing.Optional[builtins.str] = None,
    readers: typing.Optional[typing.Sequence[_aws_cdk_aws_iam_ceddda9d.IGrantable]] = None,
    source_kms_key: typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey] = None,
    asset_hash: typing.Optional[builtins.str] = None,
    asset_hash_type: typing.Optional[_aws_cdk_ceddda9d.AssetHashType] = None,
    bundling: typing.Optional[typing.Union[_aws_cdk_ceddda9d.BundlingOptions, typing.Dict[builtins.str, typing.Any]]] = None,
    exclude: typing.Optional[typing.Sequence[builtins.str]] = None,
    follow_symlinks: typing.Optional[_aws_cdk_ceddda9d.SymlinkFollowMode] = None,
    ignore_mode: typing.Optional[_aws_cdk_ceddda9d.IgnoreMode] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__01aa7b72ddb55b4e9c06c6216b9cff2482e318d6ad65b75aa6e4fa44e197f003(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    bucket: _aws_cdk_aws_s3_ceddda9d.IBucket,
    key: builtins.str,
    object_version: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__73ffb8bc096eeb5acc087de114546008b597c2f9769d8c1115e6b0f3472974c9(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    build_arn: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f7d138525cf0c6ad71105d4422e4f3cd022412cb600abdd3c03e252467f7b478(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    build_arn: typing.Optional[builtins.str] = None,
    build_id: typing.Optional[builtins.str] = None,
    role: typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__551e40ddeafd29db40fff59984f916c22299a859d987a82afa5e44182605017c(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    build_id: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__12941e76da73d1fb0a8113ccb21bc7dcdf888b465317a85a82b38deabb69f666(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    account: typing.Optional[builtins.str] = None,
    environment_from_arn: typing.Optional[builtins.str] = None,
    physical_name: typing.Optional[builtins.str] = None,
    region: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__83ae99059a3f4b6d0eac7b382368760ade9295a9563b9f7ab96a3a3b11b363b8(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    fleet_arn: typing.Optional[builtins.str] = None,
    fleet_id: typing.Optional[builtins.str] = None,
    role: typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b00d5ccce3d0b3d9c2b51eae0baaeb059c52921521e42bf9c8d60d33da483fce(
    alias_name: builtins.str,
    *,
    description: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e24f5b505687ec117a2611e69db366a71407d445998ae7af4fc53086225d78ec(
    region: builtins.str,
    desired_capacity: typing.Optional[jsii.Number] = None,
    min_size: typing.Optional[jsii.Number] = None,
    max_size: typing.Optional[jsii.Number] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1d7c1cafa704235e8c7c22f0babc5bcb076a129181d6569ac69e172e533f69c5(
    grantee: _aws_cdk_aws_iam_ceddda9d.IGrantable,
    *actions: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5bced8236ec32c93a595c407ba901878cc9d2256e8311b71c182205b0fb40a66(
    metric_name: builtins.str,
    *,
    account: typing.Optional[builtins.str] = None,
    color: typing.Optional[builtins.str] = None,
    dimensions_map: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    id: typing.Optional[builtins.str] = None,
    label: typing.Optional[builtins.str] = None,
    period: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
    region: typing.Optional[builtins.str] = None,
    stack_account: typing.Optional[builtins.str] = None,
    stack_region: typing.Optional[builtins.str] = None,
    statistic: typing.Optional[builtins.str] = None,
    unit: typing.Optional[_aws_cdk_aws_cloudwatch_ceddda9d.Unit] = None,
    visible: typing.Optional[builtins.bool] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__68991ef0ce6784f9f286e5d071bc251c86b2b925331565c0ec03af23ef683754(
    scope: _constructs_77d1e7e8.Construct,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9d7010ffc2b4c1fb02cd1e07fe5bb1d68676dd11570fed2cd459c0505f8e45a8(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    game_server_group_name: builtins.str,
    instance_definitions: typing.Sequence[typing.Union[InstanceDefinition, typing.Dict[builtins.str, typing.Any]]],
    launch_template: _aws_cdk_aws_ec2_ceddda9d.ILaunchTemplate,
    vpc: _aws_cdk_aws_ec2_ceddda9d.IVpc,
    auto_scaling_policy: typing.Optional[typing.Union[AutoScalingPolicy, typing.Dict[builtins.str, typing.Any]]] = None,
    balancing_strategy: typing.Optional[BalancingStrategy] = None,
    delete_option: typing.Optional[DeleteOption] = None,
    max_size: typing.Optional[jsii.Number] = None,
    min_size: typing.Optional[jsii.Number] = None,
    protect_game_server: typing.Optional[builtins.bool] = None,
    role: typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole] = None,
    vpc_subnets: typing.Optional[typing.Union[_aws_cdk_aws_ec2_ceddda9d.SubnetSelection, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__48d603aa779f14f81d3db2b3cd7ae4a0ff5b9261c16733151a59f20ac6a829e0(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    auto_scaling_group_arn: builtins.str,
    game_server_group_arn: typing.Optional[builtins.str] = None,
    game_server_group_name: typing.Optional[builtins.str] = None,
    role: typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__846520817af100925d03fe3dc61ab7cd70c568bf5abfde70677e06e42c232636(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    destinations: typing.Sequence[IGameSessionQueueDestination],
    game_session_queue_name: builtins.str,
    allowed_locations: typing.Optional[typing.Sequence[builtins.str]] = None,
    custom_event_data: typing.Optional[builtins.str] = None,
    notification_target: typing.Optional[_aws_cdk_aws_sns_ceddda9d.ITopic] = None,
    player_latency_policies: typing.Optional[typing.Sequence[typing.Union[PlayerLatencyPolicy, typing.Dict[builtins.str, typing.Any]]]] = None,
    priority_configuration: typing.Optional[typing.Union[PriorityConfiguration, typing.Dict[builtins.str, typing.Any]]] = None,
    timeout: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6cb33d7a6d095570518d46828dd10e1034ae4dfa9fd69413f0de6b941264bc66(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    game_session_queue_arn: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9abe3c8dfc0d7493f78870441d89e451d4012dea9b62447d44af88e912a94a09(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    game_session_queue_arn: typing.Optional[builtins.str] = None,
    game_session_queue_name: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__46707c5adccba8071b9aa0cfec2dac4419e4abf4a3801b5b7ad8ebe85740cf31(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    game_session_queue_name: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0726b630a813fb456a6509ecd3b21784fcc7d6f8936316cac6394bff525110dc(
    destination: IGameSessionQueueDestination,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9ca155302605299f39ebc02214b9c2ec1ec3ecb1d07672160bbfe85b446feb43(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    alias_name: builtins.str,
    description: typing.Optional[builtins.str] = None,
    fleet: typing.Optional[IFleet] = None,
    terminal_message: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__02b9841ad4d64fe609fa4d225adb886af4e5300981093e8e23b9dade3b39154d(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    alias_arn: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0a0852329e6582921470d2df6eb3f175d7598559ee0bbb5a199fc9ba6eed831a(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    alias_arn: typing.Optional[builtins.str] = None,
    alias_id: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fddb71a5d89a4ff9a839d371c159d1513dc760d472525e873ec06490b9ed62db(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    alias_id: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b0f96582da85e159c90711da4321ddc6d10a9be0aaa75bf5d139f2ada0d0a9ec(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    content: IBuild,
    ingress_rules: typing.Optional[typing.Sequence[typing.Union[IngressRule, typing.Dict[builtins.str, typing.Any]]]] = None,
    fleet_name: builtins.str,
    instance_type: _aws_cdk_aws_ec2_ceddda9d.InstanceType,
    runtime_configuration: typing.Union[RuntimeConfiguration, typing.Dict[builtins.str, typing.Any]],
    description: typing.Optional[builtins.str] = None,
    desired_capacity: typing.Optional[jsii.Number] = None,
    locations: typing.Optional[typing.Sequence[typing.Union[Location, typing.Dict[builtins.str, typing.Any]]]] = None,
    max_size: typing.Optional[jsii.Number] = None,
    metric_group: typing.Optional[builtins.str] = None,
    min_size: typing.Optional[jsii.Number] = None,
    peer_vpc: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IVpc] = None,
    protect_new_game_session: typing.Optional[builtins.bool] = None,
    resource_creation_limit_policy: typing.Optional[typing.Union[ResourceCreationLimitPolicy, typing.Dict[builtins.str, typing.Any]]] = None,
    role: typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole] = None,
    use_certificate: typing.Optional[builtins.bool] = None,
    use_spot: typing.Optional[builtins.bool] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ef7abe85750cf6ce2c0acf9b4d63ece12f0d8efc194a92c524abd18fef5d5d93(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    build_fleet_arn: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a61afc3b99684bbcad3253856e305c24c5d37c7a1b410354b519756b5c5a3dfd(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    build_fleet_id: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0ff1a5dfaf3ccd3895ed18ca2bad230faa4172c04c6bed9596351df73b837a68(
    source: IPeer,
    port: Port,
) -> None:
    """Type checking stubs"""
    pass
