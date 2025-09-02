import os
import sys
PROJECT_PATH = os.getcwd()
PROJECT_FOLDER = os.path.basename(PROJECT_PATH)
SOURCE_PATH = os.path.join(
    PROJECT_PATH,PROJECT_FOLDER
)
sys.path.append(SOURCE_PATH)