from sherlock_ai import hardcoded_value_detector
import asyncio
from sherlock_ai import SherlockAI, LoggingConfig
config = LoggingConfig(
    log_format_type="json"
)
sherlock_ai = SherlockAI(config=config)
sherlock_ai.setup()
# @hardcoded_value_detector
# def first_function():
#     message = 'Hello World'
#     number = 42
#     print(message)
#     print(f'Value: {number}')


# @hardcoded_value_detector
# def second_function():
#     url = 'https://example.com'
#     timeout = 30
#     print(f'Connecting to {url} with timeout {timeout}')


@hardcoded_value_detector
async def third_function():
    s = 'Kunal Aggarwal'
    num = 70
    print(f'Connecting to {s} with timeout {num}')

    @hardcoded_value_detector
    async def second_function():
        url = 'https://example.com'
        timeout = 30
        print(f'Connecting to {url} with timeout {timeout}')

    await second_function()


if __name__ == '__main__':
    # first_function()
    # second_function()
    asyncio.run(third_function())
