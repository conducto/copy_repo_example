# Using copy_repo in Conduto Pipelines

This example shows how your pipeline can use local code while you iterate locally, and remote code when triggered by a [Conduto Integration](https://conducto.com/docs/integrations).

Specifically, it uses `copy_repo` and `dockerfile` together.
If that's not your case, then you can safely ignore the parts about the docker build context.

## The Sample App

The sample app is packaged as a docker container.

    ❯ docker build . -t myfiglet
    ❯ docker run myfiglet
     _   _      _ _        __        __         _     _ _
    | | | | ___| | | ___   \ \      / /__  _ __| | __| | |
    | |_| |/ _ \ | |/ _ \   \ \ /\ / / _ \| '__| |/ _` | |
    |  _  |  __/ | | (_) |   \ V  V / (_) | |  | | (_| |_|
    |_| |_|\___|_|_|\___/     \_/\_/ \___/|_|  |_|\__,_(_)

You can also install it locally.

    ❯ pip install .
    ❯ myfiglet
     _   _      _ _        __        __         _     _ _
    | | | | ___| | | ___   \ \      / /__  _ __| | __| | |
    | |_| |/ _ \ | |/ _ \   \ \ /\ / / _ \| '__| |/ _` | |
    |  _  |  __/ | | (_) |   \ V  V / (_) | |  | | (_| |_|
    |_| |_|\___|_|_|\___/     \_/\_/ \___/|_|  |_|\__,_(_)

    ❯ pip uninstall myfiglet

## Using it in a pipeline

The [Dockerfile](./Dockerfile) already knows where the code needs to go:

```
COPY . /usr/local/src/myapp
```

The challenge is to make `/usr/local/src/myapp` contain the right code at the right times:

- local code when developing locally
- *compare branch* code when testing a pull request
- *target branch* code when testing a merge
- live local code in a debug session

`copy_repo=True` handes this for the most part, but it needs some cues from the [Image](https://conducto.com/docs/basics/images) object:

```
img = co.Image(dockerfile="Dockerfile",
               copy_repo=True,
               path_map={'.':'/usr/local/src/myapp'})
```

- `dockerfile` instructions for building the image filesystem
- `copy_repo` let Conducto choose the source repo based on context
- `path_map` mount hostside files at containerside paths (for debug sessions)

## Conducto's Process

When working with the pipeline defined in [pipeline.py](./pipeline.py), Conducto does the following:

#### build the image

1. Decide which repo
 - if user launched, copy from user's machine
 - if integration launched, copy from appropriate branch
 - user can override by using `copy_url` and `copy_branch` instead of `copy_repo`

2. Set the build context to the repo and `docker build`
 - if `copy_repo=True` use the repo root for the build context
 - otherwise use the dockerfile directory as the build context
 - user can override by setting `context='somewhere/else'`

3. Copy the whole repo into `/conducto/src` for use by pipeline nodes

#### start a live debug session

1. Mount local files overtop image files based on `path_map`
 - `{".":` -- take the local directory containing the pipeline
 - `"/usr/local/src/myapp}` -- and put mount it here in the image

## Scenarios

There are a few ways to run this app:

 - Without Docker or Conducto
 - User-Launched Conducto Pipeleine
 - Integration-Launched Conducto Pipeline
 - Conducto Live Debug Session

The sections below explain how we can end up with the right code each time.

#### Without Docker or Conducto

You can install this app to your local system like:
```
pip install -e .
```

The `-e` flag (for "editable") tells pip to install the package using symlinks--instead of making copies.
This is helpful during development because you can edit the code and rerun it without needing to run `pip install .` for every change.


#### Docker Only, No Conducto

This command will create a docker image:

```
docker build . -t myapp
```

The installation commands in [`Dockerfile`](./Dockerfile) handle app setup, and you can run it with something like:

```
docker run myapp
```

This is handy because that image is portable.
Wherever it goes, `/usr/local/src/myapp` and its other dependencies go also.

#### User-Launched Conducto Pipeline

If you're launching a pipeline manually, `copy_repo=True` tells Conducto to provide Docker with files from wherever you're launching it.
It's still the `COPY` directive in the Dockerfile that actually copies the files into the image.

To make updated files accessible to the pipeline, simply rebuild the node images.

#### Integration-Launched Conducto Pipeline

If a [Conducto Integtaion](https://www.conducto.com/docs/integrations) launches the pipeline, `copy_repo=True` provides Docker with a branch that [depends on the integration](https://www.conducto.com/docs/integrations/github#events-and-parameters).

From there, the process continues like in the previous section.

#### Conducto Live Debug Session

If you opt to [debug live code](https://www.conducto.com/docs/basics/debugging#debugging-live-code) your local code will be mounted in the debug container.
This is where `path_map` comes in.

In this case, the pipeline's parent  gets mounted at `/usr/local/src/myapp`, which hides whatever Docker copied into the image.

If the Dockerfile used `pip install -e .` the rest of the container filesystem will be set up to use the mounted code.
This lets you make changes that show up in the debug session without needing to restart the session.
