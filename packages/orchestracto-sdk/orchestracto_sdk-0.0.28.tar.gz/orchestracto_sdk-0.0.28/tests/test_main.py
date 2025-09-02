from orc_sdk.main import workflow, task, SROBlock, get_steps


def test_main():

    @task()
    def foo():
        print("foo")

    @task()
    def bar(key: str):
        print(f"bar {key}")

    @task()
    def xyz():
        print("xyz")

    @task()
    def abc():
        print("abc")

    #
    #                    /foo \
    #                abc/       xyz\
    #              /     \ bar/      \
    #  foo -> bar /                     \
    #             \      foo-------------bar
    #               xyz/
    #                   \bar
    #

    foo_step = foo()

    bar_step = foo_step >> bar(key="some_key")

    abc_step = bar_step >> abc()
    xyz_step = bar_step >> xyz()

    last_xyz_step = abc_step >> SROBlock(foo(), bar()) >> xyz()

    xyz_step >> bar()
    last_foo_step = xyz_step >> foo()

    last_bar_step = SROBlock(last_xyz_step, last_foo_step) >> bar()

    stlist = get_steps(foo_step)
    pass


def test_simple():
    @task()
    def foo():
        print("foo")

    @task()
    def bar():
        print("bar")

    @task()
    def fin():
        print("fin")

    foobar = SROBlock(foo().with_id("the_foo"), bar().with_id("the_bar"))
    foobar >> fin().with_id("the_fin")

    pass
