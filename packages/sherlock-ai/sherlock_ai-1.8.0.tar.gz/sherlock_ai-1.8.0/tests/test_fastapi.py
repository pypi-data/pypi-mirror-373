# from constants import DEFAULT_GREETING, MINUTE_INTERVAL, USER_STATUS_MESSAGE

from fastapi import FastAPI, Request
from sherlock_ai import get_logger, set_request_id
import uuid
from sherlock_ai import log_performance, monitor_memory, monitor_resources, hardcoded_value_detector
from sherlock_ai.analysis import smart_check
from sherlock_ai.monitoring import sherlock_error_handler, sherlock_performance_insights
import time
from tests.test_configuration import test_decorator_function_source
# from tests.helper_nested import helper_nested
logger = get_logger('ApiLogger')


def create_app():
    app = FastAPI()

    @app.middleware('http')
    # @log_performance
    # @monitor_memory
    # @monitor_resources
    async def request_id_middleware(request: Request, call_next):
        request_id = set_request_id()
        request.state.request_id = request_id
        logger.info(f'Request started')
        response = await call_next(request)
        logger.info(f'Request completed')
        response.headers['X-Request-ID'] = request_id
        return response

    @app.get('/health')
    # @log_performance(include_args=True)
    # @monitor_memory
    # @monitor_resources
    async def health_check():
        try:
            # helper_nested(1)
            logger.info('Health check')
            print(1 / 0)
            return {'message': 'OK'}
        except Exception as e:
            logger.error(f'Error in health check: {e}')
            raise

    @app.get('/health-2')
    # @sherlock_performance_insights(latency=3, include_args=True)
    # @log_performance(include_args=True)
    async def health_check_2():
        test_decorator_function_source()
        time.sleep(6)
        logger.info('Health check 2')
        return {'message': 'OK'}

    @app.get('/greet')
    # @smart_check
    # @sherlock_error_handler
    # @log_performance(include_args=True)
    async def greet_user(name: str):
        greeting = 'Hello, World!'
        timeout = 60
        response = 'Processed'
        print(1 / 0)
        return {'message': greeting, 'processed': response, 'timeout': timeout}
    return app


app = create_app()
