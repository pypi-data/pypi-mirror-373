import os
import time
import concurrent.futures
from datetime import datetime
from queue import Queue
import random
from typing import List, Dict, Any
from llm_wrapper import LLMWrapper

class ParallelLLMTester:
    def __init__(self, db_config: Dict[str, Any], max_workers: int = 10):
        self.db_config = db_config
        self.max_workers = max_workers
        self.results_queue = Queue()
        self.errors_queue = Queue()
        self.test_requests = [
            "What are the benefits of renewable energy?",
            "Explain machine learning in simple terms",
            "What is the future of artificial intelligence?",
            "How does blockchain technology work?",
            "What are the advantages of cloud computing?",
            "Describe the impact of climate change on ecosystems",
            "How do neural networks function?",
            "What is quantum computing and its applications?",
            "Explain the concept of sustainable development",
            "What are the latest trends in cybersecurity?",
            "How does 5G technology improve connectivity?",
            "What is the role of big data in modern business?",
            "Describe the Internet of Things (IoT) ecosystem",
            "How do recommendation systems work?",
            "What are the ethical considerations in AI development?"
        ]
        
    def create_wrapper_instance(self) -> LLMWrapper:
        """Create a new LLM wrapper instance for each thread"""
        return LLMWrapper(
            service_url="https://cars-dev-ai.openai.azure.com",
            api_key="9wvAHhgPf3FMiPek68vnXUUCZTih2XXhltWyGBjnh7gAYGCpjnCBJQQJ99BDACLArgHXJ3w3AAABACOGGrF0",
            db_config=self.db_config,
            deployment_name="gpt-4.1",
            api_version="2024-12-01-preview",
            default_model='gpt-4'
        )
    
    def single_request_worker(self, thread_id: int, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """Worker function for a single request"""
        wrapper = None
        try:
            wrapper = self.create_wrapper_instance()
            
            start_time = time.time()
            
            response = wrapper.send_request(
                input_text=request_data['text'],
                customer_id=request_data['customer_id'],
                organization_id=request_data['organization_id'],
                temperature=request_data.get('temperature', 0.7),
                max_tokens=request_data.get('max_tokens', 1500)
            )
            
            end_time = time.time()
            
            result = {
                'thread_id': thread_id,
                'customer_id': request_data['customer_id'],
                'success': True,
                'response': response,
                'execution_time': end_time - start_time,
                'timestamp': datetime.now().isoformat()
            }
            
            self.results_queue.put(result)
            return result
            
        except Exception as e:
            error_result = {
                'thread_id': thread_id,
                'customer_id': request_data.get('customer_id'),
                'success': False,
                'error': str(e),
                'execution_time': time.time() - start_time if 'start_time' in locals() else 0,
                'timestamp': datetime.now().isoformat()
            }
            self.errors_queue.put(error_result)
            return error_result
            
        finally:
            if wrapper:
                try:
                    wrapper.close()
                except:
                    pass
    
    def test_concurrent_requests(self, num_requests: int = 50) -> Dict[str, Any]:
        """Test concurrent requests using ThreadPoolExecutor"""
        print(f"\n{'='*60}")
        print(f"TESTING CONCURRENT REQUESTS ({num_requests} requests)")
        print(f"{'='*60}")
        
        # Prepare test data
        test_data = []
        for i in range(num_requests):
            test_data.append({
                'text': random.choice(self.test_requests),
                'customer_id': random.randint(1, 10),
                'organization_id': random.randint(1, 5),
                'temperature': round(random.uniform(0.3, 0.9), 1),
                'max_tokens': random.randint(1000, 2000)
            })
        
        start_time = time.time()
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            future_to_index = {
                executor.submit(self.single_request_worker, i, data): i 
                for i, data in enumerate(test_data)
            }
            
            completed = 0
            for _future in concurrent.futures.as_completed(future_to_index):
                completed += 1
                if completed % 10 == 0:
                    print(f"Completed: {completed}/{num_requests}")
        
        end_time = time.time()
        total_execution_time = end_time - start_time
        
        # Collect results
        results = []
        while not self.results_queue.empty():
            results.append(self.results_queue.get())
        
        errors = []
        while not self.errors_queue.empty():
            errors.append(self.errors_queue.get())
        
        return {
            'total_requests': num_requests,
            'successful_requests': len(results),
            'failed_requests': len(errors),
            'total_execution_time': total_execution_time,
            'average_request_time': sum(r['execution_time'] for r in results) / len(results) if results else 0,
            'requests_per_second': num_requests / total_execution_time,
            'results': results,
            'errors': errors
        }
    
    def test_burst_load(self, burst_size: int = 20, num_bursts: int = 3, delay_between_bursts: int = 5) -> List[Dict[str, Any]]:
        """Test burst load patterns"""
        print(f"\n{'='*60}")
        print(f"TESTING BURST LOAD ({num_bursts} bursts of {burst_size} requests each)")
        print(f"{'='*60}")
        
        burst_results = []
        
        for burst_num in range(num_bursts):
            print(f"\nStarting burst {burst_num + 1}/{num_bursts}...")
            
            burst_result = self.test_concurrent_requests(burst_size)
            burst_result['burst_number'] = burst_num + 1
            burst_results.append(burst_result)
            
            print(f"Burst {burst_num + 1} completed:")
            print(f"  - Successful: {burst_result['successful_requests']}")
            print(f"  - Failed: {burst_result['failed_requests']}")
            print(f"  - RPS: {burst_result['requests_per_second']:.2f}")
            
            if burst_num < num_bursts - 1:
                print(f"Waiting {delay_between_bursts}s before next burst...")
                time.sleep(delay_between_bursts)
        
        return burst_results
    
    def test_database_consistency(self) -> Dict[str, Any]:
        """Test database consistency under concurrent load"""
        print(f"\n{'='*60}")
        print("TESTING DATABASE CONSISTENCY")
        print(f"{'='*60}")
        
        wrapper = self.create_wrapper_instance()
        
        try:
            # Get initial stats
            initial_stats = wrapper.get_usage_stats()
            initial_requests = initial_stats['total_requests']
            
            # Run concurrent test
            test_result = self.test_concurrent_requests(30)
            
            # Wait a moment for database writes to complete
            time.sleep(2)
            
            # Get final stats
            final_stats = wrapper.get_usage_stats()
            final_requests = final_stats['total_requests']
            
            requests_difference = final_requests - initial_requests
            expected_new_requests = test_result['successful_requests']
            
            consistency_check = {
                'initial_requests': initial_requests,
                'final_requests': final_requests,
                'requests_difference': requests_difference,
                'expected_new_requests': expected_new_requests,
                'consistent': requests_difference == expected_new_requests,
                'test_result': test_result
            }
            
            print("Database consistency check:")
            print(f"  - Initial requests in DB: {initial_requests}")
            print(f"  - Final requests in DB: {final_requests}")
            print(f"  - New requests recorded: {requests_difference}")
            print(f"  - Expected new requests: {expected_new_requests}")
            print(f"  - Consistent: {'✓' if consistency_check['consistent'] else '✗'}")
            
            return consistency_check
            
        finally:
            wrapper.close()
    
    def run_comprehensive_test(self) -> Dict[str, Any]:
        """Run comprehensive parallel testing suite"""
        print(f"\n{'='*80}")
        print("COMPREHENSIVE PARALLEL LLM WRAPPER TEST")
        print(f"Database Type: {self.db_config['type']}")
        print(f"Max Workers: {self.max_workers}")
        print(f"{'='*80}")
        
        test_results = {
            'start_time': datetime.now().isoformat(),
            'db_type': self.db_config['type'],
            'max_workers': self.max_workers
        }
        
        # Test 1: Basic concurrent requests
        test_results['concurrent_test'] = self.test_concurrent_requests(50)
        
        # Test 2: Burst load testing
        test_results['burst_test'] = self.test_burst_load(20, 3, 3)
        
        # Test 3: Database consistency
        test_results['consistency_test'] = self.test_database_consistency()
        
        # Test 4: High load test
        print(f"\n{'='*60}")
        print("TESTING HIGH LOAD (100 concurrent requests)")
        print(f"{'='*60}")
        test_results['high_load_test'] = self.test_concurrent_requests(100)
        
        test_results['end_time'] = datetime.now().isoformat()
        
        # Summary
        self.print_test_summary(test_results)
        
        return test_results
    
    def print_test_summary(self, results: Dict[str, Any]):
        """Print comprehensive test summary"""
        print(f"\n{'='*80}")
        print("TEST SUMMARY")
        print(f"{'='*80}")
        
        total_requests = 0
        total_successful = 0
        total_failed = 0
        
        for test_name, test_data in results.items():
            if test_name in ['start_time', 'end_time', 'db_type', 'max_workers']:
                continue
                
            if test_name == 'burst_test':
                for burst in test_data:
                    total_requests += burst['total_requests']
                    total_successful += burst['successful_requests']
                    total_failed += burst['failed_requests']
            elif isinstance(test_data, dict) and 'total_requests' in test_data:
                total_requests += test_data['total_requests']
                total_successful += test_data['successful_requests']
                total_failed += test_data['failed_requests']
        
        print(f"Database Type: {results['db_type']}")
        print(f"Max Workers: {results['max_workers']}")
        print(f"Total Requests: {total_requests}")
        print(f"Successful Requests: {total_successful}")
        print(f"Failed Requests: {total_failed}")
        print(f"Success Rate: {(total_successful/total_requests)*100:.2f}%" if total_requests > 0 else "N/A")
        
        # Performance summary
        if 'concurrent_test' in results:
            ct = results['concurrent_test']
            print("\nPerformance Metrics:")
            print(f"  - Average Request Time: {ct['average_request_time']:.2f}s")
            print(f"  - Requests Per Second: {ct['requests_per_second']:.2f}")
        
        # Database consistency
        if 'consistency_test' in results:
            ct = results['consistency_test']
            print(f"\nDatabase Consistency: {'✓ PASSED' if ct['consistent'] else '✗ FAILED'}")


def get_database_configs():
    """Get all database configurations"""
    return {
        'postgresql': {
            'type': 'postgresql',
            'dbname': os.getenv('DB_NAME', 'llm_wrapper_db'),
            'user': os.getenv('DB_USER', 'postgres'),
            'password': os.getenv('DB_PASSWORD', 'Hibiz123'),
            'host': os.getenv('DB_HOST', 'localhost'),
            'port': os.getenv('DB_PORT', '5432')
        },
        'mysql': {
            'type': 'mysql',
            'dbname': os.getenv('MYSQL_DB_NAME', 'llm_wrapper_db'),
            'user': os.getenv('MYSQL_USER', 'root'),
            'password': os.getenv('MYSQL_PASSWORD', 'password'),
            'host': os.getenv('MYSQL_HOST', 'localhost'),
            'port': os.getenv('MYSQL_PORT', '3306')
        },
        'mongodb': {
            'type': 'mongodb',
            'dbname': os.getenv('MONGO_DB_NAME', 'llm_wrapper_db'),
            'host': os.getenv('MONGO_HOST', 'localhost'),
            'port': int(os.getenv('MONGO_PORT', '27017')),
            'user': os.getenv('MONGO_USER'),
            'password': os.getenv('MONGO_PASSWORD')
        }
    }


def main():
    """Main function to run parallel tests"""
    db_type = os.getenv('DATABASE_TYPE', 'postgresql').lower()
    max_workers = int(os.getenv('MAX_WORKERS', '10'))
    
    configs = get_database_configs()
    
    if db_type not in configs:
        print(f"Unsupported database type: {db_type}")
        print(f"Supported types: {', '.join(configs.keys())}")
        return
    
    db_config = configs[db_type]
    
    # Initialize tester
    tester = ParallelLLMTester(db_config, max_workers)
    
    try:
        # Run comprehensive tests
        results = tester.run_comprehensive_test()
        
        # Optionally save results to file
        import json
        with open(f'parallel_test_results_{db_type}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json', 'w') as f:
            json.dump(results, f, indent=2, default=str)
        
        print("\nTest results saved to file.")
        
    except KeyboardInterrupt:
        print("\nTest interrupted by user.")
    except Exception as e:
        print(f"Test failed with error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()