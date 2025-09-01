[positional-arguments]
run *FLAGS:
    pipx run --editable -- . "$@"

clean:
    rm -rfv src/*.egg-info*

verify:
    pre-commit run --all-files
