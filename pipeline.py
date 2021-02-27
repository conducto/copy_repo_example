import conducto as co

img = co.Image(dockerfile="./Dockerfile", copy_repo=True, path_map={'.':'/usr/local/src/myapp'})

def main() -> co.Parallel:
    with co.Parallel(image=img) as node:
        node["count underscores"] = co.Exec(
            """
            set -euox pipefail
            myfiglet | tr -cd '_' | wc -c | tee count.txt
            grep '59' count.txt
            """)
        node["tree returns zero"] = co.Exec(
            """
            set -euox pipefail
            mytree
            """)
    return node

def pr() -> co.Parallel:
    with co.Serial(image=img) as node:


        # code will be in /mnt/conducto, but either:
        # - we need it in /usr/local/src/myapp instead
        # - we need to run:
        #   cd /mnt/conducto && pip install -e .
        #   for each node that needs to run the app

        # both are ugly, what am I missing?

        node["prep"] = co.Exec("echo what goes here?")
        node["test"] = main()
    return node





if __name__ == "__main__":
    co.main(default=main)
