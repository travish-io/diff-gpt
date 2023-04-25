import os
import sys
import time
import threading
import requests
from dotenv import load_dotenv
import openai


def spinning_cursor():
    while True:
        for cursor in '|/-\\':
            yield cursor


def animate_spinner(stop_event):
    spinner = spinning_cursor()
    while not stop_event.is_set():
        sys.stdout.write(next(spinner))
        sys.stdout.flush()
        time.sleep(0.1)
        sys.stdout.write('\b')


def format_api_url(pr_url):
    # Remove any trailing slashes from the input URL
    pr_url = pr_url.rstrip("/")

    # Split the URL into its parts
    parts = pr_url.split("/")

    # Extract the repository owner and name from the URL
    owner = parts[3]
    repo = parts[4]

    # Extract the pull request number from the URL
    pr_number = parts[-1]

    # Construct the API URL using the owner, repo, and PR number
    api_url = f"https://api.github.com/repos/{owner}/{repo}/pulls/{pr_number}"

    return api_url


def get_diff_file_content(api_url, headers, auth):
    response = requests.get(api_url, headers=headers, auth=auth)
    response.raise_for_status()
    return response.content


def generate_summary(diff_file_content, openai_api_key):
    def chunk_diff(diff_text, max_tokens=4097):
        lines = diff_text.split("\n")
        chunks = []
        current_chunk = ""

        for line in lines:
            temp_chunk = f"{current_chunk}\n{line}"
            if len(temp_chunk) <= max_tokens:
                current_chunk = temp_chunk
            else:
                chunks.append(current_chunk)
                current_chunk = line

        if current_chunk:
            chunks.append(current_chunk)

        return chunks

    def handle_response_error():
        print("Error: Unable to generate summary")
        return ""

    def make_openai_request(chunk, api_key):
        openai.api_key = api_key

        response = openai.Completion.create(
            model="text-davinci-003",
            prompt=f"Please provide a detailed summary of the changes made in the following GitHub pull request diff, describing the overall purpose and impact of the changes in a way that non-technical people will understand. Use Unicode bullet points to highlight the most important changes made:\n\n{chunk}",
            max_tokens=200,
            temperature=0.3,
            top_p=0.1,
            n=1
        )

        summary = response.choices[0].text.strip(
        ) if response and response.choices else handle_response_error()

        # Post-process the summary to filter out unwanted lines
        summary_lines = summary.split("\n")
        filtered_lines = [
            line for line in summary_lines
            if len(line) > 20  # Remove short lines
            # Remove lines starting with code-related characters
            and not line.startswith(("+", "-", "@", "<"))
            # Remove lines containing brackets
            and not any(char in line for char in "{}()")
        ]
        return "\n".join(filtered_lines)

    chunks = chunk_diff(diff_file_content)

    # Start the spinner animation
    stop_spinner = threading.Event()
    spinner_thread = threading.Thread(
        target=animate_spinner, args=(stop_spinner,))
    spinner_thread.start()

    summaries = [make_openai_request(chunk, openai_api_key)
                 for chunk in chunks]

    # Stop the spinner animation
    stop_spinner.set()
    spinner_thread.join()

    # Filter out empty summaries before joining
    summary = "\n\n".join(filter(None, summaries))

    return summary


def main():
    if len(sys.argv) != 2:
        print("Usage: python main.py <GitHub Pull Request URL>")
        sys.exit(1)

    load_dotenv()

    openai_api_key = os.environ["OPENAI_API_KEY"]
    github_pat = os.environ["GITHUB_PAT"]

    pr_url = sys.argv[1]
    api_url = format_api_url(pr_url)
    headers = {"Accept": "application/vnd.github.diff"}
    auth = (f"{github_pat}", "x-oauth-basic")

    diff_file_content = get_diff_file_content(api_url, headers, auth)
    diff_file_content = diff_file_content.decode(
        'utf-8')  # decode the bytes object into a string
    summary = generate_summary(diff_file_content, openai_api_key)

    print(summary)

    # with open("summary.txt", "w") as f:
    #     f.write(summary)


if __name__ == "__main__":
    main()
