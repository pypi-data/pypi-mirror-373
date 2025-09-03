from ..reporting.report import report


def skip_test(*, tags: str) -> bool:
    """
    Checks if we need to Skip the test or not
    returns True for skipping the test
    returns False for not skipping the test
    """
    # Get the runner tags from the report object
    # Runner tags are saved to report object and i accessed through the whole test execution
    runner_tags: tuple = report.summary.test.tags
    # Check if we have any tags for test execution
    if not runner_tags:
        # If no tags are present then we will not skip the test
        return False
    # Check if the tags is a string
    if not isinstance(tags, str):
        # If tags is not a string then we will not skip the test.
        # Testers need to provide the tags in string format to even check the tags skip test logic
        return False
    # Strip the tags. Remove any leading or trailing spaces
    tags: str = tags.strip()
    # Convert the test tags string with #tags to list separated by #
    test_tags: list = tags.split("#") if tags.startswith('#') else []
    # Strip all tags and also remove empty tags
    test_tags: list = [test_tag.strip() for test_tag in test_tags if test_tag.strip()]
    # Check for #ALWAYS (This will run for all tag cases, eg: login api)
    if 'ALWAYS' in test_tags:
        # If ALWAYS is present in the test tags then we will not skip the test
        return False
    # Check if any of the runner test tag is present in the current test else skip the test
    if any(runner_tag in test_tags for runner_tag in runner_tags):
        return False
    # Skip the test
    return True
