from atikin_utils import snake_case, camel_case, kebab_case, truncate, safe_format, slugify

def test_cases():
    assert snake_case("HelloWorld Example") == "hello_world_example"
    assert camel_case("hello_world example") == "HelloWorldExample"
    assert camel_case("hello world", lower_first=True).startswith("hello")
    assert kebab_case("Hello World_Test") == "hello-world-test"
    assert truncate("abcdef", 3) == "..."
    assert safe_format("Hi {name} {x}", name="Jamshed") == "Hi Jamshed {x}"
    assert slugify("Hello, World!") == "hello-world"
