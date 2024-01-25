# stress_tool.py
import argparse  # Library for parsing command-line arguments
import concurrent.futures   # Provides a high-level interface for asynchronously executing
import csv  # Provides functionality for reading from and writing to CSV files
import json  # For working with JSON data
import requests  # HTTP library for making requests
import time  # Provides time-related functions


# Define Constant
API_URL = "https://microcks.gin.dev.securingsam.io/rest/Reputation+API/1.0.0/domain/ranking/"


# Function to fetch the reputation data for a given domain using the Reputation service API
def fetch_domain_reputation(domain):
    try:
        response = requests.get(API_URL + domain, headers={"Authorization": "Token I_am_under_stress_when_I_test"})
        response.raise_for_status()
        assert response.status_code == 200, f"No response from - {domain}"
        return response.json()
    except requests.RequestException as e:
        return {"error": str(e)}


# Function to load domains from a JSON file. Returns an empty list if there is an error
def load_domains_from_json(json_file):
    try:
        with open(json_file, "r") as file:
            data = json.load(file)
            return data.get("domains", [])
    except (json.JSONDecodeError, FileNotFoundError) as e:
        print(f"Error loading domains from JSON: {str(e)}")
        return []


# Calculate time taken
def calculate_time_taken(start_time):
    total_time = time.time() - start_time
    return total_time


# Calculates the error rate as a percentage
def calculate_error_rate(failed_requests, successful_requests):
    error_rate = failed_requests / (failed_requests + successful_requests) * 100 \
        if failed_requests + successful_requests > 0 else 0
    return error_rate


# Print the results
def print_the_results(total_time, failed_requests, successful_requests, error_rate, csv_filename):
    print(f"Time in total: {total_time:.2f} seconds")
    print(f"Requests in total: {failed_requests + successful_requests}")
    print(f"Error rate: {error_rate:.2f}% ({failed_requests} / {failed_requests + successful_requests})")
    print(f"Average time for one request: {total_time / (failed_requests + successful_requests) * 1000:.2f} ms")
    print(f"Results saved to: {csv_filename}")


# Stress test function. It uses ThreadPoolExecutor to make concurrent requests to the Reputation service API
def stress_test(domain_count, concurrency, timeout):
    start_time = time.time()
    successful_requests = 0
    failed_requests = 0
    csv_filename = f"reputation_stress_results_{int(time.time())}.csv"
    list_domains = load_domains_from_json("domains.json")  # list domains from json file - domains.json
    if not list_domains:
        print("No valid domains found. Exiting.")
        return
    domains = []
    for domain in list_domains:
        domains.extend([domain] * domain_count)  # extend domains from list of domains * domain_count
    try:
        with open(csv_filename, mode="w", newline="") as csv_file:
            fieldnames = ["Domain", "Reputation", "Categories"]
            writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
            writer.writeheader()
            # This creates a pool of worker threads (max_workers=concurrency) using a ThreadPoolExecutor.
            # The with statement ensures proper cleanup of resources when the block is exited.
            with concurrent.futures.ThreadPoolExecutor(max_workers=concurrency) as executor:
                # Submits tasks to the executor. Each submitted task (a Future object) the resulting Future object is
                # then added to the dictionary as a key, with the associated domain as its value.
                future_to_domain = {}
                for domain in domains:
                    future = executor.submit(fetch_domain_reputation, domain)
                    future_to_domain[future] = domain
                #  Iterates over completed futures as they become available
                for future in concurrent.futures.as_completed(future_to_domain):
                    # Retrieves the domain associated with the completed future
                    domain = future_to_domain[future]
                    time_remaining = time.time() - start_time
                    if time_remaining > timeout:
                        print(f"Timeout reached - {timeout} seconds, please increase the timeout")
                        return f"Timeout reached - {timeout}"
                    try:
                        # Gets the result of the completed future. If the task is still running,
                        # this call will block until the result is available
                        reputation_data = future.result()
                        # Checks if there is an error in the reputation data
                        if "error" in reputation_data:
                            failed_requests += 1
                        else:
                            successful_requests += 1
                        writer.writerow({"Domain": domain, "Reputation": reputation_data.get("reputation"), "Categories":
                                        reputation_data.get("categories")})
                    except Exception as e:
                        print(f"An error occurred for domain {domain}: {str(e)}")
                        failed_requests += 1

        total_time = calculate_time_taken(start_time)
        error_rate = calculate_error_rate(failed_requests, successful_requests)

        print(f"\nStress test is over!\nReason: Finished successfully")
        print_the_results(total_time, failed_requests, successful_requests, error_rate, csv_filename)
    except KeyboardInterrupt:
        print(f"\nStress test is over!\nReason: Interrupted by user\nPartial output:")
        total_time = calculate_time_taken(start_time)
        error_rate = calculate_error_rate(failed_requests, successful_requests)
        print_the_results(total_time, failed_requests, successful_requests, error_rate, csv_filename)


def main():
    parser = argparse.ArgumentParser(description="Reputation Service Stress Test")
    parser.add_argument("--concurrency", type=int, default=10, help="Number of concurrent requests")
    parser.add_argument("--domains", type=int, default=10, help="Number of domains")
    parser.add_argument("--timeout", type=int, default=60, help="Timeout in seconds")
    args = parser.parse_args()
    stress_test(args.domains, args.concurrency, args.timeout)


if __name__ == "__main__":
    main()
