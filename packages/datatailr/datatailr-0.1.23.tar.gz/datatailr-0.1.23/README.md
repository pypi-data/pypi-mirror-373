<div style="text-align: center;">
  <a href="https://www.datatailr.com/" target="_blank">
    <img src="https://s3.eu-west-1.amazonaws.com/datatailr.com/assets/datatailr-logo.svg" alt="Datatailr Logo" />
  </a>
</div>

---

**Datatailr empowers your team to streamline analytics and data workflows
from idea to production without infrastructure hurdles.**

# What is Datatailr?

Datatailr is a platform that simplifies the process of building and deploying data applications.

It makes it easier to run and maintain large-scale data processing and analytics workloads.

## What is this package?
This is the Python package for Datatailr, which allows you to interact with the Datatailr platform.

It provides the tools to build, deploy, and manage batch jobs, data pipelines, services and analytics applications.

Datatailr manages the underlying infrastructure so your applications can be deployed in an easy, secure and scalable way.

## Installation

### Installing the `dt` command line tool
Before you can use the Datatailr Python package, you need to install the `dt` command line tool.
**[INSTALLATION INSTRUCTIONS FOR DATATAILR GO HERE]**

### Installing the Python package
You can install the Datatailr Python package using pip:
```bash
pip install datatailr
```

### Testing the installation
```python
import datatailr

print(datatailr.__version__)
print(datatailr.__provider__)
```


## Quickstart
The following example shows how to create a simple data pipeline using the Datatailr Python package.

```python
from datatailr.scheduler import batch_job, Batch

@batch_job()
def func_no_args() -> str:
    return "no_args"


@batch_job()
def func_with_args(a: int, b: float) -> str:
    return f"args: {a}, {b}"

with Batch(name="MY test DAG", local_run=True) as dag:
    for n in range(2):
        res1 = func_no_args().alias(f"func_{n}")
        res2 = func_with_args(1, res1).alias(f"func_with_args_{n}")
```

Running this code will create a graph of jobs and execute it.
Each node on the graph represents a job, which in turn is a call to a function decorated with `@batch_job()`.

Since this is a local run then the execution of each node will happen sequentially in the same process.

To take advantage of the datatailr platform and execute the graph at scale, you can run it using the job scheduler as presented in the next section.

## Execution at Scale
To execute the graph at scale, you can use the Datatailr job scheduler. This allows you to run your jobs in parallel, taking advantage of the underlying infrastructure.

You will first need to separate your function definitions from the DAG definition. This means you should define your functions as a separate module, which can be imported into the DAG definition.


```python
# my_module.py

from datatailr.scheduler import batch_job

@batch_job()
def func_no_args() -> str:
    return "no_args"


@batch_job()
def func_with_args(a: int, b: float) -> str:
    return f"args: {a}, {b}"
```

To use these functions in a batch job, you just need to import them and run in a DAG context:

```python
from my_module import func_no_args, func_with_args
from datatailr.scheduler import Batch, Schedule

schedule = Schedule(at_hours=0)

with Batch(name="MY test DAG", schedule=schedule) as dag:
    for n in range(2):
        res1 = func_no_args().alias(f"func_{n}")
        res2 = func_with_args(1, res1).alias(f"func_with_args_{n}")
```

This will submit the entire DAG for execution, and the scheduler will take care of running the jobs in parallel and managing the resources.
The DAG in the example above will be scheduled to run daily at 00:00.

___
Visit [our website](https://www.datatailr.com/) for more!
