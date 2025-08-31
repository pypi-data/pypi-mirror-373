# simple-lambda
`simple-lambda` is a script that wraps around [uv](https://docs.astral.sh/uv/) to publish simple scripts to AWS Lambda. 

The core idea surrounds [PEP-723](https://peps.python.org/pep-0723/) inline metadata scripts which uv has great [support](https://docs.astral.sh/uv/guides/scripts/#declaring-script-dependencies) for.

## Prerequisites
- [uv](https://docs.astral.sh/uv/): the intention is to use the install UV.
- [aws cli](https://docs.aws.amazon.com/cli/latest/userguide/cli-chap-getting-started.html) configured.

## Installation

Optional installation as a tool.

```bash
uv tool install simple-lambda
```

Use `uvx simple-lambda` if you don't want to install it as a tool.


## Usage
### Deploying a package
```
 Usage: simple-lambda deploy [OPTIONS] FUNCTION_NAME FILE_PATH                                                         
                                                                                                                       
╭─ Arguments ─────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ *    function_name      TEXT  [required]                                                                            │
│ *    file_path          FILE  Path to the main Python file containing the Lambda function handler. [required]       │
╰─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
╭─ Options ───────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ --help          Show this message and exit.                                                                         │
╰─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
```

Define the lambda function first via the UI or using something like terraform.

Create a script locally:
```bash
touch my_code.py
```

Add dependencies using UV:
```bash
uv add --script my_code.py requests
```

Optionally lock dependencies using UV:
```bash
uv lock --script my_code.py
```

Once you finish adding your code to the file. You can now deploy it:
```bash
uvx simple-lambda deploy lambda_function_name my_code.py
```

`simple-lambda` will automatically handle the dependencies based on the architecture and the runtime defined for the lambda function.

### Build package only
If you only want to build the zip file, you can use the build command. You will however need to specify the architecture and python version.
```
 Usage: simple-lambda build [OPTIONS] FILE_PATH                                                                        
                                                                                                                       
╭─ Arguments ─────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ *    file_path      FILE  Path to the main Python file containing the Lambda function handler. [required]           │
╰─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
╭─ Options ───────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ *  --architecture          [x86_64|arm64]  The target architecture of the lambda. [required]                        │
│    --output                FILE            Path to the output .zip file. [default: deployment_package.zip]          │
│    --python-version        TEXT            The Python version for the Lambda deployment package. [default: 3.13]    │
│    --help                                  Show this message and exit.                                              │
╰─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
```
