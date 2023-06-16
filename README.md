# How to start up the application

1. Clone this repository.

2. [Optional] Set up a Python virtual environment by running python3 -m venv venv.

3. [Optional] Activate the virtual environment:
    - For MacOS/Linux, use the command source venv/bin/activate.
    - For Windows, use the command venv/Scripts/activate.
4. After activating the virtual environment, ensure that you have the latest version of pip installed by running `pip install --upgrade pip`.

5. Install the dependencies with the following command:
    ```bash
    pip install -r requirements.txt
    ```
6. Update `broker_props` in the code with your Solace details.
7. To run the service1.py run:
    ```bash
    python service1.py
    ```
8. To run service2.py run:
    ```bash
    python service2.py
    ```
