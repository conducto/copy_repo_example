# copy_repo

This example shows how your pipeline can use local code while you iterate locally, and remote code when triggered by a [Conduto Integration](https://conducto.com/docs/integrations).

The [Dockerfile](./Dockerfile) knows where the code needs to go:

```
COPY . /usr/local/src/myapp
```

The challenge is to make `/usr/local/src/myapp` contain the right code at the right times.  We achieve it like this:

```
img = co.Image(dockerfile="Dockerfile",
               copy_repo=True,
               path_map={'.':'/usr/local/src/myapp'})
```

- `dockerfile` instructions for building the image filesystem
- `copy_repo` let Conducto choose the source repo based on context
- `path_map` mount hostside files at containerside paths (for debug sessions)

# Scenarios

There are a few ways to run this app

 - Without Docker or Conducto
 - Without Conducto
 - User-Launched Conducto Pipeleine
 - Integration-Launched Conducto Pipeline
 - Conducto Live Debug Session

The sections below explain how `/usr/local/src/myapp` ends up with the right code each time.

## Without Docker or Conducto

You can install this app to your local system like:
```
pip install -e .
```

The `-e` flag (for "editable") tells pip to install the package using symlinks--instead of making copies.
This is helpful during development because you can edit the code and rerun it without needing to run `pip install .` for every change.


## Docker Only, No Conducto

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

## User-Launched Conducto Pipeline

If you're launching a pipeline manually, `copy_repo=True` tells Conducto to provide Docker with files from wherever you're launching it.
It's still the `COPY` directive in the Dockerfile that actually copies the files into the image.

To make updated files accessible to the pipeline, simply rebuild the node images.

## Integration-Launched Conducto Pipeline

If a [Conducto Integtaion](https://www.conducto.com/docs/integrations) launches the pipeline, `copy_repo=True` provides Docker with a branch that [depends on the integration](https://www.conducto.com/docs/integrations/github#events-and-parameters).

From there, the process continues like in the previous section.

## Conducto Live Debug Session

If you opt to [debug live code](https://www.conducto.com/docs/basics/debugging#debugging-live-code) your local code will be mounted in the debug container.
This is where `path_map` comes in.

In this case, the pipeline's parent  gets mounted at `/usr/local/src/myapp`, which hides whatever Docker copied into the image.

If the Dockerfile uses `pip install -e .` the rest of the container filesystem will be set up to reference the mounted code.
This lets you make changes that show up in the debug session without needing to restart it.
