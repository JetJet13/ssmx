<p align="center">
    <img src="https://user-images.githubusercontent.com/8130149/50049737-de4c4180-00b9-11e9-977a-f8432d207365.png">
</p>

# ssmx

`ssmx` is a CLI tool for injecting parameters stored in AWS SSM into executables.

It also provides commands to retrieve and set parameters in AWS SSM.

## Installation

```
pip install ssmx
```

## Usage

Running:

```
ssmx --help
```

## Configuring Credentials

The Following authentication methods are supported:

- Environment variables
- Shared credential file (~/.aws/credentials)
- AWS config file (~/.aws/config)
- AWS profiles

For more details please see [here](http://boto3.readthedocs.io/en/latest/guide/configuration.html).

### List parameters

List all parameters:

```
ssmx list
```

Output:

```
+------------------------------------+---------------+
| Name                               | Description   |
+====================================+===============+
| /platform/infra/testing            | Test param    |
+------------------------------------+---------------+
| MY_KEY                             | MY TEST KEY   |
+------------------------------------+---------------+
```

Filter parameters by name:

```
ssmx list --name my-app
```

Will list parameters starting with `my-app`

```
+---------------------+----------------------+
| Name                | Description          |
+=====================+======================+
| my-app.hostname     | my app hostname      |
| my-app.secret-key   | hush puppy           |
+---------------------+----------------------+
```

### Delete Parameters

```
ssmx delete --name <MY_KEY>
```

Will delete the parameter `MY_KEY`. Invalid parameters are ignored and printed on stdout.

Output:

```
+----------------------+
| Deleted Parameters   |
+======================+
| MY_KEY               |
+----------------------+
```

### Get parameters

```bash
ssmx get --name <MY_KEY>
```

Will retrieve and decrypt the param MY_KEY
Output:

```
+--------+---------+
| Name   | Value   |
+========+=========+
| MY_KEY | MY_VAL  |
+--------+---------+
```

### Put parameters

```bash
ssmx put
--name <name>
--value <value>
--description <description> # optional
--encrypt # optional
--key-id <kms_key_id> # required only when --encrypt is specified
```

**Important Note:** `put` behaves like an upsert, meaning if no entry exists with the name provided, it will create a new entry, and if an entry already exists with the name provided, it will overwrite the current value with the value provided.

### Provide env variables to an executable

```
ssmx exec --env-file <file_path> -- <executable>
```

Using the `exec` command, you can specify an `env` file that contains plain and secret values. Secret values need to be provided in the following format:

```bash
PLAIN_ENV_VAR=hello world
SECRET_ENV_VAR=ssm:<MY_KEY>
```

#### Example

Let's assume we are working with a node.js application that requires specific secret envrionment variables for specific environments. In other words, our application depends on `.env` files to contain the environment variables it needs to function correctly for each environment it's deployed in.

Suppose our `dev.env` file looks like the following

```bash
THIRD_PARTY_HOSTNAME=https://api.third-party.com
THIRD_PARTY_ACCESS_TOKEN=ssm:my-app.dev-third-party-access-token
```

We now need to pass this `dev.env` file to `ssmx` to fetch and decrypt the value for `THIRD_PARTY_ACCESS_TOKEN` and then inject the two env. variables into the process that will run our node.js application.

```bash
$ ssmx exec --env-file ./env/dev.env -- npm start
```

#### Example with --name parameter

Let's simplify our example from above and let's assume we store all our plain and secret env. variables in AWS SSM and we don't use `.env` files.

We also prefix our keys in AWS SSM with `<env>-my-app`, i.e.

```
+--------------------------------------+------------------------------+
| Name                                 | Value                        |
+======================================+==============================+
| /dev-my-app/third-party-hostname     | https://api.third-party.com  |
| /dev-my-app/third-party-access-token | shhhh-my-access-token        |
+--------------------------------------+------------------------------+
```

We can then acheive the same result in the previous example with the following command

```bash
$ ssmx exec --name dev-my-app -- npm start
```

Now this feature is really handy because if you're using docker to containerize your applications and AWS ECS to host your containers, you can simply provide an environment variable in your container definition, (i.e. `APP_NAME` ) to differentiate between each environment.

For example, in our Dockerfile we can do the following 

```docker
ENTRYPOINT [ "./run-app.sh" ]
```

./run-app.sh

```bash
#!/usr/bin/env bash
set -e
echo "Starting up..."

# $APP_NAME is exposed by the container definition 
ssmx exec --name $APP_NAME -- npm start
```

#### Important Note

If you plan to use the `--name` parameter with `ssmx exec`, you need to follow a specific format for the keys you create in AWS SSM. The keys need to follow the `path` format which works as follows:

```bash
/<root-path-prefix>/<another-path-prefix>/.../<MY_KEY>

# examples
/my-app/third-party-hostname
/my-app/dev/third-party-hostname
```

You can read in more detail about paths [here](https://docs.aws.amazon.com/systems-manager/latest/APIReference/API_GetParametersByPath.html#systemsmanager-GetParametersByPath-request-Path)

### License

`ssmx` is released under [MIT](./LICENSE)

### Inspirations

This project is a fork from HelloFresh's [ssm-cli](https://github.com/hellofresh/ssm-cli) and drew inspiration from the following projects:

- [Chamber](https://github.com/segmentio/chamber)
- [kms-env](https://github.com/ukayani/kms-env)
- [dotenv](https://github.com/theskumar/python-dotenv)
