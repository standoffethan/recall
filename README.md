# memory_app_bloom

See detais about our project on our DevPost here:  
https://devpost.com/software/recall-93a6j5

---

Instructions to start the backend:  
---------------------WINDOWS-----------------------  
1. open Docker Desktop  
2. Open command prompt  
3. navigate to the backend folder using chdir  
4. create a .env file and populate it with:  
GEMINI_API_KEY=[Your API key]  
5. run docker-compose up --build  
6. Navigate to the scripts directory  
7. create a python venv by: python -m venv venv  
8. activate the virtual environment by running: venv\Scripts\activate  
9. Download script dependencies by running: pip install -r requirements.txt  
10. run two commands:  
	set DATABASE_URL=postgresql://appuser:apppass@localhost:5433/appdb  
	python seed_passages.py  
11. run: deactivate  

----------------------LINUX-------------------------  
1. Open the terminal  
2. navigate to the backend folder using cd  
3. create a .env file and populate it with:  
GEMINI_API_KEY=[Your API key]  
4. run docker compose up --build  
5. Navigate to the scripts directory  
6. create a python venv by: python -m venv venv  
7. activate the virtual environment by running: venv\Scripts\activate
8. Download script dependencies by running: pip install -r requirements.txt
9. run the seed.sh shell file
10. run: deactivate

---

You can then download the zip file with our android project in it, unzip it and open it in android studio. You should then be able to run the app in the emulator.
