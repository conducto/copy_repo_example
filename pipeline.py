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

if __name__ == "__main__":
    co.main(default=main)
