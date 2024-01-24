# Backend Setup
## Step 1: Clone the Repository

Clone the FastAPI repository to your local machine.

```bash
git clone https://github.com/mubashirnas1r/is_project_backend.git
cd is_project_backend
```

## Step 2: Create a Virtual Environment

Create a virtual environment named `venv` using the following commands:

```bash
# For Linux/Mac
python3 -m venv venv

# For Windows
python -m venv venv
```

Activate the virtual environment:

```bash
# For Linux/Mac
source venv/bin/activate

# For Windows
.\venv\Scripts\activate
```

## Step 3: Install Dependencies

Install the required dependencies using `pip`:

```bash
pip install -r requirements.txt
```

## Step 4: Run the FastAPI Application

Run the FastAPI application using the following command:

```bash
uvicorn main:app --reload
```

The application will be accessible at [http://127.0.0.1:8000](http://127.0.0.1:8000). You can access the interactive documentation at [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs) and the JSON Swagger documentation at [http://127.0.0.1:8000/openapi.json](http://127.0.0.1:8000/openapi.json).

## Step 5: Deactivate the Virtual Environment

Once you are done, deactivate the virtual environment:

```bash
deactivate
```

Now, you have successfully set up and run a the Backend of my project in a virtual environment.

