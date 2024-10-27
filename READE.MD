# PYTHON_DEV CHALLENGE

The code was made in order to solve the proposed challenge in which a csv file retrived from CVM (Brazilian Market regulatory organ).

# How was it done?

First of all, FastAPI was used to start an api in order to receive the .csv file containing the major data needed as requested by the challenge.

Secondly, Pandas was the library used to manipulate the .csv file and push the requested data to the DataBase.

Finally, SQLModel was used to create the database for this challenge.

# How to run the code?

Start by creating and virtual environment using the command

```bash
python -m venv venv
```

and activate it using

```bash
venv/Scripts/activate
```

Afterwards, install the dependenciesas following:

```bash
pip install -r requirements.txt
```

# How to run the application?

To run the application, use the command

```bash
fastapi dev main.py
```

once you have the application running, you can go to the /docs endpoint and then send the csv file through the post method provided. Have fun!
