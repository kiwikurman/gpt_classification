import openai
import json
import uuid
from concurrent.futures import ThreadPoolExecutor
import time

# Open the file for reading
with open('keys.json', 'r') as f:
    keys = json.load(f)
    openai.api_key = keys["openai_key"]


def read_lines():
    with open('a.csv', 'r') as f:
        lines = f.readlines()

    lines = [line.strip() for line in lines]
    lines = [line.replace(",", "") for line in lines]
    lines = [line for line in lines if line.strip()]
    lines = [line for line in lines if line.find("park") < 0]
    return lines


def classify_batch(batch, ix, b_size):
    my_id = str(uuid.uuid4())[:4]
    print(f"{my_id} starting working on {ix} to {ix + b_size}")

    the_message = [{"role": "system",
                    "content": "for each line in the following text, i need exactly one line output with the following comma-separated format: summary in english of the input, classification label."},
                   {"role": "system",
                    "content": "the label should be one of the following: mechanical, electrical, clean up, operational, temperature. the operational label should capture anything related to a device malfunctioning. the temperature label should capture anything regarding temperature change."},
                   {"role": "system", "content": "the summary must be in english."},
                   {"role": "system",
                    "content": "an example for an output is: Handle does not close properly indicating that the oven is not closed, mechanical"}]

    text = "\n".join(batch)
    the_message.append({"role": "user", "content": text})
    chat_completion = openai.ChatCompletion.create(model="gpt-3.5-turbo", messages=the_message, temperature=0)
    print(f"{my_id} is done at {ix + b_size}")
    return chat_completion['choices'][0]['message']['content']


def process_lines(lines, batch_size=15):
    res = []
    with ThreadPoolExecutor(max_workers=40) as executor:
        futures = {}
        for i in range(0, len(lines), batch_size):
            batch = lines[i:i + batch_size]
            future = executor.submit(classify_batch, batch, i, batch_size)
            futures[future] = {'batch': batch, 'retry_count': 0}

        while futures:
            for future in list(futures.keys()):  # Make a list from keys to iterate safely while removing items
                batch = futures[future]["batch"]
                retry_count = futures[future]["retry_count"]
                try:
                    batch_result = future.result(timeout=30)  # Wait for 10 seconds
                    res.append(batch_result)
                except TimeoutError:
                    print(f"Timeout for batch {batch}, retrying...")
                    if retry_count < 3:
                        # Resubmit the failed batch
                        new_future = executor.submit(classify_batch, batch, i, batch_size)
                        futures[new_future] = {'batch': batch, 'retry_count': retry_count + 1}
                    else:
                        print(f"Failed after {retry_count} retries.")
                finally:
                    del futures[future]  # Remove the old future, whether we retry or not
    return res


def write_to_file(res):
    file_name = "res_" + str(uuid.uuid4())[:4] + ".txt"
    print(f"writing results to {file_name}")
    with open(file_name, "w") as f:
        f.write("\n".join(res))


if __name__ == "__main__":
    input_lines = read_lines()

    start_time = time.time()
    results = process_lines(input_lines[:50])
    end_time = time.time()

    print(f"done in {end_time - start_time} seconds")

    write_to_file(results)
