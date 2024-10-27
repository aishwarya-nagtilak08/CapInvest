import time
import logging

logger =  logging.getLogger(__name__)

class ResponseTimeLogMiddleware:
    
    def __init__(self, get_response):
        self.get_response =  get_response
    
    def __call__(self, request):
        start_time = time.time()
        response = self.get_response(request)
        end_time = time.time() - start_time
        logger.info(f"Response time took {end_time:.4f} seconds")
        return response
    