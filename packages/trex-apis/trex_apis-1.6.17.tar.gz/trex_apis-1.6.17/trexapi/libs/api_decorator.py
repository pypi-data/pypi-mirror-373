'''
Created on 22 Apr 2024

@author: jacklok
'''
import logging
from functools import wraps
import time

logger = logging.getLogger('lib')



def elapsed_time_trace(debug=False, trace_key=None):
    """
    Decorator to measure and log the execution time of a Flask endpoint.
    
    Args:
        debug (bool): If True, logs detailed request information (e.g., method, URL, headers).
        trace_key (str): Optional key to extract from request (e.g., 'request_id') for log correlation.
                         If None, no trace key is logged.
    
    Returns:
        Decorator function that wraps the endpoint.
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            start = time.time()
            result = func(*args, **kwargs)
            end = time.time()
            
            #elapsed_time = end - start
            elapsed_ms = (end - start) * 1000  # Convert seconds to milliseconds
            trace_name      = trace_key or func.func_name
            first_argument  = args[0] if args else None
            logger.info('==================== Start Elapsed Time Trace %s(%s) ===========================', trace_name, first_argument)
            logger.info('elapsed time=%s ms', ("%.2f" % (elapsed_ms)))
            logger.info('================================================================================')


            return result
        return wrapper
    return decorator
'''
def elapsed_time_trace(debug=False, trace_key=None):
    def wrapper(fn):
        import time
        def elapsed_time_trace_wrapper(*args, **kwargs):
            start = time.time()
            end = time.time()
            elapsed_time = end - start
            trace_name      = trace_key or fn.func_name
            first_argument  = args[0] if args else None
            logger.info('==================== Start Elapsed Time Trace %s(%s) ===========================', trace_name, first_argument)
            logger.info('elapsed time=%s', ("%.2gs" % (elapsed_time)))
            logger.info('================================================================================')
            
            return fn(*args, **kwargs)

        return elapsed_time_trace_wrapper
    return wrapper
'''


